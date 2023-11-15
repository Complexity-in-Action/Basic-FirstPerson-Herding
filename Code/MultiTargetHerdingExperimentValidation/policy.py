# import relevant packages
from utils import * # for project-specific custom functions
from scipy.spatial.transform import Rotation as R # to convert between Euler angles and Quaternions
import random
import math

'''
Four General Types of Target Selection Policies Defined Here:

1. Initial condition policies - where the entire target selection sequence is defined by 
the initial state of the environment prior to herder movement or target engagement
    - closest or furthest distance from herder
    - closest or furthest angular distance from herder
    - closest or furthest radial distance from containment zone
    
2. Successive policies - where first target selection is defined by the initial state 
of the environment, but then subsequent target selctions are made successively at the time 
of target engagement (but before target is corralled into the containment zone)
    - successive closest or furthest distance from herder
    - successive closest or furthest angular distance from herder

3. Dynamic policies - similar to sucessive policies, but subsequent target selctions 
are made successively when the previous target has been corralled. 
    - dynamic closest or furthest distance from herder
    - dynamic closest or furthest angular distance from herder
    - dynamic closest or furthest radial distance from containment zone

4. Complex policies - a combination of the above and/or an above policy that includes 
a target grouping or clusting function.
    - ****


All functions generally take in at least the timeseries per trial,  and output the TA ordering ([0,2,1] for example).
'''


#################################################################################################################
## 1. Initial conditon policies - where the entire target selection sequence is defined by 
## the initial state of the environment prior to herder movement or target engagement

#function to order distance from herder initial position
def get_closest_distance_from_herder_ordering(T):
    """
    arguments: T: data file
    output: ordering of indices 0, 1, 2
    example output:
    [0 2 1] if 0 is closest from herder initial position, 2 next and 1 furthest
    """
    d0 = dist(T.t0x[0] - T.p0x[0], T.t0z[0] - T.p0z[0])
    d1 = dist(T.t1x[0] - T.p0x[0], T.t1z[0] - T.p0z[0])
    d2 = dist(T.t2x[0] - T.p0x[0], T.t2z[0] - T.p0z[0])
    return np.argsort([d0, d1, d2])

#function to get ordering of angles from herder initial position
def get_closest_angle_from_herder_ordering(T):
    targetsPos = np.array([[T.t0x[0], T.t0z[0]], [T.t1x[0], T.t1z[0]], [T.t2x[0], T.t2z[0]]]) #shape (3, 2)
    angle0 = angle_between(targetsPos[0], np.array([T.p0x[0], T.p0z[0]]))
    angle1 = angle_between(targetsPos[1], np.array([T.p0x[0], T.p0z[0]])) 
    angle2 = angle_between(targetsPos[2], np.array([T.p0x[0], T.p0z[0]])) 

    return np.argsort(np.abs([angle0, angle1, angle2]))

#function to order distance from zone
def get_closest_distance_from_zone_ordering(T):
    """
    arguments: T: data file
    output: ordering of indices 0, 1, 2
    example output:
    [0 2 1] if 0 is closest from zone, 2 next and 1 furthest
    """
    distances = [dist(T.t0x[0], T.t0z[0]), dist(T.t1x[0], T.t1z[0]), dist(T.t2x[0], T.t2z[0])]
    return np.argsort(distances)


    
#################################################################################################################
## 2. Successive policies - where first target selection is defined by the initial state 
## of the environment, but then subsequent target selctions are made successively at the time 
## of target engagement (but before target is corralled into the containment zone)

#function to get successive closest from herder, then next closest from that TA, then next closest
def get_successive_closest_distance_from_herder_ordering(T):

    closest_distance_from_herder_ordering = get_closest_distance_from_herder_ordering(T)
    
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    
    #first get closest TA
    idx0 = closest_distance_from_herder_ordering[0]
    pos0 = targetsPos[idx0][:,0]
    
    #then get next closest target agent from this TA then assign right indices
    
    pos1 = targetsPos[closest_distance_from_herder_ordering[1]][:,0]
    pos2 = targetsPos[closest_distance_from_herder_ordering[2]][:,0]
    
    d1 = dist(pos1[0]-pos0[0], pos1[1]-pos0[1])    
    d2 = dist(pos2[0]-pos0[0], pos2[1]-pos0[1])

    if d1 < d2:
        idx1 = closest_distance_from_herder_ordering[1]
        idx2 = closest_distance_from_herder_ordering[2]
    else:
        idx1 = closest_distance_from_herder_ordering[2]
        idx2 = closest_distance_from_herder_ordering[1]
    
    return [idx0, idx1, idx2]

    #function to get successive closest from herder, then next closest from that TA, then next closest
