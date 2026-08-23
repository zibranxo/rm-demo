import streamlit as st
import pandas as pd
import hashlib
from data_cleaning import clean_data

# Alternative Idea: Collapse sidebar by default, rely heavily on tabs in the main container
st.set_page_config(page_title="Student Data Pipeline", layout="wide", page_icon="🎓", initial_sidebar_state="collapsed")

# Custom CSS for alternative styling
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        color: #ff4b4b;
        text-align: center;
        border-bottom: 2px dashed #ff4b4b;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Alternative Idea: Custom HTML title instead of standard st.title()
st.markdown('<div class="main-title">🚀 Next-Gen Student Pipeline</div>', unsafe_allow_html=True)

def get_file_hash(uploaded_file):
    if uploaded_file is None:
        return None
    file_bytes = uploaded_file.getvalue()
    return hashlib.md5(file_bytes).hexdigest()

def reset_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Alternative Idea: No sidebar for the core workflow, use Tabs instead.
tab_ingest, tab_analytics = st.tabs(["📂 1. Ingestion & Cleaning", "📊 2. Analytics & Shortlist"])

with tab_ingest:
    # Upload area
    col1, col2 = st.columns([3, 1])
    with col1:
        # Alternative Idea: File uploader in main area rather than sidebar
        uploaded_file = st.file_uploader("Drop your messy CSV here", type=["csv"], help="We'll clean it instantly.")
    with col2:
        st.write("")
        st.write("")
        if st.button("🗑️ Nuke State & Reset", use_container_width=True):
            reset_state()
            st.rerun()

    if uploaded_file is not None:
        current_file_hash = get_file_hash(uploaded_file)
        
        if 'file_hash' not in st.session_state or st.session_state.file_hash != current_file_hash:
            try:
                raw_df = pd.read_csv(uploaded_file)
                cleaned_df, report = clean_data(raw_df)
                
                st.session_state.file_hash = current_file_hash
                st.session_state.cleaned_df = cleaned_df
                st.session_state.report = report
                # Initialize debar status map
                st.session_state.debar_status = {sid: False for sid in cleaned_df['student_id']}
                
                # Alternative Idea: Use a toast instead of a static success message
                st.toast("File uploaded and cleaned successfully!", icon="✅")
            except Exception as e:
                st.error(f"Error processing file: {e}")
                st.stop()
                
        df = st.session_state.cleaned_df
        report = st.session_state.report

        # Alternative Idea: Bullet list in an info box instead of st.metric columns
        st.markdown("### 🛠️ Pipeline Execution Log")
        st.info(f"""
        - Started with **{report['initial_rows']}** raw rows.
        - Dropped **{report['missing_names_dropped']}** ghost records (no name).
        - Eliminated **{report['duplicates_removed']}** identical clones.
        - Normalized **{report['gender_normalized']}** gender inconsistencies.
        - Imputed **{report['missing_marks_imputed']}** missing scores with zeros.
        - Clipped **{report['out_of_range_marks_clipped']}** impossible marks.
        - Corrected **{report['totals_recalculated']}** mathematically flawed totals.
        - **Final usable roster: {report['final_rows']} students.**
        """)
        
        # Alternative Idea: Download button at the top instead of bottom
        st.download_button("📥 Export Cleaned Master Roster", data=df.to_csv(index=False).encode('utf-8'), file_name='cleaned_roster.csv', mime='text/csv')

        st.markdown("### 🚦 Candidate Roster & Debar Control")
        st.caption("Check the 'Debarred' column to blacklist a student across all analytics tabs.")
        
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
            height=300
        )
        
        for i, row in edited_df.iterrows():
            st.session_state.debar_status[row['student_id']] = row['Debarred']

with tab_analytics:
    if 'cleaned_df' not in st.session_state:
        st.warning("👈 Please upload a file in the Ingestion tab first.")
    else:
        active_df = st.session_state.cleaned_df.copy()
        active_df['Debarred'] = active_df['student_id'].map(st.session_state.debar_status)
        active_df = active_df[~active_df['Debarred']]

        st.markdown("### 🎛️ Filter Matrix")
        # Alternative Idea: Horizontal form layout for filters in a bordered container instead of sidebar sliders
        with st.container(border=True):
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            with f_col1:
                min_total = st.number_input("Min Total", 0, 300, 150)
            with f_col2:
                min_math = st.number_input("Min Math", 0, 100, 0)
            with f_col3:
                min_science = st.number_input("Min Science", 0, 100, 0)
            with f_col4:
                min_english = st.number_input("Min English", 0, 100, 0)
                
        shortlist = active_df[
            (active_df['Total'] >= min_total) &
            (active_df['Math'] >= min_math) &
            (active_df['Science'] >= min_science) &
            (active_df['English'] >= min_english)
        ]
        
        if shortlist.empty:
            st.error("No candidates survived the filter matrix.")
        else:
            st.markdown("### 🏆 The Shortlist")
            
            c_col1, c_col2 = st.columns([1, 2])
            with c_col1:
                # Alternative Idea: Inline markdown with code blocks instead of st.metric
                st.markdown(f"**Survivors:** `{len(shortlist)}`")
                st.markdown(f"**Avg Score:** `{shortlist['Total'].mean():.2f}`")
                st.markdown(f"**Highest Score:** `{shortlist['Total'].max()}`")
                
                st.write("")
                st.download_button("📥 Export Shortlist", data=shortlist.drop(columns=['student_id', 'Debarred']).to_csv(index=False).encode('utf-8'), file_name='shortlist.csv', mime='text/csv', type="primary", use_container_width=True)
                
            with c_col2:
                st.markdown("**Performance Scatter (Math vs Science)**")
                # Alternative Idea: Scatter chart instead of Bar chart
                st.scatter_chart(shortlist, x='Math', y='Science', color='Grade', size='Total', use_container_width=True)
                
            st.dataframe(shortlist.drop(columns=['student_id', 'Debarred']), hide_index=True, use_container_width=True)
