import React from "react";

export default function AboutSection() {
  return (
    <section id="about" className="max-w-6xl mx-auto px-4 py-10 scroll-mt-16">
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8">
        <h2 className="text-2xl md:text-3xl text-slate-100 font-bold">About InfraCostIQ</h2>
        <p className="text-slate-300 mt-4 leading-relaxed">
          InfraCostIQ is a cloud infrastructure cost estimation tool designed to help engineering teams
          quickly understand the financial impact of their infrastructure choices.
        </p>
        <p className="text-slate-300 mt-3 leading-relaxed">
          By comparing multiple hosting platforms side-by-side, it provides early-stage cost insights
          that help teams make informed architecture decisions.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-6">
          <div className="bg-slate-800/70 border border-slate-700 rounded-xl p-4 text-slate-200">
            <h3 className="font-semibold">Fast comparison</h3>
            <p className="text-sm text-slate-400 mt-1">Compare major platforms in one view.</p>
          </div>
          <div className="bg-slate-800/70 border border-slate-700 rounded-xl p-4 text-slate-200">
            <h3 className="font-semibold">Clear breakdown</h3>
            <p className="text-sm text-slate-400 mt-1">Understand compute, storage, network, and backup costs.</p>
          </div>
          <div className="bg-slate-800/70 border border-slate-700 rounded-xl p-4 text-slate-200">
            <h3 className="font-semibold">Planning support</h3>
            <p className="text-sm text-slate-400 mt-1">Use early cost estimates to guide architecture decisions.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
