# Paso a paso — Clave YouTube (para que Terra Natura busque videos solo)

## Importante (leé esto primero)

- La API **no está en youtube.com**. Está en **Google Cloud** (la misma cuenta de Gmail sirve).
- **Yo (la IA) no puedo entrar a tu Google** ni crear la clave por vos. Vos la creás en 5–10 minutos.
- Cuando la clave esté en tu PC, **el programa busca solo** 16 temas (Bialet, Cosquín, Punilla, etc.) y guarda los videos en la base de datos.

---

## PASO 1 — Abrí Google Cloud

1. Abrí el navegador (Chrome, Edge, etc.).
2. Entrá acá: **https://console.cloud.google.com/**
3. Iniciá sesión con tu **cuenta Gmail** (la que uses siempre).

---

## PASO 2 — Crear un proyecto

1. Arriba, al lado de “Google Cloud”, hacé clic en el **nombre del proyecto** (o dice “Seleccionar proyecto”).
2. Clic en **“Proyecto nuevo”** / **“New Project”**.
3. Nombre: `Terra Natura` (o el que quieras).
4. **Crear** y esperá unos segundos.
5. Volvé a seleccionar ese proyecto arriba (que quede activo).

---

## PASO 3 — Activar “YouTube Data API v3”

1. En el menú de la izquierda (☰), entrá a:  
   **APIs y servicios** → **Biblioteca**  
   (en inglés: *APIs & Services* → *Library*)

2. En el buscador escribí exactamente:  
   `YouTube Data API v3`

3. Clic en el resultado **YouTube Data API v3**.

4. Botón azul **HABILITAR** / **ENABLE**.

   Enlace directo a la biblioteca:  
   https://console.cloud.google.com/apis/library/youtube.googleapis.com

---

## PASO 4 — Crear la clave (lo que va en `.env`)

1. Menú ☰ → **APIs y servicios** → **Credenciales**  
   https://console.cloud.google.com/apis/credentials

2. Arriba: **+ CREAR CREDENCIALES** → **Clave de API** / **API key**.

3. Te muestra una clave que empieza con `AIza...` — **COPIALA** (Ctrl+C).

4. (Recomendado) Clic en **“Restringir clave”**:
   - Restricción de API: solo **YouTube Data API v3**
   - Guardar

---

## PASO 5 — Pegar la clave en Terra Natura

1. Abrí la carpeta del proyecto en el Explorador:  
   `Desktop\proyectos programacion\Proyecto Terra Natura`

2. Buscá el archivo **`.env`**  
   - Si no existe: copiá **`.env.example`** y renombrá la copia a **`.env`**

3. Abrí `.env` con el Bloc de notas y agregá o cambiá esta línea (pegá tu clave):

```
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXX
```

4. **Guardá** el archivo (Ctrl+S).

---

## PASO 6 — Buscar videos automáticamente

**Forma fácil (doble clic):**

`local\Recolectar-videos-YouTube.bat`

**O con la página del proyecto:**

1. Iniciá el servidor: `local\inicia_servidor_interno.bat`
2. Abrí: http://127.0.0.1:8000/turismo
3. Clic en **“Buscar videos en YouTube (API)”**

Ahí vas a ver las miniaturas y links de videos reales guardados.

---

## Si algo falla

| Mensaje | Qué hacer |
|---------|-----------|
| Falta YOUTUBE_API_KEY | No guardaste el `.env` o la línea está mal escrita |
| HTTP 403 | En Google Cloud no habilitaste YouTube Data API v3 (Paso 3) |
| Cuota agotada | Esperá 24 h o creá otra clave en otro proyecto Google |

---

## Enlaces útiles (oficiales Google)

- Consola: https://console.cloud.google.com/
- Habilitar API: https://console.cloud.google.com/apis/library/youtube.googleapis.com
- Credenciales: https://console.cloud.google.com/apis/credentials
- Documentación: https://developers.google.com/youtube/v3/getting-started
