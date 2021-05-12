import time
import shutil
import os
from pathlib import Path
import glob
import numpy as np
import math
import json
import utm
import math
import threading
from scipy import interpolate
import matplotlib.pyplot as plt
import logging
from statistics import mean 

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logging.basicConfig(level=logging.DEBUG)

def setup_logger(name, log_file, level=logging.DEBUG):
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def compute_end_point(start_pos,next_pos,max_path_length) :
    start_East,start_North,start_Block,start_UTMZone = utm.from_latlon(start_pos[0],start_pos[1])
    next_East,next_North,next_Block,next_UTMZone = utm.from_latlon(next_pos[0],next_pos[1])
    nextposdistance = compute_distance_bw_2gpsPoints(start_pos,next_pos)
    #finemovingdirectionvector = (((start_East - next_East) / nextposdistance)*max_path_length,((start_North - next_North) / nextposdistance)*max_path_length) 
    #print('max_path_length',max_path_length)
    #end_pos_utm = (start_East, start_North) + finemovingdirectionvector
    end_pos_utm = (start_East+(((next_East - start_East) / nextposdistance)*max_path_length),start_North + (((next_North - start_North) / nextposdistance)*max_path_length)) 
    print('start and end utm',(start_East,start_North),end_pos_utm  )
    end_pos_Lat,end_pos_Lon  = utm.to_latlon(end_pos_utm[0],end_pos_utm[1],start_Block,next_UTMZone)
    end_pos = (end_pos_Lat,end_pos_Lon)
    print('compute end point',start_pos, end_pos,compute_distance_bw_2gpsPoints(start_pos,end_pos))
    assert(compute_distance_bw_2gpsPoints(start_pos,end_pos) < max_path_length +3)
    return end_pos

def compute_distance_bw_2gpsPoints(Prev_Pos,Next_Pos) :
    Prev_East,Prev_North,Prev_Block,Prev_UTMZone = utm.from_latlon(Prev_Pos[0],Prev_Pos[1])
    Next_East,Next_North,Next_Block,Next_UTMZone = utm.from_latlon(Next_Pos[0],Next_Pos[1])
    Distance = (math.sqrt((Prev_East - Next_East)**2 + (Prev_North - Next_North)**2))
    return Distance

def findwaypointsinfo(Row,Col, gps_grid_waypoints, prev_waypoint, prev_North_dir) :
    MinDistance = 10000
    MinIndex = None
    Flag = []
    Nextpos = []
    FlyingNorthDir = None
    for i in range(4) :
        Distance = compute_distance_bw_2gpsPoints(prev_waypoint,(gps_grid_waypoints[Row,Col,i,0],gps_grid_waypoints[Row,Col,i,1]))
        if prev_North_dir is not None :
            if prev_North_dir :
                if i == 1 or i == 3 :
                    Distance = 10000
            else :
                if i == 0 or i == 2 :
                    Distance = 10000
        if Distance < MinDistance :
            MinDistance = Distance
            MinIndex = i
    
    if MinDistance < 1 :
        if MinIndex < 2 :
            Nextpos.append((gps_grid_waypoints[Row,Col,MinIndex+2,0],gps_grid_waypoints[Row,Col,MinIndex+2,1]))
        else :
            Nextpos.append((gps_grid_waypoints[Row,Col,MinIndex-2,0],gps_grid_waypoints[Row,Col,MinIndex-2,1]))
        Flag.append(True)
    else :
        if MinIndex < 2 :
            Nextpos.append((gps_grid_waypoints[Row,Col,MinIndex,0],gps_grid_waypoints[Row,Col,MinIndex,1]))
            Flag.append(False)
            Nextpos.append((gps_grid_waypoints[Row,Col,MinIndex+2,0],gps_grid_waypoints[Row,Col,MinIndex+2,1]))
            Flag.append(True)
        else :
            Nextpos.append((gps_grid_waypoints[Row,Col,MinIndex,0],gps_grid_waypoints[Row,Col,MinIndex,1]))
            Flag.append(False)
            Nextpos.append((gps_grid_waypoints[Row,Col,MinIndex-2,0],gps_grid_waypoints[Row,Col,MinIndex-2,1]))
            Flag.append(True)
    if MinIndex == 0 or MinIndex == 2 :
        FlyingNorthDir = False
    else :
        FlyingNorthDir = True

    assert len(Flag) == len(Nextpos), "flag array and nextpos array size differ!"
    return Nextpos,Flag,FlyingNorthDir



def compute_Aexp(Cov, P, GPSCenterPoints, current_pos , NormalizedDistance):
    assert( Cov.shape == P.shape )
    Aexp = np.ones(Cov.shape)
    CurrentPosEast,CurrentPosNorth,Block,UtmZone = utm.from_latlon(current_pos[0],current_pos[1])
    si = CurrentPosEast
    sj = CurrentPosNorth
    for i in range(Cov.shape[0]):    
        for j in range(Cov.shape[1]):
            B = (P[i][j]*Cov[i][j]) 
            #C = math.exp(math.sqrt((i - si)**2 + (j - sj)**2))
            CellEast,CellNorth,Block,UTMzone = utm.from_latlon(GPSCenterPoints[i,j,0],GPSCenterPoints[i,j,1])
            if NormalizedDistance <= 0:
                # ignore the distance
                C = 1.0
            else:
                C = math.exp((math.sqrt((CellEast - si)**2 + (CellNorth - sj)**2))/NormalizedDistance) 
            #C = C /  NormalizedDistance
            D = (B / C)  if C != 0 else 0   
            Aexp[i][j] = D  
            #print(B, C, D, i, j, Aexp[i][j])
    return Aexp

