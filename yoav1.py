"""
x = 5
y = "moshe"
z = 5.5
k = True


sum_price = 0
sum_price = sum_price + 10 # sum_price += 10
sum_price = sum_price + 40

x2 = x*x
x3 = x**2

#y2 = y**2
print (y*3)

print (5*3)
print("5"*3)

"""

"""
#string [from:to-1:step=1]

name = "avichai chen"
print (name[-4:])
print (name[:7])

print (name[:])
print (name[::2])
print (name[::3])
print (name[::-1])

print("\n")
"""

"""
name = "Avichai Chen"
print (name.lower())
print (name.upper())
print(len(name))
print(len(name[:7]))


print (name[:7]+name[-4:])
print (name[-4:]+name[:7])
"""

"""
name = input ("enter your name: ")
print ("Good morning",name,"!")
"""
"""
userInput = input("Please enter number with 3 digits: ")
digit1 = int(userInput[0])
digit2 = int(userInput[1])
digit3 = int(userInput[2])
sum_digit = digit1 + digit2 + digit3
print (sum_digit/3)
print (int(sum_digit/3))

u = input("Please enter number with 3 digits: ")
print ((int(u[0])+int(u[1])+int(u[2]))/3)
"""

"""
userInput = int(input("Please enter number with 3 digits: "))
digit1 = userInput%10
digit2 = (userInput//10)%10
digit3 = userInput//100
print ((digit1+digit2+digit3)/3)
print (int((digit1+digit2+digit3)/3))
"""


x = 5
"""
if x>10:
    print ("The number above 10")
"""

"""
if x>10:
    print ("The number above 10")
else:
    print ("The number below 10")
"""   

"""
x = 6

if x>10:
    print ("The number above 10")
elif x==10:
    print ("The number is 10")
else:
    print ("The number below 10")
""" 

"""
x = 11

if x>3 and x<10:
    print ("3<x<10")
else:
    print ("x<3 or x>10")
"""  

"""
x = 1
if x>3 and x<10:
    print ("3<x<10")
elif x>=10:
    print("x>=10")
else:
    print ("x<=3")
""" 

"""
x = 5
if x<3 or x>10:
    print ("x<3 or x>10")
"""

x = 5
if not x<3:
    print ("x>=3")







