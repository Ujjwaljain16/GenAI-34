# ADAPTIVE BOOK-LEARNING PLATFORM
## Final Architecture — Single Source of Truth

---

## PHASE 1 — PRODUCT CRITIQUE & DECISION TABLE

Every idea from all research documents has been reviewed and ruled on. No idea is pending. Every decision is final.

| Idea | Verdict | Reason |
|---|---|---|
| Bayesian Knowledge Tracing (BKT) | **KEEP — simplified** | Proven, interpretable, computationally cheap. Implement as running mastery score with guess/slip parameters. No BKT library required. |
| Deep Knowledge Tracing (DKT) | **REMOVE** | Requires thousands of training interactions. Zero training data available. 14 days is impossible. Mention in viva as future direction only. |
| Item Response Theory (IRT) | **REMOVE** | Requires psychometric calibration data. Complexity delivers no demo value. The viva story is weaker than BKT. |
| Spaced Repetition (SM2) | **KEEP** | 50 years of evidence. Ebbinghaus-grounded. Implement in 30 lines of Python. High learning impact, low effort. Non-negotiable. |
| Bloom's Taxonomy tagging | **KEEP** | Structure every question with a Bloom level. Enforce Understand → Apply → Analyze escalation. Low effort, enormous viva credibility. |
| Socratic Tutor Chat | **KEEP — core differentiator** | No other capstone does hard-enforced Socratic mode. The guardrail function (not just prompt) is the distinguishing claim. |
| Multi-Agent Architecture | **KEEP — as workflow agents** | True autonomous MAS is unreliable in 14 days. Named workflow agents with shared state give all the viva story with none of the fragility. |
| Neo4j Knowledge Graph | **KEEP — with discipline** | Prerequisite traversal is a natural graph operation. Cypher is explainable in a viva. The visible graph IS the demo centerpiece. Graph is generated dynamically per uploaded book via the Ingestion Pipeline. |
| PDF Book Ingestion Pipeline | **KEEP — core differentiator** | LLM-driven concept and edge extraction from uploaded textbooks. The graph is not pre-seeded; it is built from the user's actual book. This is what separates the platform from every hardcoded alternative. |
| RAG on Course Content | **KEEP — book corpus** | Uploaded book is chunked into ChromaDB. Prevents hallucination. Grounds all tutor and lesson responses in the student's actual reading material. Essential for viva credibility. |
| LLM Curriculum Generation | **KEEP — graph-grounded only** | LLM ranks and explains; it cannot invent concepts. All concept IDs come from Neo4j query results. Curriculum Agent receives a list derived from the ingested graph, not a blank page. |
| Mastery Learning gating | **KEEP** | Core learning science. 80% mastery threshold before concept unlock. Non-negotiable. |
| Full IRT calibration | **REMOVE** | See IRT above. |
| Attention span tracking | **REMOVE** | Too noisy. No reliable signal in 14 days. Gimmick. |
| Emotion/engagement detection | **REMOVE** | Requires camera, ML pipeline, privacy considerations. Zero educational ROI at this scale. |
| Spaced repetition scheduler | **KEEP** | SM2 with timestamps. Due dates stored in PostgreSQL. Session opener always starts with spaced-due concepts. |
| Learning Path Visualization (D3.js) | **KEEP — highest priority** | Best demo moment. Nodes light up in real time. Students see their own cognitive map drawn from the book they uploaded. No competitor offers this. |
| Code Autograder | **REMOVE** | Domain-agnostic. The platform serves arbitrary textbooks; automated code grading is not generalizable. Questions default to open-ended and MCQ formats. |
| Voice Interface | **REMOVE** | Out of scope for 14 days. Not in MVP. |
| Confidence Calibration | **KEEP — stretch** | Student predicts score before quiz. Delta shown after. Low effort, impressive metacognition story. |
| Curriculum Replan on Mastery Drop | **KEEP — stretch** | If mastery drops mid-session, Curriculum Agent re-queries Neo4j and updates path. Powerful demo moment. |
| Emotion in tutor feedback | **REMOVE** | Sentiment analysis pipeline adds zero learning value. Tutor tone is calibrated in system prompt. |
| Social features / leaderboards | **REMOVE** | Wrong product type. This is a personal cognitive tool, not a social platform. |
| AR/VR | **REMOVE** | Not relevant to a 14-day academic capstone. |
| Teacher dashboard (class heatmap) | **KEEP — stretch only** | Impressive for judges if time allows. Do not block core features for this. |

**Overengineering identified and rejected:** DKT, IRT, emotion detection, voice interface, social graphs, AR/VR, code autograders, domain-specific hardcoding, manually seeded concept lists.

**Undervalued ideas elevated:** PDF ingestion pipeline as primary content source, error taxonomy (not just mastery score), cross-session tutor memory opener, hard Socratic guardrail as code not just prompt, visible knowledge graph as primary UI.

---

## PHASE 2 — FINAL PRODUCT VISION

### What Exactly Are We Building?

A web application for students learning any subject from an uploaded PDF textbook. The platform runs an LLM-driven ingestion pipeline to extract concepts and prerequisite relationships from the book, constructs a knowledge graph in Neo4j, runs an adaptive diagnostic assessment, builds a personalized prerequisite-aware curriculum path, delivers chunked lessons with Bloom's-escalating questions, and provides a Socratic tutor that remembers every mistake the student has ever made — across every session — grounded entirely in the student's own book.

### What Makes It Different?

Six specific design decisions no competitor implements simultaneously:

1. The knowledge graph is built from the student's uploaded book — not a hardcoded syllabus
2. The knowledge graph is the UI — students see their own cognitive map of the book in real time
3. Error taxonomy, not just mastery score — every wrong answer is classified by misconception type
4. Socratic mode is architecturally enforced — a guardrail function blocks direct answers, not just a soft prompt
5. Cross-session memory is functional — the tutor's first words reference the student's previous struggles
6. Every technical choice maps to a named learning science citation

### Why Would a Student Use It?

Because it opens every session with: *"Last time you kept confusing osmosis with diffusion in the membrane transport chapter — want to fix that today?"* No platform does this. ChatGPT resets. YouTube is passive. Coursera doesn't know who you are — and more importantly, it doesn't know your book.

### Why Would a Professor Like It?

Because every architectural choice is grounded in peer-reviewed learning science. BKT from Knowledge Tracing literature. SM2 from Ebbinghaus. Session opener from the testing effect (Roediger & Karpicke, 2006). Bloom's gating from mastery learning meta-analyses. And the ingestion pipeline means students can bring any textbook to the platform — the system adapts to the course, not the other way around.

### Why Would a Hackathon Judge Like It?

Because in 60 seconds of demo, they watch a student upload a PDF, a knowledge graph appear from thin air, light up node by node as the student answers questions, and rearrange the curriculum path in real time. It is visually unlike anything else in the room.

### Why Would a Startup Founder Like It?

Because the core asset — a persistent, cross-session cognitive model per student, grounded in their own reading material — is defensible, compounds over time, and is not replicable by pasting a system prompt into ChatGPT.

---

### Product Vision Statement

> **"The AI tutor that reads your textbook, builds a map of your mind, and teaches to the gaps — remembering every mistake across every session."**

### One-Line Pitch

> *"Upload your textbook. Get a personalized learning path powered by a knowledge graph that shows you exactly what you know, what you're forgetting, and what you need to learn next."*

### 30-Second Demo Pitch

> "Watch this. A student uploads their biology textbook. In under 60 seconds, this knowledge graph appears — concepts extracted from the book, prerequisite edges drawn automatically. Eight adaptive questions — and the graph lights up, showing exactly what they know and what's locked. The system generates their personal curriculum path. They study one concept. They ask the tutor for help — and it never gives the answer. It asks questions back. They return tomorrow and the tutor opens with: 'Yesterday you struggled with membrane transport — let's fix that.' No platform does this. This is what we built."

### 2-Minute Project Presentation Pitch

> "Every learning platform today has the same problem: they know you failed a quiz, but they don't know why. And every session, they forget you entirely. Worse: they force you into their syllabus. You uploaded your textbook — but you're learning from their version of your course.
>
> We built a system that fixes all three. A student uploads a PDF textbook. An ingestion pipeline — built on LLM-driven concept extraction — reads the book, identifies the key concepts, infers the prerequisite relationships, and writes them into a live Neo4j knowledge graph. This takes under 60 seconds. The graph is not pre-seeded. It comes from the student's actual book.
>
> When a student logs in, an adaptive assessment runs — eight questions, each one chosen based on the previous answer. The result updates that knowledge graph: a visual map of what this student knows, what they're confused about, and what they're ready to learn. This graph is not infrastructure — it is the product.
>
> The curriculum engine queries the graph to find every concept where prerequisites are satisfied but mastery is below 80%. It builds a personalized learning path — not a generic syllabus, but a path calculated from this student's actual cognitive state, applied to their actual book.
>
> Lessons are chunked to three concepts maximum, with questions that escalate through Bloom's taxonomy — from understanding to application to analysis. No student can plateau at memorization.
>
> The Socratic tutor never gives answers. It is architecturally enforced — a guardrail function blocks any response containing the solution. It asks guiding questions. And it references the student's error history: every wrong answer is classified by misconception type, stored, and injected into the tutor's context every single session.
>
> The result is a tutor that says, three sessions in: 'You keep confusing osmosis with diffusion. Here's a question designed for that specific misconception.' No other platform does this.
>
> We built this using Neo4j for the prerequisite graph, Gemini 2.5 Flash for six specialized agents including a dedicated Ingestion Agent, BKT for mastery tracking, SM2 for spaced repetition scheduling, and ChromaDB for RAG-grounded lesson delivery from the student's uploaded book. Every decision is backed by named learning science research. This is not an AI chatbot with a progress bar. This is a persistent cognitive model of the student, built from their own reading material, made visible and actionable."

---

## PHASE 3 — FINAL DOMAIN DECISION

### Chosen Domain: Any Subject — Determined by the Uploaded Textbook

**The platform is domain-agnostic by design.** The knowledge graph is extracted from the student's PDF at upload time. The same infrastructure that handles a biology textbook handles an economics textbook, a physics textbook, or a history reader. Domain is not a configuration parameter — it is an emergent property of the ingestion pipeline.

**Examples of valid input books and their extracted concept structures:**

| Book Type | Example Concepts | Example Prerequisite Edge |
|---|---|---|
| Biology | Photosynthesis, Cellular Respiration, ATP Synthesis | Cellular Respiration requires Photosynthesis |
| Economics | Supply, Demand, Elasticity, Market Equilibrium | Elasticity requires Supply and Demand |
| Physics | Kinematics, Newton's Laws, Momentum, Energy | Momentum requires Newton's Laws |
| History | Causes of WWI, Treaty of Versailles, Rise of Fascism | Rise of Fascism requires Treaty of Versailles |

**Why a domain-agnostic platform wins on all criteria:**

- **Demo impact:** The ingestion pipeline running live — a graph materializing from a PDF in real time — is more dramatic than any pre-seeded domain.
- **Viva performance:** Explaining *how* the LLM extracts and validates concepts is more architecturally interesting than explaining *which* 50 DSA nodes were manually curated.
- **Real market:** No platform currently adapts to the student's actual textbook. This is the unsolved problem.
- **Evaluator accessibility:** Evaluators from any department recognize their subject being handled by the system.
- **Educational value:** The student's own book is their ground truth. Grounding instruction in that source removes the mismatch between what they read and what a platform teaches.

**Domain is not locked: it is determined at upload time.**

---

## PHASE 4 — FINAL FEATURE SET

### Tier 1 — Mandatory Features (Core Loop)

| Feature | Why It Exists | User Value | Educational Value | Technical Value | Demo Value | Viva Value |
|---|---|---|---|---|---|---|
| PDF Book Ingestion Pipeline | Cold start for a domain-agnostic platform; creates the knowledge graph | Student's own book drives everything | Grounds all instruction in the student's actual reading material | Ingestion Agent + LLM concept/edge extraction + Neo4j write | Watch graph materialize from a PDF upload in real time | Explain LLM-driven extraction, concept validation, edge inference |
| Adaptive Diagnostic Assessment (CAT-style, 8 questions) | Cold start solution for learner model; creates initial mastery profile | Student gets personalized path immediately | Assesses prerequisite knowledge before instruction | Assessment Agent + BKT initialization | Watch graph light up from grey in real time | Explain CAT, BKT priors, cold start strategy |
| Knowledge Graph Visualization (D3.js, mastery-colored) | The product's core UI — student sees their cognitive map of the book | Understand exactly what you know and what unlocks next | Metacognitive awareness of knowledge structure derived from the actual book | Neo4j + D3.js force-directed rendering | Most memorable visual in the room | Explain Neo4j, graph traversal, Cypher, ingestion pipeline |
| Prerequisite-Aware Curriculum Generation | Guarantees no gaps; ensures pedagogically valid sequence | Path calculated from your knowledge state and your book's structure | Mastery learning + prerequisite enforcement from extracted graph | Curriculum Agent + Neo4j traversal query | Path highlighted on graph after assessment | Explain topological sort, mastery gating |
| Chunked Lesson Delivery (max 3 concepts, Bloom-escalating) | Cognitive load compliance | Lessons don't overwhelm; questions get harder as you progress | Cognitive Load Theory + Bloom's Taxonomy | Lesson Agent + Bloom level tagging | Live lesson walk-through with question escalation | Cite Sweller (1988), Bloom (1956) |
| Socratic Tutor with Hard Guardrail | Core differentiator | Never told the answer; forced to think | Socratic learning, generation effect | Guardrail function + system prompt layers | "Notice it never gives the answer" live moment | Explain guardrail architecture, question ratio metric |
| Cross-Session Error Memory in Tutor | Differentiator #2 — no competitor does this | Tutor remembers why you failed last Tuesday | Error-targeted remediation | Error taxonomy + session summary injection | Tutor opens new session with past mistake reference | Explain error taxonomy tagging, memory injection |
| Spaced Review Session Opener | Retrieval practice before new content | Never forget what you learned before | Testing effect (Roediger & Karpicke, 2006) | SM2 scheduler + PostgreSQL due dates | "First 3 questions always from what you're forgetting" | Cite Ebbinghaus, explain SM2 algorithm |
| Mastery + Retention Dashboard | Student sees their full cognitive state mapped to the book | Know exactly what to review and when | Forgetting curve awareness | PostgreSQL queries + chart rendering | Visual dashboard with decay curves | Explain retention probability formula |
| Error Taxonomy Display | Student sees their own pattern of mistakes | "I always confuse osmosis with diffusion" becomes visible | Deliberate practice targeting | LLM error classifier + PostgreSQL error_log | "Your most common mistakes in Membrane Transport" panel | Explain misconception types, classification prompt |

