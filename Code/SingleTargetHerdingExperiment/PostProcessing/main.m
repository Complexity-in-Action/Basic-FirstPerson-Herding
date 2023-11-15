close all
clear 
clc


valid_trial_IDs = [19,20,21,22];

pathlengths = zeros(1,1);
trialtimes = zeros(1,1);
avoidance_distances = zeros(1,1);
tht = zeros(1,1);

pathlengths_sim = zeros(length(valid_trial_IDs),1);
trialtimes_sim = zeros(length(valid_trial_IDs),1);
avoidance_distances_sim = zeros(length(valid_trial_IDs),1);
sim_mean_errors = zeros(length(valid_trial_IDs),1);
c_sim = zeros(length(valid_trial_IDs),1);

c_s = zeros(length(valid_trial_IDs),1);
c_h = zeros(length(valid_trial_IDs),1);

R_G = 4;
theta = [0:0.01:1] * 2 * pi;
X_max = 60;
X_min = - X_max;
Y_max = 45;
Y_min = - Y_max;
X_lims = [X_min:0.1:X_max];
Y_lims = [Y_min:0.1:Y_max];

read_folder_name = "../../../Data/SingleTargetHerdingExperiment/Processed/Filtered/"; 

player_folders = dir(strcat(read_folder_name, "Session*"));%all folders in ExperimentA


simulation_folder = "Simulations/TestSet";
trial_count = 0;
N_up = 10000;
N_down = 1000;

sim_errors = zeros(length(valid_trial_IDs),1);
human_errors = zeros(length(valid_trial_IDs),1);
mean_errors = zeros(length(valid_trial_IDs),1);
sd_errors = zeros(length(valid_trial_IDs),1);

