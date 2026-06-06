# Mastery Engine — Implementation Specification

**Version:** 2.0.0  
**Status:** Canonical. All implementations must match exactly.  
**Purpose:** Define the single source of truth for mastery and retention updates across all platforms.

---

## 0. Guiding Principles

1. **Determinism first.** Given identical inputs, every platform produces identical outputs.
2. **Clamp everywhere.** No value ever leaves its defined range.
3. **Integer-free floats.** All stored values are `float64` / `number`. Display rounding is a UI concern only.
4. **Event order is atomic.** Each event type maps to exactly one formula. No event blends two formulas.
5. **Completion bonuses are one-time.** A lesson/quiz bonus fires only on first completion of that content version. Replays earn no bonus.
6. **Assessment measures; it does not teach.** Assessment completion carries zero mastery or retention bonus.

---

## 1. Value Ranges

### 1.1 Mastery Range

```
MASTERY_MIN = 0.0
MASTERY_MAX = 1.0
```

Mastery represents how well a learner knows a concept.  
It is a value in **[0.0, 1.0]** inclusive.

| Band | Range | Label | Curriculum Action |
|------|-------|-------|-------------------|
| Not started | 0.00 | — | — |
| Needs Remediation | (0.00, 0.30] | Remediation | Assign foundational content |
| Continue Learning | (0.30, 0.60] | Learning | Continue current path |
| Practice Required | (0.60, 0.85] | Proficient | Assign practice exercises |
| Mastered | (0.85, 1.00] | Mastered | Unlock dependent concepts |

> **Alignment note:** The mastery threshold `0.85` matches the prerequisite satisfaction condition used in Neo4j graph queries (`m.score >= 0.85`). These values are identical by design and must never diverge.

### 1.2 Retention Range

```
RETENTION_MIN = 0.0
RETENTION_MAX = 1.0
```

Retention represents how much of previously learned material is remembered over time.

**Event-driven updates** (this spec): applied immediately on learning events.  
**Time-driven decay** (login decay): applied once per login session.

#### 1.2.1 Login Decay Formula

On every login, after computing `days_since_last_seen`:

```
new_retention = clamp(retention * (0.995 ^ days_since_last_seen), RETENTION_MIN, RETENTION_MAX)
```

**Constant:** `DECAY_RATE = 0.995`  
**Worked example:**

```
retention          = 0.80
days_since_last    = 10
decay_factor       = 0.995 ^ 10 = 0.95111...
new_retention      = clamp(0.80 * 0.951, 0.0, 1.0) = 0.761
```

**Edge cases:**

```
days_since_last_seen = 0  → decay_factor = 1.0  → no change
days_since_last_seen < 0  → treat as 0 (clock skew guard)
retention = 0.0           → stays 0.0
```

> The decay is applied **before** any event-driven updates in the same session. Order: decay → event updates.

---

## 2. Constants

All constants are **exact**. No platform may substitute approximations.

```
# Mastery deltas — question events
DELTA_CORRECT          =  0.10
DELTA_WRONG            = -0.08
DELTA_HINT             = -0.03   # applied on top of DELTA_CORRECT when hint used
DELTA_SKIP             = -0.05

# Completion bonuses — awarded ONCE per content version (first completion only)
BONUS_LESSON           =  0.05
BONUS_QUIZ             =  0.08
BONUS_ASSESSMENT       =  0.00   # Assessment is diagnostic; no mastery bonus

# Retention deltas — question events
RET_CORRECT            =  0.07
RET_WRONG              = -0.05
RET_HINT               = -0.02   # applied on top of RET_CORRECT when hint used
RET_SKIP               = -0.03
RET_LESSON             =  0.04
RET_QUIZ               =  0.06
RET_ASSESSMENT         =  0.00   # Assessment is diagnostic; no retention bonus

# Retention decay
DECAY_RATE             =  0.995  # per day

# Mastery curriculum threshold
MASTERY_THRESHOLD      =  0.85   # must match Neo4j prerequisite condition

# Range bounds
MASTERY_MIN   = 0.0
MASTERY_MAX   = 1.0
RETENTION_MIN = 0.0
RETENTION_MAX = 1.0
```

---

## 3. The Clamp Function

Every formula result **must** pass through clamp before storage.

```
clamp(value, min, max) → max(min, min(max, value))
```

**No exceptions.** Apply clamp even if you believe the value cannot exceed bounds — defensive consistency is required.

---

## 4. Completion Eligibility — First-Time Guard

Completion bonuses (lesson, quiz) apply **only on the first completion** of a given content item in a given content version.

### 4.1 Required State Fields

Each learner–content pair must track:

```
session_record {
  learner_id:       string
  content_id:       string        # unique ID of the lesson or quiz
  content_version:  string        # e.g. "v1", "v2" — bumped on content edit
  bonus_awarded:    boolean       # default: false
}
```

### 4.2 Guard Logic (applies before every completion event)

```
FUNCTION isEligibleForBonus(session_record):
  IF session_record.bonus_awarded == true:
    RETURN false
  RETURN true

FUNCTION markBonusAwarded(session_record):
  session_record.bonus_awarded = true
  PERSIST session_record
```

### 4.3 Why `content_version`?

If a lesson is substantially revised and re-published under a new version, `bonus_awarded` resets to `false` for that learner. This allows the bonus to fire once per meaningful version, not once per learner lifetime.

**Worked example — replay attempt:**

```
First completion:
  isEligibleForBonus → true
  Award BONUS_LESSON (+0.05)
  markBonusAwarded → bonus_awarded = true

Replay completion:
  isEligibleForBonus → false
  No bonus awarded
  Question-level updates still apply normally
```

---

## 5. Update Rules

### 5.1 Correct Answer

Triggered when a learner answers a question **correctly** and **did not use a hint**.

