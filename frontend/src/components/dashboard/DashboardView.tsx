import React from "react";
import { MetricsGrid } from "./MetricsGrid";
import { AccountsGrid } from "./AccountsGrid";
import { ActivityLogTable } from "./ActivityLogTable";

export function DashboardView() {
  return (
    <div className="space-y-6 w-full max-w-full">
      <MetricsGrid />
      <AccountsGrid />
      <ActivityLogTable />
    </div>
  );
}
