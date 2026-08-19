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

from evaluation import (
    create_session_id,
    create_interaction_id,
    build_interaction_metadata,
    build_feedback_record,
    records_to_csv,
    evaluation_summary,
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

if "evaluation_records" not in st.session_state:
    st.session_state.evaluation_records = []

if "evaluated_interactions" not in st.session_state:
    st.session_state.evaluated_interactions = set()

if "research_session_id" not in st.session_state:
    st.session_state.research_session_id = (
        create_session_id()
    )

if "evaluation_saved_message" not in st.session_state:
    st.session_state.evaluation_saved_message = False


# =========================================================
# SAVE CONFIRMATION AFTER RERUN
# =========================================================

if st.session_state.evaluation_saved_message:

    st.success(
        "✅ Evaluation saved successfully."
    )

    st.session_state.evaluation_saved_message = False


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def is_document_overview_question(question):

    question = question.lower().strip()

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


def study_mode_description(mode):

    descriptions = {
        "Ask Question":
            "Ask a direct question and receive "
            "a source-grounded explanation.",

        "Hint Mode":
            "Receive progressive guidance without "
            "immediately receiving the complete answer.",

        "Explain Simply":
            "Turn difficult material into a clear "
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


def input_placeholder(mode):

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

            card_index = index + offset

            if card_index >= len(cards):
                continue

            card = cards[card_index]


            with columns[offset]:

                with st.container(
                    border=True
                ):

                    st.caption(
                        f"FLASHCARD {card_index + 1}"
                    )

                    st.markdown(
                        f"### {card['front']}"
                    )

                    st.write("")


                    with st.expander(
                        f"👁️ Reveal answer · Card {card_index + 1}",
                        expanded=False,
                    ):

                        st.markdown(
                            card["back"]
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
                f"✅ Check answer · Question {index + 1}",
                expanded=False,
            ):

                st.markdown(
                    item["answer"]
                )

                st.divider()

                st.caption(
                    f"📚 Source "
                    f"{item['source_number']} "
                    f"· Page "
                    f"{item['page']}"
                )


# =========================================================
# SUPPORTING SOURCES
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
                    "This passage was selected because "
                    "the retrieval system identified "
                    "textual similarity with the "
                    "learner's request."
                )


            if number < len(results):

                st.divider()


# =========================================================
# FEEDBACK FORM
# =========================================================

def render_feedback_form(message):

    interaction_id = message.get(
        "interaction_id"
    )

    if not interaction_id:
        return


    if not message.get(
        "evaluation_eligible",
        False,
    ):
        return


    # -----------------------------------------------------
    # ALREADY EVALUATED
    # -----------------------------------------------------

    if (
        interaction_id
        in st.session_state.evaluated_interactions
    ):

        st.success(
            "✅ Evaluation recorded for this interaction."
        )

        return


    metadata = message.get(
        "evaluation_metadata"
    )

    if not metadata:
        return


    st.markdown(
        "### 📊 Evaluate This Learning Experience"
    )

    st.caption(
        "Your ratings help evaluate how transparency, "
        "source grounding, and learner control "
        "influence the learning experience."
    )


    with st.form(
        key=(
            f"evaluation_form_"
            f"{interaction_id}"
        )
    ):

        col1, col2 = st.columns(2)

        col3, col4 = st.columns(2)


        with col1:

            usefulness = st.slider(
                "Usefulness",
                min_value=1,
                max_value=5,
                value=3,
                help=(
                    "How useful was this response "
                    "for your learning?"
                ),
            )


        with col2:

            trust = st.slider(
                "Trust",
                min_value=1,
                max_value=5,
                value=3,
                help=(
                    "How much did you trust "
                    "this AI response?"
                ),
            )


        with col3:

            clarity = st.slider(
                "Clarity",
                min_value=1,
                max_value=5,
                value=3,
                help=(
                    "How clear and understandable "
                    "was the response?"
                ),
            )


        with col4:

            sense_of_control = st.slider(
                "Sense of Control",
                min_value=1,
                max_value=5,
                value=3,
                help=(
                    "How much control did you feel "
                    "you had over your learning?"
                ),
            )


        active_involvement = st.radio(
            "Did this mode help you stay actively "
            "involved in learning?",
            [
                "Yes",
                "No",
                "Not sure",
            ],
            horizontal=True,
        )


        notes = st.text_area(
            "Optional comment",
            placeholder=(
                "What helped you? "
                "What could be improved?"
            ),
        )


        submitted = st.form_submit_button(
            "Save Evaluation"
        )


    # -----------------------------------------------------
    # SAVE DATA
    # -----------------------------------------------------

    if submitted:

        feedback_record = (
            build_feedback_record(
                metadata=metadata,
                usefulness=usefulness,
                trust=trust,
                clarity=clarity,
                sense_of_control=(
                    sense_of_control
                ),
                active_involvement=(
                    active_involvement
                ),
                notes=notes,
            )
        )


        st.session_state.evaluation_records.append(
            feedback_record
        )


        st.session_state.evaluated_interactions.add(
            interaction_id
        )


        st.session_state.evaluation_saved_message = True


        # IMPORTANT:
        # Restart the app so the sidebar immediately
        # recalculates the evaluation counter.
        st.rerun()


# =========================================================
# CREATE ASSISTANT MESSAGE
# =========================================================

def create_assistant_message(
    response_type,
    study_mode,
    student_input,
    results,
    answer_depth,
    top_k,
    sources_enabled,
    explanation_enabled,
    record_student_input,
    content="",
    cards=None,
    questions=None,
    evaluation_eligible=True,
):

    interaction_id = (
        create_interaction_id()
    )


    metadata = (
        build_interaction_metadata(
            session_id=(
                st.session_state
                .research_session_id
            ),
            interaction_id=interaction_id,
            study_mode=study_mode,
            response_type=response_type,
            document_name=(
                st.session_state
                .document_name
            ),
            answer_depth=answer_depth,
            top_k=top_k,
            results=results,
            sources_visible=(
                sources_enabled
            ),
            source_explanation_enabled=(
                explanation_enabled
            ),
            student_input=(
                student_input
            ),
            record_student_input=(
                record_student_input
            ),
        )
    )


    return {
        "role":
            "assistant",

        "type":
            response_type,

        "content":
            content,

        "cards":
            cards or [],

        "questions":
            questions or [],

        "mode":
            study_mode,

        "interaction_id":
            interaction_id,

        "evaluation_eligible":
            evaluation_eligible,

        "evaluation_metadata":
            metadata,
    }


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title(
        "🧠 Study Controls"
    )

    st.caption(
        "You decide how AI supports your learning."
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
    # LEARNING PREFERENCES
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
            f"Model: {DEFAULT_MODEL}"
        )


    else:

        st.error(
            "OpenAI API key not configured."
        )


    # -----------------------------------------------------
    # RESEARCH EVALUATION
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "🔬 Research Evaluation"
    )


    st.caption(
        "Session ID"
    )


    st.code(
        st.session_state
        .research_session_id
    )


    record_student_input = st.toggle(
        "Include student prompts in evaluation data",
        value=False,
        help=(
            "When disabled, the CSV does not "
            "store the learner's exact prompt."
        ),
    )


    with st.expander(
        "Research question"
    ):

        st.write(
            RESEARCH_QUESTION
        )


    # -----------------------------------------------------
    # EVALUATION COUNTER
    # -----------------------------------------------------

    evaluation_count = len(
        st.session_state
        .evaluation_records
    )


    st.metric(
        "Evaluated Interactions",
        evaluation_count,
    )


    # -----------------------------------------------------
    # SESSION SUMMARY
    # -----------------------------------------------------

    if evaluation_count > 0:

        summary = (
            evaluation_summary(
                st.session_state
                .evaluation_records
            )
        )


        st.caption(
            "Session averages"
        )


        summary1, summary2 = (
            st.columns(2)
        )


        with summary1:

            st.metric(
                "Usefulness",
                f"{summary['usefulness']:.2f}",
            )

            st.metric(
                "Clarity",
                f"{summary['clarity']:.2f}",
            )


        with summary2:

            st.metric(
                "Trust",
                f"{summary['trust']:.2f}",
            )

            st.metric(
                "Control",
                f"{summary['sense_of_control']:.2f}",
            )


        # -------------------------------------------------
        # CSV EXPORT
        # -------------------------------------------------

        csv_data = (
            records_to_csv(
                st.session_state
                .evaluation_records
            )
        )


        st.download_button(
            "⬇️ Export Evaluation CSV",
            data=csv_data,
            file_name=(
                "ai_study_buddy_"
                f"{st.session_state.research_session_id}"
                "_evaluation.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )


        if st.button(
            "Clear Evaluation Data",
            use_container_width=True,
        ):

            st.session_state.evaluation_records = []

            st.session_state.evaluated_interactions = set()

            st.rerun()


    # -----------------------------------------------------
    # CLEAR CHAT
    # -----------------------------------------------------

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
# STATUS CARDS
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
        "Version 1.0",
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
# CURRENT STUDY MODE
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
            "Try answering each card yourself "
            "before revealing the back."
        )


    elif study_mode == "Quiz Me":

        st.info(
            "Answers remain hidden until "
            "you choose to reveal them."
        )


    elif study_mode == "Hint Mode":

        st.info(
            "Study Buddy will guide you with "
            "progressive hints rather than immediately "
            "giving you the complete answer."
        )


    elif study_mode == (
        "Check My Understanding"
    ):

        st.info(
            "Explain the concept in your own words. "
            "Study Buddy will compare your explanation "
            "with the uploaded material."
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
        "Upload study material from "
        "the sidebar to begin."
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

        message_type = message.get(
            "type",
            "text",
        )


        # -------------------------------------------------
        # FLASHCARD HISTORY
        # -------------------------------------------------

        if message_type == "flashcards":

            render_flashcards(
                message.get(
                    "cards",
                    [],
                ),
                key_prefix=(
                    f"history_"
                    f"{message_index}"
                ),
            )


        # -------------------------------------------------
        # QUIZ HISTORY
        # -------------------------------------------------

        elif message_type == "quiz":

            render_quiz(
                message.get(
                    "questions",
                    [],
                ),
                key_prefix=(
                    f"history_"
                    f"{message_index}"
                ),
            )


        # -------------------------------------------------
        # TEXT HISTORY
        # -------------------------------------------------

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
                message.get(
                    "content",
                    "",
                )
            )


        # -------------------------------------------------
        # FEEDBACK FORM
        # -------------------------------------------------

        if (
            message["role"]
            == "assistant"
        ):

            render_feedback_form(
                message
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
    # SAVE USER MESSAGE
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

    assistant_message = None


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


        assistant_message = (
            create_assistant_message(
                response_type="text",
                study_mode=study_mode,
                student_input=student_input,
                results=[],
                answer_depth=answer_depth,
                top_k=top_k,
                sources_enabled=(
                    sources_enabled
                ),
                explanation_enabled=(
                    explanation_enabled
                ),
                record_student_input=(
                    record_student_input
                ),
                content=answer,
                evaluation_eligible=False,
            )
        )


    # =====================================================
    # NO API
    # =====================================================

    elif not api_key_available():

        answer = (
            "🔑 The OpenAI API is not connected."
        )


        with st.chat_message(
            "assistant"
        ):

            st.error(
                answer
            )


        assistant_message = (
            create_assistant_message(
                response_type="text",
                study_mode=study_mode,
                student_input=student_input,
                results=[],
                answer_depth=answer_depth,
                top_k=top_k,
                sources_enabled=(
                    sources_enabled
                ),
                explanation_enabled=(
                    explanation_enabled
                ),
                record_student_input=(
                    record_student_input
                ),
                content=answer,
                evaluation_eligible=False,
            )
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


            assistant_message = (
                create_assistant_message(
                    response_type="text",
                    study_mode=study_mode,
                    student_input=student_input,
                    results=[],
                    answer_depth=answer_depth,
                    top_k=top_k,
                    sources_enabled=(
                        sources_enabled
                    ),
                    explanation_enabled=(
                        explanation_enabled
                    ),
                    record_student_input=(
                        record_student_input
                    ),
                    content=answer,
                )
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


            assistant_message = (
                create_assistant_message(
                    response_type="text",
                    study_mode=study_mode,
                    student_input=student_input,
                    results=[],
                    answer_depth=answer_depth,
                    top_k=top_k,
                    sources_enabled=(
                        sources_enabled
                    ),
                    explanation_enabled=(
                        explanation_enabled
                    ),
                    record_student_input=(
                        record_student_input
                    ),
                    content=answer,
                    evaluation_eligible=False,
                )
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


        # -------------------------------------------------
        # NO EVIDENCE
        # -------------------------------------------------

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


            assistant_message = (
                create_assistant_message(
                    response_type="text",
                    study_mode=study_mode,
                    student_input=student_input,
                    results=[],
                    answer_depth=answer_depth,
                    top_k=top_k,
                    sources_enabled=(
                        sources_enabled
                    ),
                    explanation_enabled=(
                        explanation_enabled
                    ),
                    record_student_input=(
                        record_student_input
                    ),
                    content=answer,
                )
            )


        # -------------------------------------------------
        # EVIDENCE FOUND
        # -------------------------------------------------

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


                    assistant_message = (
                        create_assistant_message(
                            response_type="flashcards",
                            study_mode=study_mode,
                            student_input=student_input,
                            results=results,
                            answer_depth=answer_depth,
                            top_k=top_k,
                            sources_enabled=(
                                sources_enabled
                            ),
                            explanation_enabled=(
                                explanation_enabled
                            ),
                            record_student_input=(
                                record_student_input
                            ),
                            cards=cards,
                        )
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


                    assistant_message = (
                        create_assistant_message(
                            response_type="quiz",
                            study_mode=study_mode,
                            student_input=student_input,
                            results=results,
                            answer_depth=answer_depth,
                            top_k=top_k,
                            sources_enabled=(
                                sources_enabled
                            ),
                            explanation_enabled=(
                                explanation_enabled
                            ),
                            record_student_input=(
                                record_student_input
                            ),
                            questions=questions,
                        )
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


                    assistant_message = (
                        create_assistant_message(
                            response_type="text",
                            study_mode=study_mode,
                            student_input=student_input,
                            results=results,
                            answer_depth=answer_depth,
                            top_k=top_k,
                            sources_enabled=(
                                sources_enabled
                            ),
                            explanation_enabled=(
                                explanation_enabled
                            ),
                            record_student_input=(
                                record_student_input
                            ),
                            content=answer,
                        )
                    )


                # =========================================
                # HINT / SIMPLE / UNDERSTANDING
                # =========================================

                else:

                    with st.spinner(
                        f"Creating {study_mode}..."
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


                    assistant_message = (
                        create_assistant_message(
                            response_type="text",
                            study_mode=study_mode,
                            student_input=student_input,
                            results=results,
                            answer_depth=answer_depth,
                            top_k=top_k,
                            sources_enabled=(
                                sources_enabled
                            ),
                            explanation_enabled=(
                                explanation_enabled
                            ),
                            record_student_input=(
                                record_student_input
                            ),
                            content=answer,
                        )
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


                assistant_message = (
                    create_assistant_message(
                        response_type="text",
                        study_mode=study_mode,
                        student_input=student_input,
                        results=results,
                        answer_depth=answer_depth,
                        top_k=top_k,
                        sources_enabled=(
                            sources_enabled
                        ),
                        explanation_enabled=(
                            explanation_enabled
                        ),
                        record_student_input=(
                            record_student_input
                        ),
                        content=answer,
                        evaluation_eligible=False,
                    )
                )


    # =====================================================
    # SAVE ASSISTANT MESSAGE
    # =====================================================

    if assistant_message:

        st.session_state.messages.append(
            assistant_message
        )


        with st.chat_message(
            "assistant"
        ):

            render_feedback_form(
                assistant_message
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
    "Research Evaluation · "
    "Responsible AI · "
    "Josaphat Boesinga"
)