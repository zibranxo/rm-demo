# Student Data Pipeline & UI

A robust, interactive web application built with Streamlit and Pandas that allows users to upload, clean, filter, and export student datasets. It includes a real-time data cleaning engine and an interactive "Debar" feature for dynamic shortlisting.

## 🌟 Live Demo (Bonus)
*(If deployed, add your Streamlit Community Cloud link here)*
[Link to Live App](#)

## 🎥 Video Demonstration (90 Seconds)
*(Embed your screen recording here. You can upload it to YouTube/Loom and paste the link, or upload an `.mp4` file directly to GitHub)*
[Link to Video Demo](#)

## 🚀 How to Run Locally

### Prerequisites
- Python 3.8 or higher installed on your system.

### Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd student_data_pipeline
   ```
2. **(Optional) Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```
5. **Open in Browser:** 
   The app will automatically open in your default browser at `http://localhost:8501`.

## 🧹 Data Cleaning Logic

The core data cleaning pipeline (`data_cleaning.py`) handles various real-world data issues instantly upon upload. Here is how the logic works step-by-step:

1. **Schema Validation**: Ensures the uploaded CSV contains all required columns (`Name`, `Gender`, `Grade`, `Math`, `Science`, `English`, `Total`).
2. **Stable Identity Generation**: Assigns a unique `UUID` to each row before any cleaning occurs. This ensures that the "Debar" status tracks the correct student, even if names are duplicated or rows are filtered out.
3. **Ghost Student Removal**: Drops any rows where the `Name` is missing entirely, as these cannot be valid students.
4. **Duplicate Removal**: Removes exact duplicates based on a combination of the `Name` (normalized) and the `Grade`.
5. **Categorical Normalization**: Standardizes the `Gender` column using a strict mapping dictionary (e.g., 'm', 'male', 'M' all become 'Male').
6. **Missing & Invalid Marks Handling**:
   - Any missing subject marks (Math, Science, English) are imputed with `0`.
   - Any out-of-range marks (e.g., negative numbers or scores > 100) are clipped to valid boundaries (`0-100`).
7. **Total Validation**: Recalculates the `Total` column (`Math + Science + English`) independently. If the dataset's original total differs, it flags the mismatch and overwrites it with the mathematically correct total.

The app features a **"Cleaning Report"** expander that transparently displays exactly how many rows were affected by each of these rules.

## 🧪 Testing with Synthetic Data
A `synthetic_dirty_data.csv` file is included in this repository. It deliberately contains edge cases (missing values, typos, incorrect totals, and duplicates) to easily demonstrate and verify the robustness of the data cleaning pipeline.
