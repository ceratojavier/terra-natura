import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import {
  CalendarioNav,
  MarketingMonthCalendar,
} from "@/components/marketing-month-calendar";
import { Skeleton } from "@/components/ui/skeleton";

export function CalendarioPage() {
  const hoy = new Date();
  const [anio, setAnio] = useState(hoy.getFullYear());
  const [mes, setMes] = useState(hoy.getMonth() + 1);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["calendario-visual", anio, mes],
    queryFn: () =>
      api.get<{
        titulo: string;
        anio: number;
        mes: number;
        total_publicaciones_mes: number;
      }>(`/api/ama/calendario-visual?anio=${anio}&mes=${mes}`),
  });

  const irMes = (delta: number) => {
    let m = mes + delta;
    let a = anio;
    if (m < 1) {
      m = 12;
      a -= 1;
    }
    if (m > 12) {
      m = 1;
      a += 1;
    }
    setMes(m);
    setAnio(a);
  };

  const titulo = useMemo(
    () => data?.titulo ?? `${mes}/${anio}`,
    [data?.titulo, mes, anio]
  );

  return (
    <div className="-mx-4 w-[calc(100%+2rem)] md:-mx-8 md:w-[calc(100%+4rem)]">
      <CalendarioNav
        titulo={titulo}
        totalPubs={data?.total_publicaciones_mes}
        onPrev={() => irMes(-1)}
        onNext={() => irMes(1)}
        onHoy={() => {
          setAnio(hoy.getFullYear());
          setMes(hoy.getMonth() + 1);
        }}
      />

      {isLoading && <Skeleton className="h-[36rem] w-full rounded-xl" />}

      {isError && (
        <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-800">
          No se pudo cargar el calendario. ¿Está encendido el servidor?
        </p>
      )}

      {data && <MarketingMonthCalendar data={data as never} />}
    </div>
  );
}
