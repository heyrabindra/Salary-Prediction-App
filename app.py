import streamlit as st
import pickle
import pandas as pd
import sqlite3
import hashlib

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Salary Prediction App",
    page_icon="💼",
    layout="centered"
)

# =========================
# DATABASE SETUP
# =========================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

# =========================
# PASSWORD HASHING
# =========================
def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# USER FUNCTIONS
# =========================
def add_user(username, password):
    c.execute("INSERT INTO users(username, password) VALUES (?, ?)",
              (username, make_hash(password)))
    conn.commit()

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, make_hash(password)))
    return c.fetchone()

# =========================
# LOAD MODEL FILES
# =========================
model = pickle.load(open("knn_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
columns = pickle.load(open("columns.pkl", "rb"))

# =========================
# HELPER FUNCTION
# =========================
def get_options(prefix):
    opts = [col.replace(prefix, "") for col in columns if col.startswith(prefix)]
    return ["Other"] + sorted(list(set(opts)))

job_options = get_options("job_title_")
edu_options = get_options("education_level_")
loc_options = get_options("location_")
ind_options = get_options("industry_")
company_options = get_options("company_size_")
remote_options = get_options("remote_work_")

# =========================
# AUTH MENU
# =========================
st.title("💼 Job Salary Prediction Portal")

menu = st.selectbox("Choose Option", ["Login", "Sign Up"])

# =========================
# SIGN UP PAGE
# =========================
if menu == "Sign Up":
    st.subheader("Create New Account")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):

        if password != confirm_password:
            st.error("Passwords do not match")

        elif len(password) < 6:
            st.error("Password must be at least 6 characters")

        else:
            try:
                add_user(username, password)
                st.success("Account Created Successfully!")
                st.info("Now login from Login page")
            except:
                st.error("Username already exists")

# =========================
# LOGIN PAGE
# =========================
elif menu == "Login":
    st.subheader("Login to Continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        result = login_user(username, password)

        if result:
            st.success(f"Welcome, {username}")

            st.header("💰 Salary Prediction")

            # USER INPUT
            exp = st.number_input("Experience (years)", 0, 30)
            skills = st.number_input("Skills Count", 0, 50)
            cert = st.number_input("Certifications", 0, 20)

            job = st.selectbox("Job Role", job_options)
            edu = st.selectbox("Education", edu_options)
            loc = st.selectbox("Location", loc_options)
            ind = st.selectbox("Industry", ind_options)
            company = st.selectbox("Company Size", company_options)
            remote = st.selectbox("Remote Work", remote_options)

            if st.button("Predict Salary"):

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

                # FEATURE ENGINEERING
                input_df['exp_squared'] = input_df['experience_years'] ** 2
                input_df['skill_per_exp'] = input_df['skills_count'] / (input_df['experience_years'] + 1)
                input_df['cert_per_skill'] = input_df['certifications'] / (input_df['skills_count'] + 1)

                input_df['seniority'] = pd.cut(
                    input_df['experience_years'],
                    bins=[0, 2, 5, 10, 20],
                    labels=['Fresher', 'Junior', 'Mid', 'Senior']
                )

                input_df = pd.get_dummies(input_df)
                input_df = input_df.reindex(columns=columns, fill_value=0)

                num_cols = [
                    'experience_years',
                    'skills_count',
                    'certifications',
                    'exp_squared',
                    'skill_per_exp',
                    'cert_per_skill'
                ]

                input_df[num_cols] = scaler.transform(input_df[num_cols])

                prediction = model.predict(input_df)

                st.success(f"💰 Predicted Salary: ₹ {int(prediction[0]):,}")
                st.balloons()

        else:
            st.error("Invalid Username or Password")
