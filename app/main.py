import streamlit as st

from config import (
    APP_NAME,
    APP_SUBTITLE,
    RESEARCH_QUESTION,
    DISCLAIMER,
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
    Temporary response generator for Milestone 2.

    This will be replaced by the real AI + retrieval
    pipeline in later milestones.
    """

    if answer_depth == "Brief":
        response = (
            f"You asked: **{question}**\n\n"
            "This is currently a prototype response. "
            "The AI reasoning system will be connected "
            "in a later milestone."
        )

    elif answer_depth == "Detailed":
        response = (
            f"You asked: **{question}**\n\n"
            "AI Study Buddy 2.0 is currently operating in "
            "**prototype mode**. The purpose of this milestone "
            "is to test the learner interface, interaction flow, "
            "and student controls before connecting the full "
            "AI system.\n\n"
            "In the next development stages, the assistant will "
            "retrieve information from uploaded learning materials "
            "and generate source-grounded explanations."
        )

    else:
        response = (
            f"You asked: **{question}**\n\n"
            "Let's approach this as a learning problem.\n\n"
            "Rather than immediately giving you a final answer, "
            "AI Study Buddy will eventually help identify relevant "
            "concepts, retrieve supporting course material, and "
            "guide you toward understanding the solution.\n\n"
            "For now, this response demonstrates the planned "
            "interactive tutoring experience."
        )

    if explanation_enabled:
        response += (
            "\n\n---\n\n"
            "### 💡 Why am I showing this response?\n\n"
            "You enabled the **Explainability** option. "
            "Future versions will explain what evidence was used, "
            "how the response was constructed, and what limitations "
            "the answer may have."
        )

    if sources_enabled:
        response += (
            "\n\n---\n\n"
            "### 📚 Supporting Sources\n\n"
            "*No study materials have been uploaded yet.*\n\n"
            "Source-grounded retrieval will be introduced in "
            "Milestone 3 and Milestone 4."
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
        help=(
            "Future versions will explain why the assistant "
            "generated a particular response."
        ),
    )

    sources_enabled = st.toggle(
        "Show supporting sources",
        value=True,
        help=(
            "Future versions will display evidence from "
            "your uploaded study material."
        ),
    )

    st.divider()

    st.subheader("Research Mode")

    st.caption(
        "These controls will later allow us to study how "
        "transparency affects trust and usefulness."
    )

    st.info(RESEARCH_QUESTION)

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
# RESEARCH STATUS
# ---------------------------------------------------------

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.metric(
        "Development Stage",
        "Milestone 2",
    )

with status_col2:
    st.metric(
        "AI Mode",
        "Prototype",
    )

with status_col3:
    st.metric(
        "Source Grounding",
        "Coming Next",
    )


st.divider()


# ---------------------------------------------------------
# INTRODUCTION
# ---------------------------------------------------------

if len(st.session_state.messages) == 0:

    st.markdown(
        """
        ### Welcome 👋

        AI Study Buddy is being developed as both an educational
        application and a human-centered AI research project.

        You will eventually be able to:

        - Upload your own study materials
        - Ask questions about those materials
        - Receive source-grounded answers
        - See why information was recommended
        - Request hints instead of complete answers
        - Generate quizzes and flashcards
        - Evaluate the usefulness and trustworthiness of responses

        **Try asking a question below to test the prototype interface.**
        """
    )


# ---------------------------------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ---------------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------------

question = st.chat_input(
    "Ask AI Study Buddy a question..."
)


if question:

    # Save student question
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    # Show user message
    with st.chat_message("user"):

        st.markdown(question)


    # Generate prototype answer
    response = generate_prototype_response(
        question=question,
        answer_depth=answer_depth,
        explanation_enabled=explanation_enabled,
        sources_enabled=sources_enabled,
    )


    # Show assistant response
    with st.chat_message("assistant"):

        st.markdown(response)


    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )


    # -----------------------------------------------------
    # PROTOTYPE FEEDBACK
    # -----------------------------------------------------

    st.markdown("### 📊 Evaluate this response")

    st.caption(
        "This feedback interface will later support "
        "the research evaluation component."
    )

    feedback_col1, feedback_col2, feedback_col3 = st.columns(3)

    with feedback_col1:

        st.slider(
            "Usefulness",
            min_value=1,
            max_value=5,
            value=3,
            key=f"usefulness_{len(st.session_state.messages)}",
        )

    with feedback_col2:

        st.slider(
            "Trust",
            min_value=1,
            max_value=5,
            value=3,
            key=f"trust_{len(st.session_state.messages)}",
        )

    with feedback_col3:

        st.slider(
            "Clarity",
            min_value=1,
            max_value=5,
            value=3,
            key=f"clarity_{len(st.session_state.messages)}",
        )

    source_helpful = st.radio(
        "Would supporting evidence help you evaluate this answer?",
        ["Yes", "No", "Not sure"],
        horizontal=True,
        key=f"source_{len(st.session_state.messages)}",
    )

    st.caption(
        "Feedback is not stored yet. Data collection will be "
        "implemented later after the research design is finalized."
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "AI Study Buddy 2.0 · Human-Centered AI · "
    "Responsible AI · Education · Josaphat Boesinga"
)
