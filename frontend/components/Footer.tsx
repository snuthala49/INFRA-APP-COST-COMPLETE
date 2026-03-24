import React from "react";

export default function Footer() {
  return (
    <footer className="max-w-6xl mx-auto px-4 py-8 border-t border-slate-800 mt-10">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 text-sm text-slate-400">
        <div className="flex items-center gap-4">
          <a href="https://github.com/snuthala49/INFRA-APP-COST-COMPLETE" target="_blank" rel="noopener noreferrer" className="hover:text-slate-200">GitHub</a>
          <a href="https://www.linkedin.com/company/infracostiq/?viewAsMember=true" target="_blank" rel="noopener noreferrer" className="hover:text-slate-200">LinkedIn</a>
        </div>
        <div>© {new Date().getFullYear()} InfraCostIQ</div>
      </div>
    </footer>
  );
}