def compute_Navg(Cov, P, GPSCenterPoints, current_pos, selected_cells, Ncycle , NormalizedDistance):
    assert( Cov.shape == P.shape )
    Navg = np.ones(Cov.shape)
    CurrentPosEast,CurrentPosNorth,Block,UtmZone = utm.from_latlon(current_pos[0],current_pos[1])
    si = CurrentPosEast
    sj = CurrentPosNorth
    #print(selected_cells)
    sumNb = 0
    
    for i_c in range(len(selected_cells[0])):
        print('i_c',i_c)
        i = selected_cells[0][i_c]
        j = selected_cells[1][i_c]
        print('i,j',i,j)
        print('Ncycle',Ncycle)
        i2 = i - Ncycle  
        if i2 < 0: i2 = 0
        j2 = j - Ncycle 
        if j2 < 0: j2 = 0
        i3 = i + Ncycle 
        if i3 > Cov.shape[0]: i3 = Cov.shape[0]
        j3 = j + Ncycle 
        if j3 > Cov.shape[1]: j3 = Cov.shape[1]
        print('i2,i3,j2,j3',i2,i3,j2,j3)
        for ii in range(i2,i3):
            for jj in range(j2,j3):
                B = (P[ii][jj])
                #C = math.sqrt((ii - si)**2 + (jj - sj)**2)  
                CellEast,CellNorth,Block,UTMzone = utm.from_latlon(GPSCenterPoints[ii,jj,0],GPSCenterPoints[ii,jj,1])
                if NormalizedDistance <= 0:
                    # ignore the distance
                    C = 1.0
                else:
                    C = math.exp((math.sqrt((CellEast - si)**2 + (CellNorth - sj)**2))/NormalizedDistance) 
                #C = C /  NormalizedDistance
                D = (B / C)  if C != 0 else 0 
                sumNb = sumNb + D  
        Navg[i][j] = sumNb           
    return Navg


#A matrix with original Prob. values
def compute_Ap(Cov, P, GPSCenterPoints, current_pos , NormalizedDistance):
    assert( Cov.shape == P.shape )
    Ap = np.ones(Cov.shape)
    CurrentPosEast,CurrentPosNorth,Block,UtmZone = utm.from_latlon(current_pos[0],current_pos[1])
    si = CurrentPosEast
    sj = CurrentPosNorth
    for i in range(Cov.shape[0]):    
        for j in range(Cov.shape[1]):
            B = (P[i][j]*Cov[i][j]) 
            C = 1 #math.exp(math.sqrt((i - si)**2 + (j - sj)**2))  
            D = (B / C)  if C != 0 else 0   
            Ap[i][j] = D  
            #print(B, C, D, i, j, Aexp[i][j])
    return Ap

#A matrix with square root
def compute_Asqt(Cov, P, GPSCenterPoints, current_pos , NormalizedDistance):
    assert( Cov.shape == P.shape )
    Asqt = np.ones(Cov.shape)
    si = current_pos[0]
    sj = current_pos[1]
    for i in range(Cov.shape[0]):    
        for j in range(Cov.shape[1]):
            B = (P[i][j]*Cov[i][j]) 
            #C = math.sqrt((i - si)**2 + (j - sj)**2)
            CellEast,CellNorth,Block,UTMzone = utm.from_latlon(GPSCenterPoints[i,j,0],GPSCenterPoints[i,j,1])
            C = math.exp((math.sqrt((CellEast - si)**2 + (CellNorth - sj)**2))/NormalizedDistance) 
            #C = C /  NormalizedDistance  
            D = (B / C)  if C != 0 else 0   
            Asqt[i][j] = D  
            #print(B, C, D, i, j, Aexp[i][j])
    return Asqt

