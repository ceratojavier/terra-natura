# Publicación web — GitHub Pages + Cloudflare + NIC.ar

Esta guía deja la web pública primero en GitHub Pages y luego con dominio propio `alpinasterranatura.com.ar`.

## 1) Publicar en GitHub Pages (temporal)

1. Subir el repo a GitHub (rama `main` o `master`).
2. Ir a **Settings → Pages** del repositorio.
3. En **Build and deployment** elegir **GitHub Actions**.
4. El workflow `deploy-pages.yml` publica automáticamente `frontend/public`.
5. URL temporal esperada: `https://<usuario>.github.io/<repositorio>/`.

## 2) Preparar dominio en Cloudflare

1. Crear cuenta gratis en Cloudflare.
2. Agregar zona `alpinasterranatura.com.ar`.
3. Cloudflare mostrará 2 nameservers (ejemplo: `ns1...` y `ns2...`).

## 3) Delegar dominio en NIC.ar

1. Entrar a NIC.ar con el titular del dominio.
2. Abrir `alpinasterranatura.com.ar`.
3. Reemplazar nameservers por los de Cloudflare.
4. Guardar cambios.
5. Esperar propagación (puede demorar varias horas).

## 4) DNS en Cloudflare apuntando a GitHub Pages

Crear estos registros DNS:

- `A` para `@` a:
  - `185.199.108.153`
  - `185.199.109.153`
  - `185.199.110.153`
  - `185.199.111.153`
- `CNAME` para `www` a: `<usuario>.github.io`

Recomendado:
- Proxy de Cloudflare en **DNS only** al inicio (nube gris) hasta que valide SSL.

## 5) Configurar dominio en GitHub Pages

1. En **Settings → Pages**, campo **Custom domain**:
   - `alpinasterranatura.com.ar`
2. Guardar.
3. Marcar **Enforce HTTPS** cuando aparezca disponible.

## 6) CNAME en el sitio (cuando ya esté aprobado el dominio)

Crear archivo `frontend/public/CNAME` con:

`alpinasterranatura.com.ar`

No crear este archivo antes de tener el dominio activo, para no cortar la URL temporal de GitHub Pages.