```
new_mastery   = clamp(mastery   + DELTA_CORRECT,  MASTERY_MIN,   MASTERY_MAX)
new_retention = clamp(retention + RET_CORRECT,    RETENTION_MIN, RETENTION_MAX)
```

**Worked example:**

```
mastery = 0.60, retention = 0.70
new_mastery   = clamp(0.60 + 0.10, 0.0, 1.0) = 0.70
new_retention = clamp(0.70 + 0.07, 0.0, 1.0) = 0.77
```

**Edge case — ceiling:**

```
mastery = 0.95
new_mastery = clamp(0.95 + 0.10, 0.0, 1.0) = clamp(1.05, 0.0, 1.0) = 1.0   ✓
```

---

### 5.2 Wrong Answer

Triggered when a learner answers **incorrectly** (hint or no hint — wrong answer formula always applies).

```
new_mastery   = clamp(mastery   + DELTA_WRONG,  MASTERY_MIN,   MASTERY_MAX)
new_retention = clamp(retention + RET_WRONG,    RETENTION_MIN, RETENTION_MAX)
```

**Worked example:**

```
mastery = 0.30, retention = 0.20
new_mastery   = clamp(0.30 - 0.08, 0.0, 1.0) = 0.22
new_retention = clamp(0.20 - 0.05, 0.0, 1.0) = 0.15
```

**Edge case — floor:**

```
mastery = 0.04
new_mastery = clamp(0.04 - 0.08, 0.0, 1.0) = clamp(-0.04, 0.0, 1.0) = 0.0   ✓
```

---

### 5.3 Hint Used

Triggered when a learner uses a hint **and then answers correctly**.  
DELTA_HINT is a penalty that reduces the correct bonus.

> **Critical:** If hint used + answer **wrong** → apply Wrong Answer rule (5.2) only. Hint penalty does NOT stack with DELTA_WRONG.

```
# Hint used + correct
new_mastery   = clamp(mastery   + DELTA_CORRECT + DELTA_HINT,  MASTERY_MIN,   MASTERY_MAX)
new_retention = clamp(retention + RET_CORRECT   + RET_HINT,    RETENTION_MIN, RETENTION_MAX)

# Hint used + wrong → identical to 5.2
new_mastery   = clamp(mastery   + DELTA_WRONG,  MASTERY_MIN,   MASTERY_MAX)
new_retention = clamp(retention + RET_WRONG,    RETENTION_MIN, RETENTION_MAX)
```

**Worked example (hint + correct):**

```
mastery = 0.50, retention = 0.60
net_mastery_delta   = 0.10 + (-0.03) = 0.07
net_retention_delta = 0.07 + (-0.02) = 0.05
new_mastery   = clamp(0.50 + 0.07, 0.0, 1.0) = 0.57
new_retention = clamp(0.60 + 0.05, 0.0, 1.0) = 0.65
```

**Worked example (hint + wrong):**

```
mastery = 0.50, retention = 0.60
new_mastery   = clamp(0.50 - 0.08, 0.0, 1.0) = 0.42
new_retention = clamp(0.60 - 0.05, 0.0, 1.0) = 0.55
```

---

### 5.4 Skip Question

Triggered when a learner explicitly skips a question (not a timeout).

```
new_mastery   = clamp(mastery   + DELTA_SKIP,  MASTERY_MIN,   MASTERY_MAX)
new_retention = clamp(retention + RET_SKIP,    RETENTION_MIN, RETENTION_MAX)
```

**Worked example:**

```
mastery = 0.20, retention = 0.30
new_mastery   = clamp(0.20 - 0.05, 0.0, 1.0) = 0.15
new_retention = clamp(0.30 - 0.03, 0.0, 1.0) = 0.27
```

**Edge case — floor:**

```
mastery = 0.0
new_mastery = clamp(0.0 - 0.05, 0.0, 1.0) = 0.0   ✓
```

---

### 5.5 Lesson Completion

Fires exactly once per learner per content version (see Section 4).

```
IF isEligibleForBonus(session_record):
  new_mastery   = clamp(mastery   + BONUS_LESSON,  MASTERY_MIN,   MASTERY_MAX)
  new_retention = clamp(retention + RET_LESSON,    RETENTION_MIN, RETENTION_MAX)
  markBonusAwarded(session_record)
ELSE:
  new_mastery   = mastery     # no change
  new_retention = retention   # no change
```

**Worked example — first completion:**

```
mastery = 0.72, retention = 0.65, bonus_awarded = false
new_mastery   = clamp(0.72 + 0.05, 0.0, 1.0) = 0.77
new_retention = clamp(0.65 + 0.04, 0.0, 1.0) = 0.69
bonus_awarded → true
```

**Worked example — replay (no bonus):**

```
mastery = 0.77, retention = 0.69, bonus_awarded = true
new_mastery   = 0.77   (unchanged)
new_retention = 0.69   (unchanged)
```

---

### 5.6 Quiz Completion

Fires exactly once per learner per content version (see Section 4).

```
IF isEligibleForBonus(session_record):
  new_mastery   = clamp(mastery   + BONUS_QUIZ,  MASTERY_MIN,   MASTERY_MAX)
  new_retention = clamp(retention + RET_QUIZ,    RETENTION_MIN, RETENTION_MAX)
  markBonusAwarded(session_record)
ELSE:
  new_mastery   = mastery
  new_retention = retention
```

**Worked example — first completion:**

```
mastery = 0.80, retention = 0.55, bonus_awarded = false
new_mastery   = clamp(0.80 + 0.08, 0.0, 1.0) = 0.88
new_retention = clamp(0.55 + 0.06, 0.0, 1.0) = 0.61
bonus_awarded → true
```

---

### 5.7 Assessment Completion

