# Basic First Person Herding
This repository contains code (in python, matlab and jupyter notebook), experimental data collection and simulation builds (made with Unity) in order to reproduce the results of the experiment detailed in bin Kamruddin, A., Sandison, H., Patil, G., Musolesi, M., di Bernardo, M., & Richardson, M. J. (2023). Modeling Human Navigation and Decision Dynamics in First-Person Herding Tasks, under review.

## Instructions


### Experiment: 
Please run the .exe file present in the Experiment/FirstPersonHerdingExperiment folder. "Player ID" needs to be a four-digit number and "Experiment Code" can be any number. For "Select iniFile Name", one may select "iniExperimentA.csv" for the single-target, or "iniExperimentB.csv" for the multi-target data collection experiments. Then, click play to launch the experiment.

### Simulation: 

Please run Simulator/FirstPersonHerding.exe

- You will need to select one of "Experiment A," for the single-target herding experiment simulation, or "Experiment B" for the multi-target herding experiment simulation.
- You can adjust the Time Scale slider in order to speed up or slow down the simulation.
- You can check the "Save Data" box in order to save the simulation data. This will be saved in Simulator/FirstPersonHerding_Data/OutData.
- Click "START" to start the simulation.
- NB: you may ignore the "All Participant Data", "Observed TS Policy" and "Single Trial" inputs.

### Code and Data: 

Please place the "Data" folder, found  [here](https://data.mendeley.com/datasets/gcf4mhtb4s/1), in the same directory as the "Code" folder from this repository. 

Here is the recommended order in which to run the files

#### Single-Target Herding Experiment

- **Code/SingleTargetHerdingExperiment/PreProcessing/get_mean_human_trajectories.py**:
Calculates the mean of the time-normalised human trajectories per trial, after performing necessary trimming to account for the end of the herder activity. Displays the results as a plot and writes the mean human trajectories to the Data folder.

- **Code/SingleTargetHerdingExperiment/Parametrisation/main.py**:
Runs the model parametrisation on the mean human trajectories. As is, it runs the parametrisation for c_5 and c_6. This code can be easily modified to run the parametrisation for other parameter pairs, c_1 and c_2 for example. 

- **Code/SingleTargetHerdingExperiment/PostProcessing/main.m**:
Calculates the trajectory measures of human and simulation fits (path length, navigation time, coverage percentage and DTW error). Performs t-tests on these results.

#### Multi-Target Herding Experiment

- **Code/MultiTargetHerdingExperiment/FindTargetSelectionPolicy.ipynb**:
Predicts the order of first engagement with the various target agents according to the various defined policies. Calculates the mutually-exclusive and non-mutually-exclusive scores of each of this predicted ordering. This code also plots the actual run-order of human target selection policies and represents the same as a bar plot.

- **Code/MultiTargetHerdingExperiment/simReader.ipynb**:
This plots the simulation against the human trajectories, along with weighted and binary trace maps.
Note: for this to run, the simulation files from running the simulation build (see above, section Simulation) need to be placed in the correct folder (see code). 

- **Code/MultiTargetHerdingExperimentValidation/FindTargetSelectionPolicy.ipynb**:
Same as Code/MultiTargetHerdingExperiment/FindTargetSelectionPolicy.ipynb above, but for the target selection policy validation dataset.

- **Code/MultiTargetHerdingExperimentValidation/OptimiseThreshold.ipynb**:
Estimates the thresholds of each of the players' criteria for cluster identification.



