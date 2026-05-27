# Inventario multimedia local — Terra Natura

**Ruta raíz:** `archivos multimedia/`  
**Origen:** Creado por los dueños con fotos y videos clasificados por contexto. Complemento (o sustituto temporal) respecto del Google Drive institucional.

> **Para el agente de código / AMA:** leer esta tabla antes de armar posts, sitio web o thumbnails. Preferir rutas relativas desde la raíz del repo.

---

## Árbol de carpetas

**Normalización:** nombres de **archivos** usan **`n`** en lugar de **`ñ`**/`Ñ`** (ASCII-friendly, Git/Linux). Carpetas ya estaban como `CABANA ...`.

```
archivos multimedia/
├── fotos terra natura/
│   ├── CABANA ALPINA 1/
│   ├── CABANA ALPINA 2/
│   ├── CABANA ALPINA 3/
│   ├── CABANA SUITE 4/
│   ├── CABANA SUITE 5/
│   ├── exteriores cabanas/
│   ├── PARQUE/
│   ├── PISCINA/
│   ├── RIO Y BALNEARIOS/
│   ├── FESTIVALES/               (uso editorial según licencia/imagen propia)
│   ├── LOGO/
│   ├── recursos de la marca/
│   └── (capturas herramientas: revisar uso editorial)
└── videos terra natura/          (clips IMG_/VID_/etc.)
```

---

## Mapeo a unidades del PMS (`docs/UNIDADES.md`)

| Carpeta (aprox.) | ID sistema |
|------------------|------------|
| CABANA ALPINA **1** | `alpina-1` |
| CABANA ALPINA **2** | `alpina-2` |
| CABANA ALPINA **3** | `alpina-3` |
| CABANA SUITE **4** | `suite-4` |
| CABANA SUITE **5** | `suite-5` |

**Exteriores / parque / pileta / río:** contenido para **marketing general**, landings, home, guía huésped.

---

## Uso por canal

| Uso | Carpetas típicas |
|-----|------------------|
| **Instagram / Reels** | PISCINA, PARQUE, Alpinas (balcón interior), videos terra natura |
| **Landing parejas** | Alpinas PA matrimonial + balcón, Suite 5, atardecer |
| **Landing familia** | PARQUE, PISCINA, living Alpinas |
| **Booking / Airbnb** | 1 foto por tipo por carpeta de unidad + exteriores + pileta |
| **Logo / firma** | LOGO, recursos de la marca |

---

## Consejos técnicos

1. **Git y peso:** si `git push` pesa gigas, mejor **no** versionar `archivos multimedia/` y usar `.gitignore` + backup Drive, o **[Git LFS](https://git-lfs.github.com/)** solo para ese directorio.
2. **`ñ`/`Ñ` en nombres de archivo:** ya reemplazados por `n`/`N` sobre la colección vigente para evitar Unicode roto entre Windows/Linux.
3. **Web futura:** se pueden copiar JPG optimizadas a `frontend/public/media/` (~1200 px ancho); el original queda aquí.

---

## Próximo paso sugerido (desarrollo)

- Script opcional `local/scan-media.py`: listar JPG/PNG/MP4 y generar `archivos multimedia/inventario.json` para AMA.
- Cargar rutas destacadas por unidad en `backend/data/` cuando exista modelo de fotos por unidad.

## Versión

- Detectado automáticamente en el equipo del proyecto; actualizar tabla si reorganizás carpetas.
