function l = pathlength(T)

x = T(1,:);
y = T(2,:);


dx = diff(x);
dy = diff(y);

l = sum(sqrt(dx.^2 + dy.^2));