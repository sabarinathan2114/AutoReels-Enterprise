"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Film, Sparkles, LayoutDashboard, Compass, CreditCard, LogOut, LogIn, UserCheck, ShieldAlert } from "lucide-react";
import { CHANNELS_DATA, ChannelProfile } from "../hardcodedata";
import { CosmicSelect } from "../common/FormControls";
import { AuthStorage, AuthUserData } from "../common/authStorage";
import { AuthModal } from "../auth/AuthModal";
import { Badge } from "../common/Badge";

export type NavTab = "landing" | "studio" | "dashboard" | "plans";

interface HeaderProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  selectedChannelId: string;
  onChannelChange: (channelId: string) => void;
}

export function Header({
  activeTab,
  onTabChange,
  selectedChannelId,
  onChannelChange
}: HeaderProps) {
  const [user, setUser] = useState<AuthUserData | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  useEffect(() => {
    const savedUser = AuthStorage.getUser();
    if (savedUser) {
      setUser(savedUser);
    }
  }, []);

  const handleLogout = () => {
    AuthStorage.clearSession();
    setUser(null);
  };

  return (
    <>
      <header className="sticky top-0 z-40 glass-panel border-b border-purple-500/20 px-3 sm:px-6 py-2.5 sm:py-3.5 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 backdrop-blur-xl bg-black/70">
        {/* Brand & Title */}
        <div className="flex items-center justify-between w-full md:w-auto">
          <div
            onClick={() => onTabChange("landing")}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-violet-600 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-[0_0_20px_rgba(139,92,246,0.6)] flex-shrink-0 group-hover:scale-105 transition-transform">
              <Film className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <div className="min-w-0">
              <span className="text-base sm:text-xl font-bold tracking-tight text-gradient truncate block">
                AUTOREELS ENTERPRISE
              </span>
              <span className="text-[10px] sm:text-xs block text-purple-400/80 font-mono truncate">
                Master Build v2.0 (Free-First)
              </span>
            </div>
          </div>

          {/* User Profile / Auth Button (Mobile) */}
          <div className="md:hidden flex items-center gap-1.5">
            {user ? (
              <button
                onClick={handleLogout}
                className="p-2 rounded-xl bg-purple-900/40 border border-purple-500/30 text-purple-200"
                title="Log Out"
              >
                <LogOut className="w-3.5 h-3.5 text-red-400" />
              </button>
            ) : (
              <button
                onClick={() => setIsAuthModalOpen(true)}
                className="px-2.5 py-1.5 rounded-xl btn-cosmic text-xs font-semibold flex items-center gap-1"
              >
                <LogIn className="w-3 h-3" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>

        {/* Center Tab Navigation (Scrollable on 320px) */}
        <nav className="flex items-center gap-1 bg-purple-950/40 p-1 rounded-full border border-purple-500/20 overflow-x-auto max-w-full flex-shrink-0 self-center md:self-auto scrollbar-none">
          <button
            onClick={() => onTabChange("landing")}
            className={`flex items-center gap-1 sm:gap-1.5 px-3 sm:px-4 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap ${
              activeTab === "landing"
                ? "btn-cosmic text-white font-semibold"
                : "text-purple-300 hover:text-white"
            }`}
          >
            <Compass className="w-3.5 h-3.5 flex-shrink-0" />
            <span>Overview</span>
          </button>
          <button
            onClick={() => onTabChange("studio")}
            className={`flex items-center gap-1 sm:gap-1.5 px-3 sm:px-4 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap ${
              activeTab === "studio"
                ? "btn-cosmic text-white font-semibold"
                : "text-purple-300 hover:text-white"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 flex-shrink-0 text-amber-300" />
            <span>Studio Creator</span>
          </button>
          <button
            onClick={() => onTabChange("dashboard")}
            className={`flex items-center gap-1 sm:gap-1.5 px-3 sm:px-4 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap ${
              activeTab === "dashboard"
                ? "btn-cosmic text-white font-semibold"
                : "text-purple-300 hover:text-white"
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5 flex-shrink-0" />
            <span>Accounts & Stats</span>
          </button>
          <button
            onClick={() => onTabChange("plans")}
            className={`flex items-center gap-1 sm:gap-1.5 px-3 sm:px-4 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap ${
              activeTab === "plans"
                ? "btn-cosmic text-white font-semibold"
                : "text-purple-300 hover:text-white"
            }`}
          >
            <CreditCard className="w-3.5 h-3.5 flex-shrink-0 text-emerald-400" />
            <span>Plans</span>
          </button>
          <Link
            href="/admin"
            className="flex items-center gap-1 sm:gap-1.5 px-3 sm:px-4 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap text-purple-300 hover:text-white hover:bg-purple-900/30"
          >
            <ShieldAlert className="w-3.5 h-3.5 flex-shrink-0 text-fuchsia-400" />
            <span>Admin</span>
          </Link>
        </nav>

        {/* Right Section: Channel Switcher & Desktop Auth */}
        <div className="flex items-center gap-2 w-full md:w-auto">
          <div className="flex-1 md:w-52 min-w-0">
            <CosmicSelect
              value={selectedChannelId}
              onChange={(e) => onChannelChange(e.target.value)}
            >
              {CHANNELS_DATA.map((ch: ChannelProfile) => (
                <option key={ch.id} value={ch.id} className="bg-[#0b0814] text-white">
                  {ch.avatar} {ch.name}
                </option>
              ))}
            </CosmicSelect>
          </div>

          {/* Desktop Auth Status */}
          <div className="hidden md:flex items-center gap-2 flex-shrink-0">
            {user ? (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-purple-950/60 border border-purple-500/30">
                <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-xs text-purple-200 font-medium max-w-[100px] truncate">
                  {user.email.split("@")[0]}
                </span>
                <Badge variant="purple" className="text-[10px] py-0 px-1.5">Free</Badge>
                <button
                  onClick={handleLogout}
                  className="text-purple-400 hover:text-red-400 p-0.5 ml-1"
                  title="Log out"
                >
                  <LogOut className="w-3 h-3" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsAuthModalOpen(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl btn-cosmic text-xs font-semibold"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={(loggedUser) => setUser(loggedUser)}
      />
    </>
  );
}
