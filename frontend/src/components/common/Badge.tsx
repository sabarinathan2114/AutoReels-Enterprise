import React from "react";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "purple" | "emerald" | "yellow" | "red" | "dark";
  className?: string;
}

export function Badge({ children, variant = "purple", className = "" }: BadgeProps) {
  const variantStyles = {
    purple: "bg-purple-950/60 border-purple-500/30 text-purple-200",
    emerald: "bg-emerald-950/60 border-emerald-500/40 text-emerald-300",
    yellow: "bg-yellow-950/60 border-yellow-500/40 text-yellow-300",
    red: "bg-red-950/60 border-red-500/40 text-red-300",
    dark: "bg-black/60 border-purple-500/20 text-purple-300/80"
  };

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] sm:text-xs font-medium border font-mono tracking-tight ${
        variantStyles[variant]
      } ${className}`}
    >
      {children}
    </span>
  );
}
