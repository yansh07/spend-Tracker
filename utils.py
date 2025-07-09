import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import dotenv

def get_sheet(cred_json, spreadsheet_name):
    scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("SpendTracker").sheet1
    return sheet

SPREADSHEET_NAME = "SpendTracker"
CRED_FILE = "./gcp_service_account.json"

sheet = get_sheet(CRED_FILE, SPREADSHEET_NAME)

def read_data():
    sheet = get_sheet(CRED_FILE, SPREADSHEET_NAME)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def add_spend(row):
    sheet = get_sheet(CRED_FILE, SPREADSHEET_NAME)
    sheet.append_row(row)

def get_all_spends():
    sheet = get_sheet(CRED_FILE, SPREADSHEET_NAME)
    data = sheet.get_all_records()
    return data

def clear_sheet_data():
    sheet = get_sheet(CRED_FILE, SPREADSHEET_NAME)
    all_data = sheet.get_all_values()
    num_rows = len(all_data)

    if num_rows <=1:
        return
    for i in range(num_rows, 1, -1):
        sheet.delete_rows(i)

def generate_csv(data):
    df = pd.DataFrame(data)
    df.to_csv("spends.csv", index=False)

def send_email_with_csv(csv_path):
    dotenv.load_dotenv()

    from_address = os.getenv("EMAIL_ADDRESS")
    to_address = from_address  # sending to self
    password = os.getenv("EMAIL_PASSWORD")

    subject = "Monthly Report: Your Expenses Are Judging You 😂"
    body = "Attached is your full monthly expense report 🥲. Now cry accordingly."

    # Setup MIME
    message = MIMEMultipart()
    from_address = os.getenv("EMAIL_ADDRESS", "").strip()
    password = os.getenv("EMAIL_PASSWORD", "").strip()

    if not from_address or not password:
        raise ValueError("❌ Email credentials missing! Check your .env file.")

    message['Subject'] = subject

    # Attach body
    message.attach(MIMEText(body, 'plain'))

    # Open file in binary mode and attach
    with open(csv_path, "rb") as file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(csv_path)}"')
        message.attach(part)

    # Send email using Gmail SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_address, password)
    server.send_message(message)
    server.quit()
    print("📬 Email sent successfully!")