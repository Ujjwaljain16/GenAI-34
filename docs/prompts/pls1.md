# Lexis AI

# Prompt Library Specification (PLS)

# Part 1

Covered Components:

1. Assessment Question Generator
2. Assessment Evaluator
3. Misconception Detector
4. Learning DNA Generator

---

# Prompt 01

# Assessment Question Generator

Prompt Key

```text
assessment_question_generator
```

---

# Purpose

Generate adaptive assessment questions that measure learner understanding while maintaining alignment with:

* Concept Graph
* Difficulty Targets
* Bloom Levels
* Learner Mastery

The objective is diagnosis, not teaching.

Questions should reveal understanding gaps.

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
  "concept": {},
  "mastery": {},
  "retention": {},
  "misconceptions": [],
  "assessment_history": {},
  "difficulty_distribution": {}
}
```

---

# Inputs

```text
concept_id
concept_name
difficulty
bloom_level
question_type
target_misconceptions
```

---

# Input Schema

```json
{
  "type": "object",
  "required": [
    "concept_name",
    "difficulty",
    "bloom_level",
    "question_type"
  ],
  "properties": {
    "concept_id": {
      "type": "string",
      "format": "uuid"
    },
    "concept_name": {
      "type": "string"
    },
    "difficulty": {
      "type": "string",
      "enum": ["beginner", "intermediate", "advanced"]
    },
    "bloom_level": {
      "type": "string",
      "enum": ["remember", "understand", "apply", "analyze"]
    },
    "question_type": {
      "type": "string",
      "enum": ["mcq", "short_answer", "code_trace", "conceptual"]
    },
    "target_misconceptions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

---

# Input Example

```json
{
  "concept_id": "c_12345",
  "concept_name": "Recursion",
  "difficulty": "beginner",
  "bloom_level": "understand",
  "question_type": "short_answer",
  "target_misconceptions": ["base_case_confusion"]
}
```

---

# Difficulty Rubric

Beginner: Definition Recall, Basic Understanding, Single Concept
Intermediate: Application, Simple Reasoning, 2-Step Thinking
Advanced: Analysis, Tradeoffs, Edge Cases, Multi-Step Reasoning

---

# Bloom Rubric

Remember: Recall facts
Understand: Explain concept
Apply: Use concept
Analyze: Reason about behavior

---

# Production Prompt

```text
You are Lexis's Assessment Generation Engine.

Objective:

Generate ONE assessment question.

Rules:

1. Use ONLY the provided concept.
2. Do NOT teach.
3. Do NOT provide extra explanation.
4. Difficulty must strictly match requested difficulty.
5. Bloom level must strictly match requested bloom level.
6. Question must diagnose understanding.
7. Avoid ambiguity.
8. Avoid trivia.
9. Target misconceptions when supplied.
10. Return valid JSON only.

Concept:
{{concept_name}}

Difficulty:
{{difficulty}}

Bloom Level:
{{bloom_level}}

Known Misconceptions:
{{target_misconceptions}}

Generate:

- Question
- Expected Answer
- Hints
- Explanation
- Difficulty
- Bloom Level

Return JSON matching schema.
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
    "question",
    "expected_answer",
    "difficulty",
    "bloom_level",
    "hints",
    "explanation"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "question": { "type": "string" },
    "expected_answer": { "type": "string" },
    "difficulty": { "type": "string" },
    "bloom_level": { "type": "string" },
    "hints": {
      "type": "array",
      "items": { "type": "string" }
    },
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
  "question": "Identify the base case in this recursive function.",
  "expected_answer": "if n <= 1: return n",
  "difficulty": "beginner",
  "bloom_level": "understand",
  "hints": ["Look for the condition that returns without calling itself."],
  "explanation": "A base case stops the recursion from continuing indefinitely."
}
```

---

# Validation Rules

1. Difficulty Validator: Checks generated difficulty matches request.
2. Bloom Validator: Checks question taxonomy.
3. Concept Validator: Question must belong to supplied concept.

---

# Failure Cases

F1: Difficulty drift.
F2: Bloom mismatch.
F3: Concept leakage.
F4: Multiple concepts introduced.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with reduced context (remove target_misconceptions).
Tier 3: Fallback to pre-authored diagnostic question from concepts.json.
```

---

# Evaluation Metrics

Difficulty Accuracy: >95%
Bloom Accuracy: >95%
Concept Purity: >98%
Question Diversity: >90%

---

# Prompt 02

# Assessment Evaluator

Prompt Key

```text
assessment_evaluator
```

---

# Purpose

Evaluate learner responses. Produces educational signals, not just grading.
Must estimate: correctness, understanding, bloom achievement.

---

# Runtime Config

```yaml
model: gemini-2.5-flash
temperature: 0.1
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
  "misconceptions": {},
  "previous_attempts": {}
}
```

---

# Inputs

```text
question
expected_answer
student_answer
student_reasoning
```

---

# Input Schema

```json
{
  "type": "object",
  "required": [
    "question",
    "expected_answer",
    "student_answer"
  ],
  "properties": {
    "question": { "type": "string" },
    "expected_answer": { "type": "string" },
    "student_answer": { "type": "string" },
    "student_reasoning": { "type": "string" }
  }
}
```

---

# Input Example

```json
{
  "question": "What is the time complexity of quicksort in the worst case?",
  "expected_answer": "O(n^2)",
  "student_answer": "O(n log n)",
  "student_reasoning": "Because it uses divide and conquer."
}
```

---

# Production Prompt

```text
You are Lexis's Assessment Evaluation Engine.

Evaluate the learner response.

Rules:

1. Compare meaning, not wording.
2. Accept equivalent explanations.
3. Detect partial understanding.
4. Detect misconceptions.
5. Detect guessing.
6. Produce educational feedback.
7. Return JSON only.

Question:
{{question}}

Expected Answer:
{{expected_answer}}

Student Answer:
{{student_answer}}

Student Reasoning:
{{student_reasoning}}

Output:
- Correctness
- Score
- Bloom Achievement
- Understanding Level
- Misconceptions
- Feedback
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
    "correctness",
    "score",
    "bloom_achievement",
    "understanding_level",
    "misconceptions",
    "feedback"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "correctness": { "type": "string", "enum": ["correct", "incorrect", "partial"] },
    "score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "bloom_achievement": { "type": "string" },
    "understanding_level": { "type": "string", "enum": ["full", "partial", "weak", "none"] },
    "misconceptions": {
      "type": "array",
      "items": { "type": "string" }
    },
    "feedback": { "type": "string" }
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
  "correctness": "incorrect",
  "score": 0.0,
  "bloom_achievement": "remember",
  "understanding_level": "weak",
  "misconceptions": ["average_vs_worst_case_confusion"],
  "feedback": "O(n log n) is the average case. Think about what happens if the pivot is always the smallest element."
}
```

---

# Validation Rules

1. Score must be between 0.0 and 1.0.
2. Bloom achievement must belong to valid taxonomy.

---

# Failure Cases

F1: Keyword matching bias.
F2: Punishing alternate wording.
F3: Ignoring reasoning.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with simplified context (remove student_reasoning).
Tier 3: Deterministic fallback (exact match on expected_answer -> 1.0, else 0.0).
```

