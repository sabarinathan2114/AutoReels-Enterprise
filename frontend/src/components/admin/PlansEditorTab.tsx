"use client";

import React, { useState } from "react";
import { Sliders, CheckCircle, Zap, Shield, Sparkles } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { CosmicButton } from "../common/CosmicButton";
import { CosmicInput } from "../common/FormControls";
import { ADMIN_STRINGS } from "../hardcodedata/admin";

export interface PlanConfigItem {
  id: string;
  name: string;
  monthly_price_cents: number;
  monthly_video_quota: number;
  max_duration_seconds: number;
  resolution: string;
  watermark: boolean;
  allowed_voices_count: number;
  allowed_channels_count: number;
  storage_retention_days: number;
  is_active: boolean;
  features: string[];
}

interface PlansEditorTabProps {
  plans: PlanConfigItem[];
  onSavePlan: (planId: string, updates: Partial<PlanConfigItem>) => Promise<void>;
  isLoading: boolean;
}

export function PlansEditorTab({ plans, onSavePlan, isLoading }: PlansEditorTabProps) {
  const [editingPlanId, setEditingPlanId] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<PlanConfigItem>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const startEditing = (p: PlanConfigItem) => {
    setEditingPlanId(p.id);
    setFormData({
      name: p.name,
      monthly_video_quota: p.monthly_video_quota,
      max_duration_seconds: p.max_duration_seconds,
      resolution: p.resolution,
      watermark: p.watermark
    });
  };

  const handleSave = async (planId: string) => {
    setIsSaving(true);
    setNotice(null);
    try {
      await onSavePlan(planId, formData);
      setNotice(`Updated limits for ${planId.toUpperCase()}! Cache invalidated immediately (PLAN-04).`);
      setEditingPlanId(null);
      setTimeout(() => setNotice(null), 4000);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-purple-400" />
            <span>{ADMIN_STRINGS.plansTitle}</span>
          </h2>
          <p className="text-xs text-purple-300/80 mt-1">
            {ADMIN_STRINGS.plansSubtitle}
          </p>
        </div>
      </div>

      {notice && (
        <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 flex-shrink-0 text-emerald-400" />
          <span>{notice}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {plans.map((p) => {
          const isCurrentlyEditing = editingPlanId === p.id;

          return (
            <GlassPanel
              key={p.id}
              className={`p-5 flex flex-col justify-between space-y-4 border ${
                p.id === "plan_a"
                  ? "border-purple-500/50 shadow-[0_0_20px_rgba(139,92,246,0.15)]"
                  : "border-white/10"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge
                    variant={
                      p.id === "plan_c"
                        ? "yellow"
                        : p.id === "plan_b"
                        ? "emerald"
                        : p.id === "plan_a"
                        ? "purple"
                        : "dark"
                    }
                    className="font-mono uppercase text-[11px]"
                  >
                    {p.id}
                  </Badge>
                  <span className="text-xs font-bold text-purple-300">
                    {p.monthly_price_cents === 0 ? "FREE" : `$${p.monthly_price_cents / 100}/mo`}
                  </span>
                </div>

                <div className="font-extrabold text-white text-base">
                  {p.name}
                </div>

                {isCurrentlyEditing ? (
                  <div className="space-y-3 pt-2 text-xs">
                    <div>
                      <label className="text-[10px] uppercase font-mono text-purple-300 block mb-1">
                        {ADMIN_STRINGS.planQuotaLabel}
                      </label>
                      <CosmicInput
                        type="number"
                        min="1"
                        value={formData.monthly_video_quota ?? p.monthly_video_quota}
                        onChange={(e) =>
                          setFormData({ ...formData, monthly_video_quota: parseInt(e.target.value, 10) })
                        }
                      />
                    </div>
                    <div>
                      <label className="text-[10px] uppercase font-mono text-purple-300 block mb-1">
                        {ADMIN_STRINGS.planDurationLabel}
                      </label>
                      <CosmicInput
                        type="number"
                        min="15"
                        value={formData.max_duration_seconds ?? p.max_duration_seconds}
                        onChange={(e) =>
                          setFormData({ ...formData, max_duration_seconds: parseInt(e.target.value, 10) })
                        }
                      />
                    </div>
                    <div>
                      <label className="text-[10px] uppercase font-mono text-purple-300 block mb-1">
                        {ADMIN_STRINGS.planResolutionLabel}
                      </label>
                      <CosmicInput
                        type="text"
                        value={formData.resolution ?? p.resolution}
                        onChange={(e) => setFormData({ ...formData, resolution: e.target.value })}
                      />
                    </div>
                    <div className="flex items-center gap-2 pt-1">
                      <input
                        type="checkbox"
                        id={`watermark-${p.id}`}
                        checked={formData.watermark ?? p.watermark}
                        onChange={(e) => setFormData({ ...formData, watermark: e.target.checked })}
                        className="rounded border-purple-500/40 text-purple-600 focus:ring-0"
                      />
                      <label htmlFor={`watermark-${p.id}`} className="text-xs text-purple-200">
                        Include Watermark
                      </label>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-2 pt-2 text-xs divide-y divide-white/5">
                    <div className="flex items-center justify-between py-1">
                      <span className="text-purple-300/80">Monthly Quota</span>
                      <span className="font-bold text-white font-mono">{p.monthly_video_quota} vids</span>
                    </div>
                    <div className="flex items-center justify-between py-1">
                      <span className="text-purple-300/80">Max Duration</span>
                      <span className="font-bold text-white font-mono">{p.max_duration_seconds}s</span>
                    </div>
                    <div className="flex items-center justify-between py-1">
                      <span className="text-purple-300/80">Resolution</span>
                      <span className="font-bold text-white font-mono">{p.resolution}</span>
                    </div>
                    <div className="flex items-center justify-between py-1">
                      <span className="text-purple-300/80">Watermark</span>
                      <span className="font-bold text-white font-mono">
                        {p.watermark ? "Yes (Free)" : "No Watermark"}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-purple-500/20">
                {isCurrentlyEditing ? (
                  <div className="flex items-center gap-2">
                    <CosmicButton
                      variant="primary"
                      disabled={isSaving}
                      onClick={() => handleSave(p.id)}
                      className="flex-1 text-xs py-1.5"
                    >
                      {isSaving ? "Saving..." : "Save"}
                    </CosmicButton>
                    <button
                      type="button"
                      onClick={() => setEditingPlanId(null)}
                      className="px-3 py-1.5 rounded-xl text-xs text-purple-300 hover:text-white"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => startEditing(p)}
                    className="w-full py-2 rounded-xl bg-purple-900/40 hover:bg-purple-800/60 border border-purple-500/30 text-purple-200 hover:text-white text-xs font-semibold transition-all"
                  >
                    Edit Limits
                  </button>
                )}
              </div>
            </GlassPanel>
          );
        })}
      </div>
    </div>
  );
}
