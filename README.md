# Alzheimer Database Word Counter
Script to analyze word usage in the U.S. National Library of Medicine ClinicalTrials.gov database. The keyword used was “Alzheimer Disease”. From this search, I downloaded the summary of the results in a csv file (SearchResults_1.csv), then the details of each study as xml files (search_results folder).

To run, install python 3.11. Then, in the terminal, run
```
cd <path where you checked out this repository>
pip install pandas numpy tqdm
python alzheimerDatabaseWordCounter.py
```
The results will appear in a folder called "Output"

You can also print some extra data needed for the study into the console using
```
python otherDataFromStudies.py
```
