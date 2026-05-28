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

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "").strip()
MERCADOPAGO_PUBLIC_KEY = os.getenv("MERCADOPAGO_PUBLIC_KEY", "").strip()
MERCADOPAGO_CLIENT_ID = os.getenv("MERCADOPAGO_CLIENT_ID", "").strip()
MERCADOPAGO_CLIENT_SECRET = os.getenv("MERCADOPAGO_CLIENT_SECRET", "").strip()
MERCADOPAGO_WEBHOOK_SECRET = os.getenv("MERCADOPAGO_WEBHOOK_SECRET", "").strip()
PUBLIC_SITE_URL = os.getenv("PUBLIC_SITE_URL", "http://127.0.0.1:8000").strip()

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
