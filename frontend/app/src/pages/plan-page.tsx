import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ChevronDown, ChevronRight, MapPin, CalendarDays } from "lucide-react";
import { api } from "@/api/client";
import { PiezaDetalleModal } from "@/components/pieza-detalle-modal";
import { PageIntro } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const MESES = [
  "Ene",
  "Feb",
  "Mar",
  "Abr",
  "May",
  "Jun",
  "Jul",
  "Ago",
  "Sep",
  "Oct",
  "Nov",
  "Dic",
];

interface PiezaResumen {
  id: string;
  titulo_publicacion?: string;
  fecha_legible?: string;
  ventana_label?: string;
  tipo_pieza_label?: string;
  estado?: string;
  desarrollado?: boolean;
  copy_instagram?: string;
}

interface Hito {
  id: string;
  nombre?: string;
  dias_hasta?: number;
  intensidad?: string;
  estrategia?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  distancia_km?: number | null;
  plan_accion?: {
    resumen?: string;
    fases?: Array<{ nombre: string; que_hacemos: string; piezas: string[] }>;
    calendario_publicaciones?: Array<{
      fecha: string;
      titulo?: string;
      tipo?: string;
      ventana?: string;
      canal?: string;
    }>;
    total_publicaciones?: number;
  };
  piezas?: PiezaResumen[];
}

interface PlanResponse {
  anio: number;
  filtro_eventos?: string;
  campaña_activa?: Hito;
  meses: Array<{
    mes: number;
    mes_label: string;
    clave: string;
    total_hitos: number;
    total_publicaciones: number;
    hitos: Hito[];
  }>;
  mes_actual?: {
    mes: number;
    mes_label: string;
    hitos: Hito[];
  };
}

