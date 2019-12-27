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

df = pd.read_csv("data/coi_samples.csv")

#%% get disclosures

has_disclosures = df['HasCOI']



#%% Prepossessing for tokenizing the data (using the first sentence)
doc = nlp(df['Text'][0])
print([token.orth_ for token in doc if not (token.is_punct or token.is_space)])
print([word.lemma_ for word in doc])

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
label0 = [i for i in range(len(has_disclosures)) if not has_disclosures[i]]
label1 = [i for i in range(len(has_disclosures)) if has_disclosures[i]]

print("# of authors having disclosures: {}".format(len(label1)))
print("# of authors not having disclosures: {}".format(len(label0)))
print("# of authors: {}".format(len(df)))

#%% Split the dataset with train-valid-test
from sklearn.model_selection import train_test_split

X_string = df['Text']
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
with open("models/disclosure_classifier.pkl", "wb") as f:
    pkl.dump(pipeline, f)


#%% Discarded oversampling result
# #%% Experiment on Oversampling the entries with COI
# from imblearn.over_sampling import RandomOverSampler
# import numpy as np
#
# resampler = RandomOverSampler()
# X_cleaned = StringCleaner().fit_transform(X_train, y_train)
# X_resampled, y_resampled = resampler.fit_resample(X=np.asarray(X_cleaned).reshape((-1, 1)),
#                                                   y=y_train)
#


# #%% Experiment on pipeline with oversampling
# from sklearn.pipeline import make_pipeline
#
# pipeline_oversampled = make_pipeline(
#     StringCleaner(),
#     TfidfVectorizer(tokenizer=spacy_tokenizer),
#     LogisticRegression()
# )
#
# pipeline_oversampled.fit(pd.Series(X_resampled.reshape(-1)), pd.Series(y_resampled.reshape(-1)))
#
# #%% evaluation
# generate_evaluation_report(pipeline_oversampled)
#
# #%% get vectorized data before augmentation
#
# part_pipeline_vectorized = make_pipeline(
#     StringCleaner(),
#     TfidfVectorizer(tokenizer=spacy_tokenizer)
# )
#
# part_classifier = LogisticRegression()
#
# #%%
# X_train_vectorized = part_pipeline_vectorized.fit_transform(X_train, y_train)
#
# #%%
# from imblearn.over_sampling import ADASYN
# resampler_adasyn = ADASYN()
# X_train_vectorized_resampled, y_train_vectorized_resampled = resampler_adasyn.fit_resample(X_train_vectorized, y_train)
#
# #%%
# part_classifier.fit(X_train_vectorized_resampled, y_train_vectorized_resampled)
#
# #%%
# combined_pipeline = make_pipeline(part_pipeline_vectorized, part_classifier)
#
# #%%
# generate_evaluation_report(combined_pipeline, X_test, y_test)