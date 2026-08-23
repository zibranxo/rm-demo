# Student Data Pipeline & UI

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A robust, interactive web application built with Streamlit and Pandas designed to streamline the student shortlisting process. It allows users to upload raw student datasets, automatically clean and validate them in real-time, dynamically filter candidates based on a minimum total score requirement, and manage candidate statuses interactively.

---

## Live Demo & Presentation

* **Live Application:** [Link to Live Application](https://rm-demo.streamlit.app/)
* **Video Demonstration:** [Link to 90-second Demo Video](https://drive.google.com/drive/u/2/folders/1dYoZdqdSKDFkWTc5uRyR_lG69OtDwKuZ)

> **Note for Reviewers:** The video demonstration highlights the Upload process, the auto-cleaning functionality, the interactive Debar toggle filtering, and the CSV export capabilities.

---

## Core Features

### 1. Data Upload & Auto-Cleaning
- **File Uploader:** Easily upload raw CSV files directly from the browser.
- **Auto-Cleaning Pipeline:** Instantly process and clean the data upon upload (handling duplicates, typos, missing values, and validating/recalculating the Total column).
- **View Cleaned Data:** A clean table view allowing the user to inspect the successfully processed dataset.

### 2. Dynamic Filtering & Statistics
- **Total Score Filter:** An input field allowing the user to set a minimum total score requirement.
- **Live Shortlist:** Instantly displays the filtered list of matching students and basic summary statistics (such as total matched count and average scores).
- **Export Option:** A button to download the final filtered shortlist as a CSV file.

### 3. Real-Time Debar / Undebar Toggle & Filtering
- **Interactive Status Management:** The UI displays the cleaned student table with an interactive status control (a checkbox next to each student row) indicating whether they are Active or Debarred.
- **Visual Redlining & Apply Action:** Users can tick multiple students, then click "DEBAR!" to confidently apply exclusions. Debarred rows are instantly redlined and struck through.
- **Real-Time Exclusion:** Once applied, the system immediately ignores them during the minimum total score threshold queries, without needing to re-upload the dataset.

---

## Data Cleaning Logic

The core data cleaning pipeline (`data_cleaning.py`) handles various real-world data issues instantly upon upload:

1. **Schema Validation:** Checks that the uploaded CSV contains all expected columns (Name, Gender, Grade, Math, Science, English, Total).
2. **Stable Identity Generation:** Assigns a unique UUID to each row before any cleaning occurs. This ensures the "Debarred" status tracks the correct student.
3. **Ghost Student Removal:** Drops any rows where the Name is missing entirely.
4. **String Normalization:** Uses advanced regex to strip all quotes (single and double) from student Names. Automatically removes the text "Grade" from Grade inputs so only the numeric value remains (e.g., "Grade 5" becomes "5").
5. **Duplicate Removal:** Removes exact duplicates based on a combination of the Name (normalized) and the Grade.
6. **Categorical Normalization:** Standardizes the Gender column using a strict mapping dictionary to resolve casing and typo issues.
7. **Missing & Invalid Marks Handling:**
   - Any missing subject marks (Math, Science, English) are imputed with 0.
   - Any out-of-range marks (e.g., negative numbers or scores > 100) are clipped to valid boundaries (0 to 100).
8. **Total Validation:** The Total column is independently recalculated as Math + Science + English. If the dataset's original total differs, it overwrites it with the mathematically correct total.

---

## Installation & Local Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Step-by-Step Guide
1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd student_data_pipeline
   ```
2. **Create and activate a virtual environment (Recommended):**
   ```bash
   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate
   
   # On Windows:
   python -m venv venv
   venv\Scripts\activate
   ```
3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```
5. **Open in Browser:** 
   The app will automatically launch in your default web browser at `http://localhost:8501`.

---

## Using the Synthetic Dataset

To test the application's capabilities, a `synthetic_dirty_data.csv` file is included in the root directory. 

**Why use this file?**
It deliberately contains a multitude of edge cases designed to trigger the cleaning pipeline:
- An exact duplicate row.
- Inconsistent and messy gender casings.
- A student missing an English mark entirely.
- A student with out-of-range marks.
- A student with an incorrect Total.
- A row missing a Name (Ghost student).
- A student missing a Grade.

Try uploading this file to watch the pipeline accurately fix these exact issues.

---

## Deployment Guide (Streamlit Community Cloud)

This app is optimized for immediate, free deployment via Streamlit Community Cloud.

1. Commit and push this local repository to a public GitHub repository.
2. Navigate to share.streamlit.io and log in with your GitHub account.
3. Click "New App".
4. Select your newly created repository.
5. Ensure the Main file path is set to `app.py`.
6. Click Deploy. Your app will be live globally in under 2 minutes.

---

## Repository Structure

```text
student_data_pipeline/
|
|-- app.py                     # Main Streamlit application and UI layout
|-- data_cleaning.py           # Core data processing and cleaning pipeline
|-- requirements.txt           # Python dependencies (Streamlit, Pandas)
|-- synthetic_dirty_data.csv   # Sample dataset with deliberate edge cases
|-- README.md                  # Comprehensive project documentation
```
