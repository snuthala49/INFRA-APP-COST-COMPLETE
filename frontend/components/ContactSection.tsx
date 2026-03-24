"use client";

import React, { useState } from "react";

const WEB3FORMS_ACCESS_KEY = "f3d4e040-7f72-492d-be54-2d733681b427";

export default function ContactSection() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitted(false);
    setError("");
    setSubmitting(true);

    try {
      const res = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          access_key: WEB3FORMS_ACCESS_KEY,
          name,
          email,
          message,
          subject: `InfraCostIQ Contact Form: ${name}`,
        }),
      });

      const data = await res.json();

      if (!res.ok || data.success === false) {
        throw new Error(data?.message || "Submission failed");
      }

      setSubmitted(true);
      setName("");
      setEmail("");
      setMessage("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to send message. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section id="contact" className="max-w-6xl mx-auto px-4 py-10 scroll-mt-16">
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 max-w-2xl">
        <h2 className="text-2xl md:text-3xl text-slate-100 font-bold">Contact</h2>
        <p className="text-slate-300 mt-3">Share your use case and we can help refine your cost planning approach.</p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <input
            className="w-full px-3 py-2 rounded-md bg-slate-800 border border-slate-700 text-slate-100 placeholder:text-slate-400"
            placeholder="Name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <input
            type="email"
            className="w-full px-3 py-2 rounded-md bg-slate-800 border border-slate-700 text-slate-100 placeholder:text-slate-400"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <textarea
            className="w-full px-3 py-2 rounded-md bg-slate-800 border border-slate-700 text-slate-100 placeholder:text-slate-400 min-h-28"
            placeholder="Message"
            required
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <button
            type="submit"
            disabled={submitting}
            className="px-5 py-2.5 rounded-md bg-blue-600 hover:bg-blue-500 disabled:opacity-60 disabled:cursor-not-allowed text-white text-sm font-semibold"
          >
            {submitting ? "Sending..." : "Send Message"}
          </button>
          {submitted && <p className="text-emerald-400 text-sm">Thanks for Contacting. !! Will getback to you ASAP !!</p>}
          {error && <p className="text-rose-400 text-sm">{error}</p>}
        </form>
      </div>
    </section>
  );
}
