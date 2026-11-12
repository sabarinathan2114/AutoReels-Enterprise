"use client";

import React, { useState } from "react";
import { Search, Building, RefreshCw, CheckCircle, Shield } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { CosmicInput, CosmicSelect } from "../common/FormControls";
import { CosmicButton } from "../common/CosmicButton";
import { ADMIN_STRINGS } from "../hardcodedata/admin";

export interface TenantRow {
  id: string;
  name: string;
  slug: string;
  plan_id: string;
  plan_name: string;
  status: string;
  videos_used: number;
  quota_limit: number;
  remaining: number;
  workspace_id: string | null;
  created_at: string | null;
}

interface TenantsTabProps {
  tenants: TenantRow[];
  onSearch: (query: string) => void;
  onChangePlan: (tenantId: string, newPlanId: string) => Promise<void>;
  isLoading: boolean;
}

export function TenantsTab({ tenants, onSearch, onChangePlan, isLoading }: TenantsTabProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTenant, setSelectedTenant] = useState<TenantRow | null>(null);
  const [targetPlanId, setTargetPlanId] = useState<string>("plan_a");
  const [isChanging, setIsChanging] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearchQuery(val);
    onSearch(val);
  };

  const handleConfirmPlanChange = async () => {
    if (!selectedTenant) return;
    setIsChanging(true);
    setActionSuccess(null);
    try {
      await onChangePlan(selectedTenant.id, targetPlanId);
      setActionSuccess(`Plan for ${selectedTenant.name} updated to ${targetPlanId.toUpperCase()}`);
      setSelectedTenant(null);
      setTimeout(() => setActionSuccess(null), 4000);
    } finally {
      setIsChanging(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <GlassPanel className="p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 text-purple-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <CosmicInput
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder={ADMIN_STRINGS.searchPlaceholder}
            className="pl-10 text-sm"
          />
        </div>
        <div className="text-xs text-purple-300 font-mono self-end sm:self-center">
          Showing {tenants.length} tenants
        </div>
      </GlassPanel>

      {actionSuccess && (
        <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 flex-shrink-0 text-emerald-400" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Tenants Table (Responsive down to 320px) */}
      <GlassPanel className="p-0 overflow-hidden">
        <div className="overflow-x-auto scrollbar-thin">
          <table className="w-full text-left text-xs">
            <thead className="bg-purple-950/40 border-b border-purple-500/20 text-purple-300 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-4">{ADMIN_STRINGS.tableHeaders.studio}</th>
                <th className="py-3 px-4">{ADMIN_STRINGS.tableHeaders.plan}</th>
                <th className="py-3 px-4">{ADMIN_STRINGS.tableHeaders.usage}</th>
                <th className="py-3 px-4">{ADMIN_STRINGS.tableHeaders.status}</th>
                <th className="py-3 px-4 text-right">{ADMIN_STRINGS.tableHeaders.actions}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-500/10">
              {tenants.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-purple-400/80">
                    {isLoading ? "Loading tenant directory..." : ADMIN_STRINGS.noTenantsFound}
                  </td>
                </tr>
              ) : (
                tenants.map((t) => {
                  const usagePercent = Math.min(100, Math.round((t.videos_used / Math.max(1, t.quota_limit)) * 100));
                  return (
                    <tr key={t.id} className="hover:bg-purple-900/20 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-white flex items-center gap-2">
                          <Building className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                          <span className="truncate max-w-[140px] sm:max-w-[200px]">{t.name}</span>
                        </div>
                        <div className="text-[10px] text-purple-400/70 font-mono mt-0.5 truncate max-w-[140px]">
                          {t.slug}
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <Badge
                          variant={
                            t.plan_id === "plan_c"
                              ? "yellow"
                              : t.plan_id === "plan_b"
                              ? "emerald"
                              : t.plan_id === "plan_a"
                              ? "purple"
                              : "dark"
                          }
                          className="font-mono uppercase text-[11px]"
                        >
                          {t.plan_name}
                        </Badge>
                      </td>
                      <td className="py-3.5 px-4 min-w-[140px]">
                        <div className="flex items-center justify-between text-[11px] font-mono text-purple-200 mb-1">
                          <span>{t.videos_used} / {t.quota_limit} vids</span>
                          <span>{t.remaining} left</span>
                        </div>
                        <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              usagePercent >= 100 ? "bg-red-500" : "bg-gradient-to-r from-violet-500 to-fuchsia-500"
                            }`}
                            style={{ width: `${usagePercent}%` }}
                          />
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <Badge variant={t.status === "active" ? "emerald" : "red"} className="text-[10px]">
                          {t.status}
                        </Badge>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => {
                            setSelectedTenant(t);
                            setTargetPlanId(t.plan_id === "free" ? "plan_a" : t.plan_id);
                          }}
                          className="px-2.5 py-1 rounded-lg bg-purple-900/50 hover:bg-purple-800/60 border border-purple-500/30 text-purple-200 hover:text-white text-xs font-medium transition-all"
                        >
                          {ADMIN_STRINGS.changePlanButton}
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </GlassPanel>

      {/* Modal: Change Tenant Plan Tier */}
      {selectedTenant && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <GlassPanel className="w-full max-w-md p-6 space-y-4 border-purple-500/40">
            <div className="flex items-center gap-2 text-purple-300">
              <Shield className="w-5 h-5 text-purple-400" />
              <h3 className="text-base font-bold text-white">Manual Tier Assignment</h3>
            </div>
            <p className="text-xs text-purple-300/80">
              Assign or override subscription tier for <strong className="text-white">{selectedTenant.name}</strong>. This immediately updates video quotas and invalidates cache.
            </p>

            <div className="space-y-3 pt-2">
              <label className="text-xs font-semibold text-purple-200 block">Select Target Plan</label>
              <CosmicSelect
                value={targetPlanId}
                onChange={(e) => setTargetPlanId(e.target.value)}
              >
                <option value="free" className="bg-[#0b0814] text-white">Free Tier (2 videos/mo)</option>
                <option value="plan_a" className="bg-[#0b0814] text-white">Plan A - Creator ($19/mo • 30 videos)</option>
                <option value="plan_b" className="bg-[#0b0814] text-white">Plan B - Pro ($49/mo • 100 videos)</option>
                <option value="plan_c" className="bg-[#0b0814] text-white">Plan C - Agency ($149/mo • 300 videos)</option>
              </CosmicSelect>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-purple-500/20">
              <button
                type="button"
                onClick={() => setSelectedTenant(null)}
                className="px-4 py-2 rounded-xl text-xs text-purple-300 hover:text-white"
              >
                Cancel
              </button>
              <CosmicButton
                variant="primary"
                disabled={isChanging}
                onClick={handleConfirmPlanChange}
                className="text-xs"
              >
                {isChanging ? "Applying..." : "Confirm Tier Change"}
              </CosmicButton>
            </div>
          </GlassPanel>
        </div>
      )}
    </div>
  );
}
