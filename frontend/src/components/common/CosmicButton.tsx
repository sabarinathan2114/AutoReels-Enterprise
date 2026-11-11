import React from "react";
import { RefreshCw } from "lucide-react";

interface CosmicButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export function CosmicButton({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  icon,
  className = "",
  disabled,
  ...props
}: CosmicButtonProps) {
  const sizeClasses = {
    sm: "px-2.5 py-1.5 text-xs",
    md: "px-3.5 py-2 text-xs sm:text-sm",
    lg: "px-5 py-3 text-sm sm:text-base font-semibold"
  };

  const variantClasses = {
    primary: "btn-cosmic text-white font-semibold",
    secondary: "bg-purple-900/50 hover:bg-purple-800/60 text-purple-200 border border-purple-500/30",
    outline: "glass-panel hover:bg-purple-900/40 text-purple-200 border border-purple-500/40",
    danger: "bg-red-950/60 hover:bg-red-900/60 text-red-200 border border-red-500/40"
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={`rounded-xl flex items-center justify-center gap-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed select-none active:scale-[0.98] ${
        sizeClasses[size]
      } ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {isLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin flex-shrink-0" /> : icon}
      <span className="truncate">{children}</span>
    </button>
  );
}
