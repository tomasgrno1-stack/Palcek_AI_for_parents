import streamlit as st
import google.generativeai as genai
from PIL import Image
import uuid
import pypdf
import docx
import pandas as pd
import time

# 1. Konfigurácia aplikácie
st.set_page_config(
    page_title="Palček AI - Poradca a Asistent",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Tmavý dizajn pre dospelých a rodičov
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #60a5fa !important;
        margin-bottom: 0.2rem;
    }

    .sub-header {
        color: #94a3b8 !important;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    [data-testid="stChatMessage"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        color: #f8fafc !important;
    }

    .stButton > button {
        border-radius: 8px !important;
        background-color: #334155 !important;
        border: 1px solid #475569 !important;
        color: #f8fafc !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #60a5fa !important;
        color: #60a5fa !important;
        background-color: #1e293b !important;
    }

    [data-testid="stChatInput"] {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 12px;
    }

    [data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Načítanie API kľúča
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Chýba GOOGLE_API_KEY v Secrets!")
    st.stop()

# 4. Správa pamäte chatu
if "adult_chats" not in st.session_state:
    st.session_state.adult_chats = {}

if "current_adult_id" not in st.session_state:
    init_id = str(uuid.uuid4())
    st.session_state.adult_chats[init_id] = {"title": "💬 Nová konverzácia", "messages": []}
    st.session_state.current_adult_id = init_id

def novy_chat():
    nid = str(uuid.uuid4())
    st.session_state.adult_chats[nid] = {"title": "💬 Nová konverzácia", "messages": []}
    st.session_state.current_adult_id = nid

# 5. Bočný panel
with st.sidebar:
    st.markdown('<p class="main-header" style="font-size:1.6rem;">📘 Palček AI</p>', unsafe_allow_html=True)
    st.caption("Informačný asistent pre rodičov")
    st.write("")

    if st.button("➕ Nová konverzácia", use_container_width=True):
        novy_chat()
        st.rerun()

    st.divider()

    st.subheader("💡 Časté oblasti")

    if st.button("🏛 Legislative a preukaz ŤZP", use_container_width=True):
        st.session_state["pouzity_prompt"] = "Aké sú hlavné kroky pri žiadaní o preukaz ŤZP alebo kompenzačné príspevky pre dieťa s achondropláziou na Slovensku?"
        st.rerun()

    if st.button("🩺 Zdravotná starostlivosť a liečba", use_container_width=True):
        st.session_state["pouzity_prompt"] = "Aké preventívne lekárske prehliadky a špecialistov je dôležité pravidelne navštevovať pri achondroplázii?"
        st.rerun()

    if st.button("🏫 Škola a inkluzívne vzdelávanie", use_container_width=True):
        st.session_state["pouzity_prompt"] = "Ako pripraviť školu/škôlku na príchod dieťaťa s achondropláziou a aké úpravy prostredia navrhnúť?"
        st.rerun()

    if st.button("🚗 Kompenzácie a úpravy auta/domu", use_container_width=True):
        st.session_state["pouzity_prompt"] = "Aké sú možnosti príspevkov na úpravu automobilu alebo bezbariérovú úpravu domácnosti?"
        st.rerun()

    st.divider()
    st.subheader("💬 História")

    for cid, cdata in list(st.session_state.adult_chats.items()):
        active = (cid == st.session_state.current_adult_id)
        prefix = "📌 " if active else "💬 "
        
        col_m, col_d = st.columns([0.85, 0.15])
        with col_m:
            if st.button(f"{prefix}{cdata['title']}", key=f"adult_btn_{cid}", use_container_width=True):
                st.session_state.current_adult_id = cid
                st.rerun()
        with col_d:
            if st.button("🗑", key=f"adult_del_{cid}"):
                del st.session_state.adult_chats[cid]
                if st.session_state.current_adult_id == cid:
                    if st.session_state.adult_chats:
                        st.session_state.current_adult_id = list(st.session_state.adult_chats.keys())[0]
                    else:
                        novy_chat()
                st.rerun()

# 6. Hlavné rozhranie
curr_chat = st.session_state.adult_chats[st.session_state.current_adult_id]

st.markdown('<p class="main-header">📘 Palček AI – Poradca a Asistent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Odborná podpora, spracovanie dokumentov a informácie pre rodičov a dospelých členov komunity.</p>', unsafe_allow_html=True)

# Zobrazenie histórie
for msg in curr_chat["messages"]:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        if "file_name" in msg:
            st.caption(f"📎 Priložený súbor: **{msg['file_name']}**")
        if "image" in msg:
            st.image(msg["image"], use_container_width=True)
        st.markdown(msg["content"])

# 7. Vstup pre používateľa
col_file, col_input = st.columns([0.08, 0.92])

uploaded_file = None
with col_file:
    with st.popover("📎"):
        uploaded_file = st.file_uploader("Priložiť lekársku správu, PDF alebo obrázok", type=["png", "jpg", "jpeg", "pdf", "txt", "docx"])

with col_input:
    user_input = st.chat_input("Položte otázku alebo napíšte, s čím potrebujete pomôcť...")

user_prompt = user_input or st.session_state.pop("pouzity_prompt", None)

# 8. Generovanie odpovede
if user_prompt:
    if len(curr_chat["messages"]) == 0:
        curr_chat["title"] = user_prompt[:25] + "..." if len(user_prompt) > 25 else user_prompt

    msg_payload = {"role": "user", "content": user_prompt}
    prompt_parts = [user_prompt]

    if uploaded_file is not None:
        fname = uploaded_file.name
        ftype = uploaded_file.type
        msg_payload["file_name"] = fname

        if ftype in ["image/png", "image/jpeg", "image/jpg"]:
            img = Image.open(uploaded_file)
            prompt_parts.append(img)
            msg_payload["image"] = img
        elif ftype == "text/plain":
            text_data = uploaded_file.read().decode("utf-8")
            prompt_parts.append(f"\n\nObsah súboru ({fname}):\n{text_data}")
        elif ftype == "application/pdf":
            try:
                reader = pypdf.PdfReader(uploaded_file)
                pdf_text = "".join([page.extract_text() or "" for page in reader.pages])
                prompt_parts.append(f"\n\nObsah PDF ({fname}):\n{pdf_text}")
            except Exception as e:
                st.error(f"Chyba pri čítaní PDF: {e}")

    curr_chat["messages"].append(msg_payload)
    
    with st.chat_message("user", avatar="👤"):
        if "file_name" in msg_payload:
            st.caption(f"📎 Priložený súbor: **{msg_payload['file_name']}**")
        if "image" in msg_payload:
            st.image(msg_payload["image"], use_container_width=True)
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        
        with st.spinner("Pripravujem odpoveď..."):
            system_instruction = """Si odborný, empatiou sprevádzaný a vecný AI asistent pre rodičov v organizácii Palčekovia.

Tvoja úloha:
1. Poskytovať presné a praktické informácie ohľadom legislatívy (ŤZP, príspevky ÚPSVaR), školstva, inklúzie a zdravotnej starostlivosti pri achondroplázii.
2. Odpovedaj stručne, večne a k veci. Používaj prehľadné odrážky, aby sa odpoveď vygenerovala čo najrýchlejšie.
3. Vždy pri zdravotných témach uvádzaj, že nenahrádzaš lekársku diagnózu."""

            gen_config = genai.types.GenerationConfig(
                temperature=0.3,
                top_p=0.9,
                max_output_tokens=1500
            )

            history_data = []
            for m in curr_chat["messages"][:-1][-4:]:
                r = "user" if m["role"] == "user" else "model"
                history_data.append({"role": r, "parts": [m["content"]]})

            model = genai.GenerativeModel(
                model_name="gemini-3.6-flash",
                system_instruction=system_instruction,
                generation_config=gen_config
            )

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    chat_session = model.start_chat(history=history_data)
                    response = chat_session.send_message(prompt_parts, stream=True)

                    full_response = ""
                    for chunk in response:
                        full_response += chunk.text
                        response_placeholder.markdown(full_response + "▌")

                    response_placeholder.markdown(full_response)
                    curr_chat["messages"].append({"role": "assistant", "content": full_response})
                    break

                except Exception as err:
                    if "429" in str(err) and attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        response_placeholder.error(
                            "Služba je dočasne vyťažená. Počkajte pár sekúnd a pošlite správu znova."
                        )
                        break
