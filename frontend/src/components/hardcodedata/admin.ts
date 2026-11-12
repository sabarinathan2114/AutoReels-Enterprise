export interface AdminNavTabItem {
  id: "telemetry" | "tenants" | "upgrades" | "plans" | "audit";
  label: string;
  badge?: string;
  iconName: "activity" | "users" | "shieldAlert" | "sliders" | "history";
}

export const ADMIN_NAV_TABS: AdminNavTabItem[] = [
  { id: "telemetry", label: "System Telemetry", iconName: "activity" },
  { id: "tenants", label: "Tenants & Usage", iconName: "users" },
  { id: "upgrades", label: "Upgrade Requests", badge: "Live", iconName: "shieldAlert" },
  { id: "plans", label: "Plan Matrix Editor", iconName: "sliders" },
  { id: "audit", label: "Security & Audit", iconName: "history" }
];

export const ADMIN_STRINGS = {
  headerTitle: "SUPER ADMIN CONTROL PLANE",
  headerSubtitle: "Master Build Specification v2.0 • Security Level 3 • High-Privilege Gateway",
  unauthorizedNotice: "Super Administrator or Support credentials required to access this system.",
  loginPrompt: "Please sign in with your platform administrator credentials.",
  loginButton: "Authenticate Admin",
  emailPlaceholder: "admin@autoreels.dev",
  passwordPlaceholder: "••••••••••••",
  logoutButton: "Exit Console",
  backToApp: "Back to Studio",

  // Telemetry Tab
  telemetryTitle: "System Telemetry & Generation Farm Capacity",
  telemetrySubtitle: "Real-time health, job queues, capacity utilization, and global limits",
  dailyCapLabel: "Global Daily Render Cap",
  dailyCapDescription: "System-wide ceiling for video renders across all tenants. Prevents CPU exhaustion.",
  updateCapButton: "Update Daily Cap",
  farmStatusLabel: "Farm Status",
  activeWorkersLabel: "Active FFmpeg Workers",
  queueHealthLabel: "Queue Health",

  // Tenants Tab
  tenantsTitle: "Tenant & Workspace Directory",
  tenantsSubtitle: "Monitor active creator workspaces, quota consumption, and override subscriptions",
  searchPlaceholder: "Search by studio name or tenant slug...",
  tableHeaders: {
    studio: "Studio / Tenant",
    plan: "Current Tier",
    usage: "Usage & Monthly Quota",
    status: "Status",
    workspaceId: "Workspace ID",
    actions: "Actions"
  },
  changePlanButton: "Change Tier",
  noTenantsFound: "No tenants match the specified search query.",

  // Upgrades Tab
  upgradesTitle: "Creator Upgrade Approval Queue",
  upgradesSubtitle: "Review incoming requests to unlock Plan A, B, or C before manual billing conversion",
  emptyQueueMessage: "No pending plan upgrade requests at this moment. All requests processed.",
  approveButton: "Approve Upgrade",
  rejectButton: "Reject Request",
  rejectPrompt: "Enter rejection reason to note on request:",
  currentPlanLabel: "Current Plan",
  requestedPlanLabel: "Requested Tier",
  creatorLabel: "Creator Email",
  notesLabel: "Creator Statement",

  // Plans Editor Tab
  plansTitle: "Plan Matrix & Limits Editor (Plans as Data)",
  plansSubtitle: "Tuning limits immediately invalidates cache across all active tenant nodes within 60s (PLAN-04)",
  savePlanButton: "Save Changes & Invalidate Cache",
  planQuotaLabel: "Monthly Video Quota",
  planDurationLabel: "Max Video Duration (sec)",
  planResolutionLabel: "Video Resolution",
  planWatermarkLabel: "Render Watermark",

  // Audit Tab
  auditTitle: "Immutable Security Audit Ledger",
  auditSubtitle: "Every administrative write is cryptographically committed with actor ID and action payload (ADM-04)",
  auditTableHeaders: {
    timestamp: "Timestamp (UTC)",
    action: "Action Type",
    resource: "Resource",
    actor: "Admin User ID",
    details: "Details Payload"
  }
};