### Tier 2 — Differentiator Features (Build if ahead of schedule)

| Feature | Why It Exists | Value Summary |
|---|---|---|
| Confidence Calibration (predict → compare) | Metacognition training; identify overconfident students | Student predicts score before quiz; delta shown after; 30 minutes to implement |
| Curriculum Replan on Mastery Drop | Dynamic adaptation mid-session | If mastery drops below 0.6 during a session, Curriculum Agent re-queries Neo4j and updates remaining path |
| Bloom Level Badge per Concept | Visual Bloom progression | Each node in graph shows highest Bloom level achieved (R/U/A/An) — low effort, high viva value |
| Session Summary Generation | Powers cross-session memory | LLM generates 1-paragraph summary after each session; stored in PostgreSQL; fed to Tutor Agent on next login |
| Multi-Book Support | Platform utility | Student can have multiple books as separate "courses," each with its own knowledge graph |

### Tier 3 — Bonus Features (Mention in viva, build only if all Tier 1+2 complete)

| Feature | Value |
|---|---|
| Teacher/Instructor Dashboard (class mastery heatmap) | High judge impact; demonstrates real-world use case |
| BKT Parameter Estimation from Data | Research-grade; mention as "with more interaction data, we would estimate individual guess/slip probabilities" |
| Cross-Book Concept Deduplication | When a concept appears in multiple books, merge the node and pool mastery evidence |

**Removed entirely:** Code autograder, domain lock, hardcoded concept lists, voice, emotion detection, AR/VR, social features, DKT, full IRT, leaderboards, gamification narratives.

---

## PHASE 5 — LEARNING SCIENCE ARCHITECTURE

### Mastery Learning

**Exact Implementation:** Each concept has a mastery score (float 0.0–1.0). A concept is "mastered" when score ≥ 0.80. A concept is "locked" in the curriculum until all its prerequisite concepts are mastered. The Progress Agent updates mastery after every quiz answer.

**Data Model:**
```sql
mastery_scores(student_id UUID, concept_id VARCHAR, score FLOAT, attempts INT, updated_at TIMESTAMP)
```

**Update Logic (BKT):**
```python
def update_mastery_bkt(prior, correct, p_guess=0.25, p_slip=0.10, p_transit=0.30):
    if correct:
        likelihood = prior * (1 - p_slip) + (1 - prior) * p_guess
        posterior = (prior * (1 - p_slip)) / likelihood
    else:
        likelihood = prior * p_slip + (1 - prior) * (1 - p_guess)
        posterior = (prior * p_slip) / likelihood
    new_mastery = posterior + (1 - posterior) * p_transit
    return min(new_mastery, 1.0)
```

**UI Impact:** Node color in D3.js graph maps to mastery score. Grey = unassessed. Red = 0–0.4. Yellow = 0.4–0.8. Green = 0.8+. Node border glows when newly unlocked.

### Knowledge Tracing (BKT)

**Exact Implementation:** Four parameters per concept: p_init (prior probability of mastery before any observation), p_transit (probability of learning after each attempt), p_guess (probability of correct answer despite not mastered), p_slip (probability of wrong answer despite mastered). Default values: p_init=0.3, p_transit=0.3, p_guess=0.25, p_slip=0.10. Updated after every question response.

**Data Model:** Stored as columns in mastery_scores table. No separate BKT table needed at this scale.

**Update Logic:** See update_mastery_bkt function above.

**UI Impact:** Mastery score drives node color, prerequisite unlock, and spaced repetition scheduling.

### Bloom's Taxonomy Integration

**Exact Implementation:** Every question in the system is tagged with one of six Bloom levels: Remember (1), Understand (2), Apply (3), Analyze (4), Evaluate (5), Create (6). The Lesson Agent is instructed to generate questions in ascending order. A student cannot receive an Analyze-level question on a concept until they have demonstrated Apply-level proficiency (mastery ≥ 0.70 at Apply level).

**Data Model:**
```sql
bloom_progress(student_id UUID, concept_id VARCHAR, highest_bloom_level INT, updated_at TIMESTAMP)
```

**Update Logic:** After each correct answer, if bloom_level of question > current highest_bloom_level for that concept, update the record.

**UI Impact:** Each concept node in D3.js graph displays a small badge: R / U / A / An / E / C. Color of badge indicates progress.

### Retrieval Practice Integration

**Exact Implementation:** The first 3 questions of every session are drawn from the spaced review queue (concepts with retention_probability < 0.70 and due_date ≤ today). These are served before any new lesson content. This is architecturally enforced in the session orchestration logic, not left to chance.

**Data Model:**
```sql
spaced_review_queue(student_id UUID, concept_id VARCHAR, due_date DATE, interval_days INT, stability_days FLOAT, last_correct TIMESTAMP)
```

**Update Logic (SM2):**
```python
def sm2_update(interval, repetitions, ease_factor, quality):
    # quality: 0-5 (0=total blackout, 5=perfect)
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0: interval = 1
        elif repetitions == 1: interval = 6
        else: interval = round(interval * ease_factor)
        repetitions += 1
    ease_factor = max(1.3, ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return interval, repetitions, ease_factor
```

**UI Impact:** Session opens with "Quick Review" mode. Progress bar shows "3 reviews before new content." Students see a countdown.

### Spaced Repetition Integration

**Exact Implementation:** After every correct answer, stability_days increases (multiplied by ease_factor). After an incorrect answer, stability resets to 1 day. Retention probability is computed as: `R = e^(-t / S)` where t = days since last correct, S = stability_days. Concepts with R < 0.70 are flagged for review.

**Data Model:** See spaced_review_queue above.

**Update Logic:** Progress Agent runs SM2 update after each quiz response. Due dates recalculated and written to PostgreSQL.

**UI Impact:** Dashboard shows a "Forgetting Curve" chart per concept — actual retention probability decay over time with the scheduled review date marked.

### Socratic Learning Integration

**Exact Implementation:** Three enforcement layers:
1. System prompt with absolute prohibition and worked examples of correct vs incorrect tutor responses
2. Guardrail function: before any Tutor Agent response is returned to the user, a classifier checks if the response contains the answer to the current question (semantic similarity using embedding cosine distance threshold 0.85). If detected, the response is discarded and re-prompted with `temperature=0`.
3. Progressive hint structure: 3 pre-generated hints per question, released one at a time. Free-form LLM response only begins after hint 1 is given.

**Data Model:** Hints stored in Questions table. Hint release state tracked in Redis session.

**Update Logic:** After 3 identical wrong answers, guardrail escalates from guided question to targeted hint addressing the student's specific error type from error_taxonomy.

**UI Impact:** Tutor chat shows "Hint 1 of 3" badge. User can request next hint. Answer is never shown.

---

## PHASE 6 — LEARNER MODEL DESIGN

### What Is Stored and Why

| Field | Why It Exists | How Updated | Which Feature Consumes It |
|---|---|---|---|
| `mastery[concept_id].score` | Core adaptive signal — drives all curriculum decisions | BKT update after each quiz answer | Curriculum Agent, graph node color, unlock logic |
| `mastery[concept_id].attempts` | Confidence in the mastery estimate | Incremented after each answer | BKT guess/slip parameter weighting |
| `retention[concept_id].probability` | Prevents forgetting — spaced repetition engine | Ebbinghaus decay recalculated each session start | Session opener, spaced review queue |
| `retention[concept_id].stability_days` | SM2 interval control | SM2 update after each correct retrieval | Due date calculation |
| `errors[concept_id][]` | Targeted remediation — the key differentiator | LLM classifier tags wrong answer with error type | Tutor Agent system prompt injection, error taxonomy display |
| `bloom_level[concept_id]` | Prevents cognitive plateau | Updated when student succeeds at higher Bloom level | Lesson Agent question difficulty floor |
| `session_summaries[]` | Cross-session tutor context | LLM generates summary at end of each session | Tutor opening message, Lesson Agent context |
| `spaced_review_queue[]` | Retrieval practice scheduling | SM2 update | Session opener question selection |
| `preferred_domain` | Example personalization | Inferred from free-text responses | Lesson Agent example generation |
| `confidence_delta` | Metacognition tracking | Computed after each predict→compare event | Dashboard metacognition section |
| `learning_velocity` | Session pacing | Rate of mastery gain per session (rolling average) | Curriculum Agent: concepts per session count |

### What Is NOT Stored

- Raw conversation transcripts (privacy risk, storage cost, no query value — store LLM summaries instead)
- Emotion/attention metrics (unreliable, no implementation path)
- Full quiz answer text beyond the session (error type classification is sufficient)
- Raw timestamps beyond what SM2 requires

### Final JSON Schema

```json
{
  "student_id": "uuid-v4",
  "created_at": "2026-06-01T10:00:00Z",
  "preferred_domain": "gaming",
  "learning_velocity": 0.12,
  "confidence_calibration": {
    "avg_overconfidence_delta": 0.18,
    "total_predictions": 24
  },
  "active_book": {
    "book_id": "uuid-v4",
    "title": "Campbell Biology, 12th Edition",
    "total_concepts": 84,
    "ingestion_status": "complete"
  },
  "mastery": {
    "photosynthesis_light_reactions": {
      "score": 0.85,
      "attempts": 12,
      "updated_at": "2026-06-01T10:45:00Z"
    },
    "membrane_transport_osmosis": {
      "score": 0.45,
      "attempts": 7,
      "updated_at": "2026-06-01T11:00:00Z"
    }
  },
  "retention": {
    "photosynthesis_light_reactions": {
      "probability": 0.91,
      "stability_days": 14.0,
      "last_reviewed": "2026-05-28T10:00:00Z"
    },
    "membrane_transport_osmosis": {
      "probability": 0.62,
      "stability_days": 3.0,
      "last_reviewed": "2026-05-30T10:00:00Z"
    }
  },
  "errors": {
    "membrane_transport_osmosis": [
      { "type": "confuses_osmosis_with_diffusion", "count": 3, "last": "2026-06-01T11:00:00Z" },
      { "type": "ignores_solute_concentration_gradient", "count": 2, "last": "2026-05-30T10:00:00Z" }
    ]
  },
  "bloom_level": {
    "photosynthesis_light_reactions": "Analyze",
    "membrane_transport_osmosis": "Apply"
  },
  "spaced_review_queue": [
    {
      "concept_id": "membrane_transport_osmosis",
      "due_date": "2026-06-02",
      "interval_days": 2,
      "ease_factor": 2.1,
      "repetitions": 3
    }
  ],
  "session_summaries": [
    {
      "date": "2026-06-01",
      "book_id": "uuid-v4",
      "topics_covered": ["membrane_transport_osmosis", "membrane_transport_active"],
      "breakthrough": "understood the role of ATP in active transport",
      "struggles": ["osmosis directionality relative to solute concentration"],
      "summary": "Student demonstrated Apply-level understanding of active transport but consistently failed osmosis directionality questions. Confused which direction water moves relative to solute concentration in all 3 attempts."
    }
  ]
}
```

### Final Database Schema

```sql
-- PostgreSQL

CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    preferred_domain VARCHAR(100),
    learning_velocity FLOAT DEFAULT 0.10,
    avg_overconfidence_delta FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(500),
    file_path TEXT NOT NULL,
    ingestion_status VARCHAR(50) DEFAULT 'pending', -- pending | processing | complete | failed
    total_concepts INT,
    total_edges INT,
    ingested_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE mastery_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    concept_id VARCHAR(255) NOT NULL,
    score FLOAT NOT NULL DEFAULT 0.0,
    attempts INT NOT NULL DEFAULT 0,
    p_init FLOAT DEFAULT 0.3,
    p_transit FLOAT DEFAULT 0.3,
    p_guess FLOAT DEFAULT 0.25,
    p_slip FLOAT DEFAULT 0.10,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, book_id, concept_id)
);

CREATE TABLE bloom_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    concept_id VARCHAR(255) NOT NULL,
    highest_bloom_level INT NOT NULL DEFAULT 1,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, book_id, concept_id)
);

CREATE TABLE spaced_review_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    concept_id VARCHAR(255) NOT NULL,
    due_date DATE NOT NULL,
    interval_days INT NOT NULL DEFAULT 1,
    ease_factor FLOAT NOT NULL DEFAULT 2.5,
    repetitions INT NOT NULL DEFAULT 0,
    stability_days FLOAT NOT NULL DEFAULT 1.0,
    last_correct TIMESTAMP,
    UNIQUE(student_id, book_id, concept_id)
);

CREATE TABLE error_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    concept_id VARCHAR(255) NOT NULL,
    error_type VARCHAR(255) NOT NULL,
    count INT NOT NULL DEFAULT 1,
    last_occurrence TIMESTAMP DEFAULT NOW()
);

CREATE TABLE session_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    session_date DATE NOT NULL,
    topics_covered TEXT[],
    breakthroughs TEXT,
    struggles TEXT,
    summary_text TEXT NOT NULL,
    embedding_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    concept_id VARCHAR(255) NOT NULL,
    question_id VARCHAR(255) NOT NULL,
    bloom_level INT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    student_answer TEXT,
    error_type VARCHAR(255),
    time_taken_seconds INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_mastery_student_book ON mastery_scores(student_id, book_id);
CREATE INDEX idx_mastery_score ON mastery_scores(score);
CREATE INDEX idx_review_queue_due ON spaced_review_queue(student_id, book_id, due_date);
CREATE INDEX idx_error_log_student_concept ON error_log(student_id, book_id, concept_id);
CREATE INDEX idx_session_student ON session_summaries(student_id, session_date DESC);
CREATE INDEX idx_books_student ON books(student_id);
```

---

## PHASE 7 — KNOWLEDGE GRAPH DESIGN

### Decision: YES, Use Neo4j — Graph Is Generated from the Uploaded Book

**Why Neo4j exists in the architecture:**