export function PlanPage() {
  const hoy = new Date();
  const [anio, setAnio] = useState(hoy.getFullYear());
  const [mes, setMes] = useState(hoy.getMonth() + 1);
  const [vistaAnual, setVistaAnual] = useState(false);
  const [hitoAbierto, setHitoAbierto] = useState<string | null>(null);
  const [piezaModal, setPiezaModal] = useState<{
    hitoId: string;
    piezaId: string;
  } | null>(null);

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["plan-marketing", anio, mes, vistaAnual],
    queryFn: () =>
      api.get<PlanResponse>(
        vistaAnual
          ? `/api/ama/plan-marketing?anio=${anio}`
          : `/api/ama/plan-marketing?anio=${anio}&mes=${mes}`
      ),
  });

  const hitosMes = useMemo(() => {
    if (!data) return [];
    if (vistaAnual) {
      return data.meses.flatMap((m) => m.hitos);
    }
    return data.mes_actual?.hitos ?? data.meses.find((m) => m.mes === mes)?.hitos ?? [];
  }, [data, mes, vistaAnual]);

  const campaña = data?.campaña_activa;

  return (
    <>
      <PageIntro
        title="Plan de marketing"
        subtitle="Plan del año mes a mes: qué publicar y cuándo. Eventos lejos de Bialet (más de 60 km) no aparecen. Tocá cada publicación para ver texto y guion completo."
      />

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <span className="text-sm font-medium text-[#5c6f63]">Año</span>
        {[anio - 1, anio, anio + 1].filter((y) => y >= 2025 && y <= 2028).map((y) => (
          <Button
            key={y}
            size="sm"
            variant={y === anio ? "default" : "secondary"}
            onClick={() => setAnio(y)}
          >
            {y}
          </Button>
        ))}
        <Button
          size="sm"
          variant={vistaAnual ? "default" : "secondary"}
          className="ml-2"
          onClick={() => setVistaAnual(!vistaAnual)}
        >
          {vistaAnual ? "Ver un mes" : "Ver plan del año completo"}
        </Button>
        <Button size="sm" variant="ghost" onClick={() => refetch()} disabled={isFetching}>
          Actualizar
        </Button>
        <Button size="sm" variant="secondary" asChild className="ml-auto">
          <Link to="/calendario">
            <CalendarDays className="mr-1 h-4 w-4" />
            Vista calendario
          </Link>
        </Button>
      </div>

      {!vistaAnual && (
        <div className="mb-6 flex flex-wrap gap-1">
          {MESES.map((label, i) => {
            const m = i + 1;
            const total = data?.meses.find((x) => x.mes === m)?.total_hitos ?? 0;
            return (
              <button
                key={m}
                type="button"
                onClick={() => setMes(m)}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  mes === m
                    ? "bg-[#4a7c59] text-white"
                    : "bg-white text-[#5c6f63] hover:bg-[#e8efe5]"
                }`}
              >
                {label}
                {total > 0 && (
                  <span className="ml-1 opacity-80">({total})</span>
                )}
              </button>
            );
          })}
        </div>
      )}

      {data?.filtro_eventos && (
        <p className="mb-4 flex items-center gap-1 text-xs text-[#6b7f72]">
          <MapPin className="h-3 w-3" />
          {data.filtro_eventos}
        </p>
      )}

      {isLoading && <Skeleton className="h-64 w-full rounded-2xl" />}

      {campaña && !vistaAnual && (
        <Card className="mb-6 border-2 border-[#4a7c59]">
          <CardHeader>
            <CardTitle>Campaña prioritaria ahora</CardTitle>
          </CardHeader>
          <CardContent>
            <HitoDetalle
              hito={campaña}
              abierto
              onToggle={() => {}}
              onPiezaClick={(piezaId) =>
                setPiezaModal({ hitoId: campaña.id, piezaId })
              }
            />
          </CardContent>
        </Card>
      )}

      {vistaAnual && data?.meses && (
        <div className="mb-6 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {data.meses.map((m) => (
            <button
              key={m.clave}
              type="button"
              className="rounded-xl border border-[#dce5d8] bg-white p-4 text-left hover:border-[#4a7c59]"
              onClick={() => {
                setVistaAnual(false);
                setMes(m.mes);
              }}
            >
              <p className="font-semibold text-[#2a4034]">{m.mes_label}</p>
              <p className="text-sm text-[#6b7f72]">
                {m.total_hitos} campañas · {m.total_publicaciones} publicaciones
                planificadas
              </p>
            </button>
          ))}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>
            {vistaAnual
              ? `Todo ${anio} (${hitosMes.length} campañas)`
              : `${data?.mes_actual?.mes_label ?? MESES[mes - 1]} ${anio}`}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {hitosMes.length === 0 && (
            <p className="text-sm text-[#6b7f72]">
              No hay hitos en este período (o fueron filtrados por distancia).
            </p>
          )}
          {hitosMes.map((h) => (
            <HitoDetalle
              key={h.id}
              hito={h}
              abierto={hitoAbierto === h.id}
              onToggle={() =>
                setHitoAbierto(hitoAbierto === h.id ? null : h.id)
              }
              onPiezaClick={(piezaId) =>
                setPiezaModal({ hitoId: h.id, piezaId })
              }
            />
          ))}
        </CardContent>
      </Card>

      <PiezaDetalleModal
        hitoId={piezaModal?.hitoId ?? null}
        piezaId={piezaModal?.piezaId ?? null}
        open={!!piezaModal}
        onOpenChange={(v) => !v && setPiezaModal(null)}
      />
    </>
  );
}

function HitoDetalle({
  hito,
  abierto,
  onToggle,
  onPiezaClick,
}: {
  hito: Hito;
  abierto: boolean;
  onToggle: () => void;
  onPiezaClick: (piezaId: string) => void;
}) {
  const pa = hito.plan_accion;

  return (
    <div className="rounded-xl border border-[#e8efe5] bg-[#fafcf9]">
      <button
        type="button"
        className="flex w-full items-center gap-2 px-4 py-3 text-left"
        onClick={onToggle}
      >
        {abierto ? (
          <ChevronDown className="h-4 w-4 shrink-0" />
        ) : (
          <ChevronRight className="h-4 w-4 shrink-0" />
        )}
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-[#2a4034]">{hito.nombre}</p>
          <p className="text-xs text-[#6b7f72]">
            {hito.fecha_inicio}
            {hito.fecha_fin && hito.fecha_fin !== hito.fecha_inicio
              ? ` → ${hito.fecha_fin}`
              : ""}
            {hito.dias_hasta != null && ` · en ${hito.dias_hasta} días`}
            {hito.distancia_km != null && ` · ${hito.distancia_km} km`}
          </p>
        </div>
        <Badge variant={hito.intensidad === "alta" ? "default" : "secondary"}>
          {pa?.total_publicaciones ?? hito.piezas?.length ?? 0} posts
        </Badge>
      </button>

      {abierto && (
        <div className="border-t border-[#e8efe5] px-4 pb-4 pt-3 text-sm">
          <p className="mb-3 text-[#5c6f63]">{hito.estrategia}</p>
          {pa?.resumen && (
            <p className="mb-3 rounded-lg bg-[#eef6eb] p-3 font-medium text-[#2d5a3d]">
              {pa.resumen}
            </p>
          )}

          {pa?.fases && pa.fases.length > 0 && (
            <div className="mb-4">
              <p className="mb-2 text-xs font-bold uppercase text-[#7a8f80]">
                Plan de acción por fases
              </p>
              {pa.fases.map((f) => (
                <div key={f.nombre} className="mb-2 rounded-lg bg-white p-3">
                  <p className="font-semibold text-[#2a4034]">{f.nombre}</p>
                  <p className="text-[#5c6f63]">{f.que_hacemos}</p>
                  {f.piezas.length > 0 && (
                    <p className="mt-1 text-xs text-[#6b7f72]">
                      Fechas: {f.piezas.join(", ")}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}

          <p className="mb-2 text-xs font-bold uppercase text-[#7a8f80]">
            Qué vas a publicar (tocá para ver guion y texto)
          </p>
          <ul className="space-y-2">
            {(hito.piezas ?? [])
              .filter((p) => p.estado !== "pasada")
              .map((p) => (
                <li key={p.id}>
                  <button
                    type="button"
                    className="w-full rounded-lg border border-[#dce5d8] bg-white px-3 py-2 text-left hover:border-[#4a7c59] hover:bg-[#f4f8f2]"
                    onClick={() => onPiezaClick(p.id)}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-medium text-[#2a4034]">
                        {p.fecha_legible}
                      </span>
                      <Badge
                        variant={
                          p.estado === "hoy"
                            ? "default"
                            : p.estado === "proxima"
                              ? "warning"
                              : "secondary"
                        }
                      >
                        {p.ventana_label}
                      </Badge>
                      {!p.desarrollado && (
                        <span className="text-xs text-[#8a5a20]">
                          (se carga al abrir)
                        </span>
                      )}
                    </div>
                    <p className="mt-1 font-semibold text-[#3d5345]">
                      {p.titulo_publicacion}
                    </p>
                    <p className="text-xs text-[#6b7f72]">
                      {p.tipo_pieza_label} · Instagram reel
                    </p>
                    {p.copy_instagram && (
                      <p className="mt-1 line-clamp-2 text-xs italic text-[#5c6f63]">
                        {p.copy_instagram}
                      </p>
                    )}
                  </button>
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
}
