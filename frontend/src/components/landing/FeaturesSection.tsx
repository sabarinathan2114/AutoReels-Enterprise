"use client";

import React from "react";
import { GlassPanel } from "@/components/common/GlassPanel";
import { Badge } from "@/components/common/Badge";
import { FEATURE_SHOWCASE_DATA } from "@/components/hardcodedata";
import { Mic, Video, Layers, ShieldCheck, Share2, Sparkles } from "lucide-react";

export const FeaturesSection: React.FC = () => {
  const getIcon = (id: string) => {
    switch (id) {
      case "feat_tts":
        return <Mic className="w-5 h-5 text-purple-400" />;
      case "feat_captions":
        return <Video className="w-5 h-5 text-pink-400" />;
      case "feat_ladder":
        return <Layers className="w-5 h-5 text-cyan-400" />;
      case "feat_tenancy":
        return <ShieldCheck className="w-5 h-5 text-emerald-400" />;
      case "feat_autopilot":
        return <Share2 className="w-5 h-5 text-amber-400" />;
      case "feat_plans":
      default:
        return <Sparkles className="w-5 h-5 text-indigo-400" />;
    }
  };

  return (
    <section className="py-12 md:py-20 border-t border-purple-900/30 relative">
      <div className="max-w-7xl mx-auto px-3 sm:px-6">
        <div className="text-center max-w-3xl mx-auto mb-10 sm:mb-14">
          <Badge variant="purple" className="mb-3">Zero Compromises</Badge>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Engineered for Autonomous Video Growth
          </h2>
          <p className="text-slate-400 text-sm sm:text-base mt-2">
            Every layer of the AutoReels pipeline is tuned for speed, strict CPU memory budgets, and virality.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURE_SHOWCASE_DATA.map((feature) => (
            <GlassPanel
              key={feature.id}
              className="p-6 border-purple-800/30 hover:border-purple-500/50 transition-all duration-300 flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-purple-950/60 border border-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                    {getIcon(feature.id)}
                  </div>
                  <span className="text-[11px] font-semibold text-purple-300 bg-purple-950/50 px-2.5 py-1 rounded-md border border-purple-800/30">
                    {feature.tag}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>

              <div className="mt-4 pt-4 border-t border-purple-900/20 text-xs text-purple-300 font-medium">
                Highlight: <span className="text-white font-semibold">{feature.highlight}</span>
              </div>
            </GlassPanel>
          ))}
        </div>
      </div>
    </section>
  );
};
