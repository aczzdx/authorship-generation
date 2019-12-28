from unittest import TestCase
from statement_classifier import ClassifierWrapper
import pickle as pkl


class TestDisclosureClassifierWrapper(TestCase):

    def test_model_persistence(self):

        model_names = [
            "../models/disclosure_classifier.pkl",
            "../models/funding_classifier.pkl"
        ]

        for name in model_names:
            with self.subTest(name=name):
                with open(name, "rb") as f:
                    classifier = pkl.load(f)

                self.assertIsInstance(classifier, ClassifierWrapper)
                pipeline = classifier.pipeline
                prediction = pipeline.predict(["None", "I work for ABC Company"])

                print(prediction)

