import argparse
from asyncio.subprocess import PIPE
from asyncore import write
import fnmatch
from tempfile import NamedTemporaryFile
import subprocess
import time
import json
import xml.etree.ElementTree as ET


#Script used to cycle a package and get info on prog or test

def installPkg(pkg,version):
    process = subprocess.Popen(["pipenv", "install", pkg+"=="+version], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        #timeout is set to ntimes just in case to have some room 
        out_p, err_p = process.communicate(timeout=35.0)

    except subprocess.TimeoutExpired:
        process.kill()
        out_p, err_p = process.communicate()

    processRCode = process.returncode
    return (version,out_p,err_p,processRCode)

def execProg(prog,version,returnCode):
        if returnCode == 0:
            execProg = subprocess.Popen(["python3",prog], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                out , err = execProg.communicate(timeout=30.0)
            except subprocess.TimeoutExpired:
                execProg.kill()
                out , err = execProg.communicate()
            execProgRCode = execProg.returncode
            return (version,out,err,execProgRCode)
        else:
            return(version,"None","None",returnCode)
    

def getTests(dir,version,pkg,returnCode):
    #just in case something goes wrong
    resMap = {'name': 'pytest', 'errors': '0', 'failures': '0', 'skipped': '0', 'tests': '0', 'time': '0.0', 'timestamp': '', 'hostname': ''}
    if returnCode == 0:
        file = NamedTemporaryFile()
        process = subprocess.Popen(["pytest","-q","--junit-xml="+file.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try: 
            out, err = process.communicate(timeout=30.0)
        except subprocess.TimeoutExpired:
            process.kill()
            out, err = process.communicate()
        try:
            tree = ET.parse(file.name)
            root = tree.getroot()
            resMap = root[0].attrib
        except ET.ParseError:
            resMap = {'name': 'pytest', 'errors': '0', 'failures': '0', 'skipped': '0', 'tests': '0', 'time': '0.0', 'timestamp': '', 'hostname': ''}
        return (version,resMap,err,process.returncode)
    else:
        return (version,resMap,"None",returnCode)

def releaseType(releasetype,list):
    matching = []
    if releasetype=="major":
        matching = fnmatch.filter(list,'*.0.0')
    elif releasetype=="minor":
        matching = fnmatch.filter(list,'*.[1-9]*.0')
    elif releasetype=="patch":
        matching = fnmatch.filter(list,'*.*.[1-9]*')
    elif releasetype=="all":
        matching = list
    return matching

def fetchDependency(pkg):
    process = subprocess.Popen(['pipenv','graph','--json-tree'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        out,err = process.communicate(10)
    except subprocess.TimeoutExpired:
        process.kill()
        out,err = process.communicate()
    resMap = json.loads(out)
    for e in resMap:
        if e['key']==pkg:
            return e
    return resMap
    
def constructDict(logs,pkg,verbose,test):
        data = {}
        Package = []
        Version = []
        Installation = []
        Execution= []
        ReturnCode=[]
        ExecutionTime=[]
        Iteration=[]
        TestTime=[]
        TestErr=[]
        TestFail=[]
        TestSkip=[]
        TestSucc=[]
    #Constructing dataframe from logs
        if not (verbose):
            if not test:
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
                data = {'Package':Package,'Iteration':Iteration,'Version':Version,'Installation':Installation,
        'Execution':Execution,'ReturnCode':ReturnCode,'ExecutionTime(s)':ExecutionTime}
            else:
                for l in logs:
                    Package.append(pkg)
                    Version.append(l[0][0])
                    Iteration.append(l[2])
                    ExecutionTime.append(l[3])
                    TestTime.append(l[1][1]['time'])
                    TestErr.append(l[1][1]['errors'])
                    TestFail.append(l[1][1]['failures'])
                    TestSkip.append(l[1][1]['skipped'])
                    #Calculate success test
                    TestSucc.append(int(l[1][1]['tests']) - int(l[1][1]['skipped']) - int(l[1][1]['failures']) - int(l[1][1]['errors']))
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
                data = {'Package':Package,'Iteration':Iteration,'Version':Version,'Installation':Installation,
        'Execution':Execution,'ReturnCode':ReturnCode,'ExecutionTime(s)':ExecutionTime,
        'TestTime':TestTime,'TestErr':TestErr,'TestFail':TestFail,'TestSkip':TestSkip,'TestSucc':TestSucc}
                
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
        #print(len(Package))
        #print(len(Version))
        #print(len(Installation))
        #print(len(Execution))
        #print(len(ReturnCode))
        #print(len(ExecutionTime))
        print(data)
        with open("result.json", "w") as write_file:
            json.dump(data, write_file, indent=4)
        
        

if __name__ == '__main__':

        parser = argparse.ArgumentParser()
        #Parse args and option
        parser.add_argument("--prog",help="PATH of program or directory to be used for cyclying dependecies",action='store')
        parser.add_argument("pkg",help="package to be cycled")
        parser.add_argument("-rt","--releasetype",help="what type of release to test for default major",default="major",choices=['minor','patch','all'])
        parser.add_argument("-v","--verbose", help="logs from every process",action='store_true')
        parser.add_argument("-N","--ntimes",help="INT number of execution of prog for pkg version default 1",default=1)
        parser.add_argument("-t","--test",help="if your project using pytest use this option",action='store_true')
        parser.add_argument("--outputfile",help="Name of the ouputfile if prog outputs csv file")
        args = parser.parse_args()
        prog = args.prog
        pkg = args.pkg
        releasetype = args.releasetype
        ntimes = args.ntimes
        verbose = args.verbose
        outputfile = args.outputfile
        test=args.test

        #List of pkg version and if major,minor,patch or all.
        content_list = releaseType(releasetype,subprocess.check_output(["pip-versions", "list", pkg]).decode().splitlines())
        print(str(content_list))
        
        #List of log for each versions of pkg
        logs = []
        ran = len(content_list)
        csvLog=[]
        
        for i in range(0,ran):
            print("Testing for : " + pkg +"-"+ content_list[i] + " "+str(ntimes)+" times")
            #Install pkg from argv
            installP = installPkg(pkg,content_list[i])
            #Fetch returncode of installation
            installPRCode = installP[3]

            for k in range(0,int(ntimes)):
                #check for test option 
                if test:
                    t1 = time.time()
                    execP = getTests(prog,content_list[i],pkg,installPRCode)
                    t2 = time.time()
                    timep = t2 - t1
                    cout=""
                elif prog is not None:
                    t1 = time.time()
                    execP = execProg(prog,content_list[i],installPRCode)
                    t2 = time.time()
                    #Time ellapsed for execution time
                    timep = t2 - t1
                else :
                    print("Error nothing no test or program found")
                    exit(1)
                    #Not really part of final product
                if execP[3] == 0 :
                    #copy result from arg prog to a var
                    #check if outputfile is passed as argument
                    if outputfile is not None: 
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
                        with open("csvList.json",'w') as write_ifle:
                            json.dump(csvLog,write_ifle,indent=4)
                    else:
                        cout=""
                else :
                    cout=""
                    timep=0
                #create tuple from acquired data and add to a list
                log = (installP,execP,k,timep,cout)
                logs.append(log)
        constructDict(logs,pkg,verbose,test)
       

        
