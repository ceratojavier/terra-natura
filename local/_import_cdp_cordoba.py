"""Extrae JSON de respuesta CDP del navegador y guarda sync local."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ama" / "data" / "eventos_cordoba_turismo_sync.json"

cdp_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if not cdp_path:
    logs = sorted(Path.home().joinpath(".cursor/browser-logs").glob("cdp-response-Runtime.evaluate-*.json"))
    cdp_path = logs[-1] if logs else None
if not cdp_path or not cdp_path.is_file():
    raise SystemExit("No CDP log file")

raw = json.loads(cdp_path.read_text(encoding="utf-8"))
val = raw.get("result", {}).get("value")
if isinstance(val, str):
    payload = json.loads(val)
elif isinstance(val, dict):
    payload = val
else:
    raise SystemExit("Unexpected CDP shape")

events = payload.get("events") or []
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
    json.dumps(
        {
            "fuente": "cordobaturismo.gov.ar/wp-json/tribe/events/v1/events",
            "sync_via": "browser",
            "total_api": payload.get("total"),
            "recolectados": len(events),
            "events": events,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
print(f"OK {len(events)} eventos -> {OUT}")
