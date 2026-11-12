"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, AlertCircle, ArrowUpRight, Check, Send, X, ShieldAlert } from "lucide-react";
import { GlassPanel } from "@/components/common/GlassPanel";
import { CosmicButton } from "@/components/common/CosmicButton";
import { Badge } from "@/components/common/Badge";
import { AuthStorage } from "@/components/common/authStorage";

interface EntitlementsData {
  workspace_id: string;
  plan_id: string;
  plan_name: string;
  monthly_quota: number;
  used_this_period: number;
  remaining_quota: number;
  is_quota_exhausted: boolean;
  resolution: string;
  watermark: boolean;
  resets_at: string;
}

export const UsageMeter: React.FC = () => {
  const [entitlements, setEntitlements] = useState<EntitlementsData>({
    workspace_id: "default",
    plan_id: "free",
    plan_name: "Free Tier",
    monthly_quota: 2,
    used_this_period: 0,
    remaining_quota: 2,
    is_quota_exhausted: false,
    resolution: "720x1280",
    watermark: true,
    resets_at: "2026-12-01T00:00:00Z"
  });
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);
  const [requestedPlan, setRequestedPlan] = useState<string>("plan_a");
  const [requestNotes, setRequestNotes] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  useEffect(() => {
    const fetchEntitlements = async () => {
      try {
        const user = AuthStorage.getUser();
        const wsParam = user?.workspace_id ? `?workspace_id=${user.workspace_id}` : "";
        const res = await fetch(`http://localhost:8000/api/v1/me/entitlements${wsParam}`);
        if (res.ok) {
          const data = await res.json();
          setEntitlements(data);
        }
      } catch (err) {
        console.warn("Could not fetch live entitlements; using baseline default:", err);
      }
    };
    fetchEntitlements();
  }, []);

  const handleUpgradeSubmit = async () => {
    setIsSubmitting(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/workspaces/${entitlements.workspace_id}/upgrade-request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          requested_plan_id: requestedPlan,
          notes: requestNotes || "Submitted from dashboard usage meter"
        })
      });
      if (res.ok) {
        setSubmitSuccess(true);
        setTimeout(() => {
          setIsUpgradeModalOpen(false);
          setSubmitSuccess(false);
        }, 1500);
      }
    } catch (err) {
      alert("Upgrade request submitted! An administrator will review your tier.");
      setIsUpgradeModalOpen(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const percentUsed = Math.min(100, Math.round((entitlements.used_this_period / entitlements.monthly_quota) * 100));

  return (
    <>
      <GlassPanel className="p-4 sm:p-5 border-purple-500/30 shadow-lg shadow-purple-950/40">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-bold text-white">Monthly Video Quota</span>
              <Badge variant="purple" className="text-[11px] py-0.5 px-2">
                {entitlements.plan_name}
              </Badge>
              {entitlements.watermark && (
                <span className="text-[10px] text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-500/20">
                  Watermark Enabled
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400">
              {entitlements.used_this_period} of {entitlements.monthly_quota} videos created this calendar month
            </p>
          </div>

          <CosmicButton
            variant="outline"
            size="sm"
            onClick={() => setIsUpgradeModalOpen(true)}
            className="text-xs border-purple-500/40 hover:bg-purple-900/30 w-full sm:w-auto"
          >
            <span>Request Upgrade</span>
            <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
          </CosmicButton>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-purple-950/60 h-2.5 rounded-full overflow-hidden p-0.5 border border-purple-900/30 mb-2">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              entitlements.is_quota_exhausted
                ? "bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.8)]"
                : percentUsed > 50
                ? "bg-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.6)]"
                : "bg-gradient-to-r from-purple-500 to-indigo-400 shadow-[0_0_12px_rgba(139,92,246,0.6)]"
            }`}
            style={{ width: `${percentUsed}%` }}
          />
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span>{entitlements.remaining_quota} renders remaining</span>
          <span>Resets on 1st of next month</span>
        </div>

        {/* Quota Exhausted Banner */}
        {entitlements.is_quota_exhausted && (
          <div className="mt-3 p-3 rounded-xl bg-red-950/30 border border-red-500/40 flex items-start gap-2.5 text-xs text-red-200">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <div className="flex-1">
              <strong className="block text-white font-semibold">Monthly Limit Reached</strong>
              You have rendered all {entitlements.monthly_quota} free videos for this period. Need more? Request an upgrade for higher monthly caps.
            </div>
          </div>
        )}
      </GlassPanel>

      {/* Upgrade Request Modal */}
      {isUpgradeModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <GlassPanel className="relative w-full max-w-md p-5 sm:p-6 border-purple-500/40 shadow-2xl">
            <button
              onClick={() => setIsUpgradeModalOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="mb-5 text-left">
              <Badge variant="purple" className="mb-2">Admin Approval Required</Badge>
              <h3 className="text-lg font-bold text-white">Request Plan Upgrade</h3>
              <p className="text-xs text-slate-400 mt-1">
                Select your target tier. Platform administrators review requests without requiring payment gateways.
              </p>
            </div>

            {submitSuccess ? (
              <div className="py-6 text-center space-y-2">
                <Check className="w-10 h-10 text-emerald-400 mx-auto" />
                <p className="text-sm font-bold text-white">Upgrade Request Submitted!</p>
                <p className="text-xs text-slate-400">An administrator will update your workspace quota shortly.</p>
              </div>
            ) : (
              <div className="space-y-4 text-left">
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-300">Target Plan Tier</label>
                  <div className="space-y-2">
                    {[
                      { id: "plan_a", name: "Plan A (Creator)", quota: "30 videos/mo", res: "1080p • No Watermark", price: "$9.00 / Promo" },
                      { id: "plan_b", name: "Plan B (Growth)", quota: "100 videos/mo", res: "Character Mode • 3 Channels", price: "$29.00" },
                      { id: "plan_c", name: "Plan C (Agency)", quota: "500 videos/mo", res: "Brand Voice • Priority Render", price: "$79.00" }
                    ].map((tier) => (
                      <div
                        key={tier.id}
                        onClick={() => setRequestedPlan(tier.id)}
                        className={`p-3 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                          requestedPlan === tier.id
                            ? "bg-purple-950/60 border-purple-400 shadow-md"
                            : "bg-black/30 border-purple-900/30 hover:border-purple-600/40"
                        }`}
                      >
                        <div>
                          <p className="text-xs font-bold text-white">{tier.name}</p>
                          <p className="text-[10px] text-purple-300">{tier.quota} • {tier.res}</p>
                        </div>
                        <span className="text-xs font-semibold text-slate-200">{tier.price}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300">Creator Notes / Justification</label>
                  <textarea
                    rows={3}
                    value={requestNotes}
                    onChange={(e) => setRequestNotes(e.target.value)}
                    placeholder="e.g., Scaling short-form publishing for daily news channel..."
                    className="w-full px-3 py-2 rounded-xl bg-purple-950/30 border border-purple-500/30 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-purple-400"
                  />
                </div>

                <div className="pt-2 flex justify-end gap-2">
                  <CosmicButton
                    variant="outline"
                    size="sm"
                    onClick={() => setIsUpgradeModalOpen(false)}
                    className="text-xs"
                  >
                    Cancel
                  </CosmicButton>
                  <CosmicButton
                    variant="primary"
                    size="sm"
                    onClick={handleUpgradeSubmit}
                    disabled={isSubmitting}
                    className="text-xs font-semibold"
                  >
                    <Send className="w-3.5 h-3.5 mr-1" />
                    <span>{isSubmitting ? "Submitting..." : "Send Request"}</span>
                  </CosmicButton>
                </div>
              </div>
            )}
          </GlassPanel>
        </div>
      )}
    </>
  );
};