Prerequisite traversal — "find all concepts this student is ready to unlock given their current mastery" — is a natural graph pattern. In PostgreSQL, this is an awkward multi-join recursive CTE. In Cypher, it is four lines. The D3.js visualization also reads directly from Neo4j's REST API, eliminating a translation layer.

Critically: the graph is not manually authored. The Ingestion Agent reads the uploaded PDF, identifies key concepts chapter by chapter, infers prerequisite relationships using LLM reasoning, validates the output, and writes nodes and edges to Neo4j. The graph is a byproduct of the book — unique per upload.

**What breaks if Neo4j is removed:**

The Curriculum Agent degrades to a static topic list. Dynamic prerequisite enforcement becomes hardcoded logic that cannot adapt to a new book. The visible knowledge graph loses its live query backend. The project becomes an AI chatbot with a progress bar — exactly what every other capstone already is.

**How it contributes to personalization:**

Neo4j stores mastery edges per student per book. Every curriculum generation query starts from the student node, traverses HAS_MASTERY edges to find mastered concepts, follows PREREQUISITE_OF edges to find ready-to-learn concepts, and ranks them by difficulty and dependency centrality. The path is unique per student per session per book.

### Node Types

```cypher
// Node definitions

(:Book {
    id: STRING,              // UUID
    title: STRING,
    author: STRING,
    total_pages: INT,
    ingestion_status: STRING // "complete" | "processing" | "failed"
})

(:Concept {
    id: STRING,              // e.g. "membrane_transport_osmosis" — slugified from extraction
    name: STRING,            // e.g. "Membrane Transport: Osmosis"
    book_id: STRING,         // links to Book node
    chapter: INT,            // source chapter number
    page_range: STRING,      // e.g. "112-118"
    difficulty: INT,         // 1-5, inferred by Ingestion Agent
    description: STRING,     // LLM-generated one-sentence summary
    bloom_target: INT,       // target Bloom level for this concept
    estimated_minutes: INT
})

(:Lesson {
    id: STRING,
    concept_id: STRING,
    title: STRING,
    content_path: STRING,    // path to ChromaDB chunk or generated text
    bloom_level: INT,
    estimated_minutes: INT
})

(:Question {
    id: STRING,
    text: STRING,
    type: STRING,            // "mcq" | "open"
    bloom_level: INT,
    difficulty: INT,
    answer_key: STRING,
    hint_1: STRING,
    hint_2: STRING,
    hint_3: STRING
})

(:ErrorType {
    id: STRING,
    description: STRING,
    misconception: STRING,
    remediation_hint: STRING
})
```

### Edge Types

```cypher
// Edge definitions

(:Book)-[:HAS_CONCEPT]->(:Concept)
// All concepts belonging to a book

(:Concept)-[:PREREQUISITE_OF {strength: FLOAT, inferred_by: STRING}]->(:Concept)
// strength 0-1: how strongly concept A must be mastered before B
// inferred_by: "ingestion_agent" | "manual_correction"

(:Concept)-[:UNLOCKS]->(:Concept)
// Inverse of PREREQUISITE_OF for traversal efficiency

(:Lesson)-[:TEACHES {coverage: STRING}]->(:Concept)
// coverage: "primary" | "secondary"

(:Question)-[:ASSESSES]->(:Concept)
(:Question)-[:TAGGED_BLOOM {level: INT}]->(:Concept)
(:Concept)-[:HAS_QUESTION]->(:Question)

// Per-student dynamic edges (written by Progress Agent)
(:Student)-[:HAS_MASTERY {score: FLOAT, updated_at: DATETIME, book_id: STRING}]->(:Concept)
(:Student)-[:COMMITTED_ERROR {count: INT, error_type: STRING, concept_id: STRING}]->(:ErrorType)
```

### Ingestion-Generated Graph Example

When a student uploads *Campbell Biology, 12th Edition*, the Ingestion Agent produces a graph with edges such as:

```
Cell Structure → Membrane Structure → Membrane Transport (Passive)
Membrane Transport (Passive) → Membrane Transport (Active)
Membrane Transport (Active) → Cell Signaling
Photosynthesis (Light Reactions) → Photosynthesis (Calvin Cycle)
Photosynthesis (Calvin Cycle) → Cellular Respiration
Cellular Respiration → ATP Synthesis
DNA Structure → DNA Replication
DNA Replication → Transcription
Transcription → Translation
```

These edges are produced by the Ingestion Agent — not typed by a developer — and vary entirely by book.

### Cypher Query Examples

```cypher
-- Find all concepts student is ready to unlock from a specific book (prerequisites mastered >= 0.80)
MATCH (s:Student {id: $student_id})-[m:HAS_MASTERY]->(mastered:Concept)
WHERE m.score >= 0.80 AND m.book_id = $book_id
WITH collect(mastered.id) AS mastered_ids, s
MATCH (next:Concept {book_id: $book_id})
WHERE ALL(prereq IN [(next)<-[:PREREQUISITE_OF]-(p:Concept) | p.id]
      WHERE prereq IN mastered_ids)
AND NOT EXISTS {
    MATCH (s)-[hm:HAS_MASTERY]->(next)
    WHERE hm.score >= 0.80 AND hm.book_id = $book_id
}
RETURN next
ORDER BY next.difficulty ASC
LIMIT 5;

-- Find weakest unmastered concepts with available lessons
MATCH (s:Student {id: $student_id})-[m:HAS_MASTERY]->(c:Concept {book_id: $book_id})
WHERE m.score < 0.60 AND m.book_id = $book_id
MATCH (l:Lesson)-[:TEACHES {coverage: "primary"}]->(c)
RETURN l, c, m.score
ORDER BY m.score ASC
LIMIT 3;

-- Find student's error history for a concept (tutor context injection)
MATCH (s:Student {id: $student_id})-[e:COMMITTED_ERROR]->(err:ErrorType)
WHERE e.concept_id = $concept_id
RETURN err.description, err.remediation_hint, e.count
ORDER BY e.count DESC;

-- Get full curriculum path for a book (for visualization)
MATCH (b:Book {id: $book_id})-[:HAS_CONCEPT]->(c:Concept)
OPTIONAL MATCH (c)-[r:PREREQUISITE_OF]->(c2:Concept {book_id: $book_id})
RETURN c, r, c2;

-- Update student mastery edge after quiz
MERGE (s:Student {id: $student_id})-[m:HAS_MASTERY]->(c:Concept {id: $concept_id})
SET m.score = $new_score, m.updated_at = datetime(), m.book_id = $book_id
RETURN m;

-- Find all concepts for a book ordered by chapter and difficulty (ingestion validation)
MATCH (b:Book {id: $book_id})-[:HAS_CONCEPT]->(c:Concept)
RETURN c ORDER BY c.chapter ASC, c.difficulty ASC;
```

---

## PHASE 7A — PDF INGESTION PIPELINE

### Overview

The Ingestion Pipeline is the mechanism that converts an uploaded PDF textbook into a Neo4j knowledge graph and a ChromaDB lesson corpus. It runs once per book upload, asynchronously, and produces all artifacts consumed by the adaptive learning loop.

### Pipeline Stages

```
Student uploads PDF
        ↓
Stage 1: Text Extraction (PyMuPDF)
  → Extract raw text per page with page numbers
  → Preserve chapter/section heading structure
  → Split into chapter-level segments
        ↓
Stage 2: Concept Extraction (Ingestion Agent — Gemini 2.5 Flash)
  → For each chapter segment, prompt LLM to identify key concepts
  → Output: list of {name, slug_id, description, bloom_target, difficulty, chapter, page_range}
  → Validation: deduplicate slugs, enforce max 15 concepts per chapter
        ↓
Stage 3: Prerequisite Edge Inference (Ingestion Agent — second pass)
  → Given full concept list, prompt LLM to infer prerequisite relationships
  → Output: list of {from_concept_id, to_concept_id, strength, rationale}
  → Validation: reject self-loops, reject transitive cycles of depth > 5
        ↓
Stage 4: Graph Write (Neo4j)
  → Write all Concept nodes with MERGE (idempotent)
  → Write all PREREQUISITE_OF edges with MERGE
  → Write UNLOCKS inverse edges
  → Update Book node: ingestion_status = "complete", total_concepts, total_edges
        ↓
Stage 5: Lesson Chunk Ingestion (ChromaDB)
  → Chunk book text into 300-token segments with 50-token overlap
  → Tag each chunk with concept_id(s) from Stage 2
  → Embed with models/text-embedding-004
  → Write to ChromaDB collection keyed by book_id
        ↓
Stage 6: Question Pre-generation (Lesson Agent — async, low priority)
  → For each concept, pre-generate 3 questions at Bloom levels 1, 2, 3
  → Store in Questions table with hint_1, hint_2, hint_3
  → Run in background; fallback to live generation if not yet available
```

### Ingestion Agent System Prompt (Concept Extraction Pass)

```
System: You are an academic knowledge extraction agent. You receive a chapter from 
a textbook and must identify the key concepts a student must learn from it.

For each concept, output a JSON array with objects containing:
- name: human-readable concept name (e.g. "Osmosis", "The Treaty of Versailles")
- slug_id: lowercase, underscore-separated identifier (e.g. "membrane_transport_osmosis")
- description: one-sentence summary of what the concept covers
- bloom_target: the highest Bloom level this concept typically reaches (1-6)
- difficulty: estimated difficulty 1-5 relative to the book's level
- chapter: chapter number (from the metadata provided)
- page_range: "start_page-end_page" string

Rules:
- Maximum 15 concepts per chapter
- Concepts must be learnable in isolation — not chapter summaries
- Do not include concepts that are merely mentioned in passing
- Output only a JSON array. No preamble, no backticks.
```

### Ingestion Agent System Prompt (Edge Inference Pass)

```
System: You are a curriculum design agent. You receive a complete list of concepts 
from a textbook. Your task is to identify which concepts are prerequisites for others.

For each prerequisite relationship, output a JSON array with objects containing:
- from_concept_id: slug_id of the prerequisite concept
- to_concept_id: slug_id of the dependent concept
- strength: float 0.0-1.0 (how strongly the prerequisite must be mastered)
- rationale: one sentence explaining why A must be understood before B

Rules:
- Only infer edges that represent genuine conceptual dependencies
- Do not infer edges for mere thematic proximity (both about cells ≠ prerequisite)
- Strength > 0.8: student will likely fail the dependent concept without the prerequisite
- Strength 0.5-0.8: understanding is aided but not blocked without the prerequisite
- Do not create circular dependencies
- Output only a JSON array. No preamble, no backticks.
```

### Ingestion Validation Logic

```python
def validate_ingestion_output(concepts: list, edges: list, book_id: str) -> IngestionResult:
    concept_ids = {c['slug_id'] for c in concepts}
    
    # Validate concepts
    assert len(concepts) <= 200, "Too many concepts — likely extraction error"
    for c in concepts:
        assert re.match(r'^[a-z0-9_]+$', c['slug_id']), f"Invalid slug: {c['slug_id']}"
        assert 1 <= c['difficulty'] <= 5
        assert 1 <= c['bloom_target'] <= 6
    
    # Validate edges
    valid_edges = []
    for e in edges:
        if e['from_concept_id'] not in concept_ids:
            continue  # silently drop edges to unknown concepts
        if e['to_concept_id'] not in concept_ids:
            continue
        if e['from_concept_id'] == e['to_concept_id']:
            continue  # reject self-loops
        valid_edges.append(e)
    
    # Cycle detection (DFS)
    graph = defaultdict(list)
    for e in valid_edges:
        graph[e['from_concept_id']].append(e['to_concept_id'])
    assert not has_cycle(graph), "Cycle detected in prerequisite graph"
    
    return IngestionResult(concepts=concepts, edges=valid_edges)
```

### Ingestion Status & Error Handling

- Long books (> 400 pages) are processed chapter by chapter with a progress event stream to the frontend
- If concept extraction fails for a chapter, that chapter is flagged and retried once; on second failure, the chapter is skipped and logged
- If cycle detection fails after edge inference, the Ingestion Agent is re-prompted with the detected cycle and asked to remove the offending edge
- Book node `ingestion_status` is set to `"failed"` only if > 20% of chapters fail extraction; otherwise partial graphs are valid and flagged with a warning

---

## PHASE 8 — MEMORY SYSTEM DESIGN

### Complete Memory Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MEMORY ARCHITECTURE                         │
├────────────────┬────────────────┬───────────────┬───────────────┤
│   SHORT-TERM   │  SESSION MEM   │  LONG-TERM    │  GRAPH MEM    │
│   (Redis)      │  (Redis)       │  (PostgreSQL) │  (Neo4j)      │
├────────────────┼────────────────┼───────────────┼───────────────┤
│ Active concept │ Last 10 turns  │ Mastery scores│ Concept nodes │
│ Current hints  │ Current quiz   │ Error taxonomy│ Mastery edges │
│ Hint counter   │ state          │ Session summ- │ Prereq edges  │
│ Session start  │ Bloom level    │ aries         │ Error edges   │
│ timestamp      │ achieved this  │ Spaced queue  │ Book nodes    │
│ Active book_id │ session        │ Bloom progress│               │
│                │                │ Book registry │               │
│ TTL: 2 hours   │ TTL: 2 hours   │ Persistent    │ Persistent    │
└────────────────┴────────────────┴───────────────┴───────────────┘
                                          │
                                ┌─────────┴─────────┐
                                │  SEMANTIC MEMORY   │
                                │   (ChromaDB)       │
                                ├───────────────────┤
                                │ Book text chunks  │
                                │  (per book_id     │
                                │   collection)     │
                                │ Session summary   │
                                │ embeddings        │
                                │ (for RAG)         │
                                └───────────────────┘
