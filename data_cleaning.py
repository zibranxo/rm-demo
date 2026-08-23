import pandas as pd
import uuid

# Configuration
MAX_MARKS = 100
MIN_MARKS = 0
EXPECTED_COLUMNS = ["Name", "Gender", "Grade", "Math", "Science", "English", "Total"]
GENDER_MAP = {
    "m": "Male",
    "male": "Male",
    "f": "Female",
    "female": "Female",
    "other": "Other",
    "o": "Other"
}

def validate_schema(df):
    """Check if uploaded dataframe has the required columns."""
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}"
    return True, "Schema valid"

def clean_data(raw_df):
    """
    Cleans the raw dataset based on business rules.
    Returns the cleaned DataFrame and a dictionary report of cleaning actions.
    """
    report = {
        "initial_rows": len(raw_df),
        "missing_names_dropped": 0,
        "duplicates_removed": 0,
        "gender_normalized": 0,
        "missing_marks_imputed": 0,
        "out_of_range_marks_clipped": 0,
        "totals_recalculated": 0,
        "final_rows": 0
    }
    
    df = raw_df.copy()
    
    # 1. Schema Check (strip whitespace from columns first)
    df.columns = df.columns.str.strip()
    is_valid, msg = validate_schema(df)
    if not is_valid:
        raise ValueError(msg)
        
    # 2. Add stable identity (UUID) BEFORE any cleaning
    df.insert(0, 'student_id', [str(uuid.uuid4()) for _ in range(len(df))])
    
    # 3. Drop rows with missing Name (ghost students)
    initial_len = len(df)
    df = df.dropna(subset=['Name'])
    report["missing_names_dropped"] = initial_len - len(df)
    
    # Clean quotes from Names and remove 'Grade ' prefix for consistent matching
    df['Name'] = df['Name'].astype(str).str.replace(r'''['"]+''', '', regex=True).str.strip().str.title()
    df['Grade'] = df['Grade'].fillna("Unknown").astype(str).str.replace(r'(?i)grade\s*', '', regex=True).str.strip()
    
    # 4. Remove exact duplicates based on Name and Grade
    initial_len = len(df)
    df = df.drop_duplicates(subset=['Name', 'Grade'], keep='first')
    report["duplicates_removed"] = initial_len - len(df)
    
    # 5. Normalize Gender
    def map_gender(g):
        if pd.isna(g):
            return "Unknown"
        g_lower = str(g).strip().lower()
        return GENDER_MAP.get(g_lower, "Unknown")
        
    original_gender = df['Gender'].copy()
    df['Gender'] = df['Gender'].apply(map_gender)
    report["gender_normalized"] = (original_gender.astype(str).str.strip().str.lower() != df['Gender'].str.lower()).sum()
    
    # 6. Handle missing and out-of-range marks
    subjects = ['Math', 'Science', 'English']
    for sub in subjects:
        # Coerce to numeric, making non-parsable values NaN
        df[sub] = pd.to_numeric(df[sub], errors='coerce')
        
        # Impute missing with 0
        missing_count = df[sub].isna().sum()
        report["missing_marks_imputed"] += missing_count
        df[sub] = df[sub].fillna(0)
        
        # Clip out-of-range marks
        out_of_range_count = ((df[sub] < MIN_MARKS) | (df[sub] > MAX_MARKS)).sum()
        report["out_of_range_marks_clipped"] += out_of_range_count
        df[sub] = df[sub].clip(lower=MIN_MARKS, upper=MAX_MARKS)
        
    # 7. Recalculate Total and report mismatches
    df['Calculated_Total'] = df['Math'] + df['Science'] + df['English']
    
    # Clean the raw total column to compare
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
    
    mismatches = (df['Calculated_Total'] != df['Total']).sum()
    report["totals_recalculated"] = mismatches
    
    # Overwrite with correct total
    df['Total'] = df['Calculated_Total']
    df = df.drop(columns=['Calculated_Total'])
    
    report["final_rows"] = len(df)
    
    return df, report
