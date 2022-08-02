import argparse
from asyncio.subprocess import PIPE
import matplotlib.pyplot as plt
from re import sub
import readline
from socket import timeout
import subprocess
import sys
import time
import pandas as pd
import xml.etree.ElementTree as ET



# This a first iteration of varypy as in it is just to cycle a package from a passed argument
# it must be use in an virtual env because it uses pip for installing the diffent version of the package
# in this version in particular mostly for testing, the for loop is specificaly used in a range because otherwise
# the loop goes on for a long time.
# One of the main challenge will probably be to allow the use of pipenv since it's support for python version < 3.6 has been dropped.
# For now the script works fine if use correctly (no error handling for now), it captures output and error from pip and the script passed in argument as well.
# Continuing the lousy description, now use a fix python version for testing and dev, mainly testing on the simple decision tree algo. With 2 data set that are cut
# for ease of exec. Still the same thing, cyclying package to test if the dependencies change the result of the program. Only cyclying one dependencie at a time.




def installPkg(pkg,version):
    process = subprocess.Popen(["pipenv", "install", pkg+"=="+version], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        #timeout is set to ntimes just in case to have some room 
        out_p, err_p = process.communicate(timeout=30.0)

    except subprocess.TimeoutExpired:
        process.kill()
        out_p, err_p = process.communicate()

    processRCode = process.returncode
    return (version,out_p,err_p,processRCode)

def execProg(prog,version):
    execProg = subprocess.Popen(["python3",prog], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out , err = execProg.communicate(timeout=30.0)
    except subprocess.TimeoutExpired:
        execProg.kill()
        out , err = execProg.communicate()
    execProgRCode = execProg.returncode
    return (version,out,err,execProgRCode)

def averageCsv(names):
    res = []
    key =""
    for n in names:
        temp = pd.read_csv(n)
        key = temp.keys() #tab of keys
        res.append(temp)
    df = pd.concat(res)
    result=df.groupby(key[0], as_index=False).mean()
    return result

def getTests(dir,version):
    process = subprocess.Popen(["pytest", "-q",dir,"--junitxml=xmlTest.xml"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
    #timeout is set to ntimes just in case to have some room 
        out, err = process.communicate(timeout=30.0)

    except subprocess.TimeoutExpired:
        process.kill()
        out, err = process.communicate()

    tree = ET.parse('xmlTest.xml')
    root = tree.getroot()
    resMap = {}
    for attribute in root:
        resMap[attribute.tag] = attribute.attrib
        print(attribute.tag,attribute.attrib)
    return (version,resMap,err,process.returncode)




if __name__ == '__main__':

        #usage must be python3 cyclePackage prog pkg [option]?

        mainP = ""
        pkg = ""
        prog = ""
        parser = argparse.ArgumentParser()

        parser.add_argument("prog", help="PATH of program to be used for cyclying dependecies")
        parser.add_argument("--pkg",help="package to be cycled",required=True)
        parser.add_argument("--display", help="S for simple display")
        parser.add_argument("--ntimes",help="INT number of execution of prog for pkg version",default=1)
        parser.add_argument("--test",help="If prog is test file",action='store_true')
        parser.add_argument("--outputfile",help="ouputfile of prog if there is any",default="")
        args = parser.parse_args()
        prog = args.prog
        pkg = args.pkg
        ntimes = args.ntimes
        option = args.display
        outputfile = args.outputfile
        test = args.test

        print("What is going on in the mainP :"+mainP)
        #List of pkg version
        content_list = subprocess.check_output(["pip-versions", "list", pkg]).decode().splitlines()
        #List of log for each versions of pkg
        logs = []
        #List of each iteration of output for N times
        cLogs = []
        ran = len(content_list)
        Package = []
        Version = []
        Installation = []
        Execution= []
        ReturnCode=[]
        ExecutionTime=[]
        Iteration=[]
        csvLog=[]
        
        for i in range(25,26):
            print("Testing for : " + pkg +"-"+ content_list[i] + " "+str(ntimes)+" times")
            #Install pkg from argv
            installP = installPkg(pkg,content_list[i])
            execP = []
            for k in range(0,int(ntimes)):
                #exec prog from argv
                #get execution time
                #Check if return code of pipenv install is 0
                if installP[3] == 0:
                    t1 = time.time()
                    if test:
                        execP = getTests(prog,content_list[i])
                    else:
                        execP = execProg(prog,content_list[i])
                    t2 = time.time()
                    #Time ellapsed for execution time
                    timep = t2 - t1

                    #Not really part of final product
                    if execP[3] == 0 :
                        #copy result from arg prog to a var
                        #check if outputfile is passed as argument
                        if outputfile != "": 
                            catout = subprocess.Popen(["cat",outputfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            try :
                                cout , cerr = catout.communicate(timeout=20.0)
                                try :
                                    #create a submission file specific to the result of the current pkg 
                                    catmkf = subprocess.Popen(["cat",outputfile],stdout=open(str(k)+pkg+content_list[i]+outputfile,"w"),stderr=subprocess.PIPE)
                                    cmkf , cerrmkf = catmkf.communicate(timeout=20.0)
                                except : 
                                    catmkf.kill()
                                    cmkf, cerrmkf = catmkf.communicate()

                            except subprocess.TimeoutExpired:
                                catout.kill()
                                cout , cerr = catout.communicate()

                            csvLog.append(str(k)+pkg+content_list[i]+outputfile)
                        else:
                            cout=""
                    else :
                        timep=0
                #create tuple from acquired data and add to a list
                log = (installP,execP,k,timep,cout)
                logs.append(log)
                #add csv file to tab csvLog
                

        #Constructing dataframe from logs
        if option =="S":
            for l in logs:
                Package.append(pkg)
                Version.append(l[0][0])
                Iteration.append(l[2])
                ExecutionTime.append(l[3])
                resCode_p = str(l[0][3])
                
                response =""
                atWhere =""
                if resCode_p=="0":
                    resCode = str(l[1][3])
                    response = "PASS"
                    atWhere = "installation"
                    Installation.append(response)
                    if resCode=="0":
                        response = "PASS"
                        atWhere = "execution"
                        Execution.append(response)
                        ReturnCode.append(resCode)
                    else:
                        response = "FAIL"
                        atWhere = "execution"
                        Execution.append(response)
                        ReturnCode.append(resCode)
                else:
                    response = "FAIL"
                    atWhere = "installation"
                    Installation.append(response)
                    Execution.append("None")
                    ReturnCode.append(resCode_p)
                
                #print("@" + atWhere + " --> " + response)
                #print("Logging of results from " + prog)
                #print(l[2].decode())
                
                
        else:
            for l in logs:
                print("----------------------------------")
                print("Starting LOGS for : ")
                print(prog+" @Version --> "+l[0][0])
                print("----------------------------------")
                #weird behavior with print pip err be careful check later
                print("Logging of Pip output for return code --> " + l[0][3] +" : " + l[0][1].decode())
                print("Logging of Pip err for return code --> " + l[0][3] + " : " + l[0][2].decode())
                print("-----------------------------")
                print("Logging output for " + pkg  + " @ return code --> " + l[1][3] + l[1][1].decode())
                print("Logging error for " +pkg  + " @ return code --> " + l[1][3] + l[1][2].decode())
                print("Logging of results from " + prog)
                for e in range(len(l[2])):
                    print(str(e)+" th iteration of "+prog+" for "+pkg+" : ")
                    print(l[2][e].decode())
        print("----------------------------------")
        print("LOGS : ")
        print(len(Package))
        print(len(Version))
        print(len(Installation))
        print(len(Execution))
        print(len(ReturnCode))
        print(len(ExecutionTime))
        data = {'Package':Package,'Iteration':Iteration,'Version':Version,'Installation':Installation,'Execution':Execution,'ReturnCode':ReturnCode,'ExecutionTime(s)':ExecutionTime}
        df = pd.DataFrame(data)
        print(df)
        csvDf = averageCsv(csvLog)
        for frame in csvLog:
            df = pd.read_csv(frame)
            
        csvDf.plot.scatter(x="Predicted",y="Id")
        plt.show()
        print(csvDf)

        
