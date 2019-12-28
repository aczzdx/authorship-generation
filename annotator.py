import pandas as pd


def add_coi_and_funding_prediction(df: pd.DataFrame, coi_tag: str, funding_tag: str) -> pd.DataFrame:
    """ Append columns of predicting COI and funding back to the data frame
    :param df: The source data frame
    :param coi_tag: The column name for COI (Conflict of Interests)
    :param funding_tag: The column name for funding statement
    :return: The modified data frame
    """
    import pickle as pkl
    from disclosure_classifier import ClassifierWrapper

    with open("models/disclosure_classifier.pkl", "rb") as f:
        coi_pipeline_wrapper: ClassifierWrapper = pkl.load(f)
        coi_pipeline = coi_pipeline_wrapper.pipeline

    with open("models/coi_identification_model.pkl", "rb") as f:
        funding_pipeline_wrapper: ClassifierWrapper = pkl.load(f)
        funding_pipeline = funding_pipeline_wrapper.pipeline

    # df = pd.read_csv("authors.csv")
    coi_text = df[coi_tag]
    has_coi = coi_pipeline.predict_proba(coi_text)
    df['has_coi Probability'] = has_coi[:, 1]

    funding_text = df[funding_tag]
    has_funding = funding_pipeline.predict_proba(funding_text)
    df['has_funding Probability'] = has_funding[:, 1]

    return df
