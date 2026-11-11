"use client";

import React, { useState } from "react";
import { Header } from "@/components/layout/Header";
import { StudioView } from "@/components/studio/StudioView";
import { DashboardView } from "@/components/dashboard/DashboardView";
import { CHANNELS_DATA } from "@/components/hardcodedata";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"studio" | "dashboard" | "channels">("studio");
  const [selectedChannelId, setSelectedChannelId] = useState<string>(CHANNELS_DATA[0].id);

  return (
    <div className="min-h-screen cosmic-bg text-slate-100 flex flex-col w-full overflow-x-hidden">
      {/* 🔮 Universal Responsive Header */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        selectedChannelId={selectedChannelId}
        onChannelChange={setSelectedChannelId}
      />

      {/* 🚀 Dynamic View Area (Responsive down to 320px) */}
      <main className="flex-1 p-3 sm:p-5 md:p-6 max-w-7xl mx-auto w-full transition-all duration-300">
        {activeTab === "studio" && <StudioView />}
        {activeTab === "dashboard" && <DashboardView />}
      </main>
    </div>
  );
}
