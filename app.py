import streamlit as st
import requests
from datetime import datetime
from openai import OpenAI

# --------------------------------------------------
# Inizializza il client OpenAI leggendo la chiave dai secrets
# --------------------------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --------------------------------------------------
# Configurazione pagina Streamlit
# --------------------------------------------------
st.set_page_config(page_title="Assistente Social", layout="wide")
st.title("🧠 Assistente Virtuale per i Social Media")

# --------------------------------------------------
# UI: input utente
# --------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    platform = st.selectbox(
        "Scegli la piattaforma",
        ["Instagram", "LinkedIn", "Facebook", "TikTok"],
    )
with col2:
    tone = st.selectbox(
        "Tono del messaggio",
        [
            "Professionale",
            "Creativo",
            "Amichevole",
            "Istituzionale",
        ],
    )

idea = st.text_area("Inserisci un'idea o una traccia", height=150)

uploaded_file = st.file_uploader(
    "📷 Carica un'immagine (opzionale)", type=["png", "jpg", "jpeg"]
)

# --------------------------------------------------
# Funzioni helper
# --------------------------------------------------

def genera_post(platform: str, tone: str, idea: str) -> str:
    """Richiede a GPT‑4o di generare un post social."""
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Sei un copywriter esperto di social media per agenzie pubblicitarie.",
            },
            {
                "role": "user",
                "content": (
                    f"Crea un post per {platform} con tono {tone}. "
                    f"Tema: {idea}. Max 150 parole divise in 2–3 paragrafi. "
                    "Includi una call‑to‑action e 3 hashtag non generici."
                ),
            },
        ],
        temperature=0.7,
        max_tokens=400,
    )
    return resp.choices[0].message.content.strip()


def suggerisci_trend() -> str:
    """Restituisce 3 trend social aggiornati per il settore advertising."""
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": (
                    "Dammi 3 trend social del momento per agenzie pubblicitarie in 3 bullet brevi (max 50 parole totali)."
                ),
            }
        ],
        temperature=0.6,
        max_tokens=120,
    )
    return resp.choices[0].message.content.strip()


# Airtable setup
AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE = "Contenuti"

def salva_su_airtable(fields: dict):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    res = requests.post(url, headers=headers, json={"fields": fields})
    return res.status_code == 200, res.text

# --------------------------------------------------
# Azione principale
# --------------------------------------------------
if st.button("🚀 Genera & Salva Post"):
    if not idea.strip():
        st.warning("Inserisci almeno un'idea.")
        st.stop()

    with st.spinner("Generazione del copy in corso…"):
        post_text = genera_post(platform, tone, idea)
        trend_text = suggerisci_trend()

    st.subheader("✏️ Post generato")
    st.markdown(post_text)

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Immagine caricata", use_column_width=True)

    st.markdown("### 🌟 Trend / best‑practice del momento")
    st.info(trend_text)

    ok, resp = salva_su_airtable(
        {
            "Piattaforma": platform,
            "Tono": tone,
            "Prompt": idea,
            "Testo Generato": post_text,
            "Timestamp": datetime.utcnow().isoformat(),
        }
    )

    if ok:
        st.success("✅ Post salvato su Airtable!")
    else:
        st.error(f"Errore salvataggio Airtable: {resp}")
