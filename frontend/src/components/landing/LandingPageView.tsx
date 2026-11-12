"use client";

import React, { useState } from "react";
import { HeroSection } from "@/components/landing/HeroSection";
import { HowItWorksSection } from "@/components/landing/HowItWorksSection";
import { LivePlanComparison } from "@/components/landing/LivePlanComparison";
import { FeaturesSection } from "@/components/landing/FeaturesSection";
import { FaqSection } from "@/components/landing/FaqSection";
import { Footer } from "@/components/landing/Footer";
import { OnboardingModal } from "@/components/onboarding/OnboardingModal";
import { AuthModal } from "@/components/auth/AuthModal";

interface LandingPageViewProps {
  onEnterStudio: () => void;
  onEnterDashboard: () => void;
  onViewPlans: () => void;
}

export const LandingPageView: React.FC<LandingPageViewProps> = ({
  onEnterStudio,
  onEnterDashboard,
  onViewPlans
}) => {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState<boolean>(false);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState<boolean>(false);
  const [upgradeRequestedPlan, setUpgradeRequestedPlan] = useState<string | null>(null);

  const handleStartFree = () => {
    // Open onboarding flow directly
    setIsOnboardingOpen(true);
  };

  const handleSelectPlan = (planId: string) => {
    if (planId === "free") {
      setIsOnboardingOpen(true);
    } else {
      setUpgradeRequestedPlan(planId);
      setIsAuthModalOpen(true);
    }
  };

  const handleRequestUpgrade = (planId: string) => {
    setUpgradeRequestedPlan(planId);
    alert(`Upgrade Request initiated for ${planId.toUpperCase()}. Please sign in or submit your request to the administrator.`);
    setIsAuthModalOpen(true);
  };

  const handleOnboardingComplete = (data: { studioName: string; niche: string; voice: string }) => {
    // Lead user straight into the Studio view
    onEnterStudio();
  };

  const handleAuthSuccess = () => {
    setIsAuthModalOpen(false);
    onEnterStudio();
  };

  return (
    <div className="w-full flex flex-col min-h-screen">
      {/* 1. Hero Showcase */}
      <HeroSection
        onStartFree={handleStartFree}
        onViewPlans={onViewPlans}
      />

      {/* 2. 3-Step How It Works */}
      <HowItWorksSection />

      {/* 3. Live Database Plan Comparison */}
      <LivePlanComparison
        onSelectPlan={handleSelectPlan}
        onRequestUpgrade={handleRequestUpgrade}
      />

      {/* 4. Enterprise Features */}
      <FeaturesSection />

      {/* 5. FAQ Accordion */}
      <FaqSection />

      {/* 6. Footer with navigation */}
      <Footer
        onNavigate={(view) => {
          if (view === "studio") onEnterStudio();
          else if (view === "dashboard") onEnterDashboard();
          else if (view === "plans") onViewPlans();
          else window.scrollTo({ top: 0, behavior: "smooth" });
        }}
      />

      {/* Modals */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      <OnboardingModal
        isOpen={isOnboardingOpen}
        onClose={() => setIsOnboardingOpen(false)}
        onComplete={handleOnboardingComplete}
      />
    </div>
  );
};