---

# Evaluation Metrics

Agreement with Human Graders: >90%
Misconception Precision: >85%
Score Stability: >95%

---

# Prompt 03

# Misconception Detector

Prompt Key

```text
misconception_detector
```

---

# Purpose

Convert learner mistakes into structured taxonomy.
Critical component for Tutor, Curriculum, DNA, and Recommendations.

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
  "concept_taxonomy": {},
  "error_history": {},
  "assessment_history": {}
}
```

---

# Inputs

```text
concept
question
expected_answer
student_answer
reasoning
```

---

# Input Schema

```json
{
  "type": "object",
  "required": [
    "concept",
    "question",
    "expected_answer",
    "student_answer"
  ],
  "properties": {
    "concept": { "type": "string" },
    "question": { "type": "string" },
    "expected_answer": { "type": "string" },
    "student_answer": { "type": "string" },
    "reasoning": { "type": "string" }
  }
}
```

---

# Input Example

```json
{
  "concept": "Recursion",
  "question": "What happens if we forget a base case?",
  "expected_answer": "Stack overflow",
  "student_answer": "It loops back to the start",
  "reasoning": "Recursion is like a while loop."
}
```

---

# Production Prompt

```text
You are Lexis's Misconception Detection Engine.

Your task:

Map learner mistakes into known misconception categories.

Rules:

