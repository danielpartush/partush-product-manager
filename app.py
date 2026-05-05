import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Partush Product Manager", layout="wide")

st.title("Partush Product Manager")
st.write("בדיקת חיבור ל-Google Sheets")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

import json

service_account_info = json.loads(st.secrets["gcp_service_account_json"])

credentials = Credentials.from_service_account_info(
    service_account_info,
    scopes=SCOPES
)
client = gspread.authorize(credentials)

sheet_url = st.secrets["google_sheet_url"]
sheet = client.open_by_url(sheet_url)

worksheet = sheet.sheet1
data = worksheet.get_all_records()

st.success("החיבור ל-Google Sheets עובד!")

st.write("כמות שורות שנמצאו:", len(data))
st.dataframe(data)
