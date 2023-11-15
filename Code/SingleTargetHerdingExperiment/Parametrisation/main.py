# import relevant packages

import subprocess
import os
import socket
import numpy as np
import random
import pandas as pd
from scipy.optimize import minimize
import numpy as np
import pandas as pd
import similaritymeasures
from pathlib import Path

# set needed parameters and variables

target_offset = 8.5

b = 3.5
kg = 43.3789
c1 = 0.1 
c2 = 0.3911
ko = 176.3562
c3 = 1.25
c4 = .05
c5 = .8
#c3_obs_G = 0.7108
#c4_obs_G = 0.1698

directory = os.getcwd()

simNumber = 0 #won't be used for now

valid_trial_IDs = [6,7,8,9,10,11,12,13,14,15,16,17];

# for a particular trial ID, load relevent human mean trajectory data and initial conditions

def parametrisation_step(trialID):
    parametrisations_per_trial_ID = 10
    params_found = np.zeros((parametrisations_per_trial_ID, 2)) # 2 for two of kg, ko
    
    
    def run_process(init_param_vals): 
        def traj_error(k):
            def FW_Model(target_offset,b,kg,c1,c2,ko,c3,c4,c5,c3_obs_G,c4_obs_G):
                #send new parameters   
                message = '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(simNumber,herder_xpos,herder_zpos,target_xpos,target_zpos,herder_angle,target_offset,b,kg,c1,c2,ko,c3,c4,c5,c3_obs_G, c4_obs_G)
                connection.sendall(message.encode('utf-8'))
    
                # Check for new game data 
                data_bytes = connection.recv(4)
                data = data_bytes.decode('utf-8')           
                #print('received: %s' % data)

                # Process game data if received
                if data == "done":
                    M = pd.read_csv(directory+'\Build\FW_Herding_Data\SimData\simData.csv');
                    sim_data = pd.DataFrame([M.P1xpos, M.P1zpos]).T
                else:
                    # break if no more data comming in from client    
                    print('no more data from', client_address)
                return sim_data
            c3_obs_G = k[0] #
            c4_obs_G = k[1] #
            print('c3_obs_G: %s' % c3_obs_G)
            print('c4_obs_G: %s' % c4_obs_G)
            sim = FW_Model(target_offset,b,kg,c1,c2,ko,c3,c4,c5, c3_obs_G, c4_obs_G)
            return MyDist(mean_human_data,sim)
        # run process
        # **************************************************************************

        options = {'eps': 0.01, 'disp': True}

        
        print('connection from', client_address)
        res = minimize(traj_error,init_param_vals, method='SLSQP', bounds = ((.1,1.0),(.1,1.0)), options = options) # (parameter) bounds
        return res.x
    #loading human data
    M = pd.read_excel('init_conds_trial_set.xlsx')
    i = M.loc[M['Trial_ID'] == trialID].index[0]
    
    assert M.Trial_ID[i] == trialID, "Got wrong initial condition data!"
        
    herder_xpos = M.P1xpos0[i];
    herder_zpos = M.P1zpos0[i]
    herder_angle = M.P1Heading0[i]

    target_xpos = M.Targetxpos0[i]
    target_zpos = M.Targetzpos0[i]

    #load mean human trajectory corresponding to trial ID 
    M = pd.read_csv(directory+'\MEAN_HUMAN_TRAJECTORIES\MEAN_HUMAN_Trial_ID_'+ str(trialID).zfill(2) +'.csv');
    mean_human_data = pd.DataFrame([M.P1xpos, M.P1zpos]).T;
    
    for i in range(parametrisations_per_trial_ID):
        c3_obs_G_init = np.random.uniform(.1,1.0)
        c4_obs_G_init = np.random.uniform(.1,1.0)
        init_param_vals = np.array([c3_obs_G_init, c4_obs_G_init])
        params_found[i,:] = run_process(init_param_vals)
        
    
    
    df = pd.DataFrame(params_found, columns = ['c3_obs_G', 'c4_obs_G'])
    file_name =  directory+'\PARAMS_OUTGOING\params_outgoing_' + str(trialID).zfill(2) +'.csv'
    filepath = Path(file_name)
    df.to_csv(filepath, index = False)
    
    return

# functions that we will need 
def MyDist(P,Q):
    err, _ = similaritymeasures.dtw(np.column_stack((P.P1xpos.to_numpy(), P.P1zpos.to_numpy())), np.column_stack((Q.P1xpos.to_numpy(), Q.P1zpos.to_numpy())))
    print('Error: %s' % err)
    return err

#os.mkdir(directory+'\PARAMS_OUTGOING') #folder to which all the outgoing parameters will be stored

# Create a TCP/IP socket
# Initialize TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10000)                     # Set TCP server address
sock.bind(server_address)                                 # Bind the TCP socket address to the port
# Print TCP socket info to terminal
print('starting up on %s port %s' % server_address)
sock.listen(1)

# open unity exe file  
subprocess.Popen([directory+'\Build\FW_Herding.exe'])

# First, waits for clinet connection from unity game
print('waiting for a connection')
connection, client_address = sock.accept()

for trialID in valid_trial_IDs:
    parametrisation_step(trialID)
    
# Finally, close up the connection
print("DONE")
connection.close()

