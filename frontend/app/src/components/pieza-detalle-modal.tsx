import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { api } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  GuionProduccionPanel,
  type GuionProduccion,
} from "@/components/guion-produccion-panel";

export interface PiezaDetalle {
  id: string;
  titulo_publicacion?: string;
  fecha_legible?: string;
  ventana_label?: string;
  tipo_pieza_label?: string;
  canal?: string;
  formato?: string;
  copy_instagram?: string;
  hashtags?: string[];
  brief_prompt?: string;
  brief_creativo?: string;
  guion?: {
    hook?: string;
    voz_off?: string;
    duracion_total_seg?: number;
    escenas?: Array<{
      numero: number;
      tipo?: string;
      duracion_seg?: number;
      texto_pantalla?: string;
      notas?: string;
    }>;
    checklist?: string[];
  };
  desarrollado?: boolean;
  guion_produccion?: GuionProduccion;
  prompt_video_pro?: string;
}

export function PiezaDetalleModal({
  hitoId,
  piezaId,
  open,
  onOpenChange,
}: {
  hitoId: string | null;
  piezaId: string | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  const qc = useQueryClient();
  const nav = useNavigate();

  const enviarPub = useMutation({
    mutationFn: () =>
      api.post<{ ok: boolean; mensaje?: string }>(
        "/api/ama/pieza/enviar-publicaciones",
        { hito_id: hitoId, pieza_id: piezaId }
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["publicaciones"] });
      onOpenChange(false);
      nav("/publicaciones");
    },
  });

  const { data, isLoading } = useQuery({
    queryKey: ["pieza", hitoId, piezaId],
    queryFn: () =>
      api.get<PiezaDetalle>(
        `/api/ama/plan-marketing/pieza/${encodeURIComponent(hitoId!)}/${encodeURIComponent(piezaId!)}`
      ),
    enabled: open && !!hitoId && !!piezaId,
  });

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/40" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-[min(640px,94vw)] -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-2xl border border-[#dce5d8] bg-white p-6 shadow-xl">
          <div className="mb-4 flex items-start justify-between gap-4">
            <div>
              <Dialog.Title className="text-lg font-bold text-[#2a4034]">
                {data?.titulo_publicacion || "Publicación"}
              </Dialog.Title>
              <Dialog.Description className="text-sm text-[#6b7f72]">
                {data?.fecha_legible} · {data?.ventana_label} · {data?.tipo_pieza_label}
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <button
                type="button"
                className="rounded-lg p-1 hover:bg-[#f0f4ee]"
                aria-label="Cerrar"
              >
                <X className="h-5 w-5" />
              </button>
            </Dialog.Close>
          </div>

          {isLoading && <Skeleton className="h-48 w-full" />}

          {data && (
            <div className="space-y-5 text-sm">
              <section>
                <h4 className="mb-2 font-semibold text-[#4a7c59]">
                  Texto para Instagram
                </h4>
                <pre className="whitespace-pre-wrap rounded-xl bg-[#f4f8f2] p-4 font-sans text-[#2a4034]">
                  {data.copy_instagram}
                </pre>
                {data.hashtags && data.hashtags.length > 0 && (
                  <p className="mt-2 text-xs text-[#6b7f72]">
                    {data.hashtags.join(" ")}
                  </p>
                )}
              </section>

              {data.guion && (
                <section>
                  <h4 className="mb-2 font-semibold text-[#4a7c59]">Guion del reel</h4>
                  <p className="mb-1">
                    <strong>Gancho:</strong> {data.guion.hook}
                  </p>
                  <p className="mb-3 text-[#5c6f63]">
                    <strong>Voz en off:</strong> {data.guion.voz_off}
                  </p>
                  <p className="mb-2 text-xs font-semibold uppercase text-[#7a8f80]">
                    Escenas ({data.guion.duracion_total_seg}s total)
                  </p>
                  <ol className="space-y-2">
                    {(data.guion.escenas ?? []).map((e) => (
                      <li
                        key={e.numero}
                        className="rounded-lg border border-[#e8efe5] px-3 py-2"
                      >
                        <span className="font-medium">
                          {e.numero}. [{e.tipo}] {e.duracion_seg}s
                        </span>
                        <p className="text-[#3d5345]">{e.texto_pantalla}</p>
                        {e.notas && (
                          <p className="text-xs text-[#6b7f72]">{e.notas}</p>
                        )}
                      </li>
                    ))}
                  </ol>
                </section>
              )}

              {data.brief_prompt && (
                <section>
                  <h4 className="mb-2 font-semibold text-[#4a7c59]">
                    Brief completo (para revisar / CapCut)
                  </h4>
                  <pre className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded-xl bg-[#faf8f4] p-4 text-xs text-[#3d5345]">
                    {data.brief_prompt}
                  </pre>
                </section>
              )}

              {hitoId && piezaId && (
                <GuionProduccionPanel
                  hitoId={hitoId}
                  piezaId={piezaId}
                  initial={data.guion_produccion}
                  formato={data.formato}
                />
              )}
            </div>
          )}

          <div className="mt-6 flex flex-wrap justify-end gap-2">
            {hitoId && piezaId && (
              <Button
                variant="default"
                disabled={enviarPub.isPending}
                onClick={() => enviarPub.mutate()}
              >
                {enviarPub.isPending
                  ? "Enviando…"
                  : "Enviar a publicaciones"}
              </Button>
            )}
            <Dialog.Close asChild>
              <Button variant="secondary">Cerrar</Button>
            </Dialog.Close>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
