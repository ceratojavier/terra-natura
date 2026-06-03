from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Angulo = Literal["parejas", "familia", "evento", "temporada_baja", "reserva_directa"]
Canal = Literal["instagram", "facebook", "whatsapp_status", "tiktok"]
ObjetivoPub = Literal["cta_reserva", "fidelizacion", "utilidad", "branding"]
FormatoPub = Literal["reel", "carousel", "post", "status"]
EstadoPub = Literal["borrador", "pendiente_aprobacion", "aprobado", "publicado", "cancelado"]
ModoPub = Literal["aprobacion", "automatico"]


class GenerarCopyIn(BaseModel):
    angulo: Angulo = "parejas"
    canal: Canal = "instagram"
    tema_extra: str = ""
    cuerpo_extra: str | None = None


class PublicacionCreate(BaseModel):
    fecha_publicacion: date
    hora: str = "10:00"
    canal: Canal = "instagram"
    angulo: Angulo = "parejas"
    titulo: str = ""
    texto: str = Field(default="", description="Texto del post para redes")
    hashtags: list[str] = Field(default_factory=list)
    estado: EstadoPub = "borrador"
    notas: str = ""
    video_ruta: str | None = None


class PublicacionPatch(BaseModel):
    fecha_publicacion: date | None = None
    hora: str | None = None
    canal: Canal | None = None
    titulo: str | None = None
    texto: str | None = None
    hashtags: list[str] | None = None
    estado: EstadoPub | None = None
    notas: str | None = None
    video_ruta: str | None = None


class ConfigAmaPatch(BaseModel):
    modo_publicacion: ModoPub | None = None


class VideoSlideshowIn(BaseModel):
    titulo_en_video: str = "Terra Natura · Bialet Massé"
    subtitulo: str = "Reservá por WhatsApp"
    carpeta_media: str | None = Field(
        None,
        description="Subcarpeta en archivos multimedia/, ej. Parque o Alpinas",
    )


class GenerarSemanaIn(BaseModel):
    desde: date | None = None
    dias: int = Field(default=7, ge=1, le=31)
    guardar_en_calendario: bool = True


class GenerarCalendarioEditorialIn(BaseModel):
    """Calendario de publicaciones por rango (desde/hasta), no cantidad fija."""
    desde: date | None = None
    hasta: date | None = None
    dias: int | None = Field(default=None, ge=7, le=366, description="Alternativa legacy si no hay hasta")
    guardar_en_calendario: bool = True
    reemplazar_borradores_en_rango: bool = False


class GenerarCalendario90In(BaseModel):
    desde: date | None = None
    dias: int = Field(default=90, ge=14, le=120)
    guardar_en_calendario: bool = True
    reemplazar_borradores_en_rango: bool = False


class VideoDesdeGuionIn(BaseModel):
    pub_id: str | None = None
    guion: dict | None = None
    assets: dict | None = None


class GuionProduccionPiezaIn(BaseModel):
    hito_id: str
    pieza_id: str


class PiezaEnviarPublicacionesIn(BaseModel):
    hito_id: str
    pieza_id: str
    video_ruta: str | None = Field(
        None,
        description="Ruta relativa al MP4; si falta, se busca el último render de la pieza",
    )


class GuionProduccionEscenaIn(BaseModel):
    hito_id: str
    pieza_id: str
    numero: int = Field(..., ge=1, le=30)
    youtube_id: str | None = None
    youtube_url: str | None = None
    youtube_inicio_seg: float | None = Field(None, ge=0)
    youtube_fin_seg: float | None = Field(None, ge=0)
    foto_ruta: str | None = None


class VideoLoteCalendarioIn(BaseModel):
    dias: int = Field(default=14, ge=1, le=90)
    max_videos: int = Field(default=5, ge=1, le=20)


class PipelineDiaIn(BaseModel):
    fecha: date | None = None
    render_video: bool = True
    guardar_calendario: bool = True
    carpeta_media: str | None = "Parque"
