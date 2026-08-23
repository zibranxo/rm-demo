# 🎓 Student Data Pipeline & UI

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A robust, interactive web application built with Streamlit and Pandas designed to streamline the student shortlisting process. It allows users to upload messy, real-world student datasets, automatically clean and validate them in real-time, dynamically filter candidates based on academic performance, and manage candidate statuses interactively.

---

## 🌟 Live Demo & Presentation

* **Live Application:** [Link to Streamlit Community Cloud Deployment](#) *(Replace with your live link)*
* **Video Demonstration:** [Link to 90-second Demo Video](#) *(Replace with YouTube/Loom link or embed)*

> **Note for Reviewers:** The video demonstration highlights the Upload process, the Auto-Cleaning Report panel, the interactive Debar toggle filtering, and the CSV export capabilities.

---

## ✨ Core Features

### 1. Seamless Data Upload & Auto-Cleaning
- **Drag-and-Drop Upload:** Easily upload raw CSV files directly from the browser.
- **Robust Auto-Cleaning:** The instant a file is uploaded, the backend pipeline standardizes text, imputes missing values, validates scores, and recalculates totals (see *Data Cleaning Logic* for details).
- **Transparent Cleaning Report:** A live metrics panel explains exactly what the algorithm did (e.g., "1 duplicate removed", "3 out-of-range marks clipped"). This ensures the automated pipeline isn't a "black box".

### 2. Interactive Debar Management
- **Stable Candidate Identity:** Generates a hidden `UUID` for every student upon upload.
- **Real-Time Toggle:** An interactive `st.data_editor` table provides a "Debarred" checkbox next to every student.
- **Instant Exclusion:** Checking the "Debarred" box immediately and seamlessly excludes the student from the Live Shortlist, without needing to reload the page or re-upload the dataset.

### 3. Dynamic Shortlist Filtering & Visual Statistics
- **Total Score Filter:** A dynamic input slider to set the minimum required total score.
- **Granular Subject Filters:** Additional filters to ensure minimum competencies in specific subjects (Math, Science, English).
- **Live Statistics:** Instantly updating metrics showing the total number of matched active candidates, the cohort's average score, and the top score.
- **Visual Analytics:** A dynamic bar chart displaying the average total score broken down by student grade.

### 4. One-Click Exports
- **Download Shortlist:** Export the final, filtered list of active candidates as a clean CSV for HR or admissions teams.
- **Download Full Clean Dataset:** Export the entirely cleaned master dataset (excluding the Debar filter) for independent verification or database ingestion.

---

## 🛠️ Technology Stack & Rationale

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/)
  - *Rationale:* Streamlit provides built-in state management which is crucial for retaining the interactive "Debar" status across filtering reruns. Its `st.data_editor` component is perfectly suited for managing tabular toggles seamlessly.
- **Data Processing:** [Pandas](https://pandas.pydata.org/)
  - *Rationale:* The industry standard for robust data manipulation. It handles null imputations, deduplication, and aggregation efficiently, keeping the `clean_data` function highly readable and performant.

---

## 🧹 Deep Dive: Data Cleaning Logic

The core data cleaning pipeline (`data_cleaning.py`) is designed to handle messy, real-world data issues instantly. Here is the step-by-step logic applied to every uploaded file:

1. **Schema Validation:** Checks that the uploaded CSV contains all expected columns (`Name`, `Gender`, `Grade`, `Math`, `Science`, `English`, `Total`).
2. **Stable Identity Generation:** Assigns a unique `UUID` to each row *before* any cleaning occurs. This guarantees that the "Debar" status tracks the correct student in Streamlit's session state, even if names are duplicated or rows are filtered out.
3. **Ghost Student Removal:** Drops any rows where the `Name` is missing entirely (e.g., `,Male,10,50,50,50,150`). A candidate without a name cannot be shortlisted.
4. **Duplicate Definition & Removal:** Removes exact duplicates based on a composite key of the `Name` (normalized to Title Case) and the `Grade`. It retains the first occurrence of the student.
5. **Categorical Normalization:** Standardizes the `Gender` column using a strict mapping dictionary to resolve casing and typo issues (e.g., `'m'`, `'male'`, and `'M'` are all mapped cleanly to `'Male'`). Unmappable values are flagged as `'Unknown'`.
6. **Missing & Invalid Marks Handling:**
   - **Missing Data:** Any missing subject marks (Math, Science, English) are imputed with `0`, treating the subject as unattempted or failed.
   - **Out-of-Range Data:** Any mathematically impossible marks (e.g., `-5` or `105`) are clipped to valid boundaries (`0` to `100`).
7. **Total Validation & Recalculation:** The `Total` column is strictly recalculated as `Math + Science + English`. If the raw dataset's total differs from the calculated total, the mismatch is flagged for the report, and the column is overwritten with the mathematically correct sum.

---

## 🚀 Installation & Local Setup

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

## 🧪 Using the Synthetic Dataset

To test the application's capabilities, a `synthetic_dirty_data.csv` file is included in the root directory. 

**Why use this file?**
It deliberately contains a multitude of edge cases designed to trigger the cleaning pipeline:
- An exact duplicate row (John Doe).
- Inconsistent and messy gender casings (`f`, `m`, `male`, `F`).
- A student missing an English mark entirely.
- A student with out-of-range marks (`-5` and `105`).
- A student with an incorrect Total (`60+70+65` listed as `300`).
- A row missing a Name (Ghost student).
- A student missing a Grade.

**Try uploading this file first to watch the Cleaning Report accurately flag and fix these exact issues!**

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

This app is optimized for immediate, free deployment via Streamlit Community Cloud.

1. Commit and push this local repository to a public GitHub repository.
2. Navigate to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **"New App"**.
4. Select your newly created repository.
5. Ensure the **Main file path** is set to `app.py`.
6. Click **Deploy!** Your app will be live globally in under 2 minutes.

---

## 📁 Repository Structure

```text
student_data_pipeline/
│
├── app.py                     # Main Streamlit application and UI layout
├── data_cleaning.py           # Core data processing and cleaning pipeline
├── requirements.txt           # Python dependencies (Streamlit, Pandas)
├── synthetic_dirty_data.csv   # Sample dataset with deliberate edge cases
└── README.md                  # Comprehensive project documentation
```
