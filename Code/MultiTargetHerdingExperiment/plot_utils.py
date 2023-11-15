import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from utils import * # for project-specific custom functions

field_dimensions = [120, 90] # the field (walls) are of dimensions 120 by 90 m
    
def plot_circle(x,y,r=4,color='maroon'): #simple function to plot the containment zone rings
    theta = np.linspace(-np.pi, np.pi, 100)
    plt.plot(x+ r*np.cos(theta), y+ r*np.sin(theta),color)
    return

def plot_walls():
    X_max = field_dimensions[0] /2
    X_min = -X_max
    Y_max = field_dimensions[1] /2
    Y_min = -Y_max #positions of walls

    X_lims = np.arange(X_min, X_max, 0.01);
    Y_lims = np.arange(Y_min, Y_max, 0.01);
    plt.plot(X_lims, Y_max*np.ones(np.size(X_lims)), color='0.8')# North Wall
    plt.plot(X_lims, Y_min*np.ones(np.size(X_lims)), color='0.8')# South Wall
    plt.plot(X_min*np.ones(np.size(Y_lims)), Y_lims, color='0.8')# West Wall
    plt.plot(X_max*np.ones(np.size(Y_lims)), Y_lims, color='0.8')# East Wall
    return

def plot_trialtrajectories(data, numHerders, numTargets, title):
    for h in range(numHerders):
        hcolx = 'p%dx' % (h)
        hcolz = 'p%dz' % (h)
        hcolxq = 'p%dxq' % (h)
        hcolyq = 'p%dyq' % (h)
        hcolzq = 'p%dzq' % (h)
        hcolwq = 'p%dwq' % (h)
        heading_init = R.from_quat([data[hcolxq][0], data[hcolyq][0], data[hcolzq][0], data[hcolwq][0]]).as_rotvec()[1]
        plt.arrow(data[hcolx][0], data[hcolz][0], np.cos(heading_init), np.sin(heading_init), shape = 'full', lw = 0,length_includes_head=True, head_width=2.5)
        plt.text(data[hcolx][0], data[hcolz][0], 'H%d' % (h))
        plt.plot(data[hcolx], data[hcolz], c=[0,0,.7], linestyle='dashed')
    
    for t in range(numTargets):
        tcolx = 't%dx' % (t)
        tcolz = 't%dz' % (t)
        plt.plot(data[tcolx][0], data[tcolz][0], c='r',  marker = 'o')
        plt.plot(data[tcolx], data[tcolz], c=[.7,0,0], linestyle='dashed')
        plt.text(data[tcolx][0], data[tcolz][0], 'T%d' % (t))

    plot_circle(0,0)
    plot_walls()

    plt.title(title)
    plt.figure()
    plt.show()
    return

def plot_initialconditions(data, numHerders, numTargets, title):
    for h in range(numHerders):
        hcolx = 'p%dx' % (h)
        hcolz = 'p%dz' % (h)
        hcolxq = 'p%dxq' % (h)
        hcolyq = 'p%dyq' % (h)
        hcolzq = 'p%dzq' % (h)
        hcolwq = 'p%dwq' % (h)
        heading_init = R.from_quat([data[hcolxq][0], data[hcolyq][0], data[hcolzq][0], data[hcolwq][0]]).as_rotvec()[1]
        plt.arrow(data[hcolx][0], data[hcolz][0], np.cos(heading_init), np.sin(heading_init), shape = 'full', lw = 0,length_includes_head=True, head_width=2.5)
        plt.text(data[hcolx][0], data[hcolz][0], 'H%d' % (h))
    
    for t in range(numTargets):
        tcolx = 't%dx' % (t)
        tcolz = 't%dz' % (t)
        plt.plot(data[tcolx][0], data[tcolz][0], c='r',  marker = 'o')
        plt.text(data[tcolx][0], data[tcolz][0], 'T%d' % (t))

    plot_circle(0,0)
    plot_walls()

    plt.title(title)
    plt.figure()
    plt.show()
    return

#function to plot the trials along with the right colors for the target orderings.
def plotter(T, ordering, colors): 
    """
    arguments:
    T: data file
    ordering: ordering in which to plot the targets red, green and then blue
    if ordering is [0, 2, 1] then the 0th target is red, 2th target is green and 1th target is blue

    returns none
    """
    heading_init = R.from_quat([T.p0xq[0], T.p0yq[0], T.p0zq[0], T.p0wq[0]]).as_rotvec()[1]
    plt.arrow(T.p0x[0], T.p0z[0], np.cos(heading_init), np.sin(heading_init), shape = 'full', lw = 0,length_includes_head=True, head_width=2.5)
    plt.plot(T.p0x, T.p0z, c=[.7,.7,.7])
    
    plot_colors = ['a','a','a']
    j=0
    
    for i in ordering:
        plot_colors[i] = colors[j]
        j +=1
    
    
    
    plt.plot(T.t0x[0], T.t0z[0], c=plot_colors[0],  marker = 'o')
    plt.plot(T.t0x, T.t0z, plot_colors[0])
    plt.text(T.t0x[0], T.t0z[0], 'A', fontsize = 12)
    
    plt.plot(T.t1x[0], T.t1z[0], c=plot_colors[1],  marker = 'o')
    plt.plot(T.t1x, T.t1z, plot_colors[1])
    plt.text(T.t1x[0], T.t1z[0], 'B', fontsize = 12)
    
    plt.plot(T.t2x[0], T.t2z[0], c=plot_colors[2],  marker = 'o')
    plt.plot(T.t2x, T.t2z, plot_colors[2])
    plt.text(T.t2x[0], T.t2z[0], 'C', fontsize = 12)
    
    #plt.set_xlabel("x[m]")
    #plt.set_ylabel("y[m]")
    
    
    plot_circle(0,0)
    plot_walls()
    return