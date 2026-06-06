# LearnGraph AI

# Prompt Library Specification (PLS)

# Part 2

Covered Components:

5. Curriculum Generator
6. Curriculum Replanner
7. Lesson Generator
8. Exercise Generator
9. Quiz Generator

---

# Prompt 05

# Curriculum Generator

Prompt Key

```text
curriculum_generator
```

---

# Purpose

Generate a personalized learning sequence from concepts already selected by the Knowledge Graph Engine.
The LLM is NOT responsible for curriculum discovery; it only prioritizes and estimates effort.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.3
max_retries: 2
timeout_seconds: 15
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "eligible_concepts": [],
  "mastery": {},
  "retention": {},
  "misconceptions": [],
  "learning_dna": {},
  "curriculum_progress": {},
  "graph_constraints": {}
}
```

---

# Inputs

```text
eligible_concepts
max_weekly_hours
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["eligible_concepts", "max_weekly_hours"],
  "properties": {
    "eligible_concepts": {
      "type": "array",
      "items": { "type": "string" }
    },
    "max_weekly_hours": {
      "type": "number",
      "minimum": 1
    }
  }
}
```

---

# Input Example

```json
{
  "eligible_concepts": ["Recursion", "Trees", "Graphs"],
  "max_weekly_hours": 10
}
```

---

# Production Prompt

```text
You are LearnGraph's Curriculum Planning Engine.

IMPORTANT:

You are NOT allowed to introduce concepts.
You may ONLY use concepts contained in Eligible Concepts.

Your task:

Rank concepts for study order.

Use:

- Mastery
- Retention
- Misconceptions
- Learning DNA
- Dependency importance

Rules:

1. Never invent concepts.
2. Never alter dependency constraints.
3. Prioritize highest learning impact.
4. Explain every recommendation.
5. Estimate study duration.
6. Return JSON only.

Eligible Concepts:
{{eligible_concepts}}

Mastery:
{{mastery}}

Retention:
{{retention}}

Misconceptions:
{{misconceptions}}

Learning DNA:
{{learning_dna}}
```

---

# Output Schema

```json
{
  "type": "object",
  "required": ["schema_version", "generated_at", "prompt_version", "curriculum"],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "curriculum": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["concept", "priority", "estimated_minutes", "reason"],
        "properties": {
          "concept": { "type": "string" },
          "priority": { "type": "integer" },
          "estimated_minutes": { "type": "integer" },
          "reason": { "type": "string" }
        }
      }
    }
  }
}
```

---

# Output Example

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-06-02T12:00:00Z",
  "prompt_version": "v1",
  "curriculum": [
    {
      "concept": "Recursion",
      "priority": 1,
      "estimated_minutes": 120,
      "reason": "Low mastery and prerequisite for Trees"
    }
  ]
}
```

---

# Validation Rules

1. Concept must exist in `eligible_concepts`.
2. No duplicates.
3. Priority must be sequential.
4. Duration: 15 ≤ duration ≤ 600.

---

# Failure Cases

F1: Hallucinated concept.
F2: Dependency violation.
F3: No rationale.
F4: Invalid duration.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with reduced context (remove Learning DNA).
Tier 3: Deterministic fallback (sort concepts by depth in neo4j graph and current mastery levels).
```

---

# Evaluation Metrics

Ranking Agreement: >85%
Dependency Compliance: 100%
Hallucination Rate: 0%

---

# Prompt 06

# Curriculum Replanner

Prompt Key

```text
curriculum_replanner
```

---

# Purpose

Adapt curriculum after new learner evidence arrives (e.g., Assessment Complete, Retention Drop).

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.3
max_retries: 2
timeout_seconds: 15
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "previous_curriculum": {},
  "updated_mastery": {},
  "updated_retention": {},
  "updated_errors": {},
  "graph_state": {}
}
```

---

# Inputs

```text
curriculum_id
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["curriculum_id"],
  "properties": {
    "curriculum_id": { "type": "string", "format": "uuid" }
  }
}
```

---

# Input Example

```json
{
  "curriculum_id": "cur_888"
}
```

---

# Production Prompt

```text
You are LearnGraph's Curriculum Replanning Engine.

Your task:

Update an existing curriculum.

Rules:

1. Preserve dependency order.
2. Explain every change.
3. Use only graph-approved concepts.
4. Add concepts only if supplied.
5. Remove concepts only when justified.
6. Return JSON only.

Previous Curriculum:
{{previous_curriculum}}

Updated Mastery:
{{updated_mastery}}

Updated Retention:
{{updated_retention}}

Updated Errors:
{{updated_errors}}

Graph State:
{{graph_state}}
```

---

# Output Schema

