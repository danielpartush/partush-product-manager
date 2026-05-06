import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="Partush Product Manager", layout="wide")

SHEET_ID = "1DLnLWYh3RX94bnbOs32d_5jke5KS33l7g030BNFBSD8"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.title("מערכת ניהול מוצרי האתר - פרטוש משקאות")
st.caption("גרסת טסט ללא API — לא משנה כלום באתר")

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def is_empty(v):
    if pd.isna(v):
        return True
    return str(v).strip().lower() in ["", "nan", "none", "null"]

def clean_text(v):
    if is_empty(v):
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()

def looks_cut(text):
    text = clean_text(text)
    if not text:
        return True
    if len(text) < 100:
        return True
    bad_endings = ("ו", "של", "עם", "ב", "ל", "ה", ",", "-", ":", ";")
    return text.endswith(bad_endings)

def image_missing(v):
    if is_empty(v):
        return True
    text = str(v).strip()
    return not text.startswith("http")

def detect_product_type(name, category):
    txt = f"{name} {category}".lower()

    if any(x in txt for x in ["בירה", "beer", "לאגר", "אייל", "ipa"]):
        return "בירה"
    if any(x in txt for x in ["יין", "wine", "קברנה", "מרלו", "שרדונה", "סוביניון", "רוזה", "מוסקטו"]):
        return "יין"
    if any(x in txt for x in ["וודקה", "vodka"]):
        return "וודקה"
    if any(x in txt for x in ["וויסקי", "ויסקי", "whisky", "whiskey", "בורבון"]):
        return "וויסקי"
    if any(x in txt for x in ["ערק", "arak"]):
        return "ערק"
    if any(x in txt for x in ["טקילה", "tequila"]):
        return "טקילה"
    if any(x in txt for x in ["ג׳ין", "ג'ין", "gin"]):
        return "ג׳ין"
    if any(x in txt for x in ["רום", "rum"]):
        return "רום"
    if any(x in txt for x in ["ליקר", "liqueur"]):
        return "ליקר"
    if any(x in txt for x in ["בריזר", "breezer", "קוקטייל"]):
        return "קוקטייל מוכן"
    if any(x in txt for x in ["פופקורן", "קרח"]):
        return "מוצר חנות"
    return "כללי"

def make_description(name, short_desc, category):
    name = clean_text(name)
    short_desc = clean_text(short_desc)
    category = clean_text(category)
    ptype = detect_product_type(name, category)

    if ptype == "בירה":
        text = f"{name} היא בירה מרעננת ונגישה, המתאימה לשתייה קרה, לאירוח, לערב חברים או לצד ארוחה קלילה. המוצר מציע חוויית שתייה נעימה ומאוזנת, עם אופי קל לשתייה שמתאים למגוון רחב של לקוחות."

    elif ptype == "יין":
        text = f"{name} הוא יין איכותי המתאים לארוחות, אירוח ושולחן שבת. היין מעניק חוויית שתייה נעימה ומאוזנת, ומתאים למי שמחפש בקבוק טוב ונגיש לשימוש יומיומי או לאירוע משפחתי."

    elif ptype == "וודקה":
        text = f"{name} היא וודקה איכותית בעלת אופי נקי וחלק, המתאימה לשתייה נקייה, עם קרח או כבסיס לקוקטיילים. בחירה טובה למי שמחפש משקה אלכוהולי קלאסי ונוח לשילוב באירוח."

    elif ptype == "וויסקי":
        text = f"{name} הוא וויסקי איכותי עם אופי עשיר ונוכחות מורגשת. מתאים לשתייה נקייה, עם קרח או לאירוח, ומיועד לחובבי וויסקי שמחפשים בקבוק עם חוויית שתייה נעימה ומרשימה."

    elif ptype == "ערק":
        text = f"{name} הוא ערק בעל אופי אניסי מובהק, מתאים לשתייה קרה, עם מים או קרח, ומשתלב מצוין באירוח ישראלי ובארוחות עשירות."

    elif ptype == "טקילה":
        text = f"{name} היא טקילה איכותית המתאימה לשתייה נקייה, בצ׳ייסר או כבסיס לקוקטיילים. בחירה טובה לאירוח, מסיבות וערבים עם חברים."

    elif ptype == "ג׳ין":
        text = f"{name} הוא ג׳ין איכותי המתאים לשתייה עם טוניק, קרח ותוספות כמו לימון או עשבי תיבול. מתאים במיוחד לקוקטיילים ולאירוח קליל."

    elif ptype == "רום":
        text = f"{name} הוא רום איכותי המתאים לשתייה נקייה, עם קרח או כבסיס לקוקטיילים. מתאים לאירוח ולמי שמחפש משקה עם אופי מתקתק ועשיר."

    elif ptype == "ליקר":
        text = f"{name} הוא ליקר איכותי ומתוק, המתאים לשתייה נקייה, עם קרח או לשילוב בקוקטיילים וקינוחים. בחירה טובה לאירוח ולמי שמחפש משקה נעים ונגיש."

    elif ptype == "קוקטייל מוכן":
        text = f"{name} הוא משקה מוכן לשתייה, קליל ומרענן, שמתאים במיוחד לאירוח, בילוי ושתייה קרה. פתרון נוח למי שמחפש משקה טעים וזמין בלי הכנה מיוחדת."

    elif ptype == "מוצר חנות":
        text = f"{name} הוא מוצר משלים ונוח לאירוח, מסיבות, אירועים ושימוש יומיומי. מתאים ללקוחות שמחפשים פתרון פשוט, זמין ואיכותי לצד קניית משקאות."

    else:
        text = f"{name} הוא מוצר איכותי מקטגוריית המשקאות, המתאים לאירוח, לשימוש יומיומי וללקוחות שמחפשים מוצר נגיש וברור לרכישה באתר."

    if short_desc and len(short_desc) > 20:
        text += f"\n\n{short_desc}"

    if category:
        text += f"\n\nקטגוריה: {category}"

    return text

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

    if "קטגוריות" in possible_cols:
        default_cat_index = possible_cols.index("קטגוריות")
    else:
        default_cat_index = 0

    category_col = st.selectbox("עמודת קטגוריות", possible_cols, index=default_cat_index)

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
        "סוג מוצר": detect_product_type(name, category),
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

st.dataframe(view_df, use_container_width=True, height=450)

st.divider()

st.subheader("בדיקת מוצר בודד")

if len(view_df) > 0:
    product_options = view_df["שם מוצר"].fillna("").tolist()
    selected_name = st.selectbox("בחר מוצר לבדיקה", product_options)
    selected = view_df[view_df["שם מוצר"] == selected_name].iloc[0]

    c1, c2 = st.columns([1, 2])

    with c1:
        st.write("**שם מוצר:**", selected["שם מוצר"])
        st.write("**מק״ט:**", selected["מק״ט"])
        st.write("**סוג מוצר:**", selected["סוג מוצר"])
        st.write("**קטגוריה:**", selected["קטגוריה"])
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
        st.text_area("תיאור מוצע", selected["תיאור מוצע"], height=240)

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
