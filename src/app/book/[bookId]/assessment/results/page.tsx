"use client";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { CheckCircle, BookOpen, Lock, AlertTriangle, Map, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Sidebar } from "@/components/Sidebar";

export default function AssessmentResultsPage() {
  const router = useRouter();
  const params = useParams();
  const bookId = params.bookId as string;

  const [results, setResults] = useState({ mastered: 0, available: 0, locked: 0, weakSpots: [] as string[] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/assessment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bookId, action: "complete" }),
    })
      .then(r => r.json())
      .then(d => { setResults(d); setLoading(false); });
  }, [bookId]);

  const total = results.mastered + results.available + results.locked;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 flex items-center justify-center p-6">
        <div className="max-w-lg w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Here's where you're starting.</h1>
            <p className="text-slate-500">We've mapped your knowledge so you don't repeat what you already know.</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-3 mb-8">
            <Card className="text-center p-4">
              <CheckCircle className="h-6 w-6 text-emerald-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-slate-900">{results.mastered}</p>
              <p className="text-xs text-slate-500">Already mastered</p>
            </Card>
            <Card className="text-center p-4">
              <BookOpen className="h-6 w-6 text-indigo-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-slate-900">{results.available}</p>
              <p className="text-xs text-slate-500">Ready to learn</p>
            </Card>
            <Card className="text-center p-4">
              <Lock className="h-6 w-6 text-slate-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-slate-900">{results.locked}</p>
              <p className="text-xs text-slate-500">Locked (prereqs first)</p>
            </Card>
          </div>

          {/* Progress bar */}
          {total > 0 && (
            <div className="mb-6">
              <div className="flex rounded-full overflow-hidden h-3">
                <div className="bg-emerald-500 transition-all" style={{ width: `${(results.mastered / total) * 100}%` }} />
                <div className="bg-indigo-400 transition-all" style={{ width: `${(results.available / total) * 100}%` }} />
                <div className="bg-slate-200 transition-all" style={{ width: `${(results.locked / total) * 100}%` }} />
              </div>
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>Mastered</span><span>Available</span><span>Locked</span>
              </div>
            </div>
          )}

          {/* Weak spots */}
          {results.weakSpots?.length > 0 && (
            <Card className="mb-6 border-amber-200">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                  <p className="text-sm font-medium text-amber-700">Confident-but-wrong topics — priority revision later</p>
                </div>
                <ul className="space-y-1">
                  {results.weakSpots.map((s, i) => (
                    <li key={i} className="text-xs text-slate-600 flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-amber-400 shrink-0" />{s}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* CTAs */}
          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline" onClick={() => router.push(`/book/${bookId}/graph`)}>
              <Map className="h-4 w-4" /> See my graph
            </Button>
            <Button onClick={() => router.push(`/book/${bookId}`)}>
              Start learning <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
