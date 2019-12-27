#%% import numpy and set seed

import numpy as np
np.random.seed(575537)

#%% imports and preload database

import pandas as pd
import sklearn
import spacy
from sklearn.base import TransformerMixin

nlp = spacy.load("en_core_web_sm")

#%% Get ground truth

df = pd.read_csv("joined.csv")
#%% get disclosures

disclosures = df['Funding Acknowledgements_before']
real_has_disclosures = ~(df['Formatted_Funding Acknowledgements'].isna())

#%% tokenizer using spacy
from spacy.lang.en import English
import string
parser = English()
punctuation = string.punctuation


def spacy_tokenizer(sentence):

    tokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in parser(sentence)]
    tokens = [token for token in tokens if not (token in punctuation)]

    return tokens

#%% tf-idf

from sklearn.feature_extraction.text import TfidfVectorizer

tf_idf_vectorizer = TfidfVectorizer(tokenizer=spacy_tokenizer)

#%% generate labels
label0 = [i for i in range(len(real_has_disclosures)) if not real_has_disclosures[i]]
label1 = [i for i in range(len(real_has_disclosures)) if real_has_disclosures[i]]

print("# of authors having disclosures: {}".format(len(label1)))
print("# of authors not having disclosures: {}".format(len(label0)))
print("# of authors: {}".format(len(df)))

#%% Split the dataset with train-valid-test
from sklearn.model_selection import train_test_split

X_string = disclosures
Y = [0 if i in label0 else 1 for i in range(len(X_string))]

X_train, X_test, y_train, y_test = train_test_split(X_string, Y, test_size=0.5, stratify=Y)


#%% imputing the missing value

from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy="constant", fill_value="N/A")


class StringCleaner(TransformerMixin):

    def transform(self, X, **transform_params):
        return ["None" if type(s) is not str else s for s in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}


#%% build up a pipeline in sklearn


from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

classifier = LogisticRegression()
tf_idf_vectorizer = TfidfVectorizer(tokenizer=spacy_tokenizer)

pipeline = Pipeline([
    ('imputer', StringCleaner()),
    ('vectorizer', tf_idf_vectorizer),
    ('classifier', classifier)
])

#%% rock and roll

pipeline.fit(X_train, y_train)


#%% sample prediction
from sklearn import  metrics


def generate_evaluation_report(pipeline, X_test=X_test, y_test=y_test):
    predicted = pipeline.predict(X_test)
    print("Logistic Regression Accuracy:", metrics.accuracy_score(y_test, predicted))
    print("Logistic Regression Precision:", metrics.precision_score(y_test, predicted))
    print("Logistic Regression Recall:", metrics.recall_score(y_test, predicted))
    print(metrics.classification_report(y_test, predicted, digits=4))


generate_evaluation_report(pipeline)

#%% Print out mis-classified in the test case
import pickle as pkl
with open("models/funding_classifier.pkl", "wb") as f:
    pkl.dump(pipeline, f)
