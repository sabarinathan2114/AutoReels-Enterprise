"use client";

import React, { useState } from "react";
import { ChevronDown } from "lucide-react";
import { GlassPanel } from "@/components/common/GlassPanel";
import { Badge } from "@/components/common/Badge";
import { FAQ_ITEMS } from "@/components/hardcodedata";

export const FaqSection: React.FC = () => {
  const [openId, setOpenId] = useState<string | null>(FAQ_ITEMS[0].id);

  const toggle = (id: string) => {
    setOpenId(openId === id ? null : id);
  };

  return (
    <section className="py-12 md:py-20 border-t border-purple-900/30 relative">
      <div className="max-w-4xl mx-auto px-3 sm:px-6">
        <div className="text-center mb-10 sm:mb-14">
          <Badge variant="purple" className="mb-3">Answers & Clarifications</Badge>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Frequently Asked Questions
          </h2>
          <p className="text-slate-400 text-sm sm:text-base mt-2">
            Everything you need to know about our zero-cost generation architecture and multi-tenant setup.
          </p>
        </div>

        <div className="space-y-4">
          {FAQ_ITEMS.map((item) => {
            const isOpen = openId === item.id;
            return (
              <GlassPanel
                key={item.id}
                className="p-5 border-purple-800/30 transition-all duration-200"
              >
                <button
                  type="button"
                  onClick={() => toggle(item.id)}
                  className="w-full flex items-center justify-between text-left gap-4 focus:outline-none"
                >
                  <span className="text-sm sm:text-base font-semibold text-white">
                    {item.question}
                  </span>
                  <ChevronDown
                    className={`w-5 h-5 text-purple-400 shrink-0 transition-transform duration-300 ${
                      isOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>

                {isOpen && (
                  <div className="mt-3 pt-3 border-t border-purple-900/20 text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {item.answer}
                  </div>
                )}
              </GlassPanel>
            );
          })}
        </div>
      </div>
    </section>
  );
};
