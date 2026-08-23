import streamlit as st
import pandas as pd
import hashlib
import plotly.express as px
from data_cleaning import clean_data

# No emojis in page config
st.set_page_config(page_title="DTU Student Pipeline", layout="wide")

# Advanced Custom CSS for Modern UI
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Glassmorphism Header */
    .dtu-header {
        display: flex;
        align-items: center;
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px 30px;
        border-radius: 16px;
        margin-bottom: 35px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease;
    }
    .dtu-header:hover {
        transform: translateY(-2px);
    }
    .dtu-header img {
        height: 65px;
        margin-right: 25px;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
    }
    .dtu-header h1 {
        color: #f8fafc;
        margin: 0;
        font-size: 28px;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Elegant Buttons with Hover Effects */
    .stButton > button {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.15)) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(37, 99, 235, 0.3)) !important;
        border-color: rgba(96, 165, 250, 0.8) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.25);
    }
    
    /* Primary Button variant */
    button[kind="primary"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.8), rgba(37, 99, 235, 0.9)) !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.9), rgba(59, 130, 246, 1)) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    }
    
    /* Subtle container styling */
    div[data-testid="stContainer"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 5px;
    }
    
    /* Expander styling */
    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    div[data-testid="stExpander"]:hover {
        border-color: rgba(96, 165, 250, 0.5);
    }
    
    /* Metrics styling */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.4);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        border-color: rgba(96, 165, 250, 0.5);
    }
    
    /* File uploader dashed border enhancement */
    section[data-testid="stFileUploadDropzone"] {
        border: 2px dashed rgba(96, 165, 250, 0.4);
        background: rgba(15, 23, 42, 0.3);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: rgba(96, 165, 250, 0.8);
        background: rgba(15, 23, 42, 0.5);
    }
    
    /* Tabs typography */
    button[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px;
        color: #94a3b8 !important;
    }
    button[aria-selected="true"] {
        color: #f8fafc !important;
    }
    
    /* Markdown Headers */
    h3 {
        font-weight: 600 !important;
        color: #e2e8f0 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# DTU Header (Emoji-free)
st.markdown("""
<div class="dtu-header">
    <img src="https://upload.wikimedia.org/wikipedia/en/b/b5/DTU%2C_Delhi_official_logo.png" alt="DTU Logo">
    <h1>Delhi Technological University - Student Data Pipeline</h1>
</div>
""", unsafe_allow_html=True)

def get_file_hash(uploaded_file):
    if uploaded_file is None:
        return None
    return hashlib.md5(uploaded_file.getvalue()).hexdigest()

tab1, tab2 = st.tabs(["Data Upload & Cleaning", "Analytics & Shortlisting"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload Raw Student CSV", type=["csv"])
    with col2:
        st.write("")
        st.write("")
        if st.button("Reset Application", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if uploaded_file is not None:
        current_hash = get_file_hash(uploaded_file)
        if 'file_hash' not in st.session_state or st.session_state.file_hash != current_hash:
            try:
                raw_df = pd.read_csv(uploaded_file)
                cleaned_df, report = clean_data(raw_df)
                st.session_state.file_hash = current_hash
                st.session_state.cleaned_df = cleaned_df
                st.session_state.report = report
                st.session_state.debar_status = {sid: False for sid in cleaned_df['student_id']}
                
                # Removed emoji icon from toast
                st.toast("File uploaded and cleaned successfully")
            except Exception as e:
                st.error(f"Error processing file: {e}")
                st.stop()
                
        df = st.session_state.cleaned_df
        report = st.session_state.report

        st.markdown("### Data Cleaning Report")
        with st.expander("View Pipeline Execution Metrics", expanded=True):
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Initial Rows", report['initial_rows'])
            rc2.metric("Ghost Records Dropped", report['missing_names_dropped'])
            rc3.metric("Duplicates Removed", report['duplicates_removed'])
            rc4.metric("Final Usable Rows", report['final_rows'])
            
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Genders Normalized", report['gender_normalized'])
            rc2.metric("Missing Marks Imputed", report['missing_marks_imputed'])
            rc3.metric("Invalid Marks Clipped", report['out_of_range_marks_clipped'])
            rc4.metric("Totals Recalculated", report['totals_recalculated'])

        st.markdown("### Candidate Roster & Debarment")
        st.caption("Check the 'Debarred' column and click 'Apply Debar Updates' to confirm.")
        
        display_df = df.copy()
        display_df['Debarred'] = display_df['student_id'].map(st.session_state.debar_status)
        
        edited_df = st.data_editor(
            display_df,
            column_config={
                "Debarred": st.column_config.CheckboxColumn("Debarred?", default=False),
                "student_id": None
            },
            disabled=["Name", "Gender", "Grade", "Math", "Science", "English", "Total"],
            hide_index=True,
            use_container_width=True,
            height=600,
            key="debar_editor"
        )
        
        if st.button("Apply Debar Updates", type="primary"):
            for i, row in edited_df.iterrows():
                st.session_state.debar_status[row['student_id']] = row['Debarred']
            st.rerun()

with tab2:
    if 'cleaned_df' not in st.session_state:
        st.info("Please upload a dataset in the 'Data Upload & Cleaning' tab to unlock analytics.")
    else:
        active_df = st.session_state.cleaned_df.copy()
        active_df['Debarred'] = active_df['student_id'].map(st.session_state.debar_status)
        active_df = active_df[~active_df['Debarred']]
        
        st.markdown("### Shortlist Filters")
        with st.container(border=True):
            f1, f2, f3, f4 = st.columns(4)
            min_total = f1.number_input("Minimum Total Score", 0, 300, 150)
            min_math = f2.number_input("Minimum Math", 0, 100, 0)
            min_science = f3.number_input("Minimum Science", 0, 100, 0)
            min_english = f4.number_input("Minimum English", 0, 100, 0)
            
        shortlist = active_df[
            (active_df['Total'] >= min_total) &
            (active_df['Math'] >= min_math) &
            (active_df['Science'] >= min_science) &
            (active_df['English'] >= min_english)
        ]
        
        if shortlist.empty:
            st.error("No candidates matched the current filter criteria.")
        else:
            st.markdown("### Performance Analytics")
            
            # Top row charts
            c1, c2 = st.columns(2)
            
            # Histogram of Totals
            fig_hist = px.histogram(shortlist, x="Total", nbins=10, title="Distribution of Total Scores", 
                                    color_discrete_sequence=['#3b82f6'])
            fig_hist.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#e2e8f0")
            )
            c1.plotly_chart(fig_hist, use_container_width=True)
            
            # Scatter Plot Math vs Science
            fig_scatter = px.scatter(shortlist, x="Math", y="Science", size="Total", color="Grade",
                                     hover_name="Name", title="Math vs Science Performance",
                                     color_discrete_sequence=px.colors.qualitative.Set2)
            fig_scatter.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#e2e8f0")
            )
            c2.plotly_chart(fig_scatter, use_container_width=True)
            
            # Box plot for subjects
            st.markdown("#### Subject Wise Spread")
            box_data = shortlist[['Math', 'Science', 'English']].melt(var_name='Subject', value_name='Score')
            fig_box = px.box(box_data, x='Subject', y='Score', color='Subject', title="Score Spread per Subject")
            fig_box.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#e2e8f0")
            )
            st.plotly_chart(fig_box, use_container_width=True)
            
            st.markdown("### Final Shortlist")
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Shortlisted Candidates", len(shortlist))
            sc2.metric("Average Score", f"{shortlist['Total'].mean():.1f}")
            sc3.metric("Highest Score", shortlist['Total'].max())
            
            st.dataframe(shortlist.drop(columns=['student_id', 'Debarred']), hide_index=True, use_container_width=True, height=600)
            
            csv = shortlist.drop(columns=['student_id', 'Debarred']).to_csv(index=False).encode('utf-8')
            st.download_button("Export Final Shortlist as CSV", data=csv, file_name='dtu_shortlist.csv', mime='text/csv', type="primary")
