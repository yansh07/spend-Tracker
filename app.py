from utils import read_data, add_spend, get_all_spends, clear_sheet_data, generate_csv, send_email_with_csv
import pandas as pd
import streamlit as st
import datetime
import calendar
import os
import dotenv
dotenv.load_dotenv()

ACCESS_PHRASE = os.getenv("ACCESS_PHRASE")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Spend Tracker Locked")
    phrase_input = st.text_input("Enter the secret phrase to unlock:", type="password")

    if phrase_input:
        if phrase_input == ACCESS_PHRASE:
            st.session_state.authenticated = True
            st.success("✅ Access granted. Welcome!")
            st.rerun()  #Refreshes the app to hide login UI
        else:
            st.error("❌ Invalid phrase. Try again.")
    st.stop() #if not authenticated, rest of code will not render

name = "Priyanshu"
current_time = datetime.datetime.now()

if current_time.hour < 12:
    st.markdown(f"<h1 style='text-align: center;'>Good Morning 🌅, {name}</h1>", unsafe_allow_html=True)
elif current_time.hour > 12 and current_time.hour < 18:
    st.markdown(f"<h1 style='text-align: center;'>Good Afternoon 🌞, {name}</h1>", unsafe_allow_html=True)
else:
    st.markdown(f"<h1 style='text-align: center;'>Good Evening 🌃, {name}</h1>", unsafe_allow_html=True)

import pandas as pd

with st.sidebar:
    st.header("Add your spend 💸")

    with st.expander("➕ Data idhar daal", expanded=False):
        with st.form(key="data_form"):
            date = st.date_input("Date")
            category = st.selectbox("Choose a category", ("Gain", "Loss", "Borrow"))
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            note = st.text_input("Note")

            submit = st.form_submit_button("Submit")

            if submit:
                row = [str(date), category, amount, note]
                add_spend(row)
                st.success("Spend Added Successfully 🎉")

    st.header("Your total spends 🖩")
    data = get_all_spends()
    if data:
        df = pd.DataFrame(data)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        total_gain = df[df["category"] == "Gain"]["amount"].sum()
        total_loss = df[df["category"] == "Loss"]["amount"].sum()
        total_borrow = df[df["category"] == "Borrow"]["amount"].sum()
        st.metric("Total Gain 💰", f"₹ {total_gain:,.2f}")
        st.metric("Total Loss 🧾", f"₹ {total_loss:,.2f}")
        st.metric("Total Borrowed 💳", f"₹ {total_borrow:,.2f}")
    else:
        st.info("No data yet to analyze.")

with st.sidebar:
  if st.session_state.get("authenticated", False):
      if st.button("🔒 Logout"):
          st.session_state.clear()
          st.success("You have been logged out.")
          st.rerun()

today = datetime.datetime.today()
last_day = calendar.monthrange(today.year, today.month)[1]

if today.day == last_day:
    data = get_all_spends()
    generate_csv(data)
    send_email_with_csv("spends.csv")
    clear_sheet_data()
    st.success("✅ Monthly report sent to your inbox!")

st.markdown("<h3 style='text-align: center:'>Your balance table 💰</h3>", unsafe_allow_html=True)
data = get_all_spends()
df = pd.DataFrame(data)
st.dataframe(df)