valid_files = 0;
for trial_identifier = valid_trial_IDs
    trial_count = trial_count + 1;
    
    simulation_file_names = dir(strcat("../../../Data/SingleTargetHerdingExperiment/",simulation_folder,"/trialIdentifier",num2str(trial_identifier,'%02.f'),"_*"));
    
    colors = ['r'; 'y'; 'c'; 'm'; 'b']; %for more than one simulation per trial ID in the same folder

    subplot(2,2,trial_count)

    
    for i = 1:length(simulation_file_names)
        file_name = strcat("../../../Data/SingleTargetHerdingExperiment/",simulation_folder,"/", simulation_file_names(i).name);
        M_sim = readtable(file_name);
        M_sim = M_sim(1:height(M_sim) - round((height(M_sim)*.20)),:); %chop off last 20% of simulated trajectory
        
        trialtimes_sim(trial_count) = M_sim.trialtime(end) - M_sim.trialtime(1);
        [P1xpos_t_normed_sim, P1zpos_t_normed_sim] = time_normalise(M_sim, N_up, N_down);
        
        plot(P1xpos_t_normed_sim, P1zpos_t_normed_sim, '.','Color','r', 'MarkerSize',10,'DisplayName','Simulation')
        hold on
        pathlengths_sim(trial_count) = pathlength([P1xpos_t_normed_sim',P1zpos_t_normed_sim']');
        
       hold on
    end
    
    NORMED_TRAJECTORIES = zeros(N_down, 1, 2);
     file_count = 0;
    
    
    
    for player_count = 1:length(player_folders)
    
    
    
        player_ID = player_folders(player_count);
        
        if (player_ID.name == "Session01") || (player_ID.name == "Session03")
            name = strcat("00", player_ID.name(8:end));
        else
            name = player_ID.name(8:end);
        end
        
        directory = strcat(player_ID.folder,'\', player_ID.name, "\ExperimentData\FirstPersonHerding_session", name, "__trialIdentifier", num2str(trial_identifier,'%02.f'), '*');
        
        file = dir(directory);
        
        try
            M = readtable(strcat(file.folder, '\',file.name));

        catch
            continue
        end
        file_count = file_count+ 1;
        
        M = trim(M);
        trialtimes(trial_count, file_count) = M.time(end) - M.time(1);
        
        
        
        hold on
    
        pathlengths(trial_count, file_count) = pathlength([M.p0x'; M.p0z']);
        
       hold on
        
        [P1xpos_t_normed, P1zpos_t_normed] = time_normalise(M, N_up, N_down);
        
    
        NORMED_TRAJECTORIES(:, file_count,1) = P1xpos_t_normed;
        NORMED_TRAJECTORIES(:, file_count,2) = P1zpos_t_normed;
       
        plot(M.t0x(1), M.t0z(1), 'o','MarkerFaceColor','g', 'DisplayName', 'Target init cond', 'MarkerSize', 15)
    end
    valid_files = valid_files + file_count;
    
    
    
  
    mean_X = mean(NORMED_TRAJECTORIES(:,:,1), 2);
    mean_Y = mean(NORMED_TRAJECTORIES(:,:,2), 2);
    
    
    
    mean_X = smooth(mean_X,100);
    mean_Y = smooth(mean_Y,100);
    

    [errors_sim, ix,iy] = dtw([P1xpos_t_normed_sim', P1zpos_t_normed_sim']', [mean_X, mean_Y]');
    sim_mean_errors(trial_count) = errors_sim / length(ix);


    plot(mean_X, mean_Y, 'k.', 'MarkerSize',10)
    hold on
    plot(mean_X(1), mean_Y(1),'o','MarkerFaceColor',[0.9290 0.6940 0.1250], 'DisplayName', 'Herder init cond', 'MarkerSize', 15)
    hold on
    
    %%%%% SD Bounds
    SD_right = zeros(N_down-1, 2);
    SD_left = zeros(N_down-1, 2);
    for idx = 1:N_down-1 % for each index in the mean human trajectory
       slope = (mean_Y(idx+1) - mean_Y(idx)) / (mean_X(idx+1) - mean_X(idx)); %slope at that index
    
    
       m = -1/slope; %slope for perpendicular line
       b = mean_Y(idx) - m*mean_X(idx); %y-intercept of that line
       x = NORMED_TRAJECTORIES(idx,:,1);
       y = NORMED_TRAJECTORIES(idx,:,2);
    
       perpSlope = -1/m;
       
    
       yInt = -perpSlope * x + y;
       xIntersection = (yInt - b) / (m - perpSlope); 
       yIntersection = perpSlope * xIntersection + yInt; 
    
       perp_distance_values = sqrt((xIntersection - mean_X(idx)).^2 + (yIntersection - mean_Y(idx)).^2);
       factor_distance= 1.65*std(perp_distance_values); % 1.65 sigma = 90%
       
       y_right = mean_Y(idx) + factor_distance*sin(atan(m));
       x_right = mean_X(idx) + factor_distance*cos(atan(m));
    
       y_left = mean_Y(idx) - factor_distance*sin(atan(m));
       x_left = mean_X(idx) - factor_distance*cos(atan(m));
    
       SD_left(idx,1) = x_left;
       SD_left(idx,2) = y_left;
       SD_right(idx,1) = x_right;
       SD_right(idx,2) = y_right;
    end


    P = [(SD_right(1,1) + SD_left(1,1))/2; SD_right(:,1); (SD_right(end,1) + SD_left(end,1))/2; (SD_right(1,1) + SD_left(1,1))/2; SD_left(:,1); (SD_right(end,1) + SD_left(end,1))/2];
    Q = [(SD_right(1,2) + SD_left(1,2))/2; SD_right(:,2); (SD_right(end,2) + SD_left(end,2))/2; (SD_right(1,2) + SD_left(1,2))/2; SD_left(:,2); (SD_right(end,2) + SD_left(end,2))/2];

      pgon=polyshape(P, Q);
     plot(pgon,'FaceColor',[.7 .7 .7])

    [in,on] = isinterior(pgon,P1xpos_t_normed_sim, P1zpos_t_normed_sim);
%     percent_in = sum(in) / 10;

    [human_error, mean_error, sd_error, idx_human] = between_error(NORMED_TRAJECTORIES,90);

    P1xpos_t_normed_human_percentiled = NORMED_TRAJECTORIES(:,idx_human,1)';
    P1zpos_t_normed_human_percentiled = NORMED_TRAJECTORIES(:,idx_human,2)';
    hold on
%     plot(P1xpos_t_normed_human_percentiled, P1zpos_t_normed_human_percentiled, 'r.') %90-th percentile human

    percent_in_simulation = segmented_pathlength([P1xpos_t_normed_sim(in)', P1zpos_t_normed_sim(in)']') / pathlength([P1xpos_t_normed_sim',P1zpos_t_normed_sim']') * 100;
    c_s(trial_count) = percent_in_simulation;
    [in,on] = isinterior(pgon,P1xpos_t_normed_human_percentiled, P1zpos_t_normed_human_percentiled);
    percent_in_human = segmented_pathlength([P1xpos_t_normed_human_percentiled(in)', P1zpos_t_normed_human_percentiled(in)']') / pathlength([P1xpos_t_normed_human_percentiled', P1zpos_t_normed_human_percentiled']') * 100;
    c_h(trial_count) = percent_in_human;
    xlabel('$x [\mathrm{m}]$', 'Interpreter','latex')
    ylabel('$y [\mathrm{m}]$', 'Interpreter','latex')

    %write the mean
    write_file_name = strcat("MEAN_HUMAN_Trial_ID_", num2str(trial_identifier,'%02.f'), ".csv");
    T = array2table([mean_X, mean_Y]);
    T.Properties.VariableNames = {'P1xpos', 'P1zpos'};

    hold on
    
    plot(NORMED_TRAJECTORIES(:,:,1), NORMED_TRAJECTORIES(:,:,2),'Color','k', 'MarkerSize',10)%;[.7 .7 .7]);
    hold on
    
    xlim([X_min+0.1*X_min X_max+0.1*X_max])
    ylim([Y_min+0.1*Y_min Y_max+0.1*Y_max])
    
    
    
    
    plot(R_G*cos(theta),R_G*sin(theta),'.','Color', 'r', 'DisplayName', 'Containment Zone');
    plot(X_lims, Y_max*ones(size(X_lims)), '.', 'Color', [0.5 0.5 0.5], 'DisplayName', 'North wall'); % North Wall
    plot(X_lims, Y_min*ones(size(X_lims)), '.', 'Color', [0.5 0.5 0.5], 'DisplayName', 'South wall'); % South Wall
    plot(X_min*ones(size(Y_lims)), Y_lims, '.', 'Color', [0.5 0.5 0.5], 'DisplayName', 'West wall'); % West Wall
    plot(X_max*ones(size(Y_lims)), Y_lims, '.', 'Color', [0.5 0.5 0.5], 'DisplayName', 'East wall'); % East Wall
    ax = gca;
    ax.FontSize = 20;
    
    
   
    sim_error = dtw([mean_X, mean_Y]', [P1xpos_t_normed_sim', P1zpos_t_normed_sim']');
    sim_errors(trial_count) = sim_error;

    

    pos_X = 15;
    pos_Y = 20;
    if trial_count == 3
        pos_Y = -10;
    elseif trial_count == 6 || trial_count == 4
        pos_X = -25;
    elseif trial_count == 5
        pos_X = -25;
        pos_Y = 25;
    end
       

    if trial_identifier == 21
        label = "13 top";
    elseif trial_identifier == 22
        label = "13 bottom";
    else
        label = string(trial_identifier-5);
    end

    title(strcat("Trial ID: ", label))
    axis equal
    human_errors(trial_count) = human_error;
    mean_errors(trial_count) = mean_error;
    sd_errors(trial_count) = sd_error;
    

end


ps = zeros(length(valid_trial_IDs),1);
p_sd = zeros(length(valid_trial_IDs),1);
tts = zeros(length(valid_trial_IDs),1);
tts_sd = zeros(length(valid_trial_IDs),1);
ads = zeros(length(valid_trial_IDs),1);
ads_sd = zeros(length(valid_trial_IDs),1);
thts = zeros(length(valid_trial_IDs),1);
thts_sd = zeros(length(valid_trial_IDs),1);

for idx = 1:length(valid_trial_IDs)
    ps(idx) = mean(nonzeros(pathlengths(idx,:)));
    p_sd(idx) = std(nonzeros(pathlengths(idx,:)));

    tts(idx) = mean(nonzeros(trialtimes(idx,:)));
    tts_sd(idx) = std(nonzeros(trialtimes(idx,:)));

end


disp("*******************************************************************")
disp("Pathlengths")
[h,p,ci,stats]=ttest2(pathlengths_sim, ps)
disp("*******************************************************************")
disp("Trial Times")
[h,p,ci,stats]=ttest2(trialtimes_sim, tts)
disp("*******************************************************************")
disp("Coverage percentage")
[h,p,ci,stats]=ttest2(c_s, c_h)
disp("*******************************************************************")
disp("DTW Errors")
[h,p,ci,stats]=ttest2(sim_errors,human_errors)
disp("*******************************************************************")


CHARACTERISTICS_TABLE = table;
CHARACTERISTICS_TABLE.trial_ID = [19,20,21,22]';
CHARACTERISTICS_TABLE.ps_hum = round(ps,1);
CHARACTERISTICS_TABLE.ps_sd = round(p_sd,1);
CHARACTERISTICS_TABLE.ps_sim = round(pathlengths_sim,1);
CHARACTERISTICS_TABLE.tts_hum = round(tts,1);
CHARACTERISTICS_TABLE.tts_sd = round(tts_sd,1);
CHARACTERISTICS_TABLE.tts_sim = round(trialtimes_sim,1);

CHARACTERISTICS_TABLE.c_h = round(c_h,1);
CHARACTERISTICS_TABLE.c_s = round(c_s,1);
CHARACTERISTICS_TABLE.DTW_h = round(human_errors);
CHARACTERISTICS_TABLE.DTW_s = round(sim_errors);
MEANS_CHARACTERISTICS = table( 999, ...
    round(mean(CHARACTERISTICS_TABLE.ps_hum),1), ...
    round(mean(CHARACTERISTICS_TABLE.ps_sd),1), ...
    round(mean(CHARACTERISTICS_TABLE.ps_sim),1), ...
    round(mean(CHARACTERISTICS_TABLE.tts_hum),1), ...
    round(mean(CHARACTERISTICS_TABLE.tts_sd),1), ...
    round(mean(CHARACTERISTICS_TABLE.tts_sim),1), ...
    round(mean(CHARACTERISTICS_TABLE.c_h),1), ...
    round(mean(CHARACTERISTICS_TABLE.c_s),1), ...
    round(mean(CHARACTERISTICS_TABLE.DTW_h)), ...
    round(mean(CHARACTERISTICS_TABLE.DTW_s)));
MEANS_CHARACTERISTICS.Properties.VariableNames = CHARACTERISTICS_TABLE.Properties.VariableNames;
T = [CHARACTERISTICS_TABLE; MEANS_CHARACTERISTICS];

T.DTW_h = T.DTW_h / 1000.;
T.DTW_s = T.DTW_s / 1000.;

table2latex(T, 'table')

