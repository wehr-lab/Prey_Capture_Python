import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import interpolate
from scipy import signal
from typing import List, Union

def relentless_positivity(df: pd.DataFrame, column:str, window: int = 20, threshold: float = 0.95,tolist:bool = True) -> Union[List[List[int]], np.ndarray]:
    """
    Find ranges where column is above threshold for #window number of rows

    Returns:
        List of Lists indicating the start and end of positive ranges
    """
    inds=np.where(df[column].rolling(window).sum()>=threshold*window)[0]
    starts=inds[np.diff(inds, prepend=-1)!=1]-window+1
    ends=inds[np.diff(inds, append=-1)!=1]
    periods=np.column_stack([starts, ends])
    start=np.min(periods)
    # print(start)
    end=np.max(periods)
    # print(end)
    if tolist:
        return periods.tolist(), start, end
    else:
        return periods, start, end

def azimuth_from_center(mouse_xy, headbase_xy, cricket_xy, start, end):
    """
    Function to calculate the angle between the mouse and the cricket, azimuth,
    using the center of mass of the mouse. This is based on the Matlab code used
    to calculate geometries for the HMM (ConvertDLCtoGeometry.m in Prey-Capture-SSM).
    Arguments:
        mouse_xy (:class:`numpy.ndarray`): an n x 2 array of coordinates over time
        cricket_xy (:class:`numpy.ndarray`): an n x 2 array of coordinates over time
        headbase_xy (:class:`numpy.ndarray`): an n x 2 array of coordinates over time

    Returns:
        az (:class:`numpy.ndarray`): an array containing azimuth values over time
    """
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

def speed(xy, start, end, win:int=12, fr:int=200):
    """
    Function used to calculate speeds during the prey capture trial. Can be used
    for either mouse or cricket speeds.
    Arguments:
        xy (:class:`numpy.ndarray`): an n x 2 array of coordinates over time
        win (int): smoothing window
        fr (int): framerate of video

    Returns:
        speed (:class:`numpy.ndarray`): an array containing speed values over time
    """

    dx = np.diff(xy[0])
    dx = np.convolve(dx,np.ones(win)/win, 'same')
    dy = np.diff(xy[1])
    dy = np.convolve(dy,np.ones(win)/win, 'same')
    spd = (np.sqrt(np.square(dx)+np.square(dy)))*fr
    return spd

def distance(xy1, xy2, start, end):
    """
    Function used to calculate speeds during the prey capture trial. Can be used
    for either mouse or cricket speeds.
    Arguments:
        xy1 (:class:`numpy.ndarray`): an n x 2 array of coordinates over time
        xy2 (:class:`numpy.ndarray`): an n x 2 array of coordinates over time

    Returns:
        dist (:class:`numpy.ndarray`): an array containing distance between two
            objects over time
    """
    dist = np.sqrt(np.square(xy1[0]- xy2[0]) + np.square(xy1[1] - xy2[1]))
    dist[-1]=0 #we can think about if we want this but last point should be the capture?
    #interpolate the range values to make up for dropped cricket points
    ind = np.arange(0,len(dist))
    interp = interpolate.interp1d(ind[~np.isnan(dist)], dist[~np.isnan(dist)],bounds_error=False, fill_value=np.nan )
    range_interp = interp(ind)
    dist = range_interp
    return dist

def azimuth_from_ears(mouse_xy, cricket_xy, rear_xy, lear_xy, start, end):
    """
    Function used to calculate angle between mouse and the cricket, azimuth,
    using the ears and center of the head. Based on calculations used for
    azimuth in the Niell Lab.
    Arguments:
        mouse_xy (:class:`numpy.ndarray`): an n x 2 array of coordinates over time
        cricket_xy (:class:`numpy.ndarray`): an n x 2 array of coordinates over time
        headbase_xy (:class:`numpy.ndarray`): an n x 2 array of coordinates over time

    Returns:
        az (:class:`numpy.ndarray`): an array containing azimuth values over time
    """
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

def length(cricket_front, cricket_back):
    xy_length=np.abs(cricket_front-cricket_back)
    xy_length

    length=np.nanmedian(xy_length, axis=0)
    x_length=length[0]
    y_length=length[1]

    mean_length=(x_length+y_length)/2

    return mean_length

def geometries(cricket_xy, mouse_xy, rear_xy, lear_xy, headbase_xy, cricket_p, cricket_front, cricket_back, fr=200):
    '''
    function to calculate geometric variables from DLC points
    these geometries can then be used for metrics such as time to capture
    potential to be adapted to calculate all geometries needed for HMM
    run extract_points before running this to get needed coordinates

    Arguments:
        cricket_xy (:class:`numpy.ndarray`) : thresholded cricket xy coordinates
        cricket_p (:class:`numpy.ndarray`) : cricket probability values
        mouse_xy (:class:`numpy.ndarray`) : mouse xy coordinates
        rear_xy (:class:`numpy.ndarray`) : xy coordinates of right ear, needed for azimuth calc
        lear_xy (:class:`numpy.ndarray`) : xy coordinates of left ear, needed for azimuth calc
        fr (int) : framerate of videos, default=200

    Returns:
        range (:class:`numpy.ndarray`): distance between mouse and cricket
        mouse_spd (:class:`numpy.ndarray`): mouse speed
        cricket_spd (:class:`numpy.ndarray`): cricket speed
        az (:class:`numpy.ndarray`): azimuth (angle of mouse head to cricket)
    '''
    #find period of the video where the cricket was present for interpolation
    df = pd.DataFrame({'data':cricket_p})
    periods, start, end  = relentless_positivity(df, 'data')

    #calculate the distance between the mouse and cricket
    range = distance(cricket_xy, mouse_xy, start, end)

    #calculate mouse speed, can add to this later to do velocity in x and y
    mouse_spd = speed(mouse_xy, start, end)
    mouse_spd = np.append(mouse_spd, np.nan)
    
    cricket_spd = speed(cricket_xy, start, end)
    cricket_spd = np.append(cricket_spd, np.nan)
    #probably need to do some interpolation on these values, but not sure how well this would work right now
    #not sure which value above comment is referring to

    az  = azimuth_from_center(mouse_xy, headbase_xy, cricket_xy, start, end)

    #calculate the cricket length to bin data based on thresholds of cricket size
    c_length=length(cricket_front, cricket_back)

    return range, mouse_spd, cricket_spd, az, c_length
