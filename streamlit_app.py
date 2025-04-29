# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Streamlit UI ---

st.title('📚 Student Interaction Dashboard')

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### 📋 Raw Data", df)
    
    # Show column names to help debug
    st.write("### 📑 Columns in Uploaded File:", df.columns.tolist())
    
    try:
        # --- Try to find the right columns automatically ---
        student_col = [col for col in df.columns if 'student' in col.lower()][0]
        course_col = [col for col in df.columns if 'course' in col.lower()][0]
        group_col = [col for col in df.columns if 'group' in col.lower()][0]

        st.success(f"Detected columns: Student → '{student_col}', Course → '{course_col}', Group → '{group_col}'")
        
        # --- Process Data ---
        students = sorted(set(df[student_col].unique()))
        
        # Initialize interaction matrix
        interaction_matrix = pd.DataFrame(0, index=students, columns=students)

        with st.spinner('Processing interactions...'):
            # Loop through each course
            for course in df[course_col].unique():
                group_data = df[df[course_col] == course]
                groups = group_data[group_col].unique()
                for group in groups:
                    members = group_data[group_data[group_col] == group][student_col].tolist()
                    for i in range(len(members)):
                        for j in range(i+1, len(members)):
                            interaction_matrix.loc[members[i], members[j]] += 1
                            interaction_matrix.loc[members[j], members[i]] += 1  # symmetric

        st.write("### 🧮 Interaction Matrix", interaction_matrix)

        # --- Heatmap ---
        st.write("### 🔥 Heatmap of Interactions")
        plt.figure(figsize=(12, 10))
        sns.heatmap(interaction_matrix, cmap="YlGnBu", annot=False)
        st.pyplot(plt.gcf())
        plt.clf()

        # --- Total interactions per student ---
        st.write("### 📈 Total Interactions per Student")
        total_interactions = interaction_matrix.sum(axis=1).sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(12,6))
        total_interactions.plot(kind='bar', ax=ax)
        plt.ylabel('Total Interactions')
        plt.xlabel('Student Name')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        
        # Optional: Download the interaction matrix
        st.download_button(
            label="📥 Download Interaction Matrix CSV",
            data=interaction_matrix.to_csv().encode('utf-8'),
            file_name='interaction_matrix.csv',
            mime='text/csv'
        )

    except IndexError:
        st.error("❌ Could not automatically find the required columns. Please check that your CSV has columns related to 'Student', 'Course', and 'Group'.")
else:
    st.info("👆 Please upload a CSV file to get started!")

