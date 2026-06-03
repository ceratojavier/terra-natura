import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-[hsl(217_91%_60%)]/15 text-[hsl(217_91%_75%)]",
        secondary:
          "border-[hsl(217_28%_22%)] bg-[hsl(217_28%_14%)] text-[hsl(215_18%_70%)]",
        success:
          "border-transparent bg-[#d4ead8] text-[#2d5a3d]",
        warning:
          "border-transparent bg-[#fce8d4] text-[#8a5a20]",
        outline: "text-[hsl(210_40%_90%)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export function Badge({
  className,
  variant,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof badgeVariants>) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
