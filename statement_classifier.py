import string
from typing import List, Union

import numpy as np
import pandas as pd
import spacy
from sklearn import metrics
from sklearn.base import TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from spacy.lang.en import English
nlp = spacy.load("en_core_web_sm")
parser = English()


class ClassifierWrapper:
    punctuation = string.punctuation
    imputer = SimpleImputer(strategy="constant", fill_value="N/A")

    @property
    def seed(self) -> int:
        """ The random seed for reproducibility"""
        return 575537

    def __init__(self):
        # Setup random seed
        np.random.seed(self.seed)

        # construct all components
        self.tf_idf_vectorizer = TfidfVectorizer(tokenizer=self.tokenize_with_spacy)
        self.classifier = LogisticRegression()
        self.string_cleaner = StringCleaner()

        self.pipeline = Pipeline([
            ('imputer', self.string_cleaner),
            ('vectorizer', self.tf_idf_vectorizer),
            ('classifier', self.classifier)
        ])

    def train_pipeline(self, X: pd.Series, y: Union[pd.Series, List[int]]) -> None:
        """ Train the pipeline

        """

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, stratify=y)
        self.pipeline.fit(X_train, y_train)

        # TODO: print the testing result into logging

    @staticmethod
    def tokenize_with_spacy(sentence: str) -> List[str]:
        """ Use spacy to tokenize the sentence

        :param sentence: the sentence to be tokenize
        :return: a list of tokens
        """
        tokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_
                  for word in parser(sentence)]
        tokens = [token for token in tokens if not (token in ClassifierWrapper.punctuation)]

        return tokens

    def generate_evaluation_report(self, X_test, y_test) -> None:
        """ Generate and print the evaluation report for X_test and y_test in stdout

        :param X_test: The input data for testing.
        :param y_test: The ground truth for X_test
        """
        predicted = self.pipeline.predict(X_test)
        print("Logistic Regression Accuracy:", metrics.accuracy_score(y_test, predicted))
        print("Logistic Regression Precision:", metrics.precision_score(y_test, predicted))
        print("Logistic Regression Recall:", metrics.recall_score(y_test, predicted))
        print(metrics.classification_report(y_test, predicted, digits=4))


class StringCleaner(TransformerMixin):

    def transform(self, X, **transform_params):
        return ["None" if type(s) is not str else s for s in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}


