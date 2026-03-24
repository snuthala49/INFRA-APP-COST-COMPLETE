"use client";

import React from "react";

type TabKey = "product" | "about" | "contact";

interface Props {
  activeTab: TabKey;
  onTabClick: (tab: TabKey) => void;
}

const tabs: TabKey[] = ["product", "about", "contact"];

export default function Navbar({ activeTab, onTabClick }: Props) {
  return (
    <header className="sticky top-0 z-30 backdrop-blur-md bg-slate-950/70 border-b border-slate-800">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white shadow">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 7h18v4H3z" fill="currentColor" opacity="0.95" />
              <path d="M5 13h14v6H5z" fill="currentColor" opacity="0.75" />
            </svg>
          </div>
          <div>
            <div className="text-slate-100 font-semibold leading-none">InfraCostIQ</div>
            <div className="text-[11px] text-slate-400">Infrastructure cost intelligence</div>
          </div>
        </div>

        <nav className="flex items-center gap-1 overflow-x-auto">
          {tabs.map((tab) => {
            const isActive = activeTab === tab;
            return (
              <button
                key={tab}
                onClick={() => onTabClick(tab)}
                className={`px-3 py-1.5 rounded-md text-sm capitalize transition ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-slate-300 hover:text-white hover:bg-slate-800"
                }`}
              >
                {tab}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
