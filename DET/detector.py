#!/usr/bin/env python3
"""
 Copyright (C) 2018-2020 Intel Corporation
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import logging
import threading
import os
import sys
from collections import deque
from argparse import ArgumentParser, SUPPRESS
from math import exp as exp
from time import perf_counter
from enum import Enum

import cv2
import numpy as np
from openvino.inference_engine import IECore


logging.basicConfig(format="[ %(levelname)s ] %(message)s", level=logging.INFO, stream=sys.stdout)
log = logging.getLogger()

def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args.add_argument("-m", "--model", help="Required. Path to an .xml file with a trained model.",
                      required=True, type=str)
    args.add_argument("-i", "--input", help="Required. Path to an image/video file. (Specify 'cam' to work with "
                                            "camera)", required=True, type=str)
    args.add_argument("-l", "--cpu_extension",
                      help="Optional. Required for CPU custom layers. Absolute path to a shared library with "
                           "the kernels implementations.", type=str, default=None)
    args.add_argument("-d", "--device",
                      help="Optional. Specify the target device to infer on; CPU, GPU, FPGA, HDDL or MYRIAD is"
                           " acceptable. The sample will look for a suitable plugin for device specified. "
                           "Default value is CPU", default="CPU", type=str)
    args.add_argument("--labels", help="Optional. Labels mapping file", default=None, type=str)
    args.add_argument("-t", "--prob_threshold", help="Optional. Probability threshold for detections filtering",
                      default=0.5, type=float)
    args.add_argument("-iout", "--iou_threshold", help="Optional. Intersection over union threshold for overlapping "
                                                       "detections filtering", default=0.4, type=float)
    args.add_argument("-r", "--raw_output_message", help="Optional. Output inference results raw values showing",
                      default=False, action="store_true")
    args.add_argument("-nireq", "--num_infer_requests", help="Optional. Number of infer requests",
                      default=1, type=int)
    args.add_argument("-nstreams", "--num_streams",
                      help="Optional. Number of streams to use for inference on the CPU or/and GPU in throughput mode "
                           "(for HETERO and MULTI device cases use format <device1>:<nstreams1>,<device2>:<nstreams2> "
                           "or just <nstreams>)",
                      default="", type=str)
    args.add_argument("-nthreads", "--number_threads",
                      help="Optional. Number of threads to use for inference on CPU (including HETERO cases)",
                      default=None, type=int)
    args.add_argument("-loop_input", "--loop_input", help="Optional. Iterate over input infinitely",
                      action='store_true')
    args.add_argument("-no_show", "--no_show", help="Optional. Don't show output", action='store_true')
    args.add_argument('-u', '--utilization_monitors', default='', type=str,
                      help='Optional. List of monitors to show initially.')
    args.add_argument("--keep_aspect_ratio", action="store_true", default=False,
                      help='Optional. Keeps aspect ratio on resize.')
    return parser


class YoloParams:
    # ------------------------------------------- Extracting layer parameters ------------------------------------------
    # Magic numbers are copied from yolo samples
    def __init__(self, param, side):
        self.num = 3 if 'num' not in param else int(param['num'])
        self.coords = 4 if 'coords' not in param else int(param['coords'])
        self.classes = 80 if 'classes' not in param else int(param['classes'])
        self.side = side
        self.anchors = [10.0, 13.0, 16.0, 30.0, 33.0, 23.0, 30.0, 61.0, 62.0, 45.0, 59.0, 119.0, 116.0, 90.0, 156.0,
                        198.0,
                        373.0, 326.0] if 'anchors' not in param else [float(a) for a in param['anchors'].split(',')]

        self.isYoloV3 = False

        if param.get('mask'):
            mask = [int(idx) for idx in param['mask'].split(',')]
            self.num = len(mask)

            maskedAnchors = []
            for idx in mask:
                maskedAnchors += [self.anchors[idx * 2], self.anchors[idx * 2 + 1]]
            self.anchors = maskedAnchors

            self.isYoloV3 = True # Weak way to determine but the only one.


class Modes(Enum):
    USER_SPECIFIED = 0
    MIN_LATENCY = 1


class Mode():
    def __init__(self, value):
        self.current = value

    def next(self):
        if self.current.value + 1 < len(Modes):
            self.current = Modes(self.current.value + 1)
        else:
            self.current = Modes(0)


class ModeInfo():
    def __init__(self):
        self.last_start_time = perf_counter()
        self.last_end_time = None
        self.frames_count = 0
        self.latency_sum = 0


def scale_bbox(x, y, height, width, class_id, confidence, im_h, im_w, is_proportional):
    if is_proportional:
        scale = np.array([min(im_w/im_h, 1), min(im_h/im_w, 1)])
        offset = 0.5*(np.ones(2) - scale)
        x, y = (np.array([x, y]) - offset) / scale
        width, height = np.array([width, height]) / scale
    xmin = int((x - width / 2) * im_w)
    ymin = int((y - height / 2) * im_h)
    xmax = int(xmin + width * im_w)
    ymax = int(ymin + height * im_h)
    # Method item() used here to convert NumPy types to native types for compatibility with functions, which don't
    # support Numpy types (e.g., cv2.rectangle doesn't support int64 in color parameter)
    return dict(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, class_id=class_id.item(), confidence=confidence.item())


def parse_yolo_region(predictions, resized_image_shape, original_im_shape, params, threshold, is_proportional):
    # ------------------------------------------ Validating output parameters ------------------------------------------
    _, _, out_blob_h, out_blob_w = predictions.shape
    assert out_blob_w == out_blob_h, "Invalid size of output blob. It sould be in NCHW layout and height should " \
                                     "be equal to width. Current height = {}, current width = {}" \
                                     "".format(out_blob_h, out_blob_w)

    # ------------------------------------------ Extracting layer parameters -------------------------------------------
    orig_im_h, orig_im_w = original_im_shape
    resized_image_h, resized_image_w = resized_image_shape
    objects = list()
    size_normalizer = (resized_image_w, resized_image_h) if params.isYoloV3 else (params.side, params.side)
    bbox_size = params.coords + 1 + params.classes
    # ------------------------------------------- Parsing YOLO Region output -------------------------------------------
    for row, col, n in np.ndindex(params.side, params.side, params.num):
        # Getting raw values for each detection bounding box
        bbox = predictions[0, n*bbox_size:(n+1)*bbox_size, row, col]
        x, y, width, height, object_probability = bbox[:5]
        class_probabilities = bbox[5:]
        if object_probability < threshold:
            continue
        # Process raw value
        x = (col + x) / params.side
        y = (row + y) / params.side
        # Value for exp is very big number in some cases so following construction is using here
        try:
            width = exp(width)
            height = exp(height)
        except OverflowError:
            continue
        # Depends on topology we need to normalize sizes by feature maps (up to YOLOv3) or by input shape (YOLOv3)
        width = width * params.anchors[2 * n] / size_normalizer[0]
        height = height * params.anchors[2 * n + 1] / size_normalizer[1]

        class_id = np.argmax(class_probabilities)
        confidence = class_probabilities[class_id]*object_probability
        if confidence < threshold:
            continue
        objects.append(scale_bbox(x=x, y=y, height=height, width=width, class_id=class_id, confidence=confidence,
                                  im_h=orig_im_h, im_w=orig_im_w, is_proportional=is_proportional))
    return objects


def distance_intersection_over_union(box_1, box_2):#add DIOU-NMS (as in yolov4)
    width_of_overlap_area = min(box_1['xmax'], box_2['xmax']) - max(box_1['xmin'], box_2['xmin'])
    height_of_overlap_area = min(box_1['ymax'], box_2['ymax']) - max(box_1['ymin'], box_2['ymin'])

    cw = max(box_1['xmax'], box_2['xmax'])-min(box_1['xmin'], box_2['xmin'])
    ch = max(box_1['ymax'], box_2['ymax'])-min(box_1['ymin'], box_2['ymin'])
    c_area = cw**2+ch**2+1e-16
    rh02 = ((box_2['xmax']+box_2['xmin'])-(box_1['xmax']+box_1['xmin']))**2/4+((box_2['ymax']+box_2['ymin'])-(box_1['ymax']+box_1['ymin']))**2/4

    if width_of_overlap_area < 0 or height_of_overlap_area < 0:
        area_of_overlap = 0
    else:
        area_of_overlap = width_of_overlap_area * height_of_overlap_area
    box_1_area = (box_1['ymax'] - box_1['ymin']) * (box_1['xmax'] - box_1['xmin'])
    box_2_area = (box_2['ymax'] - box_2['ymin']) * (box_2['xmax'] - box_2['xmin'])
    area_of_union = box_1_area + box_2_area - area_of_overlap
    if area_of_union == 0:
        return 0
    return area_of_overlap / area_of_union-pow(rh02/c_area,0.6)

def intersection_over_union(box_1, box_2):
    width_of_overlap_area = min(box_1['xmax'], box_2['xmax']) - max(box_1['xmin'], box_2['xmin'])
    height_of_overlap_area = min(box_1['ymax'], box_2['ymax']) - max(box_1['ymin'], box_2['ymin'])
    if width_of_overlap_area < 0 or height_of_overlap_area < 0:
        area_of_overlap = 0
    else:
        area_of_overlap = width_of_overlap_area * height_of_overlap_area
    box_1_area = (box_1['ymax'] - box_1['ymin']) * (box_1['xmax'] - box_1['xmin'])
    box_2_area = (box_2['ymax'] - box_2['ymin']) * (box_2['xmax'] - box_2['xmin'])
    area_of_union = box_1_area + box_2_area - area_of_overlap
    if area_of_union == 0:
        return 0
    return area_of_overlap / area_of_union


def resize(image, size, keep_aspect_ratio, interpolation=cv2.INTER_LINEAR):
    if not keep_aspect_ratio:
        return cv2.resize(image, size, interpolation=interpolation)

    iw, ih = image.shape[0:2][::-1]
    w, h = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)
    image = cv2.resize(image, (nw, nh), interpolation=interpolation)
    new_image = np.full((size[1], size[0], 3), 128, dtype=np.uint8)
    dx = (w-nw)//2
    dy = (h-nh)//2
    new_image[dy:dy+nh, dx:dx+nw, :] = image
    return new_image


def preprocess_frame(frame, input_height, input_width, nchw_shape, keep_aspect_ratio):
    in_frame = resize(frame, (input_width, input_height), keep_aspect_ratio)
    if nchw_shape:
        in_frame = in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
    in_frame = np.expand_dims(in_frame, axis=0)
    return in_frame


def get_objects(output, net, new_frame_height_width, source_height_width, prob_threshold, is_proportional):
    objects = list()

    for layer_name, out_blob in output.items():
        out_blob = out_blob.buffer.reshape(net.layers[net.layers[layer_name].parents[0]].out_data[0].shape)
        layer_params = YoloParams(net.layers[layer_name].params, out_blob.shape[2])
        objects += parse_yolo_region(out_blob, new_frame_height_width, source_height_width, layer_params,
                                     prob_threshold, is_proportional)

    return objects


def filter_objects(objects, iou_threshold, prob_threshold):
    # Filtering overlapping boxes with respect to the --iou_threshold CLI parameter
    objects = sorted(objects, key=lambda obj : obj['confidence'], reverse=True)
    for i in range(len(objects)):
        if objects[i]['confidence'] == 0:
            continue
        for j in range(i + 1, len(objects)):
            if intersection_over_union(objects[i], objects[j]) > iou_threshold:
                objects[j]['confidence'] = 0

    return tuple(obj for obj in objects if obj['confidence'] >= prob_threshold)


def async_callback(status, callback_args):
    request, frame_id, frame_mode, frame, start_time, completed_request_results, empty_requests, \
    mode, event, callback_exceptions = callback_args

    try:
        if status != 0:
            raise RuntimeError('Infer Request has returned status code {}'.format(status))

        completed_request_results[frame_id] = (frame, request.output_blobs, start_time, frame_mode == mode.current)

        if mode.current == frame_mode:
            empty_requests.append(request)
    except Exception as e:
        callback_exceptions.append(e)

    event.set()


def put_highlighted_text(frame, message, position, font_face, font_scale, color, thickness):
    cv2.putText(frame, message, position, font_face, font_scale, (255, 255, 255), thickness + 1) # white border
    cv2.putText(frame, message, position, font_face, font_scale, color, thickness)


def await_requests_completion(requests):
    for request in requests:
        request.wait()


class Detector():
    def __init__(self):
        self.ie = IECore()
        self.net = []

        self.keep_aspect_ratio = True

    def destroy(self):
        del self.net 


    def init(self, model, device = 'CPU'):
        config_min_latency = {} #dictionary with settings

        # ------------- 1. Plugin initialization for specified device and load extensions library if specified -------------
        log.info("Creating Inference Engine...")
        ie = IECore()

        if 'CPU' in device:
            config_min_latency['CPU_THROUGHPUT_STREAMS'] = '1'

        if 'GPU' in device:
            config_min_latency['GPU_THROUGHPUT_STREAMS'] = '1'
            #config_min_latency['VPU_HW_STAGES_OPTIMIZATION'] = 'NO' # maybe this fixes differences!? -> https://github.com/openvinotoolkit/openvino/issues/1551

        # -------------------- 2. Reading the IR generated by the Model Optimizer (.xml and .bin files) --------------------
        log.info("Loading network")
        self.net = ie.read_network(model, os.path.splitext(model)[0] + ".bin")

        # ---------------------------------- 3. Load CPU extension for support specific layer ------------------------------
        if "CPU" in device:
            supported_layers = ie.query_network(self.net, "CPU")
            not_supported_layers = [l for l in self.net.layers.keys() if l not in supported_layers]
            if len(not_supported_layers) != 0:
                log.error("Following layers are not supported by the plugin for specified device {}:\n {}".
                        format(device, ', '.join(not_supported_layers)))
                log.error("Please try to specify cpu extensions library path")
                sys.exit(1)

        assert len(self.net.input_info) == 1, "Sample supports only YOLO based single input topologies"

        # ---------------------------------------------- 4. Preparing inputs -----------------------------------------------
        log.info("Preparing inputs")
        self.input_blob = next(iter(self.net.input_info))

        # Read and pre-process input images
        if self.net.input_info[self.input_blob].input_data.shape[1] == 3:
            self.input_height, self.input_width = self.net.input_info[self.input_blob].input_data.shape[2:]
            self.nchw_shape = True
        else:
            self.input_height, self.input_width = self.net.input_info[self.input_blob].input_data.shape[1:3]
            self.nchw_shape = False

        # ----------------------------------------- 5. Loading model to the plugin -----------------------------------------
        log.info("Loading model to the plugin")
        
        self.exec_net = self.ie.load_network(network=self.net, device_name=device,
                                                    config=config_min_latency,
                                                    num_requests=1)


    def detect(self, image, prob_threshold = 0.01, iou_threshold = 0.25 ):
        # ----------------------------------------------- 6. Doing inference -----------------------------------------------
        log.info("Starting inference...")
        #print("To close the application, press 'CTRL+C' here or switch to the output window and press ESC key")
        #print("To switch between min_latency/user_specified modes, press TAB key in the output window")

        # resize input_frame to network size
        frame = preprocess_frame(image, self.input_height, self.input_width, self.nchw_shape, self.keep_aspect_ratio)


        
        start_time = perf_counter()
        # blocking:
        #   output = self.exec_net.infer(inputs={self.input_blob: frame})   
        infer_request_handle = self.exec_net.start_async(request_id=0, inputs={self.input_blob: frame})
        infer_status = infer_request_handle.wait()
        output = infer_request_handle.output_blobs #[out_blob_name]     
        end_time = perf_counter()
        inf_time = end_time - start_time
        log.info('Inference Time was {} Seconds'.format(inf_time))

        log.info( frame.shape )
        log.info( image.shape )


        objects = get_objects(output, self.net, (self.input_height, self.input_width), image.shape[:-1], prob_threshold, self.keep_aspect_ratio)
        objects = filter_objects(objects, iou_threshold, prob_threshold)

        if len(objects):
            log.info(" Class ID | Confidence | XMIN | YMIN | XMAX | YMAX | COLOR ")

        origin_im_size = image.shape[:-1]
        for obj in objects:
            # Validation bbox of detected object
            obj['xmax'] = min(obj['xmax'], origin_im_size[1])
            obj['ymax'] = min(obj['ymax'], origin_im_size[0])
            obj['xmin'] = max(obj['xmin'], 0)
            obj['ymin'] = max(obj['ymin'], 0)
            color = (min(obj['class_id'] * 12.5, 255),
                    min(obj['class_id'] * 7, 255),
                    min(obj['class_id'] * 5, 255))
            det_label = str(obj['class_id'])

            log.info(
                    "{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} | {} ".format(det_label, obj['confidence'],
                                                                            obj['xmin'], obj['ymin'], obj['xmax'],
                                                                            obj['ymax'],
                                                                            color))

            cv2.rectangle(image, (obj['xmin'], obj['ymin']), (obj['xmax'], obj['ymax']), color, 2)
            cv2.putText(image,
                        "#" + det_label + ' ' + str(round(obj['confidence'] * 100, 1)) + ' %',
                        (obj['xmin'], obj['ymin'] - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)

        return image, objects


# __name__ guard 
if __name__ == '__main__':

    import glob

    threshold = .05
    
    # init the detector with the weights stored in the xml file
    det = Detector()
    weights_file = os.path.join( 'DET', 'weights', 'yolov4-tiny.xml')
    det.init(weights_file, device = 'CPU' ) # for VPUs use device = "MYRIAD"

    image_folder = os.path.join( 'data', 'open_field', 'results') 

    for filename in glob.glob( os.path.join( image_folder, '*[!_Detected].png' ) ): # read pngs in a folder
        
        # read the image
        img = cv2.imread(filename)

        # detect persons in the iamge
        dimg, detections = det.detect(img, prob_threshold = threshold)

        # display the detections with opencv
        cv2.imshow( filename, dimg )
    
    # wait for user input
    cv2.waitKey()

