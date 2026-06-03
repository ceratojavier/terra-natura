# Restaurar carpeta `archivos multimedia/`

**No fue eliminada del proyecto:** está listada en `.gitignore` para que Git/GitHub no suban gigas de fotos.

Si en tu PC no ves la carpeta dentro del repo, copiá de nuevo desde Google Drive o tu backup:

```
Proyecto Terra Natura/
└── archivos multimedia/
    └── fotos terra natura/
        ├── CABANA ALPINA 1/
        ├── CABANA ALPINA 2/
        ...
```

Luego ejecutá:

```bash
python scripts/build_web_gallery.py
```

Eso regenera `frontend/public/media/galeria/` y `frontend/public/media/unidades/` con fotos optimizadas para la web.
