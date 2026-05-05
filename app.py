import streamlit as st
import gspread
import json
import pandas as pd
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Partush Product Manager", layout="wide")

st.title("Partush Product Manager")
st.caption("מצב בדיקות דמה - ללא שינוי באתר")

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

def status_for(row):
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

for index, row in filtered_df.iterrows():
    sku = str(row.get("מק״ט", "")).strip()
    name = str(row.get("שם מוצר", "")).strip()
    desc = str(row.get("תיאור מוצע", "")).strip()
    image_url = str(row.get("תמונה מוצעת", "")).strip()

    status_text, icon = status_for(row)

    with st.container(border=True):
        st.markdown(f"## {icon} {name}")
        st.write(f"**מק״ט:** {sku}")
        st.write(f"**סטטוס:** {status_text}")

        col_text, col_image = st.columns([2, 1])

        with col_text:
            st.markdown("### תיאור מוצע")

            if is_empty(desc):
                st.warning("אין תיאור מוצע")
                desc = ""
            else:
                st.write(desc)

            manual_desc = st.text_area(
                "שינוי ידני לתיאור",
                value=desc,
                key=f"manual_desc_{sku}_{index}",
                height=160
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("✅ מאשר תיאור", key=f"approve_desc_{sku}_{index}"):
                    st.session_state[f"desc_status_{sku}_{index}"] = "תיאור אושר"

            with c2:
                if st.button("❌ לא מאשר תיאור", key=f"reject_desc_{sku}_{index}"):
                    st.session_state[f"desc_status_{sku}_{index}"] = "תיאור נדחה"

            with c3:
                if st.button("✏️ שמור שינוי ידני", key=f"save_manual_desc_{sku}_{index}"):
                    st.session_state[f"manual_saved_{sku}_{index}"] = manual_desc
                    st.session_state[f"desc_status_{sku}_{index}"] = "נשמר שינוי ידני לתיאור"

            desc_status = st.session_state.get(f"desc_status_{sku}_{index}", "ממתין לבדיקה")
            st.info(f"סטטוס תיאור: {desc_status}")

        with col_image:
            st.markdown("### תמונה מוצעת")
            st.caption("דרישה: 400×400, מוצר בלבד, ללא רקע")

            if is_empty(image_url):
                st.warning("אין תמונה מוצעת")
            else:
                st.image(image_url, width=400)
                st.link_button("פתח תמונה לבדיקה", image_url)

            st.checkbox(
                "בדקתי שהתמונה 400×400",
                key=f"img_size_ok_{sku}_{index}"
            )

            st.checkbox(
                "בדקתי שהתמונה ללא רקע",
                key=f"img_bg_ok_{sku}_{index}"
            )

            c4, c5 = st.columns(2)

            with c4:
                if st.button("✅ מאשר תמונה", key=f"approve_img_{sku}_{index}"):
                    size_ok = st.session_state.get(f"img_size_ok_{sku}_{index}", False)
                    bg_ok = st.session_state.get(f"img_bg_ok_{sku}_{index}", False)

                    if not size_ok or not bg_ok:
                        st.session_state[f"img_status_{sku}_{index}"] = "לא ניתן לאשר - חסרה בדיקת 400×400 או ללא רקע"
                    else:
                        st.session_state[f"img_status_{sku}_{index}"] = "תמונה אושרה"

            with c5:
                if st.button("❌ לא מאשר תמונה", key=f"reject_img_{sku}_{index}"):
                    st.session_state[f"img_status_{sku}_{index}"] = "תמונה נדחתה"

            img_status = st.session_state.get(f"img_status_{sku}_{index}", "ממתין לבדיקה")
            st.info(f"סטטוס תמונה: {img_status}")

        st.warning("מצב דמה בלבד — שום דבר עדיין לא נשלח לאתר או נשמר בגוגל שיט")
