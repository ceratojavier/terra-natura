import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { PiezaDetalleModal } from "@/components/pieza-detalle-modal";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface PubDia {
  pieza_id: string;
  hito_id: string;
  hito_nombre?: string;
  titulo?: string;
  ventana_label?: string;
  tipo_pieza_label?: string;
  canal: string;
  formato: string;
  canal_label?: string;
  formato_label?: string;
  color: string;
  desarrollado?: boolean;
}

interface BarraEvento {
  hito_id: string;
  nombre?: string;
  color: string;
  col_inicio: number;
  col_fin: number;
  span: number;
  carril: number;
  mostrar_etiqueta: boolean;
  continua_antes: boolean;
  continua_despues: boolean;
}

interface CeldaDia {
  fecha: string;
  dia: number;
  en_mes: boolean;
  es_hoy: boolean;
  publicaciones: PubDia[];
}

interface SemanaCalendario {
  dias: CeldaDia[];
  barras: BarraEvento[];
  filas_eventos: number;
}

interface CalendarioVisual {
  titulo: string;
  anio: number;
  mes: number;
  dias_semana: string[];
  semanas: SemanaCalendario[];
  leyenda: Array<{ tipo: string; etiqueta: string; color: string; fondo: string }>;
  total_publicaciones_mes: number;
}

const ALTURA_BARRA = 26;
const GAP_BARRA = 3;

function PubCard({
  pub,
  onClick,
}: {
  pub: PubDia;
  onClick: () => void;
}) {
  const esWa = pub.canal === "whatsapp";
  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      className={cn(
        "w-full rounded-md border px-2 py-1.5 text-left text-xs leading-snug transition hover:shadow-sm",
        esWa
          ? "border-[#25D366]/40 bg-[#ecfdf3] hover:border-[#25D366]"
          : "border-[#e1306c]/30 bg-[#fdf2f8] hover:border-[#e1306c]/60"
      )}
    >
      <div className="mb-0.5 flex flex-wrap items-center gap-1">
        <span
          className={cn(
            "rounded px-1 py-0.5 text-[10px] font-bold uppercase tracking-wide",
            esWa ? "bg-[#25D366] text-white" : "bg-gradient-to-r from-[#f58529] to-[#dd2a7b] text-white"
          )}
        >
          {pub.canal_label ?? (esWa ? "WhatsApp" : "Instagram")}
        </span>
        <span className="rounded bg-white/80 px-1 py-0.5 text-[10px] font-semibold text-[#4a5568]">
          {pub.formato_label ?? pub.formato}
        </span>
        {pub.desarrollado && (
          <span className="text-[10px] text-[#4a7c59]">✓ guion</span>
        )}
      </div>
      <p className="font-semibold text-[#1a2e24] line-clamp-3">{pub.titulo || "Sin título"}</p>
      <p className="mt-0.5 text-[10px] text-[#6b7f72]">
        {pub.tipo_pieza_label}
        {pub.ventana_label ? ` · ${pub.ventana_label}` : ""}
      </p>
    </button>
  );
}

function BarraFusionada({ barra }: { barra: BarraEvento }) {
  const redondeo = cn(
    !barra.continua_antes && "rounded-l-md",
    !barra.continua_despues && "rounded-r-md"
  );
  return (
    <div
      className={cn("flex h-full min-w-0 items-center overflow-hidden px-2", redondeo)}
      style={{
        gridColumn: `${barra.col_inicio + 1} / span ${barra.span}`,
        gridRow: barra.carril + 1,
        backgroundColor: barra.color,
      }}
      title={barra.nombre}
    >
      {barra.mostrar_etiqueta && (
        <span className="truncate text-xs font-semibold text-white drop-shadow-sm">
          {barra.nombre}
        </span>
      )}
    </div>
  );
}

