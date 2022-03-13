import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import interpolate
from scipy import signal

def azimuth_from_center(mouse_xy, headbase_xy, cricket_xy):
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
    return az

def speed(xy, win:int=12, fr:int=200):
    """
    Arguments:
        xy (:class:`numpy.ndarray`): an n x 2 array of coordinates over time
        win (int): smoothing window
        fr (int): framerate of video
    """

    dx = np.diff(xy[0])
    dx = np.convolve(dx,np.ones(win)/win, 'same')
    dy = np.diff(xy[1])
    dy = np.convolve(dy,np.ones(win)/win, 'same')
    spd = (np.sqrt(np.square(dx)+np.square(dy)))*fr
    return spd

def distance(xy1, xy2):
    dist = np.sqrt(np.square(xy1[0]- xy2[0]) + np.square(xy1[1] - xy2[1]))
    dist[-1]=0 #we can think about if we want this but last point should be the capture?
    #interpolate the range values to make up for dropped cricket points
    ind = np.arange(0,len(dist))
    interp = interpolate.interp1d(ind[~np.isnan(dist)], dist[~np.isnan(dist)],bounds_error=False, fill_value=np.nan )
    range_interp = interp(ind)
    dist = range_interp
    return dist

def azimuth_from_ears(mouse_xy, cricket_xy, rear_xy, lear_xy):
    #calculate azimuth
    #right now goes from -180 to 180 to show the direction, but this can cause large jumps in the plotting
    #could shift it to just going from 0 to 180 and indicate which direction the mouse is some other way
    # az seems to be shifted by 180 degrees, throwing off approach detection
    mouse_az = (np.arctan2((cricket_xy[1] - mouse_xy[1]),(cricket_xy[0] - mouse_xy[0]))*180)/np.pi
    head_az = ((np.arctan2((rear_xy[1] - lear_xy[1]),(rear_xy[0] - lear_xy[0]))*180)/np.pi) -90
    az = mouse_az-head_az
    az = np.mod(az+180,360)-180
    if np.sum(~np.isnan(az))>0:
        azOld = az
        ind = np.arange(0,len(az))
        interp = interpolate.interp1d(ind[~np.isnan(az)], az[~np.isnan(az)],bounds_error=False, fill_value=np.nan )
        az = interp(ind)
    return az

def geometries(cricket_xy, mouse_xy, rear_xy, lear_xy, headbase_xy, fr=200):
    '''
    function to calculate geometric variables from DLC points
    these geometries can then be used for metrics such as time to capture
    potential to be adapted to calculate all geometries needed for HMM
    run extract_points before running this to get needed coordinates

    Arguments:
        cricket_xy (ndarray) : thresholded cricket xy coordinates
        mouse_xy (ndarray) : mouse xy coordinates
        rear_xy (ndarray) : xy coordinates of right ear, needed for azimuth calc
        lear_xy (ndarray) : xy coordinates of left ear, needed for azimuth calc
        fr (int) : framerate of videos, default=200

    Returns:
        range (ndarray): distance between mouse and cricket
        mouse_spd (ndarray): mouse speed
        cricket_spd (ndarray): cricket speed
        az (ndarray): azimuth (angle of mouse head to cricket)
    '''
    #calculate the distance between the mouse and cricket
    range = distance(circket_xy, mouse_xy)

    #calculate mouse speed, can add to this later to do velocity in x and y
    mouse_spd = speed(mouse_xy)
    cricket_spd = speed(cricket_xy)

    #probably need to do some interpolation on these values, but not sure how well this would work right now
    #not sure which value above comment is referring to

    az  = azimuth_from_center(mouse_xy, headbase_xy, cricket_xy)

    return range, mouse_spd, cricket_spd, az
