import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "@/api/client";
import { Button } from "@/components/ui/button";
import { PageIntro } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function ConfigPage() {
  const conex = useQuery({
    queryKey: ["conexiones"],
    queryFn: () =>
      api.get<{
        instagram: { conectado: boolean; mensaje_dueno: string; ayuda?: string };
        video_ia: Record<string, { disponible?: boolean; nombre?: string }>;
      }>("/api/ama/conexiones"),
  });

  const agentes = useQuery({
    queryKey: ["agentes-lista"],
    queryFn: () =>
      api.get<{
        agentes: Array<{
          id: string;
          nombre: string;
          descripcion: string;
          icono?: string;
        }>;
      }>("/api/agentes"),
  });

  return (
    <>
      <PageIntro
        title="Configuración"
        subtitle="Conexiones para publicar en Instagram y, si querés curiosear, los módulos automáticos del sistema."
      />

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Instagram</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-[#5c6f63]">
          <Link to="/instagram-perfil" className="mb-4 inline-block">
            <Button type="button" variant="default">
              Crear / mejorar perfil profesional
            </Button>
          </Link>
          <p className="mb-3 text-xs text-[#7a8f80]">
            Bio, destacadas, link y grilla de posts — sin salir del panel.
          </p>
          {conex.isLoading ? (
            <Skeleton className="h-12 w-full" />
          ) : (
            <>
              <Badge variant={conex.data?.instagram.conectado ? "success" : "warning"}>
                {conex.data?.instagram.conectado ? "Conectado" : "Sin conectar"}
              </Badge>
              <p className="mt-3">{conex.data?.instagram.mensaje_dueno}</p>
              <p className="mt-2 text-xs">
                En el servidor, archivo <code className="rounded bg-[#f0f4ee] px-1">.env</code>
                : META_PAGE_ACCESS_TOKEN y META_IG_BUSINESS_ACCOUNT_ID. Pedile al
                programador o usá la guía de Meta Business.
              </p>
            </>
          )}
        </CardContent>
      </Card>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Herramientas de video (opcional)</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-[#5c6f63]">
          <p className="mb-3">
            El sistema arma videos con tus fotos y FFmpeg. APIs extra (Pexels, etc.)
            solo si hay clave configurada.
          </p>
          <a
            href="/video-pro/"
            className="inline-flex items-center rounded-xl bg-[#4a7c59] px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-[#3d6849]"
          >
            Abrir Video Pro Creator
          </a>
          <p className="mt-2 text-xs text-[#7a8f80]">
            Prompts en español y animación de fotos con Veo (si hay clave Google en el
            servidor).
          </p>
          {conex.data?.video_ia && (
            <ul className="space-y-1 text-xs">
              {Object.entries(conex.data.video_ia).slice(0, 8).map(([k, v]) => (
                <li key={k}>
                  {k}: {v?.disponible ? "disponible" : "no configurado"}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Módulos automáticos (avanzado)</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4 text-sm text-[#5c6f63]">
            Estos trabajos corren solos cuando tocás &quot;Preparar publicación&quot;.
            No hace falta ejecutarlos uno por uno salvo pruebas.
          </p>
          {agentes.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : (
            <ul className="space-y-3">
              {agentes.data?.agentes.map((a) => (
                <li
                  key={a.id}
                  className="rounded-lg border border-[#e8efe5] px-3 py-2 text-sm"
                >
                  <span className="mr-2">{a.icono}</span>
                  <strong>{a.nombre}</strong>
                  <p className="text-xs text-[#6b7f72]">{a.descripcion}</p>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </>
  );
}
