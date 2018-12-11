#!/usr/bin/ruby


unless Kernel.respond_to?(:require_relative)
  module Kernel
    def require_relative(path)
      require File.join(File.dirname(caller[0]), path.to_str)
    end
  end
end

require_relative "dso_5054a.rb"
require_relative "misc_utils.rb"
require_relative "hash_utils.rb"

#server_name="xcalscope1"
#server_name="192.168.2.80"
#server_name="192.168.2.84"
#server_name="169.254.38.1"
server_name=ARGV[0]

def write_preamble_file(preamble)





end


dev=Dso_5054a.new
dev.configure(server_name)
dev.open


dev.set_waveform_ascii_mode


############ preamble stuff
#preamble=dev.get_preamble
#preamble.pretty_print
#write_preamble_file(preamble)




timestamp=generate_timestamp

#preamble_filename="./data/"+ARGV[2]+"/"+ARGV[1]+"/"+timestamp+".preamble"
#preamble_file=File.new(preamble_filename,"w+")
#preamble.write_to_file(preamble_file)
#preamble_file.close

#STDOUT.print("\n Preamble file written to #{preamble_filename}")


waveform_filename="./data/"+ARGV[2]+"/"+ARGV[1]+"/"+timestamp+".dat"
waveform_file=File.new(waveform_filename,"w+")

###get the pure waveform
data=dev.get_trace

n_points=data[data.keys.first].size
n_keys=data.keys.size

STDOUT.print("\n read #{n_keys}x#{n_points} samples")
STDOUT.print("\n Waveform data written to #{waveform_filename}")

print_data_hash_to_file(waveform_file,data,seperator="  ")


STDOUT.printf("\n data contents")
data.keys.each do |key|

   STDOUT.printf("\n %s.min=%01.3g", key, data[key].min)
   STDOUT.printf("\t %s.max=%01.3g", key, data[key].max)

   STDOUT.printf("\t %s.(max-min)=%1.3g", key, data[key].max-data[key].min)
end


STDOUT.printf("\n\n")

#close open files

waveform_file.close
