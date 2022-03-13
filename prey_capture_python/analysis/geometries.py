import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import interpolate
from scipy import signal

def geometries(cricket_xy, mouse_xy, rear_xy, lear_xy, headbase_xy, fr=200):
    '''
    function to calculate geometric variables from DLC points
    these geometries can then be used for metrics such as time to capture
    potential to be adapted to calculate all geometries needed for HMM
    run extract_points before running this to get needed coordinates

    INPUTS:
        cricket_xy: array; thresholded cricket xy coordinates
        mouse_xy: array; mouse xy coordinates
        rear_xy: array; xy coordinates of right ear, needed for azimuth calc
        lear_xy: array; xy coordinates of left ear, needed for azimuth calc
        fr: int; framerate of videos, default=200

    RETURNS:
        range: array; distance between mouse and cricket
        mouse_spd: array; mouse speed
        cricket_spd: array; cricket speed
        az: array; azimuth (angle of mouse head to cricket)
    '''
    #calculate the distance between the mouse and cricket
    dist = np.sqrt(np.square(cricket_xy[0]- mouse_xy[0]) + np.square(cricket_xy[1] - mouse_xy[1]))
    dist[-1]=0 #we can think about if we want this but last point should be the capture?
    #interpolate the range values to make up for dropped cricket points
    ind = np.arange(0,len(dist))
    interp = interpolate.interp1d(ind[~np.isnan(dist)], dist[~np.isnan(dist)],bounds_error=False, fill_value=np.nan )
    range_interp = interp(ind)
    dist = range_interp

    #calculate mouse speed, can add to this later to do velocity in x and y
    win = 12
    mouse_dx = np.diff(mouse_xy[0])
    mouse_dx = np.convolve(mouse_dx,np.ones(win)/win, 'same')
    mouse_dy = np.diff(mouse_xy[1])
    mouse_dy = np.convolve(mouse_dy,np.ones(win)/win, 'same')
    mouse_spd = (np.sqrt(np.square(mouse_dx)+np.square(mouse_dy)))*fr

    #calculate cricket speed, can also change this to velocities later
    win = 12
    cricket_dx = np.diff(cricket_xy[0])
    cricket_dx = np.convolve(cricket_dx,np.ones(win)/win, 'same')
    cricket_dy = np.diff(cricket_xy[1])
    cricket_dy = np.convolve(cricket_dy,np.ones(win)/win, 'same')
    cricket_spd = (np.sqrt(np.square(cricket_dx)+np.square(cricket_dy)))*fr
    #probably need to do some interpolation on these values, but not sure how well this would work right now

    #calculate azimuth
    #right now goes from -180 to 180 to show the direction, but this can cause large jumps in the plotting
    #could shift it to just going from 0 to 180 and indicate which direction the mouse is some other way
    #az seems to be shifted by 180 degrees, throwing off approach detection
    # mouse_az = (np.arctan2((cricket_xy[1] - mouse_xy[1]),(cricket_xy[0] - mouse_xy[0]))*180)/np.pi
    # head_az = ((np.arctan2((rear_xy[1] - lear_xy[1]),(rear_xy[0] - lear_xy[0]))*180)/np.pi) -90
    # az = mouse_az-head_az
    # az = np.mod(az+180,360)-180
    # if np.sum(~np.isnan(az))>0:
    #     azOld = az
    #     ind = np.arange(0,len(az))
    #     interp = interpolate.interp1d(ind[~np.isnan(az)], az[~np.isnan(az)],bounds_error=False, fill_value=np.nan )
    #     az = interp(ind)

    #mike has a different way of calculating azimuth, try that instead
    #a=centerofmass to nose distance; b=center of mass to cricket distance, c=nose to to cricket distance
    #az=acosd(a^2+b^2-c^2)/2ab
    a=np.sqrt(np.square((mouse_xy[0]-headbase_xy[0]))+np.square((mouse_xy[1]-headbase_xy[1])))
    b=np.sqrt(np.square((headbase_xy[0]-cricket_xy[0]))+np.square((headbase_xy[1]-cricket_xy[1])))
    c=np.sqrt(np.square((mouse_xy[0]-cricket_xy[0]))+np.square((mouse_xy[1]-cricket_xy[1])))
    az=np.arccos((np.square(a)+np.square(b)-np.square(c))/(2*a*b))
    if np.sum(~np.isnan(az))>0:
        azOld = az
        ind = np.arange(0,len(az))
        interp = interpolate.interp1d(ind[~np.isnan(az)], az[~np.isnan(az)],bounds_error=False, fill_value=np.nan )
        az = interp(ind)
        az=(az*180)/np.pi

    return dist, mouse_spd, cricket_spd, az
