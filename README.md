# Umuzi Recruitment Selection Pipeline

## Overview
This script processes applicant data for the Umuzi recruitment pipeline. It cleans the raw dataset, engineers classification features, evaluates each applicant’s eligibility, and produces three Excel outputs: **Eligible**, **Borderline**, and **Not Eligible**. All output files are stored in the same repository directory.

## What the Script Does
- Loads the raw dataset from `recruitment.xlsx` (sheet: `Data`).
- Standardizes column names and fixes mislabelled fields.
- Replaces `NaN` and `"[null]"` with consistent values.
- Categorizes fields of study and education levels.
- Evaluates aptitude, coding experience, and code-challenge performance.
- Determines final eligibility for Full Stack Web Development.
- Merges each applicant group back with the original raw data.
- Exports updated Excel files:
  - `eligible_applicants.xlsx`
  - `borderline_applicants.xlsx`
  - `not_eligible_applicants.xlsx`
  - Updated `recruitment.xlsx` with new sheets.

## Project Structure
```
├── applicants_selection.py 
├── recruitment.xlsx 
├── requirements.txt 
└── README.md
```


## Requirements
All dependencies are stored in `requirements.txt`.  
Install them with:

```bash
pip install -r requirements.txt
```
# How to Run

Execute the script from the project directory:
```
python3 applicants_selection.py
```
After execution, the script will generate:

- `eligible_applicants.xlsx`

- `borderline_applicants.xlsx`

- `not_eligible_applicants.xlsx`

An updated `recruitment.xlsx` containing additional sheets

All files are stored in the same directory.

## Notes

- The input file must be named `recruitment.xlsx` and contain a sheet called Data.

- Output files overwrite previous versions.

- The script uses a rule-driven evaluation system to determine each applicant’s status.
