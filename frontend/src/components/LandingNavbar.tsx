"use client";
import Link from "next/link";
import { useState } from "react";
import { BrainCircuit, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const links = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#benefits", label: "Benefits" },
];

export function LandingNavbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="inline-flex items-center justify-center w-9 h-9 bg-indigo-600 rounded-xl shadow-sm">
            <BrainCircuit className="h-5 w-5 text-white" />
          </div>
          <span className="font-bold text-slate-900 text-lg">Lexis</span>
        </Link>

        {/* Desktop nav links */}
        <nav className="hidden md:flex items-center gap-8">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              {l.label}
            </a>
          ))}
        </nav>

        {/* Desktop CTAs */}
        <div className="hidden md:flex items-center gap-2">
          <Link href="/login">
            <Button variant="ghost" size="sm">Sign in</Button>
          </Link>
          <Link href="/login">
            <Button size="sm">Get Started</Button>
          </Link>
        </div>

        {/* Mobile menu toggle */}
        <button
          onClick={() => setOpen((v) => !v)}
          className="md:hidden p-2 text-slate-600 hover:text-slate-900"
          aria-label="Toggle menu"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile menu panel */}
      {open && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 sm:px-6 py-4 space-y-3">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className="block text-sm font-medium text-slate-600 hover:text-slate-900 py-1.5"
            >
              {l.label}
            </a>
          ))}
          <div className="flex flex-col gap-2 pt-2">
            <Link href="/login" onClick={() => setOpen(false)}>
              <Button variant="outline" className="w-full">Sign in</Button>
            </Link>
            <Link href="/login" onClick={() => setOpen(false)}>
              <Button className="w-full">Get Started</Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
