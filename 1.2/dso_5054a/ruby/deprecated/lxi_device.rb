require "socket"
require "timeout"



class Lxi_device < TCPSocket
   #  attr_accessor :timeout_seconds

   #   def initialize()
   #     @timeout_seconds   = 0.1
   #   end

   public :gets



   def send_ascii_line(line)
      line.chomp
      #puts writes each of its arguments, adding a newline after each
      self.puts(line)
   end




   def read_response()
      #v=0.1
      timeout_seconds=0.1
      result=String.new

      begin
         timeout(timeout_seconds){
            while (true) do
               result=result + self.getc.chr
            end
         }
      rescue TimeoutError => my_err
         #we do nothing, just trap the err

         ##if you are going to print, this class has a print,puts
         ## and printf method, so be careful!
         #STDOUT.print "\n_____Timeout_________(" + my_err.to_s + ")\n"
      end

      return result
   end



   def send_command(line)
      send_ascii_line(line)
      return read_response

   end


   #    def get_possible_commands()
   #       response=send_command("help")

   #       lines=response.split("\n")

   #       ### we ignore the first three lines and the last one

   #       possible_commands=lines[3..lines.size-2]

   #       return possible_commands
   #    end

   def reconnect(server_name,server_port)



   end




end
