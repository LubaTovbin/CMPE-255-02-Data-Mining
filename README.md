# CMPE-255-02-Data-Mining
Data mining for pattern discovery: How income and education levels affect various crime rates?

## Code
### reader.py
Use this file to extract, pre-process, and retrieve data (in the form of Pandas Dataframes).

For more information, run the following in your code (create file in "code/" folder):
```
import reader
help(reader)
```
Run dataVisualizationAndMLmodels.ipynb to visualize the data and run 7 different regression models.

### us_state_abbrev.py
Sourced from https://gist.github.com/rogerallen/1583593 in order to map the names of US States to Two Letter Codes


## Final Datasets Used (Sources):
### Income Dataset (Persons above the age of 25, 2005-2009):
#### Source - US Census
https://www2.census.gov/library/publications/2011/compendia/usa-counties/excel/INC01.xls
https://www2.census.gov/library/publications/2011/compendia/usa-counties/excel/INC02.xls
https://www2.census.gov/library/publications/2011/compendia/usa-counties/excel/INC03.xls

### Crime dataset:
#### Source - FBI Crime Reports
https://www2.fbi.gov/ucr/05cius/data/documents/05tbl10.xls
https://www2.fbi.gov/ucr/cius2006/data/documents/06tbl10.xls
https://www2.fbi.gov/ucr/cius2007/data/documents/07tbl10.xls
https://www2.fbi.gov/ucr/cius2008/data/documents/08tbl10.xls
https://www2.fbi.gov/ucr/cius2009/data/documents/09tbl10.xls

### Education Dataset (Persons above the age of 25, 2005-2009):
#### Source - US Census
https://www2.census.gov/library/publications/2011/compendia/usa-counties/excel/EDU01.xls
https://www2.census.gov/library/publications/2011/compendia/usa-counties/excel/EDU02.xls

### US Census All Data
https://www2.census.gov/library/publications/2011/compendia/usa-counties/zip/
metadata: https://www2.census.gov/library/publications/2011/compendia/usa-counties/excel/Mastdata.xls
