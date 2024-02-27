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
    
    assert(text!="")
    
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

    wordsWeWant = ["depression","anxiety","loneliness","distress"] #["the","alzheimer","disease","diseases","patient","patients"]
    if(wordsWeWant is not None):
        wordsWeWant = [wordInList.lower().strip() for wordInList in wordsWeWant] #lowercase
        
    #change directory to current file path
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    #check for old output and create output folder
    outputDir = os.path.abspath("./Output2")
    os.makedirs(outputDir, exist_ok = True)

    #read original csv
    toGet = []
    inputFile = os.path.abspath("./SearchResults_1.csv")
    inputDF = pd.read_csv(inputFile, engine='python').dropna(how="all")
    for index, row in inputDF.iterrows():
        yearKeyToLookFor = "Start Date"
        year = row[yearKeyToLookFor]
        if(type(year) != str):
            continue #filter out studies with no year
        else:
            year=year[-4:]

        status = row["Status"]
        NCTNum = row["NCT Number"]

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
    numCols = 7+len(wordsWeWant)*3
    shape = (len(results),numCols)
    output =np.full(shape, "", dtype="object", order='C')

    #populate rows for each study
    covidYears = ["2020","2021","2022","2023"]
    for rowInd,study in enumerate(results):
        currRow = [None]*numCols
        currRow[0] = study["year"]
        currRow[1] = int(study["year"] in covidYears)
        currRow[2] = int(study["status"] == "Completed")
        currRow[3] = len(study["words"])
        
        totalMentions = 0
        totalPercent = 0
        totalBoolMention = False
        #stats for individual words
        for goalInd,goalWord in enumerate(wordsWeWant):
            wordMentions = study["words"].count(goalWord)
            percentOfWord = 100.0*wordMentions/len(study["words"])
            indOffset = 4
            currRow[indOffset+goalInd] = str(percentOfWord)+"%"
            indOffset += len(wordsWeWant)+1
            currRow[indOffset+goalInd] = wordMentions
            indOffset += len(wordsWeWant)+1
            currRow[indOffset+goalInd] = int(wordMentions!=0)
            totalMentions+=wordMentions
            totalPercent+=percentOfWord
            totalBoolMention = (totalBoolMention or (wordMentions!=0))
        
        #cumulative stats for all words
        indOffset = 4+len(wordsWeWant)
        currRow[indOffset] = str(totalPercent)+"%"
        indOffset += len(wordsWeWant)+1
        currRow[indOffset] = totalMentions
        indOffset += len(wordsWeWant)+1
        currRow[indOffset] = int(totalBoolMention)

        assert(None not in currRow)

        output[rowInd,:] = currRow

    #sort rows
    sortCol = 4+len(wordsWeWant)+ len(wordsWeWant)+1 #sort by total mentions
    indices = (-output[:, sortCol]).astype(int).argsort()
    output = output[indices]

    # column titles
    colTitles = ["Start Year", "IsCovidYear","is completed","total words"]
    colTitles+= [currWord + " percent" for currWord in wordsWeWant]
    colTitles+= ["any word we want percent"]
    colTitles+= [currWord + " num mentions" for currWord in wordsWeWant]
    colTitles+= ["any word we want num mentions"]
    colTitles+= [currWord + " is mentioned" for currWord in wordsWeWant]
    colTitles+= ["any word we want is mentioned"]
    assert(len(colTitles) == numCols)
    
    #save the excel sheet with name of status
    with open(os.path.join(outputDir,'output.csv'), 'w', newline='', encoding="utf-8-sig") as fp:
            writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(colTitles)
            writer.writerows(output.tolist())
    
    print("Done:",time.time()-startTime)

if __name__ == "__main__":
    main()