# ---------------------------------------------------------------------------------------------------
class Planner :
    """A planner that handles waypoint creation and planning"""
    _prob_map = None
    _gps_grid = None
    _fine_gps_grid = None
    _utm_grid = None
    #Indrajit:-20201126
    _utm_corner_grid = None
    _gps_corner_grid = None
    _utm_cell_vertical_center_grid = None
    _gps_cell_vertical_center_grid = None
    _utm_cell_horizontal_center_grid = None
    _gps_cell_horizontal_center_grid = None
    _utm_grid_waypoints = None
    _gps_grid_waypoints = None
    _grid_aligned_pathplan = False
    _prev_waypoint = None
    _prev_flying_north  = None
    _prev_index  = None
    _fine_utm_corner_grid = None
    _fine_gps_corner_grid = None
    _fine_utm_grid_waypoints = None
    _fine_gps_grid_waypoints = None
    _fine_average_loc = False

    _fine_utm_grid = None
    _coverage_map = None
    _prev_coverage_index = None # the index that was previously updated
    _fine_coverage_map = None
    _planned_gps_points = []
    _planned_gps_points_flag = []
    _conf_threshold = 0.1
    _use_fine_grid = False
    _tile_size = 30
    _fine_tile_size = 30/4
    _lock = None
    _count_planpoints = 0
    _count_update = 0

    # debugging things:
    _debug = False
    _fig = None
    _ax = None

    # logging
    _log = None
    _detection_log = None
    _out_folder = None
    # nicer visualization
    _vis = None

    def  __init__(self, utm_center, area_size, prob_map=None, tile_distance=30, fine_subdiv=5, conf_threshold=0.05, debug=False, results_folder='planning_results', vis=None, gridalignedplanpath = True):
        
        if not os.path.isdir( results_folder ): 
            os.mkdir( results_folder)
        self._log = setup_logger( 'Planning_logger', os.path.join( results_folder, 'PlanningLog.log') )
        self._detection_log = setup_logger( 'Detections_logger', os.path.join( results_folder,'DetectionsLog.log') )
        self._out_folder = results_folder
        
        self._lock = threading.Lock()
        self._conf_threshold = conf_threshold
        self._tile_size = tile_distance
        self._fine_tile_size = tile_distance / fine_subdiv
        self._grid_aligned_pathplan = gridalignedplanpath
            
        utm_corners = compute_corners( utm_center, area_size )
        gps_corners = utm_list_to_gps( utm_corners )
        self._utm_grid, self._gps_grid, self._utm_corner_grid, self._gps_corner_grid, self._utm_grid_waypoints, self._gps_grid_waypoints = compute_grid( utm_center, area_size, tile_distance  )
        #self._utm_grid, self._gps_grid, self._utm_corner_grid, self._gps_corner_grid,  self._utm_cell_vertical_center_grid, self._gps_cell_vertical_center_grid, self._utm_cell_horizontal_center_grid, self._gps_cell_horizontal_center_grid, self._utm_grid_waypoints,self._gps_grid_waypoints = compute_grid( utm_center, area_size, tile_distance  )
        #self._fine_utm_grid, self._fine_gps_grid = compute_grid( utm_center, area_size, tile_distance/fine_subdiv  )
        #plt.plot(fine_gps_grid[:,:,0].flatten(), fine_gps_grid[:,:,1].flatten(), 'x', lw=2) # grid centers

        if prob_map is not None:
            self._prob_map = prob_map
            assert self._gps_grid.shape[0:2] == prob_map.shape
        else:
            self._prob_map = np.zeros( self._gps_grid.shape[0:2] )
            self._prob_map.fill(conf_threshold)

        self._coverage_map = np.ones(self._prob_map.shape)
        assert self._gps_grid.shape[0:2] == self._prob_map.shape
        assert self._coverage_map.shape == self._prob_map.shape
        self._vis = vis

        self._debug = debug
        if self._debug:
            gps_center = utm.to_latlon( *utm_center )

            if self._vis is not None:
                #self._vis.draw_points( [gps_center] ) # center
                self._vis.draw_points( gps_corners, marker='+', color='green' ) #corners of area
                self._vis.draw_points( zip(self._gps_grid[:,:,0].flatten(), self._gps_grid[:,:,1].flatten()), marker='s', color='white') # grid centers
                self._vis.draw_grid( zip(self._gps_corner_grid[:,:,0].flatten(), self._gps_corner_grid[:,:,1].flatten()), color='white') # grid corners
                #print( np.unique(self._gps_corner_grid[:,:,0].flatten()) )
                #print( np.unique(self._gps_corner_grid[:,:,1].flatten()) )
                #self._vis.draw_points( zip(self._gps_cell_vertical_center_grid[0,0,0].flatten(), self._gps_cell_vertical_center_grid[0,0,1].flatten()), marker='+', color='white') # grid centers
                #self._vis.draw_points( zip(self._gps_cell_horizontal_center_grid[0,0,0].flatten(), self._gps_cell_horizontal_center_grid[0,0,1].flatten()), marker='+', color='black') # grid centers
                self._vis.draw_points( zip(self._gps_grid_waypoints[:,:, :, 0].flatten(), self._gps_grid_waypoints[:,:, :, 1].flatten()), marker='+', color='white') # grid centers

                self._vis.save( os.path.join( self._out_folder, 'vis_grid.png') )
            else:
                # plot everything in lat/lon
                self._fig = plt.figure()
                self._ax = self._fig.add_subplot(111)
                
                plt.plot(gps_center[0], gps_center[1], 'x', c='y', lw=2) # center
                plt.plot([c[0] for c in gps_corners], [c[1] for c in gps_corners], '+', c='dimgray', lw=2)
                plt.plot(self._gps_grid[:,:,0].flatten(), self._gps_grid[:,:,1].flatten(), 's', c='gray', lw=2) # grid centers

                plt.savefig( os.path.join( self._out_folder, 'grid.png') )

            #plt.show()

    def planpoints(self, current_gps_pos):
        with self._lock:
            self._count_planpoints += 1
            self._log.debug( "planning {} path for current point {:f}, {:f}".format( 'coarse' if not self.useFineSampling() else 'fine', current_gps_pos[0],current_gps_pos[1]))
            if not self._grid_aligned_pathplan :
                if self.useFineSampling():
                    next_pts, cov_fine_index = self.planpath( current_gps_pos, self._fine_gps_grid, self._fine_coverage_map, self._fine_prob_map, norm_distance=0, num_points=1 )
                    self._log.debug( "fine coverage map: " + str(self._fine_coverage_map) )
                else:
                    next_pts, cov_index = self.planpath( current_gps_pos, self._gps_grid, self._coverage_map, self._prob_map, self._tile_size, num_points=1 )
                    self._prev_coverage_index = cov_index
                    self._log.debug( "coarse coverage map: " + str(self._coverage_map) )
            else :
                if self.useFineSampling():
                    next_pts, self._prev_index,planned_gps_points_flag,self._prev_waypoint,self._prev_flying_north = self.gridalignedplanpath( current_gps_pos, self._prev_waypoint, self._prev_flying_north, self._prev_index, self._fine_gps_grid, self._fine_gps_grid_waypoints, self._fine_coverage_map, self._fine_prob_map, norm_distance=0, num_points=1 )
                    self._log.debug( "fine coverage map: " + str(self._fine_coverage_map) )
                else:
                    next_pts, self._prev_index,planned_gps_points_flag,self._prev_waypoint,self._prev_flying_north = self.gridalignedplanpath( current_gps_pos, self._prev_waypoint, self._prev_flying_north, self._prev_index, self._gps_grid, self._gps_grid_waypoints, self._coverage_map, self._prob_map, self._tile_size, num_points=1 )
                    self._prev_coverage_index = self._prev_index
                    self._log.debug( "coarse coverage map: " + str(self._coverage_map) )
               
            
            self._log.debug( "planned {} points for line {}:".format( len(next_pts), self._count_planpoints ) + str(next_pts) )
            if self._debug and len(next_pts) > 0:
                if len(self._planned_gps_points) > 0 :
                    pts = np.row_stack( (self._planned_gps_points[-1] [-1], next_pts) )
                    #flags = np.row_stack( (self._planned_gps_points_flag[-1], planned_gps_points_flag) )
                else:
                    pts = np.row_stack( (current_gps_pos, next_pts) ) # first line!
                    #flags = np.row_stack( ([False], planned_gps_points_flag[0]) )
                    #flags = np.row_stack( (flags, planned_gps_points_flag[1]) )
                color='b' if self.useFineSampling() else 'g'

                if self._vis is not None:
                    self._vis.draw_points( [current_gps_pos], marker='x', color=color ) # current
                    for i in range(len(next_pts)):
                        if i == 0: # first point
                            p_pt = pts[0] # previous point
                        else:
                            p_pt = next_pts[i-1] # previous point
                        if planned_gps_points_flag[i]: # waypoint with recording
                            self._vis.draw_lines( zip([p_pt[0],next_pts[i][0]], [p_pt[1],next_pts[i][1]] ), linestyle='--', color=color )
                        else: # not recording (drone flies faster too)
                            self._vis.draw_lines( zip([p_pt[0],next_pts[i][0]], [p_pt[1],next_pts[i][1]] ), linestyle=':', color=color )
                    #self._vis.draw_lines( zip([c[0] for c in pts], [c[1] for c in pts]), linestyle=':', color=color ) #corners of area
                    self._vis.draw_points( zip([c[0] for c in next_pts], [c[1] for c in next_pts]), marker='+', color=color ) # planned positions

                    self._vis.save( (os.path.join( self._out_folder, 'vis_planpoints_{}.png').format(self._count_planpoints)) )
                else:
                    plt.plot(current_gps_pos[0], current_gps_pos[1], 'x', c='b' if self.useFineSampling() else 'g' , lw=2)
                    plt.plot([c[0] for c in pts], [c[1] for c in pts], ':', c='b' if self.useFineSampling() else 'g' , lw=2)
                    plt.plot([c[0] for c in next_pts], [c[1] for c in next_pts], 'P', c='b' if self.useFineSampling() else 'g' , lw=2, markersize=10)

                    plt.savefig(os.path.join( self._out_folder, 'planpoints_{}.png').format(self._count_planpoints))

            
            self._planned_gps_points.append( next_pts )
            if  self._grid_aligned_pathplan :
                self._planned_gps_points_flag.append(planned_gps_points_flag)   
                assert len(next_pts) == len(planned_gps_points_flag), "planpoints: length of points does not match the length of the recording flags!"
                return next_pts, planned_gps_points_flag
            else :
                return next_pts


    @staticmethod
    def planpath(current_gps_pos, gps_grid, coverage_map, prob_map, norm_distance, num_points=1, max_path_length = 30.0 ):
        flight_finished = np.all(coverage_map==0)
        planned_gps_points = []
        planned_path_length, prev_path_length = 0.0, 0.0
        print('norm distance',norm_distance)
        Navg_cycles = 2
        last_index = None
        while not flight_finished :
            A = compute_Aexp(coverage_map,prob_map, gps_grid, current_gps_pos, norm_distance)
            # find the index of maximum A
            max_pos = np.where(A == np.amax(A))
            if len(max_pos[0]) == 1:
                next_pos = (gps_grid[max_pos[0][0],max_pos[1][0],0], gps_grid[max_pos[0][0],max_pos[1][0],1])
                RowPos = int(max_pos[0][0])
                ColPos = int(max_pos[1][0])
                print(RowPos,ColPos)
                coverage_map[RowPos ,ColPos]=0
                #prob_map[RowPos ,ColPos]=0
            else:
                #Navg_cycles = 1 # increase the neighbourhood until we find a clear winner
                while len(max_pos[0]) > 1:
                    Pg = compute_Navg(coverage_map,prob_map, gps_grid, current_gps_pos, max_pos, Navg_cycles ,  norm_distance )
                    print(Pg)
                    max_pos = np.where(Pg == np.amax(Pg))
                    Navg_cycles = Navg_cycles + 1
                
                next_pos = (gps_grid[max_pos[0][0],max_pos[1][0],0], gps_grid[max_pos[0][0],max_pos[1][0],1])
                RowPos = int(max_pos[0][0])
                ColPos = int(max_pos[1][0])
                print(RowPos,ColPos)
                coverage_map[RowPos ,ColPos]=0
                #prob_map[RowPos ,ColPos]=0
            last_index = (RowPos,ColPos)
            planned_gps_points.append(next_pos)
            if norm_distance <= 0.0 :
                print('normdistance', norm_distance)
                prev_path_length = planned_path_length
                planned_path_length = planned_path_length + compute_distance_bw_2gpsPoints(current_gps_pos,next_pos)
                print('planned_path_length', planned_path_length)
                #For Single 30m Line
                if num_points <= 1 :
                    end_pos = compute_end_point(current_gps_pos,next_pos,max_path_length)
                    #planned_gps_points.append(end_pos)
                    planned_gps_points[-1] = end_pos
                    planned_path_length = planned_path_length + compute_distance_bw_2gpsPoints(next_pos,end_pos)
                else :
                    if planned_path_length >= max_path_length :
                        end_pos = compute_end_point(current_gps_pos,next_pos,(max_path_length - prev_path_length))
                        #planned_gps_points.append(end_pos)
                        planned_gps_points[-1] = end_pos
                        planned_path_length = planned_path_length + compute_distance_bw_2gpsPoints(next_pos,end_pos)
                        
                    
                #For Single 30m Line
                print('planned_path_length', planned_path_length)
            else :
                print('normdistance', norm_distance)
                planned_path_length = 0.0
            current_gps_pos = next_pos
            # check if we are done
            flight_finished = np.all(coverage_map==0) or len(planned_gps_points) >= num_points or planned_path_length >= max_path_length  # compute distance with gps_points and check
        return planned_gps_points, last_index
    
    @staticmethod
    def gridalignedplanpath(current_gps_pos, prev_waypoint, prev_flying_north, prev_index, gps_grid, gps_grid_waypoints, coverage_map, prob_map, norm_distance, num_points=1, max_path_length = 30.0 ):
        flight_finished = np.all(coverage_map==0)
        planned_gps_points = []
        planned_gps_points_flag = []
        print('norm distance',norm_distance)
        Navg_cycles = 2
        last_index = None
        next_last_waypoint = None
        next_flying_north = None
        if prev_waypoint is None :
            prev_waypoint = current_gps_pos
        while not flight_finished :
            if norm_distance <= 0.0 :
                prev_north_dir = prev_flying_north
                planned_gps_points, planned_gps_points_flag,next_flying_north = findwaypointsinfo(0,0, gps_grid_waypoints, prev_waypoint, prev_north_dir)
                last_index = prev_index
            else :
                prev_north_dir = None
                A = compute_Aexp(coverage_map,prob_map, gps_grid, prev_waypoint, norm_distance)
                # find the index of maximum A
                max_pos = np.where(A == np.amax(A))
                if len(max_pos[0]) == 1:
                    planned_gps_points, planned_gps_points_flag,next_flying_north = findwaypointsinfo(max_pos[0][0],max_pos[1][0], gps_grid_waypoints, prev_waypoint, prev_north_dir)
                    RowPos = int(max_pos[0][0])
                    ColPos = int(max_pos[1][0])
                    print(RowPos,ColPos)
                    coverage_map[RowPos ,ColPos]=0
                    #prob_map[RowPos ,ColPos]=0
                else:
                    #Navg_cycles = 1 # increase the neighbourhood until we find a clear winner
                    while len(max_pos[0]) > 1:
                        Pg = compute_Navg(coverage_map,prob_map, gps_grid, prev_waypoint, max_pos, Navg_cycles ,  norm_distance )
                        print(Pg)
                        max_pos = np.where(Pg == np.amax(Pg))
                        Navg_cycles = Navg_cycles + 1
                    
                    planned_gps_points, planned_gps_points_flag,next_flying_north = findwaypointsinfo(max_pos[0][0],max_pos[1][0], gps_grid_waypoints, prev_waypoint, prev_north_dir)
                    RowPos = int(max_pos[0][0])
                    ColPos = int(max_pos[1][0])
                    print(RowPos,ColPos)
                    coverage_map[RowPos ,ColPos]=0
                    #prob_map[RowPos ,ColPos]=0
                last_index = (RowPos,ColPos)
            # check if we are done
            flight_finished = np.all(coverage_map==0) or len(planned_gps_points) >= num_points  # compute distance with gps_points and check
        if  len(planned_gps_points) >= 1 :   
            next_last_waypoint = planned_gps_points[-1]
        return planned_gps_points, last_index, planned_gps_points_flag,next_last_waypoint,next_flying_north

    def update( self, line_ct_pt_gps, detections ): # FORMAT  of        detections = [{'gps': prev_pt, 'conf': 0.5}, {'gps': next_pt, 'conf': 0.1, }]
        with self._lock:
            self._count_update += 1
            self._log.debug( "update for camera {:f}, {:f} with {} detections".format( line_ct_pt_gps[0],line_ct_pt_gps[1], len(detections) ) )
            if self._prev_coverage_index is not None:
                closest_index = self._prev_coverage_index #
            else:
                closest_index = closest_point( line_ct_pt_gps, self._gps_grid )
                assert True, "This should not happen! You called update before planpoints!"
            #print( "close point: " + str(closest_index) )

            # get maximum detection
            confs = [ det['conf'] for det in detections ]
            if len(confs) > 0:
                max_conf = np.amax( confs )
                max_conf_index = np.where(confs == np.amax(confs))
                print(max_conf_index[0][0])
                max_conf_det = detections[int(max_conf_index[0][0])]
                max_conf_pos = max_conf_det['gps']
            else:
                max_conf = 0
                max_conf_pos = line_ct_pt_gps
            
            det_center_east = []
            det_center_north = []
            det_block = None
            det_utmzone = None
            for det in detections:
                if det['conf'] >= self._conf_threshold:
                    gps_loc = det['gps']
                    det_east,det_north,det_block,det_utmzone = utm.from_latlon(gps_loc[0],gps_loc[1])
                    det_center_east.append(det_east)
                    det_center_north.append(det_north)
                    self._log.debug( "detections in index ({}, {}) of probability map with {:f} confidence at ({}, {}).".format( closest_index[0], closest_index[1], det['conf'], gps_loc[0],gps_loc[1]) )
            
            if len(confs) > 0:
                average_det_east = mean(det_center_east)
                average_det_north = mean(det_center_north)
                averagegpslat,averagegpslon = utm.to_latlon(average_det_east,average_det_north,det_block,det_utmzone)
                averagedet_pos = (averagegpslat,averagegpslon)
            else :
                averagedet_pos = line_ct_pt_gps
            
            if not self._fine_average_loc:
                averagedet_pos = max_conf_pos

            
            #print( "maximum conf: " + str(max_conf) )
            self._prob_map[closest_index[0], closest_index[1]] = max_conf # update probability map!
            self._log.debug( "updating index ({}, {}) of probability map with {:f} confidence.".format( closest_index[0], closest_index[1], max_conf ) )
            self._log.debug( "probability map: " + str(self._prob_map) )
            if len(confs) > 0:
                self._log.debug( "average_det_loc: ({}, {}) " .format( averagegpslat, averagegpslon) )

            if self.useFineSampling():
                self.finishFineSampling( )
            elif max_conf > self._conf_threshold:
                # Do fine sampling in the next iteration
                if not self._grid_aligned_pathplan :
                    self.startFineSampling( line_ct_pt_gps, detections )
                else :
                    #self.startFineSampling(max_conf_pos , detections )
                    self.startFineSampling(averagedet_pos , detections )

            if self._debug:
                if self._vis is not None:
                    self._vis.draw_points( [line_ct_pt_gps], marker='^', color='k' ) # current camera
                    self._vis.save(os.path.join( self._out_folder, 'vis_update_{}.png'.format(self._count_update)))
                else:
                    plt.plot(line_ct_pt_gps[0], line_ct_pt_gps[1], '^', c='k', lw=2, markersize=10)
                    plt.savefig(os.path.join( self._out_folder, 'update_{}.png'.format(self._count_update)))


    def startFineSampling( self, ct_pt_gps, detections ):
        self._log.debug( "starting fine sampling for center point {:f}, {:f} with {} detections".format( ct_pt_gps[0],ct_pt_gps[1], len(detections) ) )
        self._use_fine_grid = True 
        utm_center = utm.from_latlon( ct_pt_gps[0], ct_pt_gps[1] ) 
        if not self._grid_aligned_pathplan :
            self._fine_utm_grid, self._fine_gps_grid, self._fine_utm_corner_grid, self._fine_gps_corner_grid, self._fine_utm_grid_waypoints, self._fine_gps_grid_waypoints = compute_grid( utm_center, (self._tile_size, self._tile_size), self._fine_tile_size  )
        else :
            self._fine_utm_grid, self._fine_gps_grid, self._fine_utm_corner_grid, self._fine_gps_corner_grid, self._fine_utm_grid_waypoints, self._fine_gps_grid_waypoints = compute_grid( utm_center, (self._tile_size, self._tile_size), self._tile_size  )

        self._fine_coverage_map = np.zeros(self._fine_utm_grid.shape[0:2]) # init with empty
        self._fine_prob_map = np.zeros(self._fine_utm_grid.shape[0:2]) # init with empty
        self._fine_prob_map.fill(self._conf_threshold)
        # fill in detections
        for det in detections:
            #if det['conf'] >= self._conf_threshold:
            if True :
                idx = closest_point( det['gps'], self._fine_gps_grid )
                self._fine_coverage_map[idx[0],idx[1]] = 1.0 # make field visitable
                if self._fine_prob_map[idx[0],idx[1]] < det['conf'] :
                    self._fine_prob_map[idx[0],idx[1]] = det['conf'] # add probability from detection

                if self._debug:
                    if self._vis is not None:
                        self._vis.draw_points( [det['gps']], marker='*', color='m' ) # show detections!
                    else:                    
                        plt.plot(det['gps'][0], det['gps'][1], '*', c='m', lw=2, markersize=10)
        self._log.debug( "fine probability map: " + str(self._fine_prob_map) )
        self._log.debug( "fine coverage map: " + str(self._fine_coverage_map) )


    def finishFineSampling( self ):
        self._use_fine_grid = False
        self._fine_utm_grid = None
        self._fine_gps_grid = None
        self._fine_coverage_map = None
        self._log.debug( "finished fine sampling" )

    def useFineSampling(self):
        #with self._lock:
        return self._use_fine_grid

