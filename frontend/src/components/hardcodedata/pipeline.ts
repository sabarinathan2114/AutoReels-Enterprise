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
