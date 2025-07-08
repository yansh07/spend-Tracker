# 🔹 Phase 1: Core App UI
#  Greeting + Name

#  Random sarcastic line or meme

#  Buttons: Add, List, Edit, Delete

# 🔹 Phase 2: Data Handling
#  Spend entry form

#  List current month's spends

#  Edit & delete via dropdown or row ID

# 🔹 Phase 3: Monthly Auto Report
#  At month-end, detect last month's data

#  Export CSV or Text file

#  Email or save locally

#  Delete after export

# import os
# import pandas
# import dotenv
import gspread
from google.oauth2.service_account import Credentials

# Define the scope
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Load credentials from JSON keyfile
creds = Credentials.from_service_account_file("gcp_service_account.json", scopes=scope)

# Authorize the client
client = gspread.authorize(creds)

# Open your sheet
sheet = client.open("SpendTracker").sheet1

# Write a test row
sheet.append_row(["2025-07-08", "Test Category", 100, "Test note"])

# Read back the data
data = sheet.get_all_records()
print(data)
