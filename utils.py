import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime
import requests
from dotenv import load_dotenv

# === Google Sheet Config ===
SPREADSHEET_NAME = "SpendTracker"
CRED_FILE = "./gcp_service_account.json"

def get_sheet(cred_json, spreadsheet_name):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope
    )
    client = gspread.authorize(creds)
    sheet = client.open(spreadsheet_name).sheet1
    return sheet

# === Sheet Operations ===

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

    if num_rows <= 1:
        return
    for i in range(num_rows, 1, -1):
        sheet.delete_rows(i)


def send_telegram_message(message):
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise ValueError("❌ Telegram credentials missing in .env file")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("📲 Telegram message sent!")
    else:
        print(f"⚠️ Telegram error: {response.text}")

def get_monthly_summary(data):
    df = pd.DataFrame(data)

    # 🧹 Normalize column names safely
    df.columns = [str(col).strip().lower() for col in df.columns]

    if "amount" not in df.columns or "category" not in df.columns:
        return "⚠️ Monthly summary cannot be created. 'Amount' or 'Category' column missing."

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    total_gain = df[df["category"] == "Gain"]["amount"].sum()
    total_loss = df[df["category"] == "Loss"]["amount"].sum()
    total_borrow = df[df["category"] == "Borrow"]["amount"].sum()

    message = (
        "*📊 Monthly Spend Summary:*\n\n"
        f"💰 *Total Gain:* ₹ {total_gain:,.2f}\n"
        f"🧾 *Total Loss:* ₹ {total_loss:,.2f}\n"
        f"💳 *Total Borrowed:* ₹ {total_borrow:,.2f}"
    )
    return message


STATUS_FILE = "last_report_sent.txt"

def has_report_been_sent_today():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            last_sent = f.read().strip()
            return last_sent == str(datetime.today().date())
    return False

def mark_report_as_sent():
    with open(STATUS_FILE, "w") as f:
        f.write(str(datetime.today().date()))
