function [P1xpos_downsampled, P1zpos_downsampled] = time_normalise(M, N_up, N_down);
% upsample to N_up points
try
    P1xpos_upsampled = interp_traj(M.P1xpos, N_up);
    P1zpos_upsampled = interp_traj(M.P1zpos, N_up);
catch
    P1xpos_upsampled = interp_traj(M.p0x, N_up);
    P1zpos_upsampled = interp_traj(M.p0z, N_up);
end

    

% downsample to N_down points

ds_ratio = N_up / N_down; % downsampling ratio
P1xpos_downsampled = downsample(P1xpos_upsampled, ds_ratio);
P1zpos_downsampled = downsample(P1zpos_upsampled, ds_ratio);

