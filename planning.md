# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

My domain is student-generated professor reviews and course advice.

Official university resources provide course descriptions and faculty information, but they do not provide insight into teaching style, workload, exam difficulty, grading practices, or feedback quality. Student reviews help students make informed decisions when selecting courses.

---

## Documents

Local text files in `documents/` — each file is a synthesized student-review-style summary for one professor/course. Sources were modeled after Rate My Professor reviews, Reddit course-advice threads, and informal student comments.

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | professor_anderson_cs101.txt | Anderson — CS 101 Intro to CS | `documents/professor_anderson_cs101.txt` |
| 2 | professor_bennett_cs201.txt | Bennett — CS 201 Data Structures | `documents/professor_bennett_cs201.txt` |
| 3 | professor_chang_cs310.txt | Chang — CS 310 Database Systems | `documents/professor_chang_cs310.txt` |
| 4 | professor_davis_math220.txt | Davis — MATH 220 Calculus II | `documents/professor_davis_math220.txt` |
| 5 | professor_evans_cs330.txt | Evans — CS 330 Software Engineering | `documents/professor_evans_cs330.txt` |
| 6 | professor_foster_cs250.txt | Foster — CS 250 Computer Organization | `documents/professor_foster_cs250.txt` |
| 7 | professor_garcia_cs320.txt | Garcia — CS 320 Web Development | `documents/professor_garcia_cs320.txt` |
| 8 | professor_harris_cs340.txt | Harris — CS 340 Algorithms | `documents/professor_harris_cs340.txt` |
| 9 | professor_ivanov_math160.txt | Ivanov — MATH 160 Calculus I | `documents/professor_ivanov_math160.txt` |
| 10 | professor_jackson_cs350.txt | Jackson — CS 350 Computer Networks | `documents/professor_jackson_cs350.txt` |

Together these cover intro programming, data structures, databases, math, systems, algorithms, and networking.

---

## Chunking Strategy

**Method:** Paragraph-based splitting (split on blank lines)

**Chunk size:** One paragraph per chunk (~100–250 characters each)

**Overlap:** No character overlap; the professor/course title line is prepended to every non-title chunk for context

**Reasoning:** Each document is a short review (~1,000 characters) with a title plus 5 topical paragraphs. Paragraph chunking keeps each chunk as one complete, retrievable thought. Fixed 500-character splits would produce only ~30 chunks across 10 documents — below the recommended minimum — and could cut mid-sentence. Expected output: ~6 chunks per document × 10 documents = **60 chunks**.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key)

**Top-k:** 4

**Vector store:** ChromaDB (persistent, `./chroma`)

Semantic search matches queries to chunks by meaning, not exact keywords — e.g. "beginner-friendly professor" can match "patient, organized, and beginner-friendly."

**Production tradeoff reflection:** For a real deployment I would weigh embedding cost (API vs local), context length for longer forum threads, multilingual support for international students, and domain-specific fine-tuning for academic jargon.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which professor is best for a beginner in programming? | Professor Anderson — students describe him as patient, organized, beginner-friendly, and helpful for students new to coding. |
| 2 | Which course has the heaviest programming project workload? | Professor Bennett's CS 201 Data Structures — projects can take six to ten hours and require careful debugging. |
| 3 | Which professor gives detailed feedback on database design projects? | Professor Chang — she explains why a schema is flawed and gives detailed feedback. |
| 4 | Which course is most dependent on group coordination? | Professor Evans's CS 330 Software Engineering — workload is project-based and group coordination can become stressful. |
| 5 | What should students do to prepare for Computer Networks exams? | For Professor Jackson's CS 350 class: learn OSI/TCP/IP models, understand packet flow, and practice explaining protocols. |

**Out-of-scope test:** "Which professor is best for machine learning?" — corpus has no ML-specific content; system should refuse.

---

## Anticipated Challenges

1. **Short documents, limited coverage** — With only ~1,000 characters per professor, some nuanced questions may lack enough context in retrieved chunks. Mitigation: paragraph chunking + title prepending + top-k=4.

2. **Hallucination risk** — The LLM may answer from training knowledge instead of documents. Mitigation: strict grounding prompt + programmatic source attribution in the Gradio UI.

---

## Architecture

```text
documents/*.txt
    ↓
ingest.py (load + clean)
    ↓
Paragraph chunking (title prepended)
    ↓
sentence-transformers (all-MiniLM-L6-v2)
    ↓
ChromaDB (./chroma)
    ↓
rag.py retrieve() — top-k=4
    ↓
Groq (llama-3.3-70b-versatile)
    ↓
app.py (Gradio) → Answer + Sources
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:** Give Cursor my Chunking Strategy and Documents sections from this file. Expect `ingest.py` with `load_documents()` and paragraph-based `chunk_documents()`. Verify 60 chunks and print 5 samples before embedding.

**Milestone 4 — Embedding and retrieval:** Give Cursor my Retrieval Approach and Architecture diagram. Expect `rag.py` with ChromaDB indexing and `retrieve()` returning chunks with source metadata and distance scores. Test with 3 evaluation questions before adding generation.

**Milestone 5 — Generation and interface:** Give Cursor grounding requirements and Gradio skeleton. Expect `app.py` with answer + sources output. Verify refusal on out-of-scope queries and source citations on in-scope queries.
