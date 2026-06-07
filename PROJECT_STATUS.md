# Lexis — Project Status & Handover

Current state of the Lexis Adaptive Book-Learning Platform. Work below lives on
branch **`feat/assessment-engine`** (25+ commits ahead of `main`, not yet pushed).
**39 unit tests pass; all 9 GenAI prompt tasks meet their PEOS targets;** the
frontend builds and has been manually QA'd through the browser end-to-end.

---

## ✅ Done & working end-to-end

### Foundation (pre-existing, verified)
- **Auth** — `/auth/register`, `/auth/login` (bcrypt + JWT); NextAuth forwards the bearer token.
- **PostgreSQL core** — `schema.sql` (26 tables + views), SQLAlchemy async, typed ENUM mappings.
- **Library + 2-step upload** — `POST /books` → `POST /books/{id}/upload` → background ingestion worker; status polling.
- **Ingestion pipeline** — PyMuPDF parse → chunk → **Gemini concept + prerequisite + sub-topic extraction** → canonicalize → cycle-check/repair → publish graph version. Source file deleted after a successful build (configurable).

### Learner-model engines (built this cycle — the product core)
Each engine is contract-first (types → schema → API → logic), unit-tested where it has pure logic, and wired to the UI.
- **Assessment + Learning DNA** — adaptive topological DAG walk (MCQ→theory→applied, branch-stop, confidence calibration); atomic `/complete` seeds `concept_mastery` + `user_concept_state` and generates Gemini DNA. `/api/v1/assessments` (start/resume, responses, complete, results).
- **Graph reveal** — per-user four-state overlay (locked/available/mastered/due). `GET /books/{id}/knowledge-graph`.
- **Curriculum + Daily Plan** — deterministic (graph-decided); **persisted "today's focus"** (soft-focus, frozen per day, regenerates when the set is mastered); concept **sub-topics** surfaced as chips. `/books/{id}/curriculum`, `/daily-plan`.
- **Lessons + Socratic Tutor + Hints** — Gemini lessons grounded in source chunks; tutor teaches by questioning (0% answer-leakage in evals), captures `user_asked` questions; **persistent/resumable** sessions. `/api/v1/lessons/...`.
- **Mastery is earned, not declared** — finishing a lesson does **not** master a concept; a **mastery-check quiz** (3 questions) gates mastery + dependency unlock. `/lessons/{id}/quiz` + `/quiz/grade`.
- **Mastery + FSRS + Revision** — canonical mastery engine (`mastery_engine.md`) + FSRS scheduler; due detection, review grading, MASTERED↔DUE. `GET /books/{id}/revision`, `POST /books/{id}/concepts/{cid}/review`.
- **Dashboard / Stats / Streaks** — aggregation + activity-derived streaks; **real notifications** (no longer a `[]` stub). `GET /dashboard`, `GET /notifications`.
- **Neo4j projection** — best-effort `PREREQUISITE_OF` / `HAS_MASTERY` / `CURRENTLY_LEARNING` (Postgres is source of truth). `POST /books/{id}/graph/sync-neo4j`.

### Frontend (wired to the real backend)
`src/lib/api.ts` adapter maps every screen to `/api/v1`. Library, upload/processing, **graph verify**, **assessment** (intro/question/results), **course/graph map**, **daily plan**, **lesson + tutor + quiz**, **revision**, **dashboard/progress**, settings, notifications. Markdown/code rendering for AI text. ~10 UX bugs found during QA and fixed (see git log).

### Quality
- **Eval harness** — `backend/evals/` golden datasets + scorers + `python -m evals.run_evals` (concept extraction, relationship, merge, assessment-gen, assessment-eval, DNA, lesson, tutor, hint). LLM-as-judge fallback for concept purity. All meet PEOS targets.
- **39 unit tests** — placement walk, curriculum planner, mastery engine, FSRS, streaks, eval scorers.

---

## 🚧 Known limitations / follow-ups for the team
- **Ingestion is O(n²) on edge inference + rate-limited (~5s/call)** → fine for small books, **not viable for large books** (e.g. 600-page LLD.pdf would take hours and exhaust the free Gemini tier). Needs batching/caching before big books.
- **File storage is local disk** (`uploads/`) behind a `StorageProvider` interface — add an S3 provider for prod (factory already in place).
- **No automated HTTP/integration tests** — coverage is unit tests + the eval harness + manual QA. API-level tests are a gap.
- **Tutor/quiz cost** — each interactive step is a live Gemini call; consider caching/pre-generation for demos (free tier ≈ 15 RPM).

## 🗄️ Database / migration notes (read before merging)
- **`schema.sql` is now correct** — a fresh `psql -f backend/db/schema.sql` applies with zero errors (verified on a scratch DB). Fixed: the escaped-quote `upload_status` enum bug, `books.file_url` made nullable, added the `daily_plans` table.
- **Existing databases**: run `backend/db/migrations/2026-06-07_ingestion_dailyplans_fixes.sql` (idempotent) to upgrade a DB built from the old schema.
- **Alembic** exists (`backend/migrations/`) but the live DB was built from `schema.sql` and is **not stamped**; only one baseline revision exists. Decide whether to standardize on Alembic or `schema.sql` and reconcile (sub-topics live in `concepts.metadata->'subtopics'`, no DDL).

## 📌 Handover checklist
- [ ] Push `feat/assessment-engine` and open a PR (crosses AGENT.md ownership lines — needs review by prompt/graph/backend owners).
- [ ] Reconcile migrations (Alembic vs schema.sql) per the notes above.
- [ ] `backend/.env` holds a Gemini key locally — **not committed**; each dev supplies their own.
- [ ] Local infra gotcha: stop Homebrew Postgres if it shadows Docker's on :5432.
