from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
# import matplotlib.pyplot as plt

def startML(query,pred, bind):
    dfOrig = pd.read_sql(query,bind)
    dfPred = pd.read_sql(pred, bind)
    preprocessData(dfOrig)
    preprocessData(dfPred)
    prediccion = applySVM(dfOrig, dfPred)
    result = generatePrediccionList(dfPred,prediccion)
    return result

def preprocessData(dataframe):
    le = preprocessing.LabelEncoder()
    for column_name in dataframe.columns:
        if dataframe[column_name].dtype == object:
            dataframe[column_name] = le.fit_transform(dataframe[column_name])
        else:
            pass
    return dataframe

def applySVM(dataframe, dfPrediction):
    X = dataframe.drop(['fk_grupo_metabolico', 'batch'], axis=1)
    y = dataframe['fk_grupo_metabolico']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=4)
    clf = svm.SVC(gamma='auto',kernel='linear', C=1.0)
    clf.fit(X_train, y_train)
    P = dfPrediction.drop(['fk_grupo_metabolico', 'batch'], axis=1)
    return clf.predict(P)

def generatePrediccionList(data, prediccion):
    dictPrediccion = {}
    i = 0
    for key, row in data.iterrows():
        dictPrediccion[row[0]] =prediccion[i]
        i = i + 1
    return dictPrediccion