export function MarketingMonthCalendar({ data }: { data: CalendarioVisual }) {
  const [piezaModal, setPiezaModal] = useState<{ hitoId: string; piezaId: string } | null>(
    null
  );

  return (
    <div className="w-full">
      {/* Leyenda compacta */}
      <div className="mb-3 flex flex-wrap gap-2">
        {data.leyenda.map((l) => (
          <span
            key={l.tipo}
            className="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium text-white"
            style={{ backgroundColor: l.color }}
          >
            {l.etiqueta}
          </span>
        ))}
      </div>

      <div className="overflow-x-auto rounded-xl border border-[#c5d4bc] bg-white shadow-sm">
        {/* Cabecera días */}
        <div className="grid min-w-[980px] grid-cols-7 border-b border-[#dce5d8] bg-[#eef4eb]">
          {data.dias_semana.map((d) => (
            <div
              key={d}
              className="border-r border-[#dce5d8] py-2 text-center text-xs font-bold uppercase tracking-wider text-[#4a6356] last:border-r-0"
            >
              {d}
            </div>
          ))}
        </div>

        {data.semanas.map((semana, wi) => {
          const filasEvento = Math.max(semana.filas_eventos, semana.barras.length > 0 ? 1 : 0);
          const altoBarras =
            filasEvento > 0 ? filasEvento * ALTURA_BARRA + (filasEvento - 1) * GAP_BARRA + 8 : 0;

          return (
            <div
              key={wi}
              className="min-w-[980px] border-b border-[#dce5d8] last:border-b-0"
            >
              {/* Barras tipo merge-cells (eventos multi-día) */}
              {filasEvento > 0 && (
                <div
                  className="grid grid-cols-7 gap-x-0 border-b border-[#e8efe5] bg-[#fafcf9] px-1 pt-1"
                  style={{
                    minHeight: altoBarras,
                    gridTemplateRows: `repeat(${filasEvento}, ${ALTURA_BARRA}px)`,
                    rowGap: GAP_BARRA,
                  }}
                >
                  {semana.barras.map((b) => (
                    <BarraFusionada key={`${b.hito_id}-${wi}-${b.carril}`} barra={b} />
                  ))}
                </div>
              )}

              {/* Días + publicaciones (lo principal) */}
              <div className="grid min-w-[980px] grid-cols-7">
                {semana.dias.map((celda) => (
                  <div
                    key={celda.fecha}
                    className={cn(
                      "flex min-h-[11rem] flex-col border-r border-[#e8efe5] p-1.5 last:border-r-0 md:min-h-[13rem]",
                      !celda.en_mes && "bg-[#f6f9f5] opacity-50",
                      celda.es_hoy && "bg-[#f0f7ed] ring-2 ring-inset ring-[#4a7c59]"
                    )}
                  >
                    <div className="mb-1.5 flex shrink-0 items-center justify-between">
                      <span
                        className={cn(
                          "inline-flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold",
                          celda.es_hoy
                            ? "bg-[#4a7c59] text-white"
                            : celda.en_mes
                              ? "text-[#2a4034]"
                              : "text-[#aab8ae]"
                        )}
                      >
                        {celda.dia}
                      </span>
                      {celda.publicaciones.length > 0 && (
                        <span className="rounded-full bg-[#4a7c59]/15 px-1.5 py-0.5 text-[10px] font-semibold text-[#2d5a3d]">
                          {celda.publicaciones.length}
                        </span>
                      )}
                    </div>

                    <div className="flex flex-1 flex-col gap-1.5 overflow-y-auto">
                      {celda.publicaciones.length === 0 ? (
                        celda.en_mes && (
                          <p className="text-[10px] italic text-[#aab8ae]">Sin publicaciones</p>
                        )
                      ) : (
                        celda.publicaciones.map((p) => (
                          <PubCard
                            key={p.pieza_id}
                            pub={p}
                            onClick={() =>
                              setPiezaModal({ hitoId: p.hito_id, piezaId: p.pieza_id })
                            }
                          />
                        ))
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <PiezaDetalleModal
        hitoId={piezaModal?.hitoId ?? null}
        piezaId={piezaModal?.piezaId ?? null}
        open={!!piezaModal}
        onOpenChange={(v) => !v && setPiezaModal(null)}
      />
    </div>
  );
}

export function CalendarioNav({
  titulo,
  totalPubs,
  onPrev,
  onNext,
  onHoy,
}: {
  titulo: string;
  totalPubs?: number;
  onPrev: () => void;
  onNext: () => void;
  onHoy: () => void;
}) {
  return (
    <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 className="text-xl font-bold text-[#2a4034] md:text-2xl">{titulo}</h2>
        <p className="text-sm text-[#6b7f72]">
          {totalPubs != null ? (
            <>
              <strong>{totalPubs}</strong> publicaciones este mes · barras = vacaciones/fines
              largos · tocá cada tarjeta para ver guion y copy
            </>
          ) : (
            "Cargando…"
          )}
        </p>
      </div>
      <div className="flex items-center gap-2">
        <Button type="button" variant="secondary" size="sm" onClick={onPrev}>
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <Button type="button" variant="secondary" size="sm" onClick={onHoy}>
          Hoy
        </Button>
        <Button type="button" variant="secondary" size="sm" onClick={onNext}>
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
