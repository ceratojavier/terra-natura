import { useEffect, useState } from "react";
import { Film, ImageIcon, Sparkles, ChevronRight, ChevronLeft } from "lucide-react";
import {
  generarPrompt,
  imagenAVideo,
  estadoApp,
  type ResultadoCompleto,
} from "@/lib/api";
import { ResultView } from "@/components/ResultView";

type Modo = "inicio" | "imagen" | "wizard" | "resultado";

const PASOS = [
  {
    key: "personajes",
    titulo: "Personaje o personajes",
    hint: "Quién aparece, actitud y presencia.",
    placeholder: "modelo femenina editorial de lujo, actitud serena",
    ejemplos: [
      "hombre joven con traje negro y actitud segura",
      "pareja elegante caminando",
      "mujer elegante en vestido fluido",
    ],
  },
  {
    key: "ambientacion",
    titulo: "Ambientación",
    hint: "Dónde ocurre la escena.",
    placeholder: "rooftop de ciudad moderna al atardecer",
    ejemplos: ["mansión minimalista", "calle urbana nocturna", "playa sofisticada"],
  },
  {
    key: "iluminacion",
    titulo: "Hora del día o iluminación",
    hint: "Luz que define el mood.",
    placeholder: "golden hour, luz cálida lateral",
    ejemplos: [
      "noche con luces de ciudad",
      "luz suave natural",
      "iluminación dramática cinematográfica",
    ],
  },
  {
    key: "estilo",
    titulo: "Estilo visual",
    hint: "Acabado y sensación de marca.",
    placeholder: "cinematográfico premium",
    ejemplos: ["lujo publicitario", "fashion film", "realista premium"],
  },
] as const;

