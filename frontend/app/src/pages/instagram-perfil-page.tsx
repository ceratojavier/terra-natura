import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Camera, Check, Copy, ExternalLink } from "lucide-react";
import { useState } from "react";
import { api } from "@/api/client";
import { PageIntro } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface KitPerfil {
  perfil: {
    nombre_perfil?: string;
    usuario_sugerido?: string;
    bio?: string;
    link_bio?: string;
    ubicacion_maps?: string;
    checklist_perfil?: Array<{
      paso: number;
      titulo: string;
      descripcion: string;
    }>;
    highlights?: Array<{
      nombre: string;
      emoji?: string;
      que_subir: string;
    }>;
    tips?: string[];
  };
  pilares?: Record<string, string>;
  publicaciones?: Array<{
    orden: number;
    fecha_sugerida?: string;
    titulo?: string;
    formato?: string;
    pilar?: string;
  }>;
}

function CopyBlock({ label, text }: { label: string; text: string }) {
  const [ok, setOk] = useState(false);
  const copiar = async () => {
    await navigator.clipboard.writeText(text);
    setOk(true);
    setTimeout(() => setOk(false), 2000);
  };
  return (
    <div className="rounded-xl border border-[#e8efe5] bg-[#fafcf9] p-4">
      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="text-sm font-semibold text-[#4a7c59]">{label}</span>
        <Button type="button" variant="secondary" size="sm" onClick={copiar}>
          {ok ? (
            <>
              <Check className="h-4 w-4" /> Copiado
            </>
          ) : (
            <>
              <Copy className="h-4 w-4" /> Copiar
            </>
          )}
        </Button>
      </div>
      <pre className="whitespace-pre-wrap font-sans text-sm text-[#2a4034]">
        {text}
      </pre>
    </div>
  );
}

export function InstagramPerfilPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["instagram-perfil"],
    queryFn: () => api.get<KitPerfil>("/api/ama/instagram-perfil"),
  });

  const p = data?.perfil;

  return (
    <>
      <PageIntro
        title="Perfil profesional de Instagram"
        subtitle="Guía paso a paso: bio, link, historias destacadas y plan de publicaciones. Copiá cada texto y pegalo en la app de Instagram en el celular."
      />

      {isLoading && <Skeleton className="h-64 w-full rounded-2xl" />}

      {p && (
        <div className="space-y-6">
          <Card className="border-[#c5d9be] bg-[#eef6eb]">
            <CardContent className="pt-5">
              <p className="text-sm text-[#3d5345]">
                Abrí <strong>Instagram</strong> en el teléfono → tu perfil →{" "}
                <strong>Editar perfil</strong>. Seguí la lista de abajo en orden.
                Cuando termines, volvé acá para crear el Reel del calendario.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Link to="/calendario">
                  <Button type="button" variant="default">
                    Ir al calendario (Reels)
                  </Button>
                </Link>
                <a
                  href={p.link_bio}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Button type="button" variant="secondary">
                    <ExternalLink className="h-4 w-4" />
                    Ver web de reservas
                  </Button>
                </a>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-[#4a7c59]" />
                Checklist (en Instagram)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="space-y-3">
                {(p.checklist_perfil ?? []).map((c) => (
                  <li
                    key={c.paso}
                    className="flex gap-3 rounded-xl border border-[#e8efe5] px-4 py-3"
                  >
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#4a7c59] text-sm font-bold text-white">
                      {c.paso}
                    </span>
                    <div>
                      <p className="font-semibold text-[#2a4034]">{c.titulo}</p>
                      <p className="text-sm text-[#5c6f63]">{c.descripcion}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>

          <CopyBlock
            label="Biografía (pegar en Instagram)"
            text={p.bio ?? ""}
          />

          <CopyBlock
            label="Nombre del perfil"
            text={p.nombre_perfil ?? "Cabañas Alpinas Terra Natura"}
          />

          <CopyBlock
            label="Usuario sugerido (@)"
            text={`@${p.usuario_sugerido ?? "alpinasterranatura"}`}
          />

          <CopyBlock label="Link en la bio" text={p.link_bio ?? ""} />

          {p.ubicacion_maps && (
            <CopyBlock label="Ubicación (Maps)" text={p.ubicacion_maps} />
          )}

          <Card>
            <CardHeader>
              <CardTitle>Historias destacadas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-[#5c6f63]">
                En Instagram: subí historias → destacar → creá cada carpeta con
                este nombre y contenido:
              </p>
              {(p.highlights ?? []).map((h) => (
                <div
                  key={h.nombre}
                  className="rounded-xl border border-[#e8efe5] p-4"
                >
                  <p className="font-semibold text-[#2a4034]">
                    {h.emoji} {h.nombre}
                  </p>
                  <p className="mt-1 text-sm text-[#5c6f63]">{h.que_subir}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          {data?.pilares && (
            <Card>
              <CardHeader>
                <CardTitle>Los 3 pilares del feed</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-[#3d5345]">
                {Object.entries(data.pilares).map(([k, v]) => (
                  <p key={k}>
                    <strong className="capitalize">{k.replace("_", " ")}:</strong>{" "}
                    {v}
                  </p>
                ))}
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Plan de 12 publicaciones (junio)</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-[#5c6f63]">
                Cada fila es un post del mes. El primero del 3/06 es el Reel del
                arroyo — lo armás desde el Calendario.
              </p>
              <ul className="space-y-2 text-sm">
                {(data?.publicaciones ?? []).map((pub) => (
                  <li
                    key={pub.orden}
                    className="flex flex-wrap items-baseline gap-2 rounded-lg bg-[#f4f8f2] px-3 py-2"
                  >
                    <span className="font-mono text-xs text-[#6b7f72]">
                      {pub.fecha_sugerida}
                    </span>
                    <span className="font-medium text-[#2a4034]">
                      {pub.titulo}
                    </span>
                    <span className="text-xs text-[#7a8f80]">
                      {pub.formato} · {pub.pilar}
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {(p.tips ?? []).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Consejos finales</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc space-y-1 pl-5 text-sm text-[#5c6f63]">
                  {p.tips!.map((t) => (
                    <li key={t}>{t}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </>
  );
}