1. Use ONLY supplied taxonomy.
2. Never invent categories.
3. Return confidence scores.
4. Detect multiple misconceptions.
5. Explain evidence.
6. Return JSON only.

Concept:
{{concept}}

Taxonomy:
{{taxonomy}}

Question:
{{question}}

Expected Answer:
{{expected_answer}}

Student Answer:
{{student_answer}}

Reasoning:
{{reasoning}}
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
    "misconceptions"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "misconceptions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["category", "confidence", "evidence"],
        "properties": {
          "category": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
          "evidence": { "type": "string" }
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
  "misconceptions": [
    {
      "category": "loop_equivalence_confusion",
      "confidence": 0.95,
      "evidence": "Student equated recursion directly to a while loop."
    }
  ]
}
```

---

# Validation Rules

1. Category must exist in taxonomy.
2. Confidence range: 0.0 to 1.0.

---

# Failure Cases

F1: Hallucinated categories.
F2: Overclassification.
F3: Low evidence.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with empty reasoning (focus only on answer).
Tier 3: Fallback to "unknown_misconception" category to prevent pipeline block.
```

---

# Evaluation Metrics

Precision: >90%
Recall: >85%
Category Accuracy: >92%

---

# Prompt 04

# Learning DNA Generator

Prompt Key

```text
learning_dna_generator
```

---

# Purpose

Create a compact learner diagnosis that powers personalization for the Tutor, Curriculum Generator, and Replanner.

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
  "mastery": {},
  "retention": {},
  "misconceptions": [],
  "assessment_results": [],
  "learning_history": [],
  "confidence_survey": {}
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
    "learner_id": { "type": "string", "format": "uuid" }
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
You are Lexis's Learning DNA Engine.

Your task:

Create a learner diagnosis.

Rules:

1. Use only supplied evidence.
2. Never infer unsupported traits.
3. Focus on learning behavior.
4. Explain strengths.
5. Explain weaknesses.
6. Explain misconceptions.
7. Recommend focus areas.
8. Return JSON only.

Mastery:
{{mastery}}

Retention:
{{retention}}

Misconceptions:
{{misconceptions}}

Bloom Results:
{{bloom_results}}

Assessment Results:
{{assessment_results}}

Learning History:
{{learning_history}}

Confidence Survey:
{{confidence_survey}}
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
    "strengths",
    "weaknesses",
    "misconceptions",
    "learning_preferences",
    "confidence_profile",
    "recommended_focus_areas",
    "learning_path_explanation"
  ],
  "properties": {
    "schema_version": { "type": "string", "enum": ["1.0.0"] },
    "generated_at": { "type": "string", "format": "date-time" },
    "prompt_version": { "type": "string", "enum": ["v1"] },
    "strengths": { "type": "array", "items": { "type": "object" } },
    "weaknesses": { "type": "array", "items": { "type": "object" } },
    "misconceptions": { "type": "array", "items": { "type": "object" } },
    "learning_preferences": { "type": "array", "items": { "type": "object" } },
    "confidence_profile": { "type": "object" },
    "recommended_focus_areas": { "type": "array", "items": { "type": "object" } },
    "learning_path_explanation": { "type": "string" }
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
  "strengths": [
    { "area": "trees", "evidence": "mastery > 0.85" }
  ],
  "weaknesses": [
    { "area": "recursion", "evidence": "mastery < 0.45" }
  ],
  "misconceptions": [],
  "learning_preferences": [],
  "confidence_profile": {},
  "recommended_focus_areas": [],
  "learning_path_explanation": "Learner performs well on data structures but struggles with algorithmic flow."
}
```

---

# Validation Rules

1. Every recommendation must contain evidence.
2. No unsupported claims.
3. No psychological profiling.
4. No IQ assumptions.

---

# Failure Cases

F1: Hallucinated strengths.
F2: Unsupported recommendations.
F3: Trait inference.
F4: Non-evidence-based diagnosis.

---

# Mitigation

```text
Tier 1: Retry prompt.
Tier 2: Retry with pruned context (remove confidence survey and learning history).
Tier 3: Deterministic fallback (build DNA entirely based on mastery score bands without LLM).
```

---

# Evaluation Metrics

Evidence Coverage: >95%
Recommendation Relevance: >90%
Hallucination Rate: <1%
Diagnostic Consistency: >95%