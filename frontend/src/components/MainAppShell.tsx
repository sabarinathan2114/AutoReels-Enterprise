"use client";

import React, { useState } from "react";
import { Header, NavTab } from "@/components/layout/Header";
import { LandingPageView } from "@/components/landing/LandingPageView";
import { StudioView } from "@/components/studio/StudioView";
import { DashboardView } from "@/components/dashboard/DashboardView";
import { LivePlanComparison } from "@/components/landing/LivePlanComparison";
import { Footer } from "@/components/landing/Footer";
import { CHANNELS_DATA } from "@/components/hardcodedata";

export function MainAppShell() {
  const [activeTab, setActiveTab] = useState<NavTab>("landing");
  const [selectedChannelId, setSelectedChannelId] = useState<string>(CHANNELS_DATA[0].id);

  return (
    <div className="min-h-screen cosmic-bg text-slate-100 flex flex-col w-full overflow-x-hidden selection:bg-purple-600 selection:text-white">
      {/* 🔮 Universal Responsive Header */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        selectedChannelId={selectedChannelId}
        onChannelChange={setSelectedChannelId}
      />

      {/* 🚀 Dynamic View Area (Strictly Responsive down to 320px) */}
      <main className="flex-1 w-full transition-all duration-300">
        {activeTab === "landing" && (
          <LandingPageView
            onEnterStudio={() => setActiveTab("studio")}
            onEnterDashboard={() => setActiveTab("dashboard")}
            onViewPlans={() => setActiveTab("plans")}
          />
        )}

        {activeTab === "studio" && (
          <div className="p-3 sm:p-5 md:p-6 max-w-7xl mx-auto w-full">
            <StudioView />
          </div>
        )}

        {activeTab === "dashboard" && (
          <div className="p-3 sm:p-5 md:p-6 max-w-7xl mx-auto w-full">
            <DashboardView />
          </div>
        )}

        {activeTab === "plans" && (
          <div className="w-full">
            <LivePlanComparison
              onSelectPlan={() => setActiveTab("studio")}
              onRequestUpgrade={(planId) => alert(`Request submitted for ${planId.toUpperCase()}! An admin will review your tier.`)}
            />
            <Footer onNavigate={(view) => setActiveTab(view)} />
          </div>
        )}
      </main>
    </div>
  );
}
