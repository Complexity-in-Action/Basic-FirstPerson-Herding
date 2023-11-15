function [percentile_error, mean_error, sd_error, idx_human] = between_error(NORMED_TRAJECTORIES,percentile)
mean_X = mean(NORMED_TRAJECTORIES(:,:,1), 2);
mean_Y = mean(NORMED_TRAJECTORIES(:,:,2), 2);
mean_X = smooth(mean_X,100);
mean_Y = smooth(mean_Y,100);
DIMS = size(NORMED_TRAJECTORIES);
errors = zeros(DIMS(2),1);
distances = zeros(DIMS(2),1);
for player_idx = 1:DIMS(2)
    X = NORMED_TRAJECTORIES(:,player_idx,1);
    Y = NORMED_TRAJECTORIES(:,player_idx,2);
    %errors(player_idx) = MyDist2([X,Y], [mean_X, mean_Y]);
    [errors(player_idx), ix,iy] = dtw([X,Y]', [mean_X, mean_Y]');
    distances(player_idx) = errors(player_idx) / length(ix);
end
errors_sorted = sort(errors);
idx = floor(percentile/100*DIMS(2));
percentile_error = errors_sorted(idx); %percetileth-best human
idx_human = find(percentile_error == errors);
mean_error = mean(distances);
sd_error = std(distances);

