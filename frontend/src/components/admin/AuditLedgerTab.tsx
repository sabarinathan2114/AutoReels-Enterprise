"use client";

import React, { useState } from "react";
import { History, Shield, Terminal, Clock, User } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { ADMIN_STRINGS } from "../hardcodedata/admin";

export interface AuditLogItem {
  id: string;
  tenant_id: string | null;
  action: string;
  resource: string;
  details: Record<string, any> | null;
  user_id: string | null;
  ip_address: string | null;
  created_at: string | null;
}

interface AuditLedgerTabProps {
  logs: AuditLogItem[];
  isLoading: boolean;
}

export function AuditLedgerTab({ logs, isLoading }: AuditLedgerTabProps) {
  const [selectedLog, setSelectedLog] = useState<AuditLogItem | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-purple-400" />
            <span>{ADMIN_STRINGS.auditTitle}</span>
          </h2>
          <p className="text-xs text-purple-300/80 mt-1">
            {ADMIN_STRINGS.auditSubtitle}
          </p>
        </div>
      </div>

      <GlassPanel className="p-0 overflow-hidden">
        <div className="overflow-x-auto scrollbar-thin">
          <table className="w-full text-left text-xs">
            <thead className="bg-purple-950/40 border-b border-purple-500/20 text-purple-300 uppercase tracking-wider font-semibold font-mono">
              <tr>
                <th className="py-3 px-4">{ADMIN_STRINGS.auditTableHeaders.timestamp}</th>
                <th className="py-3 px-4">{ADMIN_STRINGS.auditTableHeaders.action}</th>
                <th className="py-3 px-4">{ADMIN_STRINGS.auditTableHeaders.resource}</th>
                <th className="py-3 px-4">{ADMIN_STRINGS.auditTableHeaders.actor}</th>
                <th className="py-3 px-4">{ADMIN_STRINGS.auditTableHeaders.details}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-500/10">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-purple-400/80">
                    {isLoading ? "Reading audit ledger..." : "No administrative actions recorded yet."}
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr
                    key={log.id}
                    onClick={() => setSelectedLog(log)}
                    className="hover:bg-purple-900/20 transition-colors cursor-pointer"
                  >
                    <td className="py-3 px-4 whitespace-nowrap text-purple-300/80 font-mono text-[11px]">
                      {log.created_at ? new Date(log.created_at).toISOString().replace("T", " ").slice(0, 19) : "—"}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant="purple" className="font-mono text-[10px]">
                        {log.action}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-purple-200 font-mono text-[11px]">
                      {log.resource}
                    </td>
                    <td className="py-3 px-4 text-white font-mono text-[11px]">
                      User #{log.user_id ?? "system"}
                    </td>
                    <td className="py-3 px-4 max-w-xs truncate text-[11px] font-mono text-purple-300/80">
                      {JSON.stringify(log.details)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </GlassPanel>

      {/* Detail Dialog for JSON inspect */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <GlassPanel className="w-full max-w-lg p-6 space-y-4 border-purple-500/40">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Terminal className="w-5 h-5 text-purple-400" />
                <span>Audit Event Record</span>
              </h3>
              <Badge variant="purple" className="font-mono text-xs">
                {selectedLog.action}
              </Badge>
            </div>

            <div className="space-y-2 text-xs font-mono text-purple-200">
              <div><strong className="text-purple-400">Timestamp:</strong> {selectedLog.created_at}</div>
              <div><strong className="text-purple-400">Actor User:</strong> #{selectedLog.user_id}</div>
              <div><strong className="text-purple-400">Resource:</strong> {selectedLog.resource}</div>
              <div><strong className="text-purple-400">Tenant ID:</strong> {selectedLog.tenant_id ?? "N/A"}</div>
            </div>

            <div className="space-y-1">
              <span className="text-[11px] uppercase font-mono text-purple-400 font-semibold block">
                Audit Payload JSON
              </span>
              <pre className="p-3 rounded-xl bg-black/60 border border-purple-500/30 text-[11px] font-mono text-emerald-300 overflow-x-auto max-h-48">
                {JSON.stringify(selectedLog.details, null, 2)}
              </pre>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 rounded-xl btn-cosmic text-xs font-semibold"
              >
                Close Inspector
              </button>
            </div>
          </GlassPanel>
        </div>
      )}
    </div>
  );
}
