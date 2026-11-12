"use client";

import React from "react";
import { Film, ShieldCheck } from "lucide-react";

interface FooterProps {
  onNavigate: (view: "landing" | "studio" | "dashboard" | "plans") => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer className="w-full border-t border-purple-900/30 bg-black/60 backdrop-blur-md py-10 px-3 sm:px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left">
        {/* Brand & Mission */}
        <div className="flex flex-col items-center md:items-start gap-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center shadow-md shadow-purple-600/30">
              <Film className="w-4 h-4 text-white" />
            </div>
            <span className="font-extrabold text-white tracking-wider text-base">
              AUTOREELS <span className="text-purple-400 font-light">ENTERPRISE</span>
            </span>
          </div>
          <p className="text-xs text-slate-400 max-w-sm">
            Autonomous vertical video generation engine. Master Build Specification v2.0 (Free-First Architecture).
          </p>
          <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium mt-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <span>Operational on MySQL 8.0+ & FFmpeg</span>
          </div>
        </div>

        {/* Quick Navigation Links */}
        <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-slate-300 font-medium">
          <button
            type="button"
            onClick={() => onNavigate("landing")}
            className="hover:text-purple-400 transition-colors"
          >
            Overview
          </button>
          <button
            type="button"
            onClick={() => onNavigate("studio")}
            className="hover:text-purple-400 transition-colors"
          >
            Studio Creator
          </button>
          <button
            type="button"
            onClick={() => onNavigate("dashboard")}
            className="hover:text-purple-400 transition-colors"
          >
            Accounts & Stats
          </button>
          <button
            type="button"
            onClick={() => onNavigate("plans")}
            className="hover:text-purple-400 transition-colors"
          >
            Compare Plans
          </button>
        </div>

        {/* Copyright & Compliance */}
        <div className="flex flex-col items-center md:items-end gap-1 text-[11px] text-slate-500">
          <p>© 2026 AutoReels Enterprise Inc. All rights reserved.</p>
          <div className="flex items-center gap-3">
            <span className="hover:text-slate-400 cursor-pointer">Terms of Service</span>
            <span>•</span>
            <span className="hover:text-slate-400 cursor-pointer">Privacy Policy</span>
            <span>•</span>
            <span className="flex items-center gap-1 text-purple-400">
              <ShieldCheck className="w-3 h-3" /> Zero Paid API
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