```

### Short-Term Memory (Redis, TTL=2h)

**What is stored:** Current active concept ID, current active book_id, hint release state (0/1/2/3), session start timestamp, current question ID.

**What is retrieved:** Before every Tutor Agent call to check hint state and enforce progressive hint release.

**How it changes tutor behavior:** Prevents hint skipping. Enforces "you must see hint 1 before hint 2."

### Session Memory (Redis, TTL=2h)

**What is stored:** Last 10 conversation turns (role + content JSON array), current Bloom level achieved this session per concept, concepts covered this session, active book_id.

**What is retrieved:** Injected as conversation history into every Tutor Agent call.

**How it changes tutor behavior:** Tutor doesn't repeat questions already asked. Maintains conversational coherence. References what was said 3 turns ago.

### Long-Term Memory (PostgreSQL)

**What is stored:** All mastery scores, error taxonomy, session summaries, spaced review schedules, Bloom progress — all scoped per student per book.

**What is retrieved:** At session start: top-3 error types per concept from error_log, last session summary, spaced review due concepts, current mastery vector. Injected into Tutor Agent and Lesson Agent system prompts.

**How it changes tutor behavior:** Tutor opens session with: *"Last session you struggled with [struggles from session_summaries]. Let's start with a quick review."*

**How it changes curriculum generation:** Curriculum Agent receives mastery vector and re-queries Neo4j for unlockable concepts for the active book.

**How it changes lesson delivery:** Lesson Agent receives preferred_domain and generates examples in that domain (gaming, sports, etc.), grounded in the book's content via RAG.

### Error Memory

**What is stored:** error_type (LLM-classified string), concept_id, book_id, count, last_occurrence per student.

**What is retrieved:** Top-3 errors per concept injected into Tutor Agent system prompt as: *"This student historically commits these errors on [concept]: [error_1], [error_2]. Watch for these patterns and ask questions that target them specifically."*

**How it changes future lessons:** Lesson Agent receives error context and generates examples that specifically address the misconception. If error_type = "confuses_osmosis_with_diffusion", the lesson includes a side-by-side comparison example from the book's chapter.

### Memory Update Trigger Flow

```
Student submits quiz answer
        ↓
Progress Agent receives (student_id, book_id, concept_id, question_id, is_correct, student_answer)
        ↓
├── BKT update → write new mastery score to PostgreSQL + Neo4j mastery edge
├── SM2 update → write new due_date to spaced_review_queue
├── Bloom update → if is_correct and question.bloom_level > current, update bloom_progress
├── Error classification → if not is_correct, call Gemini 2.5 Flash to classify error_type
│       → write to error_log
└── Session tracker → append concept to current session's topics_covered in Redis
        ↓
On session end (user logs out or 2h Redis TTL):
├── LLM generates session_summary from Redis session state
├── Write session_summary to PostgreSQL (scoped to book_id)
├── Embed session_summary → write embedding to ChromaDB (book_id collection)
└── Clear Redis session keys
```

---

## PHASE 9 — AGENT ARCHITECTURE

### Decision: Workflow Agents (Named Pipeline, Not True MAS)

**Rejected alternatives:**

- **Single LLM:** A monolithic prompt handling ingestion, assessment, curriculum, lessons, and tutoring creates context conflicts. The tutor must be Socratic; the ingestion agent must be structured and extractive; the assessment agent must be neutral. One system prompt cannot serve all without compromise. Rejected.
- **True Multi-Agent System (autonomous):** Agents with independent goals and negotiation protocols are unreliable in 14 days. Coordination failures are not recoverable in a live demo. Rejected.

**Chosen:** Six named agents, each a specialized LLM call or Python process, orchestrated by a FastAPI Python backend. Agents share state through PostgreSQL + Neo4j + Redis. No agent calls another directly.

### System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    FastAPI ORCHESTRATOR                               │
│        (assembles context, routes calls, validates)                   │
└────┬──────────┬──────────┬──────────┬──────────┬──────────┬─────────┘
     ↓          ↓          ↓          ↓          ↓          ↓
┌─────────┐ ┌────────┐ ┌──────────┐ ┌───────┐ ┌────────┐ ┌──────────┐
│INGESTION│ │ASSESS- │ │CURRIC-   │ │LESSON │ │ TUTOR  │ │PROGRESS  │
│  AGENT  │ │MENT    │ │ULUM      │ │ AGENT │ │ AGENT  │ │ AGENT    │
│         │ │ AGENT  │ │ AGENT    │ │       │ │        │ │          │
│Gemini   │ │Gemini  │ │Gemini    │ │Gemini │ │Gemini  │ │(Python   │
│t=0.1    │ │t=0.2   │ │t=0.3     │ │t=0.4  │ │t=0.7   │ │ only)    │
│         │ │        │ │          │ │       │ │        │ │No LLM    │
│PDF text │ │CAT quiz│ │Reads     │ │Deliv- │ │Socrat- │ │          │
│→concept │ │→mastery│ │Neo4j +   │ │ers    │ │ic chat │ │BKT       │
│nodes +  │ │profile │ │mastery   │ │lesson │ │+ error │ │SM2       │
│prereq   │ │        │ │→ordered  │ │+ Bloom│ │memory  │ │Error     │
│edges →  │ │        │ │path      │ │-escal-│ │        │ │classify  │
│Neo4j    │ │        │ │          │ │ated Q │ │        │ │          │
└─────────┘ └────────┘ └──────────┘ └───────┘ └────────┘ └──────────┘
     ↓          ↓          ↓          ↓          ↓          ↓
┌────────────────────────────────────────────────────────────────────┐
│          PostgreSQL + Neo4j + Redis + ChromaDB                     │
└────────────────────────────────────────────────────────────────────┘
```

### Ingestion Agent

**Inputs:** `IngestionRequest(book_id, pdf_path, title, author)`

**Outputs:** `IngestionResult(concepts: list[Concept], edges: list[PrerequisiteEdge], chunk_count: int)`

**Prompting Strategy:** Two-pass approach (see Phase 7A for full prompts). First pass extracts concepts chapter by chapter. Second pass infers prerequisite edges across the full concept list. Temperature 0.1 for deterministic structured output.

**State Dependencies:** Writes to Neo4j (Concept nodes, PREREQUISITE_OF edges, Book node). Writes to ChromaDB (book text chunks with concept tags). Updates Book.ingestion_status in PostgreSQL.

**Failure Modes:** Cycle detected in edge output → re-prompt with cycle identified, ask to remove offending edge. Concept slug collision → append chapter number to disambiguate. > 200 concepts generated → flag as extraction error, re-run with stricter system prompt.

### Assessment Agent

**Inputs:** `AssessmentRequest(student_id, book_id, student_goal)`

**Outputs:** `AssessmentResult(mastery_vector: dict[str, float], estimated_level: str, recommended_start_concept: str)`

**Prompting Strategy:**
```
System: You are an adaptive diagnostic assessor for the book: [book_title].
Your goal is to estimate the student's mastery across key concepts from this book 
using the minimum number of questions. Ask one question at a time. Start at medium 
difficulty. If student answers correctly, increase difficulty. If incorrectly, 
decrease. Tag each question with: concept_id, bloom_level, difficulty (1-5).
Available concept IDs: [neo4j_concept_list_for_book].
After 8 questions, output a JSON mastery vector.
You CANNOT assess concepts not in the provided list.
temperature=0.2
```

**State Dependencies:** Reads Neo4j for book's concept list (whitelist). Writes initial mastery_scores to PostgreSQL after completion. Writes initial HAS_MASTERY edges to Neo4j.

**Failure Modes:** LLM generates question for concept not in the book's Neo4j graph → Orchestrator validates all concept IDs against Neo4j whitelist before accepting output; invalid IDs trigger retry.

### Curriculum Agent

**Inputs:** `CurriculumRequest(student_id, book_id, mastery_vector, neo4j_ready_concepts: list[Concept], session_goal: str)`

**Outputs:** `CurriculumPlan(ordered_concept_ids: list[str], rationale: str, estimated_sessions: int)`

**Prompting Strategy:**
```
System: You are a curriculum planner for the book: [book_title].
You receive a list of concepts the student is ready to learn (prerequisites satisfied, 
mastery < 0.80). You must order them optimally for learning, considering: cognitive 
scaffolding, concept interdependency from the book's structure, and the student's 
learning velocity. You CANNOT introduce any concept not in the provided list. 
Output a JSON ordered list with rationale for each position.
temperature=0.3
```

**State Dependencies:** Requires Neo4j query result (ready_concepts for book_id). Requires mastery_vector from PostgreSQL. Cannot operate without both.

**Failure Modes:** Empty ready_concepts list (student has mastered all concepts in book) → return congratulatory message and schedule full spaced review session.

### Lesson Agent

**Inputs:** `LessonRequest(concept_id, book_id, mastery_score, bloom_level_achieved, error_history, preferred_domain, session_context)`

**Outputs:** `LessonContent(explanation: str, worked_example: str, questions: list[Question])`

**Prompting Strategy:**
```
System: You are a lesson delivery agent teaching from the book: [book_title].
Teach [concept_name] to a student with mastery=[mastery_score] at Bloom level 
[bloom_level_achieved].

Rules:
- Maximum 3 new sub-concepts per explanation
- Concrete example before formal definition
- Generate exactly 3 questions escalating in Bloom level (start at [bloom_level_achieved + 1])
- Generate one example in the domain: [preferred_domain] if possible
- Reference these known errors and address them directly: [error_history]
- End with one open-ended question requiring synthesis

Relevant book content (use this as your primary source):
[rag_context_from_chromadb]
temperature=0.4
```

**State Dependencies:** Reads error_log, bloom_progress, preferred_domain from PostgreSQL. Retrieves RAG context from ChromaDB (book_id collection).

**Failure Modes:** LLM generates question at wrong Bloom level → Orchestrator validates bloom_level field in output; mismatches trigger retry.

### Tutor Agent

**Inputs:** `TutorRequest(student_message, concept_id, book_id, current_question, error_history, session_history_turns, hint_state, session_summary_last)`

**Outputs:** `TutorResponse(message: str, hint_released: int, contains_answer: bool)`

**Prompting Strategy:**
```
System: You are a Socratic tutor helping a student learn from the book: [book_title].
You NEVER provide direct answers. Always respond with a question or a hint.

Student context:
- Current concept: [concept_name] (from [book_title], Chapter [chapter])
- Previous session: [session_summary_last]
- Recurring errors: [error_history top-3]
- Conversation so far: [last 10 turns]

Relevant book content for grounding (do not quote verbatim):
[rag_context_from_chromadb]

NEVER include the answer to this question: [current_question.answer_key]
NEVER say "the answer is" or give the solution directly.
If student is stuck after 3 attempts, ask the most targeted guiding question 
toward their specific error type.
temperature=0.7
```

**Guardrail Function (Python, runs before every response reaches user):**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def guardrail_check(tutor_response: str, answer_key: str, threshold: float = 0.85) -> bool:
    emb_response = model.encode(tutor_response)
    emb_answer = model.encode(answer_key)
    similarity = cosine_similarity([emb_response], [emb_answer])[0][0]
    return similarity > threshold  # True = answer leaked, block response

def get_tutor_response(request: TutorRequest) -> str:
    for attempt in range(3):
        response = call_tutor_agent(request, temperature=0.7 if attempt == 0 else 0.3)
        if not guardrail_check(response.message, request.current_question.answer_key):
            return response.message
        request.system_addendum = "CRITICAL: Your previous response contained the answer. Do NOT include the answer. Ask a guiding question instead."
    return get_fallback_hint(request)  # Return pre-generated hint if all retries fail
```

**State Dependencies:** Redis (last 10 turns, hint_state, book_id). PostgreSQL (error_log, session_summaries). ChromaDB (relevant book chunk retrieval, scoped to book_id).

**Failure Modes:** Guardrail fires 3 times → return pre-generated hint_2 from Question record. Never return blank response.

### Progress Agent (Python Only — No LLM)

**Inputs:** `QuizResult(student_id, book_id, concept_id, question_id, bloom_level, is_correct, student_answer, time_taken_seconds)`

**Outputs:** `ProgressUpdate(new_mastery_score, new_due_date, error_type_if_wrong, bloom_level_updated)`

**Logic:**
```python
def process_quiz_result(result: QuizResult) -> ProgressUpdate:
    # 1. BKT mastery update
    current = get_mastery(result.student_id, result.book_id, result.concept_id)
    new_score = update_mastery_bkt(current.score, result.is_correct,
                                    current.p_guess, current.p_slip, current.p_transit)

    # 2. SM2 spaced repetition update
    quality = 5 if result.is_correct else 0
    new_interval, new_reps, new_ef = sm2_update(
        current.interval_days, current.repetitions, current.ease_factor, quality)

    # 3. Bloom level update
    if result.is_correct and result.bloom_level > get_bloom_level(
            result.student_id, result.book_id, result.concept_id):
        update_bloom_progress(result.student_id, result.book_id, result.concept_id, result.bloom_level)

    # 4. Error classification (only if incorrect)
    error_type = None
    if not result.is_correct:
        error_type = classify_error_gemini(result.student_answer, result.concept_id)
        upsert_error_log(result.student_id, result.book_id, result.concept_id, error_type)

    # 5. Write all updates atomically to PostgreSQL
    write_progress_update(result.student_id, result.book_id, result.concept_id,
                          new_score, new_interval, new_ef, new_reps)

    # 6. Update Neo4j mastery edge
    neo4j_update_mastery_edge(result.student_id, result.concept_id, new_score, result.book_id)

    return ProgressUpdate(new_mastery_score=new_score, new_due_date=...,
                          error_type_if_wrong=error_type)
```

### Sequence Diagram — Full Session Flow

```
Student          Frontend         Orchestrator      Agents           Databases
   |                |                  |               |                  |
   |-- Upload PDF ->|                  |               |                  |
   |                |-- POST /books --->               |                  |
   |                |                  |-- Ingestion Agent                |
   |                |                  |   Extract concepts + edges       |
   |                |                  |   Write Neo4j + ChromaDB         |
   |                |<-- Graph ready --|               |                  |
   |<-Knowledge     |                  |               |                  |
   |  graph appears |                  |               |                  |
   |                |                  |               |                  |
   |-- Login -----> |                  |               |                  |
   |                |-- GET /session ->|               |                  |
   |                |                  |-- Query PostgreSQL mastery       |
   |                |                  |-- Query spaced review queue      |
   |                |                  |-- Fetch last session summary     |
   |                |<- Session ready--|               |                  |
   |                |                  |               |                  |
   |-- Answer Q1 -> |                  |               |                  |
   |                |-- POST /quiz ---->               |                  |
   |                |                  |-- Progress Agent                 |
   |                |                  |   BKT + SM2 + error classify     |
   |                |                  |   Write PostgreSQL + Neo4j       |
   |                |<-- Updated graph-|               |                  |
   |<- Graph update-|                  |               |                  |
   |                |                  |               |                  |
   |-- Chat msg --> |                  |               |                  |
   |                |-- POST /tutor --->               |                  |
   |                |                  |-- Build context (Redis + PG +    |
   |                |                  |   ChromaDB book chunks)          |
   |                |                  |-- Tutor Agent (Gemini 2.5 Flash) |
   |                |                  |-- Guardrail check                |
   |                |<-- Tutor resp ---|               |                  |
   |<- Response --- |                  |               |                  |