def get_successive_furthest_distance_from_herder_ordering(T):

    closest_distance_from_herder_ordering = get_closest_distance_from_herder_ordering(T)
    furthest_distance_from_herder_ordering = closest_distance_from_herder_ordering[::-1]
    
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    
    #first get furthest TA
    idx0 = furthest_distance_from_herder_ordering[0]
    pos0 = targetsPos[idx0][:,0]
    
    #then get next closest target agent from this TA then assign right indices
    
    pos1 = targetsPos[furthest_distance_from_herder_ordering[1]][:,0]
    pos2 = targetsPos[furthest_distance_from_herder_ordering[2]][:,0]
    
    d1 = dist(pos1[0]-pos0[0], pos1[1]-pos0[1])    
    d2 = dist(pos2[0]-pos0[0], pos2[1]-pos0[1])

    if d1 < d2:
        idx1 = furthest_distance_from_herder_ordering[1]
        idx2 = furthest_distance_from_herder_ordering[2]
    else:
        idx1 = furthest_distance_from_herder_ordering[2]
        idx2 = furthest_distance_from_herder_ordering[1]
    
    return [idx0, idx1, idx2]
    
#function to get successive closest from herder in angles, then next closest from that TA, then next closest
def get_successive_closest_angle_from_herder_ordering(T):

    closest_angle_from_herder_ordering = get_closest_angle_from_herder_ordering(T)
    
    targetsPos = np.array([[T.t0x[0], T.t0z[0]], [T.t1x[0], T.t1z[0]], [T.t2x[0], T.t2z[0]]]) #shape (3, 2) 
    
    #first get first closest TA in angles space
    idx0 = closest_angle_from_herder_ordering[0]
    pos0 = targetsPos[idx0]

    
    #then get next closest target agents from 
    pos1 = targetsPos[closest_angle_from_herder_ordering[1]]
    pos2 = targetsPos[closest_angle_from_herder_ordering[2]]
    
    a1 = abs(angle_between(pos1, pos0))    
    a2 = abs(angle_between(pos2, pos0))

    #then assign right indices   
    if a1 < a2:
        idx1 = closest_angle_from_herder_ordering[1]
        idx2 = closest_angle_from_herder_ordering[2]
    else:
        idx1 = closest_angle_from_herder_ordering[2]
        idx2 = closest_angle_from_herder_ordering[1]
    
    return [idx0, idx1, idx2]


def get_successive_furthest_angle_from_herder_ordering(T):

    closest_angle_from_herder_ordering = get_closest_angle_from_herder_ordering(T)
    furthest_angle_from_herder_ordering = closest_angle_from_herder_ordering[::-1]
    
    targetsPos = np.array([[T.t0x[0], T.t0z[0]], [T.t1x[0], T.t1z[0]], [T.t2x[0], T.t2z[0]]]) #shape (3, 2) 
    
    #first get first closest TA in angles space
    idx0 = furthest_angle_from_herder_ordering[0]
    pos0 = targetsPos[idx0]

    
    #then get next closest target agents from 
    pos1 = targetsPos[furthest_angle_from_herder_ordering[1]]
    pos2 = targetsPos[furthest_angle_from_herder_ordering[2]]
    
    a1 = abs(angle_between(pos1, pos0))    
    a2 = abs(angle_between(pos2, pos0))

    #then assign right indices   
    if a1 < a2:
        idx1 = furthest_angle_from_herder_ordering[1]
        idx2 = furthest_angle_from_herder_ordering[2]
    else:
        idx1 = furthest_angle_from_herder_ordering[2]
        idx2 = furthest_angle_from_herder_ordering[1]
    
    return [idx0, idx1, idx2]


    
#################################################################################################################
## 3. Dynamic policies - similar to sucessive policies, but subsequent target selctions 
## are made successively when the previous target has been corralled. 
    
