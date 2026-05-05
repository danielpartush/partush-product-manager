import streamlit as st
import gspread
import json
import pandas as pd
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Partush Product Manager", layout="wide")

st.title("Partush Product Manager")
st.caption("מצב בדיקות דמה - ללא חיבור ל-WooCommerce וללא שינוי באתר")

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
sheet_url = st.secrets["google_sheet_url"]
sheet = client.open_by_url(sheet_url)
worksheet = sheet.sheet1

data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.success("Google Sheets מחובר ועובד")

st.subheader("נתונים מה-Google Sheet")
st.dataframe(df, use_container_width=True)

st.subheader("בדיקות דמה לפני חיבור WooCommerce")

required_columns = ["מק״ט", "שם מוצר", "תיאור מוצע", "תמונה מוצעת"]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error("חסרות עמודות בגוגל שיט:")
    st.write(missing_columns)
else:
    st.success("מבנה הטבלה תקין לבדיקה")

    total_products = len(df)
    missing_description = df[df["תיאור מוצע"].astype(str).str.strip() == ""]
    missing_image = df[df["תמונה מוצעת"].astype(str).str.strip() == ""]

    col1, col2, col3 = st.columns(3)
    col1.metric("סה״כ מוצרים", total_products)
    col2.metric("חסר תיאור", len(missing_description))
    col3.metric("חסרה תמונה", len(missing_image))

    st.subheader("סימולציית פעולות שהמערכת הייתה עושה")

    actions = []

    for _, row in df.iterrows():
        sku = row.get("מק״ט", "")
        name = row.get("שם מוצר", "")
        desc = str(row.get("תיאור מוצע", "")).strip()
        image = str(row.get("תמונה מוצעת", "")).strip()

        if desc:
            actions.append({
                "מק״ט": sku,
                "שם מוצר": name,
                "פעולה": "היה מעדכן תיאור מוצר",
                "סטטוס": "דמה בלבד - לא נשלח לאתר"
            })

        if image:
            actions.append({
                "מק״ט": sku,
                "שם מוצר": name,
                "פעולה": "היה מעדכן תמונת מוצר",
                "סטטוס": "דמה בלבד - לא נשלח לאתר"
            })

    actions_df = pd.DataFrame(actions)

    if len(actions_df) > 0:
        st.dataframe(actions_df, use_container_width=True)
    else:
        st.info("אין פעולות דמה לביצוע כרגע")
