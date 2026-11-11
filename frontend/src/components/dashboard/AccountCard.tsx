import React from "react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { YoutubeIcon, InstagramIcon, FacebookIcon, TikTokIcon } from "../common/SocialIcons";
import { SocialAccountItem } from "../hardcodedata";

interface AccountCardProps {
  account: SocialAccountItem;
}

export function AccountCard({ account }: AccountCardProps) {
  const getIconContainer = (platform: SocialAccountItem["platform"]) => {
    switch (platform) {
      case "youtube":
        return {
          bg: "bg-red-600/20 border-red-500/40",
          icon: <YoutubeIcon className="w-5 h-5 text-red-500" />
        };
      case "instagram":
        return {
          bg: "bg-pink-600/20 border-pink-500/40",
          icon: <InstagramIcon className="w-5 h-5 text-pink-500" />
        };
      case "facebook":
        return {
          bg: "bg-blue-600/20 border-blue-500/40",
          icon: <FacebookIcon className="w-5 h-5 text-blue-500" />
        };
      case "tiktok":
        return {
          bg: "bg-cyan-600/20 border-cyan-500/40",
          icon: <TikTokIcon className="w-5 h-5 text-cyan-400" />
        };
    }
  };

  const { bg, icon } = getIconContainer(account.platform);

  return (
    <GlassPanel glow className="p-4 sm:p-5 space-y-4">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className={`w-9 h-9 rounded-xl border flex items-center justify-center flex-shrink-0 ${bg}`}>
            {icon}
          </div>
          <div className="min-w-0">
            <h4 className="text-xs sm:text-sm font-bold text-white truncate">{account.name}</h4>
            <span className="text-[10px] text-purple-300 block truncate">{account.apiName}</span>
          </div>
        </div>
        <Badge variant={account.status === "Active" ? "emerald" : "yellow"} className="flex-shrink-0">
          {account.status}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-purple-500/20">
        <div className="min-w-0">
          <span className="text-purple-400 text-[10px] block truncate">{account.metricLabel}</span>
          <span className="font-bold text-white text-xs sm:text-sm truncate block">{account.metricValue}</span>
        </div>
        <div className="min-w-0">
          <span className="text-purple-400 text-[10px] block truncate">{account.secondaryLabel}</span>
          <span className="font-bold text-white text-xs sm:text-sm truncate block">{account.secondaryValue}</span>
        </div>
      </div>
    </GlassPanel>
  );
}
