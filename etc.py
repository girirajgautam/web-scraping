import pandas as pd

df = pd.read_excel("main2.xlsx")
df.to_csv("main2.csv", index=False)