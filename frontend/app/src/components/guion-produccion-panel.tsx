import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Copy, Film, RefreshCw, Video } from "lucide-react";
import { api } from "@/api/client";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface EscenaProduccion {
  numero: number;
  tipo?: string;
  titulo_escena?: string;
  duracion_seg?: number;
  descripcion_visual?: string;
  youtube_busqueda?: string;
  youtube_id?: string | null;
  youtube_url?: string | null;
  youtube_inicio_seg?: number | null;
  youtube_fin_seg?: number | null;
  instruccion_usuario?: string;
  estado?: string;
  foto_ruta?: string;
  fuente?: string;
  foto_justificacion?: string;
  foto_calidad?: { ok?: boolean; nivel?: string; mensaje?: string; ancho?: number; alto?: number };
  texto_pantalla?: string;
  effect?: string;
}

export interface GuionProduccion {
  concepto?: string;
  arco?: string;
  hook?: string;
  voz_off?: string;
  duracion_total_seg?: number;
  escenas?: EscenaProduccion[];
  prompt_video_pro?: string;
  listo_para_render?: boolean;
  escenas_pendientes_youtube?: number;
  checklist?: string[];
}

function parseTiempo(input: string): number | null {
  const s = input.trim();
  if (!s) return null;
  if (/^\d+(\.\d+)?$/.test(s)) return parseFloat(s);
  const m = s.match(/^(\d+):(\d{1,2})(?:\.(\d+))?$/);
  if (m) return parseInt(m[1], 10) * 60 + parseInt(m[2], 10) + (m[3] ? parseFloat(`0.${m[3]}`) : 0);
  return null;
}

function estadoBadge(estado?: string) {
  if (estado === "listo")
    return (
      <span className="rounded bg-[#dcfce7] px-1.5 py-0.5 text-[10px] font-semibold text-[#166534]">
        Listo
      </span>
    );
  if (estado === "pendiente_youtube")
    return (
      <span className="rounded bg-[#ffedd5] px-1.5 py-0.5 text-[10px] font-semibold text-[#c2410c]">
        Falta YouTube
      </span>
    );
  if (estado === "pendiente_foto")
    return (
      <span className="rounded bg-[#fee2e2] px-1.5 py-0.5 text-[10px] font-semibold text-[#b91c1c]">
        Falta foto
      </span>
    );
  return null;
}

