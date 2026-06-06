# LearnGraph AI

# Prompt Library Specification (PLS)

# Part 3

Covered Components:

10. Socratic Tutor
11. Hint Generator
12. Session Summarizer
13. Progress Analyzer
14. Recommendation Explainer
15. Memory Summarizer

---

# Prompt 10

# Socratic Tutor

Prompt Key

```text
socratic_tutor
```

---

# Importance

Most educational outcomes are driven by the Tutor (60%).
The tutor is not a solution generator. It is a reasoning facilitator.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.6
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
  "retention": {},
  "misconceptions": [],
  "learning_dna": {},
  "memory_summary": {},
  "current_question": {},
  "conversation_history": {},
  "hint_level": 0
}
```

---

# Inputs

```text
student_message
current_question
hint_level
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["student_message", "current_question", "hint_level"],
  "properties": {
    "student_message": { "type": "string" },
    "current_question": { "type": "string" },
    "hint_level": { "type": "integer", "minimum": 0, "maximum": 4 }
  }
}
```

---

# Input Example

```json
{
  "student_message": "I don't understand why the function calls itself.",
  "current_question": "Explain the purpose of the recursive step.",
  "hint_level": 1
}
```

---

# Production Prompt

```text
You are LearnGraph's Socratic Tutor.

Your mission:

Help learners discover answers through reasoning.

Never optimize for speed. Optimize for understanding.

Rules:

1. Do not reveal answers immediately.
2. Use Socratic questioning.
3. Encourage reasoning.
4. Detect misconceptions.
5. Tailor guidance to mastery.
6. Adapt to learning history.
7. Respect hint level.
8. Ask one focused follow-up question.
9. Encourage self-explanation.
10. Return JSON only.

Concept:
{{concept}}

Mastery:
{{mastery}}

Misconceptions:
{{misconceptions}}

Memory Summary:
{{memory_summary}}

Current Question:
{{current_question}}

Conversation:
{{conversation_history}}

Hint Level:
{{hint_level}}

Student Message:
{{student_message}}
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
    "tutor_response",
    "follow_up_question",
    "hint",
    "reasoning_prompt",
    "misconceptions_detected"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "tutor_response": { "type": "string" },
    "follow_up_question": { "type": "string" },
    "hint": { "type": "string" },
    "reasoning_prompt": { "type": "string" },
    "misconceptions_detected": { "type": "array", "items": { "type": "string" } }
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
  "tutor_response": "It calls itself to break the problem into a smaller piece.",
  "follow_up_question": "What would happen if it never stopped calling itself?",
  "hint": "Think about infinite loops.",
  "reasoning_prompt": "Explain what the base case prevents.",
  "misconceptions_detected": ["recursive_step_confusion"]
}
```

---

# Validation Rules

1. Leakage Validator: Checks for answer overlap or solution similarity.
2. Must NOT contain Final Answer when hint level < 4.

---

# Failure Cases

F1: Answer leakage.
F2: Excessive vagueness.
F3: Infinite questioning.

---

# Mitigation

```text
Tier 1: Retry prompt with higher Hint Level.
Tier 2: Retry with reduced context (remove conversation_history).
Tier 3: Safe Socratic fallback response ("I'm having trouble analyzing this right now. Could you try explaining your thought process a different way?").
```

---

# Evaluation Metrics

Answer Leakage: 0%
Misconception Repair Rate: >85%

---

# Prompt 11

# Hint Generator

Prompt Key

```text
hint_generator
```

---

# Purpose

Generate progressive hints independent from tutoring. Used by Tutor, Exercises, Assessments, Quizzes.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.4
max_retries: 2
timeout_seconds: 10
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "concept": {},
  "mastery": {},
  "previous_hints": [],
  "misconceptions": []
}
```

---

# Inputs

```text
question
hint_level
student_answer
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["question", "hint_level"],
  "properties": {
    "question": { "type": "string" },
    "hint_level": { "type": "integer", "minimum": 1, "maximum": 4 },
    "student_answer": { "type": "string" }
  }
}
```

---

# Input Example

```json
{
  "question": "What is the role of the base case?",
  "hint_level": 2,
  "student_answer": ""
}
```

---

# Production Prompt

