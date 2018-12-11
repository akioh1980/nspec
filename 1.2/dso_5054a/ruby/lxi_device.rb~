#!/usr/bin/ruby

require "socket"




class Lxi_device


   attr_accessor :hostname
   attr_accessor :port
   attr_accessor :my_sock
   attr_accessor :timeout_seconds
   attr_accessor :verbosity


   def initialize()
      #super()


      @timeout_seconds=0.1
      @verbosity=5
   end


   def configure(hostname,port=5025)


      @hostname=hostname
      @port=port



   end



   def open

      STDOUT.printf("\n Attempting to open connection to %s:%d ...",@hostname,@port)
      begin
         #   dev = Lxi_device::open(hostname,server_port)
         @my_sock = TCPSocket::open(@hostname,@port)
      rescue
         printf(" failed!")
         printf("\n Exiting \n\n\n")
         exit
      end

   end


   def close

      @my_sock.close

   end

   def send_command(cmd)

      if (@verbosity>5)
         STDOUT.printf("\n sending cmd=<#{cmd}>")

      end


      cmd.chomp
      #puts writes each of its arguments, adding a newline after each
      @my_sock.puts(cmd)

      return nil
   end


   def read_response_until_timeout()
      #v=0.1
      #timeout_seconds=0.1
      result=String.new

      begin
         timeout(timeout_seconds){
            while (true) do
               result=result + @my_sock.getc.chr
            end
         }
      rescue TimeoutError => my_err
         #we do nothing, just trap the err

         ##if you are going to print, this class has a print,puts
         ## and printf method, so be careful!
         if (@verbosity>3)

            STDOUT.print "\n_____Timeout_________(" + my_err.to_s + ")\n"
         end
      end

      return result
   end

   def read_response()
      response=@my_sock.readline.chomp


      if (@verbosity>5)
         STDOUT.printf("\n response=<#{response}>")

      end

      return response
   end

end
