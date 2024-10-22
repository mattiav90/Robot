# script.py
import sys

def my_function(arg):
    print(f"Called with argument: {arg}")

if __name__ == "__main__":
    my_function(sys.argv[1])

