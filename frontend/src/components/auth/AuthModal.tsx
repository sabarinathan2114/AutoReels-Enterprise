"use client";

import React, { useState } from "react";
import { X, Lock, Mail, User as UserIcon, ShieldCheck, Sparkles } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { CosmicButton } from "../common/CosmicButton";
import { AuthStorage, AuthUserData } from "../common/authStorage";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: AuthUserData) => void;
}

export function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setIsLoading(true);

    const endpoint = isLogin
      ? "http://localhost:8000/api/auth/login"
      : "http://localhost:8000/api/auth/register";

    const payload = isLogin
      ? { email, password }
      : { email, password, full_name: fullName || "Creator" };

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Authentication failed");
      }

      // Store JWT token and user profile into Session Storage as requested!
      AuthStorage.saveSession(data.access_token, data.user);
      onSuccess(data.user);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg("Failed to connect to authentication service.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-md">
        <GlassPanel glow className="p-5 sm:p-7 relative border-purple-500/40">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1 rounded-lg text-purple-300 hover:text-white hover:bg-purple-900/40"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Modal Header */}
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-fuchsia-600 flex items-center justify-center shadow-[0_0_20px_rgba(139,92,246,0.6)] flex-shrink-0">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">
                {isLogin ? "Creator Portal Sign In" : "Create Studio Account"}
              </h3>
              <p className="text-[11px] text-purple-300/80">
                JWT Authenticated &bull; Bcrypt Salt-Hashed
              </p>
            </div>
          </div>

          {/* Tab Switcher */}
          <div className="flex bg-purple-950/60 p-1 rounded-xl mb-4 border border-purple-500/20 text-xs">
            <button
              type="button"
              onClick={() => {
                setIsLogin(true);
                setErrorMsg("");
              }}
              className={`flex-1 py-1.5 rounded-lg font-medium transition-all ${
                isLogin ? "btn-cosmic text-white font-bold" : "text-purple-300 hover:text-white"
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setIsLogin(false);
                setErrorMsg("");
              }}
              className={`flex-1 py-1.5 rounded-lg font-medium transition-all ${
                !isLogin ? "btn-cosmic text-white font-bold" : "text-purple-300 hover:text-white"
              }`}
            >
              Register
            </button>
          </div>

          {/* Error Message Alert */}
          {errorMsg && (
            <div className="mb-4 p-2.5 rounded-xl bg-red-950/70 border border-red-500/40 text-red-200 text-xs">
              {errorMsg}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
            {!isLogin && (
              <div className="space-y-1">
                <label className="text-purple-300 block font-medium">Full Name</label>
                <div className="relative">
                  <UserIcon className="w-4 h-4 text-purple-400 absolute left-3 top-3 pointer-events-none" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Alex Johnson"
                    className="w-full glass-panel pl-9 pr-3 py-2.5 rounded-xl border border-purple-500/30 text-white focus:outline-none focus:border-purple-400 text-xs"
                  />
                </div>
              </div>
            )}

            <div className="space-y-1">
              <label className="text-purple-300 block font-medium">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-purple-400 absolute left-3 top-3 pointer-events-none" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="creator@example.com"
                  className="w-full glass-panel pl-9 pr-3 py-2.5 rounded-xl border border-purple-500/30 text-white focus:outline-none focus:border-purple-400 text-xs"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-purple-300 block font-medium">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-purple-400 absolute left-3 top-3 pointer-events-none" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full glass-panel pl-9 pr-3 py-2.5 rounded-xl border border-purple-500/30 text-white focus:outline-none focus:border-purple-400 text-xs"
                />
              </div>
              <span className="text-[10px] text-purple-400/70 block">
                Stored as 12-round salted bcrypt hash
              </span>
            </div>

            <CosmicButton
              type="submit"
              isLoading={isLoading}
              icon={<Sparkles className="w-4 h-4" />}
              className="w-full py-3 mt-2 text-xs sm:text-sm font-bold"
            >
              {isLogin ? "Sign In to Studio" : "Create Account & Save Session"}
            </CosmicButton>
          </form>
        </GlassPanel>
      </div>
    </div>
  );
}
