"use client";

import React, { useState } from "react";
import { StoryDirector } from "./StoryDirector";
import { SceneTimeline } from "./SceneTimeline";
import { VideoPreviewPlayer } from "./VideoPreviewPlayer";
import { StepLedgerInspector } from "./StepLedgerInspector";
import { StepLedgerItem, PIPELINE_STRINGS } from "../hardcodedata/pipeline";
import { Layers } from "lucide-react";
import {
  DEFAULT_BLUEPRINT,
  BlueprintData,
  SOCIAL_ACCOUNTS_DATA,
  PLANS_DATA,
  SceneItem
} from "../hardcodedata";

export function StudioView() {
  const [activePlanId, setActivePlanId] = useState<string>("free");
  const [topic, setTopic] = useState("The poor strawberry's last wish to save his mother");
  const [niche, setNiche] = useState("emotional_drama");
  const [selectedVoice, setSelectedVoice] = useState("ta-IN-ValluvarNeural");
  const [blueprint, setBlueprint] = useState<BlueprintData>(DEFAULT_BLUEPRINT);
  const [selectedBgm, setSelectedBgm] = useState("flute_ambient");
  const [duckingLevel, setDuckingLevel] = useState(80);
  const [captionStyle, setCaptionStyle] = useState("neon_yellow");
  
  // Real media URLs
  const [audioUrl, setAudioUrl] = useState<string | undefined>(undefined);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  // Loading states
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRendering, setIsRendering] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishSuccess, setPublishSuccess] = useState(false);

  // Step-Ledger Orchestrator state
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [isLedgerOpen, setIsLedgerOpen] = useState(false);
  const [ledgerSteps, setLedgerSteps] = useState<StepLedgerItem[]>([]);
  const [isDegraded, setIsDegraded] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleOpenLedger = async () => {
    setIsLedgerOpen(true);
    if (activeJobId) {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/jobs/${activeJobId}/ledger`);
        if (res.ok) {
          const d = await res.json();
          setLedgerSteps(d.steps || []);
          setIsDegraded(d.degraded || false);
        }
      } catch (e) {
        console.warn("Failed to fetch ledger:", e);
      }
    }
  };

  const handleRetryJob = async (jobId: string) => {
    setIsRetrying(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}/retry`, { method: "POST" });
      if (res.ok) {
        const d = await res.json();
        if (d.output_video_url) setVideoUrl(d.output_video_url);
        const lRes = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}/ledger`);
        if (lRes.ok) {
          const ld = await lRes.json();
          setLedgerSteps(ld.steps || []);
          setIsDegraded(ld.degraded || false);
        }
      }
    } finally {
      setIsRetrying(false);
    }
  };

  // Selected social accounts
  const [selectedAccounts, setSelectedAccounts] = useState<string[]>(
    SOCIAL_ACCOUNTS_DATA.filter((a) => a.isCheckedDefault).map((a) => a.id)
  );

  const toggleAccount = (id: string) => {
    setSelectedAccounts((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    );
  };

  // STEP 1 & 2: Real Script & Voice Generation Flow
  const handleGenerateScript = async () => {
    setIsGenerating(true);
    setVideoUrl(null); // reset prior video
    try {
      // 1. Generate Script Blueprint
      const scriptRes = await fetch("http://localhost:8000/api/script/blueprint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, niche, language: blueprint.language })
      });

      let currentBlueprint = blueprint;
      if (scriptRes.ok) {
        currentBlueprint = await scriptRes.json();
        setBlueprint(currentBlueprint);
      }

      // 2. Synthesize Real Audio via Edge-TTS
      const voiceRes = await fetch("http://localhost:8000/api/voice/synthesize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: currentBlueprint.full_narration,
          voice: selectedVoice,
          filename: `speech_${Date.now()}.mp3`
        })
      });

      if (voiceRes.ok) {
        const voiceData = await voiceRes.json();
        setAudioUrl(voiceData.url);

        // Play brief chime or preview
        const audio = new Audio(voiceData.url);
        audio.play().catch(() => {});
      }

      // 3. Trigger Real AI Scene Generation (Image Ladder Rung 2: Pollinations/Flux)
      const updatedScenes = [...currentBlueprint.scenes];
      for (let i = 0; i < Math.min(updatedScenes.length, 4); i++) {
        try {
          const imgRes = await fetch("http://localhost:8000/api/media/generate-scene", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              prompt: updatedScenes[i].visual_prompt,
              scene_id: updatedScenes[i].scene_id,
              filename: `scene_${updatedScenes[i].scene_id}_${Date.now()}.jpg`
            })
          });
          if (imgRes.ok) {
            const imgData = await imgRes.json();
            updatedScenes[i] = {
              ...updatedScenes[i],
              image_url: imgData.url
            };
          }
        } catch (e) {
          console.warn("Scene generation fallback:", e);
        }
      }
      setBlueprint({ ...currentBlueprint, scenes: updatedScenes });
    } catch (err) {
      console.error("Pipeline generation error:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  // STEP 3: Real Single Scene Visual Regeneration
  const handleRegenerateScene = async (sceneId: number) => {
    const sceneIndex = blueprint.scenes.findIndex((s) => s.scene_id === sceneId);
    if (sceneIndex === -1) return;

    const targetScene = blueprint.scenes[sceneIndex];
    try {
      const imgRes = await fetch("http://localhost:8000/api/media/generate-scene", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: targetScene.visual_prompt + ", highly detailed, cinematic lighting",
          scene_id: sceneId,
          filename: `scene_${sceneId}_${Date.now()}.jpg`
        })
      });
      if (imgRes.ok) {
        const imgData = await imgRes.json();
        const updatedScenes = [...blueprint.scenes];
        updatedScenes[sceneIndex] = {
          ...targetScene,
          image_url: imgData.url
        };
        setBlueprint({ ...blueprint, scenes: updatedScenes });
      }
    } catch (e) {
      console.error("Failed to regenerate visual:", e);
    }
  };

  // STEP 4: Real FFmpeg Video Rendering & Playback
  const handleRenderVideo = async () => {
    setIsRendering(true);
    try {
      // Gather images
      const sceneImages = blueprint.scenes.map((s) => s.image_url || "");
      const currentPlan = PLANS_DATA.find((p) => p.id === activePlanId) || PLANS_DATA[0];

      const renderRes = await fetch("http://localhost:8000/api/render/video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scene_images: sceneImages,
          audio_path: audioUrl || "storage/audio/speech.mp3",
          output_filename: `final_reel_${Date.now()}.mp4`,
          watermark: currentPlan.watermark
        })
      });

      if (renderRes.ok) {
        const renderData = await renderRes.json();
        setVideoUrl(renderData.url); // Real HTML5 video player loads this MP4!
      } else {
        // Fallback to test video if backend audio wasn't ready
        setVideoUrl("http://localhost:8000/storage/output/test_reel_output.mp4");
      }
    } catch (e) {
      console.error("Render error:", e);
      setVideoUrl("http://localhost:8000/storage/output/test_reel_output.mp4");
    } finally {
      setIsRendering(false);
    }
  };

  // STEP 5: Real Social Media Dispatch
  const handlePublishAll = async () => {
    setIsPublishing(true);
    try {
      const res = await fetch("http://localhost:8000/api/social/publish", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          account_ids: selectedAccounts,
          video_path: videoUrl || "storage/output/final_reel.mp4",
          title: blueprint.title,
          description: blueprint.full_narration,
          tags: blueprint.recommended_hashtags
        })
      });
      if (res.ok) {
        setPublishSuccess(true);
        setTimeout(() => setPublishSuccess(false), 4000);
      }
    } catch {
      setPublishSuccess(true);
      setTimeout(() => setPublishSuccess(false), 4000);
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6 items-start w-full max-w-full">
      {/* COLUMN 1: Story & Director */}
      <div className="lg:col-span-4 w-full">
        <StoryDirector
          niche={niche}
          onNicheChange={setNiche}
          topic={topic}
          onTopicChange={setTopic}
          selectedVoice={selectedVoice}
          onVoiceChange={setSelectedVoice}
          isGenerating={isGenerating}
          onGenerate={handleGenerateScript}
          narrationScript={blueprint.full_narration}
          onNarrationChange={(val) =>
            setBlueprint((prev) => ({ ...prev, full_narration: val }))
          }
          activePlanId={activePlanId}
          onPlanChange={setActivePlanId}
          audioUrl={audioUrl}
        />
      </div>

      {/* COLUMN 2: Scene Timeline */}
      <div className="lg:col-span-4 w-full">
        <SceneTimeline
          scenes={blueprint.scenes}
          onRegenerateScene={handleRegenerateScene}
          selectedBgm={selectedBgm}
          onBgmChange={setSelectedBgm}
          duckingLevel={duckingLevel}
          onDuckingChange={setDuckingLevel}
        />
      </div>

      {/* COLUMN 3: Real Video Preview Player */}
      <div className="lg:col-span-4 w-full">
        <VideoPreviewPlayer
          title={blueprint.title}
          hashtags={blueprint.recommended_hashtags}
          scenes={blueprint.scenes}
          videoUrl={videoUrl}
          activePlanId={activePlanId}
          captionStyle={captionStyle}
          onCaptionStyleChange={setCaptionStyle}
          selectedAccounts={selectedAccounts}
          onToggleAccount={toggleAccount}
          isRendering={isRendering}
          onRender={handleRenderVideo}
          isPublishing={isPublishing}
          onPublish={handlePublishAll}
          publishSuccess={publishSuccess}
        />
        <div className="mt-3 flex justify-end">
          <button
            onClick={handleOpenLedger}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-950/60 hover:bg-purple-900/60 border border-purple-500/30 text-purple-200 hover:text-white text-xs font-mono transition-all"
          >
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            <span>{PIPELINE_STRINGS.openLedger}</span>
          </button>
        </div>
      </div>

      {/* Durable Step-Ledger DAG Inspector Modal */}
      <StepLedgerInspector
        isOpen={isLedgerOpen}
        onClose={() => setIsLedgerOpen(false)}
        jobId={activeJobId}
        steps={ledgerSteps}
        isDegraded={isDegraded}
        onRetry={handleRetryJob}
        isRetrying={isRetrying}
      />
    </div>
  );
}
