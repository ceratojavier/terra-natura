import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

export function ActionCard({
  title,
  explanation,
  onClick,
  loading,
  variant = "default",
}: {
  title: string;
  explanation: string;
  onClick?: () => void;
  loading?: boolean;
  variant?: "default" | "secondary";
}) {
  return (
    <Button
      type="button"
      size="block"
      variant={variant === "secondary" ? "secondary" : "default"}
      disabled={loading}
      onClick={onClick}
      className="mb-3"
    >
      <span className="flex w-full items-center gap-2">
        {loading && <Loader2 className="h-4 w-4 shrink-0 animate-spin" />}
        <span className="text-base font-semibold">{title}</span>
      </span>
      <span className="w-full text-sm font-normal opacity-90">{explanation}</span>
    </Button>
  );
}
