#%% This function requires a refined dataframe and a reference dataframe


import pandas as pd
import recordlinkage as rl
from recordlinkage.preprocessing import clean
import pickle as pkl


class EmailChecking:

    def __init__(self):
        self.email_tags = ['Email Address']

    def transform(self, df_dirty):
        email = df_dirty[self.email_tags].duplicated(keep=False)
        show_duplicated = df_dirty[email]
        return show_duplicated


class AddressLinkage:

    def __init__(self):
        self.output_clean_csv_filename = "cleaned.csv"
        self.affiliation_tags = [
            'Department, Institution (e.g. Psychiatric Genetics, QIMR Berghofer Medical Research Institute)',
        ]
        self.city_tag = ['City (e.g. Brisbane)']
        self.country_tag = ['Country']
        self.zip_code_tag = ['ZIP or Postal Code']
        self.state_province_tag = ['State or Province (if applicable)']
        self.street_tag = ['Street address (e.g. 300 Herston Rd)']

        self.ecm_model = None

    def combine_multi_affiliation(self, df1):


        return

    def cleaning(self, df_dirty):
        affiliation = df_dirty[self.affiliation_tags[0]]
        street = df_dirty[self.street_tag]
        city = df_dirty[self.city_tag]
        zip = df_dirty[self.zip_code_tag]
        state = df_dirty[self.state_province_tag]
        country = df_dirty[self.country_tag]

        df_deparments_and_address = df_dirty.iloc[:, [affiliation, street, city, zip, state, country]]
        df_cleaned0 = df_deparments_and_address.apply(clean, axis=1)
        df_cleaned = pd.concat([df_dirty['Email Address'], df_cleaned0], axis=1)

        return df_cleaned

    def get_ground_truth(self, df1, df2):
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

    def ecm_classifier(self, index, truth):
        ecm = rl.ECMClassifier(binarize=0.67)
        result_ecm = ecm.fit_predict(index)
        a = rl.precision(truth, result_ecm)
        b = rl.recall(truth, result_ecm)
        print("precision = ", a)
        print("recall = ", b)
        return result_ecm

    def get_cluster(self, tuple_list):
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

    def get_longest_affli(self, tuple_list, df):
        df['Reference_department'] = None
        for i in range(len(tuple_list)):
            list1 = []
            for j in range(len(tuple_list[i])):
                sort_list = []
                list1.append(df['Department'][tuple_list[i][j]])

            sort_list = [len(one) for one in list1]
            max_index = tuple_list[i][sort_list.index(max(sort_list))]
            for j in tuple_list[i]:
                longest_str = df['Department'][max_index]
                df1 = df.set_value(j, 'Reference_department', longest_str)
        for i in range(len(df1['Reference_department'])):
            if df1['Reference_department'][i] == None:
                df1['Reference_department'][i] = df1['Department'][i]
        return df1

    # This is the main function, df1 is the open_refined csv file and df2 is the reference csv file.
    def address_linkage(self, df1, df2):
        # call get_ground_truth
        df_cleaned = self.cleaning(df1)
        ground_truth = self.get_ground_truth(df1=df_cleaned, df2=df2)

        new_ground_truth = [(t[1], t[0]) for t in ground_truth]
        ground_multi = pd.MultiIndex.from_tuples(new_ground_truth)

        # rename columns
        # df1.columns = ['domain name', 'department', 'street', 'city', 'zip', 'state', 'country']

        # index and check

        column_names = ['Street', 'City', 'Zip', 'Country']
        df_cleaned2 = df_cleaned
        df_cleaned = df_cleaned[['Street', 'City', 'Zip', 'Country']]
        df_cleaned1 = df_cleaned.sort_values(by=['Country', 'City'])
        indexer = rl.Index()

        indexer.block(left_on=['Country', 'City'])
        c = indexer.index(df_cleaned1)

        # compare record

        compare_cl = rl.Compare()
        for column_name in column_names:
            compare_cl.string(column_name, column_name, 'jarowinkler')
        pair_scoring = compare_cl.compute(c, df1, df1)
        pair_scoring_light = pair_scoring.iloc[:, [0, 2]]

        # use ecm_classifier

        result_ecm = self.ecm_classifier(pair_scoring_light, ground_multi)
        self.ecm_model = result_ecm

        return
        # gather the same affiliation together

        cluster = self.get_cluster(result_ecm)
        # reference_cluster = get_cluster(ground_multi)

        # get the longest affiliation if ecm classifier tests them as the same departments.

        df_address_reference_long = self.get_longest_affiliation_index(cluster, df_cleaned2)
        df_address_reference = df_address_reference_long[['Department', 'Reference_department']]
        return df_address_reference


if __name__ == '__main__':
    df_dirty = pd.read_csv("authors-csv-refine.csv")
    df_reference = pd.read_csv("reference.csv")

    linkage = AddressLinkage()
    linkage.address_linkage(df_dirty, df_reference)
    with open("address_record_linkage.pkl", "wb") as f:
        pkl.dump(linkage.ecm_model, f)
