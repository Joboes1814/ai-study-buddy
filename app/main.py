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
    generate_study_tool,
    generate_flashcards,
    generate_quiz,
    api_key_available,
    DEFAULT_MODEL,
)


# =========================================================
# PAGE CONFIG
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
# HELPERS
# =========================================================

def is_document_overview_question(
    question
):

    question = (
        question.lower().strip()
    )

    phrases = [
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
        for phrase in phrases
    )


def study_mode_description(
    mode
):

    descriptions = {

        "Ask Question":
            "Ask a direct question and receive "
            "a source-grounded explanation.",

        "Hint Mode":
            "Receive guidance without immediately "
            "being given the answer.",

        "Explain Simply":
            "Turn difficult material into a clear, "
            "student-friendly explanation.",

        "Quiz Me":
            "Test yourself before revealing "
            "the correct answers.",

        "Flashcards":
            "Study important ideas with interactive "
            "front-and-back cards.",

        "Check My Understanding":
            "Explain a concept in your own words "
            "and receive grounded feedback.",
    }

    return descriptions[mode]


def input_placeholder(
    mode
):

    placeholders = {

        "Ask Question":
            "Ask a question about your study material...",

        "Hint Mode":
            "Enter a question you want hints for...",

        "Explain Simply":
            "What concept should I explain simply?",

        "Quiz Me":
            "What topic would you like to be quizzed on?",

        "Flashcards":
            "What topic should the flashcards cover?",

        "Check My Understanding":
            "Explain a concept in your own words...",
    }

    return placeholders[mode]


# =========================================================
# FLASHCARD RENDERER
# =========================================================

def render_flashcards(
    cards,
    key_prefix,
):

    if not cards:

        st.warning(
            "No flashcards could be created "
            "from the retrieved material."
        )

        return


    st.markdown(
        "### 🗂️ Study Flashcards"
    )

    st.caption(
        "Try answering each card before "
        "revealing the back."
    )


    for index in range(
        0,
        len(cards),
        2,
    ):

        columns = st.columns(
            2,
            gap="medium",
        )


        for offset in range(2):

            card_index = (
                index + offset
            )


            if card_index >= len(cards):
                continue


            card = (
                cards[
                    card_index
                ]
            )


            with columns[offset]:

                with st.container(
                    border=True
                ):

                    st.caption(
                        f"FLASHCARD "
                        f"{card_index + 1}"
                    )

                    st.markdown(
                        f"### {card['front']}"
                    )

                    st.write("")


                    with st.expander(
                        "👁️ Reveal answer",
                        expanded=False,
                        key=(
                            f"{key_prefix}_"
                            f"card_{card_index}"
                        ),
                    ):

                        st.markdown(
                            card[
                                "back"
                            ]
                        )

                        st.divider()

                        st.caption(
                            f"📚 Source "
                            f"{card['source_number']} "
                            f"· Page "
                            f"{card['page']}"
                        )


# =========================================================
# QUIZ RENDERER
# =========================================================

def render_quiz(
    questions,
    key_prefix,
):

    if not questions:

        st.warning(
            "No quiz questions could be created "
            "from the retrieved material."
        )

        return


    st.markdown(
        "### 📝 Your Quiz"
    )

    st.caption(
        "Think through each question before "
        "revealing the answer."
    )


    for index, item in enumerate(
        questions
    ):

        with st.container(
            border=True
        ):

            st.caption(
                f"QUESTION {index + 1}"
            )

            st.markdown(
                f"### {item['question']}"
            )


            with st.expander(
                "✅ Check answer",
                expanded=False,
                key=(
                    f"{key_prefix}_"
                    f"quiz_{index}"
                ),
            ):

                st.markdown(
                    item[
                        "answer"
                    ]
                )

                st.divider()

                st.caption(
                    f"📚 Source "
                    f"{item['source_number']} "
                    f"· Page "
                    f"{item['page']}"
                )


# =========================================================
# SUPPORTING EVIDENCE
# =========================================================

