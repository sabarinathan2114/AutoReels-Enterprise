export interface PlanTier {
  id: "free" | "plan_a" | "plan_b" | "plan_c";
  name: string;
  badge: string;
  maxDurationSec: number;
  resolution: string;
  watermark: boolean;
  voiceCount: number | string;
  socialChannels: number;
  modes: string[];
  storageRetentionDays: number;
  priceMonthly: string;
}

export interface ChannelProfile {
  id: string;
  name: string;
  niche: string;
  language: string;
  defaultVoice: string;
  avatar: string;
}

export interface VoiceOption {
  id: string;
  name: string;
  language: string;
  gender: string;
  isFree: boolean;
}

export interface NicheOption {
  id: string;
  title: string;
  description: string;
}

export interface SceneItem {
  scene_id: number;
  duration_sec: number;
  visual_prompt: string;
  subtitles: string;
  image_url: string;
}

export interface BlueprintData {
  title: string;
  language: string;
  voice_id: string;
  full_narration: string;
  scenes: SceneItem[];
  recommended_hashtags: string[];
  audio_url?: string;
}

export interface SocialAccountItem {
  id: string;
  name: string;
  platform: "youtube" | "instagram" | "facebook" | "tiktok";
  handle: string;
  apiName: string;
  status: "Active" | "Pending" | "Disconnected";
  metricLabel: string;
  metricValue: string;
  secondaryLabel: string;
  secondaryValue: string;
  isCheckedDefault: boolean;
}

export interface DashboardMetric {
  id: string;
  title: string;
  value: string;
  changeLabel: string;
  isPositive: boolean;
  iconName: "tv" | "film" | "trending" | "clock";
}

export interface ActivityLogItem {
  id: string;
  icon: string;
  title: string;
  destinations: string;
  views: string;
  timestamp: string;
}

export interface CaptionStyleOption {
  id: string;
  label: string;
  colorHex: string;
  activeClass: string;
}

export interface BgmOption {
  id: string;
  name: string;
  genre: string;
}

// -------------------------------------------------------------
// AUTOREELS V2.0 SPECIFICATION CONSTANTS & PLANS
// -------------------------------------------------------------

export const PLANS_DATA: PlanTier[] = [
  {
    id: "free",
    name: "Free Tier",
    badge: "Active Default",
    maxDurationSec: 30,
    resolution: "720x1280",
    watermark: true,
    voiceCount: 2,
    socialChannels: 0,
    modes: ["Zero-Input (Preset Niches)"],
    storageRetentionDays: 3,
    priceMonthly: "$0.00"
  },
  {
    id: "plan_a",
    name: "Plan A (Creator)",
    badge: "Popular",
    maxDurationSec: 45,
    resolution: "1080x1920",
    watermark: false,
    voiceCount: 6,
    socialChannels: 1,
    modes: ["Zero-Input", "Director Mode"],
    storageRetentionDays: 14,
    priceMonthly: "$9.00 / Promo"
  },
  {
    id: "plan_b",
    name: "Plan B (Growth)",
    badge: "Pro",
    maxDurationSec: 60,
    resolution: "1080x1920",
    watermark: false,
    voiceCount: 12,
    socialChannels: 3,
    modes: ["Zero-Input", "Director Mode", "Character Mode"],
    storageRetentionDays: 30,
    priceMonthly: "$29.00"
  },
  {
    id: "plan_c",
    name: "Plan C (Agency)",
    badge: "Enterprise",
    maxDurationSec: 60,
    resolution: "1080x1920",
    watermark: false,
    voiceCount: "All + Brand Voice",
    socialChannels: 10,
    modes: ["All Modes + Autopilot"],
    storageRetentionDays: 60,
    priceMonthly: "$79.00"
  }
];

export const CHANNELS_DATA: ChannelProfile[] = [
  {
    id: "chutti_kuzhandhai",
    name: "Chutti Kuzhandhai (Tamil / Kids Stories)",
    niche: "emotional_drama",
    language: "Tamil",
    defaultVoice: "ta-IN-ValluvarNeural",
    avatar: "👶"
  },
  {
    id: "tech_360",
    name: "Tech Insights 360 (English / Tech News)",
    niche: "tech_news",
    language: "English",
    defaultVoice: "en-US-ChristopherNeural",
    avatar: "⚡"
  },
  {
    id: "geo_pulse",
    name: "Global Geopolitics (World Breaking News)",
    niche: "geopolitics",
    language: "English",
    defaultVoice: "en-US-GuyNeural",
    avatar: "🌍"
  },
  {
    id: "daily_chuckles",
    name: "Daily Chuckles (Comedy / Viral Facts)",
    niche: "humor_facts",
    language: "English",
    defaultVoice: "en-US-GuyNeural",
    avatar: "😂"
  }
];

