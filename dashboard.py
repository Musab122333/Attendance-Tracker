import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(layout="wide")

conn = sqlite3.connect("attendance.db")
df = pd.read_sql("SELECT * FROM attendance", conn)

st.title("My Attendance Tracker")

st.dataframe(df)

subject = st.selectbox("Select Subject", df["subject_name"].unique())
filtered = df[df["subject_name"] == subject]

st.line_chart(filtered["cumulative"])
