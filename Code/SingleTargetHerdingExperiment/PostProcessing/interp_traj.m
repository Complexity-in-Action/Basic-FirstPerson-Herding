function interp_arr = interp_traj(arr, N_up)
N  = N_up;
t_min = min(arr);
t_max = max(arr);
t_orig = linspace(t_min, t_max, length(arr));
t_interp = linspace(t_min, t_max, N);
interp_arr = interp1(t_orig, arr, t_interp, 'spline');