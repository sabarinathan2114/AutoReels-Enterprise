import React from "react";
import { ChevronDown } from "lucide-react";

interface FormLabelProps {
  children: React.ReactNode;
  hint?: React.ReactNode;
  className?: string;
}

export function CosmicLabel({ children, hint, className = "" }: FormLabelProps) {
  return (
    <div className={`flex items-center justify-between text-xs font-medium text-purple-300 mb-1 ${className}`}>
      <span className="truncate">{children}</span>
      {hint && <span className="text-[10px] text-purple-400/80 flex-shrink-0 ml-2">{hint}</span>}
    </div>
  );
}

interface CosmicSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  hint?: React.ReactNode;
}

export function CosmicSelect({ label, hint, children, className = "", ...props }: CosmicSelectProps) {
  return (
    <div className="w-full">
      {label && <CosmicLabel hint={hint}>{label}</CosmicLabel>}
      <div className="relative w-full">
        <select
          className={`w-full glass-panel text-xs p-2.5 rounded-xl border border-purple-500/30 text-white focus:outline-none focus:border-purple-400 cursor-pointer appearance-none pr-8 truncate ${className}`}
          {...props}
        >
          {children}
        </select>
        <ChevronDown className="w-3.5 h-3.5 text-purple-400 absolute right-2.5 top-3 pointer-events-none" />
      </div>
    </div>
  );
}

interface CosmicTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: React.ReactNode;
}

export function CosmicTextarea({ label, hint, className = "", ...props }: CosmicTextareaProps) {
  return (
    <div className="w-full">
      {label && <CosmicLabel hint={hint}>{label}</CosmicLabel>}
      <textarea
        className={`w-full glass-panel text-xs p-3 rounded-xl border border-purple-500/30 text-white focus:outline-none focus:border-purple-400 resize-none leading-relaxed placeholder:text-purple-400/40 ${className}`}
        {...props}
      />
    </div>
  );
}
