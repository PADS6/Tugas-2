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


st.divider()
st.subheader("Perbandingan Nilai Rata-rata per Pertanyaan dan Bahasa")
chosen_year2: str = st.selectbox(
    "Choose the year",
    next(os.walk(os.path.join(cwd, "data")))[1],
    key="selectbox_2"
)
chosen_category2: str = st.selectbox(
    "Choose the category",
    next(os.walk(os.path.join(cwd, "data", chosen_year2)))[1],
    key="selectbox_3"
)
folder_utama=os.path.join(cwd, "data", chosen_year2, chosen_category2)
records=[]

for languange in os.listdir(folder_utama):
    folder_bahasa=os.path.join(folder_utama, languange)
    for file_name in os.listdir(folder_bahasa):
        if chosen_year2=="2020":
            if file_name=="challenge.csv" :
                file_path=os.path.join(folder_bahasa, file_name)
                df= pd.read_csv(file_path)
                question_cols=df.columns[6:]
                for i, col in enumerate(question_cols, start=1):
                    df[col]=pd.to_numeric(df[col], errors="coerce")
                    mean_grade=df[col].mean(skipna=True)
                    records.append({
                        "Category": chosen_category2,
                        "Languange": languange,
                        "Question": f"Q{i}",
                        "Average_grade": mean_grade
                    })
        else:
            if file_name=="grades.csv" :
                file_path=os.path.join(folder_bahasa, file_name)
                df= pd.read_csv(file_path)
                question_cols=df.columns[6:]
                for i, col in enumerate(question_cols, start=1):
                    df[col]=pd.to_numeric(df[col], errors="coerce")
                    mean_grade=df[col].mean(skipna=True)
                    records.append({
                        "Category": chosen_category2,
                        "Languange": languange,
                        "Question": f"Q{i}",
                        "Average_grade": mean_grade
                    })
#buat data_frame
summary_df=pd.DataFrame(records)
st.dataframe(summary_df)
#visualisasi 
fig, ax= plt.subplots(figsize=(8,5))
sns.barplot(
    data=summary_df,
    x="Question",
    y="Average_grade",
    hue="Languange",
    palette="Set2",
    ax=ax,
    errorbar=None
)
ax.set_title("Rata-rata nilai per soal ({chosen_category2}), {chosen_year2}")
ax.set_xlabel("Soal")
ax.set_ylabel("Rata-rata nilai")
ax.legend(title="Bahasa")
st.pyplot(fig)

