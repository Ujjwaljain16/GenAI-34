import Link from "next/link";
import {
  BrainCircuit, Upload, GitBranch, Target, BookOpen, Flame, TrendingUp,
  Trophy, MessageSquareText, RotateCcw, ArrowRight, CheckCircle2, Star,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LandingNavbar } from "@/components/LandingNavbar";
import { LandingFooter } from "@/components/LandingFooter";

const features = [
  {
    icon: GitBranch,
    iconBg: "bg-indigo-100",
    iconColor: "text-indigo-600",
    title: "Knowledge Graphs",
    description:
      "Lexis breaks any book into concepts and prerequisites, mapping exactly what depends on what — so you never study out of order.",
  },
  {
    icon: Target,
    iconBg: "bg-blue-100",
    iconColor: "text-blue-600",
    title: "Adaptive Assessment",
    description:
      "A quick diagnostic finds what you already know and routes you straight to your real knowledge gaps, skipping what you've mastered.",
  },
  {
    icon: MessageSquareText,
    iconBg: "bg-emerald-100",
    iconColor: "text-emerald-600",
    title: "Socratic Tutoring",
    description:
      "Learn through guided questioning anchored strictly to the book's own text — never generic, never off-topic.",
  },
  {
    icon: RotateCcw,
    iconBg: "bg-orange-100",
    iconColor: "text-orange-600",
    title: "Spaced Repetition (FSRS)",
    description:
      "A research-backed scheduler resurfaces concepts right before you'd forget them, building durable, long-term retention.",
  },
  {
    icon: BookOpen,
    iconBg: "bg-purple-100",
    iconColor: "text-purple-600",
    title: "Any Book, Any Format",
    description:
      "Upload PDF, EPUB, or TXT files and Lexis turns static chapters into an interactive, personalized curriculum.",
  },
  {
    icon: Flame,
    iconBg: "bg-amber-100",
    iconColor: "text-amber-600",
    title: "Streaks & Progress Tracking",
    description:
      "Daily streaks, mastery rings, and retention charts keep you motivated and show your growth at a glance.",
  },
];

const steps = [
  {
    number: "1",
    icon: Upload,
    title: "Upload your book",
    description:
      "Drop in a PDF, EPUB, or TXT file. Lexis parses it and extracts a knowledge graph of concepts and dependencies.",
  },
  {
    number: "2",
    icon: Target,
    title: "Take the diagnostic",
    description:
      "A short adaptive assessment measures your baseline mastery across the graph — no wasted time on what you know.",
  },
  {
    number: "3",
    icon: TrendingUp,
    title: "Learn & retain daily",
    description:
      "Follow your personalized curriculum, tutor concept-by-concept, and let spaced repetition lock in retention.",
  },
];

const benefits = [
  "Never study a prerequisite gap by accident again",
  "Spend time only on concepts you haven't mastered",
  "Retain what you learn with science-backed spaced repetition",
  "Get Socratic guidance anchored to the actual book text",
  "Track mastery, streaks, and retention in one dashboard",
  "Works with any PDF, EPUB, or TXT — your books, your pace",
];

