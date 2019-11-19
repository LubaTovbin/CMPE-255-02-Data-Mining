#!/usr/bin/env python
# coding: utf-8

# In[6]:


from preprocess import get_processed_data
data = get_processed_data()


# In[7]:


def get_label(crime_type = "total"):
    """ 
    Returns a county-indexed dataframe of labels(y) based on crime_type
    :param crime_type: {"property", "violent", "total"}
    :return: pandas dataframe
    """
    
    if crime_type == "property":
        return data[["Property Crime"]]
    
    elif crime_type == "violent":
        return data[["Violent Crime"]]
    
    else:
        return data[["Total Crime"]]
    
def get_features(education_type="dropout", income_type="mean"):
    """ 
    Returns a county-indexed dataframe of features(X = [education, income]) based on params
    :param education_type: {"dropout", "degreeless"}
    :param income_type: {"mean", "median", "percapita", "deviation"}
    :return: pandas dataframe
    """
    
    feature_columns = []
    
    if education_type == "degreeless":
        feature_columns.append("Percent No Degree")
    else:
        feature_columns.append("Percent High School Dropouts")
        
    if income_type == "median":
        feature_columns.append("Median Income (Household)")
    elif income_type == "percapita":
        feature_columns.append("Per Capita Income")
    elif income_type == "deviation":
        feature_columns.append("Income Standard Deviation (Household)")
    else:
        feature_columns.append("Mean Income (Household)")
        
    return data[feature_columns]


def get_data(education_type="dropout", income_type="mean", crime_type = "total"):
    """ 
    Returns a county-indexed dataframe of features (education, income) and label (crime) based on params
    :param education_type: {"dropout", "degreeless"}
    :param income_type: {"mean", "median", "percapita", "deviation"}
    :param crime_type: {"property", "violent", "total"}
    :return: pandas dataframe
    """
    
    label = get_label(crime_type)
    features = get_features(education_type, income_type)
    
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


# In[ ]:




