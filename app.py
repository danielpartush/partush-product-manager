import streamlit as st
import pandas as pd

st.set_page_config(page_title="Partush Product Manager", layout="wide")

st.title("🍷 Partush Product Manager")
st.subheader("מערכת ניהול מוצרים חכמה")

# טעינת נתוני דוגמה
data = {
    "מק״ט": ["1001", "1002", "1003"],
    "שם מוצר": ["גרייגוס וודקה", "בלו נאן גולד אדישן", "ג׳ק דניאלס"],
    "סטטוס": ["ממתין לאישור", "מאושר", "נדחה"],
    "אישור תיאור": ["כן", "כן", "לא"]
}

df = pd.DataFrame(data)

st.dataframe(df, use_container_width=True)

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 עבד מוצרים חדשים"):
        st.success("המערכת עיבדה מוצרים חדשים")

with col2:
    if st.button("✅ אשר מוצר"):
        st.success("המוצר אושר")

with col3:
    if st.button("❌ דחה מוצר"):
        st.warning("המוצר נדחה")

with col4:
    if st.button("🔄 בדיקה מחדש"):
        st.info("המוצר נשלח לבדיקה מחדש")

st.divider()

st.markdown("### סטטוס מערכת:")
st.info("גרסת בדיקות ראשונית לפני חיבור מלא ל־Google Sheets ו־WooCommerce")
