filename='../ruby/2009_0402_1243_48.waveform';
filename='../ruby/2011_0218_1656_48.waveform';

%2011_0218_1653_41.waveform
%2011_0218_1656_48.waveform
%2011_0218_1713_55.waveform

data_dir='../ruby';
basename='2011_0218_1813_12';

waveform_extension='.waveform';
preamble_extension='.preamble';

waveform_filename=sprintf('%s%s',basename,waveform_extension);
preamble_filename=sprintf('%s%s',basename,preamble_extension);

graff=0;



[preamble_data] = read_csv_file(fullfile(data_dir,preamble_filename));

filename=fullfile(data_dir,waveform_filename);

if (~exist('M_full'))
M_full=csvread(filename);
end

%% the first element has zero (bug in acquistion script i think)
M=M_full(:,2:m);


[n,m]=size(M);

%idx=index(y_k);
y_k=M(1,:);
t=0:(length(y_k)-1);

t=t*preamble_data.xincrement+preamble_data.xorigin;

y_min_min=min(min(M));
y_max_max=max(max(M));


RISETIMES=[];

for k=1:n

y_k=M(k,:);

[y_min,i_min]=min(y_k);
[y_max,i_max]=max(y_k);

t1=t(i_min);
t2=t(i_max);


dy_fs=y_max-y_min;

y1=y_min+0.10*dy_fs;
y2=y_min+0.90*dy_fs;

x=t;
y=y_k;
yo=y1;

[x1_prime,y1_prime,io]=get_closest_y_value(x,y,y1);
[x2_prime,y2_prime,io]=get_closest_y_value(x,y,y2);

risetime=x2_prime-x1_prime;

RISETIMES=[RISETIMES; risetime];

figure(1)
title(escape_underscores(filename));
plot(t,y_k);
yrange([y_min_min,y_max_max]);

vline(x1_prime,'-','r');
vline(x2_prime,'-','r');

hline(y1,'-','k');
hline(y2,'-','k');


title_str=sprintf('%s trace %d',basename,k);

title(escape_underscores(title_str));

drawnow;

if (mod(k,100) ==0)
  print('-depsc',sprintf('%s_trace_%04d.png',basename,k));
end

end



figure(2);

n_bins=256;

[x,n]=hist(RISETIMES,n_bins);
bar(n,x);
xlabel('90%-10% risetime [s]');
ylabel('N events');

title_str=sprintf('Risetime Distributions for %s',basename);

title(escape_underscores(title_str));

print('-depsc',sprintf('risetime_histo_%s.eps',basename));
print('-dpng',sprintf('risetime_histo_%s.png',basename));
%figure(i);
%plot(M')


