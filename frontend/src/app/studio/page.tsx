"use client";

import { StudioView } from "@/components/studio/StudioView";
import { Header } from "@/components/layout/Header";
import { CHANNELS_DATA } from "@/components/hardcodedata";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function StudioPage() {
  const router = useRouter();
  const [selectedChannelId, setSelectedChannelId] = useState<string>(CHANNELS_DATA[0].id);

  return (
    <div className="min-h-screen cosmic-bg text-slate-100 flex flex-col w-full overflow-x-hidden">
      <Header
        activeTab="studio"
        onTabChange={(tab) => {
          if (tab === "landing") router.push("/");
          else if (tab === "plans") router.push("/plans");
          else if (tab === "dashboard") router.push("/dashboard");
        }}
        selectedChannelId={selectedChannelId}
        onChannelChange={setSelectedChannelId}
      />
      <main className="flex-1 p-3 sm:p-5 md:p-6 max-w-7xl mx-auto w-full">
        <StudioView />
      </main>
    </div>
  );
}
