import streamlit as st
import gspread
import json
import pandas as pd
import requests
from io import BytesIO
from PIL import Image
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Partush Product Manager", layout="wide")

st.title("Partush Product Manager")
st.caption("סימולציית WooCommerce מלאה - מצב דמה בלבד, ללא שינוי באתר")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

service_account_info = json.loads(st.secrets["gcp_service_account_json"])
credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

client = gspread.authorize(credentials)
sheet = client.open_by_url(st.secrets["google_sheet_url"])
worksheet = sheet.sheet1

data = worksheet.get_all_records()
df = pd.DataFrame(data)

required_columns = [
    "מק״ט",
    "שם מוצר",
    "סטטוס מוצר",
    "תיאור קיים באתר",
    "תמונה קיימת באתר",
    "תיאור מוצע",
    "תמונה מוצעת"
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error("חסרות עמודות חובה בגוגל שיט:")
    st.write(missing_columns)
    st.stop()

def is_empty(value):
    return str(value).strip() == "" or str(value).strip().lower() == "nan"

@st.cache_data(show_spinner=False)
def check_image_requirements(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content)).convert("RGBA")
        width, height = image.size
        is_400x400 = width == 400 and height == 400

        alpha = image.getchannel("A")
        has_transparency = alpha.getextrema()[0] < 255

        return {
            "ok": True,
            "width": width,
            "height": height,
            "is_400x400": is_400x400,
            "has_transparency": has_transparency,
            "can_use": is_400x400 and has_transparency,
            "error": ""
        }

    except Exception as e:
        return {
            "ok": False,
            "width": 0,
            "height": 0,
            "is_400x400": False,
            "has_transparency": False,
            "can_use": False,
            "error": str(e)
        }

def image_status_text(check):
    if check is None:
        return "אין תמונה"
    if not check["ok"]:
        return "קישור תמונה לא תקין"
    if check["can_use"]:
        return "תמונה תקינה"
    problems = []
    if not check["is_400x400"]:
        problems.append("לא 400×400")
    if not check["has_transparency"]:
        problems.append("עם רקע")
    return " / ".join(problems)

st.success("Google Sheets מחובר כמקור נתונים פנימי")

