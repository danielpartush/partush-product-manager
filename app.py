import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(
    page_title="Partush Product Manager",
    page_icon="🍷",
    layout="wide"
)

SHEET_ID = "1DLnLWYh3RX94bnbOs32d_5jke5KS33l7g030BNFBSD8"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# ---------- CSS ----------
st.markdown("""
<style>
.main-title {
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 5px;
}
.sub-title {
    color: #666;
    font-size: 16px;
    margin-bottom: 25px;
}
.card {
    background: #ffffff;
    border: 1px solid #e6e6e6;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    margin-bottom: 18px;
}
.status-bad {
    background: #fff3cd;
    color: #856404;
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 700;
}
.status-ok {
    background: #d4edda;
    color: #155724;
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 700;
}
.problem {
    background: #ffe5e5;
    color: #9b1c1c;
    padding: 7px 12px;
    border-radius: 10px;
    display: inline-block;
    margin: 3px;
    font-weight: 600;
}
.small-muted {
    color: #777;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ---------- HELPERS ----------
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

def image_missing(v):
    if is_empty(v):
        return True
    return not str(v).strip().startswith("http")

def looks_cut(text):
    text = clean_text(text)
    if not text:
        return True
    if len(text) < 120:
        return True
    bad_endings = ("ו", "של", "עם", "ב", "ל", "ה", ",", "-", ":", ";")
    return text.endswith(bad_endings)

def detect_product_type(name, category):
    txt = f"{name} {category}".lower()

    if any(x in txt for x in ["בריזר", "breezer", "קוקטייל"]):
        return "קוקטייל מוכן"
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
    if any(x in txt for x in ["פופקורן", "קרח"]):
        return "מוצר חנות"

    return "כללי"

def make_description(name, short_desc, category):
    name = clean_text(name)
    short_desc = clean_text(short_desc)
    category = clean_text(category)
    ptype = detect_product_type(name, category)

    templates = {
        "קוקטייל מוכן": f"{name} הוא משקה מוכן לשתייה, קליל ומרענן, שמתאים במיוחד לאירוח, בילוי ושתייה קרה. פתרון נוח למי שמחפש משקה טעים וזמין בלי צורך בהכנה מיוחדת.",
        "בירה": f"{name} היא בירה מרעננת ונגישה, המתאימה לשתייה קרה, לאירוח, לערב חברים או לצד ארוחה קלילה. המוצר מציע חוויית שתייה נעימה ומאוזנת.",
        "יין": f"{name} הוא יין איכותי המתאים לארוחות, אירוח ושולחן שבת. היין מעניק חוויית שתייה נעימה ומאוזנת, ומתאים למי שמחפש בקבוק טוב ונגיש.",
        "וודקה": f"{name} היא וודקה איכותית בעלת אופי נקי וחלק, המתאימה לשתייה נקייה, עם קרח או כבסיס לקוקטיילים.",
        "וויסקי": f"{name} הוא וויסקי איכותי עם אופי עשיר ונוכחות מורגשת. מתאים לשתייה נקייה, עם קרח או לאירוח.",
        "ערק": f"{name} הוא ערק בעל אופי אניסי מובהק, מתאים לשתייה קרה, עם מים או קרח, ומשתלב מצוין באירוח ישראלי ובארוחות עשירות.",
        "טקילה": f"{name} היא טקילה איכותית המתאימה לשתייה נקייה, בצ׳ייסר או כבסיס לקוקטיילים. בחירה טובה לאירוח, מסיבות וערבים עם חברים.",
        "ג׳ין": f"{name} הוא ג׳ין איכותי המתאים לשתייה עם טוניק, קרח ותוספות כמו לימון או עשבי תיבול. מתאים במיוחד לקוקטיילים ולאירוח קליל.",
        "רום": f"{name} הוא רום איכותי המתאים לשתייה נקייה, עם קרח או כבסיס לקוקטיילים. מתאים לאירוח ולמי שמחפש משקה עם אופי מתקתק ועשיר.",
        "ליקר": f"{name} הוא ליקר איכותי ומתוק, המתאים לשתייה נקייה, עם קרח או לשילוב בקוקטיילים וקינוחים.",
        "מוצר חנות": f"{name} הוא מוצר משלים ונוח לאירוח, מסיבות, אירועים ושימוש יומיומי.",
        "כללי": f"{name} הוא מוצר איכותי מקטגוריית המשקאות, המתאים לאירוח, לשימוש יומיומי וללקוחות שמחפשים מוצר נגיש וברור לרכישה באתר."
    }

    text = templates.get(ptype, templates["כללי"])

    if short_desc and len(short_desc) > 25 and short_desc not in text:
        text += f"\n\n{short_desc}"

    return text

def find_col(cols, options, fallback=0):
    for opt in options:
        if opt in cols:
            return cols.index(opt)
    return fallback

# ---------- SESSION ----------
if "approved" not in st.session_state:
    st.session_state.approved = []

if "rejected" not in st.session_state:
    st.session_state.rejected = []

# ---------- LOAD ----------
try:
    df = load_data()
except Exception as e:
    st.error("לא הצלחתי לטעון את Google Sheets. ודא שהקובץ פתוח לצפייה לכל מי שיש לו קישור.")
    st.exception(e)
    st.stop()

cols = list(df.columns)

# ---------- HEADER ----------
st.markdown('<div class="main-title">🍷 Partush Product Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">מערכת בדיקה, השלמה ואישור מוצרים לפני חיבור אמיתי ל־WooCommerce</div>', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ הגדרות מערכת")

    id_col = st.selectbox("עמודת מזהה", cols, index=find_col(cols, ["מזהה", "ID", "id"]))
    sku_col = st.selectbox("עמודת מק״ט / ברקוד", cols, index=find_col(cols, ['מק"ט', "SKU", "sku"]))
    name_col = st.selectbox("עמודת שם מוצר", cols, index=find_col(cols, ["שם", "Name", "name"]))
    short_col = st.selectbox("עמודת תיאור קצר", cols, index=find_col(cols, ["תיאור קצר", "Short description"]))
    desc_col = st.selectbox("עמודת תיאור מלא", cols, index=find_col(cols, ["תיאור", "Description"]))
    image_col = st.selectbox("עמודת תמונות", cols, index=find_col(cols, ["תמונות", "Images", "images"]))

    category_index = find_col(cols, ["קטגוריות", "Categories", "categories"], 0)
    category_col = st.selectbox("עמודת קטגוריות", cols, index=category_index)

    min_desc_len = st.slider("אורך מינימלי לתיאור תקין", 80, 400, 120)

    st.divider()
    st.info("בשלב הזה אין עדכון באתר. רק אישור והכנת קובץ עבודה.")

# ---------- BUILD DATA ----------
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
        "מזהה": clean_text(row.get(id_col, "")),
        "מק״ט": sku,
        "שם מוצר": name,
        "קטגוריה": category,
        "סוג מוצר": detect_product_type(name, category),
        "סטטוס": status,
        "בעיות": " | ".join(problems),
        "תיאור קצר": short_desc,
        "תיאור קיים": desc,
        "תמונה קיימת": image,
        "תיאור מוצע": make_description(name, short_desc, category),
        "קישור תמונה מוצעת": ""
    })

result_df = pd.DataFrame(records)
issues_df = result_df[result_df["סטטוס"] == "דורש טיפול"].copy()
ok_df = result_df[result_df["סטטוס"] == "תקין"].copy()

# ---------- METRICS ----------
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("סה״כ מוצרים", len(result_df))
m2.metric("דורשים טיפול", len(issues_df))
m3.metric("תקינים", len(ok_df))
m4.metric("אושרו עכשיו", len(st.session_state.approved))
m5.metric("נדחו לבדיקה", len(st.session_state.rejected))

st.divider()

# ---------- FILTERS ----------
st.subheader("🔎 מרכז עבודה")

c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    search = st.text_input("חיפוש לפי שם / מק״ט / מזהה", placeholder="לדוגמה: בריזר, 501067, קברנה")

with c2:
    filter_type = st.selectbox(
        "סטטוס",
        ["דורשים טיפול", "חסרה תמונה", "תיאור חסר/קצר", "תקינים", "הכול"]
    )

with c3:
    type_filter = st.selectbox(
        "סוג מוצר",
        ["הכול"] + sorted(result_df["סוג מוצר"].dropna().unique().tolist())
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

if type_filter != "הכול":
    view_df = view_df[view_df["סוג מוצר"] == type_filter]

if search:
    s = search.lower()
    view_df = view_df[
        view_df["שם מוצר"].astype(str).str.lower().str.contains(s, na=False) |
        view_df["מק״ט"].astype(str).str.lower().str.contains(s, na=False) |
        view_df["מזהה"].astype(str).str.lower().str.contains(s, na=False)
    ]

st.write(f"נמצאו **{len(view_df)}** מוצרים בתצוגה הנוכחית")

# ---------- PRODUCT CARD ----------
if len(view_df) == 0:
    st.warning("לא נמצאו מוצרים לפי הסינון הנוכחי.")
else:
    product_labels = [
        f"{r['שם מוצר']} | מק״ט: {r['מק״ט']} | {r['בעיות']}"
        for _, r in view_df.iterrows()
    ]

    selected_label = st.selectbox("בחר מוצר לעבודה", product_labels)
    selected_index = product_labels.index(selected_label)
    selected = view_df.iloc[selected_index]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    top1, top2 = st.columns([1, 2])

    with top1:
        st.markdown(f"### {selected['שם מוצר']}")
        st.write(f"**מק״ט:** {selected['מק״ט']}")
        st.write(f"**מזהה:** {selected['מזהה']}")
        st.write(f"**סוג מוצר:** {selected['סוג מוצר']}")
        st.write(f"**קטגוריה:** {selected['קטגוריה']}")

        if selected["סטטוס"] == "תקין":
            st.markdown('<span class="status-ok">תקין</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-bad">דורש טיפול</span>', unsafe_allow_html=True)

        st.markdown("#### בעיות")
        if selected["בעיות"]:
            for p in selected["בעיות"].split(" | "):
                st.markdown(f'<span class="problem">{p}</span>', unsafe_allow_html=True)
        else:
            st.success("לא נמצאו בעיות")

        st.markdown("#### תמונה קיימת")
        img = selected["תמונה קיימת"]
        if isinstance(img, str) and img.startswith("http"):
            st.image(img.split(",")[0].strip(), width=260)
        else:
            st.warning("אין תמונה קיימת תקינה")

    with top2:
        st.markdown("### עריכת מוצר לאישור")

        current_desc = st.text_area(
            "תיאור קיים באתר",
            value=selected["תיאור קיים"],
            height=150
        )

        proposed_desc = st.text_area(
            "תיאור מוצע / עריכה לפני אישור",
            value=selected["תיאור מוצע"],
            height=230
        )

        proposed_img = st.text_input(
            "קישור תמונה מוצעת",
            placeholder="הדבק כאן URL של תמונה חדשה אם צריך"
        )

        final_note = st.text_input(
            "הערת עבודה",
            placeholder="לדוגמה: צריך לבדוק מקור תמונה / התיאור אושר / להעלות ידנית"
        )

        b1, b2, b3 = st.columns(3)

        approved_row = {
            "מזהה": selected["מזהה"],
            "מק״ט": selected["מק״ט"],
            "שם מוצר": selected["שם מוצר"],
            "סוג מוצר": selected["סוג מוצר"],
            "קטגוריה": selected["קטגוריה"],
            "בעיות מקוריות": selected["בעיות"],
            "תיאור מאושר": proposed_desc,
            "תמונה קיימת": selected["תמונה קיימת"],
            "תמונה מוצעת": proposed_img,
            "הערה": final_note,
            "סטטוס עבודה": "מאושר לעדכון",
            "זמן אישור": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        with b1:
            if st.button("✅ אשר מוצר", use_container_width=True):
                st.session_state.approved.append(approved_row)
                st.success("המוצר נוסף לרשימת המאושרים")

        with b2:
            if st.button("⚠️ סמן לבדיקה", use_container_width=True):
                temp = approved_row.copy()
                temp["סטטוס עבודה"] = "דורש בדיקה ידנית"
                st.session_state.rejected.append(temp)
                st.warning("המוצר סומן לבדיקה ידנית")

        with b3:
            if st.button("🧹 נקה בחירה", use_container_width=True):
                st.info("נוקה במסך בלבד. אין שינוי באתר.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TABLE PREVIEW ----------
with st.expander("📋 הצג טבלת מוצרים מסוננת"):
    st.dataframe(view_df, use_container_width=True, height=400)

# ---------- APPROVED AREA ----------
st.divider()
st.subheader("✅ מוצרים שאושרו לעדכון")

if len(st.session_state.approved) == 0:
    st.info("עדיין לא אושרו מוצרים.")
else:
    approved_df = pd.DataFrame(st.session_state.approved)
    st.dataframe(approved_df, use_container_width=True, height=300)

    csv_approved = approved_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ הורד קובץ מוצרים מאושרים",
        data=csv_approved,
        file_name=f"partush_approved_updates_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv",
        mime="text/csv"
    )

st.subheader("⚠️ מוצרים שסומנו לבדיקה")

if len(st.session_state.rejected) == 0:
    st.info("אין מוצרים שסומנו לבדיקה.")
else:
    rejected_df = pd.DataFrame(st.session_state.rejected)
    st.dataframe(rejected_df, use_container_width=True, height=250)

# ---------- EXPORT ALL ----------
st.divider()
st.subheader("📦 ייצוא דוחות כלליים")

e1, e2 = st.columns(2)

with e1:
    csv_issues = issues_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "הורד דוח מוצרים שדורשים טיפול",
        data=csv_issues,
        file_name=f"partush_products_issues_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv",
        mime="text/csv"
    )

with e2:
    csv_all = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "הורד דוח מלא",
        data=csv_all,
        file_name=f"partush_products_full_report_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv",
        mime="text/csv"
    )