Assessments are diagnostic instruments. They **measure** mastery; they do not confer it.  
Completion fires no mastery or retention update.

```
# Assessment completion — no state change in this engine
new_mastery   = mastery     # unchanged
new_retention = retention   # unchanged
```

> The `assessment_complete` event must still be accepted by the engine without error — it simply produces no delta. Callers use the event to trigger scoring, reporting, and curriculum routing (Section 6), not state mutation.

**Worked example:**

```
mastery = 0.90, retention = 0.85
After assessment_complete:
new_mastery   = 0.90   (unchanged)
new_retention = 0.85   (unchanged)
```

> **Why no bonus?** A learner who guesses well on an assessment should not receive a mastery increase. Assessment score is an *observation*, not an *intervention*. Mastery updates come from learning events (correct, wrong, skip). Assessment drives curriculum routing decisions (Section 6), not mastery arithmetic.

---

## 6. Mastery → Curriculum Routing

The mastery value drives three curriculum decisions: remediation, progression, and unlock. This section defines the exact thresholds and their mapping to Neo4j graph operations.

### 6.1 Routing Table

| Mastery Range | State | Curriculum Action |
|---|---|---|
| 0.00 | Not started | Assign first content node |
| (0.00, 0.30] | Needs Remediation | Assign remediation path |
| (0.30, 0.60] | Continue Learning | Continue on current path |
| (0.60, 0.85] | Practice Required | Assign practice exercises |
| (0.85, 1.00] | Mastered | Unlock dependent nodes in graph |

### 6.2 Unlock Condition

A concept node is considered **satisfied** (eligible to unlock dependents) when:

```
mastery >= MASTERY_THRESHOLD   # 0.85
```

This is the **only** unlock gate. Retention, quiz score, and assessment score do not gate unlocks directly.

**Neo4j alignment:**

```cypher
// Prerequisite satisfied check — must use MASTERY_THRESHOLD = 0.85
MATCH (l:Learner {id: $learnerId})-[r:HAS_MASTERY]->(c:Concept {id: $conceptId})
WHERE r.score >= 0.85
RETURN c
```

> The literal `0.85` in Neo4j queries is derived from `MASTERY_THRESHOLD`. If the threshold changes in this spec, the Cypher queries must be updated in the same commit.

### 6.3 Routing Decision Function

```
FUNCTION getCurriculumAction(mastery):
  IF mastery == 0.0:
    RETURN "assign_first"
  IF mastery <= 0.30:
    RETURN "remediate"
  IF mastery <= 0.60:
    RETURN "continue"
  IF mastery < 0.85:
    RETURN "practice"
  RETURN "unlock_dependents"
```

### 6.4 When to Evaluate Routing

Routing is evaluated **after** every mastery update — not on a schedule. If `new_mastery` crosses a threshold boundary, the curriculum system receives the routing signal immediately.

---

## 7. Event Summary Table

| Event | Mastery Δ | Retention Δ | One-time? | Notes |
|-------|-----------|-------------|-----------|-------|
| Correct (no hint) | +0.10 | +0.07 | No | Per question |
| Wrong | −0.08 | −0.05 | No | Hint flag ignored |
| Hint + Correct | +0.07 | +0.05 | No | Net of correct + hint penalty |
| Hint + Wrong | −0.08 | −0.05 | No | Same as Wrong |
| Skip | −0.05 | −0.03 | No | Per question |
| Lesson complete | +0.05 | +0.04 | **Yes** | First completion only |
| Quiz complete | +0.08 | +0.06 | **Yes** | First completion only |
| Assessment complete | **0.00** | **0.00** | — | Diagnostic only; no state change |
| Login (decay) | — | ×0.995^days | — | Applied before event updates |

---

## 8. Edge Cases & Boundary Handling

| Scenario | Rule |
|----------|------|
| Result > 1.0 | Clamp to 1.0 |
| Result < 0.0 | Clamp to 0.0 |
| Mastery already 1.0, correct answer | Stays 1.0 |
| Mastery already 0.0, wrong answer | Stays 0.0 |
| Hint used + wrong | Apply Wrong rule only; no hint penalty |
| Lesson/quiz replayed | No completion bonus; question deltas still apply |
| Assessment completed | No mastery or retention change |
| days_since_last_seen = 0 | Decay factor = 1.0; no change |
| days_since_last_seen < 0 | Treat as 0 (clock skew guard) |
| NaN input | Treat as 0.0; log warning |
| Infinite input | Treat as 0.0; log warning |
| content_version changes | bonus_awarded resets to false for that version |

---

## 9. Pseudocode