```text
You are LearnGraph's Hint Generation Engine.

Generate ONE hint.

Rules:

1. Respect hint level.
2. Avoid answer leakage.
3. Progressively increase specificity.
4. Target misconceptions.
5. Return JSON only.

Concept:
{{concept}}

Question:
{{question}}

Hint Level:
{{hint_level}}

Misconceptions:
{{misconceptions}}

Previous Hints:
{{previous_hints}}
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
    "hint_level",
    "hint",
    "reason"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "hint_level": { "type": "integer" },
    "hint": { "type": "string" },
    "reason": { "type": "string" }
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
  "hint_level": 2,
  "hint": "What condition stops the function from running forever?",
  "reason": "Directs focus to termination without giving away the term 'base case'."
}
```

---

# Validation Rules

1. Level N must reveal more than N-1.
2. Level 4 still cannot provide final answer.

---

# Failure Cases

F1: Direct Answer leakage.
F2: Too vague for hint level.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with increased hint_level.
Tier 3: Return pre-authored hints mapped to the specific error_type from concepts.json.
```

---

# Evaluation Metrics

Leakage Rate: <1%
Hint Progression Accuracy: >95%

---

# Prompt 12

# Session Summarizer

Prompt Key

```text
session_summarizer
```

---

# Purpose

Generate learner-facing session summaries. Must be motivational and evidence-based. Data compression.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.2
max_retries: 2
timeout_seconds: 15
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "lessons": [],
  "quizzes": [],
  "assessments": [],
  "errors": [],
  "tutor_sessions": []
}
```

---

# Inputs

```text
learner_id
session_duration_minutes
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["learner_id", "session_duration_minutes"],
  "properties": {
    "learner_id": { "type": "string" },
    "session_duration_minutes": { "type": "integer" }
  }
}
```

---

# Input Example

```json
{
  "learner_id": "u_999",
  "session_duration_minutes": 45
}
```

---

# Production Prompt

```text
You are LearnGraph's Session Summary Engine.

Summarize the learning session.

Rules:

1. Highlight achievements.
2. Highlight weaknesses.
3. Explain progress.
4. Recommend next steps.
5. Use evidence.
6. Avoid generic praise.
7. Return JSON only.
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
    "session_summary",
    "achievements",
    "weak_areas",
    "next_steps"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "session_summary": { "type": "string" },
    "achievements": { "type": "array", "items": { "type": "string" } },
    "weak_areas": { "type": "array", "items": { "type": "string" } },
    "next_steps": { "type": "array", "items": { "type": "string" } }
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
  "session_summary": "Great work on Recursion! You mastered base cases but struggled with recursive step traces.",
  "achievements": ["Passed Recursion Assessment 1"],
  "weak_areas": ["Call stack tracing"],
  "next_steps": ["Practice Trees"]
}
```

---

# Validation Rules

1. Must contain evidence from context.
2. Must not hallucinate events that did not occur.

---

# Failure Cases

F1: Generic summary.
F2: Unsupported praise.
F3: Missing evidence.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with pruned context (remove tutor_sessions).
Tier 3: Return a deterministic summary template populated directly with raw metrics (e.g. "Completed 1 lesson, 2 quizzes. Mastery +0.1").
```

---

# Evaluation Metrics

Evidence Coverage: >95%
Summary Utility: >90%

---

# Prompt 13

# Progress Analyzer

Prompt Key

```text
progress_analyzer
```

---

# Purpose

Convert historical signals into actionable insights to drive Mastery Updates, Weak Concepts, Recommendations, and Curriculum Changes.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.0
max_retries: 2
timeout_seconds: 15
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "mastery_history": [],
  "retention_history": [],
  "error_history": [],
  "curriculum_progress": {}
}
```

---

# Inputs

```text
learner_id
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["learner_id"],
  "properties": {
    "learner_id": { "type": "string" }
  }
}
```

---

# Input Example

```json
{
  "learner_id": "u_999"
}
```

---

# Production Prompt

```text
You are LearnGraph's Progress Analysis Engine.

Analyze learner progress.

Use only evidence.

Identify:

- Trends
- Risks
- Improvements
- Recommendations

Return JSON only.
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
    "insights",
    "warnings",
    "recommendations"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "insights": { "type": "array", "items": { "type": "string" } },
    "warnings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "concept", "confidence"],
        "properties": {
          "type": { "type": "string" },
          "concept": { "type": "string" },
          "confidence": { "type": "number" }
        }
      }
    },
    "recommendations": { "type": "array", "items": { "type": "string" } }
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
  "insights": ["Mastery in Recursion is accelerating."],
  "warnings": [
    {
      "type": "retention_risk",
      "concept": "Arrays",
      "confidence": 0.88
    }
  ],
  "recommendations": ["Review Arrays next session."]
}
```

---

# Validation Rules

1. Warnings must map to valid tracked concepts.
2. Confidence must be between 0.0 and 1.0.

