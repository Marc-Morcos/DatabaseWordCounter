# Alzheimer Database Word Counter
Script to analyze word usage in the U.S. National Library of Medicine ClinicalTrials.gov database. The keyword used was “Alzheimer Disease”. From this search, we downloaded the summary of the results in a csv file (SearchResults_1.csv), then the details of each study as xml files (search_results folder).

Expected outputs are given in the "Output" folder for convenience
If you wish to filter for specific words, change the wordsWeWant variable on line 69 of alzeheimerDatabaseWordCounter.py, then rerun(examples given in the comments on that line)
If you wish to rerun the program, follow the instructions below.

To run:
- Delete the "Output" folder
- Install python 3.11 (https://www.python.org/downloads/release/python-3110/). 
- Then, in the terminal, run
```
cd <path where you checked out this repository>
python -m pip install pandas==1.5.2 numpy==1.24.1 tqdm==4.64.1
python alzheimerDatabaseWordCounter.py
```
The results will appear in a folder called "Output"

You can also get some extra data needed for the study using
```
python otherDataFromStudies.py
```
and the outputs will appear under "Output/otherData" 