```
CONSTANTS:
  DELTA_CORRECT    =  0.10
  DELTA_WRONG      = -0.08
  DELTA_HINT       = -0.03
  DELTA_SKIP       = -0.05
  BONUS_LESSON     =  0.05
  BONUS_QUIZ       =  0.08
  BONUS_ASSESSMENT =  0.00

  RET_CORRECT      =  0.07
  RET_WRONG        = -0.05
  RET_HINT         = -0.02
  RET_SKIP         = -0.03
  RET_LESSON       =  0.04
  RET_QUIZ         =  0.06
  RET_ASSESSMENT   =  0.00

  DECAY_RATE         = 0.995
  MASTERY_THRESHOLD  = 0.85

FUNCTION clamp(value, min=0.0, max=1.0):
  RETURN max(min, min(max, value))

FUNCTION sanitize(value):
  IF value is NaN OR value is Infinite:
    LOG warning
    RETURN 0.0
  RETURN value

FUNCTION applyLoginDecay(retention, days_since_last_seen):
  days = max(0, days_since_last_seen)   # guard negative
  RETURN clamp(retention * (DECAY_RATE ^ days))

FUNCTION updateMastery(mastery, retention, event, hint_used, session_record):
  mastery   = sanitize(mastery)
  retention = sanitize(retention)

  SWITCH event:

    CASE "correct":
      IF hint_used:
        new_mastery   = clamp(mastery   + DELTA_CORRECT + DELTA_HINT)
        new_retention = clamp(retention + RET_CORRECT   + RET_HINT)
      ELSE:
        new_mastery   = clamp(mastery   + DELTA_CORRECT)
        new_retention = clamp(retention + RET_CORRECT)

    CASE "wrong":
      new_mastery   = clamp(mastery   + DELTA_WRONG)
      new_retention = clamp(retention + RET_WRONG)

    CASE "skip":
      new_mastery   = clamp(mastery   + DELTA_SKIP)
      new_retention = clamp(retention + RET_SKIP)

    CASE "lesson_complete":
      IF isEligibleForBonus(session_record):
        new_mastery   = clamp(mastery   + BONUS_LESSON)
        new_retention = clamp(retention + RET_LESSON)
        markBonusAwarded(session_record)
      ELSE:
        new_mastery   = mastery
        new_retention = retention

    CASE "quiz_complete":
      IF isEligibleForBonus(session_record):
        new_mastery   = clamp(mastery   + BONUS_QUIZ)
        new_retention = clamp(retention + RET_QUIZ)
        markBonusAwarded(session_record)
      ELSE:
        new_mastery   = mastery
        new_retention = retention

    CASE "assessment_complete":
      new_mastery   = mastery     # no change
      new_retention = retention   # no change

    DEFAULT:
      THROW Error("Unknown event: " + event)

  routing_action = getCurriculumAction(new_mastery)
  RETURN { mastery: new_mastery, retention: new_retention, routing: routing_action }

FUNCTION getCurriculumAction(mastery):
  IF mastery == 0.0:      RETURN "assign_first"
  IF mastery <= 0.30:     RETURN "remediate"
  IF mastery <= 0.60:     RETURN "continue"
  IF mastery <  0.85:     RETURN "practice"
  RETURN "unlock_dependents"
```

---

## 10. TypeScript Implementation

