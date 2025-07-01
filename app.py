import streamlit as st

st.set_page_config(page_title="Assistente Social", layout="centered")

st.title("🤖 Assistente Virtuale per i Social Media")

platform = st.selectbox("Scegli la piattaforma", ["Instagram", "LinkedIn", "Facebook", "TikTok"])
tone = st.selectbox("Tono del messaggio", ["Professionale", "Amichevole", "Creativo", "Istituzionale"])
idea = st.text_area("Inserisci un'idea o una traccia")

if st.button("Genera Post"):
    if not idea:
        st.warning("Inserisci almeno un'idea per generare il contenuto.")
    else:
        st.success(f"Ecco un esempio di post per {platform} in tono {tone}:\n\n📢 {idea} 🚀")
