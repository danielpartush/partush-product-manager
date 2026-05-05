import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Partush Product Manager PRO",
    page_icon="🍷",
    layout="wide"
)

# כותרת ראשית
st.title("🍷 Partush Product Manager PRO")
st.subheader("מערכת חכמה לניהול מוצרי WooCommerce")

# נתוני דוגמה מתקדמים
products = [
    {
        "SKU": "1001",
        "שם מוצר": "גרייגוס וודקה",
        "תיאור": "וודקה צרפתית יוקרתית מחומרי גלם מובחרים.",
        "סטטוס": "ממתין לאישור",
        "אישור תיאור": "כן",
        "מקורות": "בדיקה ידנית",
        "תמונה": "חסרה"
    },
    {
        "SKU": "1002",
        "שם מוצר": "בלו נאן גולד אדישן",
        "תיאור": "יין מבעבע איכותי עם עלי זהב.",
        "סטטוס": "מאושר",
        "אישור תיאור": "כן",
        "מקורות": "בדיקה אוטומטית",
        "תמונה": "קיימת"
    },
    {
        "SKU": "1003",
        "שם מוצר": "ג'ק דניאלס",
        "תיאור": "וויסקי טנסי קלאסי.",
        "סטטוס": "נדחה",
        "אישור תיאור": "לא",
        "מקורות": "בדיקה חוזרת",
        "תמונה": "קיימת"
    }
]

df = pd.DataFrame(products)

# סטטיסטיקות
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("סה״כ מוצרים", len(df))

with col2:
    st.metric("ממתינים לאישור", len(df[df["סטטוס"] == "ממתין לאישור"]))

with col3:
    st.metric("מאושרים", len(df[df["סטטוס"] == "מאושר"]))

with col4:
    st.metric("חסרות תמונות", len(df[df["תמונה"] == "חסרה"]))

st.divider()

# פילטרים
status_filter = st.selectbox(
    "סנן לפי סטטוס",
    ["הכל", "ממתין לאישור", "מאושר", "נדחה"]
)

if status_filter != "הכל":
    df = df[df["סטטוס"] == status_filter]

# טבלה
st.dataframe(df, use_container_width=True)

st.divider()

# פעולות מערכת
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 סרוק מוצרים חדשים"):
        st.success("סריקה הושלמה בהצלחה")

with col2:
    if st.button("✅ אשר מוצר נבחר"):
        st.success("המוצר אושר")

with col3:
    if st.button("❌ דחה מוצר"):
        st.warning("המוצר נדחה")

with col4:
    if st.button("🔄 בדיקה מחדש"):
        st.info("המוצר נשלח לבדיקה חוזרת")

st.divider()

# מוצרים חסרים תמונה
st.markdown("### 📷 מוצרים ללא תמונה")
missing_images = df[df["תמונה"] == "חסרה"]

if not missing_images.empty:
    st.dataframe(missing_images, use_container_width=True)
else:
    st.success("כל המוצרים כוללים תמונה")

st.divider()

# לוג מערכת
st.markdown("### 🛠 סטטוס מערכת")
st.info("""
✔ Google Sheets מחובר  
✔ GitHub פעיל  
✔ Streamlit Cloud פעיל  
🔜 WooCommerce API בחיבור הבא  
🔜 מערכת AI לתיאורי מוצרים  
🔜 העלאת תמונות אוטומטית  
""")
