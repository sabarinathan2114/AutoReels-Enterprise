import React from "react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { ACTIVITY_LOGS_DATA, ActivityLogItem } from "../hardcodedata";

export function ActivityLogTable() {
  return (
    <GlassPanel className="p-4 sm:p-5 space-y-3 w-full">
      <div className="flex items-center justify-between pb-2 border-b border-purple-500/20">
        <h3 className="text-xs sm:text-sm font-bold text-purple-200 tracking-wide uppercase truncate">
          Recent Broadcast History & Performance
        </h3>
        <Badge variant="purple">Live Sync</Badge>
      </div>

      <div className="divide-y divide-purple-500/20 text-xs">
        {ACTIVITY_LOGS_DATA.map((item: ActivityLogItem) => (
          <div
            key={item.id}
            className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 sm:gap-4"
          >
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-purple-900/60 flex items-center justify-center font-bold text-purple-200 flex-shrink-0 text-base">
                {item.icon}
              </div>
              <div className="min-w-0">
                <p className="font-semibold text-white truncate text-xs sm:text-sm">
                  {item.title}
                </p>
                <span className="text-[10px] text-purple-400 block truncate">
                  Dispatched: {item.destinations}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between sm:justify-end gap-3 sm:gap-6 flex-shrink-0 pt-1 sm:pt-0 pl-12 sm:pl-0">
              <span className="text-emerald-400 font-mono font-bold text-xs sm:text-sm">
                {item.views}
              </span>
              <span className="text-[10px] sm:text-[11px] bg-purple-900/50 text-purple-200 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full border border-purple-500/30 whitespace-nowrap">
                {item.timestamp}
              </span>
            </div>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}
