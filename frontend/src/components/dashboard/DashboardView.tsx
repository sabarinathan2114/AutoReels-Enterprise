import React from "react";
import { MetricsGrid } from "./MetricsGrid";
import { UsageMeter } from "./UsageMeter";
import { AccountsGrid } from "./AccountsGrid";
import { ActivityLogTable } from "./ActivityLogTable";

export function DashboardView() {
  return (
    <div className="space-y-6 w-full max-w-full">
      {/* Real-time Quota Meter & Plan Entitlements */}
      <UsageMeter />

      {/* High-level Channel Analytics */}
      <MetricsGrid />

      {/* Connected Social Channel Holders */}
      <AccountsGrid />

      {/* Recent Broadcast History */}
      <ActivityLogTable />
    </div>
  );
}
