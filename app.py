# =========================
# IMPORT LIBRARIES
# =========================
import streamlit as st
import pickle
import pandas as pd

# =========================
# LOAD FILES
# =========================
model = pickle.load(open("knn_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
columns = pickle.load(open("columns.pkl", "rb"))

# =========================
# HELPER: EXTRACT OPTIONS FROM TRAINED COLUMNS
# =========================
def get_options(prefix):
    opts = [col.replace(prefix, "") for col in columns if col.startswith(prefix)]
    opts = sorted(list(set(opts)))
    return opts

# Extract all possible options
job_options = get_options("job_title_")
edu_options = get_options("education_level_")
loc_options = get_options("location_")
ind_options = get_options("industry_")
company_options = get_options("company_size_")
remote_options = get_options("remote_work_")

# Add baseline category (lost due to drop_first=True)
job_options = ["Other"] + job_options
edu_options = ["Other"] + edu_options
loc_options = ["Other"] + loc_options
ind_options = ["Other"] + ind_options
company_options = ["Other"] + company_options
remote_options = ["Other"] + remote_options

# =========================
# TITLE
# =========================
st.title("💼 Salary Prediction App (KNN Improved)")

# =========================
# USER INPUT
# =========================
exp = st.number_input("Experience (years)", 0, 30)
skills = st.number_input("Skills Count", 0, 50)
cert = st.number_input("Certifications", 0, 20)

job = st.selectbox("Job Role", job_options)
edu = st.selectbox("Education", edu_options)
loc = st.selectbox("Location", loc_options)
ind = st.selectbox("Industry", ind_options)
company = st.selectbox("Company Size", company_options)
remote = st.selectbox("Remote Work", remote_options)

# =========================
# CREATE INPUT
# =========================
input_dict = {
    "experience_years": exp,
    "skills_count": skills,
    "certifications": cert,
    "job_title": job,
    "education_level": edu,
    "location": loc,
    "industry": ind,
    "company_size": company,
    "remote_work": remote
}

input_df = pd.DataFrame([input_dict])

# =========================
# FEATURE ENGINEERING
# =========================
input_df['exp_squared'] = input_df['experience_years'] ** 2
input_df['skill_per_exp'] = input_df['skills_count'] / (input_df['experience_years'] + 1)
input_df['cert_per_skill'] = input_df['certifications'] / (input_df['skills_count'] + 1)

input_df['seniority'] = pd.cut(
    input_df['experience_years'],
    bins=[0, 2, 5, 10, 20],
    labels=['Fresher', 'Junior', 'Mid', 'Senior']
)

# =========================
# DUMMIES + ALIGN
# =========================
input_df = pd.get_dummies(input_df)
input_df = input_df.reindex(columns=columns, fill_value=0)

# =========================
# SCALE
# =========================
num_cols = ['experience_years', 'skills_count', 'certifications',
            'exp_squared', 'skill_per_exp', 'cert_per_skill']

input_df[num_cols] = scaler.transform(input_df[num_cols])

# =========================
# PREDICTION
# =========================
if st.button("Predict Salary"):
    prediction = model.predict(input_df)
    st.success(f"💰 Predicted Salary: {int(prediction[0])}")
    st.balloons()
