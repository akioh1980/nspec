#!/usr/bin/ruby


require_relative "dso_5054a.rb"
require_relative "misc_utils.rb"
require_relative "hash_utils.rb"

#server_name="xcalscope1.gsfc.nasa.gov"
#server_name="xcalscope1.gsfc.nasa.gov"
#server_name="192.168.2.84"
server_name=ARGV[0]

def write_preamble_file(preamble)





end


def add_counter_array_to_data(counter,data)

   # make counter array the same size as the first data array
   n_elements=data[data.keys.first].size

   counter_array=Array.new(n_elements)
   counter_array.fill(counter)

   data["counter"]=counter_array


   return data

end


dev=Dso_5054a.new
dev.configure(server_name)
dev.open


dev.set_waveform_ascii_mode


############ preamble stuff
preamble=dev.get_preamble
#preamble.pretty_print
write_preamble_file(preamble)




timestamp=generate_timestamp

basename=timestamp

preamble_filename=basename+".preamble"
preamble_file=File.new(preamble_filename,"w+")
preamble.write_to_file(preamble_file)
preamble_file.close

STDOUT.print("\n Preamble file written to #{preamble_filename}")


waveform_filename=basename+".dat"
waveform_file=File.new(waveform_filename,"w+")


min_max_filename=basename+".min_max"
min_max_file=File.new(min_max_filename,"w+")




n_waveforms=5


counter=0

while(counter < n_waveforms)


   ###get the pure waveform
   data=dev.get_trace


   data=add_counter_array_to_data(counter,data)


   n_points=data[data.keys.first].size
   n_keys=data.keys.size

   STDOUT.print("\n read #{n_keys}x#{n_points} samples")
   STDOUT.print("\n Waveform data written to #{waveform_filename}")

   print_data_hash_to_file_without_header(waveform_file,data,seperator="  ")


   ##calculate min and max

   y=data["y_v"]
   t=data["t_s"]


   min_max_file.printf("%01.6g %01.6g %01.6g\n",y.min, y.max,y.max-y.min);

   counter +=1
end


min_max_file.close



STDOUT.printf("\n data contents")
data.keys.each do |key|

   STDOUT.printf("\n %s.min=%01.3g", key, data[key].min)
   STDOUT.printf("\t %s.max=%01.3g", key, data[key].max)

   STDOUT.printf("\t %s.(max-min)=%1.3g", key, data[key].max-data[key].min)
end


STDOUT.printf("\n\n")

#close open files

waveform_file.close