```

---

## PHASE 10 — RAG ARCHITECTURE

### Decision: YES, RAG Is Used — Book Corpus Is the Source

**Why RAG is not optional:** The platform's core claim is that it teaches from *the student's actual book*. If the tutor or lesson agent hallucinates content that contradicts the book, the product fails its own premise. RAG grounds every response in the uploaded text. This is not a guardrail against hallucination in general — it is fidelity to the student's source material.

**Where RAG IS used:**
- Tutor Agent: When student asks "can you explain this concept differently?", RAG retrieves the relevant book passage and injects it as context, grounding the response in the actual text
- Lesson Agent: All explanations and worked examples are grounded in the book's actual treatment of the concept
- Session summary retrieval: Past session summaries are embedded and retrieved to give the tutor long-term context

**Where RAG is NOT used:**
- Assessment Agent: Questions must use Neo4j-validated concept IDs; assessment is about the student's knowledge state, not text retrieval
- Curriculum Agent: Path planning uses Neo4j graph structure, not text similarity
- Progress Agent: Pure logic, no text retrieval needed
- Ingestion Agent: Reads raw text directly, not the vector store

### Corpus

One ChromaDB collection per uploaded book, keyed by book_id. Populated at ingestion time:

```
chromadb_collections/
└── book_{book_id}/
    └── chunks (300-token segments, 50-token overlap, tagged with concept_ids)
```

### Chunking

300-token chunks with 50-token overlap. Each chunk tagged with:
- `book_id` (for collection scoping)
- `concept_ids` (list of concept slugs from the Ingestion Agent's extraction)
- `chapter` (source chapter number)
- `page_range` (source page range)

### Embeddings

Model: `models/text-embedding-004` (Google Gemini). The entire book corpus is embedded at ingestion time. Incremental updates are not required — the book does not change after upload.

### Retrieval

Top-3 chunks by cosine similarity to the student query, filtered by `book_id`. ChromaDB local instance handles this without an external service.

### Context Assembly

```python
def build_rag_context(query: str, concept_id: str, book_id: str) -> str:
    # 1. Query ChromaDB for top-3 chunks scoped to this book
    chunks = chroma_client.query(
        query_texts=[query],
        n_results=3,
        where={
            "$and": [
                {"book_id": {"$eq": book_id}},
                {"concept_ids": {"$contains": concept_id}}
            ]
        }
    )

    # 2. Assemble context string
    context = "\n\n".join([
        f"[Book passage — Chapter {chunk['metadata']['chapter']}, "
        f"pp. {chunk['metadata']['page_range']}]\n{chunk['document']}"
        for chunk in chunks['documents'][0]
    ])

    return f"Relevant content from the student's book:\n{context}\n\nUse this content to ground your response. Do not contradict it."
```

---

## PHASE 11 — DATABASE DESIGN

### Complete Database Architecture

**PostgreSQL** — Primary operational database. All transactional data. Student profiles, book registry, mastery, sessions.

**Neo4j Aura Free** — Graph database. Book and Concept nodes, prerequisite edges, per-student mastery edges — all generated by the Ingestion Agent.

**Redis** — Ephemeral session state. Active conversation turns, hint state, active book_id, session tracking. TTL=2h.

**ChromaDB** — Local vector store. Book text chunk embeddings (per book_id collection), session summary embeddings. No external service needed.

### PostgreSQL Full Schema

(See Phase 6 for complete table definitions)

Additional tables:

```sql
CREATE TABLE curriculum_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    concept_ids TEXT[] NOT NULL,
    rationale TEXT,
    status VARCHAR(50) DEFAULT 'active', -- active | completed | replanned
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE active_lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    concept_id VARCHAR(255) NOT NULL,
    content_json JSONB NOT NULL,
    questions_json JSONB NOT NULL,
    current_question_index INT DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

### Neo4j Schema

(See Phase 7 for complete node/edge definitions)

Additional constraints:
```cypher
CREATE CONSTRAINT book_id_unique ON (b:Book) ASSERT b.id IS UNIQUE;
CREATE CONSTRAINT concept_id_unique ON (c:Concept) ASSERT c.id IS UNIQUE;
CREATE CONSTRAINT student_id_unique ON (s:Student) ASSERT s.id IS UNIQUE;
CREATE INDEX concept_book ON :Concept(book_id);
CREATE INDEX concept_difficulty ON :Concept(difficulty);
CREATE INDEX concept_chapter ON :Concept(chapter);
```

### Redis Key Schema

```
session:{student_id}:turns               → JSON array, last 10 turns, TTL=2h
session:{student_id}:hint_state          → INT (0-3), TTL=2h
session:{student_id}:current_q           → question_id, TTL=2h
session:{student_id}:active_book_id      → book_id, TTL=2h
session:{student_id}:bloom_this_session  → JSON dict, TTL=2h
session:{student_id}:concepts_covered    → JSON array, TTL=2h
ingestion:{book_id}:status               → "processing" | "complete" | "failed", TTL=24h
ingestion:{book_id}:progress             → JSON {chapters_done, total_chapters}, TTL=24h
```

### ChromaDB Collections

```
Collection: book_{book_id}
  - id: chunk_id
  - embedding: float[]
  - document: chunk_text
  - metadata: {book_id, concept_ids, chapter, page_range, title}

Collection: session_summaries
  - id: summary_id
  - embedding: float[]
  - document: summary_text
  - metadata: {student_id, book_id, session_date, struggles, breakthroughs}
```

---

## PHASE 12 — SYSTEM ARCHITECTURE

### Full Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                            │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Knowledge   │  │   Lesson     │  │   Tutor      │             │
│  │  Graph View  │  │   View       │  │   Chat View  │             │
│  │  (D3.js)     │  │              │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Dashboard   │  │ Assessment   │  │  Book Upload │             │
│  │  (Recharts)  │  │  View        │  │  View        │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                              │ REST + WebSocket
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI BACKEND (Python)                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                       ORCHESTRATOR                           │  │
│  │  Context Assembly → Agent Routing → Response Validation      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
│  │INGESTION │ │ASSESSMENT│ │CURRICULUM│ │  LESSON  │ │ TUTOR  │  │
│  │  AGENT   │ │  AGENT   │ │  AGENT   │ │  AGENT   │ │ AGENT  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘  │
│                                              ┌──────────────────┐  │
│                                              │  PROGRESS AGENT  │  │
│                                              │  (Python only)   │  │
│                                              └──────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  JWT Authentication │ Pydantic Validation │ Error Handling   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         │              │              │              │
   ┌─────┴────┐   ┌─────┴────┐  ┌────┴─────┐  ┌────┴─────┐
   │PostgreSQL│   │  Neo4j   │  │  Redis   │  │ ChromaDB │
   │(Supabase)│   │  (Aura)  │  │ (local)  │  │ (local)  │
   └──────────┘   └──────────┘  └──────────┘  └──────────┘
                                                     │
                                             ┌───────┴───────┐
                                             │  Gemini API   │
                                             └───────────────┘
```

### Authentication

JWT-based. `POST /auth/register` and `POST /auth/login` return access tokens. All API routes protected with Bearer token middleware. Student can only access their own data (enforced at query level with student_id from JWT claims).

### Request Flow — New Book Upload

```
1. Student logs in → JWT issued
2. POST /books/upload (multipart PDF)
   → Backend saves PDF to disk/S3
   → Creates Book record (status: "processing")
   → Dispatches Ingestion Agent task (async/background)
   → Returns: {book_id, status: "processing"}
3. Frontend polls GET /books/{book_id}/status
   → Server-sent events stream: {stage, concepts_done, total_chapters}
4. Ingestion completes → Book record updated (status: "complete")
5. Frontend receives completion event → renders knowledge graph
6. Student initiates assessment → see New Session flow
```

### Request Flow — New Session

```
1. GET /session/start?book_id={book_id}
   → Orchestrator fetches mastery_vector from PostgreSQL (scoped to book_id)
   → Queries spaced_review_queue for due concepts
   → Fetches last session_summary for this book
   → Returns: {spaced_review_questions, current_curriculum, graph_data}
2. Frontend renders knowledge graph with mastery colors
3. Student completes spaced review questions (3 questions)
   → Each answer → POST /quiz → Progress Agent → database updates → graph re-renders
4. Student starts new lesson
   → POST /lesson/start → Lesson Agent (with RAG from book corpus) → returns lesson content
5. Student chats with tutor
   → POST /tutor/message → Tutor Agent (with Redis context + RAG) → guardrail → response
6. Session end (explicit logout or TTL)
   → POST /session/end → generates summary → stores in PostgreSQL + ChromaDB
```

---

## PHASE 13 — API DESIGN

### Authentication

```
POST /auth/register
  Request: {name, email, password}
  Response: {student_id, access_token, token_type}

POST /auth/login
  Request: {email, password}
  Response: {student_id, access_token, token_type}
```

### Books

```
POST /books/upload
  Auth: Bearer token
  Request: multipart/form-data {file: PDF, title: string, author: string}
  Response: {book_id, status: "processing", estimated_seconds: int}

GET /books
  Auth: Bearer token
  Response: {books: [{book_id, title, author, ingestion_status, total_concepts, created_at}]}

GET /books/{book_id}/status
  Auth: Bearer token
  Response: {book_id, ingestion_status, progress: {chapters_done, total_chapters}, total_concepts, total_edges}

GET /books/{book_id}/graph
  Auth: Bearer token
  Response: {nodes: [ConceptNode], edges: [PrerequisiteEdge]}
  Note: nodes include mastery_score and bloom_level per student
```

### Assessment

```
POST /assessment/start
  Auth: Bearer token
  Request: {book_id: string, student_goal: string}
  Response: {assessment_id, first_question: Question}

POST /assessment/answer
  Auth: Bearer token
  Request: {assessment_id, question_id, answer: string}
  Response: {next_question: Question | null, completed: bool, mastery_vector: dict | null}

GET /assessment/result/{assessment_id}
  Auth: Bearer token
  Response: {mastery_vector, estimated_level, recommended_start_concept}
```

### Curriculum

```
POST /curriculum/generate
  Auth: Bearer token
  Request: {book_id: string, session_goal: string | null}
  Response: {curriculum_plan_id, ordered_concepts: [Concept], rationale: string}

GET /curriculum/current
  Auth: Bearer token
  Query: ?book_id={book_id}
  Response: {curriculum_plan_id, ordered_concepts, completed_concepts, current_index}

POST /curriculum/replan
  Auth: Bearer token
  Request: {book_id: string, reason: "mastery_drop" | "student_request"}
  Response: {new_curriculum_plan}
```

### Lesson

```
POST /lesson/start
  Auth: Bearer token
  Request: {concept_id: string, book_id: string}
  Response: {lesson_id, explanation, worked_example, questions: [Question]}

POST /lesson/quiz
  Auth: Bearer token
  Request: {lesson_id, question_id, answer: string, time_taken_seconds: int}
  Response: {is_correct, feedback_text, mastery_updated_to, bloom_level_achieved,
             error_type_if_wrong, hint_available: bool}

GET /lesson/hint/{question_id}/{hint_number}
  Auth: Bearer token
  Response: {hint_text, hint_number, hints_remaining}
```

### Tutor

```
POST /tutor/message
  Auth: Bearer token
  Request: {message: string, concept_id: string, book_id: string, question_id: string | null}
  Response: {response: string, is_question: bool, hint_released: int | null}

GET /tutor/session/history
  Auth: Bearer token
  Response: {turns: [{role, content, timestamp}], hint_state: int}

DELETE /tutor/session/clear
  Auth: Bearer token
  Response: {cleared: true}
```

### Dashboard

```
GET /dashboard/overview
  Auth: Bearer token
  Query: ?book_id={book_id}
  Response: {mastery_scores, retention_probabilities, spaced_review_due: [Concept],
             error_taxonomy_summary, session_streak, bloom_progress}

GET /dashboard/forgetting-curve/{concept_id}
  Auth: Bearer token
  Query: ?book_id={book_id}
  Response: {concept_id, retention_history: [{date, probability}],
             next_review_date, stability_days}

GET /dashboard/errors
  Auth: Bearer token
  Query: ?book_id={book_id}
  Response: {errors_by_concept: {concept_id: [{error_type, count, last_occurrence}]}}
```

### Session

```
POST /session/start
  Auth: Bearer token
  Request: {book_id: string}
  Response: {session_id, spaced_review_questions, current_curriculum, graph_data,
             tutor_opening_message}

POST /session/end
  Auth: Bearer token
  Response: {session_summary, concepts_covered, mastery_gains}
```

### Validation Strategy

All request/response bodies validated with Pydantic models. Invalid inputs return 422 with field-level error messages. All concept_id values validated against Neo4j whitelist for the given book_id before any agent call.

### Authorization Strategy

JWT claims contain student_id. All database queries filter by student_id from JWT. Students cannot access other students' data or books. No admin role in MVP.

---

## PHASE 14 — FRONTEND DESIGN

### Technology Stack

React + TypeScript + TailwindCSS + D3.js (graph) + Recharts (dashboard charts) + Zustand (state).

### Navigation Hierarchy

```
App
├── /auth
│   ├── /login
│   └── /register
└── /app (protected)
    ├── /books (book library — upload + select)
    ├── /books/:book_id/onboarding (assessment)
    ├── /books/:book_id/graph (knowledge graph — default home per book)
    ├── /books/:book_id/learn (lesson + quiz)
    ├── /books/:book_id/tutor (Socratic chat)
    └── /books/:book_id/dashboard (mastery + retention)
