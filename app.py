import os
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

_ = st.title("Bebras Dashboard")

_ = st.header("Correlation")
cwd = os.getcwd()

chosen_year: str = st.selectbox(
    "Choose the year",
    next(os.walk(os.path.join(cwd, "data")))[1]
)

chosen_category: str = st.selectbox(
    "Choose the category",
    next(os.walk(os.path.join(cwd, "data", chosen_year)))[1]
)

chosen_language: str = st.selectbox(
    "Choose the language",
    next(os.walk(os.path.join(cwd, "data", chosen_year, chosen_category)))[1]
)

chosen_set: str = st.selectbox(
    "Choose the question set",
    next(os.walk(os.path.join(cwd, "data", chosen_year, chosen_category, chosen_language)))[2]
)

# file_suffix = os.path.join(cwd, "data", chosen_year, chosen_category)
# en_file = os.path.join(file_suffix, "en", chosen_set) + ".csv"
# id_file = os.path.join(file_suffix, "id", chosen_set) + ".csv"
# en_df = pd.read_csv(en_file)
# id_df = pd.read_csv(id_file)
# df = pd.concat([en_df, id_df], ignore_index=True)
df: pd.DataFrame = pd.read_csv(os.path.join(cwd, "data", chosen_year, chosen_category, chosen_language, chosen_set))

correlation_df = df.iloc[:, 6:].replace("-", "0").apply(pd.to_numeric, errors='coerce').corr(method="pearson")

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(correlation_df, annot=True, cmap='coolwarm', center=0, ax=ax);
ax.set_title("Pearson Correlation Heatmap")
st.pyplot(fig)
