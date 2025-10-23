import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator

# CONFIGURACIÓN GENERAL
st.set_page_config(
    page_title="OCR y Traducción con Audio",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 🎨 ESTILOS VISUALES — PALETA LAVANDA/VIOLETA
st.markdown("""
    <style>
    /* Fondo principal */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #e8dcff 0%, #d7c4ff 100%);
        color: #22143d;
        font-family: 'Poppins', sans-serif;
    }

    /* Contenedor principal */
    .block-container {
        background: #faf7ff;
        border: 1px solid #cbb3ff;
        border-radius: 16px;
        padding: 2rem 2.2rem;
        box-shadow: 0 10px 24px rgba(34, 20, 61, 0.12);
    }

    /* Encabezados */
    h1, h2, h3 {
        color: #3b2168;
        text-align: center;
        font-weight: 700;
    }

    p, label, span, div, li {
        color: #22143d;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #efe6ff;
        border-right: 2px solid #c9b1ff;
        color: #2a1d5c;
    }
    section[data-testid="stSidebar"] * {
        color: #2a1d5c !important;
    }

    /* Botones */
    div.stButton > button {
        background-color: #8b6aff;
        color: #ffffff;
        font-weight: 700;
        border-radius: 10px;
        border: 1px solid #6f51ea;
        box-shadow: 0 6px 14px rgba(34, 20, 61, 0.18);
        font-size: 16px;
        padding: 9px 24px;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: #6f51ea;
        transform: translateY(-1px);
    }

    /* Inputs */
    textarea, input, select {
        background-color: #ffffff !important;
        color: #22143d !important;
        border-radius: 10px !important;
        border: 1px solid #bda5ff !important;
    }

    textarea::placeholder, input::placeholder {
        color: #6b5a8e !important;
    }

    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #22143d !important;
        border-radius: 10px !important;
        border: 1px solid #bda5ff !important;
    }

    div[data-baseweb="select"] * {
        color: #22143d !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] div {
        background-color: #3a2d61 !important;
        border-radius: 12px;
    }
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span {
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #8b6aff !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 8px;
        border: 1px solid #6f51ea !important;
        transition: all 0.2s ease;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #6f51ea !important;
    }

    /* Checkbox */
    div[data-baseweb="checkbox"] label {
        color: #22143d !important;
    }

    /* Reproductor de audio */
    audio {
        border-radius: 10px;
        border: 2px solid #b48aff;
    }

    /* Barra superior Streamlit */
    [data-testid="stHeader"] {
        background: linear-gradient(90deg, #5a3ccf 0%, #7b59e3 100%) !important;
        color: white !important;
        height: 3.5rem;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.25);
    }

    [data-testid="stToolbar"] {
        right: 1rem;
        top: 0.5rem;
        color: white !important;
    }

    .stAlert p {
        color: #22143d !important;
    }

    .stSuccess, .stInfo {
        color: #22143d !important;
    }
    </style>
""", unsafe_allow_html=True)

# FUNCIONES AUXILIARES
def traducir_texto(text, src, dest):
    return GoogleTranslator(source=src, target=dest).translate(text)

def text_to_speech(input_language, output_language, text, tld):
    trans_text = traducir_texto(text, input_language, output_language)
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    my_file_name = text[0:20] if text.strip() else "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if mp3_files:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

remove_files(7)

# INTERFAZ PRINCIPAL
st.title("Reconocimiento Óptico de Caracteres (OCR)")
st.subheader("Convierte texto desde imágenes, tradúcelo y genera audio fácilmente.")

cam_ = st.checkbox("Usar cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.subheader("Procesamiento de Imagen")
    filtro = st.radio("Aplicar filtro a la imagen de cámara", ('Sí', 'No'))

# SUBIDA DE IMAGEN
bg_image = st.file_uploader("Cargar una imagen:", type=["png", "jpg", "jpeg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada', use_container_width=True)

    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())

    img_cv = cv2.imread(uploaded_file.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write("Texto detectado en la imagen:")
    st.success(text)

# CAPTURA DESDE CÁMARA
if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write("Texto detectado:")
    st.success(text)

# PANEL DE TRADUCCIÓN Y AUDIO
with st.sidebar:
    st.subheader("Parámetros de Traducción y Audio")

    try:
        os.mkdir("temp")
    except:
        pass

    in_lang = st.selectbox(
        "Lenguaje de entrada",
        ("Inglés", "Español", "Coreano", "Mandarín", "Japonés"),
    )
    lang_map = {
        "Inglés": "en",
        "Español": "es",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }
    input_language = lang_map.get(in_lang, "en")

    out_lang = st.selectbox(
        "Lenguaje de salida",
        ("Español", "Inglés", "Coreano", "Mandarín", "Japonés"),
    )
    output_language = lang_map.get(out_lang, "es")

    accent = st.selectbox(
        "Acento",
        ("Defecto", "Reino Unido", "Estados Unidos", "Australia", "Irlanda", "Sudáfrica", "España"),
    )
    tld_map = {
        "Defecto": "com",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
        "España": "es"
    }
    tld = tld_map.get(accent, "com")

    display_output_text = st.checkbox("Mostrar texto traducido")

    if st.button("Convertir a Audio"):
        if text.strip() == "":
            st.warning("Primero detecta o carga una imagen con texto.")
        else:
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            with open(f"temp/{result}.mp3", "rb") as audio_file:
                audio_bytes = audio_file.read()

            st.markdown("## Audio generado:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            if display_output_text:
                st.markdown("## Texto traducido:")
                st.info(output_text)