```

### Page 0: Book Upload / Library (`/books`)

Components:
- `BookUploadCard` — drag-and-drop PDF upload zone, file validation, title/author fields
- `IngestionProgress` — real-time progress bar: "Extracting concepts... (Chapter 4 of 12)", concept count ticking up
- `BookLibraryGrid` — cards per uploaded book with cover thumbnail, title, mastery % completed, last studied date
- `BookStatusBadge` — "Processing" / "Ready" / "Error" state indicators

Flow: Upload PDF → watch graph materialize → redirect to `/books/:id/onboarding`

### Page 1: Onboarding / Assessment (`/books/:book_id/onboarding`)

Components:
- `AssessmentHeader` — shows progress (Q3 of 8), book title, chapter context
- `QuestionCard` — displays current question, Bloom level badge
- `AnswerInput` — text field for open answers or MCQ buttons
- `AssessmentComplete` — shows graph preview being generated, then redirects to `/books/:id/graph`

Flow: 8 questions → graph appears → redirect to `/books/:id/graph`

### Page 2: Knowledge Graph (`/books/:book_id/graph`) — PRIMARY PAGE

Components:
- `GraphCanvas` (D3.js, full viewport) — force-directed layout, nodes colored by mastery
  - Grey node = unassessed
  - Red node = mastery < 0.4
  - Yellow node = mastery 0.4–0.8
  - Green node = mastery ≥ 0.8 (unlocked)
  - Pulsing border = newly unlocked (CSS animation)
  - Node label shows concept name + Bloom badge (R/U/A/An)
  - Click on node → opens sidebar
- `ConceptSidebar` — shows concept name, source chapter and page range, description, mastery score, retention %, error taxonomy for that concept, button "Start Lesson" or "Continue"
- `CurriculumPathOverlay` — highlights the current recommended path on the graph in blue
- `SpacedReviewAlert` — top banner: "3 concepts need review today. Start here →"
- `BookInfoBadge` — top corner: book title, total concepts, ingestion date

Key interactions: Graph updates in real time as quiz answers are submitted. Node colors transition with CSS animations. Path recalculates if mastery drops.

### Page 3: Lesson View (`/books/:book_id/learn`)

Components:
- `LessonHeader` — concept name, source chapter, Bloom level target, estimated time
- `BookSourceBadge` — "From [book_title], Chapter [N], pp. [X–Y]" — provenance visible to student
- `ConceptExplanation` — markdown-rendered explanation text (grounded in book RAG)
- `WorkedExample` — highlighted example block relevant to the concept
- `PreLessonPrimer` — "What do you already know about [concept]?" — free text before content shown
- `QuestionCard` — current question with Bloom level badge
- `HintSystem` — "Request Hint 1" button; hint appears below question; counter shows hints used
- `AnswerFeedback` — after submission: correct/incorrect, error type if wrong, mastery delta shown
- `BloomProgressBar` — shows current Bloom level achieved for this concept, next level target

### Page 4: Tutor Chat (`/books/:book_id/tutor`)

Components:
- `TutorChatWindow` — message thread, auto-scroll, user messages right, tutor messages left
- `TutorContextBar` — top banner: "Book: [title] | Topic: [concept] | Your common error: [top error type]"
- `SessionOpenerCard` — first message always: "Last session you struggled with [struggle] in Chapter [N]. Here's where we pick up."
- `MessageInput` — text field + send button + keyboard shortcut
- `HintCounter` — shows hints available for current question
- `SocraticMeter` — small indicator: "% of tutor responses are questions: 78%"

### Page 5: Dashboard (`/books/:book_id/dashboard`)

Components:
- `MasteryOverview` — horizontal bar chart (Recharts) per concept, sorted by score ascending
- `ForgettingCurveChart` — line chart per selected concept: retention % vs days, next review date marked
- `ErrorTaxonomyPanel` — accordion by concept, each expanded shows error types with counts
- `SpacedReviewQueue` — list of concepts due for review with due date and estimated review time
- `BloomProgressHeatmap` — grid: concepts × Bloom levels, filled if achieved
- `SessionHistory` — timeline of past sessions with summary text and mastery delta
- `LearningVelocityCard` — "You master 1.4 concepts per session on average"
- `BookProgressSummary` — "You have mastered 23 of 84 concepts in [book_title]"

---

## PHASE 15 — 14-DAY IMPLEMENTATION ROADMAP

### Team Assignments

- **Student 1 (Backend Lead):** FastAPI orchestrator, PostgreSQL schema, agent routing, authentication, book upload handling
- **Student 2 (AI Lead):** Ingestion Agent system prompts, all other agent prompts, guardrail function, error classification
- **Student 3 (Graph/DB Lead):** Neo4j schema + ingestion write logic, Cypher queries, Progress Agent logic, ChromaDB setup
- **Student 4 (Frontend Lead):** React app, D3.js knowledge graph, book upload UI, routing, component architecture
- **Student 5 (Integration/QA Lead):** Full-loop integration, ingestion pipeline testing, demo script, viva prep

### Day-by-Day Plan

**Days 1–2: Foundation**

| Student | Tasks |
|---|---|
| S1 | FastAPI project setup. PostgreSQL schema (all tables, including books). Alembic migrations. JWT auth endpoints. File upload endpoint skeleton. |
| S2 | Write all 6 agent system prompts (Ingestion × 2, Assessment, Curriculum, Lesson, Tutor). Manual test Ingestion Agent with a sample PDF chapter. Define Pydantic models. |
| S3 | Design Neo4j schema (Book, Concept, edge types). Write ingestion-to-graph write function. Verify prerequisite traversal Cypher query works on a small sample graph. ChromaDB setup + ingestion chunk write logic. |
| S4 | React project setup (CRA + TypeScript + Tailwind). Routing setup. Auth pages. Book upload page with drag-and-drop. |
| S5 | Select 2 sample books for demo (one biology textbook, one economics textbook). Run Ingestion Agent end-to-end on Chapter 1 of each. Validate extracted concept quality and edge accuracy. |

**Days 3–4: Ingestion Pipeline + Core Agents**

| Student | Tasks |
|---|---|
| S1 | Full async ingestion pipeline endpoint. SSE progress stream. Assessment endpoint. Curriculum endpoint. |
| S2 | Complete Ingestion Agent: concept extraction + edge inference + validation logic. Assessment Agent (CAT logic). Curriculum Agent (Neo4j query + LLM ranking). |
| S3 | Progress Agent: BKT update. SM2 update. Write PostgreSQL + Neo4j after each quiz answer. Neo4j ingestion write (Concept nodes, PREREQUISITE_OF edges, Book node status update). |
| S4 | Ingestion progress UI (real-time SSE bar, concept count ticker). Assessment UI. QuestionCard component. |
| S5 | Run full ingestion on complete demo book. Validate concept count, edge validity, cycle detection. Document any extraction quality issues. |

**Days 5–6: Lesson + Graph**

| Student | Tasks |
|---|---|
| S1 | Lesson endpoints (start, quiz, hint). Tutor endpoints (message). Session endpoints (start, end). |
| S2 | Lesson Agent with Bloom-escalating question generation. RAG context assembly for Lesson Agent. Error classification with Gemini 2.5 Flash. |
| S3 | Neo4j mastery edge update on quiz answer. Verify unlock logic. Book-scoped ChromaDB retrieval. |
| S4 | D3.js knowledge graph (force-directed layout). Node color by mastery. Book chapter metadata on node click. CurriculumPathOverlay. |
| S5 | Full ingestion → assessment → curriculum → lesson loop integration test. Document all bugs. |

**Days 7–8: Tutor + Memory**

| Student | Tasks |
|---|---|
| S1 | Full session orchestration. Context assembly function (Redis + PostgreSQL + ChromaDB → agent context object, scoped to book_id). |
| S2 | Tutor Agent: Socratic system prompt. Guardrail function. Progressive hint release logic. Redis session management (book_id-scoped). |
| S3 | Session end handler: LLM session summary generation. Write to PostgreSQL. Embed to ChromaDB (book_id collection). Neo4j mastery edge batch update. |
| S4 | Tutor chat UI. TutorContextBar with book title. SessionOpenerCard. HintCounter. Real-time graph node color updates. |
| S5 | Integration test: full session loop. Test cross-session memory (end session, new session, verify tutor opening references previous struggles on the book's concepts). |

**Days 9–10: Dashboard + Polish**

| Student | Tasks |
|---|---|
| S1 | Dashboard API endpoints (all scoped by book_id). Performance tuning. |
| S2 | Adversarial Tutor Agent testing (20× "just tell me the answer"). Tune guardrail threshold. Measure question ratio metric. |
| S3 | Verify spaced review queue populates correctly after 2 sessions. Test SM2 scheduling accuracy. |
| S4 | Dashboard page: MasteryOverview, ForgettingCurveChart, ErrorTaxonomyPanel, SpacedReviewQueue, BookProgressSummary. |
| S5 | End-to-end integration test. Complete one 30-minute student session on the demo book. Priority bug list. |

**Day 11: Real User Test**

All students: Get one actual student to upload a book and use the system for 30 minutes. Observe silently. Record reaction to the ingestion graph appearing, tutor behavior, dashboard. Fix the top 3 critical issues found.

**Day 12: Demo Hardening**

| Student | Tasks |
|---|---|
| S1 | Performance: ensure graph loads in < 2 seconds. Ensure ingestion completes in < 60 seconds for a 200-page PDF. |
| S2 | Adversarial input testing. Record guardrail trigger rate. Prepare "question ratio" number for viva. |
| S3 | Seed a demo student account with 2 prior sessions on the demo book (realistic mastery state, 5 error log entries). Verify tutor opening message references correct past struggles. |
| S4 | Graph animation: pulsing glow when node unlocks. Ingestion animation (nodes appearing one by one during pipeline). Mobile responsiveness. |
| S5 | Write demo script (8-minute flow). Record backup demo video. Test full script 3 times. |

**Day 13: Presentation**

All students: Final PPT. Viva Q&A rehearsal (all 50 questions from Phase 16). Assign questions by expertise. Record 5-minute backup demo. Polish UI copy.

**Day 14: Buffer**

Fix any remaining P0 bugs. Final run-through of demo script. Ensure all 5 students can answer the 10 most likely viva questions. Sleep.

### Critical Dependencies

```
Ingestion Agent working (D2) → Neo4j seeded with demo book (D3) → Assessment Agent (D4) → Lesson routing (D6) → Full loop test (D8)
PostgreSQL schema (D1) → Progress Agent (D4) → Dashboard data (D10)
ChromaDB ingestion write (D3) → RAG retrieval (D5) → Tutor Agent grounding (D7)
D3.js graph (D6) → Real-time updates (D8) → Demo centerpiece (D12)
Full loop (D8) → Real user test (D11) → Demo hardening (D12)
```

### Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Ingestion Agent produces noisy or incorrect edges | Medium | High | Validate on 3 different books in Days 3–5. Implement cycle detection and concept count caps. Manual correction UI is Tier 3. |
| Neo4j Aura connectivity in demo environment | Medium | High | Test on demo WiFi 48h before. Have local Neo4j desktop backup. |
| Guardrail false positives block tutor | Low | High | Set threshold at 0.85. Monitor in testing. Lower to 0.80 if too many false positives. |
| Gemini API rate limits during ingestion of long books | Medium | Medium | Chunk ingestion calls with 1-second delay between chapters. Cache extraction results after first run. |
| D3.js graph performance with large book graphs (100+ nodes) | Medium | Medium | Pre-compute layout. Cache graph JSON. Use virtualization for graphs > 80 nodes. |
| LLM generates concept ID not in Neo4j during Assessment | Medium | Medium | Orchestrator validates all concept IDs against Neo4j whitelist for the given book_id before any downstream use. |
| Student data inconsistency between PostgreSQL and Neo4j | Medium | Medium | All mastery writes are dual-writes in the same Progress Agent call. Transaction-safe with rollback on Neo4j failure. |

---

## PHASE 16 — VIVA OPTIMIZATION

### 50 Probable Viva Questions with Ideal Answers

#### Category: Product

**Q1. What problem does this solve that existing platforms don't?**
Three distinct problems simultaneously: existing platforms don't know *why* you failed (only that you did), they forget you between sessions, and they impose their own curriculum regardless of which textbook your course actually uses. Our platform reads the student's actual book, builds the knowledge graph from it, and maintains a cross-session error taxonomy per student per concept. No platform does all three.

**Q2. How is this different from ChatGPT?**
ChatGPT has no learner model, no prerequisite graph, no Bloom-level enforcement, no spaced repetition, no cross-session error memory, and no grounding in the student's actual book. It gives direct answers; our tutor architecturally cannot. The visible knowledge graph generated from the student's uploaded PDF is something no LLM chatbot offers. We implement five specific learning science mechanisms and one novel ingestion pipeline. ChatGPT implements zero.

**Q3. Why would a student use this over just asking ChatGPT about their book?**
ChatGPT will summarize the book. It won't build a prerequisite map of it, track which concepts the student has mastered, schedule what they need to review before they forget it, remember what they got wrong last Tuesday, or refuse to give them the answer when they ask a practice question. The cross-session cognitive model is the product. ChatGPT has no such model.

**Q4. What is your one-sentence product description?**
An adaptive learning platform that reads your textbook, extracts a personalized knowledge graph from it, and teaches to the gaps in your understanding using Socratic dialogue that remembers your specific misconceptions across every session.

**Q5. How does the system know what to teach next?**
The Curriculum Agent queries Neo4j for concepts where all prerequisites are mastered at ≥ 0.80 and current mastery is below threshold. The prerequisite edges come from the Ingestion Agent's analysis of the book — not from manual curation. The Curriculum Agent then ranks by difficulty (ascending) and concept centrality (concepts that unlock more downstream nodes are prioritized). The result is a path unique to this student's knowledge state, derived from their actual book.

#### Category: Learning Science

**Q6. What is Bayesian Knowledge Tracing?**
BKT models each skill as a binary latent variable: mastered or not. It has four parameters: p_init (prior probability of mastery), p_transit (probability of learning after each attempt), p_guess (probability of correct answer despite not mastered), p_slip (probability of wrong answer despite mastered). We update mastery after each response using Bayesian inference on these priors.

**Q7. Why not Deep Knowledge Tracing?**
DKT uses an LSTM to model cross-skill transfer and can outperform BKT with sufficient data. However, it requires thousands of training interactions and an ML training pipeline. We have neither in 14 days. BKT is interpretable, proven at scale, and computationally trivial. We mention DKT as the natural next step when interaction data accumulates.

**Q8. What is the forgetting curve and how is it implemented?**
Ebbinghaus (1885) showed retention decays as R = e^(-t/S), where t is days since last review and S is memory stability. We store stability_days per concept per student. Stability increases after each successful retrieval (SM2 ease_factor multiplication). The Progress Agent recalculates R at session start. Concepts below R=0.70 are queued for spaced review.

**Q9. What is the SM2 algorithm?**
SM2 (SuperMemo 2) schedules reviews at intervals that grow with each successful retrieval: first review at 1 day, then 6 days, then interval × ease_factor, where ease_factor starts at 2.5 and adjusts based on answer quality. After a failure, interval resets to 1 day. We implement this in the Progress Agent and store due_date, interval_days, ease_factor, and repetitions per concept per student.

**Q10. What is Bloom's Taxonomy and how do you enforce it?**
Six cognitive levels: Remember, Understand, Apply, Analyze, Evaluate, Create. Every question is tagged. The Lesson Agent enforces that a student must demonstrate proficiency at level N before receiving level N+1 questions on the same concept. This prevents the common failure mode of students who can define osmosis but cannot apply it to a novel scenario.

**Q11. What is the Zone of Proximal Development?**
Vygotsky's ZPD is the range of tasks a learner can accomplish with guidance but not independently. We operationalize this by calibrating question difficulty so estimated success probability is 0.65–0.80 — challenging enough to produce learning, not so hard as to produce frustration. We use mastery score and historical slip rate to estimate this.

**Q12. What is the testing effect and how do you use it?**
Roediger & Karpicke (2006) demonstrated that retrieval practice produces stronger long-term retention than re-studying the same material. Every session begins with retrieval practice on spaced-due concepts before any new content is presented. This is architecturally enforced — not optional.

**Q13. What is Cognitive Load Theory?**
Sweller (1988) argued that working memory is limited and instruction must minimize extraneous cognitive load while chunking intrinsic load appropriately. Our Lesson Agent enforces a maximum of 3 new concepts per lesson and uses concrete examples before formal definitions to reduce intrinsic load.

**Q14. Why do you tag errors by type and not just count them?**
Knowing a student failed 5 times tells us to repeat the topic. Knowing they specifically confused osmosis directionality with diffusion tells the tutor to ask "which direction does water move when solute concentration is higher outside the cell?" — a targeted question that addresses the actual misconception. Error type changes the tutoring strategy; error count alone does not.

**Q15. What is mastery learning gating?**
Bloom's mastery learning approach: students must demonstrate mastery (≥ 80%) on a concept before unlocking the next. This prevents knowledge gaps from compounding. In our system, the Curriculum Agent checks Neo4j mastery edges before recommending any concept. A concept with unmastered prerequisites is not offered.

#### Category: Ingestion Pipeline

**Q16. How does the system extract concepts from a PDF?**
Two-pass LLM process. First pass: the Ingestion Agent receives each chapter's text and is prompted to identify key concepts as a structured JSON array — name, slug_id, description, bloom_target, difficulty, chapter, page_range. Second pass: given the full concept list, the agent infers prerequisite relationships with strength scores and rationale. Both outputs are validated before writing to Neo4j.

**Q17. How do you ensure the extracted prerequisite edges are accurate?**
Three layers of validation: structural (cycle detection, self-loop rejection, concept ID existence check), semantic (strength scores must be 0–1, rationale must be present), and quantitative (more than 200 concepts or 0 edges flags an extraction error). For the demo, we also hand-review the graph for the demo book before the presentation.

**Q18. What happens if the LLM hallucinates a concept that isn't in the book?**
The validation layer checks every concept_id against the extracted concept list before writing edges. A concept_id in an edge that doesn't correspond to an extracted concept node is silently dropped. The Book node's edge count reflects only validated edges written to Neo4j.

**Q19. How long does ingestion take and how is it shown to the user?**
Under 60 seconds for a typical 200–300 page textbook. The frontend subscribes to a server-sent events stream from `/books/{book_id}/status`. The UI shows: "Extracting concepts — Chapter 4 of 12 complete — 47 concepts found so far." The knowledge graph nodes appear incrementally as chapters complete.

**Q20. What prevents a student from uploading copyrighted textbooks?**
The system does not screen for copyright compliance — it is the student's responsibility to only upload material they are authorized to use, consistent with their institution's fair-use policies. In a production deployment, an institutional licence or publisher partnership would resolve this. For this academic capstone, the uploaded book is used solely for personal learning, mirroring how a student would use their own copy.

#### Category: AI & LLM

**Q21. What temperature did you set for each agent and why?**
Ingestion Agent: 0.1 (deterministic structured extraction — randomness produces inconsistent JSON). Assessment Agent: 0.2 (deterministic for fair assessment). Curriculum Agent: 0.3 (consistent path with slight variation in rationale). Lesson Agent: 0.4 (consistent explanations, some variety in examples). Tutor Agent: 0.7 (natural conversational variation for Socratic dialogue). Error Classifier: 0.1 (deterministic classification).

**Q22. How do you prevent hallucinations in lesson content?**
The Lesson Agent receives the top-3 relevant book chunks from ChromaDB as context before generating any explanation. The system prompt instructs it to ground all claims in the provided book content and not contradict it. For the tutor, the same RAG context is injected. This is fidelity to the source material, not just hallucination prevention in general.

**Q23. What is your prompt architecture for the Tutor Agent?**
Four layers in the system prompt: (1) Role definition with absolute prohibition on direct answers. (2) Student context injection: concept, source chapter, mastery score, top-3 error types from error_log, last session summary. (3) RAG context: top-3 relevant book passages. (4) Response format constraint: always a question or hint, never a solution, never contradict the book.

**Q24. What is RAG and where do you use it?**
Retrieval-Augmented Generation: retrieve relevant documents and inject them as context before LLM generation. We chunk the uploaded book into 300-token segments, embed with Google's `models/text-embedding-004` model, and store in ChromaDB per book. The Tutor Agent and Lesson Agent retrieve the top-3 relevant chunks for each concept and inject them as grounding context — ensuring responses align with the student's actual reading material.

**Q25. Why Gemini 2.5 Flash over other models?**
Gemini 2.5 Flash delivers the ideal speed-to-capability ratio for real-time educational generation and batch ingestion. Its 1M-token context window handles full session history plus RAG context plus large book chapter text without truncation. Native JSON output mode enforces structured agent responses without function-calling overhead. Cost is near-zero — the entire demo and ingestion pipeline run within Gemini's free tier. Gemini was the team's frozen AI provider from project inception.

#### Category: Agents

**Q26. Is this a true multi-agent system?**
It is a workflow with named, specialized agents — closer to a directed pipeline of LLM calls than an autonomous MAS. True MAS involves agents with independent goals and negotiation. Our agents are stateless functions with shared state in databases. This is the appropriate choice for reliability at our scale.

**Q27. Why not LangChain?**
LangChain adds abstraction overhead that makes debugging harder. In a 14-day build, understanding every prompt injection point is essential for both reliability and viva confidence. Our orchestrator is ~200 lines of Python and fully transparent. For a demo where we must answer any question about any component, explicit is better than abstracted.

**Q28. How do agents share state?**
All agents receive typed Pydantic context objects assembled by the Orchestrator. They read from and write to the shared PostgreSQL + Neo4j stores. No agent calls another directly. All inter-agent communication is through shared state. This prevents circular dependencies and makes each agent independently testable.

**Q29. What is the Progress Agent?**
The only agent that is pure Python with no LLM. It runs BKT updates, SM2 scheduling, Bloom level updates, and triggers the error classification sub-call (Gemini 2.5 Flash). It writes to PostgreSQL and Neo4j atomically. It is the most performance-critical component because it runs after every quiz answer.

**Q30. What happens if the Ingestion Agent produces a poor quality graph?**
The validation pipeline catches structural errors (cycles, orphan edges, bad slugs). Semantic quality — whether the concepts are correctly identified — depends on the LLM's reading of the text. In testing we found Gemini 2.5 Flash produces high-quality extractions from well-structured academic textbooks. For poorly formatted PDFs (scanned images, non-semantic structure), we flag the book as "low confidence" and surface a warning in the UI.

#### Category: Neo4j

**Q31. Why Neo4j over a PostgreSQL adjacency list?**
Prerequisite traversal with mastery conditions is a natural graph pattern: "find concepts where all prerequisites are mastered and the concept itself is not yet mastered." In Cypher, this is 5 lines. In recursive SQL CTEs with mastery joins, it is 30+ lines and harder to reason about. Additionally, D3.js reads directly from Neo4j's REST API for the knowledge graph visualization. And the instructor recently taught graph databases — using Neo4j is the bonus mark strategy, not a choice between two equivalent tools.

**Q32. How is the graph populated — is it manual?**
No. The graph is entirely generated by the Ingestion Agent. A developer never types a concept node or an edge. This is architecturally central to the platform's value proposition: the same codebase handles any textbook without modification.

**Q33. Write the Cypher query for finding a student's next concepts.**
```cypher
MATCH (s:Student {id: $student_id})-[m:HAS_MASTERY]->(mastered:Concept)
WHERE m.score >= 0.80 AND m.book_id = $book_id
WITH collect(mastered.id) AS mastered_ids, s
MATCH (next:Concept {book_id: $book_id})
WHERE ALL(prereq IN [(next)<-[:PREREQUISITE_OF]-(p:Concept) | p.id]
      WHERE prereq IN mastered_ids)
