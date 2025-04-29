import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title('📚 Student Interaction Dashboard')

uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Show raw data and column headers for verification
    st.write("### Raw Data", df)
    st.write("### Detected Columns:", df.columns.tolist())

    try:
        # Hardcoded column names based on your uploaded file
        student_col = 'Student'
        course_col = 'Course'
        group_col = 'Group'

        students = sorted(set(df[student_col].unique()))
        interaction_matrix = pd.DataFrame(0, index=students, columns=students)

        with st.spinner('Processing interactions...'):
            for course in df[course_col].unique():
                course_data = df[df[course_col] == course]
                for group in course_data[group_col].dropna().unique():
                    members = course_data[course_data[group_col] == group][student_col].tolist()
                    for i in range(len(members)):
                        for j in range(i+1, len(members)):
                            interaction_matrix.loc[members[i], members[j]] += 1
                            interaction_matrix.loc[members[j], members[i]] += 1

        st.write("### 🧮 Interaction Matrix", interaction_matrix)

        st.write("### 🔥 Heatmap of Interactions")
        plt.figure(figsize=(12, 10))
        sns.heatmap(interaction_matrix, cmap="YlGnBu", annot=False)
        st.pyplot(plt.gcf())
        plt.clf()

        st.write("### 📈 Total Interactions per Student")
        total_interactions = interaction_matrix.sum(axis=1).sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(12,6))
        total_interactions.plot(kind='bar', ax=ax)
        plt.ylabel('Total Interactions')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

        st.download_button(
            label="📥 Download Interaction Matrix CSV",
            data=interaction_matrix.to_csv().encode('utf-8'),
            file_name='interaction_matrix.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
else:
    st.info("👆 Please upload a CSV file to get started!")
