import streamlit as st
import openai
import requests
import os
from datetime import datetime

# --------------------------
#  Configurazione Streamlit
# --------------------------
st.set_page_config(page_title="Assistente Social", layout="wide")
st.title("🧠 Assistente Virtuale per i Social Media")

# --------------------------
#  Carico chiavi segrete
# --------------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

AIRTABLE_TOKEN   = st.secrets["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE   = "Contenuti"

# --------------------------
#  UI – Input utente
# --------------------------
col1, col2 = st.columns(2)

with col1:
    piattaforma = st.selectbox(
        "Scegli la piattaforma",
        ["Instagram", "LinkedIn", "Facebook", "TikTok"]
    )

with col2:
    tono = st.selectbox(
        "Tono del messaggio",
        ["Professionale", "Creativo", "Amichevole", "Istituzionale"]
    )

idea = st.text_area("Inserisci un'idea o una traccia", height=150)

uploaded_file = st.file_uploader(
    "📷 Carica un'immagine (opzionale)",
    type=["png", "jpg", "jpeg"]
)

# --------------------------
#  Funzioni helper
# --------------------------
def genera_post(piattaforma, tono, idea):
    prompt = f"""
Sei un copywriter esperto di social media per agenzie pubblicitarie.
1. Crea un post per {piattaforma} con tono {tono}.
2. Tema: {idea}
3. Massimo 150 parole, divise in 2–3 paragrafi.
4. Includi una call to action.
5. Suggerisci 3 hashtag in fondo (senza # generici come #follow).
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=400
    )
    return response.choices[0].message.content.strip()

def suggerisci_trend():
    prompt = """
Dammi 3 trend social del momento per agenzie pubblicitarie (breve bullet list).
Max 50 parole totali.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=120
    )
    return resp.choices[0].message.content.strip()

def salva_su_airtable(fields: dict):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"fields": fields}
    r = requests.post(url, headers=headers, json=data)
    return r.status_code == 200, r.text

# --------------------------
#  Azione: Genera post
# --------------------------
if st.button("🚀 Genera & Salva Post"):
    if not idea.strip():
        st.warning("Inserisci almeno un'idea.")
        st.stop()

    with st.spinner("Generazione del copy in corso…"):
        testo_post = genera_post(piattaforma, tono, idea)
        trend = suggerisci_trend()

    st.subheader("✏️ Post generato")
    st.markdown(testo_post)

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Immagine caricata", use_column_width=True)

    st.markdown("### 🌟 Trend / best-practice del momento")
    st.info(trend)

    ok, resp = salva_su_airtable({
        "Piattaforma": piattaforma,
        "Tono": tono,
        "Prompt": idea,
        "Testo Generato": testo_post,
        "Timestamp": datetime.utcnow().isoformat()
    })

    if ok:
        st.success("✅ Post salvato su Airtable!")
    else:
        st.error(f"Errore salvataggio Airtable: {resp}")
