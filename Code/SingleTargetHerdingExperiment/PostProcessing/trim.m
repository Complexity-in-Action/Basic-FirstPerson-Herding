function M_trimmed = trim(M) 
%M_trimmed = M (1:height(M) - round((height(M)*.30)),:);
t0 = find(string(M.t0run)=="True",1);
idx = find(string(M.t0run(t0:end))=="False",1);
final = t0+idx;
M_trimmed = M(1:final,:);
end