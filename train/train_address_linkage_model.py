# %%
import pandas as pd
import numpy as np
import recordlinkage as rl
from recordlinkage.preprocessing import clean
from pathlib import Path
import matplotlib.pyplot as plt
import math
import re
import sklearn

# %% Get ground truth list

df1 = pd.read_csv("../data/authors-csv-refine.csv")
df2 = pd.read_csv("../data/reference.csv")

name = np.nan
for tag in ['Email Address']:
    df1[tag] = df1[tag].apply(lambda name: name.strip() if not pd.isnull(name) else name)
    df2[tag] = df2[tag].apply(lambda name: name.strip() if not pd.isnull(name) else name)
df1.columns = df1.columns + '_before'
df_combine = df1.merge(df2, how='left', left_on='Email Address_before', right_on='Email Address')
df_combine.duplicated()
ground_truth = []
df_aff = df_combine['Affiliation 1 Department, Institution']
for i in range(len(df_aff)):
    j = i + 1
    while j <= len(df_aff) - 1:
        if df_aff[i] == df_aff[j]:
            ground_truth.append((i, j))
        j = j + 1

df_deparments_and_address = df1.iloc[:, [1, 7, 8, 9, 10, 11, 12]]

df_deparments_and_address['Email Address_before'] = df_deparments_and_address['Email Address_before'].apply(
    lambda email: email.split("@")[1].split(".")[0])

df_cleaned = df_deparments_and_address.apply(clean, axis=1)
df_cleaned.columns = ['domain name', 'department', 'street', 'city', 'zip', 'state', 'country']

# index and check
column_names = ['department', 'street', 'city', 'zip', 'country']
df_cleaned2 = df_cleaned
df_cleaned = df_cleaned[['department', 'street', 'city', 'zip', 'country']]
df_cleaned1 = df_cleaned.sort_values(by=['country', 'city'])
indexer = rl.Index()

indexer.block(left_on=['country', 'city'])
c = indexer.index(df_cleaned1)

# %%
# compare record
compare_cl = rl.Compare()
for column_name in column_names:
    compare_cl.string(column_name, column_name, 'jarowinkler')
pair_scoring = compare_cl.compute(c, df_cleaned, df_cleaned)
pair_scoring1 = pair_scoring.iloc[:, [0, 1, 3]]
new_ground_truth = [(t[1], t[0]) for t in ground_truth]
ground_multi = pd.MultiIndex.from_tuples(new_ground_truth)
# %%
ecm = rl.ECMClassifier(binarize=0.7)
result_ecm = ecm.fit_predict(pair_scoring1)

a = rl.precision(ground_multi, result_ecm)
b = rl.recall(ground_multi, result_ecm)


# %%


def get_cluster(tuple_list=result_ecm):
    cluster = []
    for i in tuple_list:
        flag = 0
        for j in range(len(cluster)):
            if i[0] in cluster[j]:
                if i[1] not in cluster[j]:
                    cluster[j] = cluster[j] + (i[1],)
                flag = 1
                break
            if i[1] in cluster[j]:
                if i[0] not in cluster[j]:
                    cluster[j] = cluster[j] + (i[0],)
                flag = 1
                break
        if flag == 0:
            cluster.append(i)
    return cluster


cluster = get_cluster(result_ecm)
reference_cluster = get_cluster(ground_multi)


def get_longest_affli(tuple_list=cluster, df=df_cleaned2):
    df['reference_department'] = None
    for i in range(len(tuple_list)):
        list1 = []
        for j in range(len(tuple_list[i])):
            sort_list = []
            list1.append(df['department'][tuple_list[i][j]])

        sort_list = [len(one) for one in list1]
        max_index = tuple_list[i][sort_list.index(max(sort_list))]
        for j in tuple_list[i]:
            longest_str = df['department'][max_index]
            df.set_value(j, 'reference_department', longest_str)


get_longest_affli(cluster, df_cleaned2)

reference = df_cleaned2.to_csv(r'address_reference.csv')

#%% Dumping the ecm model

import pickle as pkl
with open("../models/ecm.model.pkl", "wb") as f:
    pkl.dump(ecm, f)

