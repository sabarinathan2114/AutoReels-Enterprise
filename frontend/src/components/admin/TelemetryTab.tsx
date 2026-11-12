"use client";

import React, { useState } from "react";
import { Activity, Server, Cpu, CheckCircle, Shield, Sliders } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { CosmicButton } from "../common/CosmicButton";
import { CosmicInput } from "../common/FormControls";
import { ADMIN_STRINGS } from "../hardcodedata/admin";

interface TelemetryData {
  total_tenants: number;
  total_users: number;
  pending_upgrade_requests: number;
  videos_rendered_this_month: number;
  max_videos_per_day: number;
  plan_distribution: Record<string, number>;
  active_workers: number;
  queue_status: string;
  capacity_status: string;
}

interface TelemetryTabProps {
  telemetry: TelemetryData | null;
  onUpdateDailyCap: (newCap: number) => Promise<void>;
}

export function TelemetryTab({ telemetry, onUpdateDailyCap }: TelemetryTabProps) {
  const [dailyCapInput, setDailyCapInput] = useState<string>(
    telemetry ? String(telemetry.max_videos_per_day) : "100"
  );
  const [isUpdating, setIsUpdating] = useState(false);
  const [capSuccessMsg, setCapSuccessMsg] = useState<string | null>(null);

  const handleCapSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const val = parseInt(dailyCapInput, 10);
    if (isNaN(val) || val <= 0) return;
    setIsUpdating(true);
    setCapSuccessMsg(null);
    try {
      await onUpdateDailyCap(val);
      setCapSuccessMsg(`Daily video cap updated to ${val} videos/day.`);
      setTimeout(() => setCapSuccessMsg(null), 4000);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Telemetry Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <GlassPanel className="p-4 sm:p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-purple-300 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">Active Tenants</span>
            <Server className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white">
            {telemetry?.total_tenants ?? "—"}
          </div>
          <div className="mt-2 text-[11px] text-purple-400/80 font-mono">
            {telemetry?.total_users ?? 0} registered creators
          </div>
        </GlassPanel>

        <GlassPanel className="p-4 sm:p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-emerald-300 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">Videos This Month</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-300">
            {telemetry?.videos_rendered_this_month ?? 0}
          </div>
          <div className="mt-2 text-[11px] text-emerald-400/80 font-mono">
            Direct FFmpeg CPU renders
          </div>
        </GlassPanel>

        <GlassPanel className="p-4 sm:p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-amber-300 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">Pending Upgrades</span>
            <Shield className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-300">
            {telemetry?.pending_upgrade_requests ?? 0}
          </div>
          <div className="mt-2 text-[11px] text-amber-400/80 font-mono">
            Awaiting SuperAdmin approval
          </div>
        </GlassPanel>

        <GlassPanel className="p-4 sm:p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-cyan-300 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">{ADMIN_STRINGS.farmStatusLabel}</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="emerald" className="text-xs font-bold py-1">
              HEALTHY (0.00% DROP)
            </Badge>
          </div>
          <div className="mt-2 text-[11px] text-cyan-400/80 font-mono">
            {telemetry?.active_workers ?? 1} CPU worker node active
          </div>
        </GlassPanel>
      </div>

      {/* Daily Cap & Capacity Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassPanel className="p-5 sm:p-6 space-y-4">
          <div className="flex items-center gap-2.5">
            <Sliders className="w-5 h-5 text-purple-400" />
            <h3 className="text-base sm:text-lg font-bold text-white">
              {ADMIN_STRINGS.dailyCapLabel}
            </h3>
          </div>
          <p className="text-xs text-purple-300/80 leading-relaxed">
            {ADMIN_STRINGS.dailyCapDescription}
          </p>

          <form onSubmit={handleCapSubmit} className="space-y-4 pt-2">
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <div className="flex-1">
                <CosmicInput
                  type="number"
                  min="1"
                  max="10000"
                  value={dailyCapInput}
                  onChange={(e) => setDailyCapInput(e.target.value)}
                  placeholder="e.g. 100"
                  className="font-mono text-base"
                />
              </div>
              <CosmicButton
                type="submit"
                variant="primary"
                disabled={isUpdating}
                className="whitespace-nowrap"
              >
                {isUpdating ? "Saving..." : ADMIN_STRINGS.updateCapButton}
              </CosmicButton>
            </div>
            {capSuccessMsg && (
              <div className="p-2.5 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 text-xs flex items-center gap-2">
                <CheckCircle className="w-4 h-4 flex-shrink-0 text-emerald-400" />
                <span>{capSuccessMsg}</span>
              </div>
            )}
          </form>
        </GlassPanel>

        {/* Plan Distribution Breakdown */}
        <GlassPanel className="p-5 sm:p-6 space-y-4">
          <h3 className="text-base sm:text-lg font-bold text-white">
            Active Subscription Distribution
          </h3>
          <div className="space-y-3 pt-1">
            {telemetry?.plan_distribution &&
              Object.entries(telemetry.plan_distribution).map(([planId, count]) => (
                <div key={planId} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono uppercase text-purple-300 font-semibold">{planId}</span>
                    <span className="text-purple-200 font-bold">{count} subscriptions</span>
                  </div>
                  <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full"
                      style={{
                        width: `${Math.min(100, (count / Math.max(1, telemetry.total_tenants)) * 100)}%`
                      }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