#function to get ordering of targets' positions measured successively from herder position.
def get_dynamic_closest_distance_from_herder_ordering(T):

    closest_distance_from_herder_ordering = get_closest_distance_from_herder_ordering(T)
    
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    targetsCt = np.array([T.t0ct, T.t1ct, T.t2ct])

    #first get closest TA
    idx0 = closest_distance_from_herder_ordering[0]
    pos0 = targetsPos[idx0][:,0]
    
    #when was that TA contained?
    try:
        first_ct_idx = np.where(targetsCt[idx0])[0][0]
    except:
        return [0,0,0]

    #what are the HA and other TA positions at that timestamp?
    h = [T.p0x[first_ct_idx], T.p0z[first_ct_idx]]
    t1 = targetsPos[closest_distance_from_herder_ordering[1]][:,first_ct_idx]
    t2 = targetsPos[closest_distance_from_herder_ordering[2]][:,first_ct_idx]

    #which one of them gets a lower distance?
    d1 = dist(h[0] - t1[0], h[1] - t1[1])
    d2 = dist(h[0] - t2[0], h[1] - t2[1])

    if d1 < d2:
        idx1 = closest_distance_from_herder_ordering[1]
        idx2 = closest_distance_from_herder_ordering[2]
    else:
        idx1 = closest_distance_from_herder_ordering[2]
        idx2 = closest_distance_from_herder_ordering[1]
    
    return [idx0, idx1, idx2]

def get_dynamic_closest_angle_from_herder_ordering(T):

    closest_angle_from_herder_ordering = get_closest_angle_from_herder_ordering(T)
    
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    targetsCt = np.array([T.t0ct, T.t1ct, T.t2ct])
    
    #which is the first closest TA from HA init pos?
    idx0 = closest_angle_from_herder_ordering[0]
    
    #when is that TA contained?
    try:
        first_ct_idx = np.where(targetsCt[idx0])[0][0]
    except:
        return [3,3,3] #so it throws a 0 score
        #successive_angle_ordering = get_successive_angle_from_herder_ordering(T, angle_ordering)  
        #return get_collinearity_capturing_ordering(T, successive_angle_ordering)
    
    #what are the HA and other TA positions at that timestamp?
    h = [T.p0x[first_ct_idx], T.p0z[first_ct_idx]]
    t1 = targetsPos[closest_angle_from_herder_ordering[1]][:,first_ct_idx]
    t2 = targetsPos[closest_angle_from_herder_ordering[2]][:,first_ct_idx]
    
    #which one of them gets a lower angle?
    a1 = abs(angle_between(h,t1))
    a2 = abs(angle_between(h,t2))
    
    if a1< a2:
        idx1 = closest_angle_from_herder_ordering[1]
        idx2 = closest_angle_from_herder_ordering[2]
    else:
        idx1 = closest_angle_from_herder_ordering[2]
        idx2 = closest_angle_from_herder_ordering[1]
        
    return [idx0, idx1, idx2]



#################################################################################################################
## 3. Complex policies - a combination of the above and/or an above policy that includes 
## a target grouping or clustering function.
threshold =  .33#22 * math.pi / 180.0 #thresnhold angle in radians for collinearity #

def get_successive_collinearity_ordering(T, threshold = threshold):

    closest_angle_from_herder_ordering = get_closest_angle_from_herder_ordering(T)

    successive_closest_angle_ordering = get_successive_closest_angle_from_herder_ordering(T)

    #threshold = .33 #thresnhold angle in radians for collinearity
    targets = {0,1,2}
    targetsContained = set(); #empty set
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    
    
    def get_cluster(idx, t = 0):
        others = targets.difference({idx}.union(targetsContained)) #what are the targets that are remaining, that is not idx and not yet contained?
        cluster = [idx];
        for i in others:
            if abs(angle_between(targetsPos[i][:,t], targetsPos[idx][:,t])) < threshold:
                cluster.append(i)
        return cluster
    
    
    def get_furthest_in_cluster(cluster, t = 0):
        distances = []
        for i in cluster:
            distances.append(dist(targetsPos[i][0,t], targetsPos[i][1,t]))
        j = np.argmax(distances)
        return cluster[j]
    
    initial_cluster = get_cluster(closest_angle_from_herder_ordering[0])

    if len(initial_cluster) == 1:
        t0 = closest_angle_from_herder_ordering[0]
        targetsContained.add(t0)
        if len(get_cluster(closest_angle_from_herder_ordering[1])) == 1: #if there are no clusters
            return successive_closest_angle_ordering
        else: #if 2,3 are in a cluster
            t1 = get_furthest_in_cluster(list(targets.difference({t0})))
            t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 2:
        t0 = get_furthest_in_cluster(initial_cluster)
        t1 = list(set(initial_cluster).difference({t0}))[0]
        t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 3: 
        t0 = get_furthest_in_cluster(initial_cluster)
        targetsContained.add(t0)
        t1 = get_furthest_in_cluster(get_cluster(list(targets.difference({t0}))[0]))
        t2 = list(targets.difference({t0}.union({t1})))[0]
        
    return [t0,t1,t2]


