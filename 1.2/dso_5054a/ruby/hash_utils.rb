class Hash
   def write_to_file(file)



      ##this assumes values come out in the same order as keys

      file.print self.keys.join(",")
      file.print "\n"

      file.print self.values.join(",")
      file.print "\n"

      #preamble.keys.each do |key|
      #   preamble_file.print("\n #{key},")
      #end



   end



   def pretty_print
      self.keys.each do |key|
         print("\n #{key}=#{self[key]}")
      end



   end




end