function EscenaCard({
  esc,
  hitoId,
  piezaId,
  onSaved,
}: {
  esc: EscenaProduccion;
  hitoId: string;
  piezaId: string;
  onSaved: (gp: GuionProduccion) => void;
}) {
  const [url, setUrl] = useState(esc.youtube_url || esc.youtube_id || "");
  const [inicio, setInicio] = useState(
    esc.youtube_inicio_seg != null ? String(esc.youtube_inicio_seg) : ""
  );
  const [fin, setFin] = useState(
    esc.youtube_fin_seg != null ? String(esc.youtube_fin_seg) : ""
  );

  const save = useMutation({
    mutationFn: () =>
      api.patch<{ guion_produccion: GuionProduccion }>("/api/ama/guion-produccion/escena", {
        hito_id: hitoId,
        pieza_id: piezaId,
        numero: esc.numero,
        youtube_url: url || undefined,
        youtube_inicio_seg: parseTiempo(inicio) ?? undefined,
        youtube_fin_seg: parseTiempo(fin) ?? undefined,
      }),
    onSuccess: (d) => onSaved(d.guion_produccion),
  });

  const esYt = esc.tipo === "broll_youtube" || esc.tipo === "clip_youtube";
  const esFoto = esc.tipo === "foto";

  return (
    <li className="rounded-xl border border-[#dce5d8] bg-[#fafcf9] p-4">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <span className="font-bold text-[#2a4034]">
          Escena {esc.numero} — {esc.titulo_escena}
        </span>
        <span className="text-xs text-[#6b7f72]">[{esc.tipo}] {esc.duracion_seg}s</span>
        {estadoBadge(esc.estado)}
      </div>

      {esc.descripcion_visual && (
        <p className="mb-2 text-sm text-[#3d5345]">{esc.descripcion_visual}</p>
      )}
      {esc.texto_pantalla && (
        <p className="mb-2 text-xs italic text-[#6b7f72]">Texto en pantalla: {esc.texto_pantalla}</p>
      )}

      {esYt && (
        <div className="mt-3 space-y-2 rounded-lg bg-[#f0f7ff] p-3">
          <p className="text-xs font-semibold text-[#1e40af]">Buscar en YouTube (copiá el título)</p>
          <div className="flex gap-2">
            <code className="flex-1 rounded bg-white px-2 py-1.5 text-xs text-[#1e3a5f]">
              {esc.youtube_busqueda}
            </code>
            <Button
              type="button"
              variant="secondary"
              className="shrink-0 text-xs"
              onClick={() => navigator.clipboard.writeText(esc.youtube_busqueda || "")}
            >
              <Copy className="h-3.5 w-3.5" />
            </Button>
          </div>
          <p className="text-[11px] text-[#64748b]">{esc.instruccion_usuario}</p>
          <label className="block text-xs font-medium text-[#334155]">
            Link o ID del video elegido
            <input
              className="mt-1 w-full rounded-lg border border-[#cbd5e1] px-2 py-1.5 text-sm"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=..."
            />
          </label>
          <div className="grid grid-cols-2 gap-2">
            <label className="text-xs font-medium text-[#334155]">
              Inicio (seg o m:ss)
              <input
                className="mt-1 w-full rounded-lg border border-[#cbd5e1] px-2 py-1.5 text-sm"
                value={inicio}
                onChange={(e) => setInicio(e.target.value)}
                placeholder="0:45"
              />
            </label>
            <label className="text-xs font-medium text-[#334155]">
              Fin (seg o m:ss)
              <input
                className="mt-1 w-full rounded-lg border border-[#cbd5e1] px-2 py-1.5 text-sm"
                value={fin}
                onChange={(e) => setFin(e.target.value)}
                placeholder="0:52"
              />
            </label>
          </div>
          <Button
            type="button"
            size="sm"
            disabled={save.isPending}
            onClick={() => save.mutate()}
          >
            Guardar escena YouTube
          </Button>
        </div>
      )}

      {esFoto && (
        <div className="mt-3 space-y-1 rounded-lg bg-[#f4f8f2] p-3 text-sm">
          <p className="font-medium text-[#2a4034]">Foto sugerida</p>
          <p className="break-all text-xs text-[#4a7c59]">
            {esc.foto_ruta || esc.fuente || "— sin archivo —"}
          </p>
          {esc.foto_justificacion && (
            <p className="text-xs text-[#5c6f63]">{esc.foto_justificacion}</p>
          )}
          {esc.foto_calidad && (
            <p
              className={cn(
                "text-xs font-medium",
                esc.foto_calidad.nivel === "ok" && "text-[#166534]",
                esc.foto_calidad.nivel === "advertencia" && "text-[#a16207]",
                esc.foto_calidad.nivel === "bajo" && "text-[#b91c1c]"
              )}
            >
              {esc.foto_calidad.mensaje}
              {esc.foto_calidad.ancho
                ? ` (${esc.foto_calidad.ancho}×${esc.foto_calidad.alto})`
                : ""}
            </p>
          )}
        </div>
      )}
    </li>
  );
}

