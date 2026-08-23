import streamlit as st
import pandas as pd
import hashlib
from data_cleaning import clean_data

st.set_page_config(page_title="DTU Recruitment Manager", layout="wide")

# Custom CSS for dark theme card matching the image style
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
    }
    
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
        margin-top: -2rem;
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
    
    .custom-card {
        background-color: #1a1a21;
        border-radius: 8px;
        border: 1px solid #333;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
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
    }
    </style>
""", unsafe_allow_html=True)

def get_file_hash(uploaded_file):
    if uploaded_file is None:
        return None
    file_bytes = uploaded_file.getvalue()
    return hashlib.md5(file_bytes).hexdigest()

# Top Bar
st.markdown("""
<div class="top-bar">
    <img src="https://upload.wikimedia.org/wikipedia/en/b/b5/DTU%2C_Delhi_official_logo.png" alt="DTU Logo">
    <span class="top-bar-title">Delhi Technological University - Student Data Pipeline</span>
</div>
""", unsafe_allow_html=True)

# Main Navigation
nav_selection = st.sidebar.radio(
    "Navigation",
    ["Data Upload & Cleaning", "Dynamic Filtering & Shortlist"]
)

if nav_selection == "Data Upload & Cleaning":
    st.markdown("""
    <div class="custom-card">
        <div class="card-title">Data Upload & Cleaning</div>
        <div class="card-subtitle">Upload the raw student CSV to auto-clean records and manage Active/Debarred status.</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Student CSV", type=["csv"])
    
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
        
        st.markdown("#### Cleaned Data & Debar Management")
        st.caption("Toggle the 'Debarred' column to immediately exclude a student from the live shortlist.")
        
        display_df = st.session_state.cleaned_df.copy()
        display_df['Debarred'] = display_df['student_id'].map(st.session_state.debar_status)
        
        edited_df = st.data_editor(
            display_df,
            column_config={"Debarred": st.column_config.CheckboxColumn("Debarred", default=False), "student_id": None},
            disabled=["Name", "Gender", "Grade", "Math", "Science", "English", "Total"],
            hide_index=True,
            use_container_width=True
        )
        
        for i, row in edited_df.iterrows():
            st.session_state.debar_status[row['student_id']] = row['Debarred']

elif nav_selection == "Dynamic Filtering & Shortlist":
    st.markdown("""
    <div class="custom-card">
        <div class="card-title">Live Shortlist</div>
        <div class="card-subtitle">Filter active students based on minimum total score requirement.</div>
    </div>
    """, unsafe_allow_html=True)
    
    if 'cleaned_df' not in st.session_state:
        st.warning("Please upload a file in the 'Data Upload & Cleaning' tab first.")
    else:
        active_df = st.session_state.cleaned_df.copy()
        active_df['Debarred'] = active_df['student_id'].map(st.session_state.debar_status)
        active_df = active_df[~active_df['Debarred']]
        
        min_total = st.number_input("Minimum Total Score", 0, 300, 150)
        
        shortlist = active_df[active_df['Total'] >= min_total]
        
        st.markdown("#### Summary Statistics")
        col1, col2 = st.columns(2)
        col1.metric("Total Matched Students", len(shortlist))
        if not shortlist.empty:
            col2.metric("Average Total Score", f"{shortlist['Total'].mean():.2f}")
        else:
            col2.metric("Average Total Score", "0")
            
        st.markdown("#### Filtered Shortlist")
        st.dataframe(shortlist.drop(columns=['student_id', 'Debarred']), hide_index=True, use_container_width=True)
        
        if not shortlist.empty:
            csv_data = shortlist.drop(columns=['student_id', 'Debarred']).to_csv(index=False).encode('utf-8')
            st.download_button("Export Final Shortlist", data=csv_data, file_name='shortlist.csv', mime='text/csv')
