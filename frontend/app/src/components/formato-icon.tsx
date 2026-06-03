import { Film, Images, MessageCircle, Smartphone } from "lucide-react";
import { cn } from "@/lib/utils";

const SIZE = {
  sm: "h-3.5 w-3.5",
  md: "h-4 w-4",
} as const;

export function FormatoIcon({
  canal,
  formato,
  size = "sm",
}: {
  canal: string;
  formato: string;
  size?: keyof typeof SIZE;
}) {
  const cls = SIZE[size];
  if (canal === "whatsapp") {
    return (
      <span className="inline-flex items-center gap-0.5 rounded bg-[#25D366]/15 px-1 py-0.5 text-[#128C7E]" title="WhatsApp Status">
        <MessageCircle className={cls} />
      </span>
    );
  }
  if (formato === "carousel") {
    return (
      <span className="inline-flex items-center gap-0.5 rounded bg-[#E1306C]/10 px-1 py-0.5 text-[#C13584]" title="Instagram carrusel">
        <Images className={cls} />
      </span>
    );
  }
  if (formato === "reel") {
    return (
      <span className="inline-flex items-center gap-0.5 rounded bg-[#E1306C]/10 px-1 py-0.5 text-[#C13584]" title="Instagram reel">
        <Film className={cls} />
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-0.5 rounded bg-[#E1306C]/10 px-1 py-0.5 text-[#C13584]" title="Instagram post">
      <Smartphone className={cls} />
    </span>
  );
}

export function InstagramBadge({ size = "sm" }: { size?: keyof typeof SIZE }) {
  return (
    <span
      className={cn(
        "inline-flex items-center justify-center rounded-md bg-gradient-to-br from-[#f58529] via-[#dd2a7b] to-[#8134af] font-bold text-white",
        size === "md" ? "h-6 w-6 text-[10px]" : "h-5 w-5 text-[9px]"
      )}
      title="Instagram"
    >
      IG
    </span>
  );
}
