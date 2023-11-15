%% Clean up
clear
close all
clc

%% Load up the files
file_name_header = "params_outgoing_";

files = dir(strcat(file_name_header,"*.csv"));

%% Load up all the medians
medians_c1 = zeros(length(files),1);
medians_c2 = zeros(length(files),1);

for idx = 1:length(files)
    T = readtable(files(idx).name);
    medians_c1(idx) = median(T.c1);
    medians_c2(idx) = median(T.c2);
end

%% Median, mean, SD of all the trials
MEDIAN_c1 = median(medians_c1)
MEAN_c1 = mean(medians_c1);
STD_c1 = std(medians_c1);

MEDIAN_c2 = median(medians_c2)
MEAN_c2 = mean(medians_c2);
STD_C2 = std(medians_c2);

