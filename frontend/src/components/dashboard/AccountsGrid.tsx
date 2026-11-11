import React from "react";
import { Plus } from "lucide-react";
import { CosmicButton } from "../common/CosmicButton";
import { AccountCard } from "./AccountCard";
import { SOCIAL_ACCOUNTS_DATA, SocialAccountItem } from "../hardcodedata";

export function AccountsGrid() {
  return (
    <div className="space-y-3 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <h3 className="text-xs sm:text-sm font-bold text-purple-200 tracking-wide uppercase">
          Connected Social Account Holders
        </h3>
        <CosmicButton
          size="sm"
          onClick={() => alert("Initiating OAuth connection flow for new channel...")}
          icon={<Plus className="w-3.5 h-3.5" />}
          className="self-start sm:self-auto"
        >
          Connect Platform
        </CosmicButton>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 w-full">
        {SOCIAL_ACCOUNTS_DATA.map((acc: SocialAccountItem) => (
          <AccountCard key={acc.id} account={acc} />
        ))}
      </div>
    </div>
  );
}
