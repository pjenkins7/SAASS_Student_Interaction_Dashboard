# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 

# Configure Streamlit
st.set_page_config(layout="wide")
st.title('📚 Student Interaction Dashboard')

uploaded_file = st.file_uploader("Upload your SAASS Groupings CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Define column names based on structure
    student_col = 'Student'
    course_col = 'Course'
    group_col = 'Group'

    students = sorted(df[student_col].unique())
    interaction_matrix = pd.DataFrame(0, index=students, columns=students)

    # Build interaction matrix
    for course in df[course_col].unique():
        course_data = df[df[course_col] == course]
        for group in course_data[group_col].dropna().unique():
            members = course_data[course_data[group_col] == group][student_col].tolist()
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    interaction_matrix.loc[members[i], members[j]] += 1
                    interaction_matrix.loc[members[j], members[i]] += 1

    # Heatmap with red-white and diagonal Xs
    heatmap_matrix = interaction_matrix.copy()
    np.fill_diagonal(heatmap_matrix.values, np.nan)  # Set diagonal to NaN

    st.markdown("### 🔥 Interaction Heatmap")
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(heatmap_matrix, cmap="Reds", annot=True, fmt='.0f', linewidths=0.5, linecolor='gray', ax=ax,
                cbar_kws={'label': 'Interactions'})
    for i in range(len(students)):
        ax.text(i + 0.5, i + 0.5, "X", ha='center', va='center', color='black', fontsize=9)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    # Compute total interactions (number of unique pairings)
    total_interactions = interaction_matrix.sum(axis=1)

    # Bar chart with labels
    st.markdown("### 📈 Total Interactions per Student")
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(total_interactions.index, total_interactions.values)
    ax.set_ylabel("Total Interactions")
    ax.set_xlabel("Student")
    plt.xticks(rotation=45, ha='right')
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    st.pyplot(fig)

    # Proper summary statistics
    st.markdown("### 📊 Summary Statistics")
    summary_stats = {
        "Total Students (|S|)": len(students),
        "Total Courses (|C|)": df[course_col].nunique(),
        "Groups per Course (|G|)": df[group_col].nunique(),
        "Min Interactions by Student": int(total_interactions.min()),
        "Max Interactions by Student": int(total_interactions.max()),
        "Average Interactions by Student": round(total_interactions.mean(), 1),
        "Median Interactions by Student": int(total_interactions.median()),
        "Students Fully Paired (met everyone)": sum(total_interactions == (len(students) - 1) * df[course_col].nunique()),
    }
    summary_df = pd.DataFrame(summary_stats.items(), columns=["Metric", "Value"])
    st.table(summary_df)

    # Download interaction matrix
    st.download_button(
        label="📥 Download Interaction Matrix CSV",
        data=interaction_matrix.to_csv().encode('utf-8'),
        file_name='interaction_matrix.csv',
        mime='text/csv'
    )

else:
    st.info("👆 Please upload a CSV file to get started!")
