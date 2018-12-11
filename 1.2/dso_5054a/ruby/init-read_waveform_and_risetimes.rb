#!/usr/bin/ruby


require "dso_5054a.rb"
require "misc_utils.rb"
require "hash_utils.rb"

server_name="xcalscope1.gsfc.nasa.gov"

def write_preamble_file(preamble)





end


dev=Dso_5054a.new
dev.configure(server_name)
dev.open


dev.set_waveform_ascii_mode


############ preamble stuff
preamble=dev.get_preamble
preamble.pretty_print
write_preamble_file(preamble)




timestamp=generate_timestamp

preamble_filename=timestamp+".preamble"
preamble_file=File.new(preamble_filename,"w+")
preamble.write_to_file(preamble_file)
preamble_file.close

STDOUT.print("\n Preamble file written to #{preamble_filename}")


waveform_filename=timestamp+".waveform"
waveform_file=File.new(waveform_filename,"w+")

STDOUT.print("\n Waveform file written to #{waveform_filename}")


risetime_filename=timestamp+".risetime"
risetime_file=File.new(risetime_filename,"w+")

STDOUT.print("\n Risetime file written to #{risetime_filename}")




n_trials=10

done=false
count=0
while(!done)


   ##start the digitizer
   #data_string=dev.digitize

   ##get the scope's calculated risetime
   risetime=dev.get_risetime
   risetime_file.print("#{risetime}\n")


   ###get the pure waveform
   waveform_string=dev.get_waveform_data
   n_points=waveform_string.split(",").size
   waveform_file.print("#{waveform_string}\n")



   STDOUT.print("\n #{count}) read #{n_points} samples")
   STDOUT.printf("\trisetime=%1.2g s",risetime)



   ### bookkeeping
   count=count+1

   if (count > n_trials)
      done=true
   end

end


#close open files

waveform_file.close
risetime_file.close
