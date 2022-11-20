import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import re
import csv
import os
import pandas as pd
import numpy as np
import time
import traceback
from tqdm import tqdm

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

    parsed = ET.parse(filepath)
    root = parsed.getroot()
    sectionsToProcess = []
    sectionsToProcess.append(root.findall('brief_summary'))
    sectionsToProcess.append(root.findall('detailed_description'))

    text = ""
    for section in sectionsToProcess:
        assert(len(section)==1 or len(section)==0)
        if(len(section)==0):continue
        section = section[0]
        sectionText = section.findall('textblock')
        assert(len(sectionText)==1)
        sectionText = sectionText[0].text
        text += "\n" + sectionText
    
    return text
    

#what each thread will do
#get a nice word list of the sections we want from an xml file
def preProcessItem(inputItem):
        try:
            filepath = os.path.join(os.getcwd(),"search_results",inputItem["NCTNum"]+".xml")
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
            year=year[-4:]

        status = row["Status"]
        NCTNum = row["NCT Number"]

        #prepare output
        if status not in statuses:
            statuses[status] = dict()
        if year not in statuses[status]:
            statuses[status][year] = dict()
        
        #prepare input
        toGet.append({"year":year,
                       "status":status,
                       "NCTNum":NCTNum})


    print("Starting file reads, total current runtime:",time.time()-startTime)
    #read all the xml files and get word lists
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
        yearDict = statuses[study["status"]][study["year"]]
        wordsFoundInCurrentStudy = set()
        currentWordlist = study["words"]
        for word in currentWordlist:
            #word already found in year
            if word in yearDict:
                yearDict[word][0] = yearDict[word][0]+1
            else:
                yearDict[word] = [1,[]] #[word count, list of percent of word in respective text]
            
            #word not already found in block
            #percent of word in respective text
            if(word not in wordsFoundInCurrentStudy):
                wordsFoundInCurrentStudy.add(word)
                percentOfWord = 100.0*currentWordlist.count(word)/len(currentWordlist)
                yearDict[word][1].append(percentOfWord)
    
    
    #format data
    colsPerYear = 3
    for statusKey,statusVal in statuses.items():

        #count max words
        maxWords = 0
        for yearVal in statusVal.values():
            maxWords = max(maxWords,len(yearVal))
        
        shape = (maxWords+2,colsPerYear*len(statusVal))
        output =np.full(shape, "", dtype="object", order='C')

        sortedYears = sorted(statusVal.items(), key=lambda item: int(item[0]) if item[0].isdecimal() else 99999999)
        for yearInd,(yearKey,yearVal) in enumerate(sortedYears):
            #titles
            col = yearInd*colsPerYear
            output[0,col] = yearKey
            output[1,col:col+colsPerYear]=["word","number of mentions","Avg percent of mentions per study"]

            #values
            sortedWords = sorted(yearVal.items(), key=lambda item: item[1][0],reverse =True)
            for row,(wordKey,wordVal) in enumerate(sortedWords):
                #average second entry (Average percent of word in respective text)
                avgPercent = str(sum(wordVal[1])/len(wordVal[1]))
                output[row+2,col:col+colsPerYear]=[wordKey,wordVal[0],avgPercent+"%"]
    
        #save the excel sheet with name of status
        with open(os.path.join(outputDir,statusKey+'.csv'), 'w', newline='', encoding="utf-8-sig") as fp:
                writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerows(output.tolist())
    
    print("Done:",time.time()-startTime)

if __name__ == "__main__":
    main()



