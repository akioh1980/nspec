#!/usr/bin/ruby -w


##loop through each file on the command line
ARGV.each do |filename|


   outfilename=filename + ".no_comma"
   of=File.new(outfilename,"w")
   print("\n", filename, "\t--->\t", outfilename)

   ## process each file line by line
   File.new(filename,"r").each do |line|
      line2=line.gsub(","," ")
      of.print line2
   end

   of.close

end