def closest_point(pt, points):
    #nodes = np.asarray(nodes)
    dist_2 = np.sum((points - pt)**2, axis=2)
    return np.where( np.amin(dist_2) == dist_2 )
 

def compute_corners( utm_center, area_size=(90,90) ):
    utm_corners = [] # [ utm.from_latlon(c[0],c[1]) for c in corners ]
    #lats = [ l[0] for l in utm_corners ]
    #lons = [ l[1] for l in utm_corners ]
    x = [-1, 1, 1,-1]
    y = [-1,-1, 1, 1]
    hsize = (area_size[0] / 2.0, area_size[1] / 2.0)

    for i in range(len(x)):
        utm_corners.append(  (utm_center[0] + x[i]*hsize[0], utm_center[1] + y[i]*hsize[1], utm_center[2], utm_center[3] ) )

    return utm_corners

def utm_list_to_gps( utm_list ):
    gps = []
    for utm_ in utm_list:
        gps.append( utm.to_latlon( *utm_) )
    return gps


def compute_grid( utm_center, area_size, tile_size  ):
    utm_corners = compute_corners( utm_center, area_size )
    es = [ l[0] for l in utm_corners ] # east
    ns = [ l[1] for l in utm_corners ] # north

    x = [0, 1, 1, 0] #left-bottom; right-bottom; right-top; left-top
    y = [0, 0, 1, 1]

    fes = interpolate.interp2d(x, y, es, kind='linear')
    fns = interpolate.interp2d(x, y, ns, kind='linear')


    
    xnew = np.arange(0,1, tile_size / area_size[0] )
    ynew = np.arange(0,1, tile_size / area_size[1] )



    offset = (tile_size/2.0,tile_size/2.0) # offset points to the center
    print(xnew)
    print(ynew)
    stackaxis = min(2,len(ynew))
    utm_grid = np.stack( (fes(xnew, ynew)+offset[0], fns(xnew, ynew)+offset[1]), axis=stackaxis ).reshape(len(ynew),len(xnew),2)
    print(utm_grid.shape)
    print(utm_grid)
    gps_grid = utm.to_latlon( utm_grid[:,:,0].flatten(), utm_grid[:,:,1].flatten(), utm_center[2], utm_center[3] )

  
    gps_grid = np.stack( (np.reshape(gps_grid[0],utm_grid.shape[0:2]), np.reshape(gps_grid[1],utm_grid.shape[0:2])), axis=2)
    print(gps_grid.shape)
    #print(gps_grid)
    #Indrajit :- Calculate Corner Points
    xcornerpoints = np.append(xnew, 1.0)
    ycornerpoints = np.append(ynew, 1.0)
    #indrajit :- Corner Utm grid

    utm_corner_grid = np.stack( (fes(xcornerpoints, ycornerpoints), fns(xcornerpoints, ycornerpoints)), axis=2 ).reshape(len(ycornerpoints),len(xcornerpoints),2)
    gps_corner_grid = utm.to_latlon( utm_corner_grid[:,:,0].flatten(), utm_corner_grid[:,:,1].flatten(), utm_center[2], utm_center[3] )
    #print(gps_corner_grid)
    #print(gps_grid)
    gps_corner_grid = np.stack( (np.reshape(gps_corner_grid[0],utm_corner_grid.shape[0:2]), np.reshape(gps_corner_grid[1],utm_corner_grid.shape[0:2])), axis=2 )

    utm_cell_vertical_center_grid = np.stack( (fes(xnew, ycornerpoints)+offset[0], fns(xnew, ycornerpoints)), axis=2 ).reshape(len(ycornerpoints),len(xnew),2)
    gps_cell_vertical_center_grid = utm.to_latlon( utm_cell_vertical_center_grid[:,:,0].flatten(), utm_cell_vertical_center_grid[:,:,1].flatten(), utm_center[2], utm_center[3] )
    gps_cell_vertical_center_grid = np.stack( (np.reshape(gps_cell_vertical_center_grid[0],utm_cell_vertical_center_grid.shape[0:2]), np.reshape(gps_cell_vertical_center_grid[1],utm_cell_vertical_center_grid.shape[0:2])), axis=2 )

    utm_cell_horizontal_center_grid = np.stack( (fes(xcornerpoints, ynew), fns(xcornerpoints, ynew)+offset[0]), axis=stackaxis ).reshape(len(ynew),len(xcornerpoints),2)
    gps_cell_horizontal_center_grid = utm.to_latlon( utm_cell_horizontal_center_grid[:,:,0].flatten(), utm_cell_horizontal_center_grid[:,:,1].flatten(), utm_center[2], utm_center[3] )
    gps_cell_horizontal_center_grid = np.stack( (np.reshape(gps_cell_horizontal_center_grid[0],utm_cell_horizontal_center_grid.shape[0:2]), np.reshape(gps_cell_horizontal_center_grid[1],utm_cell_horizontal_center_grid.shape[0:2])), axis=2 )

    utm_grid_waypoints = np.zeros((len(ynew),len(xnew),4,2))
    gps_grid_waypoints = np.zeros((len(ynew),len(xnew),4,2))
    
    #ToDo :- Make this Easier and simpler
    for i in range(len(ynew)) :
        for j in range(len(xnew)) :
            utm_grid_waypoints[i,j,0,0:2] = utm_cell_horizontal_center_grid[i,j,0:2]
            gps_grid_waypoints[i,j,0,0:2] =  utm.to_latlon(  utm_grid_waypoints[i,j,0,0], utm_grid_waypoints[i,j,0,1], utm_center[2], utm_center[3] )
            utm_grid_waypoints[i,j,1,0:2] = utm_cell_vertical_center_grid[i,j,0:2]
            gps_grid_waypoints[i,j,1,0:2] =  utm.to_latlon(  utm_grid_waypoints[i,j,1,0], utm_grid_waypoints[i,j,1,1], utm_center[2], utm_center[3] )
            utm_grid_waypoints[i,j,2,0:2] = utm_cell_horizontal_center_grid[i,j+1,0:2]
            gps_grid_waypoints[i,j,2,0:2] =  utm.to_latlon( utm_grid_waypoints[i,j,2,0], utm_grid_waypoints[i,j,2,1], utm_center[2], utm_center[3] )
            utm_grid_waypoints[i,j,3,0:2] = utm_cell_vertical_center_grid[i+1,j,0:2]
            gps_grid_waypoints[i,j,3,0:2] =  utm.to_latlon( utm_grid_waypoints[i,j,3,0], utm_grid_waypoints[i,j,3,1], utm_center[2], utm_center[3] )
    

    #print(utm_grid_waypoints.shape)
    assert gps_grid.shape == utm_grid.shape
    assert gps_corner_grid.shape == utm_corner_grid.shape

    #return utm_grid, gps_grid, utm_corner_grid, gps_corner_grid, utm_cell_vertical_center_grid, gps_cell_vertical_center_grid, utm_cell_horizontal_center_grid, gps_cell_horizontal_center_grid,utm_grid_waypoints,gps_grid_waypoints
    return utm_grid, gps_grid, utm_corner_grid, gps_corner_grid, utm_grid_waypoints,gps_grid_waypoints



