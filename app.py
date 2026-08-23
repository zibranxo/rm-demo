import streamlit as st
import pandas as pd
import hashlib
from data_cleaning import clean_data

st.set_page_config(page_title="DTU Recruitment Manager", layout="wide", initial_sidebar_state="expanded")

# Custom CSS to mimic the layout and styling in the image
st.markdown("""
    <style>
    /* Main container styling to match the card in the image */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Top header area styling */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    .top-bar {
        display: flex;
        align-items: center;
        padding: 10px 20px;
        background-color: #1e1e24;
        border-bottom: 1px solid #333;
        margin-bottom: 20px;
        margin-left: -4rem;
        margin-right: -4rem;
        margin-top: -1rem;
    }
    .top-bar img {
        height: 40px;
        margin-right: 15px;
    }
    .top-bar-title {
        color: white;
        font-size: 20px;
        font-weight: 600;
        margin: 0;
    }
    
    /* Profile section in sidebar */
    .profile-section {
        display: flex;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid #333;
        margin-bottom: 15px;
    }
    .profile-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #333;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        font-size: 20px;
    }
    .profile-text {
        display: flex;
        flex-direction: column;
    }
    .profile-name {
        color: #e4e4e7;
        font-size: 14px;
        font-weight: 600;
    }
    .profile-role {
        color: #71717a;
        font-size: 12px;
    }
    
    /* Card Container */
    .custom-card {
        background-color: #1a1a21;
        border-radius: 8px;
        border: 1px solid #333;
        padding: 20px;
        margin-top: 20px;
    }
    .card-title {
        font-size: 18px;
        font-weight: 600;
        color: white;
        margin-bottom: 5px;
    }
    .card-subtitle {
        font-size: 13px;
        color: #a1a1aa;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Generate file hash
def get_file_hash(uploaded_file):
    if uploaded_file is None:
        return None
    file_bytes = uploaded_file.getvalue()
    return hashlib.md5(file_bytes).hexdigest()

# --- Top Bar ---
st.markdown("""
<div class="top-bar">
    <img src="https://upload.wikimedia.org/wikipedia/en/b/b5/DTU%2C_Delhi_official_logo.png" alt="DTU Logo">
    <span class="top-bar-title">Delhi Technological University - Recruitment Manager</span>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Layout ---
st.sidebar.markdown("""
<div class="profile-section">
    <div class="profile-icon">👤</div>
    <div class="profile-text">
        <span class="profile-name">Arnav Sagar</span>
        <span class="profile-role">24/SE/03B</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation mimicking the image structure
nav_selection = st.sidebar.radio(
    "",
    ["Dashboard", "Jobs (Upload Data)", "My Applications (Shortlist)"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: #71717a; font-size: 12px; margin-top: 50px;'>Need help?</div>", unsafe_allow_html=True)
if st.sidebar.button("Contact Team", use_container_width=True):
    st.sidebar.success("Support contact: admin@dtu.ac.in")

# --- Main Area Routing ---
if nav_selection == "Dashboard":
    st.markdown("""
    <div class="custom-card">
        <div class="card-title">Recruitment Dashboard</div>
        <div class="card-subtitle">Overview of the student database. Navigate to 'Jobs' to upload data.</div>
    </div>
    """, unsafe_allow_html=True)
    
    if 'cleaned_df' in st.session_state:
        df = st.session_state.cleaned_df
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("No student data available. Please upload a dataset.")

elif nav_selection == "Jobs (Upload Data)":
    st.markdown("""
    <div class="custom-card">
        <div class="card-title">Upload & Clean Data</div>
        <div class="card-subtitle">Ingest the raw student CSV to instantly clean and validate records.</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["csv"])
    
    if uploaded_file is not None:
        current_file_hash = get_file_hash(uploaded_file)
        
        if 'file_hash' not in st.session_state or st.session_state.file_hash != current_file_hash:
            try:
                raw_df = pd.read_csv(uploaded_file)
                cleaned_df, report = clean_data(raw_df)
                
                st.session_state.file_hash = current_file_hash
                st.session_state.cleaned_df = cleaned_df
                st.session_state.report = report
                st.session_state.debar_status = {sid: False for sid in cleaned_df['student_id']}
            except Exception as e:
                st.error(f"Error processing file: {e}")
                st.stop()
        
        st.success("Dataset successfully ingested and cleaned.")
        
        st.markdown("#### Candidate Debarment")
        st.caption("Toggle the 'Debarred' column to remove a student from the active shortlist.")
        
        display_df = st.session_state.cleaned_df.copy()
        display_df['Debarred'] = display_df['student_id'].map(st.session_state.debar_status)
        
        edited_df = st.data_editor(
            display_df,
            column_config={"Debarred": st.column_config.CheckboxColumn("Debarred?", default=False), "student_id": None},
            disabled=["Name", "Gender", "Grade", "Math", "Science", "English", "Total"],
            hide_index=True,
            use_container_width=True
        )
        
        for i, row in edited_df.iterrows():
            st.session_state.debar_status[row['student_id']] = row['Debarred']

elif nav_selection == "My Applications (Shortlist)":
    st.markdown("""
    <div class="custom-card">
        <div class="card-title">Live Shortlist</div>
        <div class="card-subtitle">Filter active students based on academic criteria.</div>
    </div>
    """, unsafe_allow_html=True)
    
    if 'cleaned_df' not in st.session_state:
        st.warning("Please upload a file in the 'Jobs' tab first.")
    else:
        active_df = st.session_state.cleaned_df.copy()
        active_df['Debarred'] = active_df['student_id'].map(st.session_state.debar_status)
        active_df = active_df[~active_df['Debarred']]
        
        col1, col2, col3, col4 = st.columns(4)
        min_total = col1.number_input("Min Total Score", 0, 300, 150)
        min_math = col2.number_input("Min Math Score", 0, 100, 0)
        min_science = col3.number_input("Min Science Score", 0, 100, 0)
        min_english = col4.number_input("Min English Score", 0, 100, 0)
        
        shortlist = active_df[
            (active_df['Total'] >= min_total) &
            (active_df['Math'] >= min_math) &
            (active_df['Science'] >= min_science) &
            (active_df['English'] >= min_english)
        ]
        
        st.dataframe(shortlist.drop(columns=['student_id', 'Debarred']), hide_index=True, use_container_width=True)
        
        if not shortlist.empty:
            csv_data = shortlist.drop(columns=['student_id', 'Debarred']).to_csv(index=False).encode('utf-8')
            st.download_button("Export Final Shortlist", data=csv_data, file_name='dtu_shortlist.csv', mime='text/csv', use_container_width=True)