def render_sources(
    results,
    explanation_enabled,
):

    if not results:
        return


    with st.expander(
        "📚 View supporting evidence"
    ):

        for number, result in enumerate(
            results,
            start=1,
        ):

            similarity = (
                result["score"]
                * 100
            )

            st.markdown(
                f"**Source {number} "
                f"· Page {result['page']} "
                f"· Similarity "
                f"{similarity:.1f}%**"
            )

            st.write(
                result["text"]
            )

            if explanation_enabled:

                st.caption(
                    "This passage was selected "
                    "because the retrieval system "
                    "identified textual similarity "
                    "with the learner's request."
                )

            if number < len(results):

                st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title(
        "🧠 Study Controls"
    )

    st.caption(
        "You decide how AI supports "
        "your learning."
    )

    st.divider()


    # -----------------------------------------------------
    # STUDY MODE
    # -----------------------------------------------------

    st.subheader(
        "🎯 Study Mode"
    )

    study_mode = st.selectbox(
        "How would you like to learn?",
        [
            "Ask Question",
            "Hint Mode",
            "Explain Simply",
            "Quiz Me",
            "Flashcards",
            "Check My Understanding",
        ],
    )

    st.caption(
        study_mode_description(
            study_mode
        )
    )


    # -----------------------------------------------------
    # RESPONSE CONTROLS
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "⚙️ Learning Preferences"
    )

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
    # DOCUMENT
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

                st.session_state.document = (
                    document
                )

                st.session_state.document_name = (
                    uploaded_file.name
                )

            except Exception as error:

                st.error(
                    f"Unable to process document: "
                    f"{error}"
                )


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

            st.text(
                document[
                    "full_text"
                ][:3000]
            )


        if st.button(
            "Remove Study Material",
            use_container_width=True,
        ):

            st.session_state.document = None
            st.session_state.document_name = None
            st.session_state.messages = []

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
            f"Model: "
            f"{DEFAULT_MODEL}"
        )

    else:

        st.error(
            "OpenAI API key not configured."
        )


    # -----------------------------------------------------
    # RESEARCH
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "🔬 Research Mode"
    )

    st.caption(
        "Studying transparency, trust, "
        "usefulness, and learner agency."
    )

    with st.expander(
        "Research question"
    ):

        st.write(
            RESEARCH_QUESTION
        )


    st.divider()


    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# HEADER
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
# STATUS AREA
# =========================================================

status1, status2, status3, status4 = (
    st.columns(
        4,
        gap="medium",
    )
)


with status1:

    st.metric(
        "Development Stage",
        "Milestone 7",
    )


with status2:

    st.metric(
        "AI Mode",
        (
            "Grounded AI"
            if api_key_available()
            else "Not Connected"
        ),
    )


with status3:

    st.metric(
        "Study Material",
        (
            "Ready"
            if st.session_state.document
            else "No Document"
        ),
    )


with status4:

    st.metric(
        "Study Mode",
        study_mode,
    )


st.divider()


# =========================================================
# MODE PANEL
# =========================================================

with st.container(
    border=True
):

    st.markdown(
        f"## 🎯 {study_mode}"
    )

    st.write(
        study_mode_description(
            study_mode
        )
    )


    if study_mode == "Flashcards":

        st.info(
            "Try to answer each card yourself "
            "before revealing the back."
        )


    elif study_mode == "Quiz Me":

        st.info(
            "Answers stay hidden until you choose "
            "to reveal them."
        )


    elif study_mode == "Hint Mode":

        st.info(
            "Study Buddy will guide you with "
            "progressive hints instead of immediately "
            "giving you the answer."
        )


    elif study_mode == (
        "Check My Understanding"
    ):

        st.info(
            "Explain the concept in your own words. "
            "Study Buddy will compare your explanation "
            "with your uploaded material."
        )


# =========================================================
# DOCUMENT STATUS
# =========================================================

