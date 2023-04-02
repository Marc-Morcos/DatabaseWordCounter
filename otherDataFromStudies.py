import xml.etree.ElementTree as ET
import os
import pandas as pd
import numpy as np
import json

# extract attribute where we expect a single answer (or 0)
def getSingularAttribute(attribute,root):
    all = root.findall(attribute)
    if(len(all) == 0):
        return "Not Specified"
    assert(len(all) == 1)
    return all[0].text

#count value in category
def countValue(category,value, outputDict):
    if not (category in outputDict):
        outputDict[category] = dict()

    if(value in outputDict[category]):
        outputDict[category][value]+=1
    else:
        outputDict[category][value]=1


def main():

    #change directory to current file path
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    #read original csv 
    toGet = []
    statusesWeWant = ["Recruiting","Enrolling by invitation","Active, not recruiting","Completed"]
    statusesExcluded = []
    inputFile = os.path.abspath("./SearchResults_1.csv")
    inputDF = pd.read_csv(inputFile, engine='python').dropna(how="all")
    for index, row in inputDF.iterrows():
        yearKeyToLookFor = "Start Date"
        year = row[yearKeyToLookFor]
        if(type(year) != str):
            year = "No Start Date"
        else:
            year=year[-4:]
            assert(year.isnumeric())
            if(int(year)<2020):
                year = "pre2020"
            else:
                year = "2020AndBeyond"

        status = row["Status"]
        NCTNum = row["NCT Number"]

        #exclude statuses we dont want
        if status not in statusesWeWant:
            if status not in statusesExcluded:
                statusesExcluded.append(status)
            continue
        
        #prepare input
        toGet.append({"year":year,
                       "status":status,
                       "NCTNum":NCTNum})


    results = {
        "pre2020": {
            "enrollmentNotIncludingNonSpecified": []
            },
        "2020AndBeyond": {
            "enrollmentNotIncludingNonSpecified": []
            },
        "No Start Date": {
            "enrollmentNotIncludingNonSpecified": []
            },
    }
    #read all the xml files and get stats
    for item in toGet:
        filepath = os.path.join(os.getcwd(),"search_results",item["NCTNum"]+".xml")
        parsed = ET.parse(filepath)
        root = parsed.getroot()

        #location country
        countries = root.findall('location_countries')
        outputCountry = "Not Specified"
        NumUS = 0
        NumNonUS = 0
        countriesList = []
        for countrylabel in countries:
                textList = countrylabel.findall("country")
                for text in textList:
                     countriesList.append(text.text.lower())
        if(len(countries) > 0):
            for finalCountry in countriesList:
                if(finalCountry == "united states"):
                    NumUS+=1
                else:
                    NumNonUS+=1
            if(NumUS>0):
                if(NumNonUS>0):
                    outputCountry = "USA+Other"
                else:
                    outputCountry = "USA"
            else:
                outputCountry = "Other"     
        countValue("Country",outputCountry,results[item["year"]])     
        
        #gender 
        eligibility = root.findall("eligibility")
        assert(len(eligibility) == 1)
        eligibility = eligibility[0]
        gender = getSingularAttribute('gender',eligibility)
        countValue("gender",gender,results[item["year"]])   

        #enrollment 
        enrollment = getSingularAttribute("enrollment",root)
        if(enrollment!="Not Specified"):
            assert(enrollment.isnumeric())
            enrollment = int(enrollment)
            results[item["year"]]["enrollmentNotIncludingNonSpecified"].append(enrollment)

        
        study_design_info = root.findall("study_design_info")
        assert(len(study_design_info) <= 1)
        if(len(study_design_info) == 1):
            study_design_info = study_design_info[0]

            #allocation
            allocation = getSingularAttribute("allocation",study_design_info)
            countValue("allocation",allocation,results[item["year"]])        

            #intervention_mode
            intervention_mode=  getSingularAttribute("allocation",study_design_info)
            countValue("intervention_mode",intervention_mode,results[item["year"]])

            #masking
            masking=  getSingularAttribute("masking",study_design_info)
            #get first word
            if(masking != "Not Specified"):
                masking = masking.split()[0]
            countValue("masking",masking,results[item["year"]])

            #primary_purpose
            primary_purpose=  getSingularAttribute("primary_purpose",study_design_info)
            countValue("primary_purpose",primary_purpose,results[item["year"]])
        else:
            countValue("allocation","Not Specified",results[item["year"]])        
            countValue("intervention_mode","Not Specified",results[item["year"]])
            countValue("masking","Not Specified",results[item["year"]])
            countValue("primary_purpose","Not Specified",results[item["year"]])

    #tally enrollment stats
    for key in results:
        stats = {
            "MEAN":np.mean(results[key]["enrollmentNotIncludingNonSpecified"]),
            "STDDEV":np.std(results[key]["enrollmentNotIncludingNonSpecified"])
        }
        results[key]["enrollmentNotIncludingNonSpecified"] = stats
        
    print("Results")
    print("Total Studies",len(inputDF))
    print("Sections we want", statusesWeWant)
    print("Num studies in sections we want",len(toGet))
    print("Sections we dont want", statusesExcluded)
    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()



