# load up relevant liraries
from utils import * #custom-built functions
import os # for directories
from pathlib import Path
import math # for pi
#import similaritymeasures #for DTW distance function

cwd = os.getcwd() # Current working directory
read_dataDir = os.path.join(Path(cwd).parents[2], "Data\SingleTargetHerdingExperiment\Processed\Filtered") #Directory of all sessions with the six outliers discarded 
write_dataDir = os.path.join(Path(cwd).parents[2], "Data\SingleTargetHerdingExperiment\Processed\Mean") # directory to write mean human trajectories to

first_trial = 6 # first five trials were practise trials
last_trial = 17 + 1 # 17 because that's the set of parametrisation trials, + 1 for pythonic indexing

fig, _ = plt.subplots(3, 4,figsize=(32,18)) # 15 sub-figures in three rows of five columns
axes = fig.get_axes()

for trial_count, trial in enumerate(range(first_trial, last_trial)):
    participant_count = 0 # because not all participants have completed all trials satisfactorily (some trajectories are discarded)
    trial_ID = "{:02}".format(trial) # put in string format with leading zero if needed
    filePaths = [path for path in Path(read_dataDir).rglob('*trialIdentifier'+trial_ID+'*')] # get files corresponding to particular trialID across all participants
    num_participants = len(filePaths) #how many participants have completed this trial properly
    NORMED_TRAJS = np.zeros((num_participants, 2, 1000)) # initialise array to store time-normalised trajectories
    for filePath in filePaths: # for each participant
        T = pd.read_csv(filePath)
        plotter(T, axes[trial_count], trial_count, 'k') # visualise
        NORMED_TRAJS[participant_count, 0, :], NORMED_TRAJS[participant_count, 1, :] = time_normalize(T) #note that this also snips off trajectories for appropriate end of herder activity. refer function definition
        participant_count +=1
    MEAN_TRAJ = np.mean(NORMED_TRAJS, axis=0) #get mean trajectory per trial
    axes[trial_count].plot(MEAN_TRAJ[0], MEAN_TRAJ[1], 'k.', markersize = 5) # plot mean trajectory
    d = {'P1xpos': MEAN_TRAJ[0], 'P1zpos': MEAN_TRAJ[1]} # arrange in suitable format
    pd.DataFrame(data=d).to_csv(write_dataDir+'\MEAN_HUMAN_Trial_ID_'+trial_ID+'.csv') #write in correct folder

fig.show() # show all subplots
plt.waitforbuttonpress(0) # wait for button press before closing