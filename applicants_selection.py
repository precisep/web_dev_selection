import pandas as pd
import numpy as np
import re

def main()-> pd.DataFrame:
    
    raw_data = pd.read_excel('recruitment.xlsx',engine="openpyxl",sheet_name="Data")
    raw_data.columns = raw_data.columns.str.lower().str.replace(' ', '_').str.replace(r'[()]', '_', regex=True)
    
    fix_map = {
    "second_language": "institution_highest_education",
    "institution_highest_education": "qualification_highest_education",
    "qualification_highest_education": "second_language"
    }
    corrected_data = raw_data.rename(columns=fix_map)

    feature_selection_list = ["application_id",
    "learner_id",
    "qualification_highest_education",
    "currently_studying",
    "field_of_current_education",
    "highest_education_level",
    "has_coding_experience",
    "programming_language_experince",
    "code_challenge_plagirism",
    "coding_challenge_score",
    "code_challenge_multiple_choice_score",
    "code_challenge_final_score",
    "numeracy_score",
    "logic_score",
    "problem_solving_score",
    "sequence_score",
    "literacy_score",
    "statistics_score"
    ]
    selection_data = corrected_data[feature_selection_list]
    def replace_missing_values(df, placeholder="missing"):
        updated_df = df.copy()
        updated_df = updated_df.replace("[null]", np.nan)

        text_columns = updated_df.select_dtypes(include="object").columns
        numeric_columns = updated_df.select_dtypes(include=["int64", "float64"]).columns

        updated_df[text_columns] = updated_df[text_columns].fillna(placeholder)
        updated_df[numeric_columns] = updated_df[numeric_columns].fillna(0)

        return updated_df
    selection_data = replace_missing_values(selection_data)

    field_category_map = {
    "computer_science": ["computer", "computing", "science", "cs"],
    "software_engineering": ["software", "engineering", "engineer", "devops"],
    "information_technology": ["information", "technology", "it", "ict", "informatics"],
    "programming": ["programming", "programmer", "developer", "development"],
    "web_development": ["web", "frontend", "backend", "fullstack", "full", "stack"],
    "application_systems": ["application", "app", "systems", "system"],
    "data_science": ["data","analytics","analyst","science","statistics","mathematics","maths","stats"],
    "engineering_general": ["engineering","engineer","electrical","mechanical","civil","industrial","chemical","metallurgical"],
    "cybersecurity": ["cybersecurity", "security", "network", "networking"],
    "ai_ml_bigdata": ["ai","artificial","machine","learning","ml","big","data","cloud"],
    "economics_finance": ["economics","economics","econometrics","finance","financial","actuarial","management","accounting"],
    }

    level_map = {
        "bachelor": ["bachelor", "bsc", "bcom", "ba"],
        "honours": ["honours", "honor", "hon", "nqf 8"],
        "postgrad_diploma": ["postgraduate", "pgd", "pgce", "post grad"],
        "advanced_diploma": ["advanced", "adv", "ad", "nqf 7"],
        "masters": ["master", "msc", "mba"],
        "doctorate": ["doctorate", "phd", "dphil"],
        "diploma": ["diploma", "dip"],
        "higher_certificate": ["higher", "certificate", "nqf 5"],
        "certificate": ["certificate"],
        "short_course": ["short", "course", "online", "certification"],
        "undergraduate": ["university", "undergraduate"],
        "nqf_levels": ["nqf 4", "nqf 5", "nqf 6", "nqf 7", "nqf 8"],
        }

    def normalize_education_value(value):
        text = str(value).strip().lower()
        text = re.sub(r"[^a-z0-9]+", " ", text)
        tokens = [t for t in text.split() if t]
        return tokens

    def match_any(tokens, category_map):
        hits = []
        for category, keywords in category_map.items():
            if any(token in keywords for token in tokens):
                hits.append(category)
        return hits if hits else "missing"

    selection_data["field_category"] = selection_data["field_of_current_education"].apply(
        lambda field: match_any(normalize_education_value(field), field_category_map)
    )

    selection_data["education_level"] = selection_data["highest_education_level"].apply(
        lambda level: match_any(normalize_education_value(level), level_map)
    )
    
    field_keywords = [word.lower() for word in field_category_map]
    level_keywords = [item.lower() for sublist in level_map.values() for item in sublist]

    selection_data["aptitude_meets_requirement"] = (
        (selection_data["numeracy_score"] >= 6) &
        (selection_data["logic_score"] >= 6) &
        (selection_data["problem_solving_score"] >= 6) &
        (selection_data["sequence_score"] >= 6) &
        (selection_data["literacy_score"] >= 5) &
        (selection_data["statistics_score"] >= 5)
    )


    def is_fullstack_fit(row):
        field_valid = any(word in str(row['field_category']).lower() for word in field_category_map)
        level_keywords = [item.lower() for sublist in level_map.values() for item in sublist]
        level_valid = any(word in str(row['highest_education_level']).lower() for word in level_keywords)
        uptitude_score_met = row["aptitude_meets_requirement"]

        return uptitude_score_met and (field_valid or level_valid)

    selection_data["is_fullstack_fit"] = selection_data.apply(is_fullstack_fit, axis=1)
    def check_coding_experience(value):
        return 1 if value == 1 else "no coding experience"

    selection_data["has_coding_experience"] = selection_data["has_coding_experience"].apply(check_coding_experience)

    def determine_code_challenge_outcome(row):
        plagiarism_detected = row.get("code_challenge_plagiarism", 0)
        challenge_score = row.get("coding_challenge_score", 0)
        mc_score = row.get("code_challenge_multiple_choice_score", 0)
        final_score = row.get("code_challenge_final_score", 0)

        if plagiarism_detected and final_score < 50:
            return "code challenge not passed"

        manual_review_condition_1 = challenge_score == 0 and not plagiarism_detected and mc_score >= 60
        manual_review_condition_2 = challenge_score == 100 and mc_score == 100
        if manual_review_condition_1 or manual_review_condition_2:
            return "manual review"

        if final_score >= 70 and not plagiarism_detected:
            return "passed"


        return "fail"

    selection_data["code_challenge_outcome"] = selection_data.apply(determine_code_challenge_outcome, axis=1)

    def determine_eligibility(row):
        missing_field_or_level = (
        row["field_category"] == "missing" or
        row["education_level"] == "missing")


        missing_issues = sum([
        not row["aptitude_meets_requirement"],
        not row["is_fullstack_fit"],
        row["code_challenge_outcome"] != "passed",
        row["has_coding_experience"] == "no coding experience",
        missing_field_or_level
        ])


        if missing_issues == 0:
            return "eligible"
        elif missing_issues <= 2:
            return "borderline"
        else:
            return "not_eligible"

    selection_data["eligibility"] = selection_data.apply(determine_eligibility, axis=1)

    def merge_applicants_with_raw(selection_dataframe, raw_dataframe, eligibility_status):
        applicants_group = selection_dataframe[selection_dataframe["eligibility"] == eligibility_status]
        merged_df = applicants_group.merge(raw_dataframe,on="application_id",how="left",suffixes=('', '_raw'))


        for col in raw_dataframe.columns:
            if col in applicants_group.columns and col != "application_id":
                merged_df.drop(f"{col}_raw", axis=1, inplace=True)


        extra_columns = [col for col in merged_df.columns if col not in raw_dataframe.columns]
        merged_df = merged_df[list(raw_dataframe.columns) + extra_columns]

        return merged_df
    eligible_applicants = merge_applicants_with_raw(selection_data, raw_data, "eligible")
    print("Eligible Applicants:")
    print(eligible_applicants.info())
    print(eligible_applicants.head(10))

    border_line_applicants = merge_applicants_with_raw(selection_data, raw_data, "borderline")
    print("\nBorderline Applicants:")
    print(border_line_applicants.info())
    print(border_line_applicants.head(10))

    not_fit_for_fullstack_web_dev = merge_applicants_with_raw(selection_data, raw_data, "not_eligible")
    print("\nNot Fit for Fullstack Web Development Applicants:")
    print(not_fit_for_fullstack_web_dev.info())
    not_fit_for_fullstack_web_dev.head(10)

    print("\nStoring data to Excel files...")
    with pd.ExcelWriter('recruitment.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        raw_data.to_excel(writer, sheet_name='Data', index=False)
        eligible_applicants.to_excel(writer, sheet_name='Eligible', index=False)
        border_line_applicants.to_excel(writer, sheet_name='Borderline', index=False)
        not_fit_for_fullstack_web_dev.to_excel(writer, sheet_name='Not_Eligible', index=False)

    eligible_path = 'eligible_applicants.xlsx'
    borderline_path = 'borderline_applicants.xlsx'
    not_eligible_path = 'not_eligible_applicants.xlsx'

    eligible_applicants.to_excel(eligible_path, index=False)
    border_line_applicants.to_excel(borderline_path, index=False)
    not_fit_for_fullstack_web_dev.to_excel(not_eligible_path, index=False)
if __name__ == "__main__":
    print("Starting applicant selection process...")
    main()
    print("Applicant selection process completed.")