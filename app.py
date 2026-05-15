import streamlit as st
import pickle
import pandas as pd
import sqlite3
import hashlib

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
conn.commit()

def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    c.execute("INSERT INTO users VALUES (?, ?)", (username, make_hash(password)))
    conn.commit()

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, make_hash(password)))
    return c.fetchone()

# ---------------- LOGIN/SIGNUP ----------------
menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Sign Up":
    st.title("Create Account")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        add_user(new_user, new_pass)
        st.success("Account Created! Go to Login")

elif choice == "Login":
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if login_user(username, password):

            st.success("Login Successful!")

            # LOAD MODEL
            model = pickle.load(open("knn_model.pkl", "rb"))
            scaler = pickle.load(open("scaler.pkl", "rb"))
            columns = pickle.load(open("columns.pkl", "rb"))

            st.title("💼 Salary Prediction App")

            exp = st.number_input("Experience", 0, 30)
            skills = st.number_input("Skills Count", 0, 50)
            cert = st.number_input("Certifications", 0, 20)

            if st.button("Predict Salary"):
                st.success("Prediction works here")

        else:
            st.error("Wrong Username or Password")
