"use client";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { Brain, ListChecks, Zap, ChevronRight, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Sidebar } from "@/components/Sidebar";

export default function AssessmentIntroPage() {
  const router = useRouter();
  const params = useParams();
  const bookId = params.bookId as string;
  const [title, setTitle] = useState("this book");

  useEffect(() => {
    fetch(`/api/books/${bookId}`)
      .then(r => r.json())
      .then(d => setTitle(d.book?.title ?? "this book"));
  }, [bookId]);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 flex items-center justify-center p-6">
        <div className="max-w-lg w-full">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center h-16 w-16 bg-indigo-100 rounded-2xl mb-4">
              <Brain className="h-8 w-8 text-indigo-600" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mb-2">Placement assessment</h1>
            <p className="text-slate-600 leading-relaxed">
              We'll ask a few questions per topic to find out what you already know, so we don't teach you things you've already mastered.
            </p>
          </div>

          <div className="space-y-3 mb-8">
            <Card>
              <CardContent className="p-4 flex items-start gap-3">
                <ListChecks className="h-5 w-5 text-indigo-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-slate-900">Adaptive question flow</p>
                  <p className="text-sm text-slate-500">Questions escalate: MCQ → Theory → Applied. If you fail easy, we skip the whole branch.</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-start gap-3">
                <Zap className="h-5 w-5 text-amber-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-slate-900">Confidence check</p>
                  <p className="text-sm text-slate-500">You'll rate your confidence <em>before</em> seeing if you're right. Confident-but-wrong topics get priority revision later.</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-start gap-3">
                <BookOpen className="h-5 w-5 text-emerald-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-slate-900">Personalized starting point</p>
                  <p className="text-sm text-slate-500">After this, your graph shows exactly what's mastered, available, and locked — no blank slate.</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="text-center text-sm text-slate-500 mb-6">
            Takes about 5–15 minutes depending on the book. You can't skip it, but it's worth it.
          </div>

          <Button className="w-full" size="lg" onClick={() => router.push(`/book/${bookId}/assessment/question`)}>
            Begin assessment <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </main>
    </div>
  );
}
