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
        dem_img_file  = os.path.join( lfr_path, 'dem.png' )
        dem_info_file = os.path.join( lfr_path, 'dem_info.json' )
        dem_obj_file  = os.path.join( lfr_path, 'dem.obj' )

        with open(dem_info_file) as json_file:
            self._info = json.load(json_file)

        if 'cornersUTM' in self._info:
            ul_rel_utm = self.relative_utm( [(self._info['cornersUTM'][0][0],self._info['cornersUTM'][0][1])] )
            lr_rel_utm = self.relative_utm( [(self._info['cornersUTM'][1][0],self._info['cornersUTM'][1][1])] )
            pts_min = [ul_rel_utm[0][0],lr_rel_utm[0][1]]
            pts_max = [ul_rel_utm[0][1],lr_rel_utm[0][0]]
        else: # this might be very slow, because it reads every vertex in the OBJ model
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

