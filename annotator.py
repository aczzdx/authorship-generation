# %%
from sklearn.base import TransformerMixin


class StringCleaner(TransformerMixin):

    def transform(self, X, **transform_params):
        return ["None" if type(s) is not str else s for s in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}


# %%

from spacy.lang.en import English
import string

parser = English()
punctuation = string.punctuation


def spacy_tokenizer(sentence):
    tokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in parser(sentence)]
    tokens = [token for token in tokens if not (token in punctuation)]

    return tokens




# %% sample code for extracting csv
import pandas as pd

def add_coi_and_funding_prediction(df: pd.DataFrame, coi_tag, funding_tag) -> pd.DataFrame:
    # %%
    import pickle as pkl

    with open("disclosure_classifier.pkl", "rb") as f:
        coi_pipeline = pkl.load(f)

    with open("coi_identification_model.pkl", "rb") as f:
        funding_pipeline = pkl.load(f)
    # df = pd.read_csv("authors.csv")
    coi_text = df[coi_tag]
    has_coi = coi_pipeline.predict_proba(coi_text)
    df['has_coi Probability'] = has_coi[:, 1]

    funding_text = df[funding_tag]
    has_funding = funding_pipeline.predict_proba(funding_text)
    df['has_funding Probability'] = has_funding[:, 1]

    return df
