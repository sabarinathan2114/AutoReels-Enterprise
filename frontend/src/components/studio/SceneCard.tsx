import React, { useState } from "react";
import { RefreshCw } from "lucide-react";
import { SceneItem } from "../hardcodedata";

interface SceneCardProps {
  scene: SceneItem;
  index: number;
  onRegenerate: (sceneId: number) => Promise<void> | void;
}

export function SceneCard({ scene, index, onRegenerate }: SceneCardProps) {
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleRegenClick = async () => {
    setIsRegenerating(true);
    try {
      await onRegenerate(scene.scene_id);
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <div className="p-2.5 sm:p-3 rounded-xl bg-purple-950/30 border border-purple-500/20 hover:border-purple-400/40 transition-all flex flex-col sm:flex-row gap-2.5 sm:gap-3.5 items-stretch sm:items-center">
      {/* 9:16 Thumbnail Container */}
      <div className="relative w-full sm:w-20 h-32 sm:h-28 rounded-lg overflow-hidden flex-shrink-0 bg-purple-900/50 border border-purple-500/30">
        {scene.image_url ? (
          <img
            src={scene.image_url}
            alt={`Scene ${scene.scene_id}`}
            className="w-full h-full object-cover transition-opacity duration-300"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[10px] text-purple-300">
            9:16 Visual
          </div>
        )}
        <span className="absolute bottom-1 left-1 bg-black/75 text-[9px] font-mono px-1.5 py-0.5 rounded text-purple-200">
          0:0{index * 4}s
        </span>
      </div>

      {/* Scene Prompt & Subtitle */}
      <div className="flex-1 space-y-1.5 min-w-0">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-purple-200 truncate">
            Scene {scene.scene_id} ({scene.duration_sec}s)
          </span>
          <button
            onClick={handleRegenClick}
            disabled={isRegenerating}
            className="text-[10px] text-purple-400 hover:text-purple-200 flex items-center gap-1 flex-shrink-0 py-0.5 px-1.5 rounded hover:bg-purple-900/40 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${isRegenerating ? "animate-spin text-purple-300" : ""}`} />
            <span>{isRegenerating ? "Generating AI..." : "Regen"}</span>
          </button>
        </div>
        <p className="text-[11px] text-purple-300/80 line-clamp-2 leading-relaxed break-words">
          {scene.visual_prompt}
        </p>
        <div className="bg-black/40 px-2 py-1 rounded text-[10px] text-yellow-300/90 font-mono truncate">
          💬 &ldquo;{scene.subtitles}&rdquo;
        </div>
      </div>
    </div>
  );
}
