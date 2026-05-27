# Guiones y storytelling

## Estructura estándar (reel / TikTok)

1. **Hook (0–3 s):** pregunta o imagen fuerte — “¿Sabías que Bialet está a 600 m del lago?”
2. **Desarrollo (3–25 s):** 3–4 planos — parque, interior Alpina, vista balcón, pileta
3. **Prueba social (opcional):** detalle real (dueños en predio, hamacas, casita niños)
4. **CTA (últimos 3 s):** “Escribinos por WhatsApp” + handle

Generado en código: `ama/engine/script_generator.py` → campo `guion` en cada publicación.

## Campos del guion JSON

```json
{
  "hook": "...",
  "voz_off": "...",
  "musica": "instrumental cálida 90-110 BPM",
  "escenas": [
    {"tipo": "clip_youtube", "duracion_seg": 5, "fuente": "url"},
    {"tipo": "foto", "fuente": "archivos multimedia/...", "texto_pantalla": "..."},
    {"tipo": "cierre", "cta": "wa.me/..."}
  ],
  "checklist_pre_publicar": []
}
```

## Storytelling por ángulo

| Ángulo | Historia |
|--------|----------|
| parejas | Refugio romántico — matrimonial PA, living despejado, sin “4 adultos apretados” |
| familia | Espacio chicos + tranquilidad adultos — pileta, parque |
| evento | Base después del festival — descanso cerca del lago |
| reserva_directa | Trato con dueños, sin sorpresas OTA |
| temporada_baja | Escapada inteligente lun–jue, mejor precio |

## Voz off (español rioplatense cordobés sutil)

- Usar **vos**: “¿Querés que te pasemos fechas?”
- Evitar locución neutra tipo “ustedes estimados viajeros”
- Frases cortas para subtítulos automáticos

## Texto en pantalla

- Máximo 6 palabras por tarjeta
- Contraste alto (sombra o caja semitransparente)
- No tapar vista del valle en fotos hero

## Música y ritmo

- Entrada suave, beat al segundo plano foto pileta
- Corte en beat al cambiar escena (edición manual CapCut/Canva)
- Silenciar audio original de clip YouTube si hay voz superpuesta

## Carrusel (sin voz)

1. Portada: gancho  
2. Beneficio 1: ubicación  
3. Beneficio 2: unidad (Alpina vs Suite)  
4. Beneficio 3: servicios  
5. CTA: WhatsApp  

## Aprobación

Todo guion sale en **borrador**. Dueño puede marcar “aprobado” en calendario antes de producir.
