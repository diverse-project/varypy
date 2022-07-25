import argparse
from asyncio.subprocess import PIPE
import getopt
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
# Continuing the lousy description, now use a fix python version for testing and dev, mainly testing on the simple decision tree algo. With 2 data set that are cut
# for ease of exec. Still the same thing, cyclying package to test if the dependencies change the result of the program. Only cyclying one dependencie at a time.



if __name__ == '__main__':

        #usage must be python3 cyclePackage prog pkg [option]?

        pkg = ""
        prog = ""
        parser = argparse.ArgumentParser()

        parser.add_argument("prog", help="program to be used for cyclying dependecies")
        parser.add_argument("--pkg",help="package to be cycled",required=True)
        parser.add_argument("--display", help="simple version of logs for -S")
        parser.add_argument("--ntimes",help="number of execution of prog for pkg version")
        args = parser.parse_args()
        prog = args.prog
        pkg = args.pkg
        ntimes = args.ntimes
        option = args.display

        #List of pkg version
        content_list = subprocess.check_output(["pip-versions", "list", pkg]).decode().splitlines()
        #List of log for each versions of pkg
        logs = []
        #List of each iteration of output for N times
        cLogs = []
        ran = len(content_list)

        
        for i in range(60,61):
            print("Testing for : " + pkg +"-"+ content_list[i] + " "+ntimes+" times")
            #Install pkg from argv
            process = subprocess.Popen(["pipenv", "install", pkg+"=="+content_list[i]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try: 
                out_p, err_p = process.communicate(timeout=int(ntimes)*100)

                for k in range(0,int(ntimes)):
                    
                        #exec prog from argv
                        execProg = subprocess.Popen(["python3",prog], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                        try:
                            out , err = execProg.communicate(timeout=100)
                            #copy result from arg prog to a var 
                            catout = subprocess.Popen(["cat","submission.csv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            try :
                                cout , cerr = catout.communicate(timeout=100)
                                try :
                                    #create a submission file specific to the result of the current pkg 
                                    catmkf = subprocess.Popen(["cat","submission.csv"],stdout=open(str(k)+pkg+content_list[i]+"submission.csv","w"),stderr=subprocess.PIPE)
                                    cmkf , cerrmkf = catmkf.communicate(timeout=20)
                                except : 
                                    catmkf.kill()
                                    cmkf, cerrmkf = catmkf.communicate()

                            except subprocess.TimeoutExpired:
                                catout.kill()
                                cout , cerr = catout.communicate()

                        except subprocess.TimeoutExpired:
                            execProg.kill()
                            out , err = execProg.communicate()
                        #create tuple from acquired data and add to a list
                        cLogs.append(cout)
                log = ((content_list[i],out_p,err_p,str(process.returncode)),(content_list[i],out,err,str(execProg.returncode)),cLogs)
                logs.append(log)

            except subprocess.TimeoutExpired:
                process.kill()
                out_p, err_p = process.communicate()

        if option =="S":
            for l in logs:
                print("----------------------------------")
                print("Starting LOGS for : ")
                print(prog+" @Version --> "+l[0][0])
                resCode_p = l[0][3]
                resCode = l[1][3]
                response =""
                atWhere =""
                if resCode_p=="0":
                    response = "PASS"
                    atWhere = "installation"
                    if resCode=="0":
                        response = "PASS"
                        atWhere = "execution"
                    else:
                        response = "FAIL returnCode : " + resCode
                        atWhere = "execution"
                else:
                    response = "FAIL returnCode : " + resCode_p
                    atWhere = "installation"
                
                print("@" + atWhere + " --> " + response)
                #print("Logging of results from " + prog)
                #print(l[2].decode())
                
        else:
            for l in logs:
                print("----------------------------------")
                print("Starting LOGS for : ")
                print(prog+" @Version --> "+l[0][0])
                print("----------------------------------")
                print("Logging of Pip output for return code --> " + l[0][3] +" : " + l[0][1].decode())
                print("Logging of Pip err for return code --> " + l[0][3] + " : " + l[0][2].decode())
                print("-----------------------------")
                print("Logging output for " + pkg  + " @ return code --> " + l[1][3] + l[1][1].decode())
                print("Logging error for " +pkg  + " @ return code --> " + l[1][3] + l[1][2].decode())
                print("Logging of results from " + prog)
                for e in l[2]:
                    print(e.decode())
                

        
