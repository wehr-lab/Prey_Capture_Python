import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from dataclasses import dataclass
# from typing import List, Literal
# from pathlib import Path
#
# @dataclass
# class Position:
#     x: List[int]
#     y: List[int]
#     p: List[float]
#
# @dataclass
# class Track:
#     positions: List[Position]
#     animal: Literal['mouse', 'cricket']
#
#     @classmethod
#     def from_dlc(cls, file:Path) -> Track:
#         ...
#
# track = Track.from_dlc('file.csv')
def getmidpoint(pt1,pt2):
    '''
    '''
    midpoint=0.5*(pt1+pt2)
    return midpoint

def extract_points(file, bodyparts, fr=200, pix2cm=15.8, thresh=0.7, startonly=False ):
    '''
    function to extract mouse and cricket xy positions from DLC output csv
    will also get the likelihood values for cricket positions
    can be adapted later to add extraction of likelihood for the mouse

    Args:
        file (str): filename/ path to the DLC output
        bodyparts (list): list of the bodypart labels from DLC you need
            added as an input since names vary across models
        fr (int): framerate of videos, default=200
        pix2cm (int): conversion from pixels to cm, default=15.8 (needs to be checked)
        thresh (int): threshold for likelihood values, default=0.7
        startonly (bool): flag to only include the first 2min in calculations so laser is always on


    Returns:
        mouse_xy (:class:`numpy.ndarray`): xy coordinates for the mouse across the trial
        cricket_xy (:class:`numpy.ndarray`): xy coordinates for the cricket across trial, cricket_xy is filtered to remove points with low likelihood
        cricket_p (:class:`numpy.ndarray`): likelihood values of cricket points

    '''
    #set the constant values that will be used throughout
    #load relevant dlc points from the csv, limits the amount you have to work with
    # print(bodyparts)
    data=pd.read_csv(file, skiprows=[0,1], header=[0,1])
    if startonly==False:
        data=data.loc[:,bodyparts]
    else:
        data=data.loc[:,bodyparts]
        data=data.iloc[0:(120*fr)]
    #create 2d array for mouse xy coordinates
    #right now indexing df depends on order of your bodyparts lists, find a better way to deal with this
    rear_x=data[bodyparts[0],'x'].to_numpy()
    # plt.plot(rear_x)
    rear_y=data[bodyparts[0],'y'].to_numpy()
    # plt.plot(rear_y)

    lear_x=data[bodyparts[1],'x'].to_numpy()
    # plt.plot(lear_x)
    lear_y=data[bodyparts[1],'y'].to_numpy()
    # plt.plot(lear_y)

    rear_xy=np.asarray([rear_x,rear_y])
    # plt.figure(figsize=(10,10))
    # plt.plot(rear_xy[0], rear_xy[1])
    lear_xy=np.asarray([lear_x,lear_y])
    # plt.figure(figsize=(10,10))
    # plt.plot(lear_xy[0], lear_xy[1])

    headbase_x=data[bodyparts[4],'x'].to_numpy()
    headbase_y=data[bodyparts[4],'y'].to_numpy()
    headbase_xy=np.asarray([headbase_x,headbase_y])/pix2cm


    mouse_xy=getmidpoint(rear_xy,lear_xy)/pix2cm
    # plt.figure(figsize=(10,10))
    # plt.plot(mouse_xy[0],mouse_xy[1])

    #extract cricket likelihood and xy coordinates, same indexing issue
    #average function?
    cricket_p=(data[bodyparts[2],'likelihood'].to_numpy()+data[bodyparts[3],'likelihood'].to_numpy())/2
    #add pvalues to the same array as xy
    cricket_x=(data[bodyparts[2],'x'].to_numpy()+data[bodyparts[3],'x'].to_numpy())/(2*pix2cm)
    # plt.figure(figsize=(10,10))
    # plt.plot(cricket_x)
    cricket_y=(data[bodyparts[2],'y'].to_numpy()+data[bodyparts[3],'y'].to_numpy())/(2*pix2cm)
    # plt.figure(figsize=(10,10))
    # plt.plot(cricket_y)

    cricket_front=data[bodyparts[2]].to_numpy()
    cricket_back=data[bodyparts[3]].to_numpy()

    thresh_cricket_x=cricket_x.copy()
    thresh_cricket_x[cricket_p<thresh]=np.nan
    thresh_cricket_y=cricket_y.copy()
    thresh_cricket_y[cricket_p<thresh]=np.nan

    cricket_xy=[thresh_cricket_x, thresh_cricket_y]
    # plt.figure(figsize=(10,10))
    # plt.plot(cricket_xy[0], cricket_xy[1],linestyle="", marker='.', markersize=1)

    return mouse_xy, cricket_p, cricket_xy, rear_xy, lear_xy, headbase_xy, cricket_front, cricket_back
