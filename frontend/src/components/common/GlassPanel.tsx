import React from "react";

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}

export function GlassPanel({ children, className = "", glow = false }: GlassPanelProps) {
  return (
    <div
      className={`rounded-2xl transition-all duration-300 w-full max-w-full overflow-hidden ${
        glow ? "glass-panel-glow" : "glass-panel"
      } ${className}`}
    >
      {children}
    </div>
  );
}
