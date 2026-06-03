export interface ProgramaEstado {
  nombre: string;
  herramientas: { python: boolean; ffmpeg: boolean; yt_dlp: boolean };
  youtube_biblioteca: number;
  cola_pendientes: number;
  calendario: { total: number; pendientes: number; hoy: number };
  mensaje: string;
}

export interface AmaDashboard {
  modo_publicacion: string;
  total_calendario: number;
  pendientes_aprobacion: number;
  publicaciones_hoy: number;
  mensaje: string;
  hoy_detalle?: {
    fecha?: string;
    publicaciones?: Array<{
      canal?: string;
      tipo?: string;
      copy?: string;
      estado?: string;
    }>;
  };
}

export interface PublishItem {
  id: string;
  fecha?: string;
  canal?: string;
  estado?: string;
  copy?: string;
  video_ruta?: string;
  meta?: Record<string, unknown>;
}

export interface AgentMeta {
  id: string;
  nombre: string;
  descripcion: string;
  icono?: string;
  tareas: Array<{ id: string; titulo: string; automatico: boolean }>;
}

export interface AgentsHub {
  agentes: AgentMeta[];
  ultimo_ciclo: Record<string, unknown> | null;
  leads_total: number;
  reservas_activas: number;
  cola_pendientes: number;
  cola_aprobados: number;
  mensaje: string;
}

export interface PipelineResult {
  ok?: boolean;
  fecha?: string;
  carpeta_salida?: string;
  plan?: Record<string, unknown>;
  guion?: Record<string, unknown>;
  video?: { ruta?: string; ok?: boolean };
  cola?: unknown;
  error?: string;
}

export interface EstrategaPlan {
  fecha?: string;
  angulo?: string;
  unidad_sugerida?: string[];
  eventos?: Array<{ nombre?: string; fecha?: string }>;
  copy_angle?: string;
  demanda?: Record<string, unknown>;
}

export interface DirectorPlanMes {
  mes?: string;
  titulo?: string;
  focos?: string[];
  semanas?: Array<Record<string, unknown>>;
}
