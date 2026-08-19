import os

from openai import OpenAI


# =========================================================
# MODEL CONFIGURATION
# =========================================================

DEFAULT_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)

# Minimum TF-IDF similarity required before
# we allow the AI to answer from retrieved evidence.
MIN_RELEVANCE_SCORE = 0.05


# =========================================================
# API STATUS
# =========================================================

def api_key_available():
    """
    Check whether an OpenAI API key is available
    without exposing the key itself.
    """

    return bool(
        os.getenv("OPENAI_API_KEY")
    )


# =========================================================
# BUILD SOURCE CONTEXT
# =========================================================

def build_source_context(results):
    """
    Convert retrieved passages into labeled
    evidence for the language model.
    """

    source_blocks = []

    for number, result in enumerate(
        results,
        start=1,
    ):

        source_blocks.append(
            (
                f"[Source {number}, Page {result['page']}]\n"
                f"{result['text']}"
            )
        )

    return "\n\n".join(source_blocks)


# =========================================================
# EVIDENCE QUALITY CHECK
# =========================================================

def evidence_is_sufficient(results):
    """
    Check whether retrieval produced enough
    evidence to justify generating an answer.
    """

    if not results:
        return False

    best_score = max(
        result["score"]
        for result in results
    )

    return best_score >= MIN_RELEVANCE_SCORE


# =========================================================
# GROUNDED QUESTION ANSWERING
# =========================================================

def generate_grounded_answer(
    question,
    results,
    answer_depth="Detailed",
):
    """
    Generate an answer using ONLY retrieved passages
    from the uploaded study material.
    """

    if not results:

        return (
            "I don't have enough information in your "
            "uploaded study material to answer this "
            "question confidently."
        )


    if not evidence_is_sufficient(results):

        return (
            "I don't have enough information in your "
            "uploaded study material to answer this "
            "question confidently."
        )


    api_key = os.getenv(
        "OPENAI_API_KEY"
    )


    if not api_key:

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )


    client = OpenAI(
        api_key=api_key
    )


    # -----------------------------------------------------
    # ANSWER STYLE
    # -----------------------------------------------------

    if answer_depth == "Brief":

        style_instruction = (
            "Give a concise educational answer in "
            "approximately 2 to 4 sentences."
        )


    elif answer_depth == "Guided Learning":

        style_instruction = (
            "Teach the concept step by step. Begin with "
            "a guiding idea or hint before giving the full "
            "explanation. Encourage the learner to think "
            "through the material."
        )


    else:

        style_instruction = (
            "Give a clear and reasonably detailed "
            "educational explanation."
        )


    # -----------------------------------------------------
    # SOURCE CONTEXT
    # -----------------------------------------------------

    source_context = build_source_context(
        results
    )


    # -----------------------------------------------------
    # SYSTEM INSTRUCTIONS
    # -----------------------------------------------------

    instructions = f"""
You are AI Study Buddy 2.0, a human-centered educational AI assistant.

Your role is to help students understand material from an uploaded
study document.

STRICT SOURCE-GROUNDING RULES:

1. Answer ONLY from the study passages provided below.

2. Do NOT use outside knowledge to fill missing information.

3. If the supplied evidence is insufficient, respond:

"I don't have enough information in your uploaded study material
to answer this question confidently."

4. Important factual claims must include citations using:

[Source 1, p. 3]

5. Never invent sources.

6. Never invent page numbers.

7. Never claim that the document says something that is not
supported by the supplied passages.

8. Encourage the learner to evaluate the supporting material.

9. Present AI output as educational guidance rather than
unquestionable authority.

10. Keep explanations understandable for students.

RESPONSE STYLE:

{style_instruction}
"""


    # -----------------------------------------------------
    # USER PROMPT
    # -----------------------------------------------------

    prompt = f"""
STUDENT QUESTION:

{question}


RETRIEVED STUDY MATERIAL:

{source_context}


Answer the student's question using only the supplied study material.
"""


    # -----------------------------------------------------
    # GENERATE RESPONSE
    # -----------------------------------------------------

    response = client.responses.create(
        model=DEFAULT_MODEL,
        instructions=instructions,
        input=prompt,
        store=False,
    )


    return response.output_text


# =========================================================
# DOCUMENT OVERVIEW
# =========================================================

def generate_document_overview(
    document_text,
    answer_depth="Detailed",
):
    """
    Generate an overview of the uploaded document.

    This is used for questions such as:

    - What is this document about?
    - What is this document for?
    - Summarize this document.
    - What is the purpose of this document?
    """

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )


    if not api_key:

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )


    if not document_text.strip():

        return (
            "I could not extract enough readable text "
            "from the uploaded document."
        )


    client = OpenAI(
        api_key=api_key
    )


    # Limit context during prototype development.
    document_context = document_text[:15000]


    # -----------------------------------------------------
    # OVERVIEW STYLE
    # -----------------------------------------------------

    if answer_depth == "Brief":

        style_instruction = (
            "Explain what the document is about and its "
            "apparent purpose in 2 to 4 sentences."
        )


    elif answer_depth == "Guided Learning":

        style_instruction = (
            "Explain what the document is about, identify "
            "its main ideas, and suggest what a student "
            "should focus on while studying it."
        )


    else:

        style_instruction = (
            "Give a clear overview of the document, including "
            "its apparent purpose, major ideas, topics, and "
            "important themes."
        )


    instructions = f"""
You are AI Study Buddy 2.0.

Use ONLY the uploaded document supplied below.

Do not introduce outside information.

If the purpose of the document is not explicitly stated,
clearly explain that you are inferring its apparent purpose
from the document's content.

Do not make claims that are unsupported by the document.

{style_instruction}
"""


    prompt = f"""
UPLOADED STUDY DOCUMENT:

{document_context}


Explain what this document is about.
"""


    response = client.responses.create(
        model=DEFAULT_MODEL,
        instructions=instructions,
        input=prompt,
        store=False,
    )


    return response.output_text