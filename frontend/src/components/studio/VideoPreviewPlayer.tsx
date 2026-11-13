import React, { useRef, useState } from "react";
import { Tv, Film, Send, CheckCircle, Play, Pause, Volume2, VolumeX, Sparkles, Download, RotateCcw, ShieldAlert } from "lucide-react";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { CosmicButton } from "../common/CosmicButton";
import { YoutubeIcon, InstagramIcon, FacebookIcon, TikTokIcon } from "../common/SocialIcons";
import {
  CAPTION_STYLES,
  SOCIAL_ACCOUNTS_DATA,
  SceneItem,
  CaptionStyleOption,
  SocialAccountItem,
  PLANS_DATA,
  PlanTier
} from "../hardcodedata";

interface VideoPreviewPlayerProps {
  title: string;
  hashtags: string[];
  scenes: SceneItem[];
  videoUrl?: string | null;
  activePlanId: string;
  captionStyle: string;
  onCaptionStyleChange: (styleId: string) => void;
  selectedAccounts: string[];
  onToggleAccount: (accountId: string) => void;
  isRendering: boolean;
  onRender: () => void;
  isPublishing: boolean;
  onPublish: () => void;
  publishSuccess: boolean;
  isDegraded?: boolean;
  onRetry?: () => void;
  isRetrying?: boolean;
}

