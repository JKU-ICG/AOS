#ifndef IMAGE_H
#define IMAGE_H
// implementation from https://github.com/AlexeyAB/darknet

//#include "darknet.h"


#include <stdlib.h>
#include <stdio.h>
#include <float.h>
#include <string.h>
#include <math.h>

#ifdef __unix
#define sprintf_s(buf, size, ...) snprintf((buf), (size), __VA_ARGS__)
#define fopen_s(pFile,filename,mode) ((*(pFile))=fopen((filename),(mode)))==NULL
#endif

enum IMTYPE {PNG, BMP, TGA, JPG};


typedef struct {
    int w; // width
    int h; // heigth
    int c; // number of channels
    float *data; // data
} Image;

/*float get_color(int c, int x, int max);
void flip_image(Image a);
void draw_box(Image a, int x1, int y1, int x2, int y2, float r, float g, float b);
void draw_box_width(Image a, int x1, int y1, int x2, int y2, int w, float r, float g, float b);
void draw_bbox(Image a, box bbox, int w, float r, float g, float b);
void draw_label(Image a, int r, int c, Image label, const float *rgb);
void draw_weighted_label(Image a, int r, int c, Image label, const float *rgb, const float alpha);
void write_label(Image a, int r, int c, Image *characters, char *string, float *rgb);
void draw_detections(Image im, int num, float thresh, box *boxes, float **probs, char **names, Image **labels, int classes);
void draw_detections_v3(Image im, detection *dets, int num, float thresh, char **names, Image **alphabet, int classes, int ext_output);
Image image_distance(Image a, Image b);*/
void scale_image(Image m, float s);
// Image crop_image(Image im, int dx, int dy, int w, int h);
Image random_crop_image(Image im, int w, int h);
Image random_augment_image(Image im, float angle, float aspect, int low, int high, int size);
void random_distort_image(Image im, float hue, float saturation, float exposure);
Image resize_image(Image im, int w, int h);
void copy_image_from_bytes(Image im, char *pdata);
void fill_image(Image m, float s);
void letterbox_image_into(Image im, int w, int h, Image boxed);
//LIB_API Image letterbox_image(Image im, int w, int h);
Image resize_min(Image im, int min);
Image resize_max(Image im, int max);
void translate_image(Image m, float s);
void normalize_image(Image p);
Image rotate_image(Image m, float rad);
void rotate_image_cw(Image im, int times);
void embed_image(Image source, Image dest, int dx, int dy);
void saturate_image(Image im, float sat);
void exposure_image(Image im, float sat);
void distort_image(Image im, float hue, float sat, float val);
void saturate_exposure_image(Image im, float sat, float exposure);
void hsv_to_rgb(Image im);
//LIB_API void rgbgr_image(Image im);
void constrain_image(Image im);
void composite_3d(char *f1, char *f2, char *out, int delta);
int best_3d_shift_r(Image a, Image b, int min, int max);

Image grayscale_image(Image im);
Image threshold_image(Image im, float thresh);

Image collapse_image_layers(Image source, int border);
Image collapse_images_horz(Image *ims, int n);
Image collapse_images_vert(Image *ims, int n);
Image merge_images_channels(Image* ims, int n);

void show_image(Image p, const char *name);
void show_image_normalized(Image im, const char *name);
void save_image_png(Image im, const char *name);
void save_image(Image p, const char *name);
void show_images(Image *ims, int n, char *window);
void show_image_layers(Image p, char *name);
void show_image_collapsed(Image p, char *name);

void print_image(Image m);

Image make_image(int w, int h, int c);
Image make_random_image(int w, int h, int c);
Image make_empty_image(int w=0, int h=0, int c=0);
Image make_uniform_image(int w, int h, int c, float val);
void free_image(Image m);
Image float_to_image_scaled(int w, int h, int c, float *data);
Image float_to_image(int w, int h, int c, float *data);
Image copy_image(Image p);
void copy_image_inplace(Image src, Image dst);
Image load_image(const char *filename, int w = 0, int h  = 0, int c = 0);
Image load_image_stb(const char* filename, int channels = 0);
Image load_image_stb_resize(char *filename, int w, int h, int c);
bool is_empty_image(Image img); // { return img.c == 0 || img.w == 0 || img.h == 0; }
Image prepare_image_ogl(Image src, int channels = 0);
//LIB_API Image load_image_color(char *filename, int w, int h);
//Image **load_alphabet();

float get_pixel(Image m, int x, int y, int c);
float get_pixel_extend(Image m, int x, int y, int c);
void set_pixel(Image m, int x, int y, int c, float val);
void add_pixel(Image m, int x, int y, int c, float val);
float bilinear_interpolate(Image im, float x, float y, int c);

Image get_image_layer(Image m, int l);

void test_resize(char *filename);

#endif
