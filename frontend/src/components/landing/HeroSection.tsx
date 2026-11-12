"use client";

import React from "react";
import { Sparkles, ArrowRight, Play, CheckCircle, ShieldCheck } from "lucide-react";
import { CosmicButton } from "@/components/common/CosmicButton";
import { Badge } from "@/components/common/Badge";
import { LANDING_HERO_DATA } from "@/components/hardcodedata";

interface HeroSectionProps {
  onStartFree: () => void;
  onViewPlans: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  onStartFree,
  onViewPlans
}) => {
  return (
    <section className="relative pt-6 pb-16 md:pt-12 md:pb-24 overflow-hidden w-full">
      {/* Background Cosmic Violet Glow Orb */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] sm:w-[500px] h-[300px] sm:h-[500px] bg-purple-600/15 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-3 sm:px-6 flex flex-col lg:flex-row items-center gap-10 lg:gap-14">
        {/* Left: Value Proposition */}
        <div className="flex-1 text-center lg:text-left space-y-6 w-full">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-950/60 border border-purple-500/30 text-purple-300 text-xs sm:text-sm font-medium backdrop-blur-md">
            <Sparkles className="w-4 h-4 text-purple-400 animate-pulse" />
            <span>{LANDING_HERO_DATA.badge}</span>
          </div>

          <h1 className="text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-[1.15]">
            {LANDING_HERO_DATA.headlinePrefix}{" "}
            <span className="bg-gradient-to-r from-purple-400 via-violet-300 to-indigo-400 bg-clip-text text-transparent">
              {LANDING_HERO_DATA.headlineHighlight}
            </span>
          </h1>

          <p className="text-sm sm:text-base md:text-lg text-slate-300 max-w-2xl mx-auto lg:mx-0 leading-relaxed font-normal">
            {LANDING_HERO_DATA.description}
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 sm:gap-4 pt-2">
            <CosmicButton
              variant="primary"
              size="lg"
              className="w-full sm:w-auto text-sm sm:text-base font-semibold py-3 px-6 shadow-lg shadow-purple-600/25"
              onClick={onStartFree}
            >
              <span>{LANDING_HERO_DATA.primaryCta}</span>
              <ArrowRight className="w-4 h-4 ml-2" />
            </CosmicButton>

            <CosmicButton
              variant="outline"
              size="lg"
              className="w-full sm:w-auto text-sm sm:text-base border-purple-500/40 hover:bg-purple-950/30 text-purple-200"
              onClick={onViewPlans}
            >
              <span>{LANDING_HERO_DATA.secondaryCta}</span>
            </CosmicButton>
          </div>

          {/* Trust Points */}
          <div className="flex flex-wrap items-center justify-center lg:justify-start gap-4 pt-4 text-xs sm:text-sm text-slate-400">
            <span className="flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-400" /> No credit card required
            </span>
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-purple-400" /> Commercial use license
            </span>
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-400" /> 1-Click fast export
            </span>
          </div>

          {/* Key Metrics Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-6 border-t border-purple-900/30">
            {LANDING_HERO_DATA.stats.map((stat, idx) => (
              <div key={idx} className="bg-purple-950/20 rounded-xl p-3 border border-purple-800/20 text-center lg:text-left">
                <div className="text-white font-bold text-sm sm:text-base">{stat.value}</div>
                <div className="text-slate-400 text-xs mt-0.5">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Live Vertical 9:16 Video Mockup Showcase */}
        <div className="w-full max-w-[280px] sm:max-w-[320px] lg:max-w-[340px] shrink-0 mx-auto">
          <div className="relative rounded-[32px] p-2 bg-gradient-to-b from-purple-500/30 via-purple-950/40 to-slate-900/80 border border-purple-500/40 shadow-2xl shadow-purple-950/80">
            {/* Phone Screen Container */}
            <div className="relative aspect-[9/16] rounded-[24px] overflow-hidden bg-slate-950 flex flex-col justify-between border border-purple-500/20">
              {/* Top Notch & Channel Meta */}
              <div className="z-10 p-4 bg-gradient-to-b from-black/80 via-black/40 to-transparent flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xl">👶</span>
                  <div className="text-left">
                    <p className="text-xs font-bold text-white leading-tight">Chutti Kuzhandhai</p>
                    <p className="text-[10px] text-purple-300">Emotional Drama • Tamil</p>
                  </div>
                </div>
                <Badge variant="purple" className="text-[10px] py-0.5 px-2">9:16 HD</Badge>
              </div>

              {/* Center Scene Visual Background */}
              <div className="absolute inset-0 bg-cover bg-center filter brightness-[0.85] transition-all duration-700"
                style={{
                  backgroundImage: "url('https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=600')"
                }}
              />

              {/* Glowing Caption Overlay (18% bottom safe zone) */}
              <div className="z-10 px-4 pb-6 pt-16 bg-gradient-to-t from-black/95 via-black/50 to-transparent flex flex-col items-center text-center">
                <div className="mb-3 px-3 py-1.5 rounded-lg bg-black/70 border border-yellow-500/40 shadow-lg">
                  <p className="text-xs sm:text-sm font-extrabold text-yellow-400 tracking-wide uppercase">
                    "இந்த ஒரு ஆசை அவனுடைய வாழ்க்கையை மாற்றியது..."
                  </p>
                </div>
                
                <p className="text-[11px] text-slate-300 line-clamp-1 mb-3">
                  #shorts #tamil #drama #autoreels
                </p>

                {/* Simulated playback bar */}
                <div className="w-full h-1 bg-white/20 rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500 rounded-full w-2/3 animate-pulse" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
