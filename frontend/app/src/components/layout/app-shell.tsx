import { NavLink, Outlet } from "react-router-dom";
import {
  CalendarDays,
  CalendarRange,
  CalendarPlus,
  Film,
  Home,
  MessageCircle,
  Mountain,
  Send,
  Settings,
  Camera,
  Radar,
} from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  {
    to: "/hoy",
    label: "Hoy",
    hint: "Qué mirar y preparar",
    icon: Home,
  },
  {
    to: "/plan",
    label: "Plan de marketing",
    hint: "Feriados y campañas",
    icon: CalendarRange,
  },
  {
    to: "/calendario",
    label: "Calendario",
    hint: "Mes completo visual",
    icon: CalendarDays,
  },
  {
    to: "/publicaciones",
    label: "Publicaciones",
    hint: "Revisar y subir a Instagram",
    icon: Send,
  },
  {
    to: "/radar-eventos",
    label: "Radar eventos",
    hint: "Novedades y avisos tuyos",
    icon: Radar,
  },
  {
    to: "/instagram-perfil",
    label: "Perfil Instagram",
    hint: "Bio, destacadas y plan de feed",
    icon: Camera,
  },
  {
    to: "/configuracion",
    label: "Configuración",
    hint: "Instagram y opciones avanzadas",
    icon: Settings,
  },
] as const;

export function AppShell() {
  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="border-b border-[#dce5d8] bg-white/80 md:w-64 md:border-b-0 md:border-r">
        <div className="flex items-center gap-3 px-5 py-5">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#4a7c59] text-white shadow-md">
            <Mountain className="h-6 w-6" />
          </div>
          <div>
            <p className="font-semibold text-[#2a4034]">Terra Natura</p>
            <p className="text-xs text-[#6b7f72]">Bialet Massé · sierras</p>
          </div>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3 md:flex-col md:overflow-visible md:px-3 md:pb-6">
          {nav.map(({ to, label, hint, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  "min-w-[7rem] shrink-0 rounded-xl px-3 py-2.5 transition-colors md:min-w-0",
                  isActive
                    ? "bg-[#e3efe0] text-[#2d5a3d]"
                    : "text-[#5c6f63] hover:bg-[#f0f5ee]"
                )
              }
            >
              <div className="flex items-center gap-2">
                <Icon className="h-4 w-4 shrink-0" />
                <span className="text-sm font-semibold">{label}</span>
              </div>
              <p className="mt-0.5 hidden text-xs text-[#7a8f80] md:block">{hint}</p>
            </NavLink>
          ))}
          <a
            href="/video-pro/"
            target="_blank"
            rel="noopener noreferrer"
            className="min-w-[7rem] shrink-0 rounded-xl px-3 py-2.5 text-[#5c6f63] transition-colors hover:bg-[#f0f5ee] md:min-w-0"
          >
            <div className="flex items-center gap-2">
              <Film className="h-4 w-4 shrink-0" />
              <span className="text-sm font-semibold">Video Pro</span>
            </div>
            <p className="mt-0.5 hidden text-xs text-[#7a8f80] md:block">
              Crear vídeo con IA
            </p>
          </a>
          <div className="my-2 hidden border-t border-[#e8efe5] md:block" />
          <p className="hidden px-3 text-[10px] font-semibold uppercase tracking-wide text-[#9aab9e] md:block">
            Operación (móvil)
          </p>
          <a
            href="/panel.html#/nueva-reserva"
            target="_blank"
            rel="noopener noreferrer"
            className="min-w-[7rem] shrink-0 rounded-xl px-3 py-2.5 text-[#2d5a3d] transition-colors hover:bg-[#e3efe0] md:min-w-0"
          >
            <div className="flex items-center gap-2">
              <CalendarPlus className="h-4 w-4 shrink-0" />
              <span className="text-sm font-semibold">Nueva reserva</span>
            </div>
            <p className="mt-0.5 hidden text-xs text-[#7a8f80] md:block">
              Panel PMS en el celular
            </p>
          </a>
          <a
            href="/panel.html#/calendario"
            target="_blank"
            rel="noopener noreferrer"
            className="min-w-[7rem] shrink-0 rounded-xl px-3 py-2.5 text-[#5c6f63] transition-colors hover:bg-[#f0f5ee] md:min-w-0"
          >
            <div className="flex items-center gap-2">
              <CalendarDays className="h-4 w-4 shrink-0" />
              <span className="text-sm font-semibold">Calendario PMS</span>
            </div>
            <p className="mt-0.5 hidden text-xs text-[#7a8f80] md:block">
              Ocupación y Booking
            </p>
          </a>
          <a
            href="https://wa.me/5493541571190"
            target="_blank"
            rel="noopener noreferrer"
            className="min-w-[7rem] shrink-0 rounded-xl px-3 py-2.5 text-[#5c6f63] transition-colors hover:bg-[#f0f5ee] md:min-w-0"
          >
            <div className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4 shrink-0" />
              <span className="text-sm font-semibold">WhatsApp</span>
            </div>
            <p className="mt-0.5 hidden text-xs text-[#7a8f80] md:block">
              Consultas y cierre
            </p>
          </a>
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <main className="flex-1 p-4 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export function PageIntro({
  title,
  subtitle,
}: {
  title: string;
  subtitle?: string;
}) {
  return (
    <header className="mb-6">
      <h1 className="text-2xl font-bold tracking-tight text-[#2a4034] md:text-3xl">
        {title}
      </h1>
      {subtitle && (
        <p className="mt-2 max-w-2xl text-base text-[#5c6f63]">{subtitle}</p>
      )}
    </header>
  );
}