def get_dynamic_collinearity_capturing_ordering(T):

    closest_angle_from_herder_ordering = get_closest_angle_from_herder_ordering(T)
    
    #threshold = 0.33 #thresnhold angle in radians for collinearity
    targets = {0,1,2}
    targetsContained = set(); #empty set
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    targetsCt = np.array([T.t0ct, T.t1ct, T.t2ct])
    
    def get_cluster(idx, t = 0):
        others = targets.difference({idx}.union(targetsContained)) #what are the targets that are remaining, that is not idx and not yet contained?
        cluster = [idx];
        for i in others:
            if abs(angle_between(targetsPos[i][:,t], targetsPos[idx][:,t])) < threshold:
                cluster.append(i)
        return cluster

    def get_furthest_in_cluster(cluster, t = 0):
        distances = []
        for i in cluster:
            distances.append(dist(targetsPos[i][0,t], targetsPos[i][1,t]))
        j = np.argmax(distances)
        return cluster[j]
    
    t0 = get_furthest_in_cluster(get_cluster(closest_angle_from_herder_ordering[0]))
    targetsContained.add(t0)
    
    #look for next closest TA in terms of angles
    targets_remaining = list(targets.difference({t0}))
    t1idx = targets_remaining[0]
    t2idx = targets_remaining[1]

    try:
        t = np.where(targetsCt[t0])[0][0] #when is the first target agent contained?
    except:
        return [0,0,0] # in order to throw a 0 score upon matching with the real ordering.
       
    t1 = targetsPos[t1idx][:,t]
    t2 = targetsPos[t2idx][:,t]
    h = [T.p0x[t], T.p0z[t]]

    a1 = abs(angle_between(h,t1))
    a2 = abs(angle_between(h,t2))

    if a1 < a2:
        idx = t1idx
    else:
        idx = t2idx

    t1 = get_furthest_in_cluster(get_cluster(idx,t),t)
    t2 = list(targets.difference({t0,t1}))[0]

    return [t0, t1, t2]

