import React, { useState } from "react";
import { Sparkles, Volume2, ShieldCheck, SlidersHorizontal, Flame, Gauge } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { CosmicButton } from "../common/CosmicButton";
import { CosmicSelect, CosmicTextarea } from "../common/FormControls";
import { NICHES_DATA, VOICES_DATA, PLANS_DATA, PlanTier } from "../hardcodedata";
import { CURATED_VIRAL_TRENDS, HOOK_FORMULAS } from "../hardcodedata/pipeline";

interface StoryDirectorProps {
  niche: string;
  onNicheChange: (val: string) => void;
  topic: string;
  onTopicChange: (val: string) => void;
  selectedVoice: string;
  onVoiceChange: (val: string) => void;
  isGenerating: boolean;
  onGenerate: () => void;
  narrationScript: string;
  onNarrationChange: (val: string) => void;
  activePlanId: string;
  onPlanChange: (planId: string) => void;
  audioUrl?: string;
}

export function StoryDirector({
  niche,
  onNicheChange,
  topic,
  onTopicChange,
  selectedVoice,
  onVoiceChange,
  isGenerating,
  onGenerate,
  narrationScript,
  onNarrationChange,
  activePlanId,
  onPlanChange,
  audioUrl
}: StoryDirectorProps) {
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [directorMode, setDirectorMode] = useState<"zero_input" | "director">("director");
  const [hookFormula, setHookFormula] = useState("curiosity_gap");

  const wordCount = narrationScript.trim() ? narrationScript.trim().split(/\s+/).length : 0;
  const estimatedSeconds = Math.max(3, Math.round(wordCount / 2.5));
  const wpm = estimatedSeconds > 0 ? Math.round((wordCount / (estimatedSeconds / 60))) : 0;
  const isPacingOptimal = wpm >= 120 && wpm <= 175;

  const handlePreviewVoice = async () => {
    setIsPlayingAudio(true);
    try {
      // Real API call to synthesize voice sample if audioUrl is not ready
      let playUrl = audioUrl;
      if (!playUrl) {
        const res = await fetch("http://localhost:8000/api/voice/synthesize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: narrationScript.slice(0, 100) || "வணக்கம்! இது உங்கள் முதல் தானியங்கி ரீல்ஸ் வீடியோ.",
            voice: selectedVoice,
            filename: `preview_${selectedVoice}.mp3`
          })
        });
        if (res.ok) {
          const data = await res.json();
          playUrl = data.url;
        }
      }

      if (playUrl) {
        const audio = new Audio(playUrl);
        audio.onended = () => setIsPlayingAudio(false);
        audio.onerror = () => setIsPlayingAudio(false);
        await audio.play();
      } else {
        setIsPlayingAudio(false);
      }
    } catch (e) {
      console.error("Audio playback error:", e);
      setIsPlayingAudio(false);
    }
  };

  return (
    <GlassPanel className="p-3.5 sm:p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-purple-500/20">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-2 h-2 rounded-full bg-violet-400 animate-pulse flex-shrink-0" />
          <h2 className="text-xs sm:text-sm font-semibold tracking-wider text-purple-200 uppercase truncate">
            1. Story & AI Director
          </h2>
        </div>
        
        {/* Plan Tier Selector */}
        <div className="flex items-center gap-1.5">
          <select
            value={activePlanId}
            onChange={(e) => onPlanChange(e.target.value)}
            className="bg-purple-950/80 border border-purple-500/40 text-purple-200 text-[10px] sm:text-xs rounded-lg px-2 py-0.5 focus:outline-none"
          >
            {PLANS_DATA.map((p: PlanTier) => (
              <option key={p.id} value={p.id} className="bg-[#0b0814]">
                {p.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Mode Switcher (Zero-Input vs Director Mode per AutoReels v2.0) */}
      <div className="flex bg-purple-950/60 p-1 rounded-xl border border-purple-500/20 text-xs">
        <button
          type="button"
          onClick={() => setDirectorMode("zero_input")}
          className={`flex-1 py-1.5 rounded-lg font-medium transition-all text-center ${
            directorMode === "zero_input"
              ? "btn-cosmic text-white font-bold"
              : "text-purple-300 hover:text-white"
          }`}
        >
          ⚡ Auto-Pilot
        </button>
        <button
          type="button"
          onClick={() => setDirectorMode("director")}
          className={`flex-1 py-1.5 rounded-lg font-medium transition-all text-center ${
            directorMode === "director"
              ? "btn-cosmic text-white font-bold"
              : "text-purple-300 hover:text-white"
          }`}
        >
          🎬 Director Mode
        </button>
      </div>

      {/* Story Mode / Niche */}
      <CosmicSelect
        label="Story Mode / Domain"
        value={niche}
        onChange={(e) => onNicheChange(e.target.value)}
      >
        {NICHES_DATA.map((n) => (
          <option key={n.id} value={n.id} className="bg-[#0b0814] text-white">
            {n.title}
          </option>
        ))}
      </CosmicSelect>

      {/* Trend Radar Chips */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-[11px] text-purple-300">
          <span className="flex items-center gap-1 font-semibold text-purple-200">
            <Flame className="w-3.5 h-3.5 text-amber-400" />
            Trend Radar (Zero Scraping)
          </span>
          <span className="text-[10px] text-purple-400">Viral Velocity</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {CURATED_VIRAL_TRENDS.map((tr) => (
            <button
              key={tr.id}
              type="button"
              onClick={() => onTopicChange(tr.title)}
              className="px-2 py-1 bg-purple-950/70 hover:bg-purple-900/80 border border-purple-500/30 hover:border-purple-400 rounded-lg text-[10px] text-purple-200 hover:text-white transition-all text-left flex items-center gap-1.5"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span className="truncate max-w-[200px]">{tr.title}</span>
              <span className="text-amber-400 font-mono text-[9px]">{(tr.velocity_score * 100).toFixed(0)}%</span>
            </button>
          ))}
        </div>
      </div>

      {/* Topic Prompt */}
      <CosmicTextarea
        label="Topic or Story Premise"
        value={topic}
        onChange={(e) => onTopicChange(e.target.value)}
        rows={3}
        placeholder="Enter your story idea..."
      />

      {/* Hook Formula Selector */}
      <CosmicSelect
        label="Hook Strategy Formula"
        hint={<span className="text-purple-400">3-Act Retention</span>}
        value={hookFormula}
        onChange={(e) => setHookFormula(e.target.value)}
      >
        {HOOK_FORMULAS.map((h) => (
          <option key={h.id} value={h.id} className="bg-[#0b0814] text-white">
            {h.label} — {h.desc}
          </option>
        ))}
      </CosmicSelect>

      {/* Voice Synthesizer */}
      <CosmicSelect
        label="Voice Synthesis (Edge-TTS Free)"
        hint={<span className="text-emerald-400">Zero Cost</span>}
        value={selectedVoice}
        onChange={(e) => onVoiceChange(e.target.value)}
      >
        {VOICES_DATA.map((v) => (
          <option key={v.id} value={v.id} className="bg-[#0b0814] text-white">
            {v.name}
          </option>
        ))}
      </CosmicSelect>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-2 pt-1">
        <CosmicButton
          onClick={onGenerate}
          isLoading={isGenerating}
          icon={<Sparkles className="w-3.5 h-3.5" />}
          className="flex-1 w-full"
        >
          {isGenerating ? "Synthesizing Script & Audio..." : "Generate Script & Voice"}
        </CosmicButton>

        <CosmicButton
          variant="outline"
          onClick={handlePreviewVoice}
          isLoading={isPlayingAudio}
          icon={<Volume2 className="w-3.5 h-3.5 text-purple-400" />}
          className="w-full sm:w-auto"
        >
          {isPlayingAudio ? "Playing Audio..." : "Preview Audio"}
        </CosmicButton>
      </div>

      {/* Script Textarea */}
      <div className="pt-2">
        <div className="flex items-center justify-between pb-1 text-xs">
          <span className="text-purple-200 font-medium">Full Narration Script</span>
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
            isPacingOptimal
              ? "text-emerald-300 border-emerald-500/40 bg-emerald-950/40"
              : "text-amber-300 border-amber-500/40 bg-amber-950/40"
          }`}>
            {wpm} WPM {isPacingOptimal ? "✓ Optimal Pacing" : "• Adjust Length"} (~{estimatedSeconds}s)
          </span>
        </div>
        <CosmicTextarea
          value={narrationScript}
          onChange={(e) => onNarrationChange(e.target.value)}
          rows={5}
        />
      </div>
    </GlassPanel>
  );
}