# __name__ guard 
if __name__ == '__main__':

    # for visualization on DEM image
    from PathVisualizer import Visualizer
    

    
    
    gps_center = (48.3356687, 14.3262629)
    utm_center = utm.from_latlon( gps_center[0], gps_center[1] )
    gps_start = (48.335673, 14.32703)
    grid_size = 30
    num_cells = 3
    area_size = (grid_size*num_cells, grid_size*num_cells) # produce a square grid
    
    
    # path to the digital elevation model as required by the Visualizer
    dem_path = os.path.join( Path(__file__).parent.absolute(), '..',  'data', 'open_field', 'DEM' )
    vis = Visualizer( dem_path ) # initialize an instance of the visualizer (this is optional)

    prob_map =   None 

    # Optionally define a probability map (as numpy array)
    prob_map = np.ones( (np.asarray(area_size)/grid_size).astype(int) ) * .1
    prob_map[0,0] = .9 # a high probability area is visited first
    # Note that probabilities of zero are never visited while flying

    # initialize the planning algorithm
    p = Planner( utm_center, area_size, prob_map=prob_map, tile_distance=grid_size , debug=True, vis=vis, 
        conf_threshold=0.05, # only detections above this confidence score are resampled
        gridalignedplanpath = True)

    # Simualtion with the planning algorithm below
    path = np.array([gps_start[0],gps_start[1]])
    prev_pt = gps_start
    
    for i in range(num_cells**2+1):

        next_pts, record_flags = p.planpoints( prev_pt )
        next_pt = next_pts[-1]

        if record_flags[0] : # if True the drone should record while flying
            first_pt = prev_pt
        else :
            first_pt = next_pts[0]
        path = np.row_stack((path,next_pts)) 
        
        # update information for planning
        ct_pt = ( (first_pt[0]+next_pt[0])/2, (first_pt[1]+next_pt[1])/2 )
        detections = [] # no detections


        if i == 3: # simulte a detection
            detections = [{'gps': np.asarray(next_pt)-3e-5, 'conf': 0.3}]

        # update with position of AOS image and the detections 
        p.update( ct_pt, detections )
        prev_pt = next_pt


    plt.show()
