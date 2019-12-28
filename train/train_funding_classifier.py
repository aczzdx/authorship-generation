if __name__ == '__main__':
    import pickle as pkl
    from disclosure_classifier import ClassifierWrapper
    import pandas as pd

    pipeline = ClassifierWrapper()

    df = pd.read_csv("../data/joined.csv")
    funding_statement = df['Funding Acknowledgements_before']
    has_funding = ~(df['Formatted_Funding Acknowledgements'].isna())

    pipeline.train_pipeline(funding_statement, has_funding)

    with open("../models/funding_classifier.pkl", "wb") as f:
        pkl.dump(pipeline, f)
