import streamlit as st
import pandas as pd
import hashlib
import plotly.express as px
from data_cleaning import clean_data

st.set_page_config(page_title="DTU Student Pipeline", layout="wide", page_icon="🎓")

# Custom CSS for DTU Header
st.markdown("""
    <style>
    .dtu-header {
        display: flex;
        align-items: center;
        background-color: #2c3e50;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .dtu-header img {
        height: 60px;
        margin-right: 20px;
    }
    .dtu-header h1 {
        color: white;
        margin: 0;
        font-size: 28px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# DTU Header
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

tab1, tab2 = st.tabs(["📥 Data Upload & Cleaning", "📊 Analytics & Shortlisting"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload Raw Student CSV", type=["csv"])
    with col2:
        st.write("")
        st.write("")
        if st.button("🗑️ Reset Application", use_container_width=True):
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
                st.toast("File uploaded and cleaned successfully!", icon="✅")
            except Exception as e:
                st.error(f"Error processing file: {e}")
                st.stop()
                
        df = st.session_state.cleaned_df
        report = st.session_state.report

        st.markdown("### ✨ Data Cleaning Report")
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

        st.markdown("### 🚦 Candidate Roster & Debarment")
        st.caption("Check the 'Debarred' column to instantly exclude a student from the analytics and shortlist.")
        
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
            height=400
        )
        
        for i, row in edited_df.iterrows():
            st.session_state.debar_status[row['student_id']] = row['Debarred']

with tab2:
    if 'cleaned_df' not in st.session_state:
        st.info("👈 Please upload a dataset in the 'Data Upload & Cleaning' tab to unlock analytics.")
    else:
        active_df = st.session_state.cleaned_df.copy()
        active_df['Debarred'] = active_df['student_id'].map(st.session_state.debar_status)
        active_df = active_df[~active_df['Debarred']]
        
        st.markdown("### 🎛️ Shortlist Filters")
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
            st.markdown("### 📊 Performance Analytics")
            
            # Top row charts
            c1, c2 = st.columns(2)
            
            # Histogram of Totals
            fig_hist = px.histogram(shortlist, x="Total", nbins=10, title="Distribution of Total Scores", 
                                    color_discrete_sequence=['#3498db'])
            fig_hist.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            c1.plotly_chart(fig_hist, use_container_width=True)
            
            # Scatter Plot Math vs Science
            fig_scatter = px.scatter(shortlist, x="Math", y="Science", size="Total", color="Grade",
                                     hover_name="Name", title="Math vs Science Performance",
                                     color_discrete_sequence=px.colors.qualitative.Set2)
            fig_scatter.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            c2.plotly_chart(fig_scatter, use_container_width=True)
            
            # Box plot for subjects
            st.markdown("#### Subject Wise Spread")
            box_data = shortlist[['Math', 'Science', 'English']].melt(var_name='Subject', value_name='Score')
            fig_box = px.box(box_data, x='Subject', y='Score', color='Subject', title="Score Spread per Subject")
            fig_box.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_box, use_container_width=True)
            
            st.markdown("### 🏆 Final Shortlist")
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Shortlisted Candidates", len(shortlist))
            sc2.metric("Average Score", f"{shortlist['Total'].mean():.1f}")
            sc3.metric("Highest Score", shortlist['Total'].max())
            
            st.dataframe(shortlist.drop(columns=['student_id', 'Debarred']), hide_index=True, use_container_width=True)
            
            csv = shortlist.drop(columns=['student_id', 'Debarred']).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Final Shortlist as CSV", data=csv, file_name='dtu_shortlist.csv', mime='text/csv', type="primary")
