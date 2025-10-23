import streamlit as st
import os
import time
import glob
from gtts import gTTS
from PIL import Image, ExifTags
import base64

# CONFIGURACIÓN GENERAL
st.set_page_config(
    page_title="Texto a Audio",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ESTILOS: lavanda/violeta con alto contraste y sin texto blanco sobre claro
st.markdown("""
    <style>
    /* Fondo general (un poco más oscuro para mejor contraste) */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #e8dcff 0%, #d7c4ff 100%);
        color: #22143d; /* texto principal oscuro */
        font-family: 'Poppins', sans-serif;
    }

    /* Card central para contenido: fondo claro encima del degradado */
    .block-container {
        background: #faf7ff;         /* claro, no blanco puro */
        border: 1px solid #cbb3ff;   /* sutil */
        border-radius: 16px;
        padding: 2rem 2.2rem;
        box-shadow: 0 10px 24px rgba(34, 20, 61, 0.12);
    }

    /* Encabezados */
    h1, h2, h3 {
        color: #3b2168;              /* violeta oscuro legible */
        text-align: center;
        font-weight: 700;
    }

    /* Párrafos y listas */
    p, li, label {
        color: #22143d;
    }

    /* Sidebar con mejor contraste */
    section[data-testid="stSidebar"] {
        background: #efe6ff;
        border-right: 2px solid #c9b1ff;
        color: #2a1d5c;
    }
    section[data-testid="stSidebar"] * {
        color: #2a1d5c !important;
    }

    /* Botón: fondo violeta más oscuro, texto claro permitido (bg oscuro) */
    div.stButton > button {
        background-color: #8b6aff;   /* más oscuro */
        color: #ffffff;               /* OK porque el fondo del botón es oscuro */
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

    /* Textarea y Select: fondo claro y texto oscuro */
    textarea, .stTextInput input {
        background-color: #ffffff !important;
        color: #22143d !important;
        border-radius: 10px !important;
        border: 1px solid #bda5ff !important;
    }
    textarea::placeholder, .stTextInput input::placeholder {
        color: #6b5a8e !important; /* placeholder más visible */
    }
    /* Select (Baseweb) */
    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #22143d !important;
        border-radius: 10px !important;
        border: 1px solid #bda5ff !important;
    }
    /* Texto interno del select */
    div[data-baseweb="select"] * {
        color: #22143d !important;
    }

    /* Enlaces (descarga) */
    a {
        color: #5a3ccf;
        font-weight: 600;
        text-decoration: none;
        border-bottom: 1px dotted #5a3ccf;
    }
    a:hover {
        color: #3f2aa0;
    }

    /* Reproductor de audio */
    audio {
        border-radius: 10px;
        border: 2px solid #b48aff;
    }
    </style>
""", unsafe_allow_html=True)

# TÍTULO PRINCIPAL
st.title("Convierte Texto en Audio")

# IMAGEN PRINCIPAL
image = Image.open('cinna2.jpeg')
try:
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break
    exif = dict(image._getexif().items())
    if exif[orientation] == 3:
        image = image.rotate(180, expand=True)
    elif exif[orientation] == 6:
        image = image.rotate(270, expand=True)
    elif exif[orientation] == 8:
        image = image.rotate(90, expand=True)
except (AttributeError, KeyError, IndexError):
    pass

st.image(image, width=320, caption="Genera tu voz desde texto")

# SIDEBAR
with st.sidebar:
    st.header("Instrucciones")
    st.write("1️⃣ Escribe o pega un texto que quieras escuchar.\n\n2️⃣ Elige el idioma.\n\n3️⃣ Haz clic en Convertir a Audio y descarga tu archivo MP3.")

# CREAR CARPETA TEMPORAL
try:
    os.mkdir("temp")
except:
    pass

# TEXTO DE EJEMPLO
st.markdown("### Ejemplo de texto:")
st.write("""You shine so bright, like city lights,
Every word you say feels right.
Let the music play, don't say goodbye,
My heart’s alive when you’re nearby.""")

# ÁREA DE TEXTO
st.markdown("### Escribe tu texto para convertir en audio:")
text = st.text_area("Ingresa aquí el texto que deseas escuchar:")

# SELECCIÓN DE IDIOMA
option_lang = st.selectbox("Selecciona el idioma:", ("Español", "Inglés"))
lg = 'es' if option_lang == "Español" else 'en'
tld = 'com'

# FUNCIÓN DE CONVERSIÓN
def text_to_speech(text, tld, lg):
    tts = gTTS(text, lang=lg)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, text

# BOTÓN PARA CONVERTIR
if st.button("Convertir a Audio"):
    if text.strip() == "":
        st.warning("Escribe algo antes de convertir.")
    else:
        result, output_text = text_to_speech(text, tld, lg)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()

        st.markdown("## Tu audio listo:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        # DESCARGA DEL AUDIO
        with open(f"temp/{result}.mp3", "rb") as f:
            data = f.read()

        bin_str = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(result)}.mp3">Descargar tu audio</a>'
        st.markdown(href, unsafe_allow_html=True)

# LIMPIEZA DE ARCHIVOS TEMPORALES
def remove_files(n):
    mp3_files = glob.glob("temp/*.mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

remove_files(7)
