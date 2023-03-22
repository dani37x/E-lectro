import sklearn
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

import pickle

df = pd.read_excel('electro.xlsx')
df_binary = df[['category', 'price', 'user_type']]
df_binary.columns = ['category', 'price', 'user type']

print(df_binary.head())
print(df_binary.info())
print(df_binary.describe().T)

df_binary['category'] = df_binary['category'].replace('TOYS', 1).replace('AGD', 2)
print(df_binary.describe().T)

sns.pairplot(df_binary)

X = df_binary[['category','price']]
y = df_binary['user type']

X_train, X_test, y_train, y_test = train_test_split(
    X, 
    y, 
    test_size = 0.2, 
    random_state=10, 
    shuffle=True
)

classifier = RandomForestClassifier(n_estimators=3, max_depth=2, random_state=10)
classifier.fit(X_train.values, y_train)

print(classifier.predict([[2,1800]]))

y_pred = classifier.predict(X_test.values)
print('Accuracy: %.3f' % accuracy_score(y_test, y_pred))
print(classifier.score(X.values,y))


for estaminator in classifier.estimators_:     

    feature_names = np.array(X)
    class_names = np.array(y)

    fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (4,4), dpi=900)
    tree.plot_tree(
        estaminator,
        feature_names=feature_names, 
        class_names=class_names,
        filled=True,
        rounded=True
    )
    plt.show()

pickle.dump(classifier, open("classifier.pkl", "wb"))