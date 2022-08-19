import argparse
import json
import pandas as pd
import matplotlib as plt

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
    parser.add_argument("--prog",help="PATH of program or directory to be used for cyclying dependecies")
    parser.add_argument("--pkg",help="package to be cycled",required=True)
    parser.add_argument("--releasetype",help="what type of release to test for default major",default="major",choices=['minor','patch','all'])
    parser.add_argument("--verbose", help="logs from every process",action='store_true')
    parser.add_argument("--ntimes",help="INT number of execution of prog for pkg version default 1",default=1)
    parser.add_argument("--test",help="if your project using pytest use this option",action='store_true')
    
    args = parser.parse_args()
    prog = args.prog
    pkg = args.pkg
    releasetype = args.releasetype
    ntimes = args.ntimes
    verbose = args.verbose
    outputfile = args.outputfile
    test=args.test

    #Constructing dataframe from logs
    resMap = {}
    with open("result.json", "r") as read_file:
        resMap = json.load(read_file)
    df = pd.DataFrame(resMap)
    print(df)
    