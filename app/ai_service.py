import json
import os

from openai import OpenAI


# =========================================================
# MODEL CONFIGURATION
# =========================================================

DEFAULT_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)

MIN_RELEVANCE_SCORE = 0.05


# =========================================================
# OPENAI CLIENT
# =========================================================

def api_key_available():

    return bool(
        os.getenv("OPENAI_API_KEY")
    )


def get_client():

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(
        api_key=api_key
    )


# =========================================================
# SOURCE HELPERS
# =========================================================

def build_source_context(results):

    source_blocks = []

    for number, result in enumerate(
        results,
        start=1,
    ):

        source_blocks.append(
            (
                f"[Source {number}, "
                f"Page {result['page']}]\n"
                f"{result['text']}"
            )
        )

    return "\n\n".join(
        source_blocks
    )


def evidence_is_sufficient(results):

    if not results:
        return False

    best_score = max(
        result["score"]
        for result in results
    )

    return (
        best_score
        >= MIN_RELEVANCE_SCORE
    )


def get_style_instruction(
    answer_depth
):

    if answer_depth == "Brief":

        return (
            "Keep the response concise "
            "and focused."
        )

    if answer_depth == "Guided Learning":

        return (
            "Teach step by step and encourage "
            "the learner to think before giving "
            "complete explanations."
        )

    return (
        "Give a clear and reasonably detailed "
        "educational explanation."
    )


# =========================================================
# NORMAL GROUNDED ANSWER
# =========================================================

def generate_grounded_answer(
    question,
    results,
    answer_depth="Detailed",
):

    if not evidence_is_sufficient(
        results
    ):

        return (
            "I don't have enough information in "
            "your uploaded study material to answer "
            "this question confidently."
        )

    client = get_client()

    source_context = (
        build_source_context(
            results
        )
    )

    style_instruction = (
        get_style_instruction(
            answer_depth
        )
    )

    instructions = f"""
You are AI Study Buddy 2.0,
a human-centered educational AI assistant.

Use ONLY the supplied study material.

RULES:

1. Do not use outside factual knowledge.
2. Base important claims on the supplied passages.
3. Cite claims using labels such as:
   [Source 1, p. 3]
4. Never invent sources.
5. Never invent page numbers.
6. If evidence is insufficient, say:
   "I don't have enough information in your uploaded
   study material to answer this question confidently."
7. Encourage the learner to inspect the original source.
8. Present your explanation as educational guidance,
   not unquestionable authority.

STYLE:

{style_instruction}
"""

    prompt = f"""
STUDENT QUESTION:

{question}


RETRIEVED STUDY MATERIAL:

{source_context}


Answer using only the supplied study material.
"""

    response = (
        client.responses.create(
            model=DEFAULT_MODEL,
            instructions=instructions,
            input=prompt,
            max_output_tokens=800,
            store=False,
        )
    )

    return response.output_text


# =========================================================
# DOCUMENT OVERVIEW
# =========================================================

def generate_document_overview(
    document_text,
    answer_depth="Detailed",
):

    if not document_text.strip():

        return (
            "I could not extract enough "
            "readable text from the document."
        )

    client = get_client()

    document_context = (
        document_text[:15000]
    )

    style_instruction = (
        get_style_instruction(
            answer_depth
        )
    )

    instructions = f"""
You are AI Study Buddy 2.0.

Use ONLY the uploaded document.

Explain:

- what the document is about
- its apparent purpose
- major ideas
- important themes
- what a student should pay attention to

Do not use outside factual knowledge.

If the purpose is not explicitly stated,
say that you are inferring its apparent
purpose from the text.

STYLE:

{style_instruction}
"""

    prompt = f"""
UPLOADED DOCUMENT:

{document_context}


Provide an educational overview.
"""

    response = (
        client.responses.create(
            model=DEFAULT_MODEL,
            instructions=instructions,
            input=prompt,
            max_output_tokens=800,
            store=False,
        )
    )

    return response.output_text


# =========================================================
# HINT / SIMPLE / UNDERSTANDING MODES
# =========================================================

def generate_study_tool(
    student_input,
    results,
    study_mode,
    answer_depth="Detailed",
):

    if not evidence_is_sufficient(
        results
    ):

        return (
            "I don't have enough information in "
            "your uploaded study material to create "
            "this learning activity confidently."
        )

    client = get_client()

    source_context = (
        build_source_context(
            results
        )
    )

    style_instruction = (
        get_style_instruction(
            answer_depth
        )
    )


    if study_mode == "Hint Mode":

        mode_instruction = """
Give exactly 3 progressively useful hints.

Do NOT immediately reveal the complete answer.

End with one guiding question that encourages
the student to reason through the material.
"""


    elif study_mode == "Explain Simply":

        mode_instruction = """
Explain the requested concept using:

- simple vocabulary
- short sentences
- one accessible analogy or example when appropriate

Do not distort the source material.

Finish with:

**Key takeaway:** ...
"""


    elif study_mode == (
        "Check My Understanding"
    ):

        mode_instruction = """
Evaluate the student's explanation against
the supplied source material.

Use these sections:

### What You Got Right

### What Could Be Improved

### Unsupported Claims

### Stronger Explanation

### Next Question

If the student's input does not actually
include their own explanation, ask them to
explain the concept first.
"""


    else:

        raise ValueError(
            "This study mode uses a "
            "different generator."
        )


    instructions = f"""
You are AI Study Buddy 2.0.

Use ONLY the supplied study material.

The learner controls the activity.

RULES:

1. Do not use outside factual knowledge.
2. Do not invent information.
3. Do not invent sources or page numbers.
4. Cite factual explanations when appropriate.
5. Keep the learner actively involved.
6. Encourage review of the original source.

STUDY MODE:

{study_mode}

MODE INSTRUCTIONS:

{mode_instruction}

STYLE:

{style_instruction}
"""


    prompt = f"""
STUDENT INPUT:

{student_input}


RETRIEVED STUDY MATERIAL:

{source_context}
"""


    response = (
        client.responses.create(
            model=DEFAULT_MODEL,
            instructions=instructions,
            input=prompt,
            max_output_tokens=800,
            store=False,
        )
    )

    return response.output_text


