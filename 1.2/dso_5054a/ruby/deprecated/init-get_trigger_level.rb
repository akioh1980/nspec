#!/usr/bin/ruby


require "lxi_device.rb"


server_name="xcalscope1.gsfc.nasa.gov"
server_port=5025


server_description=sprintf("%s:%d",server_name,server_port)
printf("\n Attempting to open connection to %s:%d ...",server_name,server_port)



begin
   dev = Lxi_device::open(server_name,server_port)
rescue
   printf(" failed!")
   printf("\n Exiting \n\n\n")
   exit
end



cmd="TRIGGER:LEVEL?"
response=dev.send_command(cmd)

response2=dev.read_response


print("\n cmd=#{cmd}")
print("\n response=#{response}")
print("\n response2=#{response2}")
