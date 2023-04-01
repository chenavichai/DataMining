# Q1

# if we not return anything - the function return None, so i use it to break the function
def my_func(x1,x2,x3):
    # if one of the parameters is int - print that it should be float + return None (default)
    if isinstance(x1, int) or isinstance(x2, int) or isinstance(x3, int):
        print ("Error: parameters should be float")
        return None
    # if all the parameters isn't float (str,list..) - so it's not good and return only None 
    elif not(isinstance(x1, float) and isinstance(x2, float) and isinstance(x3, float)):
        return None 
    
    # if we here in the program so all the numbers is float, we need calculate and return result
    numerator = (x1+x2+x3)*(x2+x3)*x3
    denominator = x1 + x2 + x3
    # if the denominator is zero - print that it is not a number and return None (default)
    if denominator == 0:
        print ("Not a number – denominator equals zero")
        return None 
    else:
        return float (numerator/denominator)

my_func(1.5,2.5,-4.0)



# Q2
def revword (word:str) -> str:
    # take the str, reverse it and make the letters lower
    return word[::-1].lower()

def countword() -> int:
    # read from the file and split the word into list
    f = open ("text.txt","r")
    lst_text = f.read().split()
    word = lst_text[0].lower()
    
    # run all the list except the first word and fix the direction
    for i in range (1,len(lst_text)): 
        lst_text[i] = revword(lst_text[i])
    
    # run all the list and count the number of the first word
    counter = 0
    for w in lst_text:
        if word == w:
            counter += 1
    return counter
    
print (countword())
