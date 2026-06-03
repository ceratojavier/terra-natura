import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/layout/app-shell";
import { CalendarioPage } from "@/pages/calendario-page";
import { ConfigPage } from "@/pages/config-page";
import { HoyPage } from "@/pages/hoy-page";
import { PlanPage } from "@/pages/plan-page";
import { PublicacionesPage } from "@/pages/publicaciones-page";
import { InstagramPerfilPage } from "@/pages/instagram-perfil-page";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename="/app">
        <Routes>
          <Route element={<AppShell />}>
            <Route index element={<Navigate to="/hoy" replace />} />
            <Route path="hoy" element={<HoyPage />} />
            <Route path="plan" element={<PlanPage />} />
            <Route path="calendario" element={<CalendarioPage />} />
            <Route path="publicaciones" element={<PublicacionesPage />} />
            <Route path="instagram-perfil" element={<InstagramPerfilPage />} />
            <Route path="configuracion" element={<ConfigPage />} />
            {/* Rutas viejas → nuevas */}
            <Route path="programa" element={<Navigate to="/hoy" replace />} />
            <Route path="marketing" element={<Navigate to="/plan" replace />} />
            <Route path="agentes" element={<Navigate to="/configuracion" replace />} />
          </Route>
          <Route path="*" element={<Navigate to="/hoy" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