export function VideoPreviewPlayer({
  title,
  hashtags,
  scenes,
  videoUrl,
  activePlanId,
  captionStyle,
  onCaptionStyleChange,
  selectedAccounts,
  onToggleAccount,
  isRendering,
  onRender,
  isPublishing,
  onPublish,
  publishSuccess,
  isDegraded = false,
  onRetry,
  isRetrying = false
}: VideoPreviewPlayerProps) {
  const currentPlan = PLANS_DATA.find((p) => p.id === activePlanId) || PLANS_DATA[0];
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (videoRef.current.paused) {
      videoRef.current.play();
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !videoRef.current.muted;
    setIsMuted(videoRef.current.muted);
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
      setDuration(videoRef.current.duration || 0);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (videoRef.current) {
      const val = parseFloat(e.target.value);
      videoRef.current.currentTime = val;
      setCurrentTime(val);
    }
  };

  const handleDownload = () => {
    if (!videoUrl) return;
    const a = document.createElement("a");
    a.href = videoUrl;
    a.download = `autoreels_${activePlanId}_${Date.now()}.mp4`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const currentPreviewImage =
    scenes[0]?.image_url ||
    "https://images.unsplash.com/photo-1543332164-6e82f355badc?w=600&auto=format&fit=crop&q=80";

  const renderPlatformIcon = (platform: SocialAccountItem["platform"]) => {
    switch (platform) {
      case "youtube":
        return <YoutubeIcon className="w-4 h-4 text-red-500 flex-shrink-0" />;
      case "instagram":
        return <InstagramIcon className="w-4 h-4 text-pink-500 flex-shrink-0" />;
      case "facebook":
        return <FacebookIcon className="w-4 h-4 text-blue-500 flex-shrink-0" />;
      case "tiktok":
        return <TikTokIcon className="w-4 h-4 text-cyan-400 flex-shrink-0" />;
    }
  };

  return (
    <GlassPanel className="p-3.5 sm:p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-purple-500/20">
        <div className="flex items-center gap-2 min-w-0">
          <Tv className="w-4 h-4 text-purple-400 flex-shrink-0" />
          <h2 className="text-xs sm:text-sm font-semibold tracking-wider text-purple-200 uppercase truncate">
            3. Live 9:16 Video Player
          </h2>
        </div>
        <div className="flex items-center gap-1.5">
          <Badge variant={currentPlan.watermark ? "yellow" : "emerald"}>
            {currentPlan.resolution} {currentPlan.watermark ? "(Watermark)" : "(No Watermark)"}
          </Badge>
        </div>
      </div>

      {/* Responsive 9:16 Video Container (Fits cleanly down to 320px) */}
      <div className="relative mx-auto w-full max-w-[240px] sm:max-w-[270px] aspect-[9/16] rounded-2xl overflow-hidden border-2 border-purple-500/40 shadow-[0_0_30px_rgba(139,92,246,0.3)] bg-black flex flex-col justify-between group">
        {videoUrl ? (
          /* REAL HTML5 VIDEO PLAYER WITH CUSTOM CONTROLS & SCRUBBER */
          <div className="relative w-full h-full flex flex-col justify-between">
            <video
              ref={videoRef}
              src={videoUrl}
              autoPlay
              loop
              playsInline
              onTimeUpdate={handleTimeUpdate}
              className="absolute inset-0 w-full h-full object-cover"
            />

            {/* Top Watermark Badge */}
            <div className="relative z-10 flex items-center justify-between p-2.5">
              <span className="bg-black/60 backdrop-blur text-[10px] text-purple-200 px-2 py-0.5 rounded border border-purple-500/30">
                {currentPlan.resolution}
              </span>
              {currentPlan.watermark && (
                <span className="bg-black/80 backdrop-blur text-[9px] text-amber-300 font-medium px-2 py-0.5 rounded border border-amber-500/40 pointer-events-none">
                  ⚡ AutoReels Free
                </span>
              )}
            </div>

            {/* Center Play/Pause Overlay Button */}
            <button
              type="button"
              onClick={togglePlay}
              className="absolute inset-0 m-auto w-12 h-12 rounded-full bg-purple-950/70 border border-purple-400/50 flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity z-10"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
            </button>

            {/* Bottom Controls Bar & Scrubber */}
            <div className="relative z-10 p-2.5 bg-gradient-to-t from-black/90 via-black/60 to-transparent space-y-1">
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min={0}
                  max={duration || 1}
                  step={0.1}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-1 bg-purple-950 rounded-lg appearance-none cursor-pointer accent-purple-400"
                />
              </div>
              <div className="flex items-center justify-between text-[9px] font-mono text-purple-200">
                <span>{currentTime.toFixed(1)}s / {duration.toFixed(1)}s</span>
                <button
                  type="button"
                  onClick={toggleMute}
                  className="p-1 hover:text-white"
                >
                  {isMuted ? <VolumeX className="w-3.5 h-3.5 text-red-400" /> : <Volume2 className="w-3.5 h-3.5 text-purple-300" />}
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* IMAGE PREVIEW BEFORE RENDERING */
          <div className="relative w-full h-full flex flex-col justify-between p-3 sm:p-4">
            <img
              src={currentPreviewImage}
              alt="Current Frame"
              className="absolute inset-0 w-full h-full object-cover opacity-85"
            />

            {/* Top Badge */}
            <div className="relative z-10 flex items-center justify-between">
              <Badge variant="dark">Preview Image</Badge>
              <span className="text-[10px] text-white/90 font-mono drop-shadow">0:00 / 0:40</span>
            </div>

            {/* Center Dynamic Subtitle Frame */}
            <div className="relative z-10 text-center px-2">
              <div className="inline-block bg-black/75 backdrop-blur-md px-2.5 sm:px-3 py-1.5 rounded-xl border border-yellow-400/40 shadow-lg max-w-full">
                <span className="text-sm sm:text-base font-extrabold text-[#FFD700] tracking-wide inline-block">
                  உணர்ச்சிகரமான
                </span>
                <span className="text-sm sm:text-base font-extrabold text-white ml-1.5">
                  கதை
                </span>
              </div>
            </div>

            {/* Bottom Metadata */}
            <div className="relative z-10 space-y-0.5">
              <p className="text-[10px] sm:text-[11px] font-bold text-white line-clamp-1 drop-shadow">
                {title}
              </p>
              <p className="text-[8px] sm:text-[9px] text-purple-200/90 font-mono truncate">
                {hashtags.join(" ")}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Degradation Notice & Retry Action */}
      {isDegraded && (
        <div className="p-2.5 rounded-xl bg-amber-950/40 border border-amber-500/40 flex items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-1.5 min-w-0">
            <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <span className="text-[11px] text-amber-200 truncate">Degraded fallback applied</span>
          </div>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              disabled={isRetrying}
              className="px-2 py-1 rounded-lg bg-amber-900/60 hover:bg-amber-800/80 text-amber-200 text-[10px] font-bold flex items-center gap-1 transition-all"
            >
              <RotateCcw className={`w-3 h-3 ${isRetrying ? "animate-spin" : ""}`} />
              {isRetrying ? "Retrying..." : "Retry Steps"}
            </button>
          )}
        </div>
      )}

      {/* Download Video Action */}
      {videoUrl && (
        <div className="pt-1">
          <button
            type="button"
            onClick={handleDownload}
            className="w-full py-2 px-3 rounded-xl bg-purple-950/80 hover:bg-purple-900/90 border border-purple-500/40 hover:border-purple-400 text-purple-100 hover:text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(139,92,246,0.2)]"
          >
            <Download className="w-3.5 h-3.5 text-purple-300" />
            <span>
              {activePlanId === "free" ? "Download Watermarked MP4 (Free Tier)" : "Download Pristine 1080p MP4"}
            </span>
          </button>
        </div>
      )}

      {/* Subtitle Theme Switcher */}
      <div className="space-y-1.5 pt-1">
        <label className="text-xs text-purple-300 font-medium block">
          Kinetic Subtitle Theme
        </label>
        <div className="grid grid-cols-3 gap-1.5 sm:gap-2 text-[10px] sm:text-xs">
          {CAPTION_STYLES.map((style: CaptionStyleOption) => (
            <button
              key={style.id}
              onClick={() => onCaptionStyleChange(style.id)}
              className={`py-1.5 px-1 rounded-lg border text-center transition-all truncate ${
                captionStyle === style.id
                  ? style.activeClass
                  : "border-purple-500/20 text-purple-300 hover:border-purple-400/40"
              }`}
            >
              {style.label}
            </button>
          ))}
        </div>
      </div>

      {/* Social Accounts Dispatch Destinations */}
      <div className="space-y-2 pt-2 border-t border-purple-500/20">
        <div className="flex items-center justify-between text-xs text-purple-300 font-medium">
          <span>Broadcast Destinations</span>
          <span className="text-[10px] text-purple-400">
            {currentPlan.socialChannels === 0 ? "Upgrade for Autopilot" : `Limit: ${currentPlan.socialChannels}`}
          </span>
        </div>
        <div className="space-y-1.5">
          {SOCIAL_ACCOUNTS_DATA.map((acc: SocialAccountItem) => {
            const isChecked = selectedAccounts.includes(acc.id);
            return (
              <label
                key={acc.id}
                onClick={() => onToggleAccount(acc.id)}
                className={`flex items-center justify-between p-2 rounded-xl border cursor-pointer text-xs transition-all ${
                  isChecked
                    ? "bg-purple-950/60 border-purple-400/50"
                    : "bg-purple-950/20 border-purple-500/20 opacity-70 hover:opacity-100"
                }`}
              >
                <div className="flex items-center gap-2 min-w-0 pr-2">
                  {renderPlatformIcon(acc.platform)}
                  <span className="truncate text-[11px] sm:text-xs text-purple-100">
                    {acc.name}
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => {}}
                  className="accent-purple-500 rounded flex-shrink-0 cursor-pointer"
                />
              </label>
            );
          })}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-2 pt-1">
        <CosmicButton
          variant="outline"
          onClick={onRender}
          isLoading={isRendering}
          icon={<Film className="w-3.5 h-3.5" />}
          className="w-full"
        >
          {isRendering ? "Rendering with FFmpeg..." : "Render Final 9:16 Video"}
        </CosmicButton>

        <CosmicButton
          variant="primary"
          onClick={onPublish}
          isLoading={isPublishing}
          icon={<Send className="w-4 h-4" />}
          className="w-full py-2.5 sm:py-3 text-xs sm:text-sm font-bold"
        >
          {isPublishing ? "Publishing to Accounts..." : "One-Click Publish to All Selected Accounts"}
        </CosmicButton>

        {publishSuccess && (
          <div className="p-2 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs text-center flex items-center justify-center gap-1.5 animate-fadeIn">
            <CheckCircle className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">Dispatched to all selected accounts!</span>
          </div>
        )}
      </div>
    </GlassPanel>
  );
}
