export interface StepLedgerItem {
  id: string;
  step_key: string;
  scene_index: number | null;
  status: "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED" | "SKIPPED" | "DEGRADED";
  attempt: number;
  provider: string | null;
  input_hash: string;
  error_class: string | null;
  error_detail: string | null;
  cost_micros: number;
  started_at: string | null;
  finished_at: string | null;
}

export const PIPELINE_STRINGS = {
  ledgerTitle: "DURABLE STEP-LEDGER DAG",
  ledgerSubtitle: "Content-addressable idempotency • Partial-failure recovery • Zero duplicate work",
  dagStages: {
    script: "1. Story Script & Blueprint",
    image: "2. Scene Media (Fan-Out)",
    tts: "3. Neural Voice & Subtitles",
    compose: "4. FFmpeg Video Compose"
  },
  honestEtaLabel: "Honest Estimated Duration",
  degradedWarning: "Degradation policy applied: fallback assets used to guarantee reel delivery",
  retryButton: "Resume from Failed Step",
  retryingLabel: "Resuming DAG...",
  closeLedger: "Close Inspector",
  openLedger: "Inspect Step Ledger DAG"
};

export interface ViralTrend {
  id: string;
  title: string;
  summary: string;
  category: string;
  velocity_score: number;
  suggested_angle: string;
}

export const HOOK_FORMULAS = [
  { id: "curiosity_gap", label: "Curiosity Gap", desc: "Leaves viewer craving the revelation" },
  { id: "negative_hook", label: "Negative Hook", desc: "'Stop doing this wrong' framing" },
  { id: "shock_stat", label: "Shocking Statistic", desc: "99% of people don't know..." },
  { id: "bold_claim", label: "Bold Controversy", desc: "Challenges mainstream belief" }
];

export const CURATED_VIRAL_TRENDS: ViralTrend[] = [
  {
    id: "trend-001",
    title: "James Webb Detects Impossible Ancient Galaxies",
    summary: "Astrophysicists find massive galaxies existing just 300 million years after the Big Bang.",
    category: "Science & Space",
    velocity_score: 0.98,
    suggested_angle: "How new cosmic discoveries rewrite textbooks overnight."
  },
  {
    id: "trend-002",
    title: "Why Coffee Tastes Different In Space",
    summary: "Microgravity alters fluid dynamics making regular brew taste flat to astronauts.",
    category: "Daily Facts",
    velocity_score: 0.92,
    suggested_angle: "The bizarre science of human taste buds in zero gravity."
  },
  {
    id: "trend-003",
    title: "Ancient Roman Self-Healing Concrete Mystery",
    summary: "Scientists unlock the 2,000-year-old mystery of quicklime that seals cracks automatically.",
    category: "History & Tech",
    velocity_score: 0.95,
    suggested_angle: "Why ancient monuments outlast modern skyscrapers."
  }
];
