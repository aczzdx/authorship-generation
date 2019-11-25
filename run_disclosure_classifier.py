#%%
from sklearn.base import TransformerMixin


class StringCleaner(TransformerMixin):

    def transform(self, X, **transform_params):
        return ["None" if type(s) is not str else s for s in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}

#%%

from spacy.lang.en import English
import string
parser = English()
punctuation = string.punctuation


def spacy_tokenizer(sentence):

    tokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in parser(sentence)]
    tokens = [token for token in tokens if not (token in punctuation)]

    return tokens


#%%
import pickle as pkl
with open("disclosure_classifier.pkl", "rb") as f:
    pipline = pkl.load(f)

#%% sample code for extracting csv
import pandas as pd
df = pd.read_csv("authors.csv")
coi_text = df["Conflict of Interest/Disclosures"]
has_coi = pipline.predict_proba(coi_text)

#%%
df_out = pd.DataFrame()
df_out['has_coi'] = has_coi[:, 1]
df_out['text'] = coi_text

df_out.to_csv("coi_test_result.csv")



