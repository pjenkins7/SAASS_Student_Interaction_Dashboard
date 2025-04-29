# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Streamlit UI ---

st.title('Student Interaction Dashboard')

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### Raw Data", df)
    
    # --- Process Data ---

    # Create a list of all students
    students = sorted(set(df['Student Name'].unique()))
    
    # Initialize interaction matrix
    interaction_matrix = pd.DataFrame(0, index=students, columns=students)

    # Loop through each group to count interactions
    for course in df['Course'].unique():
        group_data = df[df['Course'] == course]
        groups = group_data['Group'].unique()
        for group in groups:
            members = group_data[group_data['Group'] == group]['Student Name'].tolist()
            for i in range(len(members)):
                for j in range(i+1, len(members)):
                    interaction_matrix.loc[members[i], members[j]] += 1
                    interaction_matrix.loc[members[j], members[i]] += 1  # symmetric

    st.write("### Interaction Matrix", interaction_matrix)

    # --- Heatmap ---
    st.write("### Heatmap of Interactions")
    plt.figure(figsize=(12, 10))
    sns.heatmap(interaction_matrix, cmap="YlGnBu", annot=False)
    st.pyplot(plt.gcf())
    plt.clf()

    # --- Total interactions per student ---
    st.write("### Total Interactions per Student")
    total_interactions = interaction_matrix.sum(axis=1).sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(12,6))
    total_interactions.plot(kind='bar', ax=ax)
    plt.ylabel('Total Interactions')
    st.pyplot(fig)

else:
    st.info("👆 Please upload a CSV file to get started!")

