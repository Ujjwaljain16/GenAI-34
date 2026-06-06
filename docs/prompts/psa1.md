# LearnGraph AI

# Prompt System Architecture Specification (PSA)

Version: 1.0

---

# 1. Purpose

This document defines the complete prompt architecture used by LearnGraph AI.

The architecture governs:

* Prompt design
* Prompt execution
* Prompt storage
* Prompt versioning
* Prompt observability
* Prompt evaluation
* Prompt safety
* Prompt deployment
* Prompt rollback

This document serves as the authoritative specification for all prompt-driven components.

---

# 2. Architectural Principles

## Principle 1

Prompts are software.

Treat prompts as:

* Versioned assets
* Tested assets
* Observable assets
* Deployable assets

Never treat prompts as static strings.

---

## Principle 2

LLMs are decision engines, not databases.

All factual learner state comes from:

PostgreSQL

Examples:

* mastery
* retention
* assessments
* quiz history
* learning preferences
* misconceptions

---

Neo4j

Examples:

* prerequisite graph
* concept dependencies
* curriculum graph
* concept relationships

---

The LLM never invents state.

---

## Principle 3

Prompt outputs must be machine-readable.

All prompts output:

```json
{
}
```

No markdown.

No prose.

No free-form output.

---

## Principle 4

Every prompt execution is observable.

Every run must produce:

* input snapshot
* prompt version
* model version
* latency
* token counts
* validation results
* final output

---

## Principle 5

Prompts must be composable.

No prompt should directly invoke another prompt.

Instead:

```text
Application Layer
      ↓
Prompt Orchestrator
      ↓
Prompt Runtime
      ↓
LLM
```

This prevents recursive prompt coupling.

---

# 3. High-Level Prompt Architecture

```text
                ┌───────────────────────┐
                │ Learning Graph Engine │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ Context Retrieval     │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ Prompt Orchestrator   │
                └───────────┬───────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼

 Assessment        Curriculum       Tutor

 Generator         Generator        Engine

          ▼                 ▼                 ▼

                ┌───────────────────────┐
                │ Gemini 2.5 Flash      │
                └───────────┬───────────┘
                            │
                            ▼

                Output Validation

                            │
                            ▼

                Persistence Layer
```

---

# 4. Prompt Hierarchy

Prompts are categorized into five layers.

---

## Layer 0

System Prompt Layer

Purpose:

Global rules.

Examples:

* JSON only
* No hallucination
* No concept invention
* Safety constraints

Shared across all prompts.

---

## Layer 1

Task Prompt Layer

Defines task behavior.

Examples:

* Assessment Generator
* Lesson Generator
* Quiz Generator

---

## Layer 2

Context Layer

Injects learner state.

Examples:

```json
{
  "mastery": {},
  "retention": {},
  "misconceptions": {},
  "learning_history": {}
}
```

---

## Layer 3

Execution Layer

Contains:

* temperature
* max tokens
* model config

Example:

```json
{
  "model":"gemini-2.5-flash",
  "temperature":0.3,
  "max_tokens":4000
}
```

---

## Layer 4

Validation Layer

Ensures:

* schema compliance
* guardrails
* correctness

before output is accepted.

---

# 5. Prompt Ownership Model

Every prompt must have an owner.

---

## Prompt Owner

Responsible for:

* correctness
* educational quality
* version updates

Example:

```json
{
  "prompt_id":"lesson_generator",
  "owner":"learning-science-team"
}
```

---

## Technical Owner

Responsible for:

* deployment
* monitoring
* rollback

Example:

```json
{
  "technical_owner":"ai-platform-team"
}
```

---

# 6. Prompt Lifecycle

```text
Design
  ↓
Review
  ↓
Offline Evaluation
  ↓
Canary Deployment
  ↓
Production
  ↓
Monitoring
  ↓
Improvement
```

---

# Stage 1

Design

Activities:

* requirement analysis
* educational review
* prompt drafting

Outputs:

```text
prompt_v1
```

---

# Stage 2

Review

Participants:

* AI engineer
* learning scientist
* evaluator

Checklist:

* hallucination risk
* JSON compliance
* educational quality

---

# Stage 3

Offline Evaluation

Run prompt against:

Golden Dataset

Examples:

```text
100 recursion learners
100 tree learners
100 graph learners
```

Metrics:

* correctness
* personalization
* consistency

---

# Stage 4

Canary

Deploy to:

```text
5% users
```

Monitor:

* failure rate
* latency
* user engagement

---

# Stage 5

Production

Rollout:

```text
100%
```

after evaluation passes.

---

# 7. Prompt Registry Architecture

All prompts stored in Prompt Registry.

---

## Registry Schema

```sql
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY,

    prompt_key VARCHAR(200),

    name VARCHAR(500),

    category VARCHAR(100),

    description TEXT,

    owner VARCHAR(200),

    technical_owner VARCHAR(200),

    active_version_id UUID,

    created_at TIMESTAMP,

    updated_at TIMESTAMP
);
```

---

# Prompt Versions

