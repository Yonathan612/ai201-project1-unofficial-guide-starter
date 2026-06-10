# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Student-generated professor reviews and course advice.

Official university sites list courses and faculty, but not teaching style, workload, exam difficulty, or feedback quality. This system answers questions like "Which professor is best for beginners?" using review-style documents in `documents/`.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Professor Anderson — CS 101 | Local text file | `documents/professor_anderson_cs101.txt` |
| 2 | Professor Bennett — CS 201 | Local text file | `documents/professor_bennett_cs201.txt` |
| 3 | Professor Chang — CS 310 | Local text file | `documents/professor_chang_cs310.txt` |
| 4 | Professor Davis — MATH 220 | Local text file | `documents/professor_davis_math220.txt` |
| 5 | Professor Evans — CS 330 | Local text file | `documents/professor_evans_cs330.txt` |
| 6 | Professor Foster — CS 250 | Local text file | `documents/professor_foster_cs250.txt` |
| 7 | Professor Garcia — CS 320 | Local text file | `documents/professor_garcia_cs320.txt` |
| 8 | Professor Harris — CS 340 | Local text file | `documents/professor_harris_cs340.txt` |
| 9 | Professor Ivanov — MATH 160 | Local text file | `documents/professor_ivanov_math160.txt` |
| 10 | Professor Jackson — CS 350 | Local text file | `documents/professor_jackson_cs350.txt` |

Sources were modeled after Rate My Professor reviews, Reddit course-advice threads, and informal student comments.

---

## Chunking Strategy

**Chunk size:** One paragraph per chunk (~100–250 characters)

**Overlap:** No character overlap; professor/course title prepended to each non-title chunk

**Why these choices fit your documents:** Each review is ~1,000 characters with 5 topical paragraphs (workload, exams, feedback, advice). Paragraph chunks are self-contained. Fixed 500-char windows would yield only ~30 chunks and risk mid-sentence cuts.

**Preprocessing:** Normalize line endings and whitespace via `clean_text()` in `ingest.py`. No HTML stripping needed for plain `.txt` files.

**Final chunk count:** 60 (6 chunks × 10 documents)

### Sample Chunks

**Chunk 1** — `professor_anderson_cs101.txt` (chunk 1)
> Professor Anderson - CS 101: Introduction to Computer Science
>
> Students describe Professor Anderson as patient, organized, and beginner-friendly. Reviews consistently say that he explains programming concepts slowly and gives many examples during class.

**Chunk 2** — `professor_bennett_cs201.txt` (chunk 2)
> Professor Bennett - CS 201: Data Structures
>
> The workload is heavy. Programming projects can take six to ten hours, especially projects involving linked lists, trees, recursion, and hash tables.

**Chunk 3** — `professor_chang_cs310.txt` (chunk 4)
> Professor Chang - CS 310: Database Systems
>
> Professor Chang gives detailed feedback on database design projects. Students like that she explains why a schema is flawed instead of only marking it wrong.

**Chunk 4** — `professor_evans_cs330.txt` (chunk 2)
> Professor Evans - CS 330: Software Engineering
>
> The workload is project-based. Students say the course is not difficult conceptually, but group coordination and deadlines can become stressful.

**Chunk 5** — `professor_jackson_cs350.txt` (chunk 5)
> Professor Jackson - CS 350: Computer Networks
>
> Best advice from students: learn the OSI and TCP/IP models early, practice explaining packet flow, and review old labs before exams.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (local, free, no API key)

**Production tradeoff reflection:** For a real deployment I would weigh API cost vs local compute, max sequence length for long forum threads, multilingual embeddings for international students, and domain-specific models for academic jargon. MiniLM balances speed, size, and quality for short English reviews in this prototype.

### Retrieval Test Results

Run: `python test_retrieval.py`

**Query 1:** "Which professor is best for a beginner in programming?"
- Top hit: `professor_anderson_cs101.txt` (distance: 0.42) — "patient, organized, and beginner-friendly"
- **Why relevant:** Directly describes Anderson as ideal for new coders.

**Query 2:** "Which course has the heaviest programming project workload?"
- Top hit: `professor_bennett_cs201.txt` (distance: 0.38) — "projects can take six to ten hours"
- **Why relevant:** Bennett chunk explicitly states the heaviest hour estimate.

**Query 3:** "What should students do to prepare for Computer Networks exams?"
- Top hit: `professor_jackson_cs350.txt` (distance: 0.21) — OSI/TCP/IP models and packet flow
- **Why relevant:** Lowest distance score; chunk contains exact exam prep advice.

---

## Grounded Generation

**System prompt grounding instruction:**

