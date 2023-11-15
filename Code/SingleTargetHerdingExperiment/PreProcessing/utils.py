import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob # for directory search
import re # regular expressions
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import interp1d

field_dimensions = [120, 90] # the field (walls) are of dimensions 120 by 90 m
containment_radius = 4.0
cow_radius = .5 #radius of our spherical cow
repulsion_distance = 10 #meters, aboev which there is no repulsion between HA and TA.

def get_trial_identifier(file_name): # from file name, get trial identifier as string
    return re.search(r'(?<=trialIdentifier)\w+', file_name).group(0)[:2]

def plot_circle(x,y,axis, r=containment_radius,color='maroon'): #simple function to plot the containment zone rings
    theta = np.linspace(-np.pi, np.pi, 100)
    axis.plot(x+ r*np.cos(theta), y+ r*np.sin(theta),color)
    return

def plot_walls(axis): # simple function to plot the game field walls
    X_max = field_dimensions[0] /2
    X_min = -X_max
    Y_max = field_dimensions[1] /2
    Y_min = -Y_max #positions of walls

    X_lims = np.arange(X_min, X_max, 0.01);
    Y_lims = np.arange(Y_min, Y_max, 0.01);
    axis.plot(X_lims, Y_max*np.ones(np.size(X_lims)), color='0.9')# North Wall
    axis.plot(X_lims, Y_min*np.ones(np.size(X_lims)), color='0.9')# South Wall
    axis.plot(X_min*np.ones(np.size(Y_lims)), Y_lims, color='0.9')# West Wall
    axis.plot(X_max*np.ones(np.size(Y_lims)), Y_lims, color='0.9')# East Wall
    return



def get_end_herder_activity_method_one(T):
    """
    Gets the index where the herder activity ends
    Arguments: T: Data table
    Output: idx: right index in T defined as 
    1) get first time TA enters the containment zone
    2) What is the last time, going back in time from moment 1), where the HA influences the TA?
                
    """

    TA_dist = np.sqrt(T.t0x**2 + T.t0z**2) #distance of TA from containment zone (CZ)

    t0 = np.where(TA_dist < containment_radius + cow_radius)[0][0] # first time index when TA enters (more specifically, touches) CZ

    idx = np.where(T.t0run[0:t0])[0][-1] #what we need according to point 2) above.

    return idx

def get_end_herder_activity(T):

    """
    Gets the index where the herder activity ends
    Arguments: T: Data table
    Output: idx: right index in T defined as 
    1) get first time HA influences TA
    2) What is the last time, going forwards in time from moment 1), where the HA influences the TA?
                
    """

    t0 = np.where(T.t0run)[0][0] # point 1)

    idx = np.where(T.t0run[t0+1:] == False)[0][0]

    return idx + t0

#function to get participant ID from filepath
def get_partID(filePath):
    """get whatever is between "session" and double-underscore
    example: filePath.name = 'FirstPersonHerding_session2012__trialIdentifier08_trialOrder12_2023322_1099.csv'
    then return 2012
    """
    s = filePath.name
    start = 'session'
    end = '__'

    result = re.search('%s(.*)%s' % (start, end), s).group(1)
    return result
    
#function that takes in 1-D array and upsamples it to N points
def interp_traj(arr, N=10000):

    # interpolate array over `N` evenly spaced points
    min_val = np.min(arr)
    max_val = np.max(arr)

    t_orig = np.linspace(min_val, max_val, len(arr))
    t_interp = np.linspace(min_val, max_val, N)
    f = interp1d(x=t_orig, y=arr)
    interp_arr = f(t_interp)
    
    return interp_arr

#function that upsamples through interp_traj function, then downsamples
#input: timeseries data matrix
def time_normalize(T):
    
    herder_end_idx = get_end_herder_activity(T)
    
    x = interp_traj(T.p0x[:herder_end_idx])
    z = interp_traj(T.p0z[:herder_end_idx])
    
    return x[::10],z[::10] #going from 10,000 points to 1000 points (taking every 10th point)

def plotter(T, axis, trial_count, color, trim = True, partID=None): # plot function that takes in timeseries data
    fontsize = 16
    heading_init = R.from_quat([T.p0xq[0], T.p0yq[0], T.p0zq[0], T.p0wq[0]]).as_rotvec()[1]
    #axis.arrow(T.p0x[0], T.p0z[0], np.cos(heading_init), np.sin(heading_init), shape = 'full', lw = 0,length_includes_head=True, head_width=2.5)
    if trim:
        herder_end_idx = get_end_herder_activity(T)
    else:
        herder_end_idx = len(T)
    axis.plot(T.p0x[:herder_end_idx], T.p0z[:herder_end_idx], 'k.', markersize=.1)
    if herder_end_idx != 0:
        axis.plot(T.t0x[0], T.t0z[0], 'bo')
        #plt.plot(T.t0x, T.t0z, 'b')
    plot_circle(0,0, axis)
    plot_walls(axis)
    axis.axis("equal")
    axis.set_title("Trial ID: " + str(trial_count+1), fontsize = fontsize)
    axis.set_xlabel("x[m]", fontsize = fontsize)
    axis.set_ylabel("y[m]", fontsize = fontsize)
    if partID is not None:
        axis.text(T.p0x[700], T.p0z[700],partID)
    return

# function to get signed angle between two 2D vectors
def angle_between(vec1, vec2):
    """
    arguments:
    vec1, vec2 which are two vectors in the plane

    returns:
    angle between them in [-pi, pi]
    angle is measured from vec1 to vec2
    (counterclockwise is positive)
    """
    if np.linalg.norm(vec1) != 0:
        vec1 = vec1 / np.linalg.norm(vec1)

    if np.linalg.norm(vec2) != 0:
        vec2 = vec2 / np.linalg.norm(vec2)
    
    x1 = vec1[0]
    y1 = vec1[1]
    x2 = vec2[0]
    y2 = vec2[1]
    
    return np.arctan2(x1*y2-y1*x2,x1*x2+y1*y2)


def get_epsilon(T):
    t0 = np.where(T.t0run)[0][0] # get first time HA influences TA
    v1 = [T.t0x[t0], T.t0z[t0]]
    v2 = [T.p0x[t0], T.p0z[t0]]
    return abs(angle_between(v1,v2))