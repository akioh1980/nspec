filename='../ruby/2009_0401_1700_57.risetime';


filename='../ruby/2009_0402_1243_48.risetime';


n=1;
[S] = readfilen(filename,n);



%% cut huge values
keep=(S < 1e30);
S=S(keep);


%keep samples over 1229
%idx=index(S);
%keep=(idx>1229);
%S=S(keep);

idx=index(S);


figure(1);
hist(S,50)
xlabel('Risetime [s]')
ylabel('Count')

figure(gcf+1)
plot(idx,S);
xlabel('Risetime [s]')
ylabel('Count')
