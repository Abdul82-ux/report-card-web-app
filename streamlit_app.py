# Streamlit version of the Report Card App with Admin Login
import streamlit as st
import pandas as pd
import os
from PIL import Image
from fpdf import FPDF
from io import BytesIO

# Set folder paths
project_folder = os.path.join(os.path.expanduser("~"), "Downloads", "Project")
students = ["Adams", "Bala", "Deji", "Ngozi"]
admin_credentials = {"admin": "admin123"}  # Simple admin user/pass

# Helper functions
def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

def calculate_ranks():
    student_totals = {}
    for student in students:
        try:
            df = pd.read_excel(os.path.join(project_folder, f"{student}.xlsx"), skiprows=8, engine='openpyxl')
            total_score = df.iloc[:, 1:4].sum(axis=1).sum()
            student_totals[student] = total_score
        except:
            student_totals[student] = 0
    sorted_students = sorted(student_totals.items(), key=lambda x: x[1], reverse=True)
    return {name: ordinal(i+1) for i, (name, _) in enumerate(sorted_students)}

def generate_pdf(student_name, df, rank):
    pdf = FPDF()
    pdf.add_page()

    logo_path = os.path.join(project_folder, "ICY.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=25)

    photo_path = os.path.join(project_folder, f"{student_name} Image.png")
    if os.path.exists(photo_path):
        pdf.image(photo_path, x=170, y=8, w=25)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "IGBOBI COLLEGE YABA", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Igobobi College Road, Fadeyi, Lagos", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, f"Student Name: {student_name}", ln=False)
    pdf.cell(0, 10, f"Rank: {rank} Position", ln=True, align="R")
    pdf.ln(5)

    headers = ["Subject", "CA1", "CA2", "Exam", "Final", "Grade", "Remark"]
    col_widths = [27]*7

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C")
    pdf.ln()

    for _, row in df.iterrows():
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], 10, str(val), border=1, align="C")
        pdf.ln()

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()

# --- Streamlit UI ---
st.set_page_config(page_title="Report Card Portal")
st.title("🎓 Student Report Card Portal")

role = st.selectbox("Login as", ["Student", "Admin"])
username = st.text_input("User ID")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if role == "Student":
        if username in students and password == "123456":
            st.success(f"Welcome {username}!")
            file_path = os.path.join(project_folder, f"{username}.xlsx")
            if not os.path.exists(file_path):
                st.error("Student data not found.")
            else:
                df = pd.read_excel(file_path, skiprows=8, engine='openpyxl')
                df = df.iloc[:, :7]
                df.fillna("", inplace=True)

                for i in df.index:
                    try:
                        ca1 = int(df.loc[i, "CA1"] or 0)
                        ca2 = int(df.loc[i, "CA2"] or 0)
                        exam = int(df.loc[i, "Exam"] or 0)
                        final = ca1 + ca2 + exam
                        df.loc[i, "Final"] = final
                        if final >= 75:
                            df.loc[i, "Grade"] = "A"
                            df.loc[i, "Remark"] = "Excellent"
                        elif final >= 60:
                            df.loc[i, "Grade"] = "B"
                            df.loc[i, "Remark"] = "Very Good"
                        elif final >= 50:
                            df.loc[i, "Grade"] = "C"
                            df.loc[i, "Remark"] = "Credit"
                        else:
                            df.loc[i, "Grade"] = "F"
                            df.loc[i, "Remark"] = "Failed"
                    except ValueError:
                        continue

                st.subheader(f"Report Card for {username}")
                st.dataframe(df)

                ranks = calculate_ranks()
                st.info(f"Rank: {ranks.get(username, 'N/A')} Position")

                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", data=csv, file_name="report_card.csv", mime="text/csv")

                pdf_bytes = generate_pdf(username, df, ranks.get(username, 'N/A'))
                st.download_button("Download PDF", data=pdf_bytes, file_name="report_card.pdf", mime="application/pdf")
        else:
            st.error("Invalid student credentials")

    elif role == "Admin":
        if username in admin_credentials and password == admin_credentials[username]:
            st.success("Welcome Admin!")
            st.header("📊 Student Performance Overview")
            ranks = calculate_ranks()
            for student in students:
                file_path = os.path.join(project_folder, f"{student}.xlsx")
                if os.path.exists(file_path):
                    df = pd.read_excel(file_path, skiprows=8, engine='openpyxl')
                    total = df.iloc[:, 1:4].sum(axis=1).sum()
                    st.markdown(f"**{student}** — Total Score: `{int(total)}` — Rank: `{ranks.get(student)}`")
        else:
            st.error("Invalid admin credentials")
