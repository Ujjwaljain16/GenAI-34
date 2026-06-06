/**
 * FSRS-4.5 implementation
 * Free Spaced Repetition Scheduler — the scheduling engine behind the daily plan.
 * Each node carries: stability (S), difficulty (D), recall probability (R).
 * nextDue = lastReview + interval derived from S and target retention.
 */

export type FSRSGrade = 1 | 2 | 3 | 4; // Again | Hard | Good | Easy

export interface FSRSCard {
  stability: number;       // S — how long memory survives (days)
  difficulty: number;      // D — 0–1, higher = harder
  recallProbability: number; // R — current recall chance 0–1
  lapseCount: number;
  reviewCount: number;
  lastReviewed: string | null;
  nextDue: string | null;
}

export interface FSRSResult {
  stability: number;
  difficulty: number;
  recallProbability: number;
  interval: number;         // days until next review
  nextDue: string;
}

// FSRS-4.5 default parameters
const W = [
  0.4072, 1.1829, 3.1262, 15.4722,
  7.2102, 0.5316, 1.0651, 0.0589,
  1.5330, 0.1544, 1.0050, 2.0037,
  0.1425, 0.1097, 0.2259, 2.9898,
  0.5100, 0.3567, 0.0100,
];

const DECAY = -0.5;
const FACTOR = 19 / 81; // 0.9 ** (1/DECAY) - 1 roughly
const TARGET_RETENTION = 0.9;

function forgettingCurve(t: number, s: number): number {
  return Math.pow(1 + FACTOR * (t / s), DECAY);
}

function initDifficulty(grade: FSRSGrade): number {
  return W[4] - Math.exp(W[5] * (grade - 1)) + 1;
}

function initStability(grade: FSRSGrade): number {
  return Math.max(W[grade - 1], 0.1);
}

function nextInterval(stability: number): number {
  return Math.max(
    1,
    Math.round(stability / FACTOR * (Math.pow(TARGET_RETENTION, 1 / DECAY) - 1))
  );
}

function nextDifficulty(d: number, grade: FSRSGrade): number {
  const delta = W[6] * (grade - 3);
  return Math.min(10, Math.max(1, d - delta + W[7] * (10 - d) * (grade - 1)));
}

function nextRecallStability(s: number, d: number, r: number, grade: FSRSGrade): number {
  if (grade === 1) {
    // Lapse
    return W[11] * Math.pow(d, -W[12]) * (Math.pow(s + 1, W[13]) - 1) * Math.exp(W[14] * (1 - r));
  }
  const hardPenalty = grade === 2 ? W[15] : 1;
  const easyBonus = grade === 4 ? W[16] : 1;
  return s * (
    Math.exp(W[8]) *
    (11 - d) *
    Math.pow(s, -W[9]) *
    (Math.exp(W[10] * (1 - r)) - 1) *
    hardPenalty *
    easyBonus + 1
  );
}

export function scheduleCard(card: FSRSCard, grade: FSRSGrade, reviewDate = new Date()): FSRSResult {
  let stability: number;
  let difficulty: number;

  if (card.reviewCount === 0) {
    // First review — initialize
    stability = initStability(grade);
    difficulty = initDifficulty(grade);
  } else {
    const daysSinceLast = card.lastReviewed
      ? (reviewDate.getTime() - new Date(card.lastReviewed).getTime()) / 86400000
      : 0;
    const r = forgettingCurve(daysSinceLast, card.stability);
    stability = nextRecallStability(card.stability, card.difficulty, r, grade);
    difficulty = nextDifficulty(card.difficulty, grade);
  }

  const interval = nextInterval(stability);
  const nextDueDate = new Date(reviewDate);
  nextDueDate.setDate(nextDueDate.getDate() + interval);

  return {
    stability: Math.max(0.1, stability),
    difficulty: Math.min(10, Math.max(1, difficulty)),
    recallProbability: TARGET_RETENTION,
    interval,
    nextDue: nextDueDate.toISOString().split("T")[0],
  };
}

export function getRecallProbability(card: FSRSCard, asOf = new Date()): number {
  if (!card.lastReviewed || card.reviewCount === 0) return 1;
  const days = (asOf.getTime() - new Date(card.lastReviewed).getTime()) / 86400000;
  return forgettingCurve(days, card.stability);
}

export function isDue(card: FSRSCard, asOf = new Date()): boolean {
  if (!card.nextDue) return false;
  return new Date(card.nextDue) <= asOf;
}

export function gradeFromLabel(label: "Again" | "Hard" | "Good" | "Easy"): FSRSGrade {
  const map: Record<string, FSRSGrade> = { Again: 1, Hard: 2, Good: 3, Easy: 4 };
  return map[label];
}
