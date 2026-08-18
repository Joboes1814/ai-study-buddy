# AI Study Buddy 2.0 — System Architecture

## Architecture Goal

AI Study Buddy 2.0 is designed as a modular educational AI system.

The architecture separates the user interface, AI processing, document retrieval, study tools, data storage, and research evaluation components.

This separation will make the system easier to develop, test, evaluate, and improve.

## High-Level Architecture

```text
                         STUDENT
                            │
                            ▼
                  ┌───────────────────┐
                  │ Streamlit Web UI  │
                  └───────────────────┘
                            │
            ┌───────────────┼────────────────┐
            │               │                │
            ▼               ▼                ▼
        Questions      Study Material    Study Tools
                                            │
                                            ├─ Quiz
                                            ├─ Summary
                                            ├─ Flashcards
                                            └─ Practice
            │
            ▼
     ┌─────────────────┐
     │ AI Orchestrator │
     └─────────────────┘
            │
      ┌─────┼──────────────┐
      │     │              │
      ▼     ▼              ▼
 Retrieval  LLM       Explanation
 Engine     Layer       Module
      │
      ▼
 Supporting Evidence
      │
      ▼
 AI Response + Sources
      │
      ▼
 Student Feedback
      │
      ▼
 Evaluation Database
```

## Component 1 — User Interface

The first version will use Streamlit.

The interface will provide:

* Question input
* Document upload
* Conversation history
* Answer display
* Source display
* Explanation controls
* Study tools
* Feedback controls

## Component 2 — Document Processing

Uploaded learning materials will be processed into smaller text sections.

The system will eventually:

1. Accept a study document.
2. Extract its text.
3. Divide the text into manageable chunks.
4. Convert those chunks into embeddings.
5. Store them for semantic retrieval.

## Component 3 — Retrieval Engine

When a student asks a question, the retrieval engine will search the uploaded material for relevant passages.

```text
Student Question
       ↓
Embedding
       ↓
Semantic Search
       ↓
Relevant Passages
```

These passages will provide context for the AI response.

## Component 4 — AI Response Generation

The language model will receive:

* The student's question
* Relevant retrieved passages
* Response instructions
* Requested explanation level

The system will then generate an answer grounded in the selected learning material.

## Component 5 — Source Transparency

The response interface will display the evidence used to support the answer.

A future response may look like:

```text
ANSWER

Photosynthesis converts light energy into chemical energy...

SUPPORTING SOURCE

Biology Notes — Chapter 4, Section 2

WHY THIS SOURCE WAS USED

This section directly explains the relationship between
sunlight, chlorophyll, and glucose production.
```

## Component 6 — Explainability

Students will be able to request additional explanation.

Possible controls include:

```text
Explain more simply
Show supporting evidence
Why did you give this answer?
Give me a hint instead
Show a detailed explanation
```

This feature is intended to support learner agency.

## Component 7 — Study Tools

The same document-grounded system can support:

* Quizzes
* Flashcards
* Summaries
* Review questions
* Concept explanations

The goal is to reuse the same evidence base rather than generating disconnected study material.

## Component 8 — Feedback System

After receiving an answer, students may optionally provide feedback.

Potential measures include:

```text
Usefulness:     1 2 3 4 5

Trust:          1 2 3 4 5

Clarity:        1 2 3 4 5

Source helpful? Yes / No

Did this help
you learn?      Yes / No
```

## Component 9 — Evaluation Layer

Feedback data may later be analyzed to examine whether particular interface features influence trust and perceived usefulness.

Possible comparisons include:

```text
Answer only
        vs.
Answer + Source

Answer only
        vs.
Answer + Explanation

Fixed response
        vs.
Student-controlled response depth
```

## Planned Technology Stack

### Frontend

Streamlit

### Core Language

Python

### AI Layer

Large Language Model API or compatible local model

### Retrieval

Embeddings + Vector Search

### Database

SQLite

### Analysis

Pandas + Matplotlib

## Privacy Considerations

The system should avoid collecting unnecessary student-identifying information.

Research evaluation data should be separated from normal application data whenever possible.

Any future study involving human participants should only begin after appropriate academic and ethical review.

## Future Architecture

If the project grows beyond the prototype stage, the architecture may evolve toward:

```text
Frontend
   ↓
React / Flutter

API
   ↓
FastAPI

AI Services
   ↓
Retrieval + LLM + Evaluation

Database
   ↓
PostgreSQL / Vector Database
```

The initial implementation will remain intentionally simple so that the research question, system behavior, and evaluation can remain the main focus.
