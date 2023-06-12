# Breast Cancer Database Word Counter
Script to analyze word usage in the U.S. National Library of Medicine ClinicalTrials.gov database. The keyword used was “Breast Cancer”. We also prefiltered it for studies with the following statusses: ["Recruiting","Enrolling by invitation","Active, not recruiting","Completed"]
From this search, I downloaded the summary of the results in a csv file (SearchResults_1.csv), then the details of each study as xml files (search_results.zip).

To run, extract search_results.zip into a folder called "search_results", install python 3.11 and in the terminal, run
```
cd <path where you checked out this repository>
python -m pip install pandas==1.5.2 numpy==1.24.1 tqdm==4.64.1
python databaseWordCounter.py
```
The results will appear in a folder called "Output"

You can also get some extra data needed for the study into the console using
```
python otherDataFromStudies.py
```
and the outputs will also appear in the "Output" folder
