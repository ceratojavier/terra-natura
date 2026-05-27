# YouTube API — videos turismo en la base de datos

## 1. Crear clave (gratis, Google)

1. Entrá a https://console.cloud.google.com/
2. Creá un proyecto (ej. `Terra-Natura`).
3. **APIs y servicios** → **Biblioteca** → buscá **YouTube Data API v3** → **Habilitar**.
4. **Credenciales** → **Crear credenciales** → **Clave de API**.
5. Copiá la clave.

## 2. Configurar Terra Natura

En el archivo `.env` del proyecto (copiá desde `.env.example`):

```
YOUTUBE_API_KEY=AIza...tu_clave...
```

## 3. Recolectar videos

Con el servidor apagado o prendido:

```bash
python -m backend.services.youtube_turismo_cli
```

O doble clic: `local\Recolectar-videos-YouTube.bat`

O desde el panel: http://127.0.0.1:8000/turismo → **Buscar videos en YouTube**

## Qué guarda

Por cada video real:

- Título, canal, URL, miniatura
- Duración, vistas, fecha de publicación
- Localidad asociada (Bialet, Cosquín, Carlos Paz…)
- ID YouTube (sin duplicar)

## Cuota

La API gratis da ~10.000 unidades/día. Cada búsqueda usa ~100–200 unidades.  
El script hace ~16 búsquedas → unas 2.000 unidades por corrida (cabe en el plan gratis).

## Si falla 403

- API no habilitada en el proyecto Google
- Cuota del día agotada (esperar 24 h o pedir aumento en Console)
- Clave incorrecta en `.env`