if st.session_state.document:

    document = (
        st.session_state.document
    )

    st.success(
        f"📄 **{st.session_state.document_name}** "
        f"· {document['page_count']} page(s)"
    )

else:

    st.info(
        "Upload study material from the "
        "sidebar to begin."
    )


st.divider()


# =========================================================
# CHAT HISTORY
# =========================================================

for message_index, message in enumerate(
    st.session_state.messages
):

    with st.chat_message(
        message["role"]
    ):

        message_type = (
            message.get(
                "type",
                "text",
            )
        )


        if message_type == "flashcards":

            render_flashcards(
                message["cards"],
                key_prefix=(
                    f"history_"
                    f"{message_index}"
                ),
            )


        elif message_type == "quiz":

            render_quiz(
                message["questions"],
                key_prefix=(
                    f"history_"
                    f"{message_index}"
                ),
            )


        else:

            if (
                message["role"]
                == "assistant"
                and message.get("mode")
            ):

                st.caption(
                    f"Study mode: "
                    f"{message['mode']}"
                )

            st.markdown(
                message["content"]
            )


# =========================================================
# CHAT INPUT
# =========================================================

student_input = st.chat_input(
    input_placeholder(
        study_mode
    )
)


if student_input:

    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "type": "text",
            "content": student_input,
        }
    )


    with st.chat_message(
        "user"
    ):

        st.markdown(
            student_input
        )


    results = []

    answer = ""


    # =====================================================
    # NO DOCUMENT
    # =====================================================

    if not st.session_state.document:

        answer = (
            "📄 Please upload a PDF or TXT "
            "study document first."
        )

        with st.chat_message(
            "assistant"
        ):

            st.warning(
                answer
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "type": "text",
                "content": answer,
                "mode": study_mode,
            }
        )


    # =====================================================
    # NO API
    # =====================================================

    elif not api_key_available():

        answer = (
            "🔑 The OpenAI API "
            "is not connected."
        )

        with st.chat_message(
            "assistant"
        ):

            st.error(
                answer
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "type": "text",
                "content": answer,
                "mode": study_mode,
            }
        )


    # =====================================================
    # DOCUMENT OVERVIEW
    # =====================================================

    elif (
        study_mode == "Ask Question"
        and is_document_overview_question(
            student_input
        )
    ):

        try:

            with st.spinner(
                "Reading the document..."
            ):

                answer = (
                    generate_document_overview(
                        document_text=(
                            st.session_state
                            .document[
                                "full_text"
                            ]
                        ),
                        answer_depth=(
                            answer_depth
                        ),
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


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "type": "text",
                    "content": answer,
                    "mode": study_mode,
                }
            )


        except Exception as error:

            st.error(
                f"AI service error: "
                f"{error}"
            )


    # =====================================================
    # RETRIEVAL
    # =====================================================

    else:

        with st.spinner(
            "Searching your study material..."
        ):

            results = (
                retrieve_relevant_chunks(
                    question=student_input,
                    document=(
                        st.session_state.document
                    ),
                    top_k=top_k,
                )
            )


        if not results:

            answer = (
                "I don't have enough information "
                "in your uploaded study material "
                "to support this activity confidently."
            )

            with st.chat_message(
                "assistant"
            ):

                st.warning(
                    answer
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "type": "text",
                    "content": answer,
                    "mode": study_mode,
                }
            )


        else:

            try:

                # =========================================
                # FLASHCARDS
                # =========================================

                if study_mode == "Flashcards":

                    with st.spinner(
                        "Building your flashcards..."
                    ):

                        cards = (
                            generate_flashcards(
                                student_input=(
                                    student_input
                                ),
                                results=results,
                            )
                        )


                    with st.chat_message(
                        "assistant"
                    ):

                        render_flashcards(
                            cards,
                            key_prefix=(
                                f"new_"
                                f"{len(st.session_state.messages)}"
                            ),
                        )


                        if sources_enabled:

                            render_sources(
                                results,
                                explanation_enabled,
                            )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "type": "flashcards",
                            "cards": cards,
                            "mode": study_mode,
                        }
                    )


                # =========================================
                # QUIZ
                # =========================================

                elif study_mode == "Quiz Me":

                    with st.spinner(
                        "Building your quiz..."
                    ):

                        questions = (
                            generate_quiz(
                                student_input=(
                                    student_input
                                ),
                                results=results,
                            )
                        )


                    with st.chat_message(
                        "assistant"
                    ):

                        render_quiz(
                            questions,
                            key_prefix=(
                                f"new_"
                                f"{len(st.session_state.messages)}"
                            ),
                        )


                        if sources_enabled:

                            render_sources(
                                results,
                                explanation_enabled,
                            )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "type": "quiz",
                            "questions": questions,
                            "mode": study_mode,
                        }
                    )


                # =========================================
                # NORMAL QUESTION
                # =========================================

                elif study_mode == "Ask Question":

                    with st.spinner(
                        "Creating a grounded explanation..."
                    ):

                        answer = (
                            generate_grounded_answer(
                                question=student_input,
                                results=results,
                                answer_depth=(
                                    answer_depth
                                ),
                            )
                        )


                    with st.chat_message(
                        "assistant"
                    ):

                        st.markdown(
                            "### 🧠 Grounded Answer"
                        )

                        st.markdown(
                            answer
                        )

                        if sources_enabled:

                            render_sources(
                                results,
                                explanation_enabled,
                            )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "type": "text",
                            "content": answer,
                            "mode": study_mode,
                        }
                    )


                # =========================================
                # OTHER LEARNING TOOLS
                # =========================================

                else:

                    with st.spinner(
                        f"Creating "
                        f"{study_mode}..."
                    ):

                        answer = (
                            generate_study_tool(
                                student_input=(
                                    student_input
                                ),
                                results=results,
                                study_mode=(
                                    study_mode
                                ),
                                answer_depth=(
                                    answer_depth
                                ),
                            )
                        )


                    with st.chat_message(
                        "assistant"
                    ):

                        st.markdown(
                            answer
                        )


                        if sources_enabled:

                            render_sources(
                                results,
                                explanation_enabled,
                            )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "type": "text",
                            "content": answer,
                            "mode": study_mode,
                        }
                    )


            except Exception as error:

                st.error(
                    "The AI service encountered "
                    "an error."
                )

                st.code(
                    str(error)
                )


    # =====================================================
    # FEEDBACK
    # =====================================================

    if (
        st.session_state.document
        and api_key_available()
    ):

        st.markdown(
            "### 📊 Learning Experience"
        )


        with st.container(
            border=True
        ):

            st.caption(
                "Help evaluate how AI transparency "
                "and learner control affect your experience."
            )


            interaction_id = (
                len(
                    st.session_state.messages
                )
            )


            col1, col2 = st.columns(2)

            col3, col4 = st.columns(2)


            with col1:

                st.slider(
                    "Usefulness",
                    1,
                    5,
                    3,
                    key=(
                        f"usefulness_"
                        f"{interaction_id}"
                    ),
                )


            with col2:

                st.slider(
                    "Trust",
                    1,
                    5,
                    3,
                    key=(
                        f"trust_"
                        f"{interaction_id}"
                    ),
                )


            with col3:

                st.slider(
                    "Clarity",
                    1,
                    5,
                    3,
                    key=(
                        f"clarity_"
                        f"{interaction_id}"
                    ),
                )


            with col4:

                st.slider(
                    "Sense of Control",
                    1,
                    5,
                    3,
                    key=(
                        f"control_"
                        f"{interaction_id}"
                    ),
                )


            st.radio(
                "Did this learning mode help "
                "you stay actively involved?",
                [
                    "Yes",
                    "No",
                    "Not sure",
                ],
                horizontal=True,
                key=(
                    f"agency_"
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
    "Learner Agency · "
    "Source-Grounded Learning · "
    "Responsible AI · "
    "Josaphat Boesinga"
)