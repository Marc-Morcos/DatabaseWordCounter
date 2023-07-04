import os
import pandas as pd
import numpy as np
import json

# extract attribute where we expect a single answer (or 0)
def getSingularAttribute(attribute,root):
    return root.get(attribute,"Not Specified")

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
    statusesWeWant = ["RECRUITING","ENROLLING_BY_INVITATION","ACTIVE_NOT_RECRUITING","COMPLETED"]
    statusesExcluded = []
    inputFile = os.path.abspath("./SearchResults_1.csv")
    inputDF = pd.read_csv(inputFile, engine='python').dropna(how="all")
    for index, row in inputDF.iterrows():
        yearKeyToLookFor = "Start Date"
        year = row[yearKeyToLookFor]
        if(type(year) != str):
            continue #filter out studies with no start date
        else:
            
            year=year[:4]
            assert(year.isnumeric())
            if(int(year)<2020):
                year = "before2020"
            else:
                year = "2020AndBeyond"

        status = row["Study Status"].upper()
        NCTNum = row["NCT Number"]

        #filter statuses we dont want
        if status not in statusesWeWant:
            if status not in statusesExcluded:
                statusesExcluded.append(status)
            continue
        
        #prepare input
        toGet.append({"year":year,
                       "status":status,
                       "NCTNum":NCTNum})


    results = {
        "before2020": {
            "enrollmentNotIncludingNonSpecified": []
            },
        "2020AndBeyond": {
            "enrollmentNotIncludingNonSpecified": []
            }
    }
    #read all the json files and get stats
    for item in toGet:
        filepath = os.path.join(os.getcwd(),"search_results",item["NCTNum"]+".json")
        with open(filepath, "r", encoding="utf8") as f:
            jsonData = json.load(f)

        #location country
        countries = jsonData["protocolSection"].get("contactsLocationsModule",dict()).get("locations",[])
        outputCountry = "Not Specified"
        NumUS = 0
        NumNonUS = 0
        countriesList = []
        for location in countries:
                tmp = location.get("country",None)
                if(tmp is not None):
                    countriesList.append(tmp)
        if(len(countries) > 0):
            for finalCountry in countriesList:
                if(finalCountry.lower() == "united states"):
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
        eligibility = jsonData["protocolSection"]["eligibilityModule"]
        sex = getSingularAttribute('sex',eligibility)
        countValue("sex",sex,results[item["year"]])   

        #enrollment 
        enrollment = getSingularAttribute("count",jsonData["protocolSection"]["designModule"].get("enrollmentInfo",dict()))
        if(enrollment!="Not Specified"):
            assert(isinstance(enrollment,int) or enrollment.isnumeric())
            enrollment = int(enrollment)
            results[item["year"]]["enrollmentNotIncludingNonSpecified"].append(enrollment)

        
        study_design_info = (jsonData["protocolSection"]["designModule"]).get("designInfo",None)
        if(study_design_info is not None):

            #allocation
            allocation = getSingularAttribute("allocation",study_design_info)
            countValue("allocation",allocation,results[item["year"]])        

            #intervention_model
            intervention_model=  getSingularAttribute("interventionModel",study_design_info)
            countValue("interventionModel",intervention_model,results[item["year"]])

            #masking
            masking=  getSingularAttribute("masking",study_design_info.get("maskingInfo",dict()))
            #get first word
            if(masking != "Not Specified"):
                masking = masking.split()[0]
            countValue("masking",masking,results[item["year"]])

            #primary_purpose
            primary_purpose=  getSingularAttribute("primaryPurpose",study_design_info)
            countValue("primaryPurpose",primary_purpose,results[item["year"]])
        else:
            countValue("allocation","Not Specified",results[item["year"]])        
            countValue("interventionModel","Not Specified",results[item["year"]])
            countValue("masking","Not Specified",results[item["year"]])
            countValue("primaryPurpose","Not Specified",results[item["year"]])

    #tally enrollment stats
    for key in results:
        stats = {
            "MEAN":np.mean(results[key]["enrollmentNotIncludingNonSpecified"]),
            "STDDEV":np.std(results[key]["enrollmentNotIncludingNonSpecified"])
        }
        results[key]["enrollmentNotIncludingNonSpecified"] = stats
    
    outputDir = os.path.abspath("./Output")
    os.makedirs(outputDir, exist_ok = True)
    with open(os.path.join(outputDir,"otherData.txt"), 'w') as f:
        f.writelines([\
        "_Results_",\
        "\nTotal Studies: "+str(len(inputDF)),\
        "\nSections we want: "+str(statusesWeWant),\
        "\nNum studies after applying filters: "+str(len(toGet)),\
        "\nSections we dont want: "+str(statusesExcluded),\
        "\n"+json.dumps(results, indent=4),\
        ])


if __name__ == "__main__":
    main()



