export interface PaquetePrompt {
  resumen: string;
  descripcion_visual: string;
  prompt_final: string;
  elementos?: Record<string, string>;
}

export interface ResultadoCompleto {
  idioma: string;
  resumen: string;
  elementos_definidos: Record<string, string>;
  descripcion_visual: string;
  prompt_final: string;
  variantes: {
    cinematografica: PaquetePrompt;
    realista: PaquetePrompt;
    premium: PaquetePrompt;
  };
}

export async function generarPrompt(body: {
  personajes: string;
  ambientacion: string;
  iluminacion: string;
  estilo: string;
}): Promise<ResultadoCompleto> {
  const r = await fetch("/api/video-pro/generar-prompt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, modo: "wizard" }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function imagenAVideo(form: FormData): Promise<unknown> {
  const r = await fetch("/api/video-pro/imagen-a-video", {
    method: "POST",
    body: form,
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function estadoApp(): Promise<{ veo: { disponible: boolean; mensaje: string } }> {
  const r = await fetch("/api/video-pro/estado");
  return r.json();
}
