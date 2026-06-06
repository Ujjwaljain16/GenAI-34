# Lexis AI

# Prompt Evaluation & Observability Specification (PEOS)

Version: 1.0

Status: Production

Purpose:

Define how Lexis evaluates, monitors, validates, audits, improves, and safely deploys prompt-based educational systems.

A production AI learning platform is not measured by prompt quality.

It is measured by:

```text
Educational Outcomes
      +
Consistency
      +
Reliability
      +
Observability
      +
Improvement Velocity
```

---

# 1. Evaluation Philosophy

Most AI systems evaluate:

```text
Prompt
   â†“
Output
```

Lexis evaluates:

```text
Learner
   â†“
Interaction
   â†“
Learning Outcome
```

Therefore evaluation occurs at 4 levels:

```text
Level 1
Output Quality

Level 2
Educational Quality

Level 3
Personalization Quality

Level 4
Learning Outcome Quality
```

---

# 2. Evaluation Architecture

```text
Prompt Run
     â”‚
     â–¼

Schema Validation
     â”‚
     â–¼

Automated Evaluation
     â”‚
     â–¼

LLM Evaluation
     â”‚
     â–¼

Human Evaluation
     â”‚
     â–¼

Metrics Store
     â”‚
     â–¼

Dashboard
```

---

# 3. Evaluation Categories

Every prompt belongs to one or more categories.

| Category      | Examples             |
| ------------- | -------------------- |
| Generation    | Lessons, Questions   |
| Evaluation    | Assessment Evaluator |
| Diagnostic    | Learning DNA         |
| Tutoring      | Socratic Tutor       |
| Planning      | Curriculum Generator |
| Summarization | Session Summary      |
| Memory        | Memory Summarizer    |

Each category receives different metrics.

---

# 4. Golden Dataset Framework

Every prompt must be evaluated on a fixed benchmark.

Purpose:

Prevent regression.

---

## Golden Dataset Structure

```json
{
  "dataset_id":"assessment_v1",
  "samples":[]
}
```

---

Dataset Types:

### Assessment Dataset

Contains:

```text
Concept
Difficulty
Bloom
Gold Question
```

---

### Evaluation Dataset

Contains:

```text
Question
Expected Answer
Student Answer
Human Grade
```

---

### Misconception Dataset

Contains:

```text
Answer
Reasoning
Known Misconceptions
```

---

### Curriculum Dataset

Contains:

```text
Learner State
Expected Priorities
```

---

### Tutor Dataset

Contains:

```text
Conversation
Expected Tutor Behavior
```

---

# 5. Offline Evaluation Framework

Purpose:

Evaluate before deployment.

---

Pipeline:

```text
Prompt Version
      â”‚
      â–¼

Benchmark Dataset

      â”‚
      â–¼

Automated Scoring

      â”‚
      â–¼

LLM Judging

      â”‚
      â–¼

Human Review
```

---

Deployment cannot occur without passing offline evaluation.

---

# 6. Automated Evaluation

Level 1 evaluation.

Checks:

```text
Schema Validity

JSON Validity

Required Fields

Token Limits

Constraint Violations
```

---

Metrics:

```text
Schema Pass Rate

JSON Pass Rate

Retry Rate
```

Targets:

```text
Schema Pass Rate > 99%

Retry Rate < 2%
```

---

# 7. Educational Evaluation Framework

Educational quality is measured separately.

---

Dimensions:

### Correctness

Is information accurate?

---

### Clarity

Can learners understand it?

---

### Bloom Alignment

Does difficulty match intended Bloom level?

---

### Pedagogical Quality

Is instruction educationally sound?

---

### Misconception Coverage

Are known misconceptions addressed?

---

# Educational Scoring Rubric

Scale:

```text
1-5
```

---

Score 1

Poor

---

Score 3

Acceptable

---

Score 5

Excellent

---

Deployment Threshold:

```text
Average > 4.2
```

