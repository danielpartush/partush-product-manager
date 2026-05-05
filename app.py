import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="Partush Product Manager", layout="wide")

SHEET_ID = "1DLnLWYh3RX94bnbOs32d_5jke5KS33l7g030BNFBSD8"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.title("מערכת ניהול מוצרי האתר - פרטוש משקאות")
st.caption("גרסת טסט מלאה ללא API — לא משנה כלום באתר")

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def is_empty(v):
    return pd.isna(v) or str(v).strip() == "" or str(v).strip().lower() in ["nan", "none", "null"]

def clean_text(v):
    if is_empty(v):
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()

def looks_cut(text):
    text = clean_text(text)
    if not text:
        return True
    if len(text) < 80:
        return True
    if text.endswith(("ו", "של", "עם", "ב", "ל", "ה", ",", "-", ":", ";")):
        return True
    return False

def image_missing(v):
    if is_empty(v):
        return True
    text = str(v).strip()
    return not text.startswith("http")

def make_description(name, short_desc, category):
    name = clean_text(name)
    short_desc = clean_text(short_desc)
    category = clean_text(category)

    base = f"{name} הוא מוצר איכותי מבית פרטוש משקאות, מתאים ללקוחות שמחפשים מוצר אמין, נגיש ומוכן לשימוש יומיומי או לאירוח."
    
    if short_desc and len(short_desc) > 20:
        base += f"\n\n{short_desc}"

    if category:
        base += f"\n\nקטגוריה: {category}. מומלץ להציג באתר עם תמונה ברורה, רקע נקי ותיאור מלא שמסביר ללקוח מה הוא קונה."

    return base

try:
    df = load_data()
except Exception as e:
    st.error("לא הצלחתי לטעון את Google Sheets. ודא שהקובץ משותף כצופה לכל מי שיש לו קישור.")
    st.exception(e)
    st.stop()

st.success(f"הקובץ נטען בהצלחה — {len(df)} מוצרים")

possible_cols = list(df.columns)

with st.sidebar:
    st.header("הגדרות עמודות")

    id_col = st.selectbox("עמודת מזהה", possible_cols, index=possible_cols.index("מזהה") if "מזהה" in possible_cols else 0)
    sku_col = st.selectbox("עמודת מק״ט", possible_cols, index=possible_cols.index('מק"ט') if 'מק"ט' in possible_cols else 0)
    name_col = st.selectbox("עמודת שם מוצר", possible_cols, index=possible_cols.index("שם") if "שם" in possible_cols else 0)
    short_col = st.selectbox("עמודת תיאור קצר", possible_cols, index=possible_cols.index("תיאור קצר") if "תיאור קצר" in possible_cols else 0)
    desc_col = st.selectbox("עמודת תיאור מלא", possible_cols, index=possible_cols.index("תיאור") if "תיאור" in possible_cols else 0)
    image_col = st.selectbox("עמודת תמונות", possible_cols, index=possible_cols.index("תמונות") if "תמונות" in possible_cols else 0)
    category_col = st.selectbox("עמודת קטגוריות", possible_cols, index=possible_cols.index("קטגוריות") if "קטגוריות" in possible_cols else 0)

    st.divider()
    min_desc_len = st.slider("אורך מינימלי לתיאור תקין", 50, 400, 120)

records = []

for idx, row in df.iterrows():
    name = clean_text(row.get(name_col, ""))
    sku = clean_text(row.get(sku_col, ""))
    desc = clean_text(row.get(desc_col, ""))
    short_desc = clean_text(row.get(short_col, ""))
    image = clean_text(row.get(image_col, ""))
    category = clean_text(row.get(category_col, ""))

    problems = []

    if is_empty(desc):
        problems.append("תיאור חסר")
    elif len(desc) < min_desc_len:
        problems.append("תיאור קצר מדי")
    elif looks_cut(desc):
        problems.append("תיאור נראה חתוך")

    if image_missing(image):
        problems.append("חסרה תמונה")

    status = "תקין" if not problems else "דורש טיפול"

    records.append({
        "שורה": idx + 2,
        "מזהה": row.get(id_col, ""),
        "מק״ט": sku,
        "שם מוצר": name,
        "קטגוריה": category,
        "סטטוס": status,
        "בעיות": " | ".join(problems),
        "תיאור קצר": short_desc,
        "תיאור קיים": desc,
        "תמונה קיימת": image,
        "תיאור מוצע": make_description(name, short_desc, category) if problems else "",
        "סטטוס עבודה": "ממתין לבדיקה" if problems else "תקין"
    })

