import argparse
import json
import pandas as pd
import matplotlib as plt
import subprocess

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

def plotSome(csvLog):
    csvDf = averageCsv(csvLog)
    for frame in csvLog:
        df = pd.read_csv(frame)
        
    csvDf.plot.scatter(x="Predicted",y="Id")
    plt.show()
    print(csvDf)

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
    test = args.test
    outputfile = args.outputfile


    #cyclePackage = subprocess.Popen(['python3','~/projet/varypy/cyclePackage.py',parser])
    #Constructing dataframe from logs
    resMap = {}
    with open("result.json", "r") as read_file:
        resMap = json.load(read_file)
    df = pd.DataFrame(resMap)
    df.to_csv(pkg+"-"+releasetype)
    print(df)

    #Constructing csv mean
    if outputfile is not None:
        resList = []
        with open("csvList.json",'r') as read_ifle:
            resList = json.load(read_ifle)
        csvMean = averageCsv(resList)
        print(csvMean)
    
    