---

# Failure Cases

F1: Failing to identify clear retention drops.
F2: Hallucinating mastery increases.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry focusing only on retention_history.
Tier 3: Bypass LLM; rely strictly on mastery_engine.md deterministic updates to trigger curriculum changes.
```

---

# Evaluation Metrics

Trend Accuracy: >90%

---

# Prompt 14

# Recommendation Explainer

Prompt Key

```text
recommendation_explainer
```

---

# Purpose

Explain recommendations generated by curriculum engine. Transparency increases trust.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.3
max_retries: 2
timeout_seconds: 10
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "graph_state": {},
  "mastery": {},
  "retention": {},
  "misconceptions": []
}
```

---

# Inputs

```text
recommended_concept
dependency_depth
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["recommended_concept"],
  "properties": {
    "recommended_concept": { "type": "string" },
    "dependency_depth": { "type": "integer" }
  }
}
```

---

# Input Example

```json
{
  "recommended_concept": "Trees",
  "dependency_depth": 2
}
```

---

# Production Prompt

```text
You are LearnGraph's Recommendation Explanation Engine.

Explain recommendations.

Rules:

1. Use evidence.
2. Mention mastery.
3. Mention dependencies.
4. Mention misconceptions.
5. Be concise.
6. Return JSON only.
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
    "explanation"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "concept": { "type": "string" },
    "explanation": { "type": "string" }
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
  "concept": "Trees",
  "explanation": "Trees is recommended because you have mastered its prerequisite, Recursion, and you are ready for a new topic."
}
```

---

# Validation Rules

1. Every explanation requires Evidence, Dependency context, and Recommendation Reason.

---

# Failure Cases

F1: Unsupported explanations.
F2: Hallucinated dependencies.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with empty misconceptions context.
Tier 3: Generate deterministic explanation string from mastery + prerequisite graph.
```

---

# Evaluation Metrics

Trust Score: >90%

---

# Prompt 15

# Memory Summarizer

Prompt Key

```text
memory_summarizer
```

---

# Purpose

Convert large learner history into compact long-term memory. Store patterns, not events.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.2
max_retries: 2
timeout_seconds: 25
schema_version: 1.0.0
```

---

# Context Retrieval

```json
{
  "sessions": [],
  "assessments": [],
  "lessons": [],
  "errors": [],
  "progress_history": []
}
```

---

# Inputs

```text
learner_id
current_memory_state
```

---

# Input Schema

```json
{
  "type": "object",
  "required": ["learner_id"],
  "properties": {
    "learner_id": { "type": "string" },
    "current_memory_state": { "type": "string" }
  }
}
```

---

# Input Example

```json
{
  "learner_id": "u_999",
  "current_memory_state": "Learner prefers visual explanations."
}
```

---

# Production Prompt

```text
You are LearnGraph's Memory Summarization Engine.

Your task:

Compress learner history into durable educational memory.

Rules:

1. Store patterns, not events.
2. Use evidence.
3. Avoid temporary observations.
4. Avoid unsupported traits.
5. Keep memory compact.
6. Return JSON only.

History:
{{history}}
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
    "learning_preferences",
    "persistent_strengths",
    "persistent_weaknesses",
    "repeated_misconceptions",
    "effective_teaching_patterns",
    "memory_summary"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "learning_preferences": { "type": "array", "items": { "type": "string" } },
    "persistent_strengths": { "type": "array", "items": { "type": "string" } },
    "persistent_weaknesses": { "type": "array", "items": { "type": "string" } },
    "repeated_misconceptions": { "type": "array", "items": { "type": "string" } },
    "effective_teaching_patterns": { "type": "array", "items": { "type": "string" } },
    "memory_summary": { "type": "string" }
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
  "learning_preferences": ["Visual diagrams"],
  "persistent_strengths": ["Algorithmic logic"],
  "persistent_weaknesses": ["Pointer tracking"],
  "repeated_misconceptions": ["off_by_one"],
  "effective_teaching_patterns": ["Step-by-step memory trace diagrams"],
  "memory_summary": "Responds well to visual memory mapping. Struggles with edge cases."
}
```

---

# Validation Rules

1. No psychological profiling.
2. No IQ estimation.

---

# Failure Cases

F1: Memory bloat (storing events).
F2: Unsupported traits.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with reduced context (only last 3 sessions).
Tier 3: Append raw events to an uncompressed history log until summarizer recovers.
```

---

# Evaluation Metrics

Memory Utility: >90%
Memory Compression Ratio: >95%