```json
{
  "type": "object",
  "required": [
    "schema_version",
    "generated_at",
    "prompt_version",
    "added_concepts",
    "removed_concepts",
    "reordered_concepts",
    "reasons",
    "updated_curriculum"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "added_concepts": { "type": "array", "items": { "type": "string" } },
    "removed_concepts": { "type": "array", "items": { "type": "string" } },
    "reordered_concepts": { "type": "array", "items": { "type": "string" } },
    "reasons": { "type": "array", "items": { "type": "string" } },
    "updated_curriculum": { "type": "array", "items": { "type": "object" } }
  }
}
```

---

# Output Example

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-06-02T12:00:00Z",
  "prompt_version": "v1",
  "added_concepts": [],
  "removed_concepts": ["Trees"],
  "reordered_concepts": [],
  "reasons": ["Trees removed until Recursion mastery improves above 0.85"],
  "updated_curriculum": []
}
```

---

# Validation Rules

1. No dependency violations.
2. No unsupported additions.
3. Reasons required.

---

# Failure Cases

F1: Replanner breaks dependency chain.
F2: Replanner introduces hallucinated topics.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with empty updated_errors.
Tier 3: Deterministic fallback (keep existing curriculum without changes).
```

---

# Evaluation Metrics

Plan Stability: >80%
Adaptation Accuracy: >90%
Dependency Compliance: 100%

---

# Prompt 07

# Lesson Generator

Prompt Key

```text
lesson_generator
```

---

# Purpose

Generate personalized lessons that Explain, Connect, Demonstrate, Practice, and Reinforce.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.5
max_retries: 2
timeout_seconds: 30
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "concept": {},
  "mastery": {},
  "retention": {},
  "misconceptions": [],
  "learning_dna": {},
  "learning_history": {}
}
```

---

# Inputs

```text
concept
target_bloom
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["concept", "target_bloom"],
  "properties": {
    "concept": { "type": "string" },
    "target_bloom": { "type": "string" }
  }
}
```

---

# Input Example

```json
{
  "concept": "Recursion",
  "target_bloom": "Apply"
}
```

---

# Production Prompt

```text
You are LearnGraph's Personalized Lesson Engine.

Generate a lesson.

Requirements:

1. Adapt depth to mastery.
2. Adapt examples to learning preferences.
3. Address known misconceptions.
4. Build toward target bloom level.
5. Use progressive explanation.
6. Avoid unnecessary jargon.
7. Include exercises.
8. Include misconception prevention.
9. Return JSON only.

Concept:
{{concept}}

Mastery:
{{mastery}}

Retention:
{{retention}}

Misconceptions:
{{misconceptions}}

Learning DNA:
{{learning_dna}}

Learning History:
{{learning_history}}

Target Bloom:
{{target_bloom}}
```

---

# Output Schema

```json
{
  "type": "object",
  "required": [
    "schema_version",
    "generated_at",
    "prompt_version",
    "concept",
    "introduction",
    "mental_model",
    "core_explanation",
    "analogy",
    "worked_examples",
    "common_mistakes",
    "practice_exercises",
    "summary",
    "key_takeaways"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "concept": { "type": "string" },
    "introduction": { "type": "string" },
    "mental_model": { "type": "string" },
    "core_explanation": { "type": "string" },
    "analogy": { "type": "string" },
    "worked_examples": { "type": "array", "items": { "type": "string" } },
    "common_mistakes": { "type": "array", "items": { "type": "string" } },
    "practice_exercises": { "type": "array", "items": { "type": "string" } },
    "summary": { "type": "string" },
    "key_takeaways": { "type": "array", "items": { "type": "string" } }
  }
}
```

---

# Output Example

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-06-02T12:00:00Z",
  "prompt_version": "v1",
  "concept": "Recursion",
  "introduction": "Recursion is solving a problem by solving smaller versions of itself.",
  "mental_model": "Think of nested Russian dolls.",
  "core_explanation": "A function calls itself until a base case is met.",
  "analogy": "A line of people asking the person in front of them a question.",
  "worked_examples": ["Factorial algorithm code walkthrough."],
  "common_mistakes": ["Forgetting the base case."],
  "practice_exercises": ["Write a recursive countdown."],
  "summary": "Recursion needs a base case and a recursive step.",
  "key_takeaways": ["Always define the base case first."]
}
```

---

# Validation Rules

1. Lesson Completeness.
2. Misconception Coverage.
3. Bloom Alignment.

---

# Failure Cases

F1: Too advanced.
F2: Too shallow.
F3: Ignoring misconceptions.
F4: No examples.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with empty Learning DNA (to simplify generation).
Tier 3: Deterministic fallback (Use standard, static lesson template for the concept from concepts.json).
```

---

# Evaluation Metrics

Lesson Quality: >90%
Misconception Coverage: >95%
Bloom Alignment: >90%

---

# Prompt 08

# Exercise Generator

Prompt Key

```text
exercise_generator
```

---

# Purpose

Generate adaptive deliberate practice.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.5
max_retries: 2
timeout_seconds: 15
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "concept": {},
  "mastery": {},
  "misconceptions": [],
  "lesson_summary": {}
}
```

