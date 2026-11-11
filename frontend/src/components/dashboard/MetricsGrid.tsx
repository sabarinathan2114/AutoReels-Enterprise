import React from "react";
import { Tv, Film, TrendingUp, Clock, CheckCircle } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { METRICS_DATA, DashboardMetric } from "../hardcodedata";

export function MetricsGrid() {
  const renderMetricIcon = (iconName: DashboardMetric["iconName"]) => {
    switch (iconName) {
      case "tv":
        return <Tv className="w-4 h-4 text-purple-400" />;
      case "film":
        return <Film className="w-4 h-4 text-purple-400" />;
      case "trending":
        return <TrendingUp className="w-4 h-4 text-emerald-400" />;
      case "clock":
        return <Clock className="w-4 h-4 text-purple-400" />;
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 w-full">
      {METRICS_DATA.map((metric: DashboardMetric) => (
        <GlassPanel key={metric.id} className="p-4 sm:p-5 space-y-1">
          <div className="flex items-center justify-between text-xs text-purple-300 font-medium">
            <span className="truncate pr-2">{metric.title}</span>
            {renderMetricIcon(metric.iconName)}
          </div>
          <div className="text-xl sm:text-2xl font-extrabold text-white truncate">
            {metric.value}
          </div>
          <div
            className={`text-[11px] flex items-center gap-1 truncate ${
              metric.isPositive ? "text-emerald-400" : "text-purple-400"
            }`}
          >
            {metric.iconName === "tv" && <CheckCircle className="w-3 h-3 flex-shrink-0" />}
            <span>{metric.changeLabel}</span>
          </div>
        </GlassPanel>
      ))}
    </div>
  );
}
