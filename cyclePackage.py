from asyncio.subprocess import PIPE
from re import sub
import readline
import subprocess
import sys


# This a first iteration of varypy as in it is just to cycle a package from a passed argument
# it must be use in an virtual env because it uses pip for installing the diffent version of the package
# in this version in particular mostly for testing, the for loop is specificaly used in a range because otherwise
# the loop goes on for a long time.
# One of the main challenge will probably be to allow the use of pipenv since it's support for python version < 3.6 has been dropped.
# For now the script works fine if use correctly (no error handling for now), it captures output and error from pip and the script passed in argument as well.



if __name__ == '__main__':

        #usage must be python3 cyclePackage prog pkg

        pkg = sys.argv[2]
        prog = sys.argv[1]
      
        content_list = subprocess.check_output(["pip-versions", "list", pkg]).decode().splitlines()
        logs = []

        for i in range(50,54):
            print("Testing for : " + pkg +"-"+ content_list[i])
            process = subprocess.Popen(["pip", "install", pkg+'=='+ content_list[i]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            out_p, err_p = process.communicate()
            execProg = subprocess.Popen(["python3",prog], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            execProg.wait()
            out , err = execProg.communicate()
            log = ((content_list[i],out_p,err_p,str(process.returncode)),(content_list[i],out,err,str(execProg.returncode)))
            logs.append(log)

        for l in logs:
            print("----------------------------------")
            print("Starting LOGS for : ")
            print(prog+" @Version --> "+l[0][0])
            print("----------------------------------")
            print("Logging of Pip output for return code --> " + l[0][3] +" : " + l[0][1].decode())
            print("Logging of Pip err for return code --> " + l[0][3] + " : " + l[0][2].decode())
            print("-----------------------------")
            print("Logging output of " + pkg  + " for return code --> " + l[1][3] + l[1][1].decode())
            print("Logging error of " +pkg  + " for return code --> " + l[1][3] + l[1][2].decode())

        