# successive collinearity policy with noise
def get_stochastic_collinearity_capturing_ordering(T):
    """
    based on the initial conditions, what is the predicted stochastic policy?
    """
    targetsPos = np.array([[T.t0x[0], T.t0z[0]], [T.t1x[0], T.t1z[0]], [T.t2x[0], T.t2z[0]]]) #shape (3, 2)
    
    gamma = .2 #radians
    
    angle0 = angle_between(targetsPos[0], np.array([T.p0x[0], T.p0z[0]])) + np.random.uniform(-gamma,gamma) 
    angle1 = angle_between(targetsPos[1], np.array([T.p0x[0], T.p0z[0]])) + np.random.uniform(-gamma,gamma) 
    angle2 = angle_between(targetsPos[2], np.array([T.p0x[0], T.p0z[0]])) + np.random.uniform(-gamma,gamma)

    angle_ordering = np.argsort(np.abs([angle0, angle1, angle2]))

    #first get first closest TA in angles space
    idx0 = angle_ordering[0]
    pos0 = targetsPos[idx0]

    
    #then get next closest target agents from 
    pos1 = targetsPos[angle_ordering[1]]
    pos2 = targetsPos[angle_ordering[2]]
    
    a1 = abs(angle_between(pos1, pos0)  + np.random.uniform(-gamma,gamma)   )  
    a2 = abs(angle_between(pos2, pos0)  + np.random.uniform(-gamma,gamma)   )  

    #then assign right indices   
    if a1 < a2:
        idx1 = angle_ordering[1]
        idx2 = angle_ordering[2]
    else:
        idx1 = angle_ordering[2]
        idx2 = angle_ordering[1]
    
    successive_angle_ordering =  [idx0, idx1, idx2]
    
    #threshold = .33 #thresnhold angle in radians for collinearity
    targets = {0,1,2}
    targetsContained = set(); #empty set
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
        
    """
    #old cluster function
    def get_cluster(idx, t = 0):
        others = targets.difference({idx}.union(targetsContained)) #what are the targets that are remaining, that is not idx and not yet contained?
        cluster = [idx];
        for i in others:
            if abs(angle_between(targetsPos[i][:,t], targetsPos[idx][:,t])) < threshold:
                cluster.append(i)
        return cluster
    """
    def get_cluster(idx, t=0):
        others = targets.difference({idx}.union(targetsContained)) #what are the targets that are remaining, that is not idx and not yet contained?
        cluster = {idx};
        for i in others:
            if abs(angle_between(targetsPos[i][:,t], targetsPos[idx][:,t])) < threshold:
                cluster.add(i)
        
        if len(cluster.difference({idx})):   
            for j in cluster.difference({idx}):
                remaining = list(targets.difference({idx}.union({j}).union(targetsContained)))
                if len(remaining):
                    assert len(remaining) == 1 #because there are only three targets in total
                    if abs(angle_between(targetsPos[j][:,t], targetsPos[remaining[0]][:,t])) < threshold:
                        cluster.add(remaining[0])         
        return list(cluster)       
    
    def get_furthest_in_cluster(cluster, t = 0):
        distances = []
        for i in cluster:
            distances.append(dist(targetsPos[i][0,t], targetsPos[i][1,t]))
        distances += np.random.uniform(-gamma,gamma,len(distances))
        j = np.argmax(distances)
        return cluster[j]
    
    initial_cluster = get_cluster(angle_ordering[0])

    if len(initial_cluster) == 1:
        t0 = angle_ordering[0]
        targetsContained.add(t0)
        if len(get_cluster(angle_ordering[1])) == 1: #if there are no clusters
            return successive_angle_ordering
        else: #if 2,3 are in a cluster
            t1 = get_furthest_in_cluster(list(targets.difference({t0})))
            t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 2:
        t0 = get_furthest_in_cluster(initial_cluster)
        t1 = list(set(initial_cluster).difference({t0}))[0]
        t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 3: #now with new cluster fucntion, enters here for thhreshold = 0.33. previously didn't
        t0 = get_furthest_in_cluster(initial_cluster)
        targetsContained.add(t0)
        t1 = get_furthest_in_cluster(get_cluster(list(targets.difference({t0}))[0]))
        assert t0 != t1
        t2 = list(targets.difference({t0}.union({t1})))[0]
    return [t0,t1,t2]

# deinfed by heading angle of herding relative ot targets
def get_heading_capturing_ordering(T):
    
    targets = {0,1,2}

    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    targetsCt = np.array([T.t0ct, T.t1ct, T.t2ct])
    
    heading_init = quat_to_angle(T.p0xq[0], T.p0yq[0], T.p0zq[0], T.p0wq[0])
    heading_init_vector = [np.cos(heading_init), np.sin(heading_init)]

    h_0 = [T.p0x[0], T.p0z[0]]

    ha0 = abs(angle_between(heading_init_vector, targetsPos[0][:,0] - h_0))
    ha1 = abs(angle_between(heading_init_vector, targetsPos[1][:,0] - h_0))
    ha2 = abs(angle_between(heading_init_vector, targetsPos[2][:,0] - h_0))

    a0 = abs(angle_between(targetsPos[0][:,0], np.array([T.p0x[0], T.p0z[0]])))
    a1 = abs(angle_between(targetsPos[1][:,0], np.array([T.p0x[0], T.p0z[0]])))
    a2 = abs(angle_between(targetsPos[2][:,0], np.array([T.p0x[0], T.p0z[0]]))) 

    def f(ha, a):
        return a/ha

    idx0 = np.argmin([f(ha0,a0), f(ha1,a1), f(ha2,a2)])
    remaining = list(targets.difference({idx0}))
    try:
        t = np.where(targetsCt[idx0])[0][0]
    except:
        return [0,0,0]
        #return get_collinearity_capturing_ordering(T, successive_angle_ordering)
    t1 = targetsPos[remaining[0]][:,t]
    t2 = targetsPos[remaining[1]][:,t]

    heading_t = quat_to_angle(T.p0xq[t], T.p0yq[t], T.p0zq[t], T.p0wq[t])
    heading_t_vector = [np.cos(heading_t), np.sin(heading_t)]
    h_t = [T.p0x[t], T.p0z[t]]

    ha1 = abs(angle_between(heading_t_vector, t1-h_t))
    ha2 = abs(angle_between(heading_t_vector, t2-h_t))

    a1 = abs(angle_between(h_t,t1))
    a2 = abs(angle_between(h_t,t2))

    if f(ha1,a1) < f(ha2,a2):
        idx1 = remaining[0]
        idx2 = remaining[1]
    else:
        idx1 = remaining[1]
        idx2 = remaining[0]

    return [idx0, idx1, idx2]


