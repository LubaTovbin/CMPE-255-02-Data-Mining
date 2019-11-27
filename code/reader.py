#!/usr/bin/env python
# coding: utf-8

# In[6]:


from preprocess import get_processed_data, get_processed_data_state, LoadViolentCrimeData, LoadPropertyCrimeData, LoadIncomeDistribution, LoadEducationData

data = get_processed_data()
state_data = get_processed_data_state()

# In[7]:


def get_label(crime_type = "total", reg = "sqrt_log", subset=False):
    """ 
    Returns a county-indexed dataframe of labels(y) based on crime_type
    :param crime_type: {"property", "violent", "total"}
    :param reg: {"none", "log", "sqrt_log"}
    :param subset: {True, False}
    :return: pandas dataframe
    """
    
    crime = ""
    if reg == "log":
        crime += "Log "
    elif reg == "sqrt_log":
        crime += "Root Log "
        
    if crime_type == "property":
        crime += "Property Crime"
    
    elif crime_type == "violent":
        crime += "Violent Crime"
    else:
        crime += "Total Crime"
    
    if subset == True:
        return state_data[[crime]]
    
    return data[[crime]]
        
    
def get_features(education_type="dropout", income_type="mean", get_high_bracket = False, subset=False):
    """ 
    Returns a county-indexed dataframe of features(X = [education, income]) based on params
    :param education_type: {"dropout", "degreeless", "degree"}
    :param income_type: {"mean", "median", "percapita", "deviation"}
    :param get_high_bracket: {True, False}
    :param subset: {True, False}
    :return: pandas dataframe
    """
    
    feature_columns = []
    
    if education_type == "degreeless":
        feature_columns.append("Percent No Degree")
    elif education_type == "dropout":
        feature_columns.append("Percent High School Dropouts")
    else:
        feature_columns.append("Percent Any Degree")
        
    if income_type == "median":
        feature_columns.append("Median Income (Household)")
    elif income_type == "percapita":
        feature_columns.append("Per Capita Income")
    elif income_type == "deviation":
        feature_columns.append("Income Standard Deviation (Household)")
    else:
        feature_columns.append("Mean Income (Household)")
        
    if get_high_bracket == True:
        feature_columns.append("High Bracket Income (Household)")
        
    if subset == True:
        return state_data[feature_columns]
    
    return data[feature_columns]


def get_data(education_type="dropout", income_type="mean", crime_type = "total", crime_reg = "sqrt_log", get_high_bracket = True, subset=False):
    """ 
    Returns a county-indexed dataframe of features (education, income) and label (crime) based on params
    :param education_type: {"dropout", "degreeless", "degree"}
    :param income_type: {"mean", "median", "percapita", "deviation"}
    :param crime_type: {"property", "violent", "total"}
    :param crime_reg: {"none", "log", "sqrt_log"}
    :param subset: {True, False}
    :return: pandas dataframe
    """
    
    label = get_label(crime_type, crime_reg, subset)
    features = get_features(education_type, income_type, get_high_bracket, subset)
    
    queried_data = features.merge(label, on="Area_name")
    
    return queried_data
    
    
def get_all_data():
    """ 
    Returns a county-indexed dataframe of all feature types (X) and label types (y)
    Refer to schema or documentation of the get_data function for information about columns
    Preferably use for exploration and visualization only. 
    Use the get_data, get_features, or get_label functions to retrieve data for processing
    :return: pandas dataframe
    """
    
    return data

def get_all_data_by_state():
    """
    Returns all data for entire states only
    :return: pandas dataframe
    """
    
    return state_data

def get_us_income_distribution():
    """
    Returns the income distribution for all income ranges in the United States
    :return: pandas series
    """
    return LoadIncomeDistribution()
    
def get_all_property_crime():
    """
    Returns all the property crime data
    :return: pandas dataframe
    """
    return LoadPropertyCrimeData()
    
def get_all_violent_crime():
    """
    Returns all the violent crime data
    :return: pandas dataframe
    """
    return LoadViolentCrimeData()

def get_all_education_data():
    """
    Returns all education data (states included)
    :return: pandas dataframe
    """
    return LoadEducationData()
    
    
# In[ ]:




