import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime
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

STATUS_FILE = "last_report_sent.txt"
def has_report_been_sent_today():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            last_sent_date = f.read().strip()
            return last_sent_date == str(datetime.today().date())
    return False

def mark_report_as_sent():
    with open(STATUS_FILE, "w") as f:
        f.write(str(datetime.today().date()))

def generate_csv(data):
    df = pd.DataFrame(data)
    df.to_csv("spends.csv", index=False)

def send_email_with_csv(csv_path):
    dotenv.load_dotenv()

    from_address = os.getenv("EMAIL_ADDRESS", "").strip()
    password = os.getenv("EMAIL_PASSWORD", "").strip()
    to_address = from_address  # sending to self

    if not from_address or not password:
        raise ValueError("❌ Email credentials missing! Check your .env file.")

    subject = "Monthly Report: Your Expenses Are Judging You 😂"
    body = "Attached is your full monthly expense report 🥲. Now cry accordingly."

    # Setup MIME
    message = MIMEMultipart()
    message['From'] = from_address
    message['To'] = to_address
    message['Subject'] = subject

    # Attach body
    message.attach(MIMEText(body, 'plain'))

    # Attach CSV
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