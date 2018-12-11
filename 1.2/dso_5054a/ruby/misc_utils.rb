def generate_timestamp
   tm=Time.now

   logfile_name= String.new
   logfile_name= logfile_name + sprintf("%04d_%02d%02d_", tm.year , tm.month, tm.day)

   logfile_name= logfile_name + sprintf("%02d%02d_%02d", tm.hour, tm.min, tm.sec)

   # logfile_name= logfile_name + sprintf("%02d%02d", tm.hour, tm.min)

   return logfile_name
end

#### data_set shoulde be a vector of different sets
#
# data_set=Array.new
# data_set.push(data_phase)
# data_set.push(data_mag)
#
# cdata=merge_data_sets(data_set)

def merge_data_sets(data_set)

   cdata=Hash.new



   data_set.each do |data_i|

      data_i.keys.each do |key|

         my_value=data_i[key]

         cdata[key]=my_value
      end




   end

   return cdata
end


def combine_data_hash(data1,data2)

   if (data1.size == 0)
      return data2
   end

   if (data2.size == 0)
      return data1
   end


   data1.keys.each do |key|
      data1[key].concat(data2[key])
   end

   return data1

end


def print_xy_to_file(outfile,x,y,x_label,y_label,seperator=" ")

   outfile.print(x_label)
   outfile.print(seperator)
   outfile.print(y_label)
   outfile.print("\n")


   for i in 0...y.size
      outfile.print(x[i])
      outfile.print(seperator)
      outfile.print(y[i])
      outfile.print("\n")
   end

end

def print_xyz_to_file(outfile,x,y,z,x_label,y_label,z_label,seperator=" ")

   outfile.print(x_label)
   outfile.print(seperator)
   outfile.print(y_label)
   outfile.print(seperator)
   outfile.print(z_label)
   outfile.print("\n")


   for i in 0...y.size
      outfile.print(x[i])
      outfile.print(seperator)
      outfile.print(y[i])
      outfile.print(seperator)
      outfile.print(z[i])
      outfile.print("\n")
   end

end

#%%% labels=["A", "B", "C"]
#%%%
#%%% data=[A, B, C]
#%%%
#%%% A=[1, 2, 3]
#%%% B=[4, 5, 6]
#%%% C=[7, 8, 9]
#%%%
def print_data_pseudo_matrix_to_file(outfile,data,labels,seperator=" ")

   label_str="%" + labels.join(seperator)
   outfile.print(label_str)

   outfile.print("\n")



   for i in 0...data[0].size
      for j in 0...data.size
         outfile.print(data[j][i])
         if (j != data.size-1)
            outfile.print(seperator)
         end
      end

      outfile.print("\n")
   end

end

### the data hash is a hash of arrays
def print_data_hash_to_file(outfile,data,seperator=" ")

   label_str= data.keys.sort.join(seperator)
   outfile.print(label_str)



   outfile.print("\n")

   # my_keys=data.keys

   for i in 0...data[data.keys.sort.first].size
      data.keys.sort.each do |key|
         outfile.print(data[key][i])

         if (key != data.keys.sort.last)
            outfile.print(seperator)
         end
      end

      outfile.print("\n")
   end

end

def print_data_hash_to_file_without_header(outfile,data,seperator=" ")

   ## this would print the header
   # label_str= data.keys.sort.join(seperator)
   # outfile.print(label_str)



   #  outfile.print("\n")

   # my_keys=data.keys

   for i in 0...data[data.keys.sort.first].size
      data.keys.sort.each do |key|
         outfile.print(data[key][i])

         if (key != data.keys.sort.last)
            outfile.print(seperator)
         end
      end

      outfile.print("\n")
   end

end


def combine_data_hash_unit_test
   ###### test with Vector
   a=[1, 2, 3]
   b=[4, 5, 6]
   c=[7, 8, 9]

   data1=Hash.new

   data1["A"]=a
   data1["B"]=b
   data1["C"]=c

   aa=[4, 5, 6]
   bb=[7, 8, 9]
   cc=[10, 11, 12]

   data2=Hash.new
   data2["A"]=aa
   data2["B"]=bb
   data2["C"]=cc

   data3=combine_data_hash(data1,data2)


   ###test with GSL vector
   a=GSL::linspace(1,3,3)
   b=GSL::linspace(4,6,3)
   c=GSL::linspace(7,9,3)

   data1=Hash.new

   data1["A"]=a
   data1["B"]=b
   data1["C"]=c

   ###test with GSL vector
   aa=GSL::linspace(4,6,3)
   bb=GSL::linspace(7,9,3)
   cc=GSL::linspace(10,12,3)

   data2=Hash.new
   data2["A"]=aa
   data2["B"]=bb
   data2["C"]=cc

   data4=combine_data_hash(data1,data2)

end
