"use client";
import React, { useState, useEffect } from "react";

const DarkModeToggle: React.FC = () => {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    if (dark) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  }, [dark]);

  return (
    <button
      className="px-3 py-1 border rounded mb-6 text-sm bg-white/10 hover:bg-white/20 transition"
      onClick={() => setDark(!dark)}
    >
      {dark ? "Light Mode" : "Dark Mode"}
    </button>
  );
};

export default DarkModeToggle;
