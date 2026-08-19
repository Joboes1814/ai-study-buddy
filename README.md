# 🧠 AI Study Buddy 2.0

**A Human-Centered, Source-Grounded AI Learning Assistant**

AI Study Buddy 2.0 is an experimental educational AI research
prototype designed to explore how transparency, source grounding,
and learner control influence trust and perceived usefulness in
AI-assisted learning.

Rather than functioning as a general-purpose chatbot, AI Study Buddy
works with study materials uploaded by the learner and provides
different ways to engage with that material.

---

## 🔬 Research Motivation

Generative AI tools can provide students with fast answers, but fast
answers do not necessarily support meaningful learning.

Students may accept AI-generated information without understanding
where it came from, how reliable it is, or whether the information
actually reflects their course material.

AI Study Buddy 2.0 explores a different approach:

> AI should support the learner's reasoning rather than replace it.

The project therefore emphasizes:

- source grounding
- transparency
- learner agency
- explainability
- responsible AI
- human-AI interaction
- active learning

---

## ❓ Research Question

**How do transparency and source-grounded explanations influence
student trust and perceived usefulness in an AI learning assistant?**

The prototype also explores whether learner-controlled interaction
modes influence students' sense of control and active participation
during AI-assisted learning.

---

## 🎯 Core Features

### 📄 Study Material

Students can upload:

- PDF documents
- TXT documents

The system extracts readable text and prepares the material for
retrieval and AI-assisted learning.

---

### 🔎 Source Retrieval

For specific questions, AI Study Buddy:

1. processes the uploaded document
2. divides the document into passages
3. uses TF-IDF representations
4. calculates textual similarity
5. retrieves passages relevant to the learner's request
6. supplies those passages as evidence to the AI

Retrieved passages maintain their page references whenever available.

---

### 🧠 Source-Grounded Answers

AI-generated explanations are instructed to use the retrieved
study material rather than freely answering from outside knowledge.

Important claims can include source references such as:

`[Source 1, p. 12]`

Students can also inspect the passages selected by the retrieval
system.

---

## 🎓 Learner-Controlled Study Modes

AI Study Buddy 2.0 currently provides six learning modes.

### 🧠 Ask Question

Receive a source-grounded explanation of a topic from the uploaded
study material.

### 💡 Hint Mode

Receive progressive hints rather than immediately receiving the
complete answer.

### 🧒 Explain Simply

Transform difficult material into clearer, student-friendly language.

### 📝 Quiz Me

Generate questions from the uploaded study material.

Answers remain hidden until the learner chooses to reveal them.

### 🗂️ Flashcards

Generate interactive flashcards containing important concepts from
the uploaded material.

Students are encouraged to think about the answer before revealing
the back of each card.

### ✅ Check My Understanding

Students explain a concept in their own words.

AI Study Buddy then compares the explanation with the uploaded
material and identifies:

- accurate ideas
- missing information
- areas that could be improved
- unsupported claims
- a stronger explanation
- a follow-up learning question

---

## 📊 Research Evaluation

The prototype includes an interaction-level evaluation system.

After an eligible AI interaction, learners can evaluate:

- usefulness
- trust
- clarity
- sense of control
- active involvement

Each evaluation is associated with an anonymous session identifier
and interaction identifier.

The prototype can also record experimental conditions such as:

- study mode
- answer style
- number of retrieved passages
- retrieval similarity
- source visibility
- source-explanation setting

Evaluation data can be exported as CSV for later analysis.

Student prompts are excluded from evaluation data by default and
can only be included when the corresponding setting is enabled.

---

## 🔐 Privacy-Conscious Prototype Design

AI Study Buddy is an experimental research prototype.

The current application is designed so that:

- uploaded document text is not intentionally written to a permanent
  research database by the application
- evaluation data is maintained within the current Streamlit session
- students can export evaluation data as CSV
- exact student prompts are excluded from evaluation records by default
- retrieved document passages are sent to the configured AI service when
  an AI response is generated
- document-level overview requests may send a limited portion of the
  uploaded document to the configured AI service
- API requests in the current implementation use `store=False`

Users should not upload confidential, private, legally protected,
or highly sensitive documents to the public research prototype.

---

## ⚠️ Responsible AI Notice

AI Study Buddy should not be treated as an unquestionable academic
authority.

Students should:

- inspect supporting evidence
- compare explanations with original study materials
- verify important academic information
- use AI as a learning aid rather than a replacement for independent
  reasoning

The system may still make mistakes.

---

## 🏗️ System Architecture

```text
                    Student
                       │
                       ▼
                PDF / TXT Upload
                       │
                       ▼
              Document Processing
                       │
                       ▼
             Text + Page Extraction
                       │
                       ▼
                 Text Chunking
                       │
                       ▼
              TF-IDF Representation
                       │
                       ▼
              Cosine Similarity
                       │
                       ▼
             Relevant Passages
                       │
                       ▼
              Grounded AI Layer
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
      Explanation     Quiz       Flashcards
          │
          ├──────── Hint Mode
          ├──────── Explain Simply
          └──────── Understanding Check
                       │
                       ▼
              Source Transparency
                       │
                       ▼
             Learner Evaluation
                       │
                       ▼
                  CSV Export

