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


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide",
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document" not in st.session_state:
    st.session_state.document = None

if "document_name" not in st.session_state:
    st.session_state.document_name = None


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def generate_prototype_response(
    question: str,
    answer_depth: str,
    explanation_enabled: bool,
    sources_enabled: bool,
):
    """
    Temporary response generator.

    Milestone 4 will replace this with
    document retrieval + grounded answers.
    """

    if answer_depth == "Brief":

        response = (
            f"You asked: **{question}**\n\n"
            "This is currently a prototype response. "
            "The document has not yet been searched "
            "for relevant evidence."
        )

    elif answer_depth == "Detailed":

        response = (
            f"You asked: **{question}**\n\n"
            "AI Study Buddy 2.0 is currently operating "
            "in **Milestone 3 mode**.\n\n"
            "The application can now accept and process "
            "study materials. In the next milestone, "
            "the assistant will retrieve relevant passages "
            "from the uploaded material and use them to "
            "support its response."
        )

    else:

        response = (
            f"You asked: **{question}**\n\n"
            "Let's approach this as a learning problem.\n\n"
            "Your study material can now be uploaded and "
            "processed. In the next milestone, AI Study Buddy "
            "will identify the most relevant parts of that "
            "material and use them to guide your learning."
        )


    # -----------------------------------------------------
    # EXPLAINABILITY
    # -----------------------------------------------------

    if explanation_enabled:

        response += (
            "\n\n---\n\n"
            "### 💡 Why am I showing this response?\n\n"
            "You enabled the **Explainability** option. "
            "Future responses will explain which evidence "
            "was selected from your study material and why "
            "it was considered relevant."
        )


    # -----------------------------------------------------
    # SOURCES
    # -----------------------------------------------------

    if sources_enabled:

        response += "\n\n---\n\n"

        response += "### 📚 Supporting Sources\n\n"

        if st.session_state.document:

            response += (
                f"Study material loaded: "
                f"**{st.session_state.document_name}**\n\n"
                "The document has been processed successfully.\n\n"
                "Milestone 4 will retrieve and display the "
                "specific passages most relevant to your question."
            )

        else:

            response += (
                "*No study material has been uploaded yet.*\n\n"
                "Upload a PDF or TXT file from the sidebar."
            )

    return response


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.title("🧠 Study Controls")

    st.write(
        "Customize how AI Study Buddy supports your learning."
    )

    st.divider()


    # -----------------------------------------------------
    # RESPONSE SETTINGS
    # -----------------------------------------------------

    answer_depth = st.selectbox(
        "Answer style",
        [
            "Brief",
            "Detailed",
            "Guided Learning",
        ],
        index=1,
        help=(
            "Choose whether you want a short response, "
            "a detailed explanation, or guided learning."
        ),
    )

    explanation_enabled = st.toggle(
        "Explain the AI response",
        value=True,
    )

    sources_enabled = st.toggle(
        "Show supporting sources",
        value=True,
    )


    # -----------------------------------------------------
    # DOCUMENT UPLOAD
    # -----------------------------------------------------

    st.divider()

    st.subheader("📄 Study Material")

    uploaded_file = st.file_uploader(
        "Upload your study material",
        type=["pdf", "txt"],
        help=(
            "Upload a PDF or TXT file. "
            "AI Study Buddy will process the document "
            "for source-grounded learning."
        ),
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

                    document = process_uploaded_document(
                        uploaded_file
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

        document = st.session_state.document

        st.success(
            f"Loaded: {st.session_state.document_name}"
        )

        st.caption(
            f"{document['page_count']} page(s)"
            f" · "
            f"{document['character_count']:,} "
            f"characters extracted"
        )


        # -------------------------------------------------
        # TEXT PREVIEW
        # -------------------------------------------------

        with st.expander(
            "Preview extracted text"
        ):

            if document["full_text"]:

                preview = (
                    document["full_text"][:3000]
                )

                st.text(preview)

                if len(
                    document["full_text"]
                ) > 3000:

                    st.caption(
                        "Preview limited to the "
                        "first 3,000 characters."
                    )

            else:

                st.warning(
                    "No readable text was extracted "
                    "from this document."
                )


        # -------------------------------------------------
        # REMOVE DOCUMENT
        # -------------------------------------------------

        if st.button(
            "Remove Study Material",
            use_container_width=True,
        ):

            st.session_state.document = None

            st.session_state.document_name = None

            st.rerun()


    # -----------------------------------------------------
    # RESEARCH MODE
    # -----------------------------------------------------

    st.divider()

    st.subheader("🔬 Research Mode")

    st.caption(
        "These controls will later help us study "
        "how transparency affects trust and usefulness."
    )

    st.info(RESEARCH_QUESTION)


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


# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------

st.title("🧠 AI Study Buddy 2.0")

st.subheader(
    "Learn with AI — without giving up control of your learning."
)

st.write(APP_SUBTITLE)

st.warning(DISCLAIMER)


# ---------------------------------------------------------
# DEVELOPMENT STATUS
# ---------------------------------------------------------

status_col1, status_col2, status_col3 = (
    st.columns(3)
)


with status_col1:

    st.metric(
        "Development Stage",
        "Milestone 3",
    )


with status_col2:

    st.metric(
        "AI Mode",
        "Prototype",
    )


with status_col3:

    document_status = (
        "Document Ready"
        if st.session_state.document
        else "No Document"
    )

    st.metric(
        "Study Material",
        document_status,
    )


st.divider()


# ---------------------------------------------------------
# INTRODUCTION
# ---------------------------------------------------------

if len(st.session_state.messages) == 0:

    st.markdown(
        """
        ### Welcome 👋

        AI Study Buddy is being developed as both
        an educational application and a
        human-centered AI research project.

        **Milestone 3 adds study material processing.**

        You can now:

        - Upload PDF study material
        - Upload TXT notes
        - Extract readable text
        - Preview the extracted content
        - Keep the document available during the session

        Coming next:

        - Search the uploaded document
        - Retrieve relevant passages
        - Show evidence with answers
        - Generate source-grounded explanations

        **Upload a document from the sidebar and try it.**
        """
    )


# ---------------------------------------------------------
# DOCUMENT SUMMARY
# ---------------------------------------------------------

if st.session_state.document:

    document = st.session_state.document

    st.info(
        f"📄 Current study material: "
        f"**{st.session_state.document_name}**"
        f" — {document['page_count']} page(s), "
        f"{document['character_count']:,} characters."
    )


# ---------------------------------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ---------------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------------

question = st.chat_input(
    "Ask AI Study Buddy a question..."
)


if question:

    # -----------------------------------------------------
    # SAVE STUDENT QUESTION
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # -----------------------------------------------------
    # DISPLAY STUDENT QUESTION
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    # -----------------------------------------------------
    # GENERATE RESPONSE
    # -----------------------------------------------------

    response = generate_prototype_response(
        question=question,
        answer_depth=answer_depth,
        explanation_enabled=explanation_enabled,
        sources_enabled=sources_enabled,
    )


    # -----------------------------------------------------
    # DISPLAY ASSISTANT RESPONSE
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        st.markdown(response)


    # -----------------------------------------------------
    # SAVE ASSISTANT RESPONSE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )


    # -----------------------------------------------------
    # FEEDBACK
    # -----------------------------------------------------

    st.markdown(
        "### 📊 Evaluate this response"
    )

    st.caption(
        "Feedback is currently experimental "
        "and is not being stored."
    )


    feedback_col1, feedback_col2, feedback_col3 = (
        st.columns(3)
    )


    with feedback_col1:

        st.slider(
            "Usefulness",
            min_value=1,
            max_value=5,
            value=3,
            key=(
                f"usefulness_"
                f"{len(st.session_state.messages)}"
            ),
        )


    with feedback_col2:

        st.slider(
            "Trust",
            min_value=1,
            max_value=5,
            value=3,
            key=(
                f"trust_"
                f"{len(st.session_state.messages)}"
            ),
        )


    with feedback_col3:

        st.slider(
            "Clarity",
            min_value=1,
            max_value=5,
            value=3,
            key=(
                f"clarity_"
                f"{len(st.session_state.messages)}"
            ),
        )


    st.radio(
        "Would supporting evidence help you "
        "evaluate this answer?",
        [
            "Yes",
            "No",
            "Not sure",
        ],
        horizontal=True,
        key=(
            f"source_"
            f"{len(st.session_state.messages)}"
        ),
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "AI Study Buddy 2.0 · "
    "Human-Centered AI · "
    "Responsible AI · "
    "Education · "
    "Josaphat Boesinga"
)