result_df = pd.DataFrame(records)
issues_df = result_df[result_df["סטטוס"] == "דורש טיפול"].copy()
ok_df = result_df[result_df["סטטוס"] == "תקין"].copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("סה״כ מוצרים", len(result_df))
col2.metric("דורשים טיפול", len(issues_df))
col3.metric("תקינים", len(ok_df))
col4.metric("אחוז טיפול", f"{round(len(issues_df) / max(len(result_df), 1) * 100, 1)}%")

st.divider()

st.subheader("חיפוש וסינון")

search = st.text_input("חפש לפי שם מוצר / מק״ט / מזהה")

filter_type = st.radio(
    "בחר תצוגה",
    ["דורשים טיפול", "חסרה תמונה", "תיאור חסר/קצר", "תקינים", "הכול"],
    horizontal=True
)

view_df = result_df.copy()

if filter_type == "דורשים טיפול":
    view_df = view_df[view_df["סטטוס"] == "דורש טיפול"]
elif filter_type == "חסרה תמונה":
    view_df = view_df[view_df["בעיות"].str.contains("חסרה תמונה", na=False)]
elif filter_type == "תיאור חסר/קצר":
    view_df = view_df[view_df["בעיות"].str.contains("תיאור", na=False)]
elif filter_type == "תקינים":
    view_df = view_df[view_df["סטטוס"] == "תקין"]

if search:
    s = search.lower()
    view_df = view_df[
        view_df["שם מוצר"].astype(str).str.lower().str.contains(s, na=False) |
        view_df["מק״ט"].astype(str).str.lower().str.contains(s, na=False) |
        view_df["מזהה"].astype(str).str.lower().str.contains(s, na=False)
    ]

st.write(f"נמצאו {len(view_df)} מוצרים בתצוגה הנוכחית")

st.dataframe(
    view_df,
    use_container_width=True,
    height=500
)

st.divider()

st.subheader("בדיקת מוצר בודד")

if len(view_df) > 0:
    selected_name = st.selectbox("בחר מוצר לבדיקה", view_df["שם מוצר"].fillna("").tolist())
    selected = view_df[view_df["שם מוצר"] == selected_name].iloc[0]

    c1, c2 = st.columns([1, 2])

    with c1:
        st.write("**שם מוצר:**", selected["שם מוצר"])
        st.write("**מק״ט:**", selected["מק״ט"])
        st.write("**סטטוס:**", selected["סטטוס"])
        st.write("**בעיות:**", selected["בעיות"])

        img = selected["תמונה קיימת"]
        if isinstance(img, str) and img.startswith("http"):
            first_img = img.split(",")[0].strip()
            st.image(first_img, caption="תמונה קיימת", width=250)
        else:
            st.warning("אין תמונה תקינה להצגה")

    with c2:
        st.write("**תיאור קיים:**")
        st.text_area("תיאור קיים", selected["תיאור קיים"], height=180)

        st.write("**תיאור מוצע:**")
        st.text_area("תיאור מוצע", selected["תיאור מוצע"], height=220)

st.divider()

st.subheader("ייצוא דוחות")

now = datetime.now().strftime("%Y-%m-%d_%H-%M")

csv_issues = issues_df.to_csv(index=False).encode("utf-8-sig")
csv_all = result_df.to_csv(index=False).encode("utf-8-sig")

c1, c2 = st.columns(2)

with c1:
    st.download_button(
        "הורד דוח מוצרים שדורשים טיפול",
        data=csv_issues,
        file_name=f"partush_products_issues_{now}.csv",
        mime="text/csv"
    )

with c2:
    st.download_button(
        "הורד דוח מלא",
        data=csv_all,
        file_name=f"partush_products_full_report_{now}.csv",
        mime="text/csv"
    )
