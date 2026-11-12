"use client";

import React, { useState } from "react";
import { Sparkles, ArrowRight, Check, X, Film, Mic, User } from "lucide-react";
import { GlassPanel } from "@/components/common/GlassPanel";
import { CosmicButton } from "@/components/common/CosmicButton";
import { Badge } from "@/components/common/Badge";
import { NICHES_DATA, VOICES_DATA } from "@/components/hardcodedata";

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (data: { studioName: string; niche: string; voice: string }) => void;
}

export const OnboardingModal: React.FC<OnboardingModalProps> = ({
  isOpen,
  onClose,
  onComplete
}) => {
  const [step, setStep] = useState<number>(1);
  const [studioName, setStudioName] = useState<string>("My Viral Studio");
  const [selectedNiche, setSelectedNiche] = useState<string>(NICHES_DATA[0].id);
  const [selectedVoice, setSelectedVoice] = useState<string>(VOICES_DATA[0].id);

  if (!isOpen) return null;

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      onComplete({
        studioName,
        niche: selectedNiche,
        voice: selectedVoice
      });
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <GlassPanel className="relative w-full max-w-lg p-5 sm:p-7 border-purple-500/40 shadow-2xl shadow-purple-950/80">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Step Progress Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <Badge variant="purple" className="text-xs">Step {step} of 3</Badge>
            <span className="text-xs text-purple-300 font-semibold">Free Onboarding</span>
          </div>
          <div className="w-full h-1.5 bg-purple-950/60 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full transition-all duration-300"
              style={{ width: `${(step / 3) * 100}%` }}
            />
          </div>
        </div>

        {/* Step 1: Workspace & Studio Identity */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="text-left">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Film className="w-5 h-5 text-purple-400" />
                Name Your Studio Workspace
              </h3>
              <p className="text-xs sm:text-sm text-slate-400 mt-1">
                Your workspace will hold your video drafts, social channel integrations, and free monthly quota.
              </p>
            </div>

            <div className="space-y-2 text-left">
              <label className="text-xs font-semibold text-slate-300">Workspace / Channel Name</label>
              <input
                type="text"
                value={studioName}
                onChange={(e) => setStudioName(e.target.value)}
                placeholder="e.g. Daily Facts Studio"
                className="w-full px-3.5 py-2.5 rounded-xl bg-purple-950/30 border border-purple-500/30 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400"
              />
            </div>

            <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-xs text-emerald-300 flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Default Free Plan initialized: 2 video renders included per month.</span>
            </div>
          </div>
        )}

        {/* Step 2: Content Niche Selection */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="text-left">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-pink-400" />
                Select Your Content Niche
              </h3>
              <p className="text-xs sm:text-sm text-slate-400 mt-1">
                Choose the primary style for your autonomous scripts and visuals.
              </p>
            </div>

            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {NICHES_DATA.map((n) => (
                <div
                  key={n.id}
                  onClick={() => setSelectedNiche(n.id)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all text-left ${
                    selectedNiche === n.id
                      ? "bg-purple-950/60 border-purple-400 shadow-md shadow-purple-950"
                      : "bg-black/30 border-purple-900/30 hover:border-purple-600/40"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">{n.title}</span>
                    {selectedNiche === n.id && (
                      <Check className="w-4 h-4 text-purple-400" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">{n.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Default Neural Voice Selection */}
        {step === 3 && (
          <div className="space-y-4">
            <div className="text-left">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Mic className="w-5 h-5 text-amber-400" />
                Pick Your Primary Neural Voice
              </h3>
              <p className="text-xs sm:text-sm text-slate-400 mt-1">
                Synthesized at zero cost with word-level kinetic subtitle markers.
              </p>
            </div>

            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {VOICES_DATA.map((v) => (
                <div
                  key={v.id}
                  onClick={() => setSelectedVoice(v.id)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all text-left flex items-center justify-between ${
                    selectedVoice === v.id
                      ? "bg-purple-950/60 border-purple-400 shadow-md shadow-purple-950"
                      : "bg-black/30 border-purple-900/30 hover:border-purple-600/40"
                  }`}
                >
                  <div>
                    <span className="text-sm font-bold text-white">{v.name}</span>
                    <p className="text-[11px] text-purple-300">
                      {v.language} • {v.gender}
                    </p>
                  </div>
                  {selectedVoice === v.id && (
                    <Check className="w-4 h-4 text-purple-400" />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer Navigation */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-purple-900/30">
          {step > 1 ? (
            <CosmicButton
              variant="outline"
              size="sm"
              onClick={() => setStep(step - 1)}
              className="text-xs"
            >
              Back
            </CosmicButton>
          ) : <div />}

          <CosmicButton
            variant="primary"
            size="sm"
            onClick={handleNext}
            className="text-xs font-semibold px-5"
          >
            <span>{step === 3 ? "Enter Studio Creator" : "Continue"}</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
          </CosmicButton>
        </div>
      </GlassPanel>
    </div>
  );
};
