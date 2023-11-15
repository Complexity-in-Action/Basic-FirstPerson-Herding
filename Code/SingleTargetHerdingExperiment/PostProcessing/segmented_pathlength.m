function l = segmented_pathlength(T)

x = T(1,:);
y = T(2,:);


dx = diff(x);
dy = diff(y);


point_to_point_distances = sqrt(dx.^2 + dy.^2);

l= 0;

for idx = 1:length(x) -1 
    if point_to_point_distances(idx) < 1
        l = l  + point_to_point_distances(idx);
    end
end