export default function App() {
  const [modo, setModo] = useState<Modo>("inicio");
  const [paso, setPaso] = useState(0);
  const [form, setForm] = useState({
    personajes: "",
    ambientacion: "",
    iluminacion: "",
    estilo: "",
  });
  const [resultado, setResultado] = useState<ResultadoCompleto | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [veoOk, setVeoOk] = useState(false);

  const [imagenFile, setImagenFile] = useState<File | null>(null);
  const [imagenPreview, setImagenPreview] = useState<string | null>(null);
  const [promptImagen, setPromptImagen] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  useEffect(() => {
    estadoApp().then((e) => setVeoOk(e.veo?.disponible ?? false));
  }, []);

  const campo = PASOS[paso]?.key as keyof typeof form;

  async function finalizarWizard() {
    setLoading(true);
    setError("");
    try {
      const r = await generarPrompt(form);
      setResultado(r);
      setModo("resultado");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function enviarImagen() {
    if (!imagenFile) {
      setError("Subí una imagen primero.");
      return;
    }
    setLoading(true);
    setError("");
    setVideoUrl(null);
    const fd = new FormData();
    fd.append("imagen", imagenFile);
    fd.append("prompt", promptImagen);
    fd.append("personajes", form.personajes);
    fd.append("ambientacion", form.ambientacion);
    fd.append("iluminacion", form.iluminacion);
    fd.append("estilo", form.estilo || "cinematográfico premium");
    fd.append("generar_veo", "true");
    try {
      const res = (await imagenAVideo(fd)) as {
        paquete: ResultadoCompleto;
        veo?: { ok?: boolean; url_descarga?: string; mensaje_usuario?: string };
      };
      setResultado(res.paquete);
      if (res.veo?.ok && res.veo.url_descarga) {
        setVideoUrl(res.veo.url_descarga);
      }
      setModo("resultado");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  function usarVariante(v: "cinematografica" | "realista" | "premium") {
    if (!resultado) return;
    const pack = resultado.variantes[v];
    setResultado({
      ...resultado,
      resumen: pack.resumen,
      descripcion_visual: pack.descripcion_visual,
      prompt_final: pack.prompt_final,
      elementos_definidos: pack.elementos || resultado.elementos_definidos,
    });
  }

  return (
    <div className="mx-auto min-h-screen max-w-3xl px-4 py-10">
      <header className="mb-10 text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-fuchsia-600 shadow-lg shadow-violet-900/40">
          <Film className="h-7 w-7 text-white" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight">Video Pro Creator</h1>
        <p className="mt-2 text-sm text-zinc-400">
          Cuatro datos. Un director creativo. Prompts en español (España) listos para Veo.
        </p>
        <p className="mt-1 text-xs text-zinc-500">
          Veo: {veoOk ? "conectado" : "sin API key — solo prompts"}
        </p>
      </header>

      {modo === "inicio" && (
        <div className="grid gap-4 sm:grid-cols-2">
          <button
            type="button"
            className="group rounded-2xl border border-violet-500/40 bg-gradient-to-b from-violet-950/80 to-zinc-900 p-6 text-left transition hover:border-violet-400"
            onClick={() => setModo("imagen")}
          >
            <ImageIcon className="mb-3 h-8 w-8 text-violet-400" />
            <h2 className="text-lg font-semibold">Vídeo desde imagen</h2>
            <p className="mt-2 text-sm text-zinc-400">
              Subí una foto, describí el movimiento y generamos con Veo 3.1 automáticamente.
            </p>
            <span className="mt-4 inline-flex items-center text-sm text-violet-400">
              Empezar <ChevronRight className="h-4 w-4" />
            </span>
          </button>
          <button
            type="button"
            className="group rounded-2xl border border-zinc-700 bg-zinc-900/80 p-6 text-left transition hover:border-zinc-500"
            onClick={() => {
              setModo("wizard");
              setPaso(0);
            }}
          >
            <Sparkles className="mb-3 h-8 w-8 text-fuchsia-400" />
            <h2 className="text-lg font-semibold">Crear desde cero</h2>
            <p className="mt-2 text-sm text-zinc-400">
              Personaje, ambiente, luz y estilo en 4 pasos. Prompt cinematográfico al instante.
            </p>
            <span className="mt-4 inline-flex items-center text-sm text-zinc-300">
              Empezar <ChevronRight className="h-4 w-4" />
            </span>
          </button>
        </div>
      )}

      {modo === "imagen" && (
        <div className="space-y-6">
          <button
            type="button"
            className="text-sm text-zinc-500 hover:text-zinc-300"
            onClick={() => setModo("inicio")}
          >
            ← Volver
          </button>
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6">
            <h2 className="mb-4 text-lg font-semibold">Imagen + prompt de movimiento</h2>
            <label className="mb-4 flex cursor-pointer flex-col items-center rounded-xl border-2 border-dashed border-zinc-700 py-12 hover:border-violet-500">
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (!f) return;
                  setImagenFile(f);
                  setImagenPreview(URL.createObjectURL(f));
                }}
              />
              {imagenPreview ? (
                <img
                  src={imagenPreview}
                  alt="Vista previa"
                  className="max-h-48 rounded-lg object-contain"
                />
              ) : (
                <span className="text-sm text-zinc-500">Tocá para subir foto o JPG/PNG</span>
              )}
            </label>
            <textarea
              className="mb-3 w-full rounded-xl border border-zinc-700 bg-black/40 p-4 text-sm placeholder:text-zinc-600"
              rows={3}
              placeholder="Ej.: cámara lenta, el viento mueve el vestido, luz dorada…"
              value={promptImagen}
              onChange={(e) => setPromptImagen(e.target.value)}
            />
            <p className="mb-4 text-xs text-zinc-500">Opcional: refinar ambiente y estilo</p>
            <div className="grid gap-2 sm:grid-cols-2">
              <input
                className="rounded-lg border border-zinc-700 bg-black/30 px-3 py-2 text-sm"
                placeholder="Ambientación (opcional)"
                value={form.ambientacion}
                onChange={(e) => setForm({ ...form, ambientacion: e.target.value })}
              />
              <input
                className="rounded-lg border border-zinc-700 bg-black/30 px-3 py-2 text-sm"
                placeholder="Estilo (opcional)"
                value={form.estilo}
                onChange={(e) => setForm({ ...form, estilo: e.target.value })}
              />
            </div>
            <button
              type="button"
              disabled={loading}
              className="mt-6 w-full rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 py-3 font-semibold disabled:opacity-50"
              onClick={enviarImagen}
            >
              {loading ? "Generando con Veo…" : "Generar vídeo y prompts"}
            </button>
          </div>
        </div>
      )}

      {modo === "wizard" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <button
              type="button"
              className="text-sm text-zinc-500"
              onClick={() => (paso === 0 ? setModo("inicio") : setPaso(paso - 1))}
            >
              <ChevronLeft className="inline h-4 w-4" /> Atrás
            </button>
            <span className="text-xs text-zinc-500">
              Paso {paso + 1} de {PASOS.length}
            </span>
          </div>
          <div className="h-1 overflow-hidden rounded-full bg-zinc-800">
            <div
              className="h-full bg-violet-500 transition-all"
              style={{ width: `${((paso + 1) / PASOS.length) * 100}%` }}
            />
          </div>
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6">
            <h2 className="text-xl font-semibold">{PASOS[paso].titulo}</h2>
            <p className="mt-1 text-sm text-zinc-400">{PASOS[paso].hint}</p>
            <textarea
              className="mt-4 w-full rounded-xl border border-zinc-700 bg-black/40 p-4 text-base"
              rows={3}
              placeholder={PASOS[paso].placeholder}
              value={form[campo]}
              onChange={(e) => setForm({ ...form, [campo]: e.target.value })}
            />
            <p className="mt-3 text-xs text-zinc-500">Ejemplos:</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {PASOS[paso].ejemplos.map((ej) => (
                <button
                  key={ej}
                  type="button"
                  className="rounded-full border border-zinc-700 px-3 py-1 text-xs text-zinc-400 hover:border-violet-500 hover:text-violet-300"
                  onClick={() => setForm({ ...form, [campo]: ej })}
                >
                  {ej}
                </button>
              ))}
            </div>
            <button
              type="button"
              className="mt-6 w-full rounded-xl bg-violet-600 py-3 font-semibold hover:bg-violet-500"
              disabled={loading}
              onClick={() => {
                if (paso < PASOS.length - 1) setPaso(paso + 1);
                else finalizarWizard();
              }}
            >
              {loading
                ? "Creando dirección visual…"
                : paso < PASOS.length - 1
                  ? "Siguiente"
                  : "Ver prompt final"}
            </button>
          </div>
        </div>
      )}

      {modo === "resultado" && resultado && (
        <div>
          <button
            type="button"
            className="mb-6 text-sm text-zinc-500 hover:text-zinc-300"
            onClick={() => {
              setModo("inicio");
              setResultado(null);
              setVideoUrl(null);
            }}
          >
            ← Nuevo proyecto
          </button>
          <ResultView
            data={resultado}
            videoUrl={videoUrl}
            onRegenerar={usarVariante}
          />
        </div>
      )}

      {error && (
        <p className="mt-4 rounded-lg bg-red-950/50 px-4 py-3 text-sm text-red-300">
          {error}
        </p>
      )}
    </div>
  );
}
