#!/usr/bin/ruby


require "dso_5054a.rb"


server_name="xcalscope1.gsfc.nasa.gov"



dev=Dso_5054a.new
dev.configure(server_name)
dev.open


cmd="WAVEFORM:POINTS MAX"
dev.send_command(cmd)



cmd="WAVEFORM:FORMAT ASCII"
dev.send_command(cmd)




#cmd="WAVEFORM:PREAMBLE?"
#dev.send_command(cmd)


cmd="WAVEFORM:DATA?"
dev.send_command(cmd)

response=dev.read_response
print("\n cmd=#{cmd}")
print("\n response=#{response}")



preamble=dev.get_preamble


preamble.keys.each do |key|
   print("\n #{key}=#{preamble[key]}")
end
