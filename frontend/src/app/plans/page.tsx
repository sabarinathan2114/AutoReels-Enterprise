"use client";

import { LivePlanComparison } from "@/components/landing/LivePlanComparison";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/landing/Footer";
import { CHANNELS_DATA } from "@/components/hardcodedata";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function PlansPage() {
  const router = useRouter();
  const [selectedChannelId, setSelectedChannelId] = useState<string>(CHANNELS_DATA[0].id);

  return (
    <div className="min-h-screen cosmic-bg text-slate-100 flex flex-col w-full overflow-x-hidden">
      <Header
        activeTab="plans"
        onTabChange={(tab) => {
          if (tab === "landing") router.push("/");
          else if (tab === "studio") router.push("/");
          else if (tab === "dashboard") router.push("/");
        }}
        selectedChannelId={selectedChannelId}
        onChannelChange={setSelectedChannelId}
      />
      <main className="flex-1 w-full">
        <LivePlanComparison
          onSelectPlan={() => router.push("/")}
          onRequestUpgrade={(planId) => alert(`Upgrade request submitted for ${planId.toUpperCase()}!`)}
        />
      </main>
      <Footer onNavigate={(tab) => router.push("/")} />
    </div>
  );
}