#################################################################################################################
## CONSTRUCTION ZONE - HARD HATS OBLIGATORY.

def get_static_collinearity_ordering(T):
    """
    Function to order TAs in the order that they appear to the HA from the latter's initial position only.
    Arguments: T: Time series of trial data
    Output: Ordering eg. [0,2,1]
    """
    
    closest_angle_from_herder_ordering = get_closest_angle_from_herder_ordering(T)

    #threshold = .33 #thresnhold angle in radians for collinearity
    targets = {0,1,2}
    targetsContained = set(); #empty set
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    
    
    def get_cluster(idx, t = 0):
        others = targets.difference({idx}.union(targetsContained)) #what are the targets that are remaining, that is not idx and not yet contained?
        cluster = [idx];
        for i in others:
            if abs(angle_between(targetsPos[i][:,t], targetsPos[idx][:,t])) < threshold:
                cluster.append(i)
        return cluster
    
    
    def get_furthest_in_cluster(cluster, t = 0):
        distances = []
        for i in cluster:
            distances.append(dist(targetsPos[i][0,t], targetsPos[i][1,t]))
        j = np.argmax(distances)
        return cluster[j]
    
    initial_cluster = get_cluster(closest_angle_from_herder_ordering[0])

    if len(initial_cluster) == 1:
        t0 = closest_angle_from_herder_ordering[0]
        targetsContained.add(t0)
        if len(get_cluster(closest_angle_from_herder_ordering[1])) == 1: #if there are no clusters
            return closest_angle_from_herder_ordering
        else: #if 2,3 are in a cluster
            t1 = get_furthest_in_cluster(list(targets.difference({t0})))
            t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 2:
        t0 = get_furthest_in_cluster(initial_cluster)
        t1 = list(set(initial_cluster).difference({t0}))[0]
        t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 3: 
        t0 = get_furthest_in_cluster(initial_cluster)
        targetsContained.add(t0)
        t1 = get_furthest_in_cluster(get_cluster(list(targets.difference({t0}))[0]))
        t2 = list(targets.difference({t0}.union({t1})))[0]
        
    return [t0,t1,t2]

def get_distance_static_collinearity_ordering(T):
    """
    Just like other collinearity measures, except measured with respect to distances
    """
    closest_distance_from_herder_ordering = get_closest_distance_from_herder_ordering(T)

    #threshold = .33 #thresnhold angle in radians for collinearity
    targets = {0,1,2}
    targetsContained = set(); #empty set
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    
    
    def get_cluster(idx, t = 0):
        others = targets.difference({idx}.union(targetsContained)) #what are the targets that are remaining, that is not idx and not yet contained?
        cluster = [idx];
        for i in others:
            if abs(angle_between(targetsPos[i][:,t], targetsPos[idx][:,t])) < threshold:
                cluster.append(i)
        return cluster
    
    
    def get_furthest_in_cluster(cluster, t = 0):
        distances = []
        for i in cluster:
            distances.append(dist(targetsPos[i][0,t], targetsPos[i][1,t]))
        j = np.argmax(distances)
        return cluster[j]
    
    initial_cluster = get_cluster(closest_distance_from_herder_ordering[0])

    if len(initial_cluster) == 1:
        t0 = closest_distance_from_herder_ordering[0]
        targetsContained.add(t0)
        if len(get_cluster(closest_distance_from_herder_ordering[1])) == 1: #if there are no clusters
            return closest_distance_from_herder_ordering
        else: #if 2,3 are in a cluster
            t1 = get_furthest_in_cluster(list(targets.difference({t0})))
            t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 2:
        t0 = get_furthest_in_cluster(initial_cluster)
        t1 = list(set(initial_cluster).difference({t0}))[0]
        t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 3: 
        t0 = get_furthest_in_cluster(initial_cluster)
        targetsContained.add(t0)
        t1 = get_furthest_in_cluster(get_cluster(list(targets.difference({t0}))[0]))
        t2 = list(targets.difference({t0}.union({t1})))[0]
        
    return [t0,t1,t2]

