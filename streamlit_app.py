import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title('📚 Student Interaction Dashboard')

uploaded_file = st.file_uploader("Upload your SAASS Groupings CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Define column names
    student_col = 'Student'
    course_col = 'Course'
    group_col = 'Group'

    students = sorted(df[student_col].unique())
    interaction_matrix = pd.DataFrame(0, index=students, columns=students)

    # Build interaction matrix (total co-groupings)
    for course in df[course_col].unique():
        course_data = df[df[course_col] == course]
        for group in course_data[group_col].dropna().unique():
            members = course_data[course_data[group_col] == group][student_col].tolist()
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    interaction_matrix.loc[members[i], members[j]] += 1
                    interaction_matrix.loc[members[j], members[i]] += 1

    # Heatmap preparation
    heatmap_matrix = interaction_matrix.copy()
    for i in range(len(heatmap_matrix)):
        heatmap_matrix.iloc[i, i] = np.nan  # Use NaN to later place 'X'

    st.markdown("### 🔥 Heatmap of Student Interactions")
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(heatmap_matrix, cmap="Reds", annot=True, fmt=".0f", linewidths=0.5, linecolor='gray', ax=ax,
                cbar_kws={'label': 'Total Interactions'})
    for i in range(len(students)):
        ax.text(i + 0.5, i + 0.5, "X", ha='center', va='center', color='black', fontsize=9)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    # --- Distinct interactions ---
    pairwise_partners = {student: set() for student in students}
    for course in df[course_col].unique():
        course_data = df[df[course_col] == course]
        for group in course_data[group_col].dropna().unique():
            members = course_data[course_data[group_col] == group][student_col].tolist()
            for i in range(len(members)):
                for j in range(len(members)):
                    if i != j:
                        pairwise_partners[members[i]].add(members[j])
    distinct_interactions = pd.Series({s: len(partners) for s, partners in pairwise_partners.items()})
    distinct_interactions = distinct_interactions.sort_values()

    # --- Horizontal bar chart ---
    st.markdown("### Distinct Student Pairings")
    fig, ax = plt.subplots(figsize=(10, 12))
    bars = ax.barh(distinct_interactions.index, distinct_interactions.values, color='skyblue')
    ax.set_xlabel("Number of Distinct Students Paired With")
    ax.set_xlim(0, 44)
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{int(width)}', xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0), textcoords="offset points", ha='left', va='center')
    st.pyplot(fig)

    # --- Summary statistics ---
    mean_val = round(distinct_interactions.mean(), 1)
    median_val = int(distinct_interactions.median())
    std_val = round(distinct_interactions.std(ddof=0), 2)
    fully_paired = sum(distinct_interactions == len(students) - 1)

    summary_stats = pd.DataFrame([
        {
            "Metric": "Total Students",
            "Description": "Total number of unique students in the dataset",
            "Value": len(students)
        },
        {
            "Metric": "Total Courses",
            "Description": "Total number of distinct courses represented",
            "Value": df[course_col].nunique()
        },
        {
            "Metric": "Min Distinct Interactions",
            "Description": "Fewest unique students paired with by any student",
            "Value": int(distinct_interactions.min())
        },
        {
            "Metric": "Max Distinct Interactions",
            "Description": "Most unique students paired with by any student",
            "Value": int(distinct_interactions.max())
        },
        {
            "Metric": "Average Distinct Interactions",
            "Description": "Mean number of unique pairings per student",
            "Value": mean_val
        },
        {
            "Metric": "Median Distinct Interactions",
            "Description": "Middle value of distinct pairings across all students",
            "Value": median_val
        },
        {
            "Metric": "Std Dev of Distinct Interactions",
            "Description": "Standard deviation of unique pairings",
            "Value": std_val
        },
        {
            "Metric": "Students Fully Paired",
            "Description": "Number of students who interacted with all others",
            "Value": fully_paired
        }
    ])

    st.markdown("### 📋 Summary Statistics")
    st.table(summary_stats)

    # --- Individual Student Interaction Viewer ---
    st.markdown("### 👤 View Individual Student Interactions")

    # Add a blank option
    student_options = ["Select a student..."] + students
    selected_student = st.selectbox("Select a student:", student_options)

    if selected_student != "Select a student...":
        st.subheader(f"Interactions for {selected_student}")

        # Who they’ve interacted with (and how many times)
        paired_students = interaction_matrix.loc[selected_student]
        paired_students = paired_students[paired_students > 0].sort_values(ascending=False)

        st.markdown(f"**Total distinct students paired with:** {len(paired_students)}")
        st.write("#### Students Paired With:")
        st.dataframe(paired_students.rename("Times Paired"))

        # Horizontal bar chart with annotations
        fig, ax = plt.subplots(figsize=(8, max(4, len(paired_students) * 0.25)))
        paired_students.sort_values().plot(kind='barh', ax=ax, color='coral')
        ax.set_xlabel("Times Paired")
        ax.set_title(f"Pairing Frequency for {selected_student}")
        for bar in ax.patches:
            width = bar.get_width()
            ax.annotate(f'{int(width)}',
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(3, 0), textcoords="offset points",
                        ha='left', va='center')
        st.pyplot(fig)

else:
    st.info("👆 Please upload a CSV file to get started!")
