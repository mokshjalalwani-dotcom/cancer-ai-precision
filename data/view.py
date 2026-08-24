import pandas as pd

df = pd.read_csv(
    "B:\\desktop\\Projects\\cancerP2\\data\\final_cancer_dataset.tsv",
    sep="\t",
    nrows=10
)

print(df.shape)
print(df.head())