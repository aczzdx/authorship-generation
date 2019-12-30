if __name__ == '__main__':
    import pickle as pkl
    from statement_classifier import ClassifierWrapper
    import pandas as pd

    pipeline = ClassifierWrapper()

    # Preprocessing
    df = pd.read_csv("../data/coi_samples.csv")
    labels = df['HasCOI']

    # Get ground truth
    label0 = [i for i in range(len(labels)) if not labels[i]]
    label1 = [i for i in range(len(labels)) if labels[i]]

    print("# of authors having disclosures: {}".format(len(label1)))
    print("# of authors not having disclosures: {}".format(len(label0)))
    print("# of authors: {}".format(len(df)))

    X_string = df['Text']
    Y = [0 if i in label0 else 1 for i in range(len(X_string))]

    pipeline.train_pipeline(X_string, Y)

    with open("../models/disclosure_classifier.pkl", "wb") as f:
        pkl.dump(pipeline, f)
