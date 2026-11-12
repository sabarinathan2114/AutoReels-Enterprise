"use client";

import React, { useState } from "react";
import { ShieldAlert, CheckCircle, XCircle, Clock, Mail, Building, Sparkles } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { CosmicButton } from "../common/CosmicButton";
import { ADMIN_STRINGS } from "../hardcodedata/admin";

export interface UpgradeRequestItem {
  id: string;
  tenant_id: string;
  tenant_name: string;
  user_id: number;
  user_email: string;
  current_plan_id: string;
  requested_plan_id: string;
  requested_plan_name: string;
  status: string;
  notes: string | null;
  created_at: string | null;
}

interface UpgradesTabProps {
  requests: UpgradeRequestItem[];
  onApprove: (requestId: string) => Promise<void>;
  onReject: (requestId: string, reason: string) => Promise<void>;
  isLoading: boolean;
}

export function UpgradesTab({ requests, onApprove, onReject, isLoading }: UpgradesTabProps) {
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState<string>("");
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const handleApproveClick = async (req: UpgradeRequestItem) => {
    setProcessingId(req.id);
    setActionNotice(null);
    try {
      await onApprove(req.id);
      setActionNotice(`Approved upgrade for ${req.tenant_name} to ${req.requested_plan_name}!`);
      setTimeout(() => setActionNotice(null), 4000);
    } finally {
      setProcessingId(null);
    }
  };

  const handleConfirmReject = async () => {
    if (!rejectingId) return;
    setProcessingId(rejectingId);
    try {
      await onReject(rejectingId, rejectReason || "Capacity threshold reached");
      setActionNotice(`Upgrade request rejected.`);
      setRejectingId(null);
      setRejectReason("");
      setTimeout(() => setActionNotice(null), 4000);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {actionNotice && (
        <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 flex-shrink-0 text-emerald-400" />
          <span>{actionNotice}</span>
        </div>
      )}

      {requests.length === 0 ? (
        <GlassPanel className="p-12 text-center space-y-3">
          <CheckCircle className="w-10 h-10 text-emerald-400 mx-auto" />
          <h3 className="text-base font-bold text-white">
            {isLoading ? "Fetching upgrade queue..." : ADMIN_STRINGS.emptyQueueMessage}
          </h3>
          <p className="text-xs text-purple-300/80 max-w-md mx-auto">
            {ADMIN_STRINGS.upgradesSubtitle}
          </p>
        </GlassPanel>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {requests.map((req) => (
            <GlassPanel
              key={req.id}
              className={`p-5 flex flex-col justify-between space-y-4 border ${
                req.status === "pending"
                  ? "border-purple-500/30 hover:border-purple-500/60"
                  : "border-white/5 opacity-75"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2 text-white font-bold text-sm">
                      <Building className="w-4 h-4 text-purple-400 flex-shrink-0" />
                      <span className="truncate max-w-[180px]">{req.tenant_name}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-purple-300/80 font-mono">
                      <Mail className="w-3 h-3 text-purple-400" />
                      <span className="truncate max-w-[180px]">{req.user_email}</span>
                    </div>
                  </div>
                  <Badge
                    variant={
                      req.status === "approved"
                        ? "emerald"
                        : req.status === "rejected"
                        ? "red"
                        : "yellow"
                    }
                    className="text-[10px] uppercase font-mono"
                  >
                    {req.status}
                  </Badge>
                </div>

                <div className="p-3 rounded-xl bg-purple-950/40 border border-purple-500/20 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-[10px] uppercase text-purple-400/80 font-mono block">
                      {ADMIN_STRINGS.currentPlanLabel}
                    </span>
                    <span className="font-semibold text-white uppercase font-mono">
                      {req.current_plan_id}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase text-purple-400/80 font-mono block">
                      {ADMIN_STRINGS.requestedPlanLabel}
                    </span>
                    <span className="font-bold text-emerald-400 uppercase font-mono flex items-center gap-1">
                      <Sparkles className="w-3 h-3" />
                      {req.requested_plan_name}
                    </span>
                  </div>
                </div>

                {req.notes && (
                  <div className="text-xs text-purple-200/90 italic bg-white/5 p-2.5 rounded-lg border border-white/5">
                    &ldquo;{req.notes}&rdquo;
                  </div>
                )}

                <div className="flex items-center gap-1 text-[10px] text-purple-400/70 font-mono">
                  <Clock className="w-3 h-3" />
                  <span>Submitted: {req.created_at ? new Date(req.created_at).toLocaleString() : "Recently"}</span>
                </div>
              </div>

              {/* Action Buttons for Pending Requests */}
              {req.status === "pending" && (
                <div className="flex items-center gap-2 pt-2 border-t border-purple-500/20">
                  <CosmicButton
                    variant="primary"
                    disabled={processingId === req.id}
                    onClick={() => handleApproveClick(req)}
                    className="flex-1 text-xs py-2"
                  >
                    <CheckCircle className="w-3.5 h-3.5 mr-1" />
                    {processingId === req.id ? "Approving..." : ADMIN_STRINGS.approveButton}
                  </CosmicButton>
                  <button
                    disabled={processingId === req.id}
                    onClick={() => setRejectingId(req.id)}
                    className="px-3 py-2 rounded-xl bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 text-red-300 hover:text-white text-xs font-semibold transition-all flex items-center gap-1"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>{ADMIN_STRINGS.rejectButton}</span>
                  </button>
                </div>
              )}
            </GlassPanel>
          ))}
        </div>
      )}

      {/* Reject Reason Dialog */}
      {rejectingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <GlassPanel className="w-full max-w-md p-6 space-y-4 border-red-500/40">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <XCircle className="w-5 h-5 text-red-400" />
              <span>Reject Upgrade Request</span>
            </h3>
            <p className="text-xs text-purple-300/80">
              {ADMIN_STRINGS.rejectPrompt}
            </p>
            <input
              type="text"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="e.g. Quota allocation currently at capacity"
              className="w-full px-3.5 py-2.5 rounded-xl bg-purple-950/40 border border-purple-500/30 text-white text-xs focus:outline-none focus:border-red-500"
            />
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-purple-500/20">
              <button
                type="button"
                onClick={() => setRejectingId(null)}
                className="px-4 py-2 text-xs text-purple-300 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={processingId === rejectingId}
                onClick={handleConfirmReject}
                className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-bold transition-all"
              >
                Confirm Rejection
              </button>
            </div>
          </GlassPanel>
        </div>
      )}
    </div>
  );
}
