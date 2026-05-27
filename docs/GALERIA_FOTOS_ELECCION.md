# Galería web — criterio de selección

Fotos optimizadas en `frontend/public/media/galeria/` (origen: `archivos multimedia/fotos terra natura/`).  
Regenerar: `python scripts/build_web_gallery.py`

## Por qué cada foto

| ID | Archivo web | Por qué la elegimos |
|----|-------------|---------------------|
| **hero** | `hero.jpg` | Panorámica del complejo desde el parque: muestra las 5 unidades y el entorno verde sin recortes confusos. Es el gancho visual correcto para la home. |
| **01-complejo-panoramica** | Vista aérea/amplia del predio | Contexto de escala: el visitante entiende que es un complejo, no una sola cabaña aislada. |
| **02-piscina** | Pileta protagonista | Amenidad diferencial en Bialet; foto limpia, sin gente identificable, horario diurno. |
| **03-pileta-alpina** | Reposeras + alpina al fondo | Une producto (cabaña) y experiencia (sol/pileta) en una sola toma — ideal para redes y web. |
| **04-alpina-vista-puerta** | Puerta abierta + valle | Gancho emocional “refugio con vista”; alinea con posicionamiento parejas sin prometer 4 adultos en PB. |
| **05-alpina-living** | Living-comedor amplio | Demuestra espacio real del PB; las camas auxiliares se leen como flex familia, no dormitorio apretado. |
| **06-suite5-ventanal** | Ventanal Suite 5 PA | Suite premium con A/A y vista; mejor foto de loft planta alta para pareja. |
| **07-suite4-interior** | Interior Suite 4 PB | Acceso sin escaleras + ambiente loft; contraste claro con Suite 5. |
| **08-suites-exterior** | Fachada dúplex suites | Muestra entradas independientes PB/PA — dato operativo que Booking no siempre transmite. |
| **09-alpina-frente-pileta** | Alpina junto a la pileta | Proximidad unidad–amenity; útil para familias que priorizan pileta cerca. |
| **10-parque-mate** | Mate en el parque (archivo en `exteriores cabanas/`) | Humaniza la estadía (tono anfitrión cordobés) sin selfie amateur ni capturas de pantalla. |
| **11-lago-plaza** | Lago desde plaza cercana | Entorno: caminata 1 km, lago San Roque — sin usar “Punilla” en copy público. |
| **12-arroyo-cercano** | Arroyo Las Mojarras | Cercanía natural real (400 m); refuerza ubicación sin stock genérico. |
| **13-parque-relax** | Lectura en el parque | Ritmo lento / descanso; complementa fotos “acción” de pileta y vista. |

## Descartadas a propósito

- Miniaturas &lt; 50 KB (`INTERIOR CABANA.jpg`, etc.) — calidad insuficiente para web.
- Capturas con timestamp en el nombre (`1000118551_…`) — aspecto informal.
- `COCINANDO ALGO RICO`, fotos personales en bici, festivales ajenos — no representan el producto alquiler.
- Archivos PNG de herramientas (Google Cloud, JSON) en la raíz de fotos — no son contenido del complejo.

## Tarjetas de unidades (home)

- **Alpinas:** `04-alpina-vista-puerta.jpg` — mejor “wow” de producto alpina.
- **Suite 4:** `07-suite4-interior.jpg` — PB accesible.
- **Suite 5:** `06-suite5-ventanal.jpg` — PA con vista y confort.
