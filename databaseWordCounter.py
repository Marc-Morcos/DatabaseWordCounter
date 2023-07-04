from concurrent.futures import ThreadPoolExecutor
import re
import csv
import os
import pandas as pd
import numpy as np
import time
import traceback
from tqdm import tqdm
import json

#get list of words
def getWords(text):
    #remove everything but words, digits, whitespace, apostrophe, and dash (replace with space)
    text = re.sub(r'[^\w\d\s\'-]+', ' ', text)
    #lowercase
    text = text.lower()
    #split into words (removes whitespace)
    text=text.split()
    #get rid of 's at END of words
    text = [re.sub("'s$", '', word) for word in text]

    return text

#get brief_summary and detailed_description
def getSectionsWeWant(filepath):  
    with open(filepath, "r", encoding="utf8") as f:
        data = json.load(f)
        description = data["protocolSection"]["descriptionModule"]
        text=description.get('briefSummary', "") + "\n" + data.get('detailedDescription', "")    
        assert(text.strip()!="")
    
    return text
    

#what each thread will do
#get a nice word list of the sections we want from an json file
def preProcessItem(inputItem):
        try:
            filepath = os.path.join(os.getcwd(),"search_results",inputItem["NCTNum"]+".json")
            text = getSectionsWeWant(filepath)
            words = getWords(text)
            inputItem["words"] = words
            return inputItem
        except Exception as e:
            print("error while processing")
            print(inputItem)
            traceback.print_exc()
            raise e
        

def main():
    startTime = time.time()
    print("Starting")

    wordsWeWant = "Depression,dysthymia,anxiety,stress,distress,PTSD" #None
    
    if(wordsWeWant is not None):
        wordsWeWant = getWords(wordsWeWant)
        print("Edited wordswewant list to look like the following:",wordsWeWant)
        wordsWeWant = [wordInList.lower() for wordInList in wordsWeWant] #lowercase

    #change directory to current file path
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    #check for old output and create output folder
    outputDir = os.path.abspath("./Output")
    os.makedirs(outputDir, exist_ok = False)

    #read original csv
    statuses = dict()
    toGet = []
    inputFile = os.path.abspath("./SearchResults_1.csv")
    inputDF = pd.read_csv(inputFile, engine='python').dropna(how="all")
    for index, row in inputDF.iterrows():
        yearKeyToLookFor = "Start Date"
        year = row[yearKeyToLookFor]
        if(type(year) != str):
            year = "No "+yearKeyToLookFor
        else:
            year=year[:4]

        status = row["Study Status"].upper()
        NCTNum = row["NCT Number"]

        #prepare output
        if status not in statuses:
            statuses[status] = dict()
        if year not in statuses[status]:
            statuses[status][year] = [dict(),0] #[word dict, number of studies for that year]
        
        #prepare input
        toGet.append({"year":year,
                       "status":status,
                       "NCTNum":NCTNum})


    print("Starting file reads, total current runtime:",time.time()-startTime)
    #read all the json files and get word lists
    numThreads = 4
    with ThreadPoolExecutor(numThreads) as executor:
        toWaitFor = []
        for item in toGet:
            toWaitFor.append(executor.submit(preProcessItem,item))
        
        results = []
        for item in tqdm(toWaitFor,desc= "Reading files and doing some preprocessing", leave=True):
            results.append(item.result())
    
    print("Starting Finalization:",time.time()-startTime)

    #count statistics
    for study in results:
        yearArr = statuses[study["status"]][study["year"]]
        yearDict = yearArr[0]
        yearArr[1] = yearArr[1]+1
        wordsFoundInCurrentStudy = set()
        currentWordlist = study["words"]
        for word in currentWordlist:
            #filter only words we want
            if wordsWeWant is not None and (word not in wordsWeWant):
                continue

            #word already found in year
            if word in yearDict:
                yearDict[word][0] = yearDict[word][0]+1
            else:
                yearDict[word] = [1,[],0] #[word count, list of percent of word in respective text,num studies in year mentioning word]
            
            #word not already found in block
            if(word not in wordsFoundInCurrentStudy):
                #percent of word in respective text
                wordsFoundInCurrentStudy.add(word)
                percentOfWord = 100.0*currentWordlist.count(word)/len(currentWordlist)
                yearDict[word][1].append(percentOfWord)
                #count num studies in year mentioning word
                yearDict[word][2]+=1
    
    
    #format data
    colTitles = ["word","number of mentions","Avg percent of mentions per study","percent of studies in year mentioning word"]
    colsPerYear = len(colTitles)
    for statusKey,statusVal in statuses.items():

        #count max words
        maxWords = 0
        for yearVal in statusVal.values():
            maxWords = max(maxWords,len(yearVal[0]))
        
        shape = (maxWords+2,colsPerYear*len(statusVal))
        output =np.full(shape, "", dtype="object", order='C')

        sortedYears = sorted(statusVal.items(), key=lambda item: int(item[0]) if item[0].isdecimal() else 99999999)
        for yearInd,(yearKey,yearValArr) in enumerate(sortedYears):
            yearVal = yearValArr[0]
            #titles
            col = yearInd*colsPerYear
            output[0,col] = yearKey
            output[0,col+1] = "Num studies:"+str(yearValArr[1])
            output[1,col:col+colsPerYear]=colTitles

            #values
            sortedWords = sorted(yearVal.items(), key=lambda item: item[1][0],reverse =True)
            for row,(wordKey,wordVal) in enumerate(sortedWords):
                #for average, divide by number of studies in group (not len(wordVal[1]) since wordVal[1] has no entries of 0%)
                output[row+2,col:col+colsPerYear]=[wordKey,wordVal[0],str(sum(wordVal[1])/yearValArr[1])+"%",str(100*wordVal[2]/yearValArr[1])+"%"]
    
        #save the excel sheet with name of status
        with open(os.path.join(outputDir,statusKey+'.csv'), 'w', newline='', encoding="utf-8-sig") as fp:
                writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerows(output.tolist())
    
    print("Done:",time.time()-startTime)

if __name__ == "__main__":
    main()



