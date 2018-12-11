#!/usr/bin/ruby


unless Kernel.respond_to?(:require_relative)
  module Kernel
    def require_relative(path)
      require File.join(File.dirname(caller[0]), path.to_str)
    end
  end
end

require_relative "lxi_device"
#require_relative "linspace"

def Array

   def to_f
      self.each_index do |i|

         self[i]=self[i].to_f
      end

   end
end

def array_of_strings_to_floats(a)

   y=Array.new

   a.each do |a_i|

      y.push(a_i.to_f)
   end

   return y
end

class Dso_5054a < Lxi_device


  def get_channel_state(ch)
    
    self.send_command("CHANNEL" + ch.to_i.to_s + "?")
    s=self.read_response

    tokens=s.split(";")
    
    data=Hash.new

    tokens.each do |token|
      (key,value)=(token.split)
      key.gsub!(":","_")
      data[key]=value      
    end

    return data
  end

 ### returns a hash 
   def get_all_displayed_preambles

     displayed_channels=self.get_list_of_all_displayed_channels

     data=Hash.new
     displayed_channels.each do |channel|
       set_waveform_source(channel)
       preamble_n=get_preamble

       data[channel]=preamble_n
     end


     return data
   end

   ### returns a hash 
   def get_preamble
     

     current_channel=self.get_waveform_source
     
     if (self.get_channel_displayed(current_channel)==0)
       STDOUT.printf("Warning: Trying to get preamble for channel #{current_channel} which is off")
       STDOUT.printf("Returning empty hash")
       STDOUT.flush
       return Hash.new       
     end

#     set_waveform_source(ch)

     
      cmd="WAVEFORM:PREAMBLE?"
      self.send_command(cmd)

      response=self.read_response


      params=response.split(",")

      result=Hash.new

      index=0

      result["ch"]=current_channel;
      result["format"]=params[index].to_i; index=index+1;
      result["type"]=params[index].to_i; index=index+1;
      result["points"]=params[index].to_i; index=index+1;
      result["count"]=params[index].to_i; index=index+1;
      result["xincrement"]=params[index].to_f; index=index+1;
      result["xorigin"]=params[index].to_f; index=index+1;
      result["xreference"]=params[index].to_i; index=index+1;
      result["yincrement"]=params[index].to_f; index=index+1;
      result["yorigin"]=params[index].to_f; index=index+1;
      result["yreference"]=params[index].to_i; index=index+1;

      ### xreference is always zero for this scope

      return result
   end

   def set_waveform_ascii_mode

      cmd="WAVEFORM:POINTS MAX"
      send_command(cmd)



      cmd="WAVEFORM:FORMAT ASCII"
      send_command(cmd)
   end

   def set_waveform_source(ch=1)

      cmd="WAVEFORM:SOURCE CHAN" + ch.to_s
      send_command(cmd)
   end

   def get_waveform_source

      cmd="WAVEFORM:SOURCE? "
      send_command(cmd)

      return self.read_response.sub("CHAN","").to_i



   end

  

   def get_waveform_data
      cmd="WAVEFORM:DATA?"
      self.send_command(cmd)

      data_string=self.read_response


      ##the first token is a 'header' and a sample
      ## eg "#800012999 2.10000e-02"
      ##
      ## the heade is a #8 and then a size

      data=data_string.split(",")

      # ' Where:
      # '    <header> = #800001000 (This is an example header)
      # ' The "#8" may be stripped off of the header and the remaining
      # ' numbers are the size, in bytes, of the waveform data block. The
      # ' size can vary depending on the number of points acquired for the
      # ' waveform. You can then read that number of bytes from the
      # ' oscilloscope and the terminating NL character.
      # '


      # In ASCii format, holes are represented by the value 9.9e+37.


      (header,data_0)=data[0].split(" ")

      data[0]=data_0

      data_string=data.join(",")

      return data_string
   end


   def get_trace
      waveform_string=self.get_waveform_data

      y_data_s=waveform_string.split(",")

      y_data=array_of_strings_to_floats(y_data_s)

      data=Hash.new
      data["y_v"]=y_data
      data["t_s"]=synthesize_time_data


      return data

   end

    def get_all_displayed_traces

     channel_list=get_list_of_all_displayed_channels
      return get_traces(channel_list)
    end

  def get_traces(channel_list=[1,2,3,4])
    
    data=Hash.new
    data["t_s"]=synthesize_time_data

    channel_list.each do |ch|
      self.set_waveform_source(ch)
      waveform_string=self.get_waveform_data
      y_data_s=waveform_string.split(",")
      y_data=array_of_strings_to_floats(y_data_s)

    
      key="y"+ch.to_s+"_v"

      data[key]=y_data


    end
    
      return data

   end

   def synthesize_time_data

      p=self.get_preamble

      n=p["points"]

      t=Array.new

      (0...n).each do |i|

         #        t[i] = ( (i * p["xincrement"]) + p["xorigin"]
         t[i] = ( (i - p["xreference"]) * p["xincrement"]) + p["xorigin"]
      end

      return t
   end

   def set_acquire_mode_average(n_avg=8)

      #      cmd="ACQUIRE:TYPE Normal
      cmd="ACQUIRE:TYPE Average"
      send_command(cmd)

      cmd="ACQUIRE:Count " + n_avg.to_s
      send_command(cmd)
   end

   def set_acquire_mode_normal

      cmd="ACQUIRE:TYPE Normal"
      #      cmd="ACQUIRE:TYPE Average"
      send_command(cmd)
   end

   def get_aquire_mode

      cmd="ACQUIRE:TYPE?"
      send_command(cmd)

      return read_response
   end

 def get_risetime
      cmd="MEASURE:RISETIME?"
      self.send_command(cmd)

      return self.read_response.to_f

   end

   def digitize
      cmd="DIGITIZE"
      self.send_command(cmd)

      return nil

   end

    def get_channel_displayed(ch)

      cmd="CHANNEL" + ch.to_i.to_s + ":DISPLAY?"
      send_command(cmd)
      return read_response.to_i
   end

   def get_list_of_all_displayed_channels
     
     active_channels=Array.new
     
     (1..4).each do |i| 

       if (get_channel_displayed(i)==1)
         active_channels.push(i)
       end
     end

      return active_channels
   end

end
