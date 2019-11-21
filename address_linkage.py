# This function requires a refined dataframe and a reference dataframe


import pandas as pd
import recordlinkage as rl
from recordlinkage.preprocessing import clean


def get_ground_truth(df1, df2):
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

    return ground_truth


def ecm_classifier(index, truth):
    ecm = rl.ECMClassifier(binarize=0.67)
    result_ecm = ecm.fit_predict(index)
    a = rl.precision(truth, result_ecm)
    b = rl.recall(truth, result_ecm)
    print("precision = ", a)
    print("recall = ", b)
    return result_ecm


def get_cluster(tuple_list):
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


def get_longest_affli(tuple_list, df):
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
            df1 = df.set_value(j, 'reference_department', longest_str)
    for i in range(len(df1['reference_department'])):
        if df1['reference_department'][i] == None:
            df1['reference_department'][i] = df1['department'][i]
    return df1


# This is the main function
def address_linkage(df1, df2):
    # call get_ground_truth

    ground_truth = get_ground_truth(df1=df1, df2=df2)

    new_ground_truth = [(t[1], t[0]) for t in ground_truth]
    ground_multi = pd.MultiIndex.from_tuples(new_ground_truth)

    # rename columns
    df1.columns = ['domain name', 'department', 'street', 'city', 'zip', 'state', 'country']

    # index and check

    column_names = ['street', 'city', 'zip', 'country']
    df_cleaned2 = df1
    df1 = df1[['street', 'city', 'zip', 'country']]
    df_cleaned1 = df1.sort_values(by=['country', 'city'])
    indexer = rl.Index()

    indexer.block(left_on=['country', 'city'])
    c = indexer.index(df_cleaned1)

    # compare record

    compare_cl = rl.Compare()
    for column_name in column_names:
        compare_cl.string(column_name, column_name, 'jarowinkler')
    pair_scoring = compare_cl.compute(c, df1, df1)
    pair_scoring_light = pair_scoring.iloc[:, [0, 2]]

    # use ecm_classifier

    result_ecm = ecm_classifier(pair_scoring_light, ground_multi)

    # gather the same affiliation together

    cluster = get_cluster(result_ecm)
    reference_cluster = get_cluster(ground_multi)

    # get the longest affiliation if ecm classifier tests them as the same departments.

    df_address_reference_long = get_longest_affli(cluster, df_cleaned2)
    df_address_reference = df_address_reference_long[['department','reference_department']]
    return df_address_reference


# call function

df1 = pd.read_csv("authors-csv-refine.csv")
df_reference = pd.read_csv("reference.csv")

df_deparments_and_address = df1.iloc[:, [7, 8, 9, 10, 11, 12]]

df_cleaned0 = df_deparments_and_address.apply(clean, axis=1)
df_cleaned = pd.concat([df1['Email Address'],df_cleaned0],axis=1)
df_address_reference = address_linkage(df1=df_cleaned, df2=df_reference)


