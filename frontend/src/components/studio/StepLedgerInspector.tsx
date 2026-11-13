"use client";

import React from "react";
import { CheckCircle, AlertTriangle, RefreshCw, XCircle, Clock, Server, Hash, Layers } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { CosmicButton } from "../common/CosmicButton";
import { PIPELINE_STRINGS, StepLedgerItem } from "../hardcodedata/pipeline";

interface StepLedgerInspectorProps {
  isOpen: boolean;
  onClose: () => void;
  jobId: string | null;
  steps: StepLedgerItem[];
  isDegraded?: boolean;
  onRetry?: (jobId: string) => Promise<void>;
  isRetrying?: boolean;
}

export function StepLedgerInspector({
  isOpen,
  onClose,
  jobId,
  steps,
  isDegraded,
  onRetry,
  isRetrying
}: StepLedgerInspectorProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md">
      <GlassPanel className="w-full max-w-2xl max-h-[90vh] flex flex-col p-4 sm:p-6 space-y-4 border-purple-500/40 shadow-[0_0_50px_rgba(139,92,246,0.25)]">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 border-b border-purple-500/20 pb-3">
          <div className="space-y-1 min-w-0">
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-purple-400 flex-shrink-0" />
              <h2 className="text-base sm:text-lg font-bold text-white tracking-tight truncate">
                {PIPELINE_STRINGS.ledgerTitle}
              </h2>
              {isDegraded && (
                <Badge variant="yellow" className="text-[10px] font-mono">
                  DEGRADED
                </Badge>
              )}
            </div>
            <p className="text-xs text-purple-300/80 truncate">
              {PIPELINE_STRINGS.ledgerSubtitle}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-purple-400 hover:text-white hover:bg-purple-900/30 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Degraded Alert if applicable */}
        {isDegraded && (
          <div className="p-3 rounded-xl bg-amber-950/40 border border-amber-500/30 text-amber-200 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <span>{PIPELINE_STRINGS.degradedWarning}</span>
          </div>
        )}

        {/* Steps List */}
        <div className="flex-1 overflow-y-auto space-y-3 pr-1 scrollbar-thin">
          {steps.length === 0 ? (
            <div className="text-center py-8 text-xs text-purple-400">
              Initializing step-ledger state for job {jobId ?? "active"}...
            </div>
          ) : (
            steps.map((step) => {
              const isSuccess = step.status === "SUCCEEDED";
              const isDegradedStep = step.status === "DEGRADED";
              const isFailed = step.status === "FAILED";
              const isRunning = step.status === "RUNNING";

              return (
                <div
                  key={step.id || `${step.step_key}_${step.scene_index}`}
                  className="p-3.5 rounded-xl bg-purple-950/30 border border-purple-500/20 space-y-2 hover:border-purple-500/40 transition-colors"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 font-semibold text-white text-xs">
                      {isSuccess && <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />}
                      {isDegradedStep && <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />}
                      {isFailed && <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />}
                      {isRunning && <RefreshCw className="w-4 h-4 text-purple-400 animate-spin flex-shrink-0" />}

                      <span className="capitalize">
                        {step.step_key === "image"
                          ? `Scene ${step.scene_index !== null ? (step.scene_index ?? 0) + 1 : 1} Visual`
                          : step.step_key}
                      </span>
                    </div>

                    <Badge
                      variant={
                        isSuccess
                          ? "emerald"
                          : isDegradedStep
                          ? "yellow"
                          : isFailed
                          ? "red"
                          : "purple"
                      }
                      className="text-[10px] uppercase font-mono"
                    >
                      {step.status}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[11px] font-mono text-purple-300/80 pt-1 border-t border-purple-500/10">
                    <div className="flex items-center gap-1">
                      <Server className="w-3 h-3 text-purple-400" />
                      <span className="truncate">{step.provider || "local"}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-purple-400" />
                      <span>Attempt #{step.attempt}</span>
                    </div>
                    <div className="flex items-center gap-1 col-span-2 sm:col-span-1">
                      <Hash className="w-3 h-3 text-purple-400" />
                      <span className="truncate">{step.input_hash ? step.input_hash.slice(0, 8) : "—"}</span>
                    </div>
                  </div>

                  {step.error_detail && (
                    <div className="text-[11px] text-red-300 font-mono bg-red-950/30 p-2 rounded-lg border border-red-500/20">
                      {step.error_class}: {step.error_detail}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between gap-3 pt-3 border-t border-purple-500/20">
          <div className="text-[10px] text-purple-400 font-mono">
            Job ID: <span className="text-white">{jobId ?? "N/A"}</span>
          </div>

          <div className="flex items-center gap-2">
            {onRetry && jobId && steps.some((s) => s.status === "FAILED" || s.status === "DEGRADED") && (
              <CosmicButton
                variant="primary"
                disabled={isRetrying}
                onClick={() => onRetry(jobId)}
                className="text-xs py-1.5"
              >
                <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isRetrying ? "animate-spin" : ""}`} />
                <span>{isRetrying ? PIPELINE_STRINGS.retryingLabel : PIPELINE_STRINGS.retryButton}</span>
              </CosmicButton>
            )}

            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded-xl text-xs text-purple-300 hover:text-white"
            >
              {PIPELINE_STRINGS.closeLedger}
            </button>
          </div>
        </div>
      </GlassPanel>
    </div>
  );
}
