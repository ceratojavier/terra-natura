# Biblioteca de estilos — reels de Instagram (inspiración, no copia)

## Qué podés pedirle al sistema

**Sí:** copiar la **lógica** que funciona (gancho 2 s, corte cada 3 s, texto grande abajo, orden entorno→habitación→CTA, música upbeat).  
**No:** bajar y republicar el video de otra cabaña (derechos de autor + Instagram te puede bajar el reel).

Terra Natura usa referencias para **armar guiones y montaje propios** con **tus fotos** + B-roll permitido (YouTube entorno).

---

## Por qué no “espío” Instagram solo

Instagram **no deja** leer reels ajenos por API de forma legal y estable. Por eso el flujo es **vos alimentás** la biblioteca; Cursor + Python **analizan** y guardan recetas.

| Forma | Qué hacés | Qué hace el sistema |
|-------|-----------|---------------------|
| **A — Video guardado** | Guardás el reel en el celular → copiás a `marketing/sistema/referencias_reels/videos/` | `reel_reference_probe.py` mide duración, cortes, ritmo |
| **B — Ficha manual** | Copiás `plantilla_referencia.yaml` → completás | Queda en `indice.json` para guiones |
| **C — Cursor** | Pegás link IG + describís qué te gusta | Skill `terra-natura-analizar-referencias` escribe la ficha |

---

## Carpetas

```
marketing/sistema/referencias_reels/
  README.md
  plantilla_referencia.yaml    # copiar por cada referencia
  indice.json                  # recetas que usa el guionista
  videos/                      # .mp4 que guardaste (solo análisis)
```

---

## Cuentas sugeridas para mirar (manual)

Buscá en IG (no hace falta seguir todas):

- Cabañas / complejos **sierras Córdoba**, **Bialet**, **Carlos Paz**, **San Roque**
- Hashtags: `#cabañasCordoba` `#escapadaALasSierras` `#alojamientocordoba`
- Mirá **Reels** con más views de cada perfil (últimos 90 días)

Anotá en la ficha: *qué hook usan*, *cuántos segundos por plano*, *si hablan a cámara o solo texto*.

---

## Patrones que suelen funcionar (ya codificados)

En `ama/data/reel_estilos_preset.json`:

| ID estilo | Descripción |
|-----------|-------------|
| `clasico_cabana` | Gancho → agua/sierras YT → 2 fotos complejo → CTA |
| `rapido_trend` | Cortes ~2,8 s, más B-roll, texto mínimo |
| `lento_emocional` | Planos 4–5 s, menos cortes, música suave |
| `antes_despues` | Hook pregunta → foto living → foto pileta → cierre |

El guionista elige estilo según `indice.json` o el preset por defecto.

---

## Comandos

```text
local\Analizar-referencia-reel.bat
```

Analiza todos los `.mp4` en `referencias_reels/videos/` y actualiza `indice.json`.

En Cursor:

> Analizá marketing/sistema/referencias_reels/videos/mi_ref.mp4 y completá una ficha en indice.json. Usá skill terra-natura-analizar-referencias.

---

## Cómo se usa en el reel final

1. `reel_style_library.py` lee `indice.json` + presets.  
2. `script_generator.py` arma escenas con duraciones y orden del estilo ganador.  
3. `editorial_reel_builder.py` monta con xfade (fotos + YouTube).

**Vos elegís estilo por día** en el calendario (`estilo_reel: rapido_trend`) o dejás el default.

---

## Legal (importante)

- Referencias = **estudio privado** en tu PC.  
- Salida publicada = **100 % material Terra Natura** (+ B-roll entorno con fragmentos cortos).  
- No uses música del reel ajeno; usá `ama/assets/music/`.
