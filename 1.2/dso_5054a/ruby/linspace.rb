
#### generates a linear spaced array
def linspace(x1,x2,n)

   span=x2-x1

   dx=span.to_f/(n-1).to_f

   a=Array.new(n)

   (0...a.size).each do |i|

      a[i]=x1+i*dx

   end


   return a
end
