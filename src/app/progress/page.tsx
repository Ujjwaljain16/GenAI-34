"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Flame, BookOpen, TrendingUp, AlertTriangle, Trophy, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ProgressRing } from "@/components/ProgressRing";
import { Sidebar } from "@/components/Sidebar";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function ProgressPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [books, setBooks] = useState<Record<string, unknown>[]>([]);
  const [user, setUser] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === "unauthenticated") { router.push("/"); return; }
    if (status !== "authenticated") return;

    Promise.all([
      fetch("/api/books").then(r => r.json()),
      fetch("/api/user").then(r => r.json()),
    ]).then(([booksData, userData]) => {
      setBooks(booksData.books ?? []);
      setUser(userData.user ?? null);
      setLoading(false);
    });
  }, [status, router]);

  const totalMastered = books.reduce((s, b) => s + ((b.masteredNodes as number) ?? 0), 0);
  const totalNodes = books.reduce((s, b) => s + ((b.totalNodes as number) ?? 0), 0);
  const retentionRate = 87; // mock

  // Mock chart data
  const chartData = Array.from({ length: 14 }, (_, i) => ({
    day: new Date(Date.now() - (13 - i) * 86400000).toLocaleDateString("en", { weekday: "short" }),
    mastered: Math.max(0, totalMastered - (13 - i) * 2 + Math.floor(Math.random() * 3)),
  }));

  if (loading) return (
    <div className="flex min-h-screen"><Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </main>
    </div>
  );

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 p-6 max-w-4xl">
        <h1 className="text-2xl font-bold text-slate-900 mb-6">Progress</h1>

        {/* Global stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="h-10 w-10 bg-emerald-100 rounded-xl flex items-center justify-center">
                <Trophy className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{totalMastered}</p>
                <p className="text-xs text-slate-500">Concepts mastered</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="h-10 w-10 bg-indigo-100 rounded-xl flex items-center justify-center">
                <BookOpen className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{books.length}</p>
                <p className="text-xs text-slate-500">Books active</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="h-10 w-10 bg-orange-100 rounded-xl flex items-center justify-center">
                <Flame className="h-5 w-5 text-orange-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{(user?.globalStreak as number) ?? 0}</p>
                <p className="text-xs text-slate-500">Day streak</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="h-10 w-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{retentionRate}%</p>
                <p className="text-xs text-slate-500">Retention rate</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Chart */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-base">Concepts mastered over time</CardTitle>
          </CardHeader>
          <CardContent>
            {totalMastered === 0 ? (
              <div className="h-40 flex items-center justify-center text-sm text-slate-400">
                Start learning to see your progress chart.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={160}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="mastered" stroke="#6366f1" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Per-book breakdown */}
        <h2 className="font-semibold text-slate-900 mb-4">Books</h2>
        {books.length === 0 ? (
          <p className="text-sm text-slate-500">No books yet — <button onClick={() => router.push("/upload")} className="text-indigo-600 hover:underline">upload one</button>.</p>
        ) : (
          <div className="space-y-4">
            {books.map(book => {
              const pct = (book.totalNodes as number) > 0 ? Math.round(((book.masteredNodes as number) / (book.totalNodes as number)) * 100) : 0;
              return (
                <Card key={book.id as string} className="cursor-pointer hover:shadow-sm transition-shadow" onClick={() => router.push(`/book/${book.id}`)}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      <ProgressRing pct={pct} size={52} stroke={5} />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-slate-900 truncate">{book.title as string}</p>
                        <div className="flex items-center gap-3 mt-1">
                          <span className="text-xs text-slate-500">{book.masteredNodes as number}/{book.totalNodes as number} mastered</span>
                          {(book.dueToday as number) > 0 && (
                            <Badge variant="due" className="text-[10px]">{book.dueToday as number} due</Badge>
                          )}
                          {(book.bookStreak as number) > 0 && (
                            <span className="text-xs text-orange-500 flex items-center gap-0.5">
                              <Flame className="h-3 w-3" />{book.bookStreak as number}d
                            </span>
                          )}
                        </div>
                        <Progress value={pct} className="mt-2 h-1.5" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
