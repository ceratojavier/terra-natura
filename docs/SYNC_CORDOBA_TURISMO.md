# Sincronizar agenda Córdoba Turismo (cuando Python recibe 403)

El sitio bloquea bots; en **Chrome** la API funciona.

## Opción A — Consola del navegador (5 minutos)

1. Abrí https://cordobaturismo.gov.ar/agenda/ en Chrome.
2. `F12` → pestaña **Consola**.
3. Pegá y ejecutá:

```javascript
(async () => {
  const out = [];
  let page = 1;
  let total = 9999;
  while (out.length < total && page < 25) {
    const u = `https://cordobaturismo.gov.ar/wp-json/tribe/events/v1/events?per_page=50&page=${page}&start_date=2026-01-01&end_date=2027-03-31`;
    const d = await fetch(u).then((r) => r.json());
    total = d.total || 0;
    out.push(...(d.events || []));
    if (!d.events?.length) break;
    page++;
  }
  const blob = new Blob(
    [JSON.stringify({ fuente: "browser", total, recolectados: out.length, events: out }, null, 2)],
    { type: "application/json" }
  );
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "eventos_cordoba_turismo_sync.json";
  a.click();
  console.log("Descargado", out.length, "eventos");
})();
```

4. Mové el archivo descargado a:  
   `ama/data/eventos_cordoba_turismo_sync.json`
5. Ejecutá `local/Actualizar-agenda-eventos.bat` o reiniciá el servidor y abrí el programa.

## Opción B — Playwright (automático en tu PC)

```powershell
pip install playwright
playwright install
cd "ruta\Proyecto Terra Natura"
py -m ama.scrapers.sources_cordoba_turismo --playwright
```

## Verificar

```powershell
py -m ama.scrapers.sources_cordoba_turismo
```

Deberías ver `Relevantes Bialet: 30+` (según rango de fechas).

Revisá descartados en `ama/data/eventos_cordoba_turismo_auditoria.json`.
