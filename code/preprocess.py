import os
try:
	os.chdir(os.path.join(os.getcwd(), 'code'))
	print(os.getcwd())
except:
	pass
# %%
import pandas as pd
import numpy as np
import sys
import os
import re

import us_state_abbrev as states

base_path = os.path.abspath("..")

# %% [markdown]
# ## Crime

# %%
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
    
    return full_county, state.upper()

def TransformData(crime_data):
    
    crime_data["Log Violent Crime"] = crime_data.apply(lambda row: np.log1p(row["Violent Crime"]) if int(row["Violent Crime"]) != 0 else 0, axis=1)
    crime_data["Log Property Crime"] = crime_data.apply(lambda row: np.log1p(row["Property Crime"]) if int(row["Property Crime"]) != 0 else 0, axis=1)
    crime_data["Log Total Crime"] = crime_data.apply(lambda row: np.log1p(row["Total Crime"]) if int(row["Total Crime"]) != 0 else 0, axis=1)
    crime_data["Root Log Violent Crime"] = crime_data.apply(lambda row: np.power(row["Log Violent Crime"], 1/2), axis=1)
    crime_data["Root Log Property Crime"] = crime_data.apply(lambda row: np.power(row["Log Property Crime"], 1/2), axis=1)
    crime_data["Root Log Total Crime"] = crime_data.apply(lambda row: np.power(row["Log Total Crime"], 1/2), axis=1)

    return crime_data


def GetCrimeDataFrame(files):
    
    dataframes = []
    
    for file in files:
        df = pd.read_excel(file, index_col=[0,1], index_row=0, encoding='utf-8')
        df.columns = df.columns.str.lower()
        df["Area_name"], df["state"] = zip(*df.apply(lambda row: GetCrimeCountyNames(row), axis=1))
        df = df.set_index("Area_name")
        df["total crime"] = df.apply(lambda row: row["violent crime"] + row["property crime"], axis=1)
        df.head()
        dataframes.append(df)
        
    final_columns = list(set.intersection(*map(set, [dframe.columns.tolist() for dframe in dataframes])))
    crime_data = pd.concat(dataframes, sort=False)

    state_map = crime_data[["state"]].reset_index().drop_duplicates().set_index("Area_name")
    crime_data = crime_data.drop(columns=["state"])
    
    by_row_index = crime_data.groupby(crime_data.index)
    crime_data = by_row_index.mean()
    
    final_columns = [col for col in final_columns if col != "state"]
    crime_data = crime_data[final_columns]
    
    final_columns = [col.title() for col in final_columns]
    crime_data.columns = final_columns
    
    crime_data = crime_data.fillna(0)
    crime_data = crime_data.loc[crime_data["Total Crime"] != 0.0]
    
    return crime_data, state_map

def LoadCrimeData():
    
    crime_data, state_map = GetCrimeDataFrame(crime_dataframes)    
    
    crime_data = TransformData(crime_data)

    cols_to_return = ["Property Crime", "Violent Crime", "Total Crime", "Log Property Crime", "Log Violent Crime", "Log Total Crime", "Root Log Property Crime", "Root Log Violent Crime", "Root Log Total Crime"]
    
    return crime_data[cols_to_return]

def LoadViolentCrimeData():
    crime_data = GetCrimeDataFrame(crime_dataframes)    
    crime_data = TransformData(crime_data)
    cols_to_return = ["Murder And Nonnegligent Manslaughter", "Forcible Rape", "Robbery", "Aggravated Assault"]
    return crime_data[cols_to_return]

def LoadPropertyCrimeData():
    crime_data = GetCrimeDataFrame(crime_dataframes)    
    crime_data = TransformData(crime_data)
    cols_to_return = ["Burglary", "Larceny-Theft", "Motor Vehicle Theft", "Arson1"]
    return crime_data[cols_to_return]

# %% [markdown]
# ## Education

# %%
education_path = os.path.join(base_path, 'data/education/')

def GetNoDegree(row):
    
    total = int(row["Total"])
    no_degree = int(row["High school graduate (includes equivalency)"]) + int(row["Some college, no degree"])
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
    education_data["Percent Any Degree"] = education_data.apply(lambda row: 100.00 - float(row["Percent No Degree"]) - float(row["Percent High School Dropouts"]), axis=1)
    
    return education_data[["Percent High School Dropouts", "Percent No Degree", "Percent Any Degree"]]

# %% [markdown]
# ## Income

# %%
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
        values.append(float(income_range_means[c])/1000.0)
        frequencies.append(int(row[c]))
        total_without += int(row[c]) * float(income_range_means[c]/1000.0)
    
    remainder = total_income - total_without
    high_bracket_mean = 0

    if total_high_bracket != 0:
        high_bracket_mean = float(remainder/total_high_bracket)
    
    values.append(int(high_bracket_mean))
    frequencies.append(int(total_high_bracket))
    
    overall_income_data = np.repeat(np.array(values), np.array(frequencies))
    std_dev = np.std(overall_income_data, dtype=np.float64, ddof=1)
    
    return std_dev, high_bracket_mean


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
    income_data["Mean Income (Household)"] = income_data["Mean Income (Household)"].astype(float)/1000.00
    income_data["Median Income (Household)"] = income_data["Median Income (Household)"].astype(float)/1000.00
    income_data["Per Capita Income"] = income_data["Per Capita Income"].astype(float)/1000.00

    income_data = income_data.loc[income_data["Mean Income (Household)"] != 0.0]
    income_data["Income Standard Deviation (Household)"], income_data["High Bracket Income (Household)"] = zip(*income_data.apply(lambda row: GetIncomeStdDeviation(row), axis=1))
    
    return income_data


def LoadIncomeData():
    
    income_data = GetIncomeDataFrame(income_path)
    return income_data[["Mean Income (Household)", "Median Income (Household)", 
                        "Per Capita Income", "Income Standard Deviation (Household)", "High Bracket Income (Household)"]]   


def LoadIncomeDistribution():

    income_data = GetIncomeDataFrame(income_path)
    income_range_means = GetIncomeRangeMeans()
    income_range_means["Households with income of \$200,000 or more"] = income_data.loc["UNITED STATES", "High Bracket Income (Household)"]*1000.00

    columns_to_drop = ["Median Income (Household)", "Mean Income (Household)", "Households with income, total", "Per Capita Income",
       "Income Standard Deviation (Household)", "High Bracket Income (Household)"]

    income_data = income_data.drop(columns_to_drop, axis=1).loc["UNITED STATES"]

    final_data = income_data.rename(lambda x: float(income_range_means[x])/1000)

    return final_data
    

# %% [markdown]
# ## Processed Data

# %%
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


# %%
def get_processed_data_state():
     
    file_path = os.path.join(base_path, 'preprocessed/education_income_crime_by_state.xlsx')
    
    if os.path.exists(file_path):
        master_df_state = pd.read_excel(file_path, index_col=0)
    
    else:
        crime_data, state_map = GetCrimeDataFrame(crime_dataframes)
        crime_data = crime_data.merge(state_map, left_index=True, right_index=True).reset_index().drop(columns=["Area_name"])
        crime_data = crime_data.groupby(["state"]).sum().reset_index().rename(columns={"state": "Area_name"})
        crime_data.set_index("Area_name")
        crime_data = TransformData(crime_data)

        education_data = LoadEducationData()
        income_data = LoadIncomeData()     

        master_df_state = crime_data.merge(income_data, on="Area_name").merge(education_data, on="Area_name")
        master_df_state.to_excel(file_path)

    return master_df_state
