#!/usr/bin/ruby -w

require "matrix"




def read_csv_matrix_as_array_of_arrays(filename)
   data=Array.new

   ## process each file line by line
   f_in=File.new(filename,"r")

   f_in.each do |line|
      x=line.chomp.split(",")

      ## delete any elements whose size==0
      x.delete_if { |element_i| (element_i.size==0) }

      data.push(x)
   end
   f_in.close

   return data

end


def write_array_of_arrays(data,filename)


   ## process each file line by line
   f_out=File.new(filename,"w")
   sep=" "

   data.each do |row|

      line=row.join(sep)
      f_out.print(line)
      f_out.print("\n")
   end
   f_out.close
end

def transpose_array_of_arrays(data)
   m=Matrix.rows(data)
   m_t=m.transpose
   data_t=m_t.to_a
   return data_t
end

############################################
#
#  end of functions
#
#############################################

if (ARGV.size <1 )
   print "\n This script needs some files to work with"
   print "\n Usage: ruby #{$0} *.waveform"

end

##loop through each file on the command line
ARGV.each do |inp_filename|


   out_filename=inp_filename + ".transpose"

   print("\n", inp_filename, "\t--->\t", out_filename)



   data=read_csv_matrix_as_array_of_arrays(inp_filename)

   data_transpose=transpose_array_of_arrays(data)

   write_array_of_arrays(data_transpose,out_filename)

end
