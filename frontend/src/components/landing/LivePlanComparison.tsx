"use client";

import React, { useState, useEffect } from "react";
import { Check, Sparkles, Send, ArrowRight } from "lucide-react";
import { GlassPanel } from "@/components/common/GlassPanel";
import { CosmicButton } from "@/components/common/CosmicButton";
import { Badge } from "@/components/common/Badge";
import { PLANS_DATA } from "@/components/hardcodedata";

interface PlanResponseItem {
  id: string;
  name: string;
  monthly_quota?: number;
  max_duration_sec: number;
  resolution: string;
  watermark: boolean;
  voices: number | string;
  social_channels: number;
  modes: string[];
  storage_retention_days: number;
  price_monthly: string;
}

interface LivePlanComparisonProps {
  onSelectPlan: (planId: string) => void;
  onRequestUpgrade: (planId: string) => void;
}

export const LivePlanComparison: React.FC<LivePlanComparisonProps> = ({
  onSelectPlan,
  onRequestUpgrade
}) => {
  const [plans, setPlans] = useState<PlanResponseItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchLivePlans = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/plans");
        if (res.ok) {
          const data: PlanResponseItem[] = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            setPlans(data);
            setIsLoading(false);
            return;
          }
        }
      } catch (err) {
        console.warn("Backend plans API unreachable; utilizing local baseline plans data:", err);
      }
      
      // Fallback to local baseline if API is down
      const fallbackData: PlanResponseItem[] = PLANS_DATA.map(p => ({
        id: p.id,
        name: p.name,
        monthly_quota: p.id === "free" ? 2 : p.id === "plan_a" ? 30 : p.id === "plan_b" ? 100 : 500,
        max_duration_sec: p.maxDurationSec,
        resolution: p.resolution,
        watermark: p.watermark,
        voices: p.voiceCount,
        social_channels: p.socialChannels,
        modes: p.modes,
        storage_retention_days: p.storageRetentionDays,
        price_monthly: p.priceMonthly
      }));
      setPlans(fallbackData);
      setIsLoading(false);
    };

    fetchLivePlans();
  }, []);

  return (
    <section id="plans" className="py-12 md:py-20 border-t border-purple-900/30 relative">
      <div className="max-w-7xl mx-auto px-3 sm:px-6">
        <div className="text-center max-w-3xl mx-auto mb-10 sm:mb-14">
          <Badge variant="purple" className="mb-3">
            {isLoading ? "Fetching Live Tiers..." : "Live MySQL Entitlements"}
          </Badge>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Transparent, Free-First Plans
          </h2>
          <p className="text-slate-400 text-sm sm:text-base mt-2">
            Every user starts on our permanent Free tier. Upgrade requests are assigned directly by administrators.
          </p>
        </div>

        {/* 4-Tier Plan Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => {
            const isFree = plan.id === "free";
            const isPopular = plan.id === "plan_a";

            return (
              <GlassPanel
                key={plan.id}
                className={`relative p-5 sm:p-6 flex flex-col justify-between transition-all duration-300 ${
                  isPopular
                    ? "border-purple-500 shadow-xl shadow-purple-950/60 bg-purple-950/30"
                    : isFree
                    ? "border-emerald-500/40 bg-emerald-950/10"
                    : "border-purple-800/30"
                }`}
              >
                {/* Popular or Free Badge */}
                {isPopular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-gradient-to-r from-purple-500 to-indigo-500 text-white text-[11px] font-bold px-3 py-1 rounded-full shadow-md uppercase tracking-wider">
                      Most Popular
                    </span>
                  </div>
                )}
                {isFree && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-emerald-600 text-white text-[11px] font-bold px-3 py-1 rounded-full shadow-md uppercase tracking-wider">
                      Default Free
                    </span>
                  </div>
                )}

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-bold text-white">{plan.name}</h3>
                  </div>

                  <div className="mb-4">
                    <span className="text-3xl font-extrabold text-white">{plan.price_monthly}</span>
                    <span className="text-xs text-slate-400 ml-1">/ month</span>
                  </div>

                  {/* Highlights */}
                  <div className="p-3 rounded-lg bg-black/40 border border-purple-900/30 mb-6 text-xs space-y-1.5">
                    <div className="flex justify-between text-slate-300">
                      <span>Monthly Quota:</span>
                      <strong className="text-purple-300 font-bold">{plan.monthly_quota || 2} Videos</strong>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Max Duration:</span>
                      <strong className="text-slate-100">{plan.max_duration_sec}s</strong>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Resolution:</span>
                      <strong className="text-slate-100">{plan.resolution}</strong>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Watermark:</span>
                      <strong className={plan.watermark ? "text-amber-400" : "text-emerald-400"}>
                        {plan.watermark ? "Yes" : "No Watermark"}
                      </strong>
                    </div>
                  </div>

                  {/* Features List */}
                  <ul className="space-y-2 text-xs text-slate-300 mb-6">
                    <li className="flex items-center gap-2">
                      <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{plan.voices} Neural Voices</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{plan.social_channels} Social Channels</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{plan.storage_retention_days} Days Cloud Retention</span>
                    </li>
                    {plan.modes && plan.modes.map((mode, midx) => (
                      <li key={midx} className="flex items-center gap-2">
                        <Check className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                        <span className="capitalize">{mode.replace(/_/g, " ")}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Plan Action CTA */}
                <div>
                  {isFree ? (
                    <CosmicButton
                      variant="primary"
                      className="w-full text-xs py-2.5 font-semibold bg-emerald-600 hover:bg-emerald-500 shadow-md shadow-emerald-950"
                      onClick={() => onSelectPlan(plan.id)}
                    >
                      <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                      Get Started Free
                    </CosmicButton>
                  ) : (
                    <CosmicButton
                      variant="secondary"
                      className="w-full text-xs py-2.5 font-semibold hover:border-purple-400"
                      onClick={() => onRequestUpgrade(plan.id)}
                    >
                      <Send className="w-3.5 h-3.5 mr-1.5" />
                      Request Upgrade
                    </CosmicButton>
                  )}
                </div>
              </GlassPanel>
            );
          })}
        </div>
      </div>
    </section>
  );
};
