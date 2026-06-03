import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { Camera, Sparkles } from "lucide-react";
import { api } from "@/api/client";
import { ActionCard } from "@/components/action-card";
import { PageIntro } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface PantallaHoy {
  estado: string;
  frase_principal: string;
  fecha_hoy_legible?: string;
  publicaciones_hoy: Array<{
    id: string;
    titulo?: string;
    copy?: string;
    canal_label?: string;
    tiene_video?: boolean;
    estado?: string;
  }>;
  pendientes_aprobacion: number;
  campaña_activa?: {
    id?: string;
    nombre?: string;
    dias_hasta?: number;
    estrategia?: string;
    pieza_hoy?: { id?: string; tipo_pieza_label?: string; objetivo?: string };
  };
  plan_editorial_hoy?: {
    titulo?: string;
    razon?: string;
    tipo_pieza_label?: string;
    copy_preview?: string;
    desde_campaña?: string;
    pieza_id?: string;
    fecha_publicacion?: string;
    guion_resumen?: string;
  };
  instagram?: { conectado: boolean; mensaje_dueno: string };
}

export function HoyPage() {
  const qc = useQueryClient();
  const nav = useNavigate();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["hoy"],
    queryFn: () => api.get<PantallaHoy>("/api/ama/hoy"),
    refetchInterval: 45_000,
  });

  const preparar = useMutation({
    mutationFn: () => api.post("/api/ama/preparar-contenido-hoy"),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["hoy"] });
      qc.invalidateQueries({ queryKey: ["publicaciones"] });
      nav("/publicaciones");
    },
  });

  if (isLoading) {
    return (
      <>
        <PageIntro title="Hoy" subtitle="Cargando…" />
        <Skeleton className="mb-4 h-24 w-full rounded-2xl" />
        <Skeleton className="h-40 w-full rounded-2xl" />
      </>
    );
  }

  const ig = data?.instagram;

  return (
    <>
      <PageIntro
        title={data?.fecha_hoy_legible ? `Hoy · ${data.fecha_hoy_legible}` : "Hoy"}
        subtitle="Acá ves si hay algo para publicar en Instagram y qué campaña está en marcha."
      />

      <Card className="mb-6 border-[#c5d9be] bg-[#eef6eb]">
        <CardContent className="pt-5">
          <p className="text-lg font-medium text-[#2a4034]">
            {data?.frase_principal}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge variant={ig?.conectado ? "success" : "warning"}>
              <Camera className="mr-1 h-3 w-3" />
              {ig?.conectado ? "Instagram conectado" : "Instagram sin conectar"}
            </Badge>
            {(data?.pendientes_aprobacion ?? 0) > 0 && (
              <Badge variant="warning">
                {data?.pendientes_aprobacion} para revisar
              </Badge>
            )}
          </div>
          {!ig?.conectado && (
            <p className="mt-2 text-sm text-[#5c6f63]">{ig?.mensaje_dueno}</p>
          )}
        </CardContent>
      </Card>

      <ActionCard
        title="Armar perfil profesional de Instagram"
        explanation="Bio, link, historias destacadas y plan del mes. Copiá y pegá en la app de Instagram."
        variant="secondary"
        onClick={() => nav("/instagram-perfil")}
      />

      <ActionCard
        title="Preparar publicación de hoy"
        explanation="Creo el texto y el video con tus fotos del complejo. Después lo revisás en Publicaciones."
        loading={preparar.isPending}
        onClick={() => preparar.mutate()}
      />

      <ActionCard
        title="Ver publicaciones pendientes"
        explanation="Lo que está listo para subir a Instagram o lo que falta aprobar."
        variant="secondary"
        onClick={() => nav("/publicaciones")}
      />

      <ActionCard
        title="Crear vídeo con Video Pro"
        explanation="Subí una foto o armá un prompt en 4 pasos. Resultado en español y, si hay clave Google, generación con Veo."
        variant="secondary"
        onClick={() => window.open("/video-pro/", "_blank", "noopener,noreferrer")}
      />

      {data?.campaña_activa && (
        <Card className="mb-6 mt-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-[#4a7c59]" />
              Campaña en curso
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p className="font-semibold text-[#2a4034]">
              {data.campaña_activa.nombre}
              {data.campaña_activa.dias_hasta != null && (
                <span className="font-normal text-[#6b7f72]">
                  {" "}
                  · en {data.campaña_activa.dias_hasta} días
                </span>
              )}
            </p>
            <p className="text-[#5c6f63]">{data.campaña_activa.estrategia}</p>
            {data.campaña_activa.pieza_hoy && (
              <p className="rounded-lg bg-[#f4f8f2] px-3 py-2 text-[#3d5345]">
                <strong>Hoy en el plan:</strong>{" "}
                {data.campaña_activa.pieza_hoy.tipo_pieza_label} —{" "}
                {data.campaña_activa.pieza_hoy.objetivo}
              </p>
            )}
            <Link
              to="/plan"
              className="text-sm font-semibold text-[#4a7c59] underline"
            >
              Ver plan completo y todas las fechas de publicación →
            </Link>
          </CardContent>
        </Card>
      )}

      {data?.plan_editorial_hoy && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Idea de hoy</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-[#5c6f63]">
            <p>
              <span className="font-medium text-[#2a4034]">
                {data.plan_editorial_hoy.tipo_pieza_label}
              </span>
              {data.plan_editorial_hoy.titulo && ` · ${data.plan_editorial_hoy.titulo}`}
            </p>
            <p>{data.plan_editorial_hoy.razon}</p>
            {data.plan_editorial_hoy.desde_campaña && (
              <p className="text-xs text-[#4a7c59]">
                Vinculado a campaña: {data.plan_editorial_hoy.desde_campaña}
                {data.plan_editorial_hoy.fecha_publicacion &&
                  ` · publicar ${data.plan_editorial_hoy.fecha_publicacion}`}
              </p>
            )}
            {data.plan_editorial_hoy.copy_preview && (
              <p className="rounded-lg border border-[#e8efe5] bg-[#fafcf9] p-3 italic">
                {data.plan_editorial_hoy.copy_preview}
              </p>
            )}
            {(data.plan_editorial_hoy.pieza_id || data.campaña_activa?.pieza_hoy?.id) && (
              <Link
                to="/plan"
                className="inline-block text-sm font-semibold text-[#4a7c59] underline"
              >
                Abrí el plan y tocá la publicación de hoy para ver el guion
                completo →
              </Link>
            )}
          </CardContent>
        </Card>
      )}

      {data?.publicaciones_hoy && data.publicaciones_hoy.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Ya programado para hoy</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.publicaciones_hoy.map((p) => (
              <div
                key={p.id}
                className="rounded-xl border border-[#e8efe5] p-3 text-sm"
              >
                <p className="font-medium">{p.titulo || p.canal_label}</p>
                <p className="line-clamp-2 text-[#6b7f72]">{p.copy}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {preparar.isError && (
        <p className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800">
          {(preparar.error as Error).message}
        </p>
      )}

      {preparar.isSuccess && (
        <p className="mt-4 rounded-lg bg-[#e3efe0] px-4 py-3 text-sm text-[#2d5a3d]">
          Listo. Revisá en Publicaciones.
        </p>
      )}

      <button
        type="button"
        className="mt-6 text-sm text-[#6b7f72] underline"
        onClick={() => refetch()}
      >
        Actualizar pantalla
      </button>
    </>
  );
}