export const NICHES_DATA: NicheOption[] = [
  {
    id: "emotional_drama",
    title: "Emotional Drama & Character Stories (Tamil / Regional)",
    description: "High-retention moral stories, kids animation, and tearjerker hooks."
  },
  {
    id: "tech_news",
    title: "High Retention Tech & AI Breakthroughs",
    description: "Fast-paced tech updates, AI tools, and future speculation."
  },
  {
    id: "geopolitics",
    title: "Geopolitics & Breaking World News",
    description: "Global conflicts, economic shifts, and country analysis."
  },
  {
    id: "humor_facts",
    title: "Viral Humor & Mind-Blowing Facts",
    description: "Shower thoughts, weird trivia, and funny daily observations."
  }
];

export const VOICES_DATA: VoiceOption[] = [
  {
    id: "ta-IN-ValluvarNeural",
    name: "Tamil: Valluvar (Expressive Male)",
    language: "Tamil",
    gender: "Male",
    isFree: true
  },
  {
    id: "ta-IN-PallaviNeural",
    name: "Tamil: Pallavi (Warm Female)",
    language: "Tamil",
    gender: "Female",
    isFree: true
  },
  {
    id: "en-US-ChristopherNeural",
    name: "English: Christopher (Documentary Male)",
    language: "English",
    gender: "Male",
    isFree: true
  },
  {
    id: "en-US-GuyNeural",
    name: "English: Guy (Energetic Shorts Male)",
    language: "English",
    gender: "Male",
    isFree: true
  },
  {
    id: "en-US-AriaNeural",
    name: "English: Aria (Professional Female)",
    language: "English",
    gender: "Female",
    isFree: true
  },
  {
    id: "hi-IN-MadhurNeural",
    name: "Hindi: Madhur (Dynamic Male)",
    language: "Hindi",
    gender: "Male",
    isFree: true
  },
  {
    id: "hi-IN-SwaraNeural",
    name: "Hindi: Swara (Expressive Female)",
    language: "Hindi",
    gender: "Female",
    isFree: true
  }
];

export const CAPTION_STYLES: CaptionStyleOption[] = [
  {
    id: "neon_yellow",
    label: "Neon Yellow",
    colorHex: "#FFD700",
    activeClass: "border-yellow-400 text-yellow-300 bg-yellow-950/40 shadow-[0_0_15px_rgba(255,215,0,0.3)]"
  },
  {
    id: "emerald_bounce",
    label: "Emerald Pop",
    colorHex: "#10B981",
    activeClass: "border-emerald-400 text-emerald-300 bg-emerald-950/40 shadow-[0_0_15px_rgba(16,185,129,0.3)]"
  },
  {
    id: "cyber_violet",
    label: "Cosmic Violet",
    colorHex: "#C084FC",
    activeClass: "border-fuchsia-400 text-fuchsia-300 bg-fuchsia-950/40 shadow-[0_0_15px_rgba(192,132,252,0.3)]"
  }
];

export const BGM_TRACKS: BgmOption[] = [
  { id: "flute_ambient", name: "Emotional Flute Ambient", genre: "Emotional" },
  { id: "synth_pulse", name: "Cyberpunk Pulsing Synth", genre: "Electronic" },
  { id: "whimsical_kids", name: "Playful Kids Whimsical", genre: "Comedy" },
  { id: "tension_riser", name: "Deep Cinematic Tension", genre: "Dramatic" }
];

export const DEFAULT_BLUEPRINT: BlueprintData = {
  title: "The Strawberry's Last Wish - ஒரு உணர்ச்சிகரமான கதை",
  language: "Tamil",
  voice_id: "ta-IN-ValluvarNeural",
  full_narration:
    "இந்த ஒரு ஆசை அவனுடைய மொத்த வாழ்க்கையையும் இப்படி மாற்றிவிடும் என்று அவன் நினைக்கவே இல்லை. தன் அம்மாவைக் காப்பாற்ற ஒரே ஒரு மந்திர ஆசையை அவன் பயன்படுத்தினான். ஆனால் அந்த ஆசை நிறைவேறும் தருணத்தில், அவன் வாழ்ந்த கிராமமே மிகப்பெரிய ஆபத்தில் மூழ்கியது.",
  scenes: [
    {
      scene_id: 1,
      duration_sec: 4,
      visual_prompt: "3D cute Pixar style emotional animated strawberry boy looking at a magical glowing tear",
      subtitles: "இந்த ஒரு ஆசை அவனுடைய வாழ்க்கையையே மாற்றியது...",
      image_url: "https://images.unsplash.com/photo-1543332164-6e82f355badc?w=600&auto=format&fit=crop&q=80"
    },
    {
      scene_id: 2,
      duration_sec: 5,
      visual_prompt: "3D animated rustic village cottage in warm evening golden hour lighting",
      subtitles: "தன் அம்மாவைக் காப்பாற்ற அந்த ஆசையை பயன்படுத்தினான்...",
      image_url: "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=600&auto=format&fit=crop&q=80"
    },
    {
      scene_id: 3,
      duration_sec: 5,
      visual_prompt: "Dramatic stormy skies with glowing magical purple aura over a village",
      subtitles: "ஆனால் கிராமமே மிகப்பெரிய ஆபத்தில் மூழ்கியது...",
      image_url: "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=600&auto=format&fit=crop&q=80"
    },
    {
      scene_id: 4,
      duration_sec: 4,
      visual_prompt: "Heartwarming reunion with golden sparkling light, emotional cartoon masterpiece",
      subtitles: "அம்மாவின் பாசம் இறுதியில் வென்றது!",
      image_url: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80"
    }
  ],
  recommended_hashtags: ["#TamilReels", "#AIStory", "#EmotionalDrama", "#Shorts", "#Viral"]
};