# =========================================================
# STRUCTURED FLASHCARDS
# =========================================================

def generate_flashcards(
    student_input,
    results,
):

    if not evidence_is_sufficient(
        results
    ):

        return []

    client = get_client()

    source_context = (
        build_source_context(
            results
        )
    )


    instructions = """
You are AI Study Buddy 2.0.

Create exactly five educational flashcards
using ONLY the supplied study material.

Each flashcard must test an important idea.

The front should contain a question,
concept, or key term.

The back should contain a concise,
student-friendly explanation.

source_number must identify which retrieved
source most directly supports the flashcard.

Do not use outside knowledge.
Do not invent evidence.
"""


    prompt = f"""
STUDENT TOPIC:

{student_input}


RETRIEVED STUDY MATERIAL:

{source_context}


Create five flashcards.
"""


    response = (
        client.responses.create(
            model=DEFAULT_MODEL,
            instructions=instructions,
            input=prompt,
            max_output_tokens=800,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "study_flashcards",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "cards": {
                                "type": "array",
                                "minItems": 5,
                                "maxItems": 5,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "front": {
                                            "type": "string"
                                        },
                                        "back": {
                                            "type": "string"
                                        },
                                        "source_number": {
                                            "type": "integer"
                                        },
                                    },
                                    "required": [
                                        "front",
                                        "back",
                                        "source_number",
                                    ],
                                    "additionalProperties": False,
                                },
                            }
                        },
                        "required": [
                            "cards"
                        ],
                        "additionalProperties": False,
                    },
                }
            },
            store=False,
        )
    )


    data = json.loads(
        response.output_text
    )

    cards = data.get(
        "cards",
        []
    )


    # -----------------------------------------------------
    # VALIDATE SOURCES LOCALLY
    # -----------------------------------------------------

    validated_cards = []

    for card in cards:

        source_number = (
            card.get(
                "source_number",
                1,
            )
        )

        if (
            source_number < 1
            or source_number > len(results)
        ):

            source_number = 1


        actual_source = (
            results[
                source_number - 1
            ]
        )


        validated_cards.append(
            {
                "front":
                    card.get(
                        "front",
                        "",
                    ),

                "back":
                    card.get(
                        "back",
                        "",
                    ),

                "source_number":
                    source_number,

                "page":
                    actual_source[
                        "page"
                    ],
            }
        )


    return validated_cards


# =========================================================
# STRUCTURED QUIZ
# =========================================================

def generate_quiz(
    student_input,
    results,
):

    if not evidence_is_sufficient(
        results
    ):

        return []

    client = get_client()

    source_context = (
        build_source_context(
            results
        )
    )


    instructions = """
You are AI Study Buddy 2.0.

Create exactly three study questions
using ONLY the supplied study material.

The questions should encourage learning,
not merely copy sentences from the source.

Each question must include:

- a question
- a concise correct answer
- the source_number that supports it

Do not use outside knowledge.
"""


    prompt = f"""
STUDENT TOPIC:

{student_input}


RETRIEVED STUDY MATERIAL:

{source_context}


Create a three-question quiz.
"""


    response = (
        client.responses.create(
            model=DEFAULT_MODEL,
            instructions=instructions,
            input=prompt,
            max_output_tokens=800,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "study_quiz",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "questions": {
                                "type": "array",
                                "minItems": 3,
                                "maxItems": 3,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question": {
                                            "type": "string"
                                        },
                                        "answer": {
                                            "type": "string"
                                        },
                                        "source_number": {
                                            "type": "integer"
                                        },
                                    },
                                    "required": [
                                        "question",
                                        "answer",
                                        "source_number",
                                    ],
                                    "additionalProperties": False,
                                },
                            }
                        },
                        "required": [
                            "questions"
                        ],
                        "additionalProperties": False,
                    },
                }
            },
            store=False,
        )
    )


    data = json.loads(
        response.output_text
    )

    questions = data.get(
        "questions",
        []
    )


    validated_questions = []

    for item in questions:

        source_number = (
            item.get(
                "source_number",
                1,
            )
        )


        if (
            source_number < 1
            or source_number > len(results)
        ):

            source_number = 1


        actual_source = (
            results[
                source_number - 1
            ]
        )


        validated_questions.append(
            {
                "question":
                    item.get(
                        "question",
                        "",
                    ),

                "answer":
                    item.get(
                        "answer",
                        "",
                    ),

                "source_number":
                    source_number,

                "page":
                    actual_source[
                        "page"
                    ],
            }
        )


    return validated_questions