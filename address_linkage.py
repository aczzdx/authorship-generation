from typing import List, Tuple

import pandas as pd
import recordlinkage as rl
import recordlinkage.preprocessing

REFERENCE_TAG = 'reference_department'


class EmailChecking:
    """Check the duplicate submission by checking the Email

    If there are multiple entries submitted from the same email address,
    they must be duplicated.
    """

    def __init__(self):
        self.email_tags = ['Email Address']

    def transform(self, df_dirty: pd.DataFrame) -> pd.DataFrame:
        """ Extract the rows that having same
        :param df_dirty: The source data frame
        :return: Extracted data frame contains mutliple submission only
        """
        email = df_dirty[self.email_tags].duplicated(keep=False)
        show_duplicated = df_dirty[email]
        return show_duplicated


class AddressLinkage:
    """Link the same address between every co-author.

    Gather the clusters with index of the same address detected by the pre-trained model, and bond
    preferred values(the longest affiliation name) with these clusters.

    Attributes:
        tags: A list with tags defined by user
        get_cluster: A list with tuples insides, indicating authors who have the same affiliations.
        get_longest_affiliation_index: A Pandas.Dataframe with an extra column added, and authors who
            are in clusters are given the reference with the longest affiliation name.
        match_with_bloc: A Pandas.Dataframe with extra column added, the entire authors are filled the
            same as what they have written.
    """
    def __init__(self) -> None:
        """Init Dataframe title tags with address, department, city, country, zip

        :return: None
        """
        self.address_tag = "street"
        self.department_tag = "department"
        self.city_tag = "city"
        self.country_tag = "country"
        self.zip_tag = "zip"

        # load the pre-trained model
        import pickle as pkl

        with open("models/ecm.model.pkl", "rb") as f:
            self.ecm = pkl.load(f)

    @property
    def tags(self) -> List[str]:
        """Reassign titles in Pandas Dataframe"""
        return [self.department_tag,
                self.address_tag, self.city_tag, self.zip_tag,
                self.country_tag]

    @staticmethod
    def get_cluster(tuple_list: List[Tuple[int, int]]) -> List[Tuple]:
        """Cluster authors who have the same affiliations, detected by ECM model

        Gather the same numbers in different tuples(all in a list) and combine those in the same tuples into a
        new one.
        Note that it is a static function.
        :param tuple_list: Record linkage results by ECM classifier
        :return: Re-cluster tuple_list as record linkage results
        """
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

    def get_longest_affiliation_index(self, cluster: List[Tuple],
                                      df: pd.DataFrame) -> pd.DataFrame:
        """Track the longest affiliation name filled by co-authors.
        :param cluster: Re-cluster tuple_list as record linkage results, return value in get_cluster function
        :param df: Dataframe converted by .csv file
        :return: Dataframe added with REFERENCE_TAG column, only writing in cells in param cluster
        """
        df[REFERENCE_TAG] = None
        for i in range(len(cluster)):
            list1 = []
            for j in range(len(cluster[i])):
                list1.append(df[self.department_tag][cluster[i][j]])

            sort_list = [len(one) for one in list1]
            max_index = cluster[i][sort_list.index(max(sort_list))]
            for j in cluster[i]:
                longest_str = max_index
                df.at[j, REFERENCE_TAG] = longest_str

        return df

    def match_with_bloc(self, df: pd.DataFrame) -> pd.DataFrame:
        """Record linkage to all university addresses, and return a Dataframe with reference.

        Main function in class Addresslinkage. Index authors records by country and city,
        compare record with all other authors, and fill the reference column either by the
        longest affiliation names (we assume they are right) or by what they have shown.
        :param df: Dataframe converted by .csv file
        :return: Dataframe added with affiliation reference column, writing in all cells
        """
        indexer = rl.Index()
        indexer.block(left_on=[self.country_tag, self.city_tag])
        c = indexer.index(df)

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
    """Split author who have multiple affiliations and merge back to give reference to all department name.

    Call functions from AddressLinkage and return a Pandas.Dataframe with an extra column, showing all the
    references.

    Attributes:
        give_reference: A Pandas.Dataframe with one more column, giving all the references to be checked by user.

    """
    def __init__(self) -> None:
        """Init Dataframe columns' index to be read"""
        self.address_column_indices = [
            [7, 8, 9, 10, 12],
            [13, 14, 15, 16, 18]
        ]

    def give_reference(self, df: pd.DataFrame) -> pd.DataFrame:
        """Deal with co-authors with two affiliations, split and merge back them fit Class AddressLinkage.

        Main function in Class DepartmentNameNormalizer, extract address and mapping to fit for the format in
        AddressLinkage, then merge back to create the reference column.
        :param df: Dataframe converted by .csv file
        :return: Dataframe with reference in column REFERENCE_TAG
        """
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
        df_to_return = df.copy()
        for i, indices in enumerate(self.address_column_indices):
            column_to_add: pd.Series = df.iloc[:, indices[0]].copy()
            for index in column_to_add.index:
                if (i, index) in index_mapping_inv:
                    mapped_i = index_mapping_inv[(i, index)]
                    if df_all_with_reference.loc[mapped_i, REFERENCE_TAG] is not None:
                        referred_i, referred_index = index_mapping[df_all_with_reference.loc[mapped_i, REFERENCE_TAG]]
                        column_to_add.at[index] = df.iloc[referred_index, self.address_column_indices[referred_i][0]]

            df_to_return.insert(self.address_column_indices[i][0] + i + 1,
                                'Reference Affiliation Name %d' % (i + 1),
                                column_to_add)

        return df_to_return


if __name__ == '__main__':
    df1 = pd.read_csv("data/authors-csv-refine.csv")
    normalizer = DepartmentNameNormalizer()
    df_referred = normalizer.give_reference(df1)

    df_referred.to_csv("another_test.csv")