export const SOCIAL_ACCOUNTS_DATA: SocialAccountItem[] = [
  {
    id: "yt_shorts_main",
    name: "Tech & Stories Shorts",
    platform: "youtube",
    handle: "@TechStoriesShorts",
    apiName: "YouTube Data API v3",
    status: "Active",
    metricLabel: "Subscribers",
    metricValue: "34.2K",
    secondaryLabel: "Daily Quota",
    secondaryValue: "2 / 6 Used",
    isCheckedDefault: true
  },
  {
    id: "ig_reels_kids",
    name: "@ChuttiKuzhandhai",
    platform: "instagram",
    handle: "@ChuttiKuzhandhai_Official",
    apiName: "Meta Graph API v19",
    status: "Active",
    metricLabel: "Followers",
    metricValue: "24.8K",
    secondaryLabel: "Reels Posted",
    secondaryValue: "89 Reels",
    isCheckedDefault: true
  },
  {
    id: "fb_page_main",
    name: "Global Insights Page",
    platform: "facebook",
    handle: "fb.com/GlobalInsightsPage",
    apiName: "Meta Page Video API",
    status: "Active",
    metricLabel: "Page Likes",
    metricValue: "52.1K",
    secondaryLabel: "Auto-Cross-Post",
    secondaryValue: "Enabled",
    isCheckedDefault: true
  }
];

export const METRICS_DATA: DashboardMetric[] = [
  {
    id: "m_channels",
    title: "Connected Channels",
    value: "4 Active",
    changeLabel: "All APIs Healthy",
    isPositive: true,
    iconName: "tv"
  },
  {
    id: "m_reels",
    title: "Reels Published",
    value: "142 Videos",
    changeLabel: "+18 this week",
    isPositive: true,
    iconName: "film"
  },
  {
    id: "m_views",
    title: "30-Day Total Views",
    value: "1,842,910",
    changeLabel: "+34.2% MoM",
    isPositive: true,
    iconName: "trending"
  },
  {
    id: "m_retention",
    title: "Avg Watch Retention",
    value: "78.4%",
    changeLabel: "Optimal Pacing",
    isPositive: true,
    iconName: "clock"
  }
];

export const ACTIVITY_LOGS_DATA: ActivityLogItem[] = [
  {
    id: "log_1",
    icon: "🍓",
    title: "The Strawberry's Last Wish (ஒரு ஆசை)",
    destinations: "YouTube Shorts & Instagram Reels",
    views: "148.2K Views",
    timestamp: "Published Today"
  },
  {
    id: "log_2",
    icon: "⚡",
    title: "Why Quantum Computers Will Change Everything",
    destinations: "YouTube Shorts",
    views: "92.5K Views",
    timestamp: "Published Yesterday"
  },
  {
    id: "log_3",
    icon: "🌍",
    title: "The Silent Trade War Reshaping 2026",
    destinations: "YouTube Shorts & Facebook Reels",
    views: "210.8K Views",
    timestamp: "3 days ago"
  }
];

// -------------------------------------------------------------
// PHASE 3: LANDING PAGE & ONBOARDING DATA (ZERO HARDCODING IN UI)
// -------------------------------------------------------------

export interface HowItWorksStep {
  step: string;
  title: string;
  description: string;
  badge: string;
  iconName: "wand" | "mic" | "sparkles" | "share2";
}

export interface FeatureItem {
  id: string;
  title: string;
  description: string;
  highlight: string;
  tag: string;
}

export interface FaqItem {
  id: string;
  question: string;
  answer: string;
}