---

# Inputs

```text
concept
mastery
target_bloom
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["concept", "mastery", "target_bloom"],
  "properties": {
    "concept": { "type": "string" },
    "mastery": { "type": "number" },
    "target_bloom": { "type": "string" }
  }
}
```

---

# Input Example

```json
{
  "concept": "Recursion",
  "mastery": 0.42,
  "target_bloom": "Apply"
}
```

---

# Production Prompt

```text
You are LearnGraph's Exercise Generation Engine.

Generate practice exercises.

Rules:

1. Match difficulty to mastery.
2. Target bloom level.
3. Address misconceptions.
4. Encourage active reasoning.
5. Provide expected solution.
6. Provide hints.
7. Return JSON only.

Concept:
{{concept}}

Mastery:
{{mastery}}

Misconceptions:
{{misconceptions}}

Target Bloom:
{{target_bloom}}
```

---

# Output Schema

```json
{
  "type": "object",
  "required": [
    "schema_version",
    "generated_at",
    "prompt_version",
    "difficulty",
    "exercises"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "difficulty": { "type": "string" },
    "exercises": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["question", "expected_solution", "hints"],
        "properties": {
          "question": { "type": "string" },
          "expected_solution": { "type": "string" },
          "hints": { "type": "array", "items": { "type": "string" } }
        }
      }
    }
  }
}
```

---

# Output Example

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-06-02T12:00:00Z",
  "prompt_version": "v1",
  "difficulty": "medium",
  "exercises": [
    {
      "question": "Write a recursive function to compute the Nth Fibonacci number.",
      "expected_solution": "if n <= 1 return n; else return fib(n-1) + fib(n-2);",
      "hints": ["Remember you need two recursive calls."]
    }
  ]
}
```

---

# Validation Rules

1. Difficulty consistency.
2. Concept consistency.

---

# Failure Cases

F1: Exercise easier than mastery.
F2: Exercise unrelated.
F3: Solution leakage in hints.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with missing misconceptions to simplify request.
Tier 3: Deterministic fallback (Use concepts.json practice_examples).
```

---

# Evaluation Metrics

Difficulty Match: >90%
Hint Quality: >90%

---

# Prompt 09

# Quiz Generator

Prompt Key

```text
quiz_generator
```

---

# Purpose

Generate post-lesson evaluation spanning Remember, Understand, Apply, Analyze.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.4
max_retries: 2
timeout_seconds: 20
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "lesson": {},
  "concept": {},
  "mastery": {},
  "misconceptions": [],
  "target_bloom": ""
}
```

---

# Inputs

```text
concept
question_count
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["concept", "question_count"],
  "properties": {
    "concept": { "type": "string" },
    "question_count": { "type": "integer" }
  }
}
```

---

# Input Example

```json
{
  "concept": "Recursion",
  "question_count": 5
}
```

---

# Production Prompt

```text
You are LearnGraph's Quiz Generation Engine.

Generate a quiz.

Rules:

1. Cover target concept.
2. Cover misconceptions.
3. Use Bloom distribution.
4. Mix difficulty appropriately.
5. Avoid duplicate questions.
6. Provide explanations.
7. Return JSON only.

Concept:
{{concept}}

Lesson:
{{lesson}}

Mastery:
{{mastery}}

Misconceptions:
{{misconceptions}}

Target Bloom:
{{target_bloom}}
```

---

# Output Schema

```json
{
  "type": "object",
  "required": [
    "schema_version",
    "generated_at",
    "prompt_version",
    "quiz"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "quiz": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["question", "difficulty", "bloom_level", "expected_answer", "explanation"],
        "properties": {
          "question": { "type": "string" },
          "difficulty": { "type": "string" },
          "bloom_level": { "type": "string" },
          "expected_answer": { "type": "string" },
          "explanation": { "type": "string" }
        }
      }
    }
  }
}
```

---

# Output Example

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-06-02T12:00:00Z",
  "prompt_version": "v1",
  "quiz": [
    {
      "question": "What is missing here: def foo(n): return foo(n-1)?",
      "difficulty": "beginner",
      "bloom_level": "analyze",
      "expected_answer": "Base case",
      "explanation": "Without a base case, it causes a stack overflow."
    }
  ]
}
```

---

# Validation Rules

1. Question Diversity.
2. Bloom Distribution.
3. Misconception Coverage.

---

# Failure Cases

F1: Repeated questions.
F2: Bloom imbalance.
F3: No misconception coverage.
F4: Answer ambiguity.

---

# Mitigation

```text
Tier 1: Retry prompt for violating questions only.
Tier 2: Retry full prompt with generic bloom distribution.
Tier 3: Deterministic fallback (Use concepts.json practice_examples adapted to MCQ).
```

---

# Evaluation Metrics

Bloom Accuracy: >95%
Misconception Coverage: >95%