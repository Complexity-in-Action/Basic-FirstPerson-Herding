%% Clean up
clear
close all
clc

%% Load up the files
file_name_header = "params_outgoing_";

files = dir(strcat(file_name_header,"*.csv"));

%% Load up all the medians
medians_kg = zeros(length(files),1);
medians_ko = zeros(length(files),1);

for idx = 1:length(files)
    T = readtable(files(idx).name);
    medians_kg(idx) = median(T.kg);
    medians_ko(idx) = median(T.ko);
end

%% Median, mean, SD of all the trials
MEDIAN_kg = median(medians_kg)
MEAN_kg = mean(medians_kg);
STD_kg = std(medians_kg);

MEDIAN_ko = median(medians_ko)
MEAN_ko = mean(medians_ko);
STD_ko = std(medians_ko);

