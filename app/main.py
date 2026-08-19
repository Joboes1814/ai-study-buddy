import streamlit as st

from config import (
    APP_NAME,
    APP_SUBTITLE,
    RESEARCH_QUESTION,
    DISCLAIMER,
)

from document_processor import (
    process_uploaded_document,
)

from retrieval import (
    retrieve_relevant_chunks,
)

from ai_service import (
    generate_grounded_answer,
    generate_document_overview,
    api_key_available,
    DEFAULT_MODEL,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide",
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document" not in st.session_state:
    st.session_state.document = None

if "document_name" not in st.session_state:
    st.session_state.document_name = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def is_document_overview_question(question):
    """
    Detect questions asking about the uploaded
    document as a whole.
    """

    question = question.lower().strip()

    overview_phrases = [
        "what is this document about",
        "what is the document about",
        "what is this document for",
        "what is the document for",
        "summarize this document",
        "summarize the document",
        "give me a summary",
        "give me an overview",
        "what does this document discuss",
        "what does the document discuss",
        "what is the purpose of this document",
        "what is the purpose of the document",
        "what are the main ideas",
        "what are the main topics",
        "tell me about this document",
    ]

    return any(
        phrase in question
        for phrase in overview_phrases
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title(
        "🧠 Study Controls"
    )

    st.write(
        "Customize how AI Study Buddy supports your learning."
    )

    st.divider()


    # -----------------------------------------------------
    # ANSWER SETTINGS
    # -----------------------------------------------------

    answer_depth = st.selectbox(
        "Answer style",
        [
            "Brief",
            "Detailed",
            "Guided Learning",
        ],
        index=1,
    )


    explanation_enabled = st.toggle(
        "Explain source selection",
        value=True,
    )


    sources_enabled = st.toggle(
        "Show supporting sources",
        value=True,
    )


    top_k = st.slider(
        "Number of source passages",
        min_value=1,
        max_value=5,
        value=3,
    )


    # -----------------------------------------------------
    # STUDY MATERIAL
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "📄 Study Material"
    )


    uploaded_file = st.file_uploader(
        "Upload PDF or TXT",
        type=[
            "pdf",
            "txt",
        ],
    )


    if uploaded_file is not None:

        if (
            st.session_state.document_name
            != uploaded_file.name
        ):

            try:

                with st.spinner(
                    "Processing study material..."
                ):

                    document = (
                        process_uploaded_document(
                            uploaded_file
                        )
                    )


                st.session_state.document = document

                st.session_state.document_name = (
                    uploaded_file.name
                )


            except Exception as error:

                st.error(
                    f"Unable to process document: {error}"
                )


    # -----------------------------------------------------
    # DOCUMENT STATUS
    # -----------------------------------------------------

    if st.session_state.document:

        document = (
            st.session_state.document
        )


        st.success(
            f"Loaded: "
            f"{st.session_state.document_name}"
        )


        st.caption(
            f"{document['page_count']} page(s)"
            f" · "
            f"{document['character_count']:,} characters"
        )


        with st.expander(
            "Preview extracted text"
        ):

            if document["full_text"]:

                preview = (
                    document["full_text"][:3000]
                )

                st.text(
                    preview
                )


                if (
                    len(document["full_text"])
                    > 3000
                ):

                    st.caption(
                        "Preview limited to the first "
                        "3,000 characters."
                    )


            else:

                st.warning(
                    "No readable text was extracted."
                )


        if st.button(
            "Remove Study Material",
            use_container_width=True,
        ):

            st.session_state.document = None
            st.session_state.document_name = None

            st.rerun()


    # -----------------------------------------------------
    # AI CONNECTION
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "🤖 AI Connection"
    )


    if api_key_available():

        st.success(
            "OpenAI API connected"
        )

        st.caption(
            f"Model: {DEFAULT_MODEL}"
        )


    else:

        st.error(
            "OpenAI API key not configured."
        )


    # -----------------------------------------------------
    # RESEARCH MODE
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "🔬 Research Mode"
    )

    st.caption(
        "Studying how transparency and source "
        "grounding influence trust and perceived usefulness."
    )

    st.info(
        RESEARCH_QUESTION
    )


    # -----------------------------------------------------
    # CLEAR CHAT
    # -----------------------------------------------------

    st.divider()

    if st.button(
        "Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.title(
    "🧠 AI Study Buddy 2.0"
)

