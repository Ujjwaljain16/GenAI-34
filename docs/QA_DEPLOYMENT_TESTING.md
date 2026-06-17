# Lexis AI: QA & Deployment Testing Guide

This document outlines the workflows and API endpoints for testing the Lexis AI backend deployed on Hugging Face.

## 🔗 Environment Details

* **Live Base URL:** `https://ujjwaljain16-lexis-ai.hf.space`
* **Interactive Swagger UI:** `https://ujjwaljain16-lexis-ai.hf.space/docs`
* **Repository:** `https://github.com/Ujjwaljain16/GenAI-34`
* **Main Branch:** `main` (Auto-deploys to HF Spaces on push)

> [!NOTE]  
> If the API responds with a `503` or timeouts initially, the Hugging Face Space might be waking up from an idle state. Just wait ~30 seconds and try again.

---

## 🧪 Test Flow 1: Document Ingestion & Canonicalization

This flow tests the newly rebuilt **V2 Ingestion Pipeline**, which features FAISS vector retrieval, local `all-MiniLM-L6-v2` embeddings, and Ordinal Guardrails.

### 1. Upload a Document
* **Endpoint:** `POST /api/v1/books`
* **Body:**
  ```json
  {
    "title": "Physics 101",
    "description": "Introduction to Physics"
  }
  ```
* **Response:** Returns a `book_id`. Save this ID!

### 2. Upload File Content
* **Endpoint:** `POST /api/v1/books/{book_id}/upload`
* **Payload:** Multipart Form Data (`file`: upload a `.txt` or `.pdf` file).
* **Action:** This automatically kicks off the asynchronous ingestion background worker.

### 3. Monitor Ingestion Status
* **Endpoint:** `GET /api/v1/books/{book_id}/status`
* **What to watch for:** The `status` field will progress through:
  1. `CHUNKING`
  2. `EXTRACTING_CONCEPTS`
  3. `CANONICALIZING` (Watch here! This runs our new 4-layer FAISS + Gemini deduplication pipeline)
  4. `EXTRACTING_RELATIONSHIPS`
  5. `VALIDATING` -> `PUBLISHING` -> `COMPLETED`
* **Expected Result:** `status: COMPLETED` with populated `nodes_count` and `edges_count`.

---

## 🧪 Test Flow 2: Knowledge Graph Integrity

This flow verifies that our Ordinal Guardrails successfully prevented invalid merges (like merging "Newton's First Law" into "Newton's Second Law").

### 1. Fetch the Knowledge Graph
* **Endpoint:** `GET /api/v1/books/{book_id}/knowledge-graph`
* **What to watch for:**
  * Look at the returned `nodes`. Are distinct concepts properly separated? 
  * Are identical concepts (e.g., "Linear Reg" and "Linear Regression") correctly merged into one node?
  * Look at the `edges`. Do they represent logical prerequisite relationships?

---

## 🧪 Test Flow 3: Assessment & Learning DNA Generation

This flow tests the dynamic assessment engine and the structured Gemini output generation for personalized student profiles.

### 1. Start an Assessment
* **Endpoint:** `POST /api/v1/assessments`
* **Body:**
  ```json
  {
    "book_id": "<your_book_id>"
  }
  ```
* **Response:** Returns an `assessment_id` and the very first `question` object.

### 2. Submit Answers
* **Endpoint:** `POST /api/v1/assessments/{assessment_id}/responses`
* **Body:**
  ```json
  {
    "question_id": "<id_from_previous_response>",
    "answer": "This is my answer.",
    "confidence_level": 4,
    "response_time_seconds": 15
  }
  ```
* **Action:** Keep submitting responses for the questions provided in the `next_question` field.

### 3. Complete Assessment & Check DNA
* **Endpoint:** `POST /api/v1/assessments/{assessment_id}/complete`
* **What to watch for:**
  * The final response should return the **Learning DNA**. 
  * **Critical:** We recently patched a major Gemini SDK schema bug here. Verify that the response contains `strengths`, `weaknesses`, `misconceptions`, and `recommended_focus_areas` without throwing a 500 `extra_forbidden` error!

---

## 🐞 Local Debugging for Teammates

If you find a bug during deployment testing and need to fix it locally:

1. **Pull the latest code:**
   ```bash
   git pull origin main
   ```
2. **Set up your environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure API Keys:**
   Create a `.env` file in the `backend` directory and add your key:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```
4. **Run the API:**
   ```bash
   python start.py
   ```

When you are ready, commit and push your changes to GitHub `main`. Hugging Face will automatically sync and redeploy the changes!
