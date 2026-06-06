"use client";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { Loader2, ChevronRight, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Sidebar } from "@/components/Sidebar";

interface Question {
  id: string;
  body: string;
  type: string;
  options?: string[];
  answer?: number;
}

const CONFIDENCE_OPTS = [
  { label: "Not sure", value: "not_sure", color: "bg-slate-100 text-slate-700 hover:bg-slate-200" },
  { label: "Fairly sure", value: "fairly_sure", color: "bg-amber-50 text-amber-700 hover:bg-amber-100 border-amber-200" },
  { label: "Certain", value: "certain", color: "bg-green-50 text-green-700 hover:bg-green-100 border-green-200" },
];

export default function AssessmentQuestionPage() {
  const router = useRouter();
  const params = useParams();
  const bookId = params.bookId as string;

  const [question, setQuestion] = useState<Question | null>(null);
  const [nodeId, setNodeId] = useState("");
  const [nodeTitle, setNodeTitle] = useState("");
  const [topicIndex, setTopicIndex] = useState(1);
  const [totalTopics, setTotalTopics] = useState(10);
  const [topoOrder, setTopoOrder] = useState<string[]>([]);
  const [topoIndex, setTopoIndex] = useState(0);

  const [confidence, setConfidence] = useState("");
  const [selected, setSelected] = useState<number | null>(null);
  const [freeText, setFreeText] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [branchStop, setBranchStop] = useState(false);
  const [loading, setLoading] = useState(true);
  const [nextLoading, setNextLoading] = useState(false);

  useEffect(() => {
    startAssessment();
  }, [bookId]);

  const startAssessment = async () => {
    setLoading(true);
    const res = await fetch("/api/assessment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bookId, action: "start" }),
    });
    const data = await res.json();
    if (data.done) { router.push(`/book/${bookId}/assessment/results`); return; }
    setQuestion(data.question);
    setNodeId(data.nodeId);
    setNodeTitle(data.nodeTitle);
    setTopicIndex(data.topicIndex);
    setTotalTopics(data.totalTopics);
    setTopoOrder(data.topoOrder ?? []);
    setLoading(false);
  };

  const submit = async () => {
    if (!confidence) return;
    setSubmitted(true);
    const answer = question?.type === "mcq" ? selected : freeText;

    const res = await fetch("/api/assessment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bookId, action: "answer", nodeId, answer, confidence, questionId: question?.id }),
    });
    const data = await res.json();
    setIsCorrect(data.correct);
    setBranchStop(!data.isMastered);
  };

  const next = async () => {
    setNextLoading(true);
    const nextIdx = topoIndex + 1;
    if (nextIdx >= topoOrder.length) {
      // Finalize
      await fetch("/api/assessment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bookId, action: "complete" }),
      });
      router.push(`/book/${bookId}/assessment/results`);
      return;
    }
    setTopoIndex(nextIdx);
    setTopicIndex(prev => prev + 1);
    setQuestion(null);
    setSubmitted(false);
    setSelected(null);
    setFreeText("");
    setConfidence("");
    setIsCorrect(null);
    setBranchStop(false);

    // Get next question for this node
    const res = await fetch("/api/assessment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bookId, action: "start", nodeIndex: nextIdx }),
    });
    const data = await res.json();
    setQuestion(data.question);
    setNodeId(data.nodeId ?? topoOrder[nextIdx]);
    setNodeTitle(data.nodeTitle ?? "");
    setNextLoading(false);
  };

  if (loading) return (
    <div className="flex min-h-screen"><Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </main>
    </div>
  );

  const pct = Math.round((topicIndex / totalTopics) * 100);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 p-6">
        <div className="max-w-2xl mx-auto">
          {/* Progress */}
          <div className="mb-6">
            <div className="flex items-center justify-between text-sm text-slate-500 mb-2">
              <span className="font-medium text-slate-700">{nodeTitle}</span>
              <span>Topic {topicIndex} of ~{totalTopics}</span>
            </div>
            <Progress value={pct} />
          </div>

          {question && (
            <Card className="mb-6">
              <CardContent className="p-6 space-y-5">
                {/* Tier badge */}
                <Badge variant="info" className="capitalize">{question.type}</Badge>

                {/* Question */}
                <p className="text-base font-medium text-slate-900 leading-relaxed">{question.body}</p>

                {/* Confidence (shown before submit) */}
                {!submitted && (
                  <div>
                    <p className="text-sm font-medium text-slate-700 mb-2">How confident are you?</p>
                    <div className="flex gap-2">
                      {CONFIDENCE_OPTS.map(opt => (
                        <button
                          key={opt.value}
                          onClick={() => setConfidence(opt.value)}
                          className={`flex-1 py-2 px-3 rounded-lg border text-sm font-medium transition-all ${
                            confidence === opt.value ? "ring-2 ring-indigo-500 " + opt.color : "border-slate-200 " + opt.color
                          }`}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Answer input */}
                {!submitted && question.type === "mcq" && question.options && (
                  <div className="space-y-2">
                    {question.options.map((opt, i) => (
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

                {!submitted && (question.type === "theory" || question.type === "applied") && (
                  <textarea
                    value={freeText}
                    onChange={e => setFreeText(e.target.value)}
                    placeholder="Type your answer..."
                    rows={4}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                  />
                )}

                {/* Feedback after submit */}
                {submitted && (
                  <div className={`flex items-start gap-3 p-4 rounded-xl ${isCorrect ? "bg-emerald-50 border border-emerald-200" : "bg-red-50 border border-red-200"}`}>
                    {isCorrect ? <CheckCircle className="h-5 w-5 text-emerald-600 mt-0.5" /> : <XCircle className="h-5 w-5 text-red-500 mt-0.5" />}
                    <div>
                      <p className={`text-sm font-medium ${isCorrect ? "text-emerald-700" : "text-red-700"}`}>
                        {isCorrect ? "Correct!" : "Not quite."}
                      </p>
                      {confidence === "certain" && !isCorrect && (
                        <p className="text-xs text-red-600 mt-1 flex items-center gap-1">
                          <AlertCircle className="h-3 w-3" /> You were certain but incorrect — flagged for priority revision.
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {branchStop && submitted && (
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm text-slate-600">
                    We'll cover <strong>{nodeTitle}</strong> and topics that build on it from scratch. Moving on.
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                  {!submitted ? (
                    <>
                      <Button variant="outline" onClick={() => { setConfidence("not_sure"); setSelected(null); submit(); }}>
                        I don't know
                      </Button>
                      <Button onClick={submit} disabled={!confidence || (question.type === "mcq" ? selected === null : !freeText.trim())} className="flex-1">
                        Submit answer
                      </Button>
                    </>
                  ) : (
                    <Button onClick={next} disabled={nextLoading} className="flex-1">
                      {nextLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <>Next topic <ChevronRight className="h-4 w-4" /></>}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}
