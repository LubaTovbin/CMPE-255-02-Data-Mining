#!/usr/bin/env python
# coding: utf-8

# In[140]:


import pandas as pd
import numpy as np
import sys
import os
import re

import us_state_abbrev as states

base_path = os.path.abspath("..")


# ## Crime

# In[141]:


crime_path = os.path.join(base_path, 'data/crime/')
crime_dataframes = [os.path.join(crime_path, file) for file in os.listdir(crime_path)]

def GetCrimeCountyNames(row):
    state = row.name[0]
    state = state.split("\ue83a")[0]
    state = state.split("-")[0]
    state = state.lower().title().strip()
    state_code = states.us_state_abbrev[state]
    
    county = row.name[1]
    county = "".join([letter for letter in county if not letter.isnumeric()])
    county = re.sub("County" ,"", county)
    county = re.sub("Police" ,"", county)
    county = re.sub("Department" ,"", county)
    county = county.strip()
    
    full_county = county + ", " + state_code.strip()
    
    return full_county

def GetCrimeDataFrame(files):
    
    dataframes = []
    
    for file in files:
        df = pd.read_excel(file, index_col=[0,1], index_row=0, encoding='utf-8')
        df.columns = df.columns.str.lower()
        df["Area_name"] = df.apply(lambda row: GetCrimeCountyNames(row), axis=1)
        df = df.set_index("Area_name")
        df["total crime"] = df.apply(lambda row: row["violent crime"] + row["property crime"], axis=1)
        df.head()
        dataframes.append(df)
        
    final_columns = list(set.intersection(*map(set, [dframe.columns.tolist() for dframe in dataframes])))
    crime_data = pd.concat(dataframes, sort=False)
    
    by_row_index = crime_data.groupby(crime_data.index)
    crime_data = by_row_index.mean()
    
    crime_data = crime_data[final_columns]
    final_columns = [col.title() for col in final_columns]
    crime_data.columns = final_columns
    
    crime_data = crime_data.fillna(0)
    crime_data = crime_data.loc[crime_data["Total Crime"] != 0.0]
    
    return crime_data

def LoadCrimeData():
    
    crime_data = GetCrimeDataFrame(crime_dataframes)    
    return crime_data[["Property Crime", "Violent Crime", "Total Crime"]]


# ## Education

# In[142]:


education_path = os.path.join(base_path, 'data/education/')

def GetNoDegree(row):
    
    total = int(row["Total"])
    no_degree = int(row["Completing less than 9th grade"]) + int(row["High school graduate (includes equivalency)"]) + int(row["Some college, no degree"])
    return ((1.00 - (float(no_degree)/float(total)))*100)


def CleanEducationAttrName(row):
    name = row["Attribute Name"]
    name = re.sub(r"Educational attainment", "", name)
    name = re.sub(r"Persons 25 years and over,", "", name)
    name = re.sub(r"persons 25 years and over", "", name)
    name = re.sub(r"2005-2009", "", name)
    name = re.sub(r"\s\s+", " ", name)
    name = re.sub("\-", "", name)
    name = name.strip().capitalize()
    return name

def GetEducationDataFrame(education_path):
    education_dataframes = [os.path.join(education_path, file) for file in os.listdir(education_path) if "EDU" in file]
    
    education_metadata = pd.read_excel(os.path.join(education_path, "education_by_counties.xlsx"))
    education_metadata["Attribute Name"] = education_metadata.apply(lambda row: CleanEducationAttrName(row), axis=1)

    education_data = []

    for idx, row in education_metadata.iterrows():
        location = row["Location"]
        filename = location[:len(location)-1]
        file = [x for x in education_dataframes if re.search(filename, x)][0]
        df = pd.read_excel(file, location, index_col=0)
        column = df.loc[:,[row["ID"]]]
        column = column.rename(columns = {row['ID']:row["Attribute Name"]})
        education_data.append(column)

    education_data = pd.concat(education_data, axis=1)
    education_data = education_data.loc[education_data["Total"] != 0]
    
    return education_data


def LoadEducationData():
    
    education_data = GetEducationDataFrame(education_path)
    education_data["Percent High School Dropouts"] = education_data.apply(lambda row: 100.00 - float(row["Percent high school graduate or higher"]), axis=1)
    education_data["Percent No Degree"] = education_data.apply(lambda row: GetNoDegree(row), axis=1)
#     education_data["Percent Any Degree"] = education_data.apply(lambda row: 100.00 - float(row["Percent No Degree"]), axis=1)
    
    return education_data[["Percent High School Dropouts", "Percent No Degree"]]#, "Percent Any Degree"]]


# ## Income

# In[155]:


income_path = os.path.join(base_path, 'data/income/')

