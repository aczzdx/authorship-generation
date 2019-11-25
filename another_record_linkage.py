from typing import List, Tuple

import pandas as pd
import recordlinkage as rl
import recordlinkage.preprocessing

REFERENCE_TAG = 'reference_department'


class AddressLinkage:

    def __init__(self) -> None:
        self.address_tag = "street"
        self.department_tag = "department"
        self.city_tag = "city"
        self.country_tag = "country"
        self.zip_tag = "zip"

        # load the pre-trained model
        import pickle as pkl

        with open("ecm.model.pkl", "rb") as f:
            self.ecm = pkl.load(f)

    @property
    def tags(self):
        return [self.department_tag,
                self.address_tag, self.city_tag, self.zip_tag,
                self.country_tag]

    @staticmethod
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

    def get_longest_affiliation_index(self, tuple_list: List[Tuple[int, int]],
                                      df: pd.DataFrame):
        df[REFERENCE_TAG] = None
        for i in range(len(tuple_list)):
            list1 = []
            for j in range(len(tuple_list[i])):
                sort_list = []
                list1.append(df[self.department_tag][tuple_list[i][j]])

            sort_list = [len(one) for one in list1]
            max_index = tuple_list[i][sort_list.index(max(sort_list))]
            for j in tuple_list[i]:
                longest_str = max_index
                # df.set_value(j, REFERENCE_TAG, longest_str)
                # df[j, REFERENCE_TAG] = longest_str
                df.at[j, REFERENCE_TAG] = longest_str

        return df

    def match_with_bloc(self, df: pd.DataFrame):

        departments_and_address = df[self.tags]

        # index by country and city
        indexer = rl.Index()
        indexer.block(left_on=[self.country_tag, self.city_tag])
        c = indexer.index(df)

        # compare score
        compare_cl = rl.Compare()
        for cname in self.tags:
            compare_cl.string(cname, cname, 'jarowinkler')

        pair_scoring = compare_cl.compute(c, df, df)
        pair_scoring = pair_scoring.iloc[:, [0, 1, 3]]

        self.ecm: rl.ECMClassifier
        result_ecm = self.ecm.predict(pair_scoring)

        cluster = self.get_cluster(result_ecm)
        df = self.get_longest_affiliation_index(cluster, df)

        # clear reference
        reference_is_null = df[REFERENCE_TAG].isnull()
        df.loc[reference_is_null, REFERENCE_TAG] = df.loc[reference_is_null].index

        return df


class DepartmentNameNormalizer:

    def __init__(self):
        self.address_column_indices = [
            [7, 8, 9, 10, 12],
            [13, 14, 15, 16, 18]
        ]

    def give_reference(self, df: pd.DataFrame) -> pd.DataFrame:

        self.address_column_indices: List[List[int]]
        self.address_column_indices.sort()

        linker = AddressLinkage()

        # extract only address and mapping
        index_mapping = dict()
        index_mapping_inv = dict()
        num_records = 0
        extracted: List[pd.DataFrame] = []

        for i, indices in enumerate(self.address_column_indices):
            extracted.append(df.iloc[:, indices][~df.iloc[:, indices[0]].isnull()])
            for index in extracted[i].index:
                index_mapping[num_records] = (i, index)
                index_mapping_inv[(i, index)] = num_records
                num_records += 1
            extracted[i].columns = linker.tags

        df_all = pd.concat(extracted, axis=0, ignore_index=True)
        df_all.apply(recordlinkage.preprocessing.clean, axis=1)

        # record linkage

        df_all_with_reference = linker.match_with_bloc(df_all)

        # merge back
        for i, indices in enumerate(self.address_column_indices):
            column_to_add: pd.Series = df.iloc[:, indices[0]].copy()
            for index in column_to_add.index:
                if (i, index) in index_mapping_inv:
                    mapped_i = index_mapping_inv[(i, index)]
                    if df_all_with_reference.loc[mapped_i, REFERENCE_TAG] is not None:
                        referred_i, referred_index = index_mapping[df_all_with_reference.loc[mapped_i, REFERENCE_TAG]]
                        column_to_add.at[index] = df.iloc[referred_index, self.address_column_indices[referred_i][0]]

            df.insert(self.address_column_indices[i][0] + i + 1,
                      'Reference Affiliation Name %d' % (i + 1),
                      column_to_add)

        return df


if __name__ == '__main__':
    df1 = pd.read_csv("authors-csv-refine.csv")
    normalizer = DepartmentNameNormalizer()
    df_referred = normalizer.give_reference(df1)

    df_referred.to_csv("another_test.csv")
