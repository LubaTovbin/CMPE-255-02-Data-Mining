# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'code'))
	print(os.getcwd())
except:
	pass
# %%
from IPython import get_ipython

# %%
import reader
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
import sklearn.metrics as metrics
from matplotlib import pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns

# %% [markdown]
# #### Loading the dataset

# %%
data=reader.get_all_data()
data.head()

# %% [markdown]
# #### Getting features and label and performing few transformations

# %%
from collections import OrderedDict
class Row(object):
    
    def __init__(self):
        self.education_type = None
        self.income_type = None
        self.crime_regularization = None
        self.LinearRegMSE = None
        self.RidgeMSE = None
        self.DecisionTreeMSE = None
        self.KNeighbourMSE = None
        self.SVR_MSE = None
        self.RandomForestMSE = None
        self.BoostingMSE = None

    def toDict(self):
        return {'education_type' : self.education_type,
                'income_type' : self.income_type,
                'crime_regularization': self.crime_regularization,
                'LinearRegMSE':  self.LinearRegMSE,
                'RidgeMSE' : self.RidgeMSE,
                'DecisionTreeMSE' : self.DecisionTreeMSE,
                'KNeighbourMSE': self.KNeighbourMSE,
                'SVR_MSE' : self.SVR_MSE,
                'RandomForestMSE': self.RandomForestMSE,
                'BoostingMSE' :self.BoostingMSE
               }

# %% [markdown]
# #### Applying models

# %%
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import ParameterGrid

import warnings
warnings.filterwarnings("ignore")

param_grid = {"education_type" :["dropout", "degree"], "income_type" :["median", "deviation"], "crime_type":["log", "sqrt_log"]}
result = pd.DataFrame()

for param in list(ParameterGrid(param_grid)):
    row = Row()
    row.education_type = "High School Dropout Percent" if param['education_type'] == 'dropout' else "Percent with Any Degree"
    row.income_type = "Median Income" if param['income_type'] == "median" else "Income Standard Deviation"
    row.crime_regularization = "Square Root of Log" if param['crime_type'] == 'log' else "Fourth Root of Log"
    X = reader.get_features(param['education_type'], param['income_type'])
    y = reader.get_label('total', param['crime_type'])
    y=np.power(y,1/2)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    
    
    ## Scale input data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train.to_numpy())
    X_test = scaler.fit_transform(X_test.to_numpy())
    
    ## Liner Regression
    linreg = LinearRegression()
    linreg.fit(X_train, y_train)
    y_pred=linreg.predict(X_test)
    row.LinearRegMSE = metrics.mean_squared_error(y_test, y_pred)
    
    ## Ridge Regression
    ridgereg = Ridge(alpha=1.0)
    ridgereg=ridgereg.fit(X_train,y_train)
    y_pred=ridgereg.predict(X_test)
    row.RidgeMSE = metrics.mean_squared_error(y_test, y_pred)
    
    ## Decision Tree
    regr = DecisionTreeRegressor(max_depth=2)
    regr.fit(X_train, y_train)
    y_pred = regr.predict(X_test)
    row.DecisionTreeMSE = metrics.mean_squared_error(y_test, y_pred)
    
    ## Random Forest Tree
    regr = RandomForestRegressor(max_depth=2)
    regr.fit(X_train, y_train)
    y_pred = regr.predict(X_test)
    row.RandomForestMSE = metrics.mean_squared_error(y_test, y_pred)
    
    ### Boosting
    params = {'n_estimators': 100, 'max_depth': 2}
    clf = GradientBoostingRegressor(**params)
    clf.fit(X_train, y_train)
    row.BoostingMSE = metrics.mean_squared_error(y_test, y_pred)
    
    ### KNN
    neigh = KNeighborsRegressor(n_neighbors=3)
    neigh.fit(X_train, y_train) 
    y_pred=neigh.predict(X_test)
    row.KNeighbourMSE = metrics.mean_squared_error(y_test, y_pred)
    
    ### SVR
    svr = SVR(gamma='auto')
    svr = svr.fit(X_train, y_train.values.ravel())
    y_pred=svr.predict(X_test)
    row.SVR_MSE = metrics.mean_squared_error(y_test, y_pred)
   
    
    result = result.append(row.toDict(), ignore_index=True)

result

# %% [markdown]
# #### SVR Support Vectors

# %%
X = reader.get_features("dropout", "median")
y = reader.get_label('total', "log")
y=np.power(y,1/2)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train.to_numpy())
X_test = scaler.fit_transform(X_test.to_numpy())


svr = SVR(gamma='auto')
svr = svr.fit(X_train, y_train.values.ravel())
y_pred=svr.predict(X_test)

print(metrics.mean_squared_error(y_test, y_pred))
supportVectors = len(svr.support_vectors_)
SV=svr.support_vectors_
print("Number of support vectors : ",supportVectors)
print(" ")
print("Support Vectors : \n", SV)

# %% [markdown]
# #### Linear Regression

# %%
X = reader.get_features("degree", "median")
y = reader.get_label('total', "log")
y=np.power(y,1/2)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train.to_numpy())
X_test = scaler.fit_transform(X_test.to_numpy())

linreg = LinearRegression()
linreg.fit(X_train, y_train)
y_pred=linreg.predict(X_test)
print(metrics.mean_squared_error(y_test, y_pred))

linreg.coef_


# %%