st.subheader(
    "Learn with AI — without giving up "
    "control of your learning."
)

st.write(
    APP_SUBTITLE
)

st.warning(
    DISCLAIMER
)


# =========================================================
# STATUS
# =========================================================

status1, status2, status3 = st.columns(3)


with status1:

    st.metric(
        "Development Stage",
        "Milestone 5",
    )


with status2:

    ai_status = (
        "Grounded AI"
        if api_key_available()
        else "Not Connected"
    )

    st.metric(
        "AI Mode",
        ai_status,
    )


with status3:

    document_status = (
        "Ready"
        if st.session_state.document
        else "No Document"
    )

    st.metric(
        "Study Material",
        document_status,
    )


st.divider()


# =========================================================
# INTRODUCTION
# =========================================================

if not st.session_state.messages:

    st.markdown(
        """
        ### Grounded AI Learning Is Active 🤖📚

        AI Study Buddy can now:

        - Read uploaded PDF and TXT study materials
        - Identify relevant passages
        - Generate explanations grounded in those passages
        - Cite supporting evidence
        - Explain why sources were selected
        - Summarize the uploaded document
        - Refuse questions that are unsupported by the material

        The current workflow is:

        **Question → Retrieval → Evidence → Grounded AI Answer**

        For document-level questions such as:

        *"What is this document about?"*

        Study Buddy analyzes the document as a whole.

        For specific questions, Study Buddy retrieves relevant
        passages before generating an answer.
        """
    )


# =========================================================
# CURRENT DOCUMENT
# =========================================================

if st.session_state.document:

    document = (
        st.session_state.document
    )

    st.info(
        f"📄 Current study material: "
        f"**{st.session_state.document_name}** "
        f"· {document['page_count']} page(s)"
    )


# =========================================================
# CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask a question about your study material..."
)


