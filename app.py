import streamlit as st
import pandas as pd
import hashlib
from data_cleaning import clean_data

# Set page config
st.set_page_config(page_title="Student Data Pipeline", layout="wide", page_icon="🎓")

def get_file_hash(uploaded_file):
    """Generate a hash for the uploaded file to detect changes."""
    if uploaded_file is None:
        return None
    file_bytes = uploaded_file.getvalue()
    return hashlib.md5(file_bytes).hexdigest()

def reset_state():
    """Clear session state to start fresh."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# --- Sidebar: Configuration & Upload ---
with st.sidebar:
    st.title("⚙️ Controls")
    
    # File Uploader
    st.header("1. Upload Data")
    uploaded_file = st.file_uploader("Upload Raw Student CSV", type=["csv"])
    
    # Reset Button
    if st.button("Reset Application"):
        reset_state()
        st.rerun()
        
    st.markdown("---")
    
    st.header("2. Filters")
    min_total_score = st.number_input("Minimum Total Score", min_value=0, max_value=300, value=150, step=5)
    
    # Bonus: Per-subject filters
    st.markdown("**Per-Subject Minimums**")
    min_math = st.slider("Math", 0, 100, 0)
    min_science = st.slider("Science", 0, 100, 0)
    min_english = st.slider("English", 0, 100, 0)

# --- Main App ---
st.title("🎓 Student Data Pipeline & UI")

if uploaded_file is None:
    st.info("👈 Please upload a CSV file from the sidebar to begin. You can use the provided synthetic dataset.")
    st.stop()

# --- State Management & Data Cleaning ---
current_file_hash = get_file_hash(uploaded_file)

# Initialize session state for the dataset and cleaning report
if 'file_hash' not in st.session_state or st.session_state.file_hash != current_file_hash:
    try:
        # Need to read and then seek to 0 so it can be re-read if needed
        raw_df = pd.read_csv(uploaded_file)
        cleaned_df, report = clean_data(raw_df)
        
        st.session_state.file_hash = current_file_hash
        st.session_state.cleaned_df = cleaned_df
        st.session_state.report = report
        
        # Initialize debar status for new file
        st.session_state.debar_status = {sid: False for sid in cleaned_df['student_id']}
    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.stop()

# Retrieve from state
df = st.session_state.cleaned_df
report = st.session_state.report

# --- 1. Data Cleaning Report ---
st.header("✨ Data Cleaning Report")
with st.expander("View Cleaning Details", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Initial Rows", report['initial_rows'])
    col2.metric("Duplicates Removed", report['duplicates_removed'])
    col3.metric("Missing Names Dropped", report['missing_names_dropped'])
    col4.metric("Final Clean Rows", report['final_rows'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Missing Marks Imputed", report['missing_marks_imputed'])
    col2.metric("Out-of-Range Clipped", report['out_of_range_marks_clipped'])
    col3.metric("Totals Recalculated", report['totals_recalculated'])
    col4.metric("Genders Normalized", report['gender_normalized'])
    
    # Export full cleaned dataset
    csv_full = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Cleaned Dataset",
        data=csv_full,
        file_name='cleaned_students_full.csv',
        mime='text/csv',
    )

# --- 2. Interactive Debar Management ---
st.header("📋 Cleaned Data & Debar Management")
st.markdown("Toggle the **Debarred** checkbox to immediately exclude a student from the live shortlist.")

# Prepare dataframe for display by mapping the debar status
display_df = df.copy()
display_df['Debarred'] = display_df['student_id'].map(st.session_state.debar_status)

# Use data_editor to allow toggling the 'Debarred' column
edited_df = st.data_editor(
    display_df,
    column_config={
        "Debarred": st.column_config.CheckboxColumn(
            "Debarred",
            help="Check to debar student",
            default=False,
        ),
        "student_id": None # Hide the UUID from the user
    },
    disabled=["Name", "Gender", "Grade", "Math", "Science", "English", "Total"], # Prevent editing other columns
    hide_index=True,
    use_container_width=True,
    key="data_editor" # Key is necessary to track changes
)

# Update session state based on editor changes
for i, row in edited_df.iterrows():
    st.session_state.debar_status[row['student_id']] = row['Debarred']

# --- 3. Live Shortlist & Statistics ---
st.header("🎯 Live Shortlist")

# Filter out debarred students first
active_students = edited_df[~edited_df['Debarred']].copy()

# Apply score filters
shortlist = active_students[
    (active_students['Total'] >= min_total_score) &
    (active_students['Math'] >= min_math) &
    (active_students['Science'] >= min_science) &
    (active_students['English'] >= min_english)
]

# Display Statistics
if not shortlist.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Matched Students", len(shortlist))
    col2.metric("Average Total Score", f"{shortlist['Total'].mean():.1f}")
    col3.metric("Top Score", shortlist['Total'].max())
    
    # Visual Summary (Bonus)
    st.markdown("**Grade-wise Average Total Score**")
    avg_by_grade = shortlist.groupby('Grade')['Total'].mean().reset_index()
    st.bar_chart(data=avg_by_grade, x='Grade', y='Total', use_container_width=True)

    # Display Shortlist
    st.dataframe(shortlist.drop(columns=['student_id', 'Debarred']), hide_index=True, use_container_width=True)
    
    # Export Shortlist
    csv_shortlist = shortlist.drop(columns=['student_id', 'Debarred']).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Shortlist CSV",
        data=csv_shortlist,
        file_name='filtered_shortlist.csv',
        mime='text/csv',
        type="primary"
    )
else:
    st.warning("No students match the current criteria.")