---

# 8. Personalization Evaluation

Lexis's key differentiator.

---

Question:

Would two different learners receive meaningfully different outputs?

---

Inputs:

```text
Learner A

Mastery = 0.25
```

vs

```text
Learner B

Mastery = 0.85
```

---

Expected:

Different:

```text
Lesson Depth

Examples

Difficulty

Hints

Recommendations
```

---

Metric:

Personalization Delta Score

Measures output divergence.

---

Target:

```text
>0.75
```

---

# 9. Assessment Generator Evaluation

Metrics:

---

Difficulty Accuracy

```text
Target >95%
```

---

Bloom Accuracy

```text
Target >95%
```

---

Concept Purity

```text
Target >98%
```

---

Question Diversity

```text
Target >90%
```

---

Hallucinated Concepts

```text
Target = 0%
```

---

# 10. Assessment Evaluator Evaluation

Metrics:

---

Human Agreement

```text
Target >90%
```

---

Score Correlation

```text
Target >0.85
```

---

Misconception Detection Precision

```text
Target >85%
```

---

Misconception Detection Recall

```text
Target >80%
```

---

# 11. Curriculum Evaluation

Metrics:

---

Dependency Compliance

```text
Target 100%
```

---

Recommendation Relevance

```text
Target >90%
```

---

Expert Curriculum Similarity

```text
Target >85%
```

---

Hallucinated Concepts

```text
Target 0%
```

---

# 12. Lesson Evaluation

Metrics:

---

Concept Accuracy

```text
Target >95%
```

---

Example Quality

```text
Target >90%
```

---

Misconception Coverage

```text
Target >95%
```

---

Lesson Completeness

Required:

```text
Introduction

Mental Model

Example

Exercise

Summary
```

---

# 13. Tutor Evaluation Framework

Most important evaluation.

---

Dimensions:

### Guidance Quality

Does tutor help thinking?

---

### Answer Leakage

Does tutor reveal solution?

---

### Misconception Repair

Does learner improve?

---

### Productive Struggle

Does learner reason?

---

### Learning Gain

Does mastery increase?

---

# Tutor Leakage Metric

Compute:

```text
Similarity(
Tutor Response,
Correct Solution
)
```

---

Target:

```text
<0.20
```

before hint level 4.

---

# Tutor Success Metric

```text
Mastery_after

-

Mastery_before
```

---

Target:

```text
+20%
```

average improvement.

---

# 14. Hint Evaluation

Metrics:

---

Progressive Disclosure

Level N should reveal more than Level N-1.

---

Leakage Rate

```text
<1%
```

---

Misconception Targeting

```text
>90%
```

---

# 15. Learning DNA Evaluation

Metrics:

---

Evidence Coverage

```text
>95%
```

---

Recommendation Quality

```text
>90%
```

---

Unsupported Claims

```text
0%
```

---

# 16. Memory Evaluation

Purpose:

Ensure memory remains useful.

---

Metrics:

### Stability

Memory should not fluctuate excessively.

Target:

```text
>85%
```

---

### Utility

Does memory improve future prompts?

Target:

```text
>90%
```

---

### Compression

Target:

```text
1000 tokens max
```

---

# 17. LLM-as-a-Judge Framework

Human review does not scale.

Use secondary evaluation model.

---

Judge Prompt Categories

```text
Educational Quality

Tutor Quality

Lesson Quality

Explanation Quality
```

---

Judge Output

```json
{
  "score":4.5,
  "reason":"..."
}
```

---

Never use judge alone.

Combine:

```text
Automated

+

LLM Judge

+

Human Review
```

---

# 18. Human Evaluation Framework

Reviewers:

```text
Learning Scientist

DSA Expert

Prompt Engineer
```

---

Review Dimensions

```text
Correctness

Pedagogy

Personalization

Safety
```

---

Review Scale

```text
1-5
```

---

Minimum Passing Score

```text
4.2
```

