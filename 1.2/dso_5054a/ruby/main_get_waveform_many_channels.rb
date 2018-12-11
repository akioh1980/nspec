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

#server_name="xcalscope1.gsfc.nasa.gov"
server_name="192.168.2.80"



dev=Dso_5054a.new
dev.configure(server_name)
dev.open


active_channels=dev.get_list_of_all_displayed_channels

dev.set_waveform_ascii_mode

basename=generate_timestamp

preamble_filename=basename+".preamble"
preamble_file=File.new(preamble_filename,"w+")

###############################################
##
##  preamble 
##
###############################################


#### this is an array of hashes 
preambles=dev.get_all_displayed_preambles


first_preamble_line=true
preambles.keys.sort.each do |key|

  preamble=preambles[key]
  if (first_preamble_line)
    
    preamble.keys.sort.each do |key|
      preamble_file.print("\n #{key},")
    end
    
    first_preamble_line=false
  end

  preamble.keys.sort.each do |key|
    preamble_file.print("#{preamble[key]},")
  end

end



#preamble.write_to_file(preamble_file)
preamble_file.close

STDOUT.print("\n Preamble file written to #{preamble_filename}\n")


###############################################
##
##   waveform
##
###############################################


waveform_filename=basename+".dso"
waveform_file=File.new(waveform_filename,"w+")



#dev.set_acquire_mode_average(n_avg=16)




###get the pure waveform
#data=dev.get_trace

#


STDOUT.print(" Active channels=#{active_channels.join(',')}\n")
STDOUT.flush

data=dev.get_traces(active_channels)
n_points=data[data.keys.first].size
n_keys=data.keys.size

#STDOUT.print("\n")
STDOUT.print(" Read #{n_keys-1}x#{n_points} samples\n")

STDOUT.print(" Waveform data written to #{waveform_filename}\n")

print_data_hash_to_file(waveform_file,data,seperator="  ")
#close open files

waveform_file.close

#######################################
##
##  the comment file
##
#######################################


#### any strings on the command line are added to 
comment_file_name=basename + ".comment"
comment_file=File::open(comment_file_name,"w")


  comment_field=ARGV.join(" ")

  comment_file.printf("%s",waveform_filename)
  comment_file.print(" | ")
  comment_file.printf("%s",comment_field)
  comment_file.printf("\n")

STDOUT.print("Comment data written to #{comment_file_name}")
STDOUT.print("\n")


#######################################3
####
#### print some statistics to the screen
####
####

STDOUT.printf("\n data contents")
data.keys.each do |key|

   STDOUT.printf("\n %s.min=%01.3g", key, data[key].min)
   STDOUT.printf("\t %s.max=%01.3g", key, data[key].max)

   STDOUT.printf("\t %s.(max-min)=%1.3g", key, data[key].max-data[key].min)
end


STDOUT.printf("\n\n")
