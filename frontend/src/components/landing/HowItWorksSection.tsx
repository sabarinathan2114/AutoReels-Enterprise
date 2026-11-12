"use client";

import React from "react";
import { Wand2, Mic, Sparkles, ArrowRight } from "lucide-react";
import { GlassPanel } from "@/components/common/GlassPanel";
import { Badge } from "@/components/common/Badge";
import { HOW_IT_WORKS_STEPS } from "@/components/hardcodedata";

export const HowItWorksSection: React.FC = () => {
  const getIcon = (name: string) => {
    switch (name) {
      case "wand":
        return <Wand2 className="w-6 h-6 text-purple-400" />;
      case "mic":
        return <Mic className="w-6 h-6 text-pink-400" />;
      case "sparkles":
      default:
        return <Sparkles className="w-6 h-6 text-amber-400" />;
    }
  };

  return (
    <section className="py-12 md:py-20 border-t border-purple-900/30 relative">
      <div className="max-w-7xl mx-auto px-3 sm:px-6">
        <div className="text-center max-w-3xl mx-auto mb-10 sm:mb-14">
          <Badge variant="purple" className="mb-3">Simplicity First</Badge>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            How AutoReels Works in 3 Simple Steps
          </h2>
          <p className="text-slate-400 text-sm sm:text-base mt-2">
            No complex video editors, timelines, or manual keyframing. Go from prompt to rendered reel automatically.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          {HOW_IT_WORKS_STEPS.map((step, idx) => (
            <GlassPanel
              key={step.step}
              className="relative p-6 flex flex-col justify-between border-purple-500/20 hover:border-purple-500/50 transition-all duration-300 group"
            >
              {/* Step indicator */}
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl font-black text-purple-500/30 group-hover:text-purple-400/50 transition-colors">
                  {step.step}
                </span>
                <Badge variant="dark" className="text-xs">{step.badge}</Badge>
              </div>

              <div className="mb-4">
                <div className="w-12 h-12 rounded-xl bg-purple-950/60 border border-purple-500/30 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  {getIcon(step.iconName)}
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
                  {step.description}
                </p>
              </div>

              <div className="pt-4 border-t border-purple-900/20 flex items-center text-xs text-purple-300 font-medium">
                <span>Autonomous execution</span>
                <ArrowRight className="w-3.5 h-3.5 ml-1.5 opacity-60 group-hover:translate-x-1 transition-transform" />
              </div>
            </GlassPanel>
          ))}
        </div>
      </div>
    </section>
  );
};
