import numpy as np
import os
import json
import matplotlib.pyplot as plt
import cv2
import utm


def read_dem(DemFileName):
    """ reads the verticex coordinates from the digital elevation model """
    Count = 0
    dem_pts = np.zeros(shape=(3,0))
    with open(DemFileName) as DemFile: 
        Line = DemFile.readline() 
        while True: 
            Line = DemFile.readline() 
            if not Line: 
                break
            CheckVertex = Line.split(' ')

            if 'v' in CheckVertex:
                VertexEast = float(CheckVertex[1])
                VertexNorth = float(CheckVertex[2])
                Height = -(float(CheckVertex[3]))

                dem_pts = np.column_stack( (dem_pts,[VertexEast,VertexNorth,Height]) )
            else :
                break
            Count = Count + 1
    return dem_pts

def unique_with_TOL(a, TOL=3.0):
    b = a.copy()
    b.sort()
    d = np.append(2*TOL, np.diff(b))
    return b[np.abs(d)>TOL]

class Visualizer :
    """A class that handles visualization of various data on dem/satellite images"""
    _img = None
    _info = None
    _pts = None

    def  __init__(self, lfr_path):
        dem_img_file = os.path.join( lfr_path, 'dem.png' )
        dem_info_file = os.path.join( lfr_path, 'dem_info.json' )
        dem_obj_file = os.path.join( lfr_path, 'dem.obj' )

        with open(dem_info_file) as json_file:
            self._info = json.load(json_file)

        if 'cornersUTM' in self._info:
            ul_rel_utm = self.relative_utm( [(self._info['cornersUTM'][0][0],self._info['cornersUTM'][0][1])] )
            lr_rel_utm = self.relative_utm( [(self._info['cornersUTM'][1][0],self._info['cornersUTM'][1][1])] )
            pts_min = [ul_rel_utm[0][0],lr_rel_utm[0][1]]
            pts_max = [ul_rel_utm[0][1],lr_rel_utm[0][0]]
        else: # this might be very slow
        #if True:
            self._pts = read_dem( dem_obj_file )
            pts_min = np.amin(self._pts, axis=1)
            pts_max = np.amax(self._pts, axis=1)

        self._img = cv2.imread( dem_img_file )


        self._fig = plt.figure(figsize=(10,10), dpi=100)
        self._ax = self._fig.add_subplot(111)
        plt.imshow(self._img, extent=(pts_min[0],pts_max[0],pts_min[1],pts_max[1]))

    def rel_pts( self, pts, format='latlon' ):
        if format == 'latlon':
            utm_pts = []
            for pt in pts:
                utm_pts.append( utm.from_latlon( pt[0], pt[1] ) )
        elif format == 'utm':
            utm_pts = pts
        else:
            raise Exception("wrong format!")
        
        return self.relative_utm( utm_pts )
    
    def relative_utm( self, utm_pts ):
        rel_pts = []
        for utm_pt in utm_pts:
            #rel_pts.append(  (utm_pt[0] - self._info['centerUTM'][0], self._info['centerUTM'][1] - utm_pt[1]) ) # <-- how it is done in Indrajit's code
            rel_pts.append(  (utm_pt[0] - self._info['centerUTM'][0], utm_pt[1] - self._info['centerUTM'][1]) )
        return rel_pts

    def draw_points( self, pts, format='latlon', color='red', marker='o' ):
        
        rel_pts = self.rel_pts(pts,format)
        plt.scatter( [pt[0] for pt in rel_pts], [pt[1] for pt in rel_pts], c=color, marker=marker )
    
    def draw_lines( self, pts, format='latlon', color='black', marker='.', linestyle='-' ):
       
        rel_pts = self.rel_pts(pts,format)
        plt.plot( [pt[0] for pt in rel_pts], [pt[1] for pt in rel_pts], color=color, marker=marker, linestyle=linestyle )

    def draw_grid( self, corner_pts, format='latlon', color='white' ):
        rel_pts = self.rel_pts(corner_pts,format)
        xs = unique_with_TOL( np.round([pt[0] for pt in rel_pts]) )
        ys = unique_with_TOL( np.round([pt[1] for pt in rel_pts]) )

        self._ax.set_xticks( xs )
        self._ax.set_yticks( ys )
        plt.grid(True, color=color)



    def show(self):
        plt.show()

    def save(self, out_file='path_visualized.png'):
        #plt.show()
        plt.savefig( out_file )


# __name__ guard 
if __name__ == '__main__':    

    anaos_data_path = os.getenv( 'ANAOS_DATA' )
    if anaos_data_path is None:
        print( 'ERROR: ANAOS_DATA environment variable not set!' )

    sitename = 'Test20201125F1'
    lfr_path = os.path.join( anaos_data_path,  'SITES', sitename, 'LFR' )
    vis = Visualizer( lfr_path )

    #with open(dem_info_file) as json_file:
    #    dem_info = json.load(json_file)

    vis = Visualizer( lfr_path )
    #vis.show()

    gps_center = (48.33982543166233, 14.33278645776759)
    utm_center = utm.from_latlon( gps_center[0], gps_center[1] )
    gps_start = (48.33953283899105, 14.330601511900792)

    vis.draw_points( [gps_start,gps_center,(gps_center[0]+0.001, gps_center[1]+0.001)] )
    vis.draw_lines( [gps_start,gps_center,(gps_center[0]+0.001, gps_center[1]+0.001)] )
    vis.draw_grid( zip([48.33955085, 48.3395532,  48.33955555, 48.3395579,  48.33956025, 48.33982073,
        48.33982309, 48.33982543, 48.33982778, 48.33983013, 48.34009062, 48.34009297,
        48.34009532, 48.34009766, 48.34010001], [14.33197332, 14.33197684, 14.33198037, 14.33237813, 14.33238165, 14.33238517,
        14.33278294, 14.33278646, 14.33278998, 14.33318775, 14.33319127, 14.33319478,
        14.33359255, 14.33359607, 14.33359959]) )
    vis.show()

    if False:
        print(dem_info)

        dem_img = cv2.imread( dem_img_file )

        dem_pts = read_dem( dem_obj_file )
        print(dem_pts.shape)
        print( "min: " + str(np.amin(dem_pts, axis=1)) )
        print( "max: " + str(np.amax(dem_pts, axis=1)) )

        pts_min = np.amin(dem_pts, axis=1)
        pts_max = np.amax(dem_pts, axis=1)

        plt.imshow(dem_img, extent=(pts_min[0],pts_max[0],pts_min[1],pts_max[1]))
        #plt.scatter(dem_pts[0,:], dem_pts[1,:], marker='o')
        plt.show()



