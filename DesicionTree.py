import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle


df = pd.read_excel('D:\projekty\E-lectro\electro.xlsx')

df_binary = df[['category', 'price', 'user_type']]
df_binary.columns = ['category', 'price', 'user type']

X = df_binary[['category','price']]
y = df_binary['user type']

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size = 0.3,
    random_state=20,
    shuffle=True
)

classifier = RandomForestClassifier()
classifier.fit(X_train.values, y_train)

# print(classifier.predict([[1,1800]]))


#save to file
pickle.dump(classifier, open("classifier.pkl", "wb"))




#open in different file

model = pickle.load(open(CLASSIFIER, "rb"))

prediction = model.predict([[1, 900]])



