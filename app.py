import streamlit as st
import gspread
import json
import pandas as pd
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Partush Product Manager", layout="wide")

st.title("Partush Product Manager")
st.caption("מצב בדיקות דמה - ללא חיבור WooCommerce וללא שינוי באתר")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

service_account_info = json.loads(st.secrets["gcp_service_account_json"])

credentials = Credentials.from_service_account_info(
    service_account_info,
    scopes=SCOPES
)

client = gspread.authorize(credentials)
sheet = client.open_by_url(st.secrets["google_sheet_url"])
worksheet = sheet.sheet1

data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.success("Google Sheets מחובר כמקור נתונים פנימי")

required_columns = ["מק״ט", "שם מוצר", "תיאור מוצע", "תמונה מוצעת"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error("חסרות עמודות חובה בגוגל שיט:")
    st.write(missing_columns)
    st.stop()

def is_empty(value):
    return str(value).strip() == "" or str(value).strip().lower() == "nan"

def product_status(row):
    problems = []

    if is_empty(row.get("תיאור מוצע", "")):
        problems.append("חסר תיאור")

    if is_empty(row.get("תמונה מוצעת", "")):
        problems.append("חסרה תמונה")

    if not problems:
        return "מוכן לבדיקה", "✅"

    return " / ".join(problems), "⚠️"

st.subheader("מוצרים לשדרוג")

search = st.text_input("חיפוש לפי שם מוצר או מק״ט")

filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["שם מוצר"].astype(str).str.contains(search, case=False, na=False) |
        filtered_df["מק״ט"].astype(str).str.contains(search, case=False, na=False)
    ]

for _, row in filtered_df.iterrows():
    status_text, icon = product_status(row)

    with st.container(border=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"### {icon} {row.get('שם מוצר', '')}")
            st.write(f"**מק״ט:** {row.get('מק״ט', '')}")
            st.write(f"**סטטוס:** {status_text}")

            desc = row.get("תיאור מוצע", "")

            if not is_empty(desc):
                st.markdown("**תיאור מוצע:**")
                st.write(desc)
            else:
                st.warning("אין תיאור מוצע למוצר הזה")

        with col2:
            image_url = row.get("תמונה מוצעת", "")

            if not is_empty(image_url):
                st.markdown("**תמונה מוצעת:**")
                st.image(image_url, use_container_width=True)
            else:
                st.warning("אין תמונה מוצעת")

        st.info("מצב דמה בלבד — לא נשלח שום שינוי לאתר")