---

# 19. Online Evaluation Framework

Production monitoring.

---

Metrics:

### Engagement

```text
Lesson Completion

Quiz Completion

Session Duration
```

---

### Learning

```text
Mastery Gain

Retention Gain
```

---

### Tutor

```text
Hint Requests

Tutor Satisfaction

Question Resolution
```

---

# 20. A/B Testing Framework

Used for:

```text
Prompt Versions

Hint Strategies

Tutor Strategies

Lesson Structures
```

---

Traffic Split

```text
50/50
```

Default.

---

Success Metrics

```text
Learning Gain

Completion Rate

Retention Improvement
```

---

Winner Selection

Must outperform baseline by:

```text
â‰¥10%
```

with statistical significance.

---

# 21. Prompt Regression Testing

Every prompt update triggers:

---

Schema Tests

---

Educational Tests

---

Golden Dataset Tests

---

Prompt Contract Tests

---

Safety Tests

---

# Regression Suite Example

```text
assessment_v1

assessment_v2

tutor_v1

lesson_v1

memory_v1
```

---

# 22. Deployment Quality Gates

Prompt cannot deploy unless:

---

Schema Pass Rate

```text
>99%
```

---

Educational Score

```text
>4.2
```

---

Hallucination Rate

```text
<1%
```

---

Tutor Leakage

```text
<1%
```

---

Dependency Compliance

```text
100%
```

---

# 23. Production Monitoring

Track:

---

Latency

---

Tokens

---

Cost

---

Retries

---

Validation Failures

---

Educational Scores

---

Stored in:

```sql
CREATE TABLE prompt_metrics (
    id UUID PRIMARY KEY,
    prompt_version_id UUID,
    runs INT,
    failures INT,
    avg_latency_ms INT,
    avg_tokens INT,
    educational_score FLOAT
);
```

---

# 24. Alerting Framework

Critical Alerts:

---

Schema Failure Spike

Threshold:

```text
>5%
```

---

Hallucination Spike

Threshold:

```text
>1%
```

---

Tutor Leakage

Threshold:

```text
>0.5%
```

---

Latency Spike

Threshold:

```text
>30%
```

increase.

---

# 25. Rollback Framework

Automatic rollback when:

```text
Failure Rate >5%

Hallucination >1%

Educational Score <4.0

Tutor Leakage >1%
```

---

Rollback Target:

```text
Previous Stable Version
```

---

# 26. Continuous Improvement Loop

```text
Prompt Runs
      â”‚
      â–¼

Evaluation

      â”‚
      â–¼

Failures

      â”‚
      â–¼

Analysis

      â”‚
      â–¼

Prompt Revision

      â”‚
      â–¼

Offline Testing

      â”‚
      â–¼

Canary

      â”‚
      â–¼

Production
```

---

# 27. Lexis Production Readiness Checklist

Every Prompt Must Have:

* Purpose
* Input Schema
* Output Schema
* Validation Rules
* Educational Validators
* Failure Modes
* Mitigation Strategy
* Offline Benchmark
* Online Metrics
* Deployment Gates
* Rollback Policy
* Observability Hooks

---

# 28. Final Lexis Prompt System Inventory

### Assessment Layer

* Assessment Generator
* Assessment Evaluator

---

### Diagnostic Layer

* Misconception Detector
* Learning DNA Generator

---

### Planning Layer

* Curriculum Generator
* Curriculum Replanner

---

### Learning Layer

* Lesson Generator
* Exercise Generator
* Quiz Generator

---

### Tutoring Layer

* Socratic Tutor
* Hint Generator

---

### Reflection Layer

* Session Summarizer
* Progress Analyzer
* Recommendation Explainer

---

### Memory Layer

* Memory Summarizer

---

### Infrastructure Layer

* Prompt Runtime
* Validation Engine
* Guardrails
* Evaluation Framework
* Observability Framework
* Versioning System
* Rollback System

---