const stats = [
  { label: "Concepts mapped per book", value: "100s", icon: GitBranch },
  { label: "Retention improvement focus", value: "FSRS", icon: RotateCcw },
  { label: "Built for", value: "Every learner", icon: Trophy },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <LandingNavbar />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-indigo-50 via-white to-slate-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-600 rounded-2xl mb-6 shadow-lg">
            <BrainCircuit className="h-9 w-9 text-white" />
          </div>

          <Badge variant="info" className="mb-4">Adaptive learning, reimagined</Badge>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 tracking-tight max-w-3xl mx-auto">
            Learn any book deeply — one concept at a time
          </h1>

          <p className="text-lg text-slate-500 mt-6 max-w-2xl mx-auto">
            Lexis turns static textbooks into interactive, personalized learning graphs.
            Upload a book, get assessed, and follow an adaptive curriculum built on
            knowledge graphs, Socratic tutoring, and spaced repetition.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-10">
            <Button asChild size="lg" className="px-8">
              <Link href="/login">
                Get Started
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="px-8">
              <a href="#how-it-works">
                See how it works
              </a>
            </Button>
          </div>

          <p className="text-xs text-slate-400 mt-6">
            Free to start. No credit card required.
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold text-slate-900">
              Everything you need to actually learn
            </h2>
            <p className="text-slate-500 mt-3">
              Not another e-reader. Lexis is a full learning engine built around how
              memory and understanding actually work.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((f) => (
              <Card key={f.title} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className={`h-10 w-10 ${f.iconBg} rounded-xl flex items-center justify-center mb-4`}>
                    <f.icon className={`h-5 w-5 ${f.iconColor}`} />
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">{f.title}</h3>
                  <p className="text-sm text-slate-500">{f.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold text-slate-900">How it works</h2>
            <p className="text-slate-500 mt-3">
              Three steps from a raw book file to a personalized, retained curriculum.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {steps.map((s, i) => (
              <div key={s.number} className="relative">
                <Card className="h-full">
                  <CardContent className="p-6 flex flex-col items-center text-center">
                    <div className="h-12 w-12 bg-indigo-600 rounded-2xl flex items-center justify-center mb-4 shadow-sm">
                      <s.icon className="h-6 w-6 text-white" />
                    </div>
                    <Badge variant="secondary" className="mb-3">Step {s.number}</Badge>
                    <h3 className="font-semibold text-slate-900 mb-2">{s.title}</h3>
                    <p className="text-sm text-slate-500">{s.description}</p>
                  </CardContent>
                </Card>
                {i < steps.length - 1 && (
                  <div className="hidden sm:flex absolute top-1/2 -right-3 -translate-y-1/2 z-10">
                    <ArrowRight className="h-5 w-5 text-slate-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="benefits" className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-4">
                Why learners choose Lexis
              </h2>
              <p className="text-slate-500 mb-8">
                Traditional textbooks assume every reader starts at the same place
                and learns at the same speed. Lexis adapts to you instead.
              </p>

              <ul className="space-y-3">
                {benefits.map((b) => (
                  <li key={b} className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
                    <span className="text-sm text-slate-700">{b}</span>
                  </li>
                ))}
              </ul>

              <Button asChild size="lg" className="inline-block mt-8">
                <Link href="/login">
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            </div>

            {/* Visual / stats card */}
            <Card className="overflow-hidden">
              <div className="h-40 bg-gradient-to-br from-indigo-400 to-purple-600 flex items-center justify-center">
                <BrainCircuit className="h-14 w-14 text-white/80" />
              </div>
              <CardContent className="p-6">
                <div className="grid grid-cols-1 gap-4">
                  {stats.map((s) => (
                    <div key={s.label} className="flex items-center gap-3">
                      <div className="h-10 w-10 bg-slate-100 rounded-xl flex items-center justify-center">
                        <s.icon className="h-5 w-5 text-indigo-600" />
                      </div>
                      <div>
                        <p className="text-lg font-bold text-slate-900">{s.value}</p>
                        <p className="text-xs text-slate-500">{s.label}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Built for focused learners</h2>
            <p className="text-slate-500 mt-3">
              Early feedback from people using Lexis to work through dense material.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                quote:
                  "The knowledge graph approach finally explained why I kept getting lost in advanced chapters — I was missing prerequisites I didn't know existed.",
                name: "Graduate researcher",
                role: "Computer Science",
              },
              {
                quote:
                  "Spaced repetition combined with the Socratic tutor made dense technical material actually stick instead of fading after a week.",
                name: "Self-taught engineer",
                role: "Backend development",
              },
              {
                quote:
                  "Being routed straight to my actual gaps instead of re-reading chapters I already understood saved a huge amount of time.",
                name: "Lifelong learner",
                role: "Independent study",
              },
            ].map((t) => (
              <Card key={t.name}>
                <CardContent className="p-6">
                  <div className="flex gap-0.5 mb-3">
                    {Array.from({ length: 5 }).map((_, idx) => (
                      <Star key={idx} className="h-4 w-4 text-amber-400 fill-amber-400" />
                    ))}
                  </div>
                  <p className="text-sm text-slate-600 mb-4">&ldquo;{t.quote}&rdquo;</p>
                  <p className="text-sm font-semibold text-slate-900">{t.name}</p>
                  <p className="text-xs text-slate-500">{t.role}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="bg-indigo-600 border-indigo-600 overflow-hidden">
            <CardContent className="p-10 sm:p-12 text-center">
              <h2 className="text-3xl font-bold text-white mb-3">
                Ready to learn smarter?
              </h2>
              <p className="text-indigo-100 mb-8 max-w-xl mx-auto">
                Upload your first book and let Lexis build your personalized
                knowledge graph in minutes.
              </p>
              <Button asChild size="lg" variant="secondary" className="px-8">
                <Link href="/login">
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      <LandingFooter />
    </div>
  );
}