```sql
CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY,

    prompt_template_id UUID,

    version VARCHAR(50),

    system_prompt TEXT,

    user_prompt TEXT,

    input_schema JSONB,

    output_schema JSONB,

    evaluation_config JSONB,

    deployment_status VARCHAR(50),

    created_by VARCHAR(200),

    created_at TIMESTAMP
);
```

---

# 8. Prompt Runtime Architecture

```text
Request
   ↓

Context Builder

   ↓

Prompt Composer

   ↓

Gemini Runtime

   ↓

Validator

   ↓

Retry Engine

   ↓

Persistence
```

---

# Context Builder Responsibilities

Collect:

```json
{
  "mastery": {},
  "retention": {},
  "misconceptions": {},
  "curriculum_state": {},
  "graph_state": {},
  "memory_summary": {}
}
```

---

# Prompt Composer Responsibilities

Construct final prompt:

```text
System Prompt
+
Task Prompt
+
Context
+
Input
```

---

# 9. Prompt Run Logging

Every execution stored.

```sql
CREATE TABLE prompt_runs (

    id UUID PRIMARY KEY,

    learner_id UUID,

    prompt_template_id UUID,

    prompt_version_id UUID,

    model_name VARCHAR(100),

    input_payload JSONB,

    context_payload JSONB,

    raw_output TEXT,

    parsed_output JSONB,

    validation_passed BOOLEAN,

    retry_count INT,

    latency_ms INT,

    prompt_tokens INT,

    completion_tokens INT,

    total_tokens INT,

    created_at TIMESTAMP
);
```

---

# 10. Prompt Versioning Strategy

Semantic Versioning

Format:

```text
MAJOR.MINOR.PATCH
```

Example:

```text
1.4.2
```

Meaning:

Major

Breaking schema change.

---

Minor

Behavioral improvement.

---

Patch

Prompt wording adjustment.

---

Examples

```text
1.0.0 Initial

1.1.0 Better personalization

1.1.1 JSON fix

2.0.0 Schema redesign
```

---

# 11. Prompt Deployment Strategy

Deployment States

```text
DRAFT
TESTING
CANARY
ACTIVE
DEPRECATED
ARCHIVED
```

Allowed transitions:

```text
DRAFT
  ↓
TESTING
  ↓
CANARY
  ↓
ACTIVE
  ↓
DEPRECATED
  ↓
ARCHIVED
```

---

# 12. Rollback Strategy

Triggers:

* Validation failure > 5%
* Hallucination rate > 3%
* Educational score drop > 10%
* Latency increase > 30%

Rollback:

```text
Current Version
        ↓
Previous Stable Version
```

Rollback target determined automatically.

---

# 13. Prompt Guardrail Framework

Every prompt execution passes through:

```text
Input Validation
       ↓
Prompt Execution
       ↓
Schema Validation
       ↓
Educational Validation
       ↓
Persistence
```

---

Guardrails implemented:

### G1

JSON-only outputs

### G2

No unsupported concepts

### G3

No curriculum invention

### G4

No prerequisite invention

### G5

No answer leakage

### G6

Bloom compliance

### G7

Difficulty compliance

### G8

Safety compliance

---

# 14. Prompt Observability Architecture

Core Metrics

---

## Reliability

```text
Success Rate
Failure Rate
Retry Rate
Validation Rate
```

---

## Cost

```text
Prompt Tokens
Completion Tokens
Total Cost
```

---

## Performance

```text
Latency
P95 Latency
P99 Latency
```

---

## Educational

```text
Learning Gain
Assessment Accuracy
Hint Effectiveness
Tutor Success Rate
```

---

# 15. Analytics Schema

```sql
CREATE TABLE prompt_metrics (

    id UUID PRIMARY KEY,

    prompt_version_id UUID,

    day DATE,

    runs INT,

    failures INT,

    retries INT,

    avg_latency_ms INT,

    avg_tokens INT,

    success_rate FLOAT,

    educational_score FLOAT,

    created_at TIMESTAMP
);
```

---

# 16. A/B Testing Framework

Supported Experiments:

```text
Prompt Wording

Context Retrieval

Hint Strategy

Tutor Strategy

Lesson Structure
```

Schema:

```sql
CREATE TABLE prompt_experiments (

    id UUID PRIMARY KEY,

    prompt_template_id UUID,

    variant_a UUID,

    variant_b UUID,

    traffic_split FLOAT,

    metric_config JSONB,

    status VARCHAR(50)
);
```

---

# 17. Failure Recovery Framework

Failure Types:

### F1

Invalid JSON

Action:

Retry with JSON repair prompt.

---

### F2

Schema mismatch

Action:

Retry once.

---

### F3

Hallucinated concepts

Action:

Reject output.

---

### F4

Low educational score

Action:

Fallback prompt version.

---

### F5

Token overflow

Action:

Context compression.

---

# 18. Future-Proofing

Architecture supports:

* Gemini upgrades
* Multi-model routing
* Deep Research agents
* Tool calling
* Agentic planning
* RAG integration
* Long-term memory evolution
* Curriculum graph expansion

without redesigning prompt infrastructure.

---