"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { CheckCircle, Loader2, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Sidebar } from "@/components/Sidebar";

interface RevisionCard {
  nodeId: string;
  nodeTitle: string;
  question: { body: string; options?: string[]; type: string; answer?: number };
  source: string;
}

const GRADES = [
  { label: "Again", value: "Again", color: "bg-red-100 text-red-700 hover:bg-red-200 border-red-200", desc: "Completely forgot" },
  { label: "Hard", value: "Hard", color: "bg-amber-100 text-amber-700 hover:bg-amber-200 border-amber-200", desc: "Recalled with effort" },
  { label: "Good", value: "Good", color: "bg-blue-100 text-blue-700 hover:bg-blue-200 border-blue-200", desc: "Recalled correctly" },
  { label: "Easy", value: "Easy", color: "bg-emerald-100 text-emerald-700 hover:bg-emerald-200 border-emerald-200", desc: "Recalled instantly" },
];

const CONFIDENCE_OPTS = [
  { label: "Not sure", value: "not_sure" },
  { label: "Fairly sure", value: "fairly_sure" },
  { label: "Certain", value: "certain" },
];

export default function RevisionSessionPage() {
  const params = useParams();
  const router = useRouter();
  const bookId = params.bookId as string;

  const [cards, setCards] = useState<RevisionCard[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [confidence, setConfidence] = useState("");
  const [selected, setSelected] = useState<number | null>(null);
  const [freeText, setFreeText] = useState("");
  const [revealed, setRevealed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [grading, setGrading] = useState(false);
  const [results, setResults] = useState<Array<{ nodeId: string; grade: string; nextDue: string }>>([]);
  const [done, setDone] = useState(false);

  useEffect(() => {
    // Build revision cards from due nodes
    fetch(`/api/books/${bookId}/daily-plan`)
      .then(r => r.json())
      .then(async plan => {
        const dueItems = (plan.planNodes ?? []).filter((n: { planType: string }) => n.planType === "revise").slice(0, 20);
        // For each, fetch questions or generate fallback
        const built: RevisionCard[] = await Promise.all(
          dueItems.map(async (item: { nodeId: string; node?: { title: string } }) => {
            const nodeRes = await fetch(`/api/books/${bookId}`).then(r => r.json());
            const node = nodeRes.book?.nodes?.find((n: { id: string }) => n.id === item.nodeId);
            const qs = node?.questions ?? [];
            const q = qs.find((x: { source: string }) => x.source === "user_asked") ?? qs[0] ?? {
              body: `Explain the concept of "${node?.title ?? item.nodeId}" in your own words.`,
              type: "theory",
            };
            return {
              nodeId: item.nodeId,
              nodeTitle: node?.title ?? item.nodeId,
              question: q,
              source: q.source ?? "generated",
            };
          })
        );
        setCards(built);
        setLoading(false);
      });
  }, [bookId]);

  const current = cards[currentIdx];

  const reveal = () => { if (confidence) setRevealed(true); };

  const grade = async (g: string) => {
    if (!current || grading) return;
    setGrading(true);

    const res = await fetch(`/api/nodes/${current.nodeId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grade: g, bookId }),
    });
    const data = await res.json();
    setResults(prev => [...prev, { nodeId: current.nodeId, grade: g, nextDue: data.nextDue }]);

    if (currentIdx + 1 >= cards.length) {
      setDone(true);
    } else {
      setCurrentIdx(i => i + 1);
      setConfidence("");
      setSelected(null);
      setFreeText("");
      setRevealed(false);
    }
    setGrading(false);
  };

  if (loading) return (
    <div className="flex min-h-screen"><Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </main>
    </div>
  );

  if (cards.length === 0) return (
    <div className="flex min-h-screen"><Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 flex items-center justify-center p-6">
        <div className="text-center">
          <CheckCircle className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
          <h2 className="text-xl font-bold text-slate-900 mb-2">Nothing due!</h2>
          <p className="text-slate-500 mb-4">You're all caught up on reviews.</p>
          <Button onClick={() => router.push(`/book/${bookId}`)}>Back to book</Button>
        </div>
      </main>
    </div>
  );

  if (done) {
    const gradeCount: Record<string, number> = {};
    results.forEach(r => { gradeCount[r.grade] = (gradeCount[r.grade] ?? 0) + 1; });
    return (
      <div className="flex min-h-screen"><Sidebar />
        <main className="flex-1 ml-16 lg:ml-56 flex items-center justify-center p-6">
          <div className="max-w-md w-full text-center">
            <div className="h-20 w-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="h-10 w-10 text-emerald-600" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mb-2">Session complete!</h1>
            <p className="text-slate-500 mb-6">You reviewed {results.length} concepts. Schedules updated.</p>

            <div className="grid grid-cols-4 gap-2 mb-6">
              {GRADES.map(g => (
                <Card key={g.label}>
                  <CardContent className="p-3 text-center">
                    <p className="text-xl font-bold text-slate-900">{gradeCount[g.label] ?? 0}</p>
                    <p className={`text-xs ${g.color.split(" ")[1]}`}>{g.label}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Button className="w-full" onClick={() => router.push(`/book/${bookId}`)}>
              Back to daily plan
            </Button>
          </div>
        </main>
      </div>
    );
  }

  const pct = Math.round((currentIdx / cards.length) * 100);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 p-6">
        <div className="max-w-2xl mx-auto">
          {/* Progress */}
          <div className="flex items-center justify-between text-sm text-slate-500 mb-2">
            <span>{currentIdx + 1} of {cards.length}</span>
            <span>{100 - pct}% remaining</span>
          </div>
          <Progress value={pct} className="mb-6" />

          <Card className="shadow-sm">
            <CardContent className="p-6 space-y-5">
              {/* Source badge */}
              <div className="flex items-center gap-2">
                <Badge variant={current?.source === "user_asked" ? "info" : current?.source === "assessment_miss" ? "warning" : "secondary"} className="text-xs">
                  {current?.source === "user_asked" ? "Your question" : current?.source === "assessment_miss" ? "Assessment miss" : "Practice"}
                </Badge>
                <span className="text-sm font-medium text-slate-700">{current?.nodeTitle}</span>
              </div>

              {/* Question */}
              <p className="text-base font-medium text-slate-900 leading-relaxed">{current?.question.body}</p>

              {/* Confidence (before reveal) */}
              {!revealed && (
                <div>
                  <p className="text-sm font-medium text-slate-700 mb-2">How confident are you?</p>
                  <div className="flex gap-2">
                    {CONFIDENCE_OPTS.map(opt => (
                      <button
                        key={opt.value}
                        onClick={() => setConfidence(opt.value)}
                        className={`flex-1 py-2 px-2 rounded-lg border text-sm font-medium transition-all ${
                          confidence === opt.value ? "ring-2 ring-indigo-500 bg-indigo-50 border-indigo-300" : "border-slate-200 hover:bg-slate-50"
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* MCQ options */}
              {!revealed && current?.question.type === "mcq" && current.question.options && (
                <div className="space-y-2">
                  {current.question.options.map((opt, i) => (
                    <button
                      key={i}
                      onClick={() => setSelected(i)}
                      className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition-all ${
                        selected === i ? "border-indigo-500 bg-indigo-50 text-indigo-700" : "border-slate-200 hover:border-slate-300"
                      }`}
                    >
                      <span className="font-medium mr-2">{String.fromCharCode(65 + i)}.</span>{opt}
                    </button>
                  ))}
                </div>
              )}

              {!revealed && current?.question.type !== "mcq" && (
                <textarea
                  value={freeText}
                  onChange={e => setFreeText(e.target.value)}
                  placeholder="Write your answer..."
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                />
              )}

              {/* Reveal button */}
              {!revealed && (
                <Button
                  onClick={reveal}
                  disabled={!confidence}
                  className="w-full"
                  variant="outline"
                >
                  Show answer
                </Button>
              )}

              {/* Answer revealed */}
              {revealed && (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                  <p className="text-xs font-semibold text-slate-500 mb-1">Answer</p>
                  <p className="text-sm text-slate-800">
                    {current?.question.type === "mcq" && current.question.options
                      ? current.question.options[current.question.answer ?? 0]
                      : "Review the concept and rate your recall."}
                  </p>
                </div>
              )}

              {/* FSRS grade buttons */}
              {revealed && (
                <div>
                  <p className="text-sm font-medium text-slate-700 mb-2">How well did you recall it?</p>
                  <div className="grid grid-cols-4 gap-2">
                    {GRADES.map(g => (
                      <button
                        key={g.value}
                        onClick={() => grade(g.value)}
                        disabled={grading}
                        className={`py-3 px-2 rounded-lg border text-sm font-medium transition-all ${g.color}`}
                      >
                        <div>{g.label}</div>
                        <div className="text-[10px] mt-0.5 opacity-70">{g.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