def GetIncomeRangeMeans():
    income_range_means = {
        "Households with income less than \$10,000": 5000,
        "Households with income of \$10,000 to \$14,999": 12500,
        "Households with income of \$15,000 to \$19,999": 17500,
        "Households with income of \$20,000 to \$24,999": 22500,
        "Households with income of \$25,000 to \$29,999": 27500,
        "Households with income of \$30,000 to \$34,999": 32500,
        "Households with income of \$35,000 to \$39,999": 37500,
        "Households with income of \$40,000 to \$44,999": 42500,
        "Households with income of \$45,000 to \$49,999": 47500,
        "Households with income of \$50,000 to \$59,999": 55000,
        "Households with income of \$60,000 to \$74,999": 67500,
        "Households with income of \$75,000 to \$99,999": 87500,
        "Households with income of \$100,000 to \$124,999": 112500,
        "Households with income of \$125,000 to \$149,999": 137500,
        "Households with income of \$150,000 to \$199,999": 175000
    }
    return income_range_means

income_range_means = GetIncomeRangeMeans()

def GetIncomeStdDeviation(row):
    
    values, frequencies = [], []

    total_income = int(row["Households with income, total"]) * int(row["Mean Income (Household)"])
    total_high_bracket = int(row["Households with income of \$200,000 or more"])
    columns_to_check = [str(x) for x in row.axes[0].tolist() if "$" in str(x) and "more" not in str(x)]
    
    total_without = 0
    for c in columns_to_check:
        values.append(int(income_range_means[c]))
        frequencies.append(int(row[c]))
        total_without += int(row[c]) * int(income_range_means[c])
    
    remainder = total_income - total_without
    high_bracket_mean = 0

    if total_high_bracket != 0:
        high_bracket_mean = int(remainder/total_high_bracket)
    
    values.append(int(high_bracket_mean))
    frequencies.append(int(total_high_bracket))
    
    overall_income_data = np.repeat(np.array(values), np.array(frequencies))
    std_dev = np.std(overall_income_data, dtype=np.float64, ddof=1)
    
    return std_dev


def CleanIncomeAttrName(row):
    name = row["Attribute Name"]
    name = re.sub(r" in the past 12 months \(in 2009 inflation-adjusted dollars\)", "", name)
    name = re.sub(r"in 2005-2009", "", name)
    name = re.sub(r"2005-2009", "", name)
    name = re.sub(r"\s\s+", " ", name)
    name = re.sub("\$", "\\$", name)
    name = name.strip()
    return name


def GetIncomeDataFrame(income_path):

    income_dataframes = [os.path.join(income_path, file) for file in os.listdir(income_path) if "INC" in file]

    income_metadata = pd.read_excel(os.path.join(income_path, "income_by_counties.xlsx"))
    income_metadata["Attribute Name"] = income_metadata.apply(lambda row: CleanIncomeAttrName(row), axis=1)

    income_data = []

    for idx, row in income_metadata.iterrows():
        location = row["Location"]
        filename = location[:len(location)-1]
        file = [x for x in income_dataframes if re.search(filename, x)][0]
        df = pd.read_excel(file, location, index_col=0)
        column = df.loc[:,[row["ID"]]]
        column = column.rename(columns = {row['ID']:row["Attribute Name"]})
        income_data.append(column)

    income_data = pd.concat(income_data, axis=1)
    income_data = income_data.rename(columns = {"Mean household income": "Mean Income (Household)",
                                            "Median household income": "Median Income (Household)",
                                           "Per capita income": "Per Capita Income"})
    return income_data


def LoadIncomeData():
    
    income_data = GetIncomeDataFrame(income_path)
    income_data["Income Standard Deviation (Household)"] = income_data.apply(lambda row: GetIncomeStdDeviation(row), axis=1)
    income_data["Income Variance (Household)"] = income_data.apply(lambda row: float(row["Income Standard Deviation (Household)"])**2, axis=1)
    
    return income_data[["Mean Income (Household)", "Median Income (Household)", 
                        "Per Capita Income", "Income Standard Deviation (Household)"]]    


# ## Processed Data

# In[156]:


def get_processed_data():
    
    file_path = os.path.join(base_path, 'preprocessed/education_income_crime.xlsx')
    
    if os.path.exists(file_path):
        master_df = pd.read_excel(file_path, index_col=0)
    
    else:
        crime_data = LoadCrimeData()
        education_data = LoadEducationData()
        income_data = LoadIncomeData()

        master_df = crime_data.merge(income_data, on="Area_name").merge(education_data, on="Area_name")
        master_df.to_excel(file_path)
    
    return master_df


# In[157]:





# In[158]:





# In[ ]:





# In[ ]:





# In[ ]:




