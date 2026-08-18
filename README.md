# AI Study Buddy 2.0

## A Human-Centered AI Learning Assistant

**AI Study Buddy 2.0** is a research-oriented educational AI project exploring how intelligent learning assistants can support students while preserving **transparency, trust, learner agency, accessibility, and responsible AI principles**.

The project combines software development with Human–AI Interaction research. Rather than focusing only on whether an AI system can generate a correct answer, AI Study Buddy asks a broader question:

> **How can an AI learning assistant provide useful academic support while helping students understand, evaluate, and remain in control of the AI-generated guidance they receive?**

---

##  Research Motivation

Generative AI is increasingly used by students for explanations, summaries, brainstorming, tutoring, and academic support.

However, several important challenges remain:

* Students may receive answers without understanding where the information came from.
* AI-generated responses may sound confident even when they are incomplete or incorrect.
* Students may become overly dependent on AI instead of developing independent reasoning.
* Users may not understand why a particular response was generated.
* Trust in AI may increase simply because an answer sounds convincing.
* Students need meaningful control over how AI participates in their learning.

AI Study Buddy 2.0 is designed to explore these issues through a working educational AI system.

---

##  Preliminary Research Question

> **How do transparency and source-grounded explanations influence student trust and perceived usefulness in an AI learning assistant?**

This question will guide both the design of the application and its future evaluation.

---

##  Research Themes

The project explores:

* Human–AI Interaction
* Responsible AI
* Trust in Artificial Intelligence
* Explainable AI
* AI in Education
* Learner Agency
* Source-Grounded AI
* Accessibility
* Human-Centered Design

---

##  Planned Features

### AI Study Assistant

Students will be able to ask questions about study materials and receive context-aware academic explanations.

### Document-Grounded Question Answering

Students will be able to upload study materials so that the assistant can generate answers based on selected sources rather than relying only on general model knowledge.

### Source Transparency

The system will show the supporting material used to generate an answer.

### Explainability

Students will be able to request an explanation of why the assistant produced a particular answer.

### Learner Control

Users will be able to choose:

* Answer depth
* Explanation style
* Study material
* Whether they want hints or full explanations
* Whether they want quizzes or review questions

### Study Tools

Planned tools include:

* Summaries
* Flashcards
* Practice questions
* Quizzes
* Study guides

### Student Feedback

Students will be able to evaluate responses using questions such as:

* Was this answer useful?
* Was the explanation understandable?
* Do you trust this answer?
* Did the source information help you evaluate the response?
* Would you use this answer while studying?

These responses may later support research on trust and perceived usefulness.

---

##  Human–AI Interaction Model

The project is based on an iterative interaction:

```text
Student
   ↓
Question
   ↓
Study Material
   ↓
AI Retrieval
   ↓
AI Response
   ↓
Supporting Evidence
   ↓
Explanation
   ↓
Student Evaluation
   ↓
Future Interaction
```

This interaction emphasizes that learning with AI should not be one-directional.

The student should remain an active participant who can question, evaluate, and control the AI system.

---

##  Planned Architecture

```text
User Interface
     │
     ▼
Streamlit Application
     │
     ├── Question Input
     ├── Document Upload
     ├── Study Tools
     └── Feedback Interface
     │
     ▼
AI Processing Layer
     │
     ├── Document Retrieval
     ├── Response Generation
     ├── Source Grounding
     └── Explanation Generation
     │
     ▼
Data Layer
     │
     ├── Study Documents
     ├── Conversation History
     └── Evaluation Feedback
```

---

##  Planned Technology Stack

### Core

* Python
* Streamlit
* SQLite

### AI

* Large Language Model integration
* Embeddings
* Semantic Search
* Retrieval-Augmented Generation

### Data & Evaluation

* Pandas
* Matplotlib
* Student feedback metrics

### Development

* Git
* GitHub
* Python virtual environments
* Automated testing

---

##  Evaluation

AI Study Buddy 2.0 will eventually include a small evaluation framework.

Potential dimensions include:

| Dimension    | Example Question                                         |
| ------------ | -------------------------------------------------------- |
| Usefulness   | Did this response help you understand the topic?         |
| Trust        | How much do you trust this response?                     |
| Transparency | Do you understand what information supported the answer? |
| Clarity      | Was the explanation easy to understand?                  |
| Agency       | Did you feel in control of how the AI supported you?     |

The purpose of the evaluation is not simply to measure whether students like the system. It is to examine how particular design choices influence the relationship between the learner and the AI assistant.

---

##  Development Roadmap

### Milestone 1 — Research Foundation

* Research question
* Project README
* System architecture
* Responsible AI goals

### Milestone 2 — Core Interface

* Streamlit interface
* Question input
* Session management

### Milestone 3 — Document Support

* File upload
* Text extraction
* Document processing

### Milestone 4 — Source-Grounded AI

* Retrieval
* Evidence selection
* Source citations

### Milestone 5 — Explainability

* Supporting evidence
* Explanation interface
* Response transparency

### Milestone 6 — Study Tools

* Quiz generation
* Summaries
* Practice questions
* Flashcards

### Milestone 7 — Learner Feedback

* Trust ratings
* Usefulness ratings
* Explanation feedback

### Milestone 8 — Evaluation

* Data analysis
* Visualization
* Research observations

### Milestone 9 — Testing & Documentation

* Unit tests
* Usability improvements
* Technical documentation

### Milestone 10 — Release

* Final demonstration
* Research summary
* Public GitHub release

---

##  Responsible AI Principles

AI Study Buddy 2.0 is being designed around several principles:

**Transparency**
Students should be able to understand where information comes from.

**Learner Agency**
AI should support student thinking rather than replace it.

**Privacy**
The system should minimize unnecessary collection of personal information.

**Accessibility**
The interface should support students with different levels of technical experience.

**Accountability**
AI-generated information should be presented as assistance rather than unquestionable authority.

---

## Author

**Josaphat Boesinga**

Software Developer · Emerging AI & Network Science Researcher

Research interests:

**Human–AI Coevolution · Network Science · Responsible AI · Computational Social Science · Human–Computer Interaction**

---

## Project Status

🟡 **Active Development**

AI Study Buddy 2.0 is currently being redesigned and rebuilt as a human-centered AI research project.