```typescript
// mastery_engine.ts
// Canonical implementation — v2.0.0
// Do NOT modify constants without a spec version bump.

export const CONSTANTS = {
  DELTA_CORRECT:     0.10,
  DELTA_WRONG:      -0.08,
  DELTA_HINT:       -0.03,
  DELTA_SKIP:       -0.05,
  BONUS_LESSON:      0.05,
  BONUS_QUIZ:        0.08,
  BONUS_ASSESSMENT:  0.00,   // diagnostic; no bonus

  RET_CORRECT:       0.07,
  RET_WRONG:        -0.05,
  RET_HINT:         -0.02,
  RET_SKIP:         -0.03,
  RET_LESSON:        0.04,
  RET_QUIZ:          0.06,
  RET_ASSESSMENT:    0.00,   // diagnostic; no bonus

  DECAY_RATE:        0.995,
  MASTERY_THRESHOLD: 0.85,

  MASTERY_MIN:   0.0,
  MASTERY_MAX:   1.0,
  RETENTION_MIN: 0.0,
  RETENTION_MAX: 1.0,
} as const;

export type MasteryEvent =
  | "correct"
  | "wrong"
  | "skip"
  | "lesson_complete"
  | "quiz_complete"
  | "assessment_complete";

export type CurriculumAction =
  | "assign_first"
  | "remediate"
  | "continue"
  | "practice"
  | "unlock_dependents";

export interface MasteryState {
  mastery:   number;
  retention: number;
}

export interface SessionRecord {
  learnerId:      string;
  contentId:      string;
  contentVersion: string;
  bonusAwarded:   boolean;
}

export interface UpdateResult {
  mastery:         number;
  retention:       number;
  masteryDelta:    number;          // actual delta after clamping
  retentionDelta:  number;          // actual delta after clamping
  bonusAwarded:    boolean;         // true if completion bonus was applied this call
  routing:         CurriculumAction;
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function sanitize(value: number, fieldName: string): number {
  if (!Number.isFinite(value)) {
    console.warn(`[mastery_engine] Non-finite value for ${fieldName}: ${value}. Using 0.0.`);
    return 0.0;
  }
  return value;
}

function getCurriculumAction(mastery: number): CurriculumAction {
  if (mastery === 0.0)                               return "assign_first";
  if (mastery <= 0.30)                               return "remediate";
  if (mastery <= 0.60)                               return "continue";
  if (mastery <  CONSTANTS.MASTERY_THRESHOLD)        return "practice";
  return "unlock_dependents";
}

// ---------------------------------------------------------------------------
// Login decay — call once per session before any event updates
// ---------------------------------------------------------------------------

export function applyLoginDecay(
  retention: number,
  daysSinceLastSeen: number
): number {
  const C = CONSTANTS;
  const days = Math.max(0, daysSinceLastSeen);  // guard negative
  return clamp(retention * Math.pow(C.DECAY_RATE, days), C.RETENTION_MIN, C.RETENTION_MAX);
}

// ---------------------------------------------------------------------------
// Core update function
// ---------------------------------------------------------------------------

export function updateMastery(
  state: MasteryState,
  event: MasteryEvent,
  hintUsed: boolean,
  sessionRecord: SessionRecord,
  persistBonus: (record: SessionRecord) => void   // caller provides persistence
): UpdateResult {
  const C = CONSTANTS;

  const mastery   = sanitize(state.mastery,   "mastery");
  const retention = sanitize(state.retention, "retention");

  let masteryDelta:   number;
  let retentionDelta: number;
  let bonusAwarded = false;

  switch (event) {
    case "correct":
      if (hintUsed) {
        masteryDelta   = C.DELTA_CORRECT + C.DELTA_HINT;  // 0.07
        retentionDelta = C.RET_CORRECT   + C.RET_HINT;    // 0.05
      } else {
        masteryDelta   = C.DELTA_CORRECT;   // 0.10
        retentionDelta = C.RET_CORRECT;     // 0.07
      }
      break;

    case "wrong":
      // hintUsed does NOT change the wrong formula
      masteryDelta   = C.DELTA_WRONG;   // -0.08
      retentionDelta = C.RET_WRONG;     // -0.05
      break;

    case "skip":
      masteryDelta   = C.DELTA_SKIP;    // -0.05
      retentionDelta = C.RET_SKIP;      // -0.03
      break;

    case "lesson_complete":
      if (!sessionRecord.bonusAwarded) {
        masteryDelta   = C.BONUS_LESSON;  // 0.05
        retentionDelta = C.RET_LESSON;    // 0.04
        bonusAwarded   = true;
        sessionRecord.bonusAwarded = true;
        persistBonus(sessionRecord);
      } else {
        masteryDelta   = 0.0;
        retentionDelta = 0.0;
      }
      break;

    case "quiz_complete":
      if (!sessionRecord.bonusAwarded) {
        masteryDelta   = C.BONUS_QUIZ;   // 0.08
        retentionDelta = C.RET_QUIZ;     // 0.06
        bonusAwarded   = true;
        sessionRecord.bonusAwarded = true;
        persistBonus(sessionRecord);
      } else {
        masteryDelta   = 0.0;
        retentionDelta = 0.0;
      }
      break;

    case "assessment_complete":
      masteryDelta   = C.BONUS_ASSESSMENT;  // 0.00
      retentionDelta = C.RET_ASSESSMENT;    // 0.00
      break;

    default:
      throw new Error(`[mastery_engine] Unknown event: "${event}"`);
  }

  const newMastery   = clamp(mastery   + masteryDelta,   C.MASTERY_MIN,   C.MASTERY_MAX);
  const newRetention = clamp(retention + retentionDelta, C.RETENTION_MIN, C.RETENTION_MAX);

  return {
    mastery:        newMastery,
    retention:      newRetention,
    masteryDelta:   newMastery   - mastery,
    retentionDelta: newRetention - retention,
    bonusAwarded,
    routing:        getCurriculumAction(newMastery),
  };
}


// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

function assertEqual(label: string, actual: number, expected: number): void {
  const ok = Math.abs(actual - expected) < 1e-10;
  console.log(`${ok ? "✓" : "✗"} ${label}: got ${actual}, expected ${expected}`);
}

function assertEq(label: string, actual: unknown, expected: unknown): void {
  const ok = actual === expected;
  console.log(`${ok ? "✓" : "✗"} ${label}: got ${actual}, expected ${expected}`);
}

function makeSession(bonusAwarded = false): SessionRecord {
  return { learnerId: "l1", contentId: "c1", contentVersion: "v1", bonusAwarded };
}

const noPersist = (_: SessionRecord) => {};

function runTests(): void {
  console.log("\n=== mastery_engine v2.0.0 tests ===\n");

  let r: UpdateResult;
  let s: SessionRecord;

  // 5.1 Correct (no hint)
  r = updateMastery({ mastery: 0.60, retention: 0.70 }, "correct", false, makeSession(), noPersist);
  assertEqual("correct no-hint mastery",   r.mastery,   0.70);
  assertEqual("correct no-hint retention", r.retention, 0.77);
  assertEq("correct routing",              r.routing,   "practice");

  // 5.1 Ceiling clamp
  r = updateMastery({ mastery: 0.95, retention: 0.97 }, "correct", false, makeSession(), noPersist);
  assertEqual("correct ceiling mastery",   r.mastery,   1.0);
  assertEqual("correct ceiling retention", r.retention, 1.0);

  // 5.2 Wrong
  r = updateMastery({ mastery: 0.30, retention: 0.20 }, "wrong", false, makeSession(), noPersist);
  assertEqual("wrong mastery",   r.mastery,   0.22);
  assertEqual("wrong retention", r.retention, 0.15);

  // 5.2 Floor clamp
  r = updateMastery({ mastery: 0.04, retention: 0.02 }, "wrong", false, makeSession(), noPersist);
  assertEqual("wrong floor mastery",   r.mastery,   0.0);
  assertEqual("wrong floor retention", r.retention, 0.0);

  // 5.3 Hint + correct
  r = updateMastery({ mastery: 0.50, retention: 0.60 }, "correct", true, makeSession(), noPersist);
  assertEqual("hint+correct mastery",   r.mastery,   0.57);
  assertEqual("hint+correct retention", r.retention, 0.65);

  // 5.3 Hint + wrong (same as wrong)
  r = updateMastery({ mastery: 0.50, retention: 0.60 }, "wrong", true, makeSession(), noPersist);
  assertEqual("hint+wrong mastery",   r.mastery,   0.42);
  assertEqual("hint+wrong retention", r.retention, 0.55);

  // 5.4 Skip
  r = updateMastery({ mastery: 0.20, retention: 0.30 }, "skip", false, makeSession(), noPersist);
  assertEqual("skip mastery",   r.mastery,   0.15);
  assertEqual("skip retention", r.retention, 0.27);

  // 5.4 Skip floor
  r = updateMastery({ mastery: 0.0, retention: 0.0 }, "skip", false, makeSession(), noPersist);
  assertEqual("skip floor mastery",   r.mastery,   0.0);
  assertEqual("skip floor retention", r.retention, 0.0);

  // 5.5 Lesson — first completion
  s = makeSession(false);
  r = updateMastery({ mastery: 0.72, retention: 0.65 }, "lesson_complete", false, s, noPersist);
  assertEqual("lesson first mastery",   r.mastery,   0.77);
  assertEqual("lesson first retention", r.retention, 0.69);
  assertEq("lesson first bonusAwarded", r.bonusAwarded, true);

  // 5.5 Lesson — replay (no bonus)
  s = makeSession(true);
  r = updateMastery({ mastery: 0.77, retention: 0.69 }, "lesson_complete", false, s, noPersist);
  assertEqual("lesson replay mastery",   r.mastery,   0.77);
  assertEqual("lesson replay retention", r.retention, 0.69);
  assertEq("lesson replay bonusAwarded", r.bonusAwarded, false);

  // 5.6 Quiz — first completion
  s = makeSession(false);
  r = updateMastery({ mastery: 0.80, retention: 0.55 }, "quiz_complete", false, s, noPersist);
  assertEqual("quiz first mastery",   r.mastery,   0.88);
  assertEqual("quiz first retention", r.retention, 0.61);
  assertEq("quiz routing", r.routing, "unlock_dependents");

  // 5.6 Quiz — replay (no bonus)
  s = makeSession(true);
  r = updateMastery({ mastery: 0.88, retention: 0.61 }, "quiz_complete", false, s, noPersist);
  assertEqual("quiz replay mastery",   r.mastery,   0.88);
  assertEqual("quiz replay retention", r.retention, 0.61);
  assertEq("quiz replay bonusAwarded", r.bonusAwarded, false);

  // 5.7 Assessment — no change
  r = updateMastery({ mastery: 0.90, retention: 0.85 }, "assessment_complete", false, makeSession(), noPersist);
  assertEqual("assessment mastery unchanged",   r.mastery,   0.90);
  assertEqual("assessment retention unchanged", r.retention, 0.85);
  assertEq("assessment bonusAwarded", r.bonusAwarded, false);

  // Login decay
  assertEqual("decay 10 days", applyLoginDecay(0.80, 10), 0.80 * Math.pow(0.995, 10));
  assertEqual("decay 0 days",  applyLoginDecay(0.80,  0), 0.80);
  assertEqual("decay negative", applyLoginDecay(0.80, -5), 0.80); // treated as 0

  // Curriculum routing
  assertEq("routing 0.00", getCurriculumAction(0.00), "assign_first");
  assertEq("routing 0.20", getCurriculumAction(0.20), "remediate");
  assertEq("routing 0.30", getCurriculumAction(0.30), "remediate");
  assertEq("routing 0.31", getCurriculumAction(0.31), "continue");
  assertEq("routing 0.60", getCurriculumAction(0.60), "continue");
  assertEq("routing 0.61", getCurriculumAction(0.61), "practice");
  assertEq("routing 0.84", getCurriculumAction(0.84), "practice");
  assertEq("routing 0.85", getCurriculumAction(0.85), "unlock_dependents");
  assertEq("routing 1.00", getCurriculumAction(1.00), "unlock_dependents");

  console.log("\n=== done ===\n");
}

// expose for test runners
function getCurriculumAction(mastery: number): CurriculumAction {
  if (mastery === 0.0)                                return "assign_first";
  if (mastery <= 0.30)                               return "remediate";
  if (mastery <= 0.60)                               return "continue";
  if (mastery <  CONSTANTS.MASTERY_THRESHOLD)        return "practice";
  return "unlock_dependents";
}

runTests();
```

