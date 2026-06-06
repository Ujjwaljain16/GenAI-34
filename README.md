# LearnGraph AI

**LearnGraph AI** is an AI-powered adaptive learning intelligence platform that creates personalized Data Structures & Algorithms (DSA) learning journeys. Instead of providing static content, it dynamically models a learner's mastery, retention, and misconceptions to continuously generate customized curricula, lessons, and tutoring experiences.

> *The core innovation is not content generation. The core innovation is persistent learner modeling.*

## Features

- **Adaptive Diagnostic Assessment**: Dynamically assesses baseline knowledge and generates a personalized **Learning DNA Report**.
- **Knowledge Graph Engine (Neo4j)**: Represents 19 core DSA concepts, prerequisite dependencies, and continuous learner topological states.
- **Socratic AI Tutor**: Gemini 2.5 Flash-powered tutor that provides structured hint levels (1-4) without simply giving away the answer, remembering past errors across sessions.
- **Dynamic Curriculum Generation**: Continually replans learning paths based on demonstrated mastery and concept prerequisites.
- **Persistent Learner Model**: Tracks mastery (0.0 to 1.0), retention decay, Bloom's taxonomy targets, and specific categorized misconceptions.

## Tech Stack

The architecture follows a modular monolith approach utilizing:

- **Frontend**: Next.js 15, React, TypeScript, TailwindCSS, shadcn/ui, Zustand
- **Backend API**: FastAPI (Python), Pydantic v2
- **Relational Database**: PostgreSQL (Stores users, assessments, mastery, memory, learning history)
- **Knowledge Graph**: Neo4j (Stores concepts, prerequisites, recommendations, traversals)
- **AI / LLM**: Gemini 2.5 Flash

## Repository Structure

```text
├── .env.example          # Environment variables template
├── AGENT.md              # Single source of truth & architecture constraints
├── README.md             # You are here
├── backend/              
│   ├── api/              # FastAPI route definitions & OpenAPI specs
│   └── db/               # PostgreSQL schema & Neo4j cypher queries
├── promptLib/            # Version-controlled Gemini prompt specifications
└── techdoc/              # Technical Requirements Documents (TRD) & Architecture
```

## System Requirements

To run this platform locally, you will need:
- Docker and Docker Compose
- Node.js (v18+)
- Python (3.10+)
- Gemini API Key

## Local Startup (Docker Compose)

> **⚠️ STRICTLY FOR LOCAL DEVELOPMENT**
> The included `docker-compose.yml` is to ensure all 5 students have an identical, one-click environment without having to manually install PostgreSQL and Neo4j on their laptops. 

1. Copy `.env.example` to `.env` and fill in your keys (including `GEMINI_API_KEY`).
2. Run `docker-compose up -d`. This will start:
   - PostgreSQL (Port 5432)
   - Neo4j (Ports 7474 / 7687)
   - FastAPI Backend (Port 8000)
   - Next.js Frontend (Port 3000)

## Free Deployment Strategy (No Docker Required)

For the live demo, do **not** attempt to host the Docker containers. Instead, use the following free managed services:
- **Frontend:** Vercel (Free)
- **Backend:** Render or Railway (Free tier)
- **Relational DB:** Supabase or Neon (Free tier Postgres)
- **Graph DB:** Neo4j AuraDB (Free tier)

Simply point the environment variables on Render/Vercel to the managed database URLs.

## Architecture & Contribution Guidelines

All contributors must strictly adhere to the rules outlined in **[AGENT.md](./AGENT.md)**.
- **Document Precedence:** `schema.sql` > `openapi.yaml` > `core_queries.cypher` > `mastery_engine.md` > `AGENT.md`.
- No direct mutations to the database schema in production; all changes require migrations.
- The AI never decides system state (Neo4j and Postgres own state).
- All AI prompts are versioned and stored in `/promptLib`.

---

