import os
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.stats.proportion import proportions_ztest

cwd: str = os.getcwd()

_ = st.title("Bebras Dashboard")
tab_correlation, tab_proportion = st.tabs(["Correlation", "Proportion"])

def score_to_bool(score: float) -> bool: 
    return score > 0

with tab_correlation:
    _ = st.subheader("Correlation")

    chosen_year: str = st.selectbox(
        "Choose the year",
        next(os.walk(os.path.join(cwd, "data")))[1],
        key="selectbox_1"
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

    df: pd.DataFrame = pd.read_csv(os.path.join(cwd, "data", chosen_year, chosen_category, chosen_language, chosen_set))

    correlation_df: pd.DataFrame = df.iloc[:, 6:].replace("-", "0").apply(pd.to_numeric, errors='coerce').corr(method="pearson")

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(correlation_df, annot=True, cmap='coolwarm', center=0, ax=ax);
    ax.set_title(f"Pearson Correlation Heatmap ({chosen_category}, {chosen_year}, {chosen_language})")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha='center')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, ha='right')
    st.pyplot(fig)


with tab_proportion:
    _ = st.subheader("Proportion of Correct Answers")

    chosen_year: str = st.selectbox(
        "Choose the year",
        next(os.walk(os.path.join(cwd, "data")))[1],
        key="y2"
    )

    chosen_category: str = st.selectbox(
        "Choose the category",
        next(os.walk(os.path.join(cwd, "data", chosen_year)))[1],
        key="c2"
    )

    folder_utama: str = os.path.join(cwd, "data", chosen_year, chosen_category)
    records = []

    en_df: pd.DataFrame
    id_df: pd.DataFrame
    en_file: str
    id_file: str
    if chosen_year == "2020":
        en_file: str = os.path.join(cwd, "data", chosen_year, chosen_category, "en", "challenge.csv")
        id_file: str = os.path.join(cwd, "data", chosen_year, chosen_category, "id", "challenge.csv")
    else:
        en_file: str = os.path.join(cwd, "data", chosen_year, chosen_category, "en", "combined_grades_and_makeup.csv")
        id_file: str = os.path.join(cwd, "data", chosen_year, chosen_category, "id", "combined_grades_and_makeup.csv")


        if not os.path.isfile(en_file):
            en_file = os.path.join(cwd, "data", chosen_year, chosen_category, "en", "grades.csv")

        if not os.path.isfile(id_file):
            id_file = os.path.join(cwd, "data", chosen_year, chosen_category, "id", "grades.csv")

    en_df = pd.read_csv(en_file).iloc[:, 6:].replace("-", "0").apply(pd.to_numeric, errors='coerce').map(score_to_bool)
    id_df = pd.read_csv(id_file).iloc[:, 6:].replace("-", "0").apply(pd.to_numeric, errors='coerce').map(score_to_bool)

    en_proportion = pd.DataFrame(en_df.mean()).reset_index()
    id_proportion = pd.DataFrame(id_df.mean()).reset_index()

    en_proportion.columns = ["Question", "Proportion"]
    en_proportion["Language"] = "English"

    id_proportion.columns = ["Question", "Proportion"]
    id_proportion["Language"] = "Indonesian"

    summary_df = pd.concat([en_proportion, id_proportion], ignore_index=True)

    fig, ax = plt.subplots(figsize=(18, 8))
    _ = sns.barplot(
        data=summary_df,
        x="Question",
        y="Proportion",
        hue="Language",
        palette="Set2",
        ax=ax,
        errorbar=None
    )
    _ = ax.set_ylim(0, 1)
    _ = ax.set_title(f"Proportion of Correct Answers per Question ({chosen_category}, {chosen_year})")
    _ = ax.set_xlabel("Question")
    _ = ax.set_ylabel("Proportion of Correct Answers")
    _ = ax.legend(title="Language")

    en_n = len(en_df)
    id_n = len(id_df)

    ztest_results = []

    for q in en_df.columns:
        count = [en_df[q].sum(), id_df[q].sum()]
        nobs = [en_n, id_n]

        zstat, p_value = proportions_ztest(count, nobs)

        ztest_results.append({
            "Question": q,
            "Z statistic": zstat,
            "P-Value": p_value,
            "Significant": "Yes" if p_value <= 0.05 else "No",
            "ID len": id_n,
            "EN len": en_n,
        })

    _ = st.pyplot(fig)
    _ = st.divider()
    _ = st.subheader("Significance Test (Proportion Z-test)")
    _ = st.dataframe(pd.DataFrame(ztest_results))
