# Cómo autorizar al agente (Cursor) para que trabaje solo

**Vos no subís fotos ni buscás en Google.** El programa Terra Natura descarga banners cuando faltan.  
Cursor (el asistente) necesita permiso para usar **internet** y **escribir archivos** en tu PC.

---

## 1. Permiso de red (internet) — lo más importante

Cuando el agente ejecuta comandos que bajan imágenes, Cursor muestra un cuadro:

- **Allow** / **Permitir** → solo esta vez  
- **Allow for this workspace** / **Permitir en este proyecto** → recomendado  
- Si aparece **Always allow** / **Siempre permitir** → marcá eso para no preguntar cada vez  

**Dónde configurarlo en Cursor (Windows):**

1. Abrí **Cursor** → engranaje **Settings** (o `Ctrl + ,`)
2. Buscá **Agent** o **Features → Agent**
3. Activá opciones del estilo:
   - **Auto-run** / ejecutar herramientas sin pedir confirmación en cada paso (si te resulta cómodo)
   - **Terminal: Allow network access** o permisos de red para el agente
4. Guardá y **reiniciá Cursor** una vez

Si el agente te pide `full_network` o **network** en un mensaje emergente: elegí **Allow for workspace** o **Always**.

---

## 2. Regla permanente para el agente (memoria del proyecto)

Copiá esto en una **User Rule** o **Project Rule** de Cursor:

```text
Terra Natura: el dueño NO sube fotos manualmente. Si falta banner de festival/recital/evento,
buscar y descargar automáticamente (og:image de fuente oficial o Wikimedia Commons),
guardar en archivos multimedia/fotos terra natura/FESTIVALES/, y registrar crédito.
Pedir permiso de red solo la primera vez; luego usar acceso permanente del workspace.
```

**Cómo agregar la regla:**

1. `Ctrl + Shift + P` → escribí **Cursor: Open Rules** o **Rules**
2. **Add rule** → pegá el texto de arriba  
3. Alcance: **This project** (Proyecto Terra Natura)

---

## 3. Qué hace el programa solo (sin que vos hagas nada)

| Acción | Cuándo |
|--------|--------|
| Actualizar eventos | Icono escritorio / **Actualizar eventos** en `/programa` |
| **Buscar foto en la web** | Automático al actualizar agenda (hasta 15 por vez) |
| Guardar imagen | `archivos multimedia/fotos terra natura/FESTIVALES/` |
| Créditos legales | `FESTIVALES/CREDITOS_DESCARGA_WEB.txt` |

**Orden de búsqueda:**

1. Imagen de la página oficial del evento (`og:image`, si hay `fuente_url`)
2. Wikimedia Commons (búsqueda por nombre + localidad + Córdoba)
3. Si no hay nada público → se usa foto del complejo (parque/lago) y la tarjeta dice **Falta asset**

---

## 4. Un solo clic en el escritorio (recomendado)

Usá el icono **Terra Natura** o el archivo:

`local\Actualizar-agenda-eventos.bat`

Eso actualiza fechas **y** intenta bajar fotos faltantes. Después abrí `/programa` y **Cargar publicaciones**.

---

## 5. Si Cursor sigue pidiendo permiso cada vez

1. Cerrá Cursor por completo  
2. Abrí de nuevo el proyecto **Proyecto Terra Natura**  
3. En el chat del agente, escribí:  
   *«Autorizo acceso permanente a red y archivos para descargar fotos de eventos automáticamente»*  
4. Cuando salga el popup → **Allow for workspace** / **Always**

---

## 6. Límites (para no mentirte)

- No todas las fiestas tienen imagen libre en internet; ahí queda fallback del complejo.  
- El agente **no** inventa fechas ni carteles falsos.  
- Algunas páginas bloquean robots; en ese caso prueba Wikimedia o foto del predio.

---

## 7. Comando manual (opcional, para el agente o vos)

```bat
cd "ruta\Proyecto Terra Natura"
py -m ama.scrapers.event_image_fetcher
```

O API con el servidor encendido:

`POST http://127.0.0.1:8000/api/programa/descargar-fotos-eventos`
