# Terra Natura — Guía huésped (Smart TV / celular)

Sitio estático para abrir en el **navegador de la Smart TV** (Samsung, LG, Android TV) o desde el celular con el mismo QR.

## Cómo usar en la TV

1. Subí esta carpeta `guest-app/` al mismo servidor donde corra la web (o abrila en local durante pruebas).
2. En la TV: abrir **Internet / Navegador** y escribir la URL, por ejemplo `https://TU-DOMINIO.com/guia/`.
3. Recomendación: **marcar favorito** en el TV y dejar un **QR** en la mesa de living que apunte a esa URL.
4. Actualizá contenido editando solo `data.json` (no hace falta recompilar).

## Personalización por estadía

Opcional: enlazar con días de estadía

`index.html?noches=5` — el bloque “Según cuánto te quedás” filtra sugerencias (`min_noches` en `data.json`).

## Seguridad

No incluir contraseñas ni datos sensibles en `data.json`. Solo info pública de turismo.
