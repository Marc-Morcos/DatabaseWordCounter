# Breast Cancer Database Word Counter
Script to analyze word usage in the U.S. National Library of Medicine ClinicalTrials.gov database. The keyword used was “Breast Cancer”. We also prefiltered it for studies with the following statusses: ["Recruiting","Enrolling by invitation","Active, not recruiting","Completed"]

To run, extract search_results.zip into a folder called "search_results", install python 3.11 and in the terminal, run
```
cd <path where you checked out this repository>
pip install pandas numpy tqdm
python databaseWordCounter.py
```

