import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { PageIntro } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface Pub {
  id: string;
  pub_id?: string;
  canal?: string;
  copy_preview?: string;
  copy?: string;
  video_ruta?: string;
  estado?: string;
}

export function PublicacionesPage() {
  const qc = useQueryClient();

  const cal = useQuery({
    queryKey: ["publicaciones"],
    queryFn: () =>
      api.get<{ publicaciones: Pub[] }>(
        "/api/ama/calendario?estado=pendiente_aprobacion"
      ),
  });

  const cola = useQuery({
    queryKey: ["cola"],
    queryFn: () => api.get<{ items: Pub[] }>("/api/ama/publish/cola"),
  });

  const aprobar = useMutation({
    mutationFn: (id: string) => api.post(`/api/ama/publish/aprobar/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["publicaciones"] }),
  });

  const publicar = useMutation({
    mutationFn: (id: string) => api.post(`/api/ama/publicar/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["publicaciones"] });
      qc.invalidateQueries({ queryKey: ["hoy"] });
    },
  });

  const items = [
    ...(cal.data?.publicaciones ?? []),
    ...(cola.data?.items ?? []).filter(
      (c) => !cal.data?.publicaciones?.some((p) => p.id === c.pub_id)
    ),
  ];

  const unique = Array.from(
    new Map(items.map((p) => [p.id || p.pub_id, p])).values()
  );

  return (
    <>
      <PageIntro
        title="Publicaciones"
        subtitle="Revisá el texto y el video. Aprobá y, si Instagram está conectado, podés subir desde acá."
      />

      {cal.isLoading && <Skeleton className="h-40 w-full rounded-2xl" />}

      {unique.length === 0 && !cal.isLoading && (
        <Card>
          <CardContent className="py-8 text-center text-[#5c6f63]">
            No hay nada pendiente. Volvé a <strong>Hoy</strong> y tocá
            &quot;Preparar publicación de hoy&quot;.
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {unique.map((p) => {
          const id = p.id || p.pub_id || "";
          const texto = p.copy || p.copy_preview || "";
          return (
            <Card key={id}>
              <CardHeader>
                <CardTitle className="text-base">
                  {p.canal === "instagram" ? "Instagram" : p.canal || "Red"}
                  {p.video_ruta ? " · con video" : " · solo texto"}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="whitespace-pre-wrap text-sm text-[#3d5345]">
                  {texto}
                </p>
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    disabled={aprobar.isPending}
                    onClick={() => aprobar.mutate(id)}
                  >
                    Marcar como aprobado
                  </Button>
                  <Button
                    size="sm"
                    disabled={publicar.isPending}
                    onClick={() => publicar.mutate(id)}
                  >
                    Subir a Instagram
                  </Button>
                </div>
                {publicar.isSuccess && publicar.variables === id && (
                  <p className="text-sm text-[#4a7c59]">
                    Pedido enviado. Si Instagram no está conectado, te indico cómo
                    copiar manualmente.
                  </p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {(publicar.data as { mensaje_dueno?: string })?.mensaje_dueno && (
        <p className="mt-4 rounded-xl bg-[#f4f8f2] p-4 text-sm">
          {(publicar.data as { mensaje_dueno: string }).mensaje_dueno}
        </p>
      )}
    </>
  );
}
