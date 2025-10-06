import os
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

cwd: str = os.getcwd()

_ = st.title("Bebras Dashboard")
tab_correlation, tab_average = st.tabs(["Correlation", "Average"])

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
    st.pyplot(fig)


with tab_average:
    _ = st.subheader("Perbandingan Nilai Rata-rata per Pertanyaan dan Bahasa")

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
    if chosen_year == "2020":
        en_file: str = os.path.join(cwd, "data", chosen_year, chosen_category, "en", "challenge.csv")
        id_file: str = os.path.join(cwd, "data", chosen_year, chosen_category, "id", "challenge.csv")

        en_df = pd.read_csv(en_file)
        id_df = pd.read_csv(id_file)
    else:
        en_file: str = os.path.join(cwd, "data", chosen_year, chosen_category, "en", "combined_grades_and_makeup.csv")
        id_file: str = os.path.join(cwd, "data", chosen_year, chosen_category, "id", "combined_grades_and_makeup.csv")

        if not os.path.isfile(en_file):
            en_file = os.path.join(cwd, "data", chosen_year, chosen_category, "en", "grades.csv")

        if not os.path.isfile(id_file):
            id_file = os.path.join(cwd, "data", chosen_year, chosen_category, "id", "grades.csv")

        en_df = pd.read_csv(en_file)
        id_df = pd.read_csv(id_file)

    en_mean = pd.DataFrame(en_df.iloc[:, 6:].replace("-", "0").apply(pd.to_numeric, errors='coerce').corr(method="pearson").mean()).reset_index()
    id_mean = pd.DataFrame(id_df.iloc[:, 6:].replace("-", "0").apply(pd.to_numeric, errors='coerce').corr(method="pearson").mean()).reset_index()


    en_mean.columns = ["Question", "Mean"]
    en_mean["Language"] = "English"

    id_mean.columns = ["Question", "Mean"]
    id_mean["Language"] = "Indonesian"

    summary_df = pd.concat([en_mean, id_mean], ignore_index=True)

    fig, ax = plt.subplots(figsize=(18, 8))
    sns.barplot(
        data=summary_df,
        x="Question",
        y="Mean",
        hue="Language",
        palette="Set2",
        ax=ax,
        errorbar=None
    )
    _ = ax.set_title(f"Mean per question ({chosen_category}, {chosen_year})")
    _ = ax.set_xlabel("Soal")
    _ = ax.set_ylabel("Rata-rata nilai")
    _ = ax.legend(title="Bahasa")
    _ = st.pyplot(fig)
