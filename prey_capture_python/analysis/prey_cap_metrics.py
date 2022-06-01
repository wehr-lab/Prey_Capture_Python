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
    if tolist:
        return periods.tolist()
    else:
        return periods

def preycap_metrics(cricket_xy, cricket_p, range, mouse_spd, az, fr=200, oldmodel=False):
        '''
        function to calculate basic metrics of prey capture behavior
        decent first pass look at if there are differences between conditions

        Arguments:
            cricket_xy (:class:`numpy.ndarray`): thresholded cricket xy coordinates
            cricket_p (:class:`numpy.ndarray`): cricket likelihoods
            range (:class:`numpy.ndarray`): distance between mouse and cricket
            mouse_spd (:class:`numpy.ndarray`): mouse speed (not velocity)
            az (:class:`numpy.ndarray`): angle between mouse's head and cricket
            fr (int): framerate of videos, default=200
            oldmodel (boolean): flag to mark cricket likelihood is bad, default=False

        Returns:
            captureT (int): time to capture the cricket --indication of start and end need to be changed
            latency (int): time to the first approach
            freqapproach (int): frequency of initiating approaches
            p_intercept (int): probability of intercepting given an approach
            p_capture (int): probability of capturing given intercepting
        '''
        #calculate the time to capture, right now running with a new, higher threshold than other calculations
        #have if/else statement so that if new models in the future fix things but we don't want to re run old data
        newthresh=0.9
        movieT=len(cricket_p)/fr
        if oldmodel==True:
            start2end=np.where(cricket_p>newthresh)[0]
            captureT=(start2end[-1]-start2end[0])/fr
        else:
            df = pd.DataFrame({'data':cricket_p})
            periods = relentless_positivity(df, 'data')
            start=np.min(periods)
            # print(start)
            end=np.max(periods)
            # print(end)
            captureT=(end-start)/fr
        if captureT.size==0:
            captureT=movieT

        #calculate latency and frequency of initiating approaches
        approach = []
        paired = list(zip(az[start:end],mouse_spd[start:end]))
        for pair in paired:
            if np.abs(pair[0]) < 30 and pair[1] > 5:
                approach.append(1)
            else:
                approach.append(0)

        approach = signal.medfilt(approach, 101) # 101 is hardcoded half a second based on framerate
        approach = np.asarray(approach)
        #plt.plot(approach)

        approachStarts = np.where(np.diff(approach)>0)
        approachEnds = np.where(np.diff(approach)<0)
        #print(approachEnds)
        firstApproach = np.min(approachStarts)
        timetoapproach = firstApproach/fr # return this
        freqapproach=np.size(approachStarts) / movieT # return this

        #calculate probability of interception given approach, and probability of capture given interception
        #getting closer, still think there is something off about the distance calculation leading to fewer interceptions
        #maybe something off with pix2cm converstion
        intercept = []
        maybeIntercept = np.take(range[start:end], approachEnds) # uses approachEnds to index range
        maybeIntercept = maybeIntercept[0] # np.take returns tuple, first value are the ones you one
        #print(maybeIntercept)
        maybeIntercept[-1] = 0 # assuming last approach is intercept/capture, makes things werk, this needs to be changed, last intercept might not be a capture

        for i in maybeIntercept:
            if i < 5:
                intercept.append(1)
            else:
                intercept.append(0)
        # find the first intercept for sake of calculating latency to intercept not approach
        # hope is that this will be closer to the latency to attack values used in Zhao et al 2019
        firstintercept= np.min(intercept>0)
        timetointercept=firstintercept/fr  #return this
        # calculate probability of intercept given approach
        tot_approach = np.size(approachEnds)
        #print(tot_approach)
        tot_intercept = sum(intercept)
        #print(tot_intercept)
        prob_inter = tot_intercept / tot_approach

        # calculate the probability of capture given contact - 1/number of intercepts
        if tot_intercept>0:
            prob_capture = 1 / tot_intercept
        else:
            print('no capture')

        return approach, captureT, freqapproach, timetoapproach, timetointercept, prob_inter, prob_capture