---

## 11. Python Implementation

```python
# mastery_engine.py
# Canonical implementation — v2.0.0
# Do NOT modify constants without a spec version bump.

from __future__ import annotations
import math
import logging
from dataclasses import dataclass, field
from typing import Callable, Literal

logger = logging.getLogger("mastery_engine")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DELTA_CORRECT:     float =  0.10
DELTA_WRONG:       float = -0.08
DELTA_HINT:        float = -0.03
DELTA_SKIP:        float = -0.05
BONUS_LESSON:      float =  0.05
BONUS_QUIZ:        float =  0.08
BONUS_ASSESSMENT:  float =  0.00   # diagnostic; no bonus

RET_CORRECT:       float =  0.07
RET_WRONG:         float = -0.05
RET_HINT:          float = -0.02
RET_SKIP:          float = -0.03
RET_LESSON:        float =  0.04
RET_QUIZ:          float =  0.06
RET_ASSESSMENT:    float =  0.00   # diagnostic; no bonus

DECAY_RATE:        float =  0.995
MASTERY_THRESHOLD: float =  0.85

MASTERY_MIN:   float = 0.0
MASTERY_MAX:   float = 1.0
RETENTION_MIN: float = 0.0
RETENTION_MAX: float = 1.0

MasteryEvent = Literal[
    "correct", "wrong", "skip",
    "lesson_complete", "quiz_complete", "assessment_complete",
]

CurriculumAction = Literal[
    "assign_first", "remediate", "continue", "practice", "unlock_dependents",
]

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class MasteryState:
    mastery:   float
    retention: float

@dataclass
class SessionRecord:
    learner_id:      str
    content_id:      str
    content_version: str
    bonus_awarded:   bool = False

@dataclass
class UpdateResult:
    mastery:          float
    retention:        float
    mastery_delta:    float    # actual delta after clamping
    retention_delta:  float    # actual delta after clamping
    bonus_awarded:    bool
    routing:          CurriculumAction

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))

def _sanitize(value: float, field_name: str) -> float:
    if not math.isfinite(value):
        logger.warning("[mastery_engine] Non-finite %s: %s. Using 0.0.", field_name, value)
        return 0.0
    return value

def get_curriculum_action(mastery: float) -> CurriculumAction:
    if mastery == 0.0:               return "assign_first"
    if mastery <= 0.30:              return "remediate"
    if mastery <= 0.60:              return "continue"
    if mastery <  MASTERY_THRESHOLD: return "practice"
    return "unlock_dependents"

# ---------------------------------------------------------------------------
# Login decay
# ---------------------------------------------------------------------------
def apply_login_decay(retention: float, days_since_last_seen: float) -> float:
    """Apply exponential retention decay. Call once per session before event updates."""
    days = max(0.0, days_since_last_seen)   # guard negative
    return _clamp(retention * (DECAY_RATE ** days))

# ---------------------------------------------------------------------------
# Core update function
# ---------------------------------------------------------------------------
def update_mastery(
    state: MasteryState,
    event: MasteryEvent,
    hint_used: bool,
    session_record: SessionRecord,
    persist_bonus: Callable[[SessionRecord], None],
) -> UpdateResult:
    """
    Apply a learning event and return the new mastery/retention state.

    Args:
        state:          Current mastery and retention [0.0, 1.0].
        event:          The event type.
        hint_used:      True only when learner used a hint before answering.
        session_record: Tracks whether completion bonus has been awarded.
        persist_bonus:  Caller-provided function to persist session_record changes.

    Returns:
        UpdateResult with new values, actual deltas, bonus flag, and routing action.
    """
    mastery   = _sanitize(state.mastery,   "mastery")
    retention = _sanitize(state.retention, "retention")

    mastery_delta:   float = 0.0
    retention_delta: float = 0.0
    bonus_awarded:   bool  = False

    if event == "correct":
        if hint_used:
            mastery_delta   = DELTA_CORRECT + DELTA_HINT  # 0.07
            retention_delta = RET_CORRECT   + RET_HINT    # 0.05
        else:
            mastery_delta   = DELTA_CORRECT   # 0.10
            retention_delta = RET_CORRECT     # 0.07

    elif event == "wrong":
        # hint_used does NOT change the wrong formula
        mastery_delta   = DELTA_WRONG    # -0.08
        retention_delta = RET_WRONG      # -0.05

    elif event == "skip":
        mastery_delta   = DELTA_SKIP     # -0.05
        retention_delta = RET_SKIP       # -0.03

    elif event == "lesson_complete":
        if not session_record.bonus_awarded:
            mastery_delta   = BONUS_LESSON   # 0.05
            retention_delta = RET_LESSON     # 0.04
            bonus_awarded   = True
            session_record.bonus_awarded = True
            persist_bonus(session_record)

    elif event == "quiz_complete":
        if not session_record.bonus_awarded:
            mastery_delta   = BONUS_QUIZ     # 0.08
            retention_delta = RET_QUIZ       # 0.06
            bonus_awarded   = True
            session_record.bonus_awarded = True
            persist_bonus(session_record)

    elif event == "assessment_complete":
        mastery_delta   = BONUS_ASSESSMENT   # 0.00
        retention_delta = RET_ASSESSMENT     # 0.00

    else:
        raise ValueError(f"[mastery_engine] Unknown event: '{event}'")

    new_mastery   = _clamp(mastery   + mastery_delta,   MASTERY_MIN,   MASTERY_MAX)
    new_retention = _clamp(retention + retention_delta, RETENTION_MIN, RETENTION_MAX)

    return UpdateResult(
        mastery         = new_mastery,
        retention       = new_retention,
        mastery_delta   = new_mastery   - mastery,
        retention_delta = new_retention - retention,
        bonus_awarded   = bonus_awarded,
        routing         = get_curriculum_action(new_mastery),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _ok(label: str, actual, expected, tol: float = 1e-10) -> None:
    if isinstance(expected, float):
        passed = abs(actual - expected) < tol
    else:
        passed = actual == expected
    print(f"  {'✓' if passed else '✗'} {label}: got {actual!r}, expected {expected!r}")

def _session(bonus_awarded: bool = False) -> SessionRecord:
    return SessionRecord("l1", "c1", "v1", bonus_awarded)

def run_tests() -> None:
    print("\n=== mastery_engine v2.0.0 tests ===\n")

    no_persist = lambda _: None

    # 5.1 Correct (no hint)
    r = update_mastery(MasteryState(0.60, 0.70), "correct", False, _session(), no_persist)
    _ok("correct no-hint mastery",   r.mastery,   0.70)
    _ok("correct no-hint retention", r.retention, 0.77)
    _ok("correct routing",           r.routing,   "practice")

    # 5.1 Ceiling
    r = update_mastery(MasteryState(0.95, 0.97), "correct", False, _session(), no_persist)
    _ok("correct ceiling mastery",   r.mastery,   1.0)
    _ok("correct ceiling retention", r.retention, 1.0)

    # 5.2 Wrong
    r = update_mastery(MasteryState(0.30, 0.20), "wrong", False, _session(), no_persist)
    _ok("wrong mastery",   r.mastery,   0.22)
    _ok("wrong retention", r.retention, 0.15)

    # 5.2 Floor
    r = update_mastery(MasteryState(0.04, 0.02), "wrong", False, _session(), no_persist)
    _ok("wrong floor mastery",   r.mastery,   0.0)
    _ok("wrong floor retention", r.retention, 0.0)

    # 5.3 Hint + correct
    r = update_mastery(MasteryState(0.50, 0.60), "correct", True, _session(), no_persist)
    _ok("hint+correct mastery",   r.mastery,   0.57)
    _ok("hint+correct retention", r.retention, 0.65)

    # 5.3 Hint + wrong
    r = update_mastery(MasteryState(0.50, 0.60), "wrong", True, _session(), no_persist)
    _ok("hint+wrong mastery",   r.mastery,   0.42)
    _ok("hint+wrong retention", r.retention, 0.55)

    # 5.4 Skip
    r = update_mastery(MasteryState(0.20, 0.30), "skip", False, _session(), no_persist)
    _ok("skip mastery",   r.mastery,   0.15)
    _ok("skip retention", r.retention, 0.27)

    # 5.4 Skip floor
    r = update_mastery(MasteryState(0.0, 0.0), "skip", False, _session(), no_persist)
    _ok("skip floor mastery",   r.mastery,   0.0)
    _ok("skip floor retention", r.retention, 0.0)

    # 5.5 Lesson — first
    s = _session(False)
    r = update_mastery(MasteryState(0.72, 0.65), "lesson_complete", False, s, no_persist)
    _ok("lesson first mastery",       r.mastery,       0.77)
    _ok("lesson first retention",     r.retention,     0.69)
    _ok("lesson first bonus_awarded", r.bonus_awarded, True)

    # 5.5 Lesson — replay
    s = _session(True)
    r = update_mastery(MasteryState(0.77, 0.69), "lesson_complete", False, s, no_persist)
    _ok("lesson replay mastery",       r.mastery,       0.77)
    _ok("lesson replay retention",     r.retention,     0.69)
    _ok("lesson replay bonus_awarded", r.bonus_awarded, False)

    # 5.6 Quiz — first
    s = _session(False)
    r = update_mastery(MasteryState(0.80, 0.55), "quiz_complete", False, s, no_persist)
    _ok("quiz first mastery",   r.mastery,   0.88)
    _ok("quiz first retention", r.retention, 0.61)
    _ok("quiz routing",         r.routing,   "unlock_dependents")

    # 5.6 Quiz — replay
    s = _session(True)
    r = update_mastery(MasteryState(0.88, 0.61), "quiz_complete", False, s, no_persist)
    _ok("quiz replay mastery",       r.mastery,       0.88)
    _ok("quiz replay retention",     r.retention,     0.61)
    _ok("quiz replay bonus_awarded", r.bonus_awarded, False)

    # 5.7 Assessment — no change
    r = update_mastery(MasteryState(0.90, 0.85), "assessment_complete", False, _session(), no_persist)
    _ok("assessment mastery unchanged",   r.mastery,       0.90)
    _ok("assessment retention unchanged", r.retention,     0.85)
    _ok("assessment bonus_awarded",       r.bonus_awarded, False)

    # Login decay
    _ok("decay 10 days",  apply_login_decay(0.80, 10),  0.80 * (0.995 ** 10))
    _ok("decay 0 days",   apply_login_decay(0.80,  0),  0.80)
    _ok("decay negative", apply_login_decay(0.80, -5),  0.80)

    # Routing
    _ok("route 0.00", get_curriculum_action(0.00), "assign_first")
    _ok("route 0.20", get_curriculum_action(0.20), "remediate")
    _ok("route 0.30", get_curriculum_action(0.30), "remediate")
    _ok("route 0.31", get_curriculum_action(0.31), "continue")
    _ok("route 0.60", get_curriculum_action(0.60), "continue")
    _ok("route 0.61", get_curriculum_action(0.61), "practice")
    _ok("route 0.84", get_curriculum_action(0.84), "practice")
    _ok("route 0.85", get_curriculum_action(0.85), "unlock_dependents")
    _ok("route 1.00", get_curriculum_action(1.00), "unlock_dependents")

    print("\n=== done ===\n")


if __name__ == "__main__":
    run_tests()
```

