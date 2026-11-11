import React from "react";
import { Layers, Image as ImageIcon } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { CosmicSelect } from "../common/FormControls";
import { SceneCard } from "./SceneCard";
import { SceneItem, BGM_TRACKS } from "../hardcodedata";

interface SceneTimelineProps {
  scenes: SceneItem[];
  onRegenerateScene: (sceneId: number) => Promise<void> | void;
  selectedBgm: string;
  onBgmChange: (bgm: string) => void;
  duckingLevel: number;
  onDuckingChange: (val: number) => void;
}

export function SceneTimeline({
  scenes,
  onRegenerateScene,
  selectedBgm,
  onBgmChange,
  duckingLevel,
  onDuckingChange
}: SceneTimelineProps) {
  return (
    <GlassPanel className="p-3.5 sm:p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-purple-500/20">
        <div className="flex items-center gap-2 min-w-0">
          <Layers className="w-4 h-4 text-purple-400 flex-shrink-0" />
          <h2 className="text-xs sm:text-sm font-semibold tracking-wider text-purple-200 uppercase truncate">
            2. Visual Scenes & Timeline
          </h2>
        </div>
        <div className="flex items-center gap-1.5">
          <Badge variant="purple">{scenes.length} Scenes (9:16)</Badge>
        </div>
      </div>

      {/* Image Ladder Indicator (AutoReels v2.0 Section 15.2) */}
      <div className="p-2 rounded-xl bg-purple-950/40 border border-purple-500/20 flex items-center justify-between text-[11px] text-purple-300">
        <div className="flex items-center gap-1.5">
          <ImageIcon className="w-3.5 h-3.5 text-purple-400" />
          <span>Image Ladder: <strong>1. Free Stock $\to$ 2. Flux AI</strong></span>
        </div>
        <span className="text-[10px] text-emerald-400 font-mono">Zero Cash Spend</span>
      </div>

      {/* Scrollable Scene Cards */}
      <div className="space-y-3 max-h-[440px] sm:max-h-[500px] overflow-y-auto pr-1">
        {scenes.map((scene, idx) => (
          <SceneCard
            key={scene.scene_id}
            scene={scene}
            index={idx}
            onRegenerate={onRegenerateScene}
          />
        ))}
      </div>

      {/* BGM & Ducking Controls */}
      <div className="pt-3 border-t border-purple-500/20 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <div>
          <CosmicSelect
            label="Background Score"
            value={selectedBgm}
            onChange={(e) => onBgmChange(e.target.value)}
          >
            {BGM_TRACKS.map((track) => (
              <option key={track.id} value={track.id} className="bg-[#0b0814]">
                {track.name} ({track.genre})
              </option>
            ))}
          </CosmicSelect>
        </div>

        <div className="space-y-1">
          <div className="flex items-center justify-between text-purple-300">
            <span>Speech Ducking</span>
            <span className="text-purple-400 font-mono font-bold">{duckingLevel}%</span>
          </div>
          <input
            type="range"
            min="30"
            max="100"
            value={duckingLevel}
            onChange={(e) => onDuckingChange(Number(e.target.value))}
            className="w-full accent-purple-500 cursor-pointer h-2 bg-purple-950/80 rounded-lg"
          />
          <span className="text-[10px] text-purple-400/70 block">
            Auto-lowers BGM by {Math.round((100 - duckingLevel) * 0.3)}dB when voice speaks
          </span>
        </div>
      </div>
    </GlassPanel>
  );
}
