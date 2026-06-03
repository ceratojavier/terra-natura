# Inventario Google Drive vs proyecto (Terra Natura)

**Carpeta Drive compartida:**  
https://drive.google.com/drive/folders/1IA8ss4mNDWWv0k9iW9cH6JueQxDOEbGK

**Fecha de control:** 2026-05-28

---

## Resumen ejecutivo

| Ubicación | Estado |
|-----------|--------|
| **Google Drive** | Completo: 10 subcarpetas + archivos sueltos en la raíz (~130+ fotos en total) |
| **PC — `archivos multimedia/fotos terra natura/`** | **Parcial** (~41 fotos descargadas; faltan PARQUE, PISCINA, exteriores, RIO, LOGO y más de Suite 5) |
| **Web — `frontend/public/media/galeria/`** | **Solo 14 imágenes** curadas para la home (no es el banco completo) |
| **Web — `frontend/public/media/unidades/`** | **Solo Alpina 1** con 8 fotos optimizadas; el resto de unidades aún incompleto |
| **Servidor (alpinasterranatura.com.ar / gh-pages)** | Igual que lo último publicado en GitHub: **~14 fotos** de galería, no el Drive entero |

**Conclusión:** Las fotos **están en Drive**, pero **no están todas disponibles en el proyecto ni en el sitio publicado**. Hace falta terminar la sincronización local y luego ejecutar `python scripts/build_web_gallery.py`.

---

## Contenido en Drive (raíz de la carpeta)

| Carpeta / bloque | Uso en el proyecto |
|------------------|-------------------|
| CABANA ALPINA 1 | `alpina-1` — web, AMA, fichas |
| CABAÑA ALPINA 2 | `alpina-2` |
| CABAÑA ALPINA 3 | `alpina-3` |
| CABAÑA SUITE 4 | `suite-4` |
| CABAÑA SUITE 5 | `suite-5` |
| exteriores cabanas | Home, hero, marketing |
| PARQUE | Home, parque, hero |
| PISCINA | Amenities, pileta |
| RIO Y BALNEARIOS | Atracciones, entorno |
| LOGO | Marca, favicon, redes |
| Archivos sueltos en raíz | Mezcla: entorno, personal, algunos reutilizables con criterio editorial |

---

## Descarga local (control del 28/05)

Descarga automática con enlace público (`gdown`): **se interrumpió** por límite de Google (“too many accesses” / permiso de archivo).

| Carpeta Drive | Fotos en PC (aprox.) | En Drive (aprox.) |
|---------------|----------------------|-------------------|
| CABANA ALPINA 1 | 14 | 14 |
| CABAÑA ALPINA 2 | 7 | 7 |
| CABAÑA ALPINA 3 | 8 | 8 |
| CABAÑA SUITE 4 | 6 | 6 |
| CABAÑA SUITE 5 | 6 | 10+ (incompleta) |
| exteriores cabanas | **0** | ~18 |
| PARQUE | **0** | ~22 |
| PISCINA | **0** | 7 |
| RIO Y BALNEARIOS | **0** | ~20 |
| LOGO | **0** | 1 |

---

## Imágenes que el sitio necesita y aún faltan en disco

El script `scripts/build_web_gallery.py` busca estos archivos (entre otros). **Hoy no están** porque faltan carpetas o el nombre en Drive lleva **Ñ** (`CABAÑA`) y el script espera `CABANA` en algunas rutas:

- `PARQUE/FOTO PANORAMICA DE NUESTRAS CABANAS.jpg`
- `exteriores cabanas/FRENTE DEL COMPLEJO.jpg`
- `PISCINA/NUESTRA PISCINA.jpg`
- `CABANA SUITE 4/INTERIOR CABANA SUITE PB.jpg` (en Drive: `CABAÑA SUITE 4/INTERIOR...`)
- … (ver salida del script al ejecutarlo)

---

## Cómo completar la sincronización (recomendado)

### Opción A — Google Drive para escritorio (más estable)

1. Instalá [Google Drive para PC](https://www.google.com/drive/download/).
2. Sincronizá la carpeta compartida.
3. Copiá o vinculá el contenido a:  
   `Proyecto Terra Natura/archivos multimedia/fotos terra natura/`
4. Ejecutá: `python scripts/build_web_gallery.py`

### Opción B — Descarga por script (reintentar más tarde)

```powershell
pip install gdown
python -c "import gdown; gdown.download_folder('https://drive.google.com/drive/folders/1IA8ss4mNDWWv0k9iW9cH6JueQxDOEbGK?usp=sharing', output=r'archivos multimedia/fotos terra natura')"
```

Si falla un archivo: en Drive → clic derecho → **Compartir** → “Cualquier persona con el enlace” → **Lector**.

### Después de tener las fotos en disco

```powershell
python scripts/build_web_gallery.py
```

Eso regenera `frontend/public/media/galeria/` y `media/unidades/` y actualiza `assets/data/unidades.json`.

**Publicar en el sitio:** solo cuando vos lo pidas (`git push` + script de gh-pages).

---

## Nota sobre el servidor

GitHub Pages **no almacena** `archivos multimedia/` (está en `.gitignore`). El sitio público solo sirve lo que esté en `frontend/public/media/`. Por eso “controlar en el servidor” = ver cuántas de esas fotos ya están copiadas y optimizadas ahí; hoy son **14 + pocas por unidad**, no el archivo completo de Drive.
