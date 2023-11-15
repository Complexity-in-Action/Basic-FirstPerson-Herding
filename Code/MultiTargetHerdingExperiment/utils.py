import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import re # regular expressions
import math
from scipy.spatial.transform import Rotation as R

exValue = 9999 # an exception value

def get_trial_identifier(file_name):
    return re.search(r'(?<=trialIdentifier)\w+', file_name).group(0)[:2]

def get_herder_col_names(herderNum):
    if(herderNum == 0):
        otherHerderNum = 1
    else:
        otherHerderNum = 0

    hcolx = 'p%dx' % (herderNum)
    hcolz = 'p%dz' % (herderNum)
    ohcolx = 'p%dx' % (otherHerderNum)
    ohcolz = 'p%dz' % (otherHerderNum)

    return [hcolx, hcolz], [ohcolx, ohcolz]

def get_order_index(targetFactor):
    """
    Arguments:
    targetFactor: Array of length numTargs, with entries the time indices of TAs' respective dependent variable (distance, actual run timestamp, angle, etc.).
    this will include exValue (=9999) as an entry, if that TA was away 15m or more from the specified HA
    this is because in that case, it won't be assigned to that particular HA.
    Each HA has its own targetFactor

    Returns:
    order: array of length numTargs, indicating ordered TA ID in which TAs were chased, but only those assigned to the given HA.
    """
    order = np.argsort(targetFactor) #get first chased order
    for i in range(len(targetFactor)):
        if(targetFactor[order[i]] == exValue): #if the TA is had been not assigned to that HA,
            order[i] = -1 #mark corresponding order value to -1
    return np.array(order, dtype=int)

def get_num_targets(data, maxTargets):
    """
    Arguments:
    data: timeseries per trial per participant
    maxTargets: maximum number of TAs, either 3, 4 or 5 in our experiment
    """
    numTargets = 0
    for t in range(0, maxTargets):
        col = 't%drun' % (t)
        if col in data.columns:
            #print("Courses column is present : Yes")
            numTargets = t + 1        
        else:
            #print("Courses column is present : No")
            break

    return numTargets

def get_observed_target_order(data, herderNum, numTargets):
    """
    Arguments: 
    data: timeseries per participant per trial
    herderNum: the HA ID (0 or 1)
    numTargets: 3, 4, or 5 in our current experiment
    
    Returns:
    targetOrder: array of length numTargs, indicating ordered TA ID in which TAs were chased, but only those assigned to the given HA.
    targetSet: same as targetOrder except it has -1 as exception value instead of 9999.
    targetHerderDifferences: array of length numTargs, with values distances between HA specifed by herderNum, indexed per TA
    this array is calculated at the time index where the given TA first ran
    """
    targetFactor = np.zeros(numTargets, dtype=int)
    targetHerderDifferences = np.zeros(numTargets, dtype=float)
    for i in range(numTargets):
        col = 't%drun' % (i)
        targetFactor[i] = np.where(data[col])[0][0] # assigns where particular TA ran to targetFactor value, indexed by TA ID.
    
    hcolx = 'p%dx' % (herderNum)
    hcolz = 'p%dz' % (herderNum)
    for t in range(numTargets):
        tcolx = 't%dx' % (t)
        tcolz = 't%dz' % (t)
        #targetHerderDifferences is an array of length numTargs, with values distances between HA specifed by herderNum, indexed per TA
        #this array is calculated at the time index where the given TA first ran
        targetHerderDifferences[t] = dist(data[tcolx][targetFactor[t]] - data[hcolx][targetFactor[t]], data[tcolz][targetFactor[t]] - data[hcolz][targetFactor[t]])
        if(targetHerderDifferences[t] > 10):
            targetFactor[t] = exValue #if given TA is further than 15m away from the specified HA at the point where it first ran, its

    targetOrder = get_order_index(targetFactor)
        
    targetSet = targetFactor
    targetSet[targetSet == exValue] = -1 #targetSet is same as targetOrder except it has -1 as exception value instead of 9999.
    return targetOrder, targetSet, targetHerderDifferences
    
# function to calculate the euclidean distance of a point from the origin
def dist(x,y):
    """
    arguments:
    (x,y): x, y coordinate of point in 2D plane
    returns float real positive number
    """
    return np.sqrt(x**2 + y**2)
    
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


def quat_to_angle(rotx, roty, rotz, rotw):
    rotation_object = R.from_quat([rotx, roty, rotz, rotw])
    playerRot = rotation_object.as_rotvec() # Direction vector
    return playerRot[1] #left/right heading direction (rotation along y-axis)


def order_match(ordering1, ordering2): 
    #if ordering1[0] == ordering2[0] and ordering1[1] == ordering2[1] and ordering1[2] == ordering2[2]:
    if (np.array(ordering1) == np.array(ordering2)).all():
        return 1
    else:
        return 0


# Python function to print permutations of a given list
def permutation(lst):
 
    # If lst is empty then there are no permutations
    if len(lst) == 0:
        return []
 
    # If there is only one element in lst then, only
    # one permutation is possible
    if len(lst) == 1:
        return [lst]
 
    # Find the permutations for lst if there are
    # more than 1 characters
 
    l = [] # empty list that will store current permutation
 
    # Iterate the input(lst) and calculate the permutation
    for i in range(len(lst)):
       m = lst[i]
 
       # Extract lst[i] or m from the list.  remLst is
       # remaining list
       remLst = lst[:i] + lst[i+1:]
 
       # Generating all permutations where m is first
       # element
       for p in permutation(remLst):
           l.append([m] + p)
    return l

def trace(mat, traj, bin_size, xlim, ylim):
    """
    gets the weighted or non-weigted trace of a trajectory trah along a heatmap
    Arguments:
    mat: heatmap
    traj: set of X,Y points. expected shape: N x 2
    """
    h, _, _ = np.histogram2d(x = traj[:,0], y = traj[:,1],  bins = (int(120/bin_size), int(90/bin_size)), range = ((-xlim, xlim), (-ylim,ylim)))
    h = h.T[::-1]
    h = h > 0
    h = h*1
    return np.sum(mat*h)/np.sum(h)