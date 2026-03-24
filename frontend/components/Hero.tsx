"use client";

import React from "react";

interface Props {
  onTryCalculator: () => void;
  onLearnMore: () => void;
}

export default function Hero({ onTryCalculator, onLearnMore }: Props) {
  return (
    <section className="max-w-6xl mx-auto px-4 pt-10 pb-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
          <p className="text-xs uppercase tracking-[0.14em] text-blue-300 mb-3">Cloud Cost Planning</p>
          <h1 className="text-3xl md:text-5xl font-bold text-slate-100 leading-tight">
            Estimate Your Application Infrastructure Cost
          </h1>
          <p className="text-slate-300 mt-4 leading-relaxed">
            Quickly estimate and compare the cost of running your application across multiple hosting
            platforms including AWS, Azure, Google Cloud, Kubernetes, and on-prem environments.
          </p>
          <p className="text-slate-400 mt-3 text-sm leading-relaxed">
            Application teams often struggle to estimate infrastructure costs and decide which hosting
            platform best fits their needs. InfraCostIQ provides an initial cost comparison to help guide
            infrastructure planning and platform decisions.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button onClick={onTryCalculator} className="px-5 py-2.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold">
              Try Calculator
            </button>
            <button onClick={onLearnMore} className="px-5 py-2.5 rounded-md border border-slate-700 hover:border-slate-500 text-slate-200 text-sm font-semibold">
              Learn More
            </button>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-slate-100 font-semibold mb-4">Quick Estimate Preview</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between text-slate-300"><span>CPU</span><span>4 vCPU</span></div>
            <div className="flex justify-between text-slate-300"><span>RAM</span><span>16 GB</span></div>
            <div className="flex justify-between text-slate-300"><span>Storage</span><span>100 GB</span></div>
          </div>
          <div className="mt-5 pt-4 border-t border-slate-800 space-y-2 text-sm">
            <div className="flex justify-between text-slate-300"><span>AWS Estimate</span><span>$120/mo</span></div>
            <div className="flex justify-between text-slate-300"><span>Azure Estimate</span><span>$118/mo</span></div>
            <div className="flex justify-between text-slate-300"><span>GCP Estimate</span><span>$110/mo</span></div>
          </div>
          <button onClick={onTryCalculator} className="mt-5 w-full px-4 py-2 rounded-md bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold">
            Try Calculator
          </button>
        </div>
      </div>
    </section>
  );
}
