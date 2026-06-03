import { Copy, Check } from "lucide-react";
import { useState } from "react";
import type { ResultadoCompleto } from "@/lib/api";

function CopyBtn({ text }: { text: string }) {
  const [ok, setOk] = useState(false);
  return (
    <button
      type="button"
      className="inline-flex items-center gap-1 rounded-lg bg-violet-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-violet-500"
      onClick={() => {
        navigator.clipboard.writeText(text);
        setOk(true);
        setTimeout(() => setOk(false), 2000);
      }}
    >
      {ok ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
      {ok ? "Copiado" : "Copiar"}
    </button>
  );
}

function Bloque({
  titulo,
  contenido,
  prompt,
}: {
  titulo: string;
  contenido: string;
  prompt?: string;
}) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/80 p-5">
      <div className="mb-2 flex items-center justify-between gap-2">
        <h3 className="font-semibold text-violet-300">{titulo}</h3>
        {prompt && <CopyBtn text={prompt} />}
      </div>
      <p className="mb-3 text-sm text-zinc-400">{contenido}</p>
      {prompt && (
        <pre className="max-h-48 overflow-y-auto whitespace-pre-wrap rounded-xl bg-black/50 p-4 text-sm text-zinc-200">
          {prompt}
        </pre>
      )}
    </div>
  );
}

export function ResultView({
  data,
  videoUrl,
  onRegenerar,
}: {
  data: ResultadoCompleto;
  videoUrl?: string | null;
  onRegenerar?: (variante: "cinematografica" | "realista" | "premium") => void;
}) {
  return (
    <div className="space-y-6">
      <p className="text-xs uppercase tracking-widest text-zinc-500">
        Resultado · {data.idioma}
      </p>

      {videoUrl && (
        <div className="rounded-2xl border border-emerald-800/50 bg-emerald-950/30 p-4">
          <p className="mb-2 font-medium text-emerald-400">Vídeo generado (Veo)</p>
          <video src={videoUrl} controls className="w-full max-h-96 rounded-xl" />
        </div>
      )}

      <Bloque titulo="Resumen" contenido={data.resumen} />

      <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-5">
        <h3 className="mb-3 font-semibold text-zinc-200">Elementos definidos</h3>
        <ul className="space-y-2 text-sm text-zinc-400">
          {Object.entries(data.elementos_definidos).map(([k, v]) => (
            <li key={k}>
              <span className="font-medium text-zinc-300 capitalize">{k}: </span>
              {v}
            </li>
          ))}
        </ul>
      </div>

      <Bloque
        titulo="Descripción visual mejorada"
        contenido={data.descripcion_visual}
      />

      <Bloque
        titulo="Prompt final"
        contenido="Listo para Veo, Runway o tu herramienta de vídeo IA."
        prompt={data.prompt_final}
      />

      <div>
        <h3 className="mb-3 text-sm font-semibold text-zinc-400">Variantes</h3>
        <div className="grid gap-4 lg:grid-cols-3">
          {(
            [
              ["cinematografica", "Más cinematográfica", "cinematografica"],
              ["realista", "Más realista", "realista"],
              ["premium", "Más premium", "premium"],
            ] as const
          ).map(([key, label, v]) => {
            const pack = data.variantes[key];
            return (
              <div
                key={key}
                className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-4"
              >
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-medium">{label}</span>
                  {onRegenerar && (
                    <button
                      type="button"
                      className="text-xs text-violet-400 hover:underline"
                      onClick={() => onRegenerar(v)}
                    >
                      Usar
                    </button>
                  )}
                </div>
                <p className="mb-2 line-clamp-2 text-xs text-zinc-500">
                  {pack.resumen}
                </p>
                <CopyBtn text={pack.prompt_final} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
