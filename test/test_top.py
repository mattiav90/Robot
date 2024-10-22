# python2_script.py
import subprocess
import sys



def function(arg):
    print("received angle: ",arg)
    subprocess.call(['python3.8', 'steer.py', arg])




if __name__ == "__main__":
    function(sys.argv[1])
