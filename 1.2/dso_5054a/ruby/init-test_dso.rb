#!/usr/bin/ruby


require "dso_5054a.rb"


server_name="xcalscope1.gsfc.nasa.gov"



dev=Dso_5054a.new
dev.configure(server_name)
dev.open





cmd="TRIGGER:LEVEL?"
dev.send_command(cmd)

response=dev.read_response.to_f


print("\n cmd=#{cmd}")
print("\n response=#{response}")
