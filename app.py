import streamlit as st
import pandas as pd

st.set_page_config(page_title="בדיקת מוצרי אתר", layout="wide")

SHEET_ID = "1DLnLWYh3RX94bnbOs32d_5jke5KS33l7g030BNFBSD8"

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.title("מערכת בדיקת מוצרים - טסט ללא API")

@st.cache_data(ttl=300)
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
    st.success("הקובץ נטען בהצלחה מ-Google Sheets")
except Exception as e:
    st.error("לא הצלחתי לטעון את הקובץ. ודא שהשיתוף פתוח לכל מי שיש לו קישור כצופה.")
    st.write(e)
    st.stop()

st.write("סה״כ מוצרים:", len(df))

# ניקוי שמות עמודות
df.columns = [str(c).strip() for c in df.columns]

st.subheader("תצוגת הקובץ")
st.dataframe(df, use_container_width=True)

# זיהוי עמודות לפי מה שראיתי אצלך
name_col = "שם"
desc_col = "תיאור"
image_col = "תמונות"
sku_col = 'מק"ט'

def is_empty(value):
    return pd.isna(value) or str(value).strip() == "" or str(value).strip().lower() in ["nan", "none"]

def short_description(value):
    if is_empty(value):
        return True
    return len(str(value).strip()) < 80

def image_missing(value):
    if is_empty(value):
        return True
    text = str(value).strip()
    return not text.startswith("http")

issues = []

for index, row in df.iterrows():
    product_issues = []

    product_name = row.get(name_col, "")
    sku = row.get(sku_col, "")

    if desc_col in df.columns and short_description(row.get(desc_col, "")):
        product_issues.append("תיאור חסר או קצר מדי")

    if image_col in df.columns and image_missing(row.get(image_col, "")):
        product_issues.append("חסרה תמונה")

    if product_issues:
        issues.append({
            "שורה": index + 2,
            "מזהה": row.get("מזהה", ""),
            "מק״ט": sku,
            "שם מוצר": product_name,
            "בעיות שנמצאו": " | ".join(product_issues),
            "תיאור קיים": row.get(desc_col, ""),
            "תמונה קיימת": row.get(image_col, "")
        })

issues_df = pd.DataFrame(issues)

st.subheader("מוצרים שדורשים טיפול")

if len(issues_df) == 0:
    st.success("לא נמצאו מוצרים עם חוסרים לפי הבדיקה הנוכחית")
else:
    st.warning(f"נמצאו {len(issues_df)} מוצרים שדורשים טיפול")
    st.dataframe(issues_df, use_container_width=True)

    csv = issues_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "הורד דוח מוצרים לטיפול",
        data=csv,
        file_name="products_issues_report.csv",
        mime="text/csv"
    )
