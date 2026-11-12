"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  ShieldAlert,
  Activity,
  Users,
  Sliders,
  History,
  Lock,
  LogOut,
  ArrowLeft,
  RefreshCw,
  AlertCircle
} from "lucide-react";
import Link from "next/link";
import { GlassPanel } from "../common/GlassPanel";
import { Badge } from "../common/Badge";
import { CosmicButton } from "../common/CosmicButton";
import { CosmicInput } from "../common/FormControls";
import { ADMIN_NAV_TABS, ADMIN_STRINGS } from "../hardcodedata/admin";
import { TelemetryTab } from "./TelemetryTab";
import { TenantsTab, TenantRow } from "./TenantsTab";
import { UpgradesTab, UpgradeRequestItem } from "./UpgradesTab";
import { PlansEditorTab, PlanConfigItem } from "./PlansEditorTab";
import { AuditLedgerTab, AuditLogItem } from "./AuditLedgerTab";

const API_BASE = "http://localhost:8000";
const ADMIN_TOKEN_KEY = "autoreels_admin_token";

export function AdminConsoleView() {
  const [token, setToken] = useState<string | null>(null);
  const [adminUser, setAdminUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<"telemetry" | "tenants" | "upgrades" | "plans" | "audit">("telemetry");

  // Admin login form states
  const [loginEmail, setLoginEmail] = useState("admin@autoreels.dev");
  const [loginPassword, setLoginPassword] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  // Data states
  const [telemetry, setTelemetry] = useState<any>(null);
  const [tenants, setTenants] = useState<TenantRow[]>([]);
  const [upgrades, setUpgrades] = useState<UpgradeRequestItem[]>([]);
  const [plans, setPlans] = useState<PlanConfigItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Restore stored token on mount
  useEffect(() => {
    const saved = localStorage.getItem(ADMIN_TOKEN_KEY);
    if (saved) {
      setToken(saved);
    }
  }, []);

  const getHeaders = useCallback(() => {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    };
  }, [token]);

  // Fetch data for active tab
  const fetchData = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    setApiError(null);
    try {
      if (activeTab === "telemetry") {
        const res = await fetch(`${API_BASE}/api/v1/admin/telemetry`, { headers: getHeaders() });
        if (res.ok) setTelemetry(await res.json());
        else if (res.status === 401 || res.status === 403) setToken(null);
      } else if (activeTab === "tenants") {
        const res = await fetch(`${API_BASE}/api/v1/admin/tenants`, { headers: getHeaders() });
        if (res.ok) setTenants(await res.json());
      } else if (activeTab === "upgrades") {
        const res = await fetch(`${API_BASE}/api/v1/admin/upgrade-requests`, { headers: getHeaders() });
        if (res.ok) setUpgrades(await res.json());
      } else if (activeTab === "plans") {
        const res = await fetch(`${API_BASE}/api/v1/admin/plans`, { headers: getHeaders() });
        if (res.ok) setPlans(await res.json());
      } else if (activeTab === "audit") {
        const res = await fetch(`${API_BASE}/api/v1/admin/audit-logs`, { headers: getHeaders() });
        if (res.ok) setAuditLogs(await res.json());
      }
    } catch (err: any) {
      setApiError(err.message || "Failed to communicate with Super Admin API");
    } finally {
      setIsLoading(false);
    }
  }, [token, activeTab, getHeaders]);

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token, activeTab, fetchData]);

  // Handle Admin Login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoggingIn(true);
    setLoginError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: loginEmail, password: loginPassword })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Authentication failed");
      }
      localStorage.setItem(ADMIN_TOKEN_KEY, data.access_token);
      setToken(data.access_token);
      setAdminUser(data.admin_user);
    } catch (err: any) {
      setLoginError(err.message);
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem(ADMIN_TOKEN_KEY);
    setToken(null);
    setAdminUser(null);
  };

  // Actions
  const handleUpdateDailyCap = async (newCap: number) => {
    const res = await fetch(`${API_BASE}/api/v1/admin/settings/daily-cap`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ cap: newCap })
    });
    if (!res.ok) {
      const d = await res.json();
      throw new Error(d.detail || "Failed to update daily cap");
    }
    await fetchData();
  };

  const handleChangeTenantPlan = async (tenantId: string, newPlanId: string) => {
    const res = await fetch(`${API_BASE}/api/v1/admin/tenants/${tenantId}/plan`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ new_plan_id: newPlanId })
    });
    if (!res.ok) {
      const d = await res.json();
      throw new Error(d.detail || "Failed to change tenant plan");
    }
    await fetchData();
  };

  const handleApproveUpgrade = async (requestId: string) => {
    const res = await fetch(`${API_BASE}/api/v1/admin/upgrade-requests/${requestId}/approve`, {
      method: "POST",
      headers: getHeaders()
    });
    if (!res.ok) {
      const d = await res.json();
      throw new Error(d.detail || "Failed to approve upgrade");
    }
    await fetchData();
  };

  const handleRejectUpgrade = async (requestId: string, reason: string) => {
    const res = await fetch(`${API_BASE}/api/v1/admin/upgrade-requests/${requestId}/reject`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ reason })
    });
    if (!res.ok) {
      const d = await res.json();
      throw new Error(d.detail || "Failed to reject upgrade");
    }
    await fetchData();
  };

  const handleSavePlan = async (planId: string, updates: Partial<PlanConfigItem>) => {
    const res = await fetch(`${API_BASE}/api/v1/admin/plans/${planId}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(updates)
    });
    if (!res.ok) {
      const d = await res.json();
      throw new Error(d.detail || "Failed to update plan limits");
    }
    await fetchData();
  };

  // Render Login Screen if not authenticated
  if (!token) {
    return (
      <div className="min-h-screen bg-[#07040D] flex items-center justify-center p-4">
        <GlassPanel className="w-full max-w-md p-6 sm:p-8 space-y-6 border-purple-500/40 shadow-[0_0_50px_rgba(139,92,246,0.2)]">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-violet-600 to-fuchsia-600 flex items-center justify-center mx-auto shadow-[0_0_25px_rgba(139,92,246,0.5)]">
              <Lock className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
              {ADMIN_STRINGS.headerTitle}
            </h1>
            <p className="text-xs text-purple-300/80">
              {ADMIN_STRINGS.loginPrompt}
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {loginError && (
              <div className="p-3 rounded-xl bg-red-950/60 border border-red-500/40 text-red-200 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
                <span>{loginError}</span>
              </div>
            )}

            <div>
              <label className="text-xs font-semibold text-purple-200 block mb-1">
                Admin Email
              </label>
              <CosmicInput
                type="email"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                placeholder={ADMIN_STRINGS.emailPlaceholder}
                required
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-purple-200 block mb-1">
                Admin Password
              </label>
              <CosmicInput
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                placeholder={ADMIN_STRINGS.passwordPlaceholder}
                required
              />
            </div>

            <CosmicButton
              type="submit"
              variant="primary"
              disabled={isLoggingIn}
              className="w-full py-2.5 text-xs font-bold"
            >
              {isLoggingIn ? "Validating Credentials..." : ADMIN_STRINGS.loginButton}
            </CosmicButton>
          </form>

          <div className="pt-2 text-center">
            <Link
              href="/"
              className="text-xs text-purple-400 hover:text-white flex items-center justify-center gap-1.5 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>{ADMIN_STRINGS.backToApp}</span>
            </Link>
          </div>
        </GlassPanel>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#07040D] text-white flex flex-col">
      {/* Top Admin Bar */}
      <header className="sticky top-0 z-40 glass-panel border-b border-purple-500/20 px-4 sm:px-8 py-3 flex items-center justify-between gap-4 backdrop-blur-xl bg-black/70">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="p-1.5 rounded-lg bg-purple-950/60 border border-purple-500/30 text-purple-300 hover:text-white transition-colors"
            title="Return to Public App"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-purple-400" />
              <span className="font-extrabold text-sm sm:text-base tracking-wide text-gradient">
                {ADMIN_STRINGS.headerTitle}
              </span>
              <Badge variant="purple" className="text-[10px] py-0 px-2 uppercase font-mono">
                {adminUser?.role || "super_admin"}
              </Badge>
            </div>
            <span className="text-[10px] text-purple-400/80 font-mono hidden sm:block">
              {ADMIN_STRINGS.headerSubtitle}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="p-2 rounded-xl bg-purple-900/40 hover:bg-purple-800/60 border border-purple-500/30 text-purple-200 hover:text-white transition-all"
            title="Refresh Ledger"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 rounded-xl bg-red-950/50 hover:bg-red-900/60 border border-red-500/30 text-red-300 hover:text-white text-xs font-semibold flex items-center gap-1.5 transition-all"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{ADMIN_STRINGS.logoutButton}</span>
          </button>
        </div>
      </header>

      {/* Main Console Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {apiError && (
          <div className="p-3.5 rounded-xl bg-red-950/60 border border-red-500/40 text-red-200 text-xs flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
              <span>{apiError}</span>
            </div>
            <button
              onClick={() => setApiError(null)}
              className="text-red-400 hover:text-white text-xs"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Tab Navigation (Responsive down to 320px) */}
        <div className="flex items-center gap-1.5 bg-purple-950/40 p-1.5 rounded-2xl border border-purple-500/20 overflow-x-auto scrollbar-none">
          {ADMIN_NAV_TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 sm:px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? "btn-cosmic text-white shadow-[0_0_15px_rgba(139,92,246,0.4)]"
                    : "text-purple-300 hover:text-white hover:bg-purple-900/30"
                }`}
              >
                {tab.iconName === "activity" && <Activity className="w-3.5 h-3.5" />}
                {tab.iconName === "users" && <Users className="w-3.5 h-3.5" />}
                {tab.iconName === "shieldAlert" && <ShieldAlert className="w-3.5 h-3.5" />}
                {tab.iconName === "sliders" && <Sliders className="w-3.5 h-3.5" />}
                {tab.iconName === "history" && <History className="w-3.5 h-3.5" />}
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className="px-1.5 py-0.2 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-mono border border-amber-500/40">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Active Tab View */}
        {activeTab === "telemetry" && (
          <TelemetryTab
            telemetry={telemetry}
            onUpdateDailyCap={handleUpdateDailyCap}
          />
        )}

        {activeTab === "tenants" && (
          <TenantsTab
            tenants={tenants}
            onSearch={(q) => {
              // Client-side search or refetch
              fetch(`${API_BASE}/api/v1/admin/tenants?search=${encodeURIComponent(q)}`, {
                headers: getHeaders()
              })
                .then((r) => r.json())
                .then((d) => setTenants(d));
            }}
            onChangePlan={handleChangeTenantPlan}
            isLoading={isLoading}
          />
        )}

        {activeTab === "upgrades" && (
          <UpgradesTab
            requests={upgrades}
            onApprove={handleApproveUpgrade}
            onReject={handleRejectUpgrade}
            isLoading={isLoading}
          />
        )}

        {activeTab === "plans" && (
          <PlansEditorTab
            plans={plans}
            onSavePlan={handleSavePlan}
            isLoading={isLoading}
          />
        )}

        {activeTab === "audit" && (
          <AuditLedgerTab
            logs={auditLogs}
            isLoading={isLoading}
          />
        )}
      </main>
    </div>
  );
}