export const LANDING_HERO_DATA = {
  badge: "⚡ AutoReels v2.0 • 100% Free-First Pipeline",
  headlinePrefix: "Turn One Click Into",
  headlineHighlight: "Viral 9:16 Vertical Reels",
  description: "Autonomous end-to-end video synthesis powered by free neural TTS, open AI visuals, and kinetic captions. Zero cash cost. No credit card required.",
  primaryCta: "Start Creating Free (2 Videos/mo)",
  secondaryCta: "Compare Plans",
  stats: [
    { label: "Cost Per Render", value: "$0.00 Free" },
    { label: "Aspect Ratio", value: "9:16 Vertical" },
    { label: "Supported Platforms", value: "YT / IG / FB" },
    { label: "Render Pacing", value: "CPU-Optimized" }
  ]
};

export const HOW_IT_WORKS_STEPS: HowItWorksStep[] = [
  {
    step: "01",
    title: "Choose Topic or Premise",
    description: "Select from proven viral niches (Emotional Drama, Tech News, Comedy, Geopolitics) or enter any premise in English or regional languages like Tamil.",
    badge: "Input Stage",
    iconName: "wand"
  },
  {
    step: "02",
    title: "AI Directs Scenes & Speech",
    description: "Our blueprint engine creates scene breakdown, prompt art, and generates hyper-realistic neural voiceovers with word-level subtitle timings.",
    badge: "Synthesis Stage",
    iconName: "mic"
  },
  {
    step: "03",
    title: "Render & 1-Click Dispatch",
    description: "FFmpeg stitches visual frames with kinetic karaoke captions and burns safe-zone layout for instant download or multi-platform broadcasting.",
    badge: "Delivery Stage",
    iconName: "sparkles"
  }
];

export const FEATURE_SHOWCASE_DATA: FeatureItem[] = [
  {
    id: "feat_tts",
    title: "Neural Multi-Voice Synthesis",
    description: "Studio-quality speech generation across 300+ natural voices and 80+ locales via zero-cost neural pipelines.",
    highlight: "Zero Cost",
    tag: "Voice Engine"
  },
  {
    id: "feat_captions",
    title: "Kinetic Word-by-Word Subtitles",
    description: "High-retention glowing karaoke captions burned via FFmpeg libass with safe zones preventing UI overlap on TikTok and Reels.",
    highlight: "Safe Zones",
    tag: "Video Engine"
  },
  {
    id: "feat_ladder",
    title: "Free Visual Ladder",
    description: "Automatic progressive fallback from Pexels/Pixabay portrait stock to typographic gradients and open AI image models.",
    highlight: "Fail-Safe",
    tag: "Media Engine"
  },
  {
    id: "feat_tenancy",
    title: "Isolated Workspaces & Tenancy",
    description: "Multi-tenant architecture isolating projects, channels, and usage quotas per team with full workspace scoping.",
    highlight: "Isolated",
    tag: "Security"
  },
  {
    id: "feat_autopilot",
    title: "Multi-Account Social Dispatch",
    description: "Broadcast ready-to-watch reels to YouTube Shorts, Instagram Reels, and Facebook Pages in a single click.",
    highlight: "Auto-Post",
    tag: "Publishing"
  },
  {
    id: "feat_plans",
    title: "Free-First Plan Architecture",
    description: "Sign up on Free tier with 2 free monthly renders, with seamless upgrade request workflows for high-volume creators.",
    highlight: "2 Videos/mo Free",
    tag: "Entitlements"
  }
];

export const FAQ_ITEMS: FaqItem[] = [
  {
    id: "faq_1",
    question: "Is AutoReels really zero cash cost to run?",
    answer: "Yes! In accordance with Master Build Spec v2.0 Section 15, AutoReels utilizes only zero-cost and open-source tools: Edge-TTS/Piper, FFmpeg libass captions, local/open visual APIs, and MySQL. No paid API keys are required for the primary creation path."
  },
  {
    id: "faq_2",
    question: "What are the exact video outputs and formats?",
    answer: "Videos are rendered as 9:16 vertical MP4s (720x1280 on the Free tier, 1080x1920 HD on Plan A/B/C) with AAC audio, centered animated subtitles within social safe zones (18% bottom, 8% top), and optimal viral pacing."
  },
  {
    id: "faq_3",
    question: "What does the Free Plan include?",
    answer: "The Free Plan includes 2 complete vertical video renders per calendar month, 30-second max duration, 720p vertical resolution, 2 neural voices, and direct MP4 downloads."
  },
  {
    id: "faq_4",
    question: "How do upgrades work if there is no payment gateway yet?",
    answer: "Plans A, B, and C are stored as database data. Creators can submit a 'Request Upgrade' directly from the plans comparison table or dashboard. A platform administrator reviews and approves the tier."
  },
  {
    id: "faq_5",
    question: "Can I manage multiple YouTube and Instagram channels?",
    answer: "Yes! Depending on your workspace tier, you can link 1 channel (Plan A), 3 channels (Plan B), or up to 10 channels (Plan C) for automated cross-platform broadcasting."
  }
];
