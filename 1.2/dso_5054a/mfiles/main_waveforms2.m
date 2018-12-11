
load('pulses.mat')
filename='../ruby/2009_0402_1243_48.risetime';


n=1;
[S] = readfilen(filename,n);


idx=index(S);
%% cut huge values
keep=(S < 1e30);


keep =keep & (idx>1500);


[n,L]=size(M);


wf=M(1,:);
wf_avg=zeros(size(wf));
acc=0;

for k=1:n
  
  
  
 wf=M(k,:);
 
 
 
 
% drawnow;
 

 rt_i=S(k);
 
 if ((rt_i > 1e-7) & (rt_i < 1.2e-7) & ( k > 1500))
 
   wf_avg=wf_avg+wf;
   acc=acc+1;

   plot(wf,'b');
 else
   
   plot(wf,'r');
 end
 
 drawnow;
 
end

 
 figure(gcf+1);
 
 
 wf_avg_final=wf_avg/acc;
plot(wf_avg_final);

filename='wave_form_avg.txt';

write_file(filename,wf_avg_final);