AND NOT EXISTS {
    MATCH (s)-[hm:HAS_MASTERY]->(next)
    WHERE hm.score >= 0.80 AND hm.book_id = $book_id
}
RETURN next ORDER BY next.difficulty ASC LIMIT 5
```

**Q34. What breaks if you remove Neo4j?**
The Curriculum Agent degrades to a static list with no prerequisite awareness. Dynamic unlock logic becomes brittle Python that cannot adapt when a new book is uploaded. The real-time knowledge graph loses its live query backend. Most critically: the Ingestion Agent has nowhere to write the extracted graph — the entire domain-agnostic value proposition collapses.

**Q35. What Neo4j traversal algorithm does the Curriculum Agent use?**
Modified topological sort with mastery weighting. We find all unmastered concepts where prerequisites are satisfied (mastery ≥ 0.80 for the active book), then rank by: (1) estimated learning time (ascending), (2) dependency centrality (concepts unlocking more downstream nodes get priority), (3) recency of related errors (concepts with recent errors get priority for targeted remediation).

#### Category: Memory

**Q36. What is the difference between short-term and long-term memory in your system?**
Short-term: Redis stores active session turns, hint state, and active book_id (ephemeral, 2h TTL, fast). Long-term: PostgreSQL stores mastery scores, error taxonomy, session summaries, and spaced review schedules (persistent, queryable, transactional, scoped per student per book). This mirrors human cognitive architecture: working memory (Redis) versus long-term memory (PostgreSQL).

**Q37. How does session memory change tutor behavior?**
The last 10 conversation turns from Redis are injected into every Tutor Agent call as conversation history. The top-3 error types from the error_log are injected into the system prompt. The last session summary from PostgreSQL is injected as the tutor opening context. The tutor cannot avoid acknowledging what happened before — it is in its system prompt.

**Q38. What is stored in ChromaDB?**
Two collection types: `book_{book_id}` collections containing 300-token chunks of the uploaded book with concept_id and chapter metadata; and a `session_summaries` collection containing embeddings of LLM-generated session summaries with student_id and book_id metadata. Both are queried by the Tutor Agent for contextual grounding.

**Q39. How do you prevent session memory from growing unboundedly?**
Redis TTL of 2 hours ensures session state is ephemeral. Only the last 10 turns are stored (sliding window). Full conversation transcripts are never persisted. At session end, a single-paragraph LLM-generated summary replaces the entire session in long-term storage. ChromaDB stores one embedding per session summary, not per turn.

**Q40. Is learner data scoped per book?**
Yes. Every record in mastery_scores, bloom_progress, error_log, session_summaries, and spaced_review_queue includes a book_id foreign key. A student who uploads two books has two entirely separate cognitive models. Neo4j mastery edges also carry a book_id property. This prevents cross-contamination between different subjects.

#### Category: Architecture

**Q41. Walk me through the request lifecycle for a Tutor Agent message.**
(1) POST /tutor/message with message, concept_id, book_id, question_id. (2) Orchestrator validates JWT, extracts student_id. (3) Fetch Redis: last 10 turns + hint_state + active book_id. (4) Fetch PostgreSQL: top-3 error types for concept + book, last session summary. (5) Fetch ChromaDB: top-3 relevant book chunks for concept_id + book_id. (6) Assemble TutorRequest Pydantic model. (7) Call Gemini 2.5 Flash. (8) Guardrail function checks response against answer_key. (9) If guardrail passes, return response. (10) Append turn to Redis session history. (11) Return to frontend.

**Q42. What is your API cost estimate per student session?**
Approximately $0.002–0.008 per 30-minute session with Gemini 2.5 Flash. Ingestion (one-time per book): approximately $0.05–0.15 for a 300-page textbook depending on density. Session costs: Assessment Agent (~500 tokens), Curriculum Agent (~800), Lesson Agent (~1,200 × 3 lessons), Tutor Agent (~400 × 8 turns), Error Classifier (~100 × 5 wrong answers). Total session: ~8,000 tokens input + ~3,000 output. At Gemini 2.5 Flash pricing the demo operates within the free tier.

**Q43. How would this scale to 10,000 students?**
Agent calls are stateless; horizontal scaling via container orchestration. PostgreSQL with read replicas for learner model queries. Neo4j Aura handles graph at scale. Redis Cluster for session state. ChromaDB would migrate to a managed vector service (Pinecone, Weaviate) at scale. Main bottleneck at scale is ingestion throughput — solved by a dedicated async ingestion worker pool with Celery + Redis.

**Q44. What are the privacy considerations?**
We store performance data (mastery, errors) but not raw conversation transcripts or the full book text (only embeddings and chunks). Gemini API is invoked under Google's standard usage policies. Student data is never shared across students. JWT ensures isolation. The uploaded PDF is stored server-side; in production this requires clear data retention and deletion policies.

**Q45. What is your cold start strategy?**
New student with a new book: Ingestion Pipeline runs first (< 60 seconds), producing the concept graph. Then the Adaptive Diagnostic runs — 8 questions using CAT-style difficulty branching against the book's extracted concepts. After 8 questions, a reliable initial mastery estimate seeds the learner model. Curriculum Agent can immediately generate a path. Zero manual configuration required.

#### Category: Architecture Board Challenges (Trap Questions)

**Q46. What if the Ingestion Agent extracts the wrong prerequisite direction — saying B requires A when in fact A requires B?**
Directional errors in prerequisite edges are the most likely quality failure mode. Three mitigations: (1) The edge inference prompt asks for explicit rationale per edge, which surfaces directional reasoning that can be reviewed. (2) Chapter order is a strong signal — concepts from earlier chapters are more likely to be prerequisites. The Ingestion Agent is primed with this heuristic. (3) The validation pipeline detects cycles, which catches the worst cases where A→B and B→A are both inferred. For the demo, we review the graph for the demo book before the presentation and correct any directional errors directly in Neo4j.

**Q47. Your BKT parameters are fixed defaults. How is that adaptive?**
Fixed defaults give the same update trajectory to all students on the same concept, which is a limitation. In production, these parameters would be estimated from historical student data using maximum likelihood estimation per concept. For our demo scale, default parameters from the literature (p_guess=0.25, p_slip=0.10) are well-validated starting points. We acknowledge individualized BKT parameter estimation as a research direction that becomes valuable with sufficient interaction data.

**Q48. What happens if the prerequisite graph traversal returns an empty set?**
Two cases: (1) Student is in a knowledge valley — has partial prerequisites but nothing fully satisfied. Curriculum Agent identifies the concept closest to unlocking (highest percentage of prerequisites mastered) and prioritizes completing that prerequisite. (2) Student has mastered all concepts in the book — display a completion state and run a full spaced review session on all concepts below retention threshold.

**Q49. The guardrail uses embedding similarity. What if a student writes the answer in their question?**
The guardrail checks the tutor's *response* against the answer key, not the student's message. The student can write the answer in their chat message — the guardrail doesn't intercept that. But the system routes based on the API endpoint: `/tutor/message` triggers the Tutor Agent flow; `/lesson/quiz` triggers the Progress Agent. The tutor receiving the student's answer in chat does not record it as a correct quiz response. The guardrail is specifically about preventing the tutor from *providing* the answer in its own words.

**Q50. What would you build differently with 3 more months?**
Three things: (1) A concept correction UI — letting students or instructors flag incorrectly extracted concepts or edges, with corrections written back to Neo4j. This closes the loop on ingestion quality. (2) BKT parameter estimation per student from accumulated interaction data — moving from fixed defaults to individualized parameters. (3) A comparative study: adaptive book-grounded Socratic tutor versus unstructured LLM chat on 30-day retention, to generate publishable evidence. The core architecture supports all three without fundamental redesign.

---

## PHASE 17 — PRESENTATION OPTIMIZATION

### Final PPT Structure (15 Slides)

**Slide 1 — Hook**
Visual: Split screen. Left: ChatGPT Study Mode — student asks about osmosis, gets a long explanation. Right: black background, the words *"ChatGPT doesn't know it was your textbook. And it won't remember this tomorrow."*
Say: "Every AI tutor today resets. Every session, you start from zero. It doesn't know your book. We built the one that does both."

**Slide 2 — Problem Statement**
Visual: Table comparing 5 platforms (Khan Academy, Coursera, Quizlet, ChatGPT, standard LMS) across 4 criteria: Reads your actual textbook / Knows why you failed / Remembers across sessions / Shows you your own knowledge map. All ✗.
Say: "The industry knows what you got wrong. None of them know why. None of them know your book. And none of them remember tomorrow."

**Slide 3 — The Insight**
Visual: Large text on dark background. *"The book is the curriculum. The student is the variable."*
Below: "Not a hardcoded course. Not a chatbot. A persistent cognitive model — derived from your actual reading material."
Say: "We don't decide what to teach. Your book does. We just track what you know."

**Slide 4 — The Ingestion Pipeline**
Visual: Three-panel animation. Panel 1: PDF upload. Panel 2: concept nodes appearing. Panel 3: prerequisite edges drawing between them.
Caption: "60 seconds. Any textbook. A live knowledge graph."
Say: "Upload your biology textbook. In 60 seconds, this graph appears — concepts extracted from your book, prerequisite relationships inferred automatically. This is not pre-seeded. This came from your PDF."

**Slide 5 — Product Overview**
Visual: Knowledge graph screenshot with mastery-colored nodes and highlighted curriculum path.
Say: "This is what a student sees after their first 8-question assessment. Their cognitive map of their book. What they know. What they're forgetting. What they need next. Real-time. Personalized to their book and their knowledge state."

**Slide 6 — Learning Science Foundation**
Visual: 5-row table. Column 1: mechanism name. Column 2: research citation. Column 3: our implementation.
Say: "Every architectural choice maps to a named learning science paper. This is not intuition — this is implementation of what researchers proved works."

**Slide 7 — Agent Architecture**
Visual: Clean pipeline diagram. Six named agents, shared state layer below.
Say: "Six specialized AI agents. The Ingestion Agent reads the book. The Assessment Agent probes the student. The Curriculum Agent finds the path. The Lesson Agent teaches it. The Tutor Agent enforces Socratic dialogue. The Progress Agent runs pure Python — no LLM — tracking mastery and scheduling review."

**Slide 8 — The Socratic Guardrail**
Visual: Code snippet of the guardrail function. Next to it: two example exchanges — tutor correctly asking a question, a blocked direct-answer attempt.
Say: "The Socratic constraint is not a prompt. It is code. Before any response reaches the student, a function checks cosine similarity between the response and the answer key. If the answer leaked, the response is discarded. This is an architectural guarantee."

**Slide 9 — Cross-Session Memory**
Visual: Two session panels. Session 1 summary: "Struggles: osmosis directionality." Session 2 opener: "Last time you confused which direction water moves in osmosis — let's start there."
Say: "The tutor's first words are generated from your previous session's struggles. Stored in PostgreSQL. Retrieved at session start. Injected into the context. No other platform does this."

**LIVE DEMO — 8 Minutes**
(See Phase 18 demo flow)

**Slide 10 — Dashboard**
Visual: Dashboard screenshot — mastery bars, forgetting curve, error taxonomy expanded.
Say: "The dashboard shows not just what you know — but what you're about to forget. And not just that you failed — but why."

**Slide 11 — Technical Stack**
Visual: Clean architecture diagram.
Say: "React frontend. FastAPI orchestrator. Gemini 2.5 Flash for six agents. Neo4j Aura for the prerequisite graph. PostgreSQL for learner data. Redis for session state. ChromaDB for RAG from the uploaded book."

**Slide 12 — Results**
Visual: Bar chart — mastery delta for demo student after one session. Text: "Tutor Socratic ratio: 78% of responses are questions. Ingestion time: 47 seconds for a 280-page textbook. Concepts extracted: 84."
Say: "Three numbers. Mastery delta after one session. Question ratio confirming the Socratic constraint holds. Ingestion time — the pipeline that makes this platform domain-agnostic."

**Slide 13 — Why This Wins**
Visual: 5 bullets.
Say: "Six decisions no other project makes simultaneously: dynamic knowledge graph from any uploaded book, visible graph as the primary UI, error taxonomy not just mastery score, hard-enforced Socratic guardrail, functional cross-session memory, and theory-to-implementation mapping for every component."

**Slide 14 — Roadmap**
Visual: Timeline.
Say: "Month 1: concept correction UI for students to flag ingestion errors. Month 3: individualized BKT parameter estimation. Month 6: controlled study on retention gains. Year 1: publisher partnerships for licensed book ingestion."

**Slide 15 — Closing**
Visual: Full-screen knowledge graph, nodes in mixed green/yellow/red. Nodes are labeled with biology concepts from the demo book.
Text: *"The AI tutor that reads your textbook, builds a map of your mind, and teaches to the gaps."*
Say: "We didn't build a chatbot. We built a system that reads your book, models your mind, and teaches to the gaps — remembering every mistake across every session. Thank you."

### What to Demo Live

**8-Minute Demo Flow:**
- 0:00–1:00 — Open book upload page. Upload a 280-page biology textbook PDF live (or from fast cache). Watch progress bar: "Chapter 3 of 18 — 34 concepts found." Watch nodes appear on the graph in real time. "The system is reading the book."
- 1:00–1:30 — Graph complete: 84 nodes, prerequisite edges visible. Click one node — sidebar shows chapter, page range, description. "These concepts came from the PDF. Not from a developer."
- 1:30–3:00 — Run adaptive diagnostic. Answer 8 questions live. Watch nodes shift from grey to red/yellow/green as mastery updates. "The system now knows what this student knows about their book."
- 3:00–3:30 — Blue curriculum path appears on graph. "The system queried the prerequisite graph and built their personal path through the book."
- 3:30–5:00 — Open one lesson (Membrane Transport). Show book-grounded explanation. Submit wrong answer. Show error type: "confuses_osmosis_with_diffusion." Show hint 1 release.
- 5:00–6:30 — Switch to Tutor chat. Type: "I don't understand osmosis." Tutor asks a guiding question. Never gives the answer. Say: "Notice — it has never said which direction water moves."
- 6:30–7:30 — Show dashboard: mastery bars, forgetting curve, error taxonomy.
- 7:30–8:00 — Open a second session as the same student. Tutor message: "Last session you confused osmosis directionality — let's fix that today." Say: "This is the only system in this room that does this."

---

## PHASE 18 — FINAL LOCKED ARCHITECTURE

### The Final Locked Product

**Name:** CognMap (working title) — "The learning platform that reads your book and shows you your own mind"

**Domain:** Any subject — determined entirely by the uploaded PDF textbook

**Target user:** University students learning from a course textbook

**Core value proposition:** A persistent cross-session cognitive model per student, derived from their actual book, made visible as a knowledge graph, taught through Socratic dialogue that never forgets

### The Final Locked MVP (14-day deliverable)

1. PDF book upload and async ingestion pipeline (LLM concept + edge extraction → Neo4j)
2. Adaptive diagnostic assessment (CAT-style, 8 questions, book-grounded)
3. Knowledge graph visualization (D3.js, extracted concept nodes, real-time mastery coloring)
4. Prerequisite-aware curriculum generation (Neo4j traversal + Curriculum Agent)
5. Chunked lesson delivery (max 3 concepts, Bloom-escalating questions, 3-hint system, RAG-grounded)
6. Socratic tutor with hard guardrail (cosine similarity check, no direct answers)
7. Cross-session error memory injection (top-3 error types per concept in every tutor prompt)
8. Session opener retrieval practice (spaced-due concepts first)
9. Mastery + retention + error dashboard (scoped per student per book)
10. Session summary generation + cross-session opening message

### The Final Locked Stretch Goals (only if MVP complete before Day 11)

1. Confidence calibration (predict → compare)
2. Curriculum replan on mastery drop
3. Bloom level badge per node in graph
4. Multi-book library with per-book mastery summary
5. Teacher class dashboard

### The Final Locked Tech Stack

| Layer | Technology | Justification |
|---|---|---|
| Frontend | React + TypeScript + TailwindCSS | Industry standard, team familiarity, fast iteration |
| Graph Visualization | D3.js (force-directed) | Most flexible graph rendering library; custom mastery coloring; live Neo4j data |
| Charts | Recharts | React-native, simple API, sufficient for dashboard |
| Backend | FastAPI (Python) | Async support for ingestion pipeline, Pydantic validation, fast dev cycle |
| PDF Parsing | PyMuPDF | Fast, accurate, preserves structure and page numbers |
| LLM | Gemini 2.5 Flash | Large context window (1M tokens) for full chapter ingestion, native JSON mode, near-zero cost, frozen choice from project inception |
| Embeddings | models/text-embedding-004 (Gemini) | Free tier, integrates natively with Gemini API, sufficient quality for book corpus |
| Primary Database | PostgreSQL (Supabase free tier) | ACID, relational, SQL for learner model |
| Graph Database | Neo4j Aura Free | Dynamic prerequisite graph from ingestion, student mastery edges, Cypher |
| Session Cache | Redis (Upstash free tier) | Ephemeral session turns, hint state, active book_id |
| Vector Store | ChromaDB (local) | No external service, per-book collections, sufficient for demo scale |
| Auth | JWT (python-jose) | Stateless, standard, no external service |
| State Management | Zustand | Lightweight, React-native |
| Async Tasks | Python asyncio + FastAPI BackgroundTasks | Sufficient for ingestion pipeline at demo scale |

### The Final Locked Roadmap

**Days 1–2:** Foundation (schema including books table, Ingestion Agent prompts, Neo4j schema, project structure)
**Days 3–4:** Ingestion Pipeline end-to-end + Assessment + Curriculum + Progress Agent BKT/SM2
**Days 5–6:** Lesson Agent (RAG-grounded) + D3.js graph (core loop functional)
**Days 7–8:** Tutor Agent + guardrail + Redis session + cross-session memory
**Days 9–10:** Dashboard + full integration test
**Day 11:** Real user test with real book + critical bug fixes
**Day 12:** Demo hardening + adversarial testing
**Day 13:** Presentation + viva rehearsal
**Day 14:** Buffer + final polish

### Non-Negotiable Architecture Decisions (Cannot Be Changed)

1. **Neo4j is used.** The instructor taught graph databases. Not using it is leaving bonus marks on the table — and it is the only appropriate store for the dynamically generated prerequisite graph.
2. **The knowledge graph is generated from the uploaded book.** No concept is manually authored. The Ingestion Agent is the source of truth for all graph content.
3. **The guardrail is code, not just a prompt.** This is the defensible claim in the viva. A soft prompt is not architecture.
4. **Error taxonomy is stored and injected.** Not just mastery score. This is the primary educational differentiator.
5. **The knowledge graph is the first thing a user sees after ingestion.** Not a chat interface. Not a course list.
6. **Session opener uses spaced-due concepts first.** This is architecturally enforced, not optional.
7. **Domain is determined by the uploaded book.** The platform is not locked to any subject. DSA, biology, economics, physics — the same codebase handles all.
8. **No voice interface, no emotion detection, no AR/VR, no social features, no DKT, no IRT, no code autograder.** These are cut. Final. Not reconsidered.

---

*This document is the single source of truth. Implementation begins with Day 1 tasks above. All architectural decisions are locked. No alternatives exist.*

---

**Document Version:** 2.0 — Adaptive Book-Learning Platform
**Supersedes:** Version 1.0 (DSA-locked platform)
**Prepared by:** Architecture Review Board (10-role composite)
**Date:** June 2026
**Status:** APPROVED — PROCEED TO IMPLEMENTATION