st.subheader("סימולציית אתר מול הצעות מערכת")

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
    product_status = str(row.get("סטטוס מוצר", "")).strip()

    site_desc = str(row.get("תיאור קיים באתר", "")).strip()
    site_image = str(row.get("תמונה קיימת באתר", "")).strip()

    suggested_desc = str(row.get("תיאור מוצע", "")).strip()
    suggested_image = str(row.get("תמונה מוצעת", "")).strip()

    site_img_check = None if is_empty(site_image) else check_image_requirements(site_image)
    suggested_img_check = None if is_empty(suggested_image) else check_image_requirements(suggested_image)

    is_new_product = product_status == "מוצר חדש"
    is_existing_product = product_status == "קיים באתר"

    needs_desc_update = not is_empty(suggested_desc) and suggested_desc != site_desc
    site_image_bad = site_img_check is None or not site_img_check["can_use"]
    suggested_image_good = suggested_img_check is not None and suggested_img_check["can_use"]

    if is_new_product:
        title_icon = "🆕"
        main_status = "מוצר חדש - נדרש תיאור ותמונה תקינה"
    elif is_existing_product:
        title_icon = "✅"
        main_status = "מוצר קיים באתר - שדרוג מבוקר"
    else:
        title_icon = "⚠️"
        main_status = "סטטוס מוצר לא מוגדר"

    with st.container(border=True):
        st.markdown(f"## {title_icon} {name}")
        st.write(f"**מק״ט:** {sku}")
        st.write(f"**סטטוס מוצר:** {product_status}")
        st.info(main_status)

        col_site, col_suggested = st.columns(2)

        with col_site:
            st.markdown("### מצב קיים באתר")

            st.markdown("**תיאור קיים באתר:**")
            if is_empty(site_desc):
                st.warning("אין תיאור קיים באתר")
            else:
                st.write(site_desc)

            st.markdown("**תמונה קיימת באתר:**")
            if is_empty(site_image):
                st.warning("אין תמונה קיימת באתר")
            else:
                st.image(site_image, width=260)
                st.link_button("פתח תמונה קיימת", site_image)

                if site_img_check and site_img_check["ok"]:
                    st.write(f"מידות: {site_img_check['width']}×{site_img_check['height']}")
                    if site_img_check["can_use"]:
                        st.success("✅ תמונת האתר תקינה")
                    else:
                        st.error(f"❌ תמונת האתר דורשת החלפה: {image_status_text(site_img_check)}")
                else:
                    st.error("❌ תמונת האתר שבורה / לא ניתנת לבדיקה")

        with col_suggested:
            st.markdown("### הצעת מערכת")

            st.markdown("**תיאור מוצע:**")
            if is_empty(suggested_desc):
                st.warning("אין תיאור מוצע")
            else:
                st.write(suggested_desc)

            edit_key = f"edit_desc_mode_{sku}_{index}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("✅ מאשר תיאור", key=f"approve_desc_{sku}_{index}"):
                    st.session_state[f"desc_status_{sku}_{index}"] = "תיאור אושר"

            with c2:
                if st.button("❌ לא מאשר תיאור", key=f"reject_desc_{sku}_{index}"):
                    st.session_state[f"desc_status_{sku}_{index}"] = "תיאור נדחה"

            with c3:
                if st.button("✏️ שינוי תיאור ידני", key=f"open_manual_desc_{sku}_{index}"):
                    st.session_state[edit_key] = True

            if st.session_state[edit_key]:
                manual_desc = st.text_area(
                    "עריכת תיאור ידנית",
                    value=suggested_desc,
                    key=f"manual_desc_{sku}_{index}",
                    height=180
                )

                save_col, cancel_col = st.columns(2)

                with save_col:
                    if st.button("💾 שמור תיאור", key=f"save_manual_desc_{sku}_{index}"):
                        row_number = index + 2
                        desc_col_number = df.columns.get_loc("תיאור מוצע") + 1
                        worksheet.update_cell(row_number, desc_col_number, manual_desc)

                        st.session_state[f"desc_status_{sku}_{index}"] = "התיאור הידני נשמר בגוגל שיט"
                        st.session_state[edit_key] = False
                        st.success("התיאור נשמר בהצלחה")
                        st.rerun()

                with cancel_col:
                    if st.button("בטל עריכה", key=f"cancel_manual_desc_{sku}_{index}"):
                        st.session_state[edit_key] = False
                        st.rerun()

            st.info(f"סטטוס תיאור: {st.session_state.get(f'desc_status_{sku}_{index}', 'ממתין לבדיקה')}")

            st.markdown("**תמונה מוצעת:**")
            if is_empty(suggested_image):
                st.warning("אין תמונה מוצעת")
            else:
                st.image(suggested_image, width=260)
                st.link_button("פתח תמונה מוצעת", suggested_image)

                if suggested_img_check and suggested_img_check["ok"]:
                    st.write(f"מידות: {suggested_img_check['width']}×{suggested_img_check['height']}")

                    if suggested_img_check["is_400x400"]:
                        st.success("✅ 400×400")
                    else:
                        st.error("❌ לא 400×400")

                    if suggested_img_check["has_transparency"]:
                        st.success("✅ ללא רקע")
                    else:
                        st.error("❌ יש רקע")

                    if suggested_img_check["can_use"]:
                        st.success("✅ התמונה המוצעת עומדת בתנאים")
                    else:
                        st.error("⛔ אי אפשר להשתמש בתמונה הזאת באתר")
                else:
                    st.error("❌ לא ניתן לבדוק את התמונה המוצעת")

            c4, c5 = st.columns(2)

            with c4:
                if st.button("✅ מאשר תמונה", key=f"approve_img_{sku}_{index}"):
                    if suggested_image_good:
                        st.session_state[f"img_status_{sku}_{index}"] = "תמונה אושרה"
                    else:
                        st.session_state[f"img_status_{sku}_{index}"] = "לא ניתן לאשר - התמונה לא עומדת בתנאים"

            with c5:
                if st.button("❌ לא מאשר תמונה", key=f"reject_img_{sku}_{index}"):
                    st.session_state[f"img_status_{sku}_{index}"] = "תמונה נדחתה"

            st.info(f"סטטוס תמונה: {st.session_state.get(f'img_status_{sku}_{index}', 'ממתין לבדיקה')}")

        st.markdown("### החלטת סימולציה")

        desc_approved = st.session_state.get(f"desc_status_{sku}_{index}") in [
            "תיאור אושר",
            "התיאור הידני נשמר בגוגל שיט"
        ]

        img_approved = st.session_state.get(f"img_status_{sku}_{index}") == "תמונה אושרה"

        if is_new_product:
            if desc_approved and img_approved and suggested_image_good:
                st.success("✅ סימולציה: המוצר החדש מוכן להקמה באתר")
            else:
                st.error("⛔ סימולציה: מוצר חדש לא מוכן. חובה לאשר תיאור ותמונה תקינה")

        elif is_existing_product:
            if site_image_bad:
                st.warning("⚠️ תמונת האתר לא תקינה — מותר להציע החלפת תמונה")
            else:
                st.info("✅ תמונת האתר תקינה — לא נחליף תמונה בלי צורך")

            actions = []

            if desc_approved and needs_desc_update:
                actions.append("עדכון תיאור באתר")

            if site_image_bad and img_approved and suggested_image_good:
                actions.append("החלפת תמונה באתר")

            if not actions:
                st.info("אין פעולות מוכנות לשליחה")
            else:
                st.success("פעולות שהיו נשלחות ל-WooCommerce:")
                for action in actions:
                    st.write(f"• {action}")

        else:
            st.error("יש למלא סטטוס מוצר: קיים באתר / מוצר חדש")

        if st.button("🧪 מדמה שליחה ל-WooCommerce", key=f"simulate_send_{sku}_{index}"):
            st.session_state[f"simulate_status_{sku}_{index}"] = "בוצעה סימולציה בלבד - לא נשלח כלום לאתר"

        st.warning(st.session_state.get(
            f"simulate_status_{sku}_{index}",
            "מצב דמה בלבד — שום דבר לא נשלח לאתר"
        ))
