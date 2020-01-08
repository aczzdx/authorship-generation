import pandas as pd

df = pd.read_csv("../data/authors.csv")
from generate_docx import InitialsGenerator

initial = InitialsGenerator()
result_test = initial.transform(df)
print(result_test)
