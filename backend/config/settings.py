"""
Configuración global — Terra Natura PMS
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./terra_natura.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-produccion")
ALGORITHM = "HS256"

API_TITLE = "Terra Natura PMS"
API_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Si tiene valor, GET /api/unidades/{id}/ical exige ?token=<valor>
ICAL_FEED_TOKEN = os.getenv("ICAL_FEED_TOKEN", "").strip()

# Meta WhatsApp Cloud API — verificación webhook (GET); vacío = no verificar (solo desarrollo).
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "").strip()
# Meta Instagram webhook — si no está definido, usa el token de WhatsApp.
INSTAGRAM_VERIFY_TOKEN = (
    os.getenv("INSTAGRAM_VERIFY_TOKEN", "").strip() or WHATSAPP_VERIFY_TOKEN
)

# YouTube Data API v3 — videos turismo (Google Cloud Console)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()

# Modos de uso de una unidad (configurable por dueño)
USOS_UNIDAD = (
    "alquiler",
    "salon_desayuno",
    "salon_comedor",
    "espacio_comun",
    "mantenimiento",
    "fuera_servicio",
    "uso_familiar",
)