```
Answer the question using ONLY the information in the provided context documents.
Do NOT use outside knowledge or guess.
If the context does not contain enough information to answer, respond with exactly:
"I don't have enough information on that."
When you use information from a source, mention the professor or course and reference the source filename.
```

Implemented in `rag.py` `generate_answer()`. Temperature set to 0.1 to reduce hallucination.

**How source attribution is surfaced in the response:**

1. The prompt instructs the LLM to cite source filenames in its answer.
2. The Gradio UI (`app.py`) programmatically lists all retrieved source files in a separate "Retrieved from" field — not left to the LLM alone.

### Example Responses

**In-scope (with citation):**
```
Question: Which professor is best for a beginner in programming?

Answer: According to professor_anderson_cs101.txt, Professor Anderson is described
as patient, organized, and beginner-friendly, and his lectures make Python less
intimidating for students who are new to coding.

Retrieved from:
• professor_anderson_cs101.txt
• professor_evans_cs330.txt
• professor_foster_cs250.txt
```

**Out-of-scope (refusal):**
```
Question: Which professor is best for machine learning?

Answer: I don't have enough information on that.

Retrieved from:
• professor_bennett_cs201.txt
• professor_foster_cs250.txt
• professor_harris_cs340.txt
• professor_jackson_cs350.txt
```

### Query Interface

**Input:** Text question box labeled "Your question"

**Output:** "Answer" text box + "Retrieved from" source list

**How to run:** `python app.py` → open http://localhost:7860

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which professor is best for a beginner in programming? | Professor Anderson — patient, beginner-friendly | Anderson is best; described as patient, organized, beginner-friendly (professor_anderson_cs101.txt) | Relevant | Accurate |
| 2 | Which course has the heaviest programming project workload? | Bennett CS 201 — 6–10 hour projects | Bennett CS 201; projects take six to ten hours (professor_bennett_cs201.txt) | Relevant | Accurate |
| 3 | Which professor gives detailed feedback on database design projects? | Professor Chang — explains schema flaws | Chang gives detailed feedback on database design projects (professor_chang_cs310.txt) | Relevant | Accurate |
| 4 | Which course is most dependent on group coordination? | Evans CS 330 — group coordination stressful | Evans CS 330; group coordination can become stressful (professor_evans_cs330.txt) | Relevant | Accurate |
| 5 | What should students do to prepare for Computer Networks exams? | Jackson — OSI/TCP/IP, packet flow, protocols | Learn OSI/TCP/IP models, practice explaining protocols (professor_jackson_cs350.txt) | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Which professor is best for machine learning?

**What the system returned:** "I don't have enough information on that." Retrieved unrelated sources: professor_bennett_cs201.txt, professor_foster_cs250.txt, professor_harris_cs340.txt, professor_jackson_cs350.txt (distances 0.55–0.59).

**Root cause (tied to a specific pipeline stage):** Retrieval coverage limitation at the document collection stage. No document in `documents/` mentions machine learning. Semantic search still returns the four "closest" embeddings, but they are weak, off-topic matches. The grounding prompt in the generation stage correctly refuses to answer rather than hallucinate.

**What you would change to fix it:** Add machine learning course reviews to the corpus (e.g., a CS 480 ML professor review). Alternatively, add a retrieval confidence threshold that refuses to answer when all distance scores exceed 0.5.

---

## Spec Reflection

**One way the spec helped you during implementation:**

Writing chunking and retrieval decisions in `planning.md` before coding led directly to paragraph chunking (60 chunks) instead of naive 500-character splits (~30 chunks). The evaluation plan gave five concrete test queries I could run through retrieval before wiring up generation, which caught the documents-vs-docs folder naming issue early.

**One way your implementation diverged from the spec, and why:**

My original notes specified 500-character chunks with 100-character overlap. After reading the documents (~1,000 characters each, organized by paragraph), I switched to paragraph-based chunking because it produced more natural, self-contained chunks and hit the recommended ~60-chunk count.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* My `planning.md` Chunking Strategy, Documents, and Architecture sections; assignment requirements for Milestone 3.
- *What it produced:* `ingest.py` with `load_documents()`, `clean_text()`, and paragraph-based `chunk_documents()`.
- *What I changed or overrode:* Updated `DOCS_DIR` from `docs` to `documents` to match the starter repo folder name. Verified 60 chunks before moving to embedding.

**Instance 2**

- *What I gave the AI:* Retrieval Approach section, grounding requirements, and Gradio skeleton from the assignment.
- *What it produced:* `rag.py` with ChromaDB indexing, `retrieve()`, Groq `generate_answer()`, and `app.py` Gradio interface.
- *What I changed or overrode:* Added try/except in `app.py` so missing API key shows a readable error instead of a Gradio crash. Tested all 5 evaluation questions and the ML failure case before documenting results in this README.