def get_distance_successive_collinearity_ordering(T):
    """
    Just like other collinearity measures, except measured with respect to distances and is now with successive distances
    """
    closest_successive_distance_from_herder_ordering = get_successive_closest_distance_from_herder_ordering(T)

    #threshold = .33 #thresnhold angle in radians for collinearity
    targets = {0,1,2}
    targetsContained = set(); #empty set
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    
    
    def get_cluster(idx, t = 0):
        others = targets.difference({idx}.union(targetsContained)) #what are the targets that are remaining, that is not idx and not yet contained?
        cluster = [idx];
        for i in others:
            if abs(angle_between(targetsPos[i][:,t], targetsPos[idx][:,t])) < threshold:
                cluster.append(i)
        return cluster
    
    
    def get_furthest_in_cluster(cluster, t = 0):
        distances = []
        for i in cluster:
            distances.append(dist(targetsPos[i][0,t], targetsPos[i][1,t]))
        j = np.argmax(distances)
        return cluster[j]
    
    initial_cluster = get_cluster(closest_successive_distance_from_herder_ordering[0])

    if len(initial_cluster) == 1:
        t0 = closest_successive_distance_from_herder_ordering[0]
        targetsContained.add(t0)
        if len(get_cluster(closest_successive_distance_from_herder_ordering[1])) == 1: #if there are no clusters
            return closest_successive_distance_from_herder_ordering
        else: #if 2,3 are in a cluster
            t1 = get_furthest_in_cluster(list(targets.difference({t0})))
            t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 2:
        t0 = get_furthest_in_cluster(initial_cluster)
        t1 = list(set(initial_cluster).difference({t0}))[0]
        t2 = list(targets.difference({t0}.union({t1})))[0]

    elif len(initial_cluster) == 3: 
        t0 = get_furthest_in_cluster(initial_cluster)
        targetsContained.add(t0)
        t1 = get_furthest_in_cluster(get_cluster(list(targets.difference({t0}))[0]))
        t2 = list(targets.difference({t0}.union({t1})))[0]
        
    return [t0,t1,t2]

def get_dynamic_distance_collinearity_capturing_ordering(T):

    closest_distance_from_herder_ordering = get_closest_distance_from_herder_ordering(T)
    
    #threshold = 0.33 #thresnhold angle in radians for collinearity
    targets = {0,1,2}
    targetsContained = set(); #empty set
    targetsPos = np.array([[T.t0x, T.t0z], [T.t1x, T.t1z], [T.t2x, T.t2z]]) #shape (3, 2, N) for N = number timesteps
    targetsCt = np.array([T.t0ct, T.t1ct, T.t2ct])
    
    def get_cluster(idx, t = 0):
        others = targets.difference({idx}.union(targetsContained)) #what are the targets that are remaining, that is not idx and not yet contained?
        cluster = [idx];
        for i in others:
            if abs(angle_between(targetsPos[i][:,t], targetsPos[idx][:,t])) < threshold:
                cluster.append(i)
        return cluster

    def get_furthest_in_cluster(cluster, t = 0):
        distances = []
        for i in cluster:
            distances.append(dist(targetsPos[i][0,t], targetsPos[i][1,t]))
        j = np.argmax(distances)
        return cluster[j]
    
    t0 = get_furthest_in_cluster(get_cluster(closest_distance_from_herder_ordering[0]))
    targetsContained.add(t0)
    
    #look for next closest TA in terms of angles
    targets_remaining = list(targets.difference({t0}))
    t1idx = targets_remaining[0]
    t2idx = targets_remaining[1]

    try:
        t = np.where(targetsCt[t0])[0][0] #when is the first target agent contained?
    except:
        return [0,0,0] # in order to throw a 0 score upon matching with the real ordering.
       
    t1 = targetsPos[t1idx][:,t]
    t2 = targetsPos[t2idx][:,t]
    h = [T.p0x[t], T.p0z[t]]

    a1 = abs(angle_between(h,t1))
    a2 = abs(angle_between(h,t2))

    if a1 < a2:
        idx = t1idx
    else:
        idx = t2idx

    t1 = get_furthest_in_cluster(get_cluster(idx,t),t)
    t2 = list(targets.difference({t0,t1}))[0]

    return [t0, t1, t2]