export function GuionProduccionPanel({
  hitoId,
  piezaId,
  initial,
  formato,
}: {
  hitoId: string;
  piezaId: string;
  initial?: GuionProduccion;
  formato?: string;
}) {
  const [gp, setGp] = useState<GuionProduccion | undefined>(initial);
  const [renderMsg, setRenderMsg] = useState("");

  useEffect(() => {
    setGp(initial);
  }, [initial]);

  const generar = useMutation({
    mutationFn: () =>
      api.post<{ guion_produccion: GuionProduccion }>("/api/ama/guion-produccion/generar", {
        hito_id: hitoId,
        pieza_id: piezaId,
      }),
    onSuccess: (d) => setGp(d.guion_produccion),
  });

  const render = useMutation({
    mutationFn: () =>
      api.post<{ ok: boolean; ruta?: string; mensaje?: string; error?: string }>(
        "/api/ama/guion-produccion/render",
        { hito_id: hitoId, pieza_id: piezaId }
      ),
    onSuccess: (d) => {
      setRenderMsg(d.ruta ? `Video listo: ${d.ruta}` : d.mensaje || "Generado");
    },
    onError: (e: Error) => setRenderMsg(e.message),
  });

  const fmt = (formato || "").toLowerCase();
  if (fmt && fmt !== "reel" && fmt !== "status") {
    return (
      <p className="text-sm text-[#6b7f72]">
        Guion de producción por escenas está disponible para Reels y Status.
      </p>
    );
  }

  return (
    <section className="space-y-4 border-t border-[#e8efe5] pt-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h4 className="font-semibold text-[#4a7c59]">Producción de video por escenas</h4>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            disabled={generar.isPending}
            onClick={() => generar.mutate()}
          >
            <RefreshCw className={cn("mr-1 h-3.5 w-3.5", generar.isPending && "animate-spin")} />
            {gp ? "Actualizar guion" : "Armar guion de escenas"}
          </Button>
          {gp?.listo_para_render && (
            <Button
              type="button"
              size="sm"
              disabled={render.isPending}
              onClick={() => render.mutate()}
            >
              <Video className="mr-1 h-3.5 w-3.5" />
              {render.isPending ? "Generando…" : "Generar video"}
            </Button>
          )}
          <a
            href="/video-pro/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center rounded-lg border border-[#dce5d8] px-3 py-1.5 text-xs font-medium text-[#4a7c59] hover:bg-[#f4f8f2]"
          >
            <Film className="mr-1 h-3.5 w-3.5" />
            Video Pro
          </a>
        </div>
      </div>

      {!gp && (
        <p className="text-sm text-[#6b7f72]">
          Armá el guion para ver cada escena: qué buscar en YouTube, qué foto usar y por qué.
        </p>
      )}

      {gp && (
        <>
          <p className="text-sm text-[#3d5345]">{gp.concepto}</p>
          {gp.escenas_pendientes_youtube ? (
            <p className="rounded-lg bg-[#ffedd5] px-3 py-2 text-sm text-[#9a3412]">
              Faltan {gp.escenas_pendientes_youtube} escena(s) de YouTube: pegá link e inicio/fin.
            </p>
          ) : (
            <p className="rounded-lg bg-[#dcfce7] px-3 py-2 text-sm text-[#166534]">
              Todas las escenas YouTube marcadas — podés generar el video.
            </p>
          )}

          {gp.prompt_video_pro && (
            <div>
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase text-[#7a8f80]">
                  Prompt profesional (copiar)
                </span>
                <Button
                  type="button"
                  variant="secondary"
                  className="h-7 text-xs"
                  onClick={() => navigator.clipboard.writeText(gp.prompt_video_pro || "")}
                >
                  <Copy className="mr-1 h-3 w-3" />
                  Copiar todo
                </Button>
              </div>
              <pre className="max-h-40 overflow-y-auto whitespace-pre-wrap rounded-xl bg-[#faf8f4] p-3 text-xs text-[#3d5345]">
                {gp.prompt_video_pro}
              </pre>
            </div>
          )}

          <ol className="space-y-3">
            {(gp.escenas ?? []).map((esc) => (
              <EscenaCard
                key={esc.numero}
                esc={esc}
                hitoId={hitoId}
                piezaId={piezaId}
                onSaved={setGp}
              />
            ))}
          </ol>

          {renderMsg && (
            <p className="text-sm font-medium text-[#2a4034]">{renderMsg}</p>
          )}
        </>
      )}
    </section>
  );
}
