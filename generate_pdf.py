from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 15)
        self.cell(0, 10, "Delhi Technological University - Student Data Pipeline", border=False, ln=1, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

pdf = PDF()
pdf.add_page()
pdf.set_font("helvetica", size=11)

def add_section(title, content):
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 10, title, ln=1)
    pdf.set_font("helvetica", size=11)
    pdf.multi_cell(0, 7, content)
    pdf.ln(5)

# --- Content ---
pdf.set_font("helvetica", "B", 18)
pdf.cell(0, 15, "Software Requirements Specification (SRS) & User Manual", ln=1, align="C")
pdf.ln(10)

srs_intro = (
    "1. Introduction\n"
    "This document outlines the Software Requirements Specification (SRS) and the User Manual for the DTU Student Data Pipeline. "
    "The application is designed to ingest raw student datasets, automatically clean them, and provide an interactive dashboard for filtering and shortlisting candidates."
)
add_section("Part 1: Software Requirements Specification (SRS)", srs_intro)

srs_reqs = (
    "2. Functional Requirements\n"
    "FR1. Data Ingestion: The system shall allow users to upload CSV files containing student records.\n"
    "FR2. Auto-Cleaning: The system shall clean quotes from names, remove 'Grade' text from grade values, impute missing marks with 0, clip out-of-range marks (0-100), remove missing names, remove exact duplicates, normalize gender formats, and strictly recalculate the Total column.\n"
    "FR3. Debar Management: The system shall provide a real-time checkbox toggle to mark a student as Debarred, which immediately excludes them from analytics.\n"
    "FR4. Shortlist Filtering: The system shall allow filtering by minimum Total, Math, Science, and English scores.\n"
    "FR5. Data Export: The system shall allow downloading the final shortlist as a CSV file.\n"
    "\n"
    "3. Non-Functional Requirements\n"
    "NFR1. Usability: The interface shall use a modern, glassmorphic UI design and be accessible via a standard web browser.\n"
    "NFR2. Performance: File processing and data cleaning shall occur in real-time upon upload."
)
add_section("", srs_reqs)

pdf.add_page()
manual_intro = (
    "1. Getting Started\n"
    "Ensure you have Python 3.8+ installed. Run the application locally by executing `streamlit run app.py` in your terminal. "
    "The application will open automatically in your browser at http://localhost:8501."
)
add_section("Part 2: User Manual", manual_intro)

manual_steps = (
    "2. Data Upload & Cleaning\n"
    "- Navigate to the 'Data Upload & Cleaning' tab.\n"
    "- Drag and drop your raw CSV file into the upload zone.\n"
    "- The system will instantly display a 'Data Cleaning Report' expanding on how many duplicates, ghost records, and missing values were fixed.\n"
    "\n"
    "3. Debarring Candidates\n"
    "- In the same tab, you will see the Candidate Roster.\n"
    "- Check the 'Debarred?' box next to any student to instantly remove them from consideration. This state is preserved across tabs.\n"
    "\n"
    "4. Analytics & Shortlisting\n"
    "- Switch to the 'Analytics & Shortlisting' tab.\n"
    "- Use the top 'Shortlist Filters' to set minimum score thresholds.\n"
    "- View the interactive scatter plots, histograms, and box plots to analyze the shortlisted cohort.\n"
    "- Click 'Export Final Shortlist as CSV' at the bottom to download your results."
)
add_section("", manual_steps)

pdf.output("SRS_and_User_Manual.pdf")
