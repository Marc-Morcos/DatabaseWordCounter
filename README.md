# Alzheimer Database Word Counter
Script to analyze word usage in the U.S. National Library of Medicine ClinicalTrials.gov database. The keyword used was “Alzheimer Disease”. From this search, we downloaded the summary of the results in a csv file (SearchResults_1.csv), then the details of each study as xml files (search_results folder). Input is read from this folder.

Expected outputs are given in the "Output" and "Output2" folders for convenience.
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
If you wish to filter for specific words, change the "wordsWeWant" variable on line 67 of alzeheimerDatabaseWordCounter.py, as shown in the comment.
The output will be sorted into a csv file for each study status. Within it, there are statistics from the studies that mention the desired words. At the top, there is the total number of studies for that year, then the number of mentions of each word in all studies in the year under "number of mentions". Under "Avg percent of mentions per study", is the sum of percent of each word makes up of the body of each study, divided by total studies.

More data can be found by running
```
python Analysis2.py
```
with outputs appearing in the "Output2" folder
The output will have all statuses mixed toghether in 1 file. For each start year, "number of mentions" and "Avg percent of mentions per study" as defined above for each word, whether the study was done in a covid year (["2020","2021","2022","2023"]), whether the study is under the "completed" status, total words in the year, and a boolean denoting whether each word was mentioned in that year.
If you wish to filter for specific words, change the "wordsWeWant" variable on line 67 of Analysis2.py.
If you wish to filter for specific statuses, change the "statusesWeWant" variable on line 71 of Analysis2.py.

You can also get some extra data needed for the study using
```
python otherDataFromStudies.py
```
and the outputs will appear under "Output/otherData" 
This will output general information about the dataset.

For more information, see the paper "Temporal Trends of Mental Health Terminology in Alzheimer’s Disease Clinical Trials" by Amir-Ali Golrokhian-Sani, Maya Morcos, Alecco Philippi, Reem Al-Rawi, Marc Morcos, Rui Fu