if question:

    # -----------------------------------------------------
    # SAVE USER QUESTION
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )


    # Default values used later
    results = []
    answer = ""


    # =====================================================
    # REQUIRE DOCUMENT
    # =====================================================

    if not st.session_state.document:

        answer = (
            "📄 Please upload a PDF or TXT study document "
            "before asking a source-grounded question."
        )


        with st.chat_message(
            "assistant"
        ):

            st.warning(
                answer
            )


    # =====================================================
    # REQUIRE OPENAI CONNECTION
    # =====================================================

    elif not api_key_available():

        answer = (
            "🔑 The OpenAI API is not connected. "
            "Please configure OPENAI_API_KEY."
        )


        with st.chat_message(
            "assistant"
        ):

            st.error(
                answer
            )


    # =====================================================
    # DOCUMENT OVERVIEW QUESTION
    # =====================================================

    elif is_document_overview_question(
        question
    ):

        try:

            with st.spinner(
                "Reading the document..."
            ):

                answer = (
                    generate_document_overview(
                        document_text=(
                            st.session_state
                            .document["full_text"]
                        ),
                        answer_depth=answer_depth,
                    )
                )


            with st.chat_message(
                "assistant"
            ):

                st.markdown(
                    "### 📄 Document Overview"
                )

                st.markdown(
                    answer
                )

                st.markdown("---")

                st.caption(
                    "This overview was generated only "
                    "from the uploaded study material."
                )


        except Exception as error:

            answer = (
                "I encountered an error while "
                "analyzing the document."
            )


            with st.chat_message(
                "assistant"
            ):

                st.error(
                    answer
                )

                st.code(
                    str(error)
                )


    # =====================================================
    # SOURCE RETRIEVAL + GROUNDED ANSWER
    # =====================================================

    else:

        with st.spinner(
            "Searching your study material..."
        ):

            results = (
                retrieve_relevant_chunks(
                    question=question,
                    document=(
                        st.session_state.document
                    ),
                    top_k=top_k,
                )
            )


        # -------------------------------------------------
        # NO RELEVANT EVIDENCE
        # -------------------------------------------------

        if not results:

            answer = (
                "I don't have enough information in your "
                "uploaded study material to answer this "
                "question confidently."
            )


            with st.chat_message(
                "assistant"
            ):

                st.warning(
                    answer
                )


        # -------------------------------------------------
        # GENERATE GROUNDED ANSWER
        # -------------------------------------------------

        else:

            try:

                with st.spinner(
                    "Creating a source-grounded explanation..."
                ):

                    answer = (
                        generate_grounded_answer(
                            question=question,
                            results=results,
                            answer_depth=answer_depth,
                        )
                    )


                with st.chat_message(
                    "assistant"
                ):

                    # -------------------------------------
                    # ANSWER
                    # -------------------------------------

                    st.markdown(
                        "### 🧠 Grounded Answer"
                    )

                    st.markdown(
                        answer
                    )


                    # -------------------------------------
                    # SUPPORTING EVIDENCE
                    # -------------------------------------

                    if sources_enabled:

                        st.markdown("---")

                        st.markdown(
                            "### 📚 Supporting Evidence"
                        )


                        for number, result in enumerate(
                            results,
                            start=1,
                        ):

                            similarity = (
                                result["score"]
                                * 100
                            )


                            with st.expander(
                                f"Source {number} "
                                f"· Page {result['page']} "
                                f"· Similarity "
                                f"{similarity:.1f}%"
                            ):

                                st.write(
                                    result["text"]
                                )


                                if explanation_enabled:

                                    st.caption(
                                        "Why this passage? "
                                        "The retrieval system "
                                        "identified this section "
                                        "as relevant to the student's "
                                        "question based on textual "
                                        "similarity."
                                    )


                    # -------------------------------------
                    # TRANSPARENCY NOTICE
                    # -------------------------------------

                    st.markdown("---")

                    st.caption(
                        "This answer was generated using "
                        "retrieved passages from the uploaded "
                        "study material. Students should still "
                        "review the original source before "
                        "relying on the answer."
                    )


            except Exception as error:

                answer = (
                    "The AI service encountered an error."
                )


                with st.chat_message(
                    "assistant"
                ):

                    st.error(
                        answer
                    )

                    st.code(
                        str(error)
                    )


    # =====================================================
    # SAVE ASSISTANT RESPONSE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


    # =====================================================
    # RESEARCH FEEDBACK
    # =====================================================

    if answer:

        st.markdown(
            "### 📊 Evaluate This Response"
        )

        st.caption(
            "These controls will later support research "
            "on transparency, trust, usefulness, and "
            "learner agency."
        )


        feedback1, feedback2, feedback3 = (
            st.columns(3)
        )


        interaction_id = len(
            st.session_state.messages
        )


        with feedback1:

            st.slider(
                "Usefulness",
                min_value=1,
                max_value=5,
                value=3,
                key=(
                    f"usefulness_"
                    f"{interaction_id}"
                ),
            )


        with feedback2:

            st.slider(
                "Trust",
                min_value=1,
                max_value=5,
                value=3,
                key=(
                    f"trust_"
                    f"{interaction_id}"
                ),
            )


        with feedback3:

            st.slider(
                "Clarity",
                min_value=1,
                max_value=5,
                value=3,
                key=(
                    f"clarity_"
                    f"{interaction_id}"
                ),
            )


        st.radio(
            "Did the transparency of this response "
            "help you evaluate the AI's answer?",
            [
                "Yes",
                "No",
                "Not sure",
            ],
            horizontal=True,
            key=(
                f"transparency_"
                f"{interaction_id}"
            ),
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Study Buddy 2.0 · "
    "Human-Centered AI · "
    "Source-Grounded Learning · "
    "Responsible AI · "
    "Josaphat Boesinga"
)