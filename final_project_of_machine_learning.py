# -*- coding: utf-8 -*-
"""Final project of Machine Learning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IyCYB08NiQHWqxm-uEardBG9-Keox19B
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import sklearn
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

from google.colab import files
import io

files = files.upload()

df = pd.read_csv(io.StringIO(files['dataset.csv'].decode('latin-1')))

df.tail()

df.columns

"""1. (i) 
###-Dataset is a numerical data
###-We can use classification
### Column labeling:
snoring range of the user: sr2, 
respiration rate: rr, 
body temperature: t, 
limb movement rate: lm, 
blood oxygen levels: bo, 
eye movement: rem,
number of hours of sleep: sr, 
heart rate: hr and 
Stress Levels: sl (0- low/normal, 1 – medium low, 2- medium, 3-medium high, 4 -high)

Descriptive analysis:
"""

df.describe().T

"""Multivariate data plot

"""

ax = df[["sr2","rr","t","t","lm","bo", "rem", "sr", "hr", "sl"]].plot()
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5));

"""Here we can see the variation in the each of the data features by ploting 

the each sample value.
"""

df.apply(np.std)

"""Here we can see that data need to be standerized after analysing the SD of the data as sr2 and rem value is higher than others.

(vi) Data visualization with seaborn and matplotlib
"""

sns.heatmap(df)

df.plot(kind="hist")

"""(ii) Correlation"""

corr = df.corr()
fig = plt.figure()
ax = fig.add_subplot(111)
cax = ax.matshow(corr,cmap='RdYlGn', vmin=-1, vmax=1)
fig.colorbar(cax)
ticks = np.arange(0,len(df.columns),1)
ax.set_xticks(ticks)
plt.xticks(rotation=90)
ax.set_yticks(ticks)
ax.set_xticklabels(df.columns)
ax.set_yticklabels(df.columns)
plt.show()

"""Here its visible that sl has clear corelation with the other values whether its positive or negative independent variables."""

sns.set()
cols = ['sr2', 'rr', 't', 'lm','bo', 'rem', 'sr', 'hr', 'sl']
sns.pairplot(df[cols], size = 3.5)
plt.show()

corr_mat = df.corr(method='spearman')
cg = sns.clustermap(corr_mat, cmap="PuBuGn", linewidths=0.1);
plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
cg

"""(v) PCA analysis with visualiztion

- Data Standardiztion and PCA analysis
"""

df_st = StandardScaler().fit_transform(df)
pd.DataFrame(df_st, columns = df.columns ).head(2)

pca_out = PCA().fit(df_st) #getting the component varienne 
# Proportion of the vatince we can see.

pca_out.explained_variance_ratio_

np.cumsum(pca_out.explained_variance_ratio_)

df1 = pd.DataFrame({'var':pca_out.explained_variance_ratio_,
             'PC':['PC1','PC2','PC3','PC4','PC5','PC6','PC7','PC8','PC9']})
sns.barplot(x='PC',y="var", 
           data=df1, color="c");

loadings = pca_out.components_
num_pc = pca_out.n_features_

pc_list = ["PC"+str(i) for i in list(range(1, num_pc+1))]
loadings_df = pd.DataFrame.from_dict(dict(zip(pc_list, loadings)))
loadings_df['variable'] = df.columns.values
loadings_df = loadings_df.set_index('variable')
loadings_df

plt.plot(loadings_df)

ax = sns.heatmap(loadings_df, annot=True, cmap='viridis')
plt.show()

"""b. data preparation"""

df.isnull().sum()   #Checking the null values

"""c. designing the test"""

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

#a linear model, Ridge Classifier.

scaler = StandardScaler()

from sklearn.linear_model import RidgeClassifier

Stress_Levels = ['Low','Medium Low','Medium','Medium High','High']
Feature_Coefficients = pd.DataFrame()
for i in range(0,3):
    SleepStress_Pred = df.copy()
    SleepStress_Pred['sl'] = SleepStress_Pred['sl'].apply(lambda x: 1 if x==i else 0)
    X = SleepStress_Pred.drop('sl',axis=1)
    y = SleepStress_Pred['sl']
    X_train, X_test, y_train, y_test = train_test_split(X,y,train_size=0.6,random_state=100)
    
    X_train = scaler.fit_transform(X_train)
    X_train = pd.DataFrame(X_train,columns=X.columns)
    
    X_test = scaler.transform(X_test)
    X_test = pd.DataFrame(X_test,columns=X.columns)
    
    Model = RidgeClassifier(random_state=100)
    
    params = {'alpha':[10000,1000,100, 10, 1.0, 0.1, 0.01,0.001,0.0001]}
    
    grid_search = GridSearchCV(estimator=Model,param_grid=params,n_jobs=-1,verbose=1,scoring='accuracy')
    grid_search.fit(X_train,y_train)
    
    Model_best = grid_search.best_estimator_
    
    y_train_pred = Model_best.predict(X_train)
    y_test_pred = Model_best.predict(X_test)
    
    print('Train Accuracy :',accuracy_score(y_train,y_train_pred))
    print('Test Accuracy :',accuracy_score(y_test,y_test_pred))
    
    Feature_Coefficients['Feature'] = X_train.columns
    Feature_Coefficients[Stress_Levels[i]] = Model_best.coef_[0]

Feature_Coefficients.set_index('Feature',inplace=True)
Feature_Coefficients.head(10)

plt.figure(figsize=(10,6))
sns.heatmap(Feature_Coefficients,annot=True)
plt.title('Heatmap of Feature Coefficients')
plt.show()

"""#With the feature coefficients for all the various stress levels. This analysis is useful for understanding feature and stress level relationship. """

from scipy import stats
df[["sr2","rr","t","lm"]].describe()
ttest,pval1 = stats.ttest_rel(df['sr2'], df['rr'], df['t'], df['lm'])
print(pval1)
if pval1<0.05:
    print("reject null hypothesis")
else:
    print("accept null hypothesis")

df[["sr2","rr","t","lm"]].describe()
ttest,pval2 = stats.ttest_rel(df['bo'], df['rem'], df['sr'], df['hr'])
print(pval2)
if pval2<0.05:
    print("reject null hypothesis")
else:
    print("accept null hypothesis")

df.drop_duplicates(inplace=True)
df.shape

df.rename(columns = {'sr2' : 'snoring range' ,'sr':'snoring rate', 'rr':'respiration rate',
                        't':'body temperature', 'lm':'limb movement', 
                        'bo':'blood oxygen', 'rem':'eye movement', 
                        'sr.1':'sleeping hours','hr':'heart rate', 
                        'sl':'stress level'}, inplace = True)
df.head()

!pip install lazypredict

pip uninstall scikit-learn -y

pip install scikit-learn==0.23.1

from lazypredict.Supervised import LazyClassifier

y = df.pop('stress level')
X = df

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.2, random_state=42,shuffle=True, stratify=y)

clf = LazyClassifier(verbose=0,predictions=True)
models,predictions = clf.fit(X_train, X_test, y_train, y_test)
models

predictions

from sklearn.metrics import classification_report
for i in predictions.columns.tolist():
    print('\t',i,'\n')
    print(classification_report(y_test, predictions[i]),'\n')

"""Most of the models are giving as overfitting however Decision Tree classifier and ridge classifier are giving acceptable accuracy.

###Checking the Decision Tree
"""

from sklearn import tree


clf1 = tree.DecisionTreeClassifier()
clf2 = clf1.fit(X, y)

tree.plot_tree(clf1)

import graphviz 
dot_data = tree.export_graphviz(clf1, out_file=None) 
graph = graphviz.Source(dot_data) 
graph.render("Sleep_gesture")

asr

"""###Ridge Classifier"""

from sklearn.linear_model import RidgeClassifier

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

x, y = make_classification(n_samples=5000, n_features=10, 
                           n_classes=3, 
                           n_clusters_per_class=1)

xtrain, xtest, ytrain, ytest=train_test_split(x, y, test_size=0.15)

rc = RidgeClassifier()
print(rc)

rc.fit(xtrain, ytrain)
score = rc.score(xtrain, ytrain)
print("Score: ", score)



ypred = rc.predict(xtest)

cm = confusion_matrix(ytest, ypred)
print(cm)

cr = classification_report(ytest, ypred)
print(cr) 


# Iris dataset classification
# x, y = iris.data, iris.target
xtrain, xtest, ytrain, ytest=train_test_split(x, y, test_size=0.15)

rc = RidgeClassifier()
print(rc)

rc.fit(xtrain, ytrain)
score = rc.score(xtrain, ytrain)
print("Score: ", score)

cv_scores = cross_val_score(rc, xtrain, ytrain, cv=10)
# print("CV average score: %.2f" % cv_scores.mean())

ypred = rc.predict(xtest)

cm = confusion_matrix(ytest, ypred)
print(cm)

cr = classification_report(ytest, ypred)
print(cr)