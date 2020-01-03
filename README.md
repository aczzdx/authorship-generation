# Authorship Generation

Meet you needs in authorship data cleaning & paragraph generation. 

Given raw data with 'CSV' format, the tool could return a cleaned 'CSV' file and then MS word file with appropriate author order, affiliations and conflict of interest (COI).
## Introduction
This repository generates an open source tool used to create author lists, acknowledgement pages, COI and other necessary supplementary information required by neuroscience journals.
## Installation
Authorship Generation is basically built to use pandas Dataframe and some scikit modules for processing data. Thus, we recommend Anaconda Vitual Environment with Python 3.8 in order to use our tool. 
1. Install the environment supporting for latest python:

    ``` conda install -c anaconda python==3.8```

2. Once creating the Vitual Environment, you could use a simple ``` pip ``` command:

    ```pip install <package name>```

    Python packages are including: 
spacy, ipywidgets, recordlinkage, sklearn, python-docx

3. Download OpenRefine 3.2 in openrefine.org
## Usage
- For GUI, open GUI.ipynb by jupyter notebook, then run the cells.
- Provide json for regular use, save all your configuations.
## Features

### Data Cleaning
- Call OpenRefine, then return normalized Country, State, City names, for example: USA -> united states of america; Californiaa -> california.
- Find duplicated email addresses, showing on GUI.
- Guess affiliation names based on other information (country, state, city, street). Give name recommendation in returned CSV file.

### Generating DOCX File
- Generate authors with annotator and their affiliations.
- Create author contributions in different group, displaying them in alphabetical order.
- For more detail, please see demo.docx in repository