---

## 12. Cross-Platform Validation Checklist

All implementations must pass every row. Tolerance: 1e-10.

**Question events** (`bonusAwarded` column only applies to completion events):

| # | State (M, R) | Event | Hint | bonus_awarded flag | Expected M | Expected R |
|---|---|---|---|---|---|---|
| 1 | 0.60, 0.70 | correct | false | — | 0.70 | 0.77 |
| 2 | 0.95, 0.97 | correct | false | — | 1.00 | 1.00 |
| 3 | 0.30, 0.20 | wrong | false | — | 0.22 | 0.15 |
| 4 | 0.04, 0.02 | wrong | false | — | 0.00 | 0.00 |
| 5 | 0.50, 0.60 | correct | true | — | 0.57 | 0.65 |
| 6 | 0.50, 0.60 | wrong | true | — | 0.42 | 0.55 |
| 7 | 0.20, 0.30 | skip | false | — | 0.15 | 0.27 |
| 8 | 0.00, 0.00 | skip | false | — | 0.00 | 0.00 |

**Completion events:**

| # | State (M, R) | Event | bonus_awarded (in) | Expected M | Expected R | bonus_awarded (out) |
|---|---|---|---|---|---|---|
| 9 | 0.72, 0.65 | lesson_complete | false | 0.77 | 0.69 | true |
| 10 | 0.77, 0.69 | lesson_complete | true | 0.77 | 0.69 | false |
| 11 | 0.80, 0.55 | quiz_complete | false | 0.88 | 0.61 | true |
| 12 | 0.88, 0.61 | quiz_complete | true | 0.88 | 0.61 | false |
| 13 | 0.90, 0.85 | assessment_complete | false | **0.90** | **0.85** | false |

**Routing:**

| # | Mastery | Expected Action |
|---|---|---|
| 14 | 0.00 | assign_first |
| 15 | 0.30 | remediate |
| 16 | 0.31 | continue |
| 17 | 0.60 | continue |
| 18 | 0.61 | practice |
| 19 | 0.84 | practice |
| 20 | 0.85 | unlock_dependents |
| 21 | 1.00 | unlock_dependents |

If any row fails, do not ship.

---

## 13. Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-02 | Initial canonical release |
| 2.0.0 | 2026-06-02 | Completion bonuses: one-time only (first completion per content version). Assessment completion: zero mastery/retention bonus (diagnostic only). Mastery bands: Mastered threshold raised from 0.75 to 0.85, aligned with Neo4j prerequisite gate. Retention decay: login decay formula added (0.995^days). Curriculum routing: explicit thresholds and getCurriculumAction function added. Validation table expanded to 21 cases. |

---

*End of mastery_engine.md — v2.0.0*