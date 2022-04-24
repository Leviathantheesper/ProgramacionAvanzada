"""
Advanced Programming Course

Feliú Sagols
April 5th, 2022
CDMX
"""

def exceptions():
    a = int(input("Type an integer number please >>> "))
    try:
        print("The inverse is %f" % (1/a))
    except ZeroDivisionError as e:
        print("No puedes poner cero")
        raise NotImplementedError("No se qué hacer")


exceptions()

while True:
    program = input("Enter a python expression >>> ")
    result = eval(program)
    print(result)
