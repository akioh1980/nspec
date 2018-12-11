filename='../ruby/2009_0402_1243_48.waveform';
filename='../ruby/2011_0218_1656_48.waveform';

%2011_0218_1653_41.waveform
%2011_0218_1656_48.waveform
%2011_0218_1713_55.waveform
filename='../ruby/22011_0218_1813_12.waveform';

base_dir='../ruby';

files=file_select([],base_dir,'*.waveform',0,1);

for i=1:length(files)

  filename=files{i};
  
M=csvread(filename);



y1=M(1,:);


figure(i);
plot(M')
title(escape_underscores(filename));

[pathstr,basename,ext,versn] = fileparts(filename);



print('-depsc',sprintf('%s.eps',basename));
print('-dpng',sprintf('%s.png',basename));

end
