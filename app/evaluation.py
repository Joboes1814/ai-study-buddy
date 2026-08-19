import csv
import io

from datetime import datetime, timezone
from uuid import uuid4


# =========================================================
# DATASET COLUMNS
# =========================================================

EVALUATION_FIELDS = [
    "timestamp_utc",
    "session_id",
    "interaction_id",
    "study_mode",
    "response_type",
    "document_name",
    "answer_depth",
    "top_k",
    "source_count",
    "best_similarity_percent",
    "sources_visible",
    "source_explanation_enabled",
    "student_input",
    "usefulness",
    "trust",
    "clarity",
    "sense_of_control",
    "active_involvement",
    "notes",
]


# =========================================================
# IDENTIFIERS
# =========================================================

def create_session_id():
    """
    Create a random anonymous identifier
    for the current Study Buddy session.
    """

    return uuid4().hex[:12]


def create_interaction_id():
    """
    Create a random identifier for one
    learner-AI interaction.
    """

    return uuid4().hex[:12]


# =========================================================
# TIME
# =========================================================

def current_utc_timestamp():
    """
    Return an ISO-formatted UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# =========================================================
# INTERACTION METADATA
# =========================================================

def build_interaction_metadata(
    session_id,
    interaction_id,
    study_mode,
    response_type,
    document_name,
    answer_depth,
    top_k,
    results,
    sources_visible,
    source_explanation_enabled,
    student_input,
    record_student_input=False,
):
    """
    Describe the conditions under which
    an AI response was produced.

    We intentionally do NOT store:
    - uploaded document text
    - retrieved passage text
    - AI response text

    Student input is stored only when
    the user explicitly enables it.
    """

    if results:

        best_similarity = max(
            result.get(
                "score",
                0,
            )
            for result in results
        )

        best_similarity_percent = round(
            best_similarity * 100,
            2,
        )

    else:

        best_similarity_percent = 0.0


    return {
        "timestamp_utc":
            current_utc_timestamp(),

        "session_id":
            session_id,

        "interaction_id":
            interaction_id,

        "study_mode":
            study_mode,

        "response_type":
            response_type,

        "document_name":
            document_name or "",

        "answer_depth":
            answer_depth,

        "top_k":
            top_k,

        "source_count":
            len(results),

        "best_similarity_percent":
            best_similarity_percent,

        "sources_visible":
            sources_visible,

        "source_explanation_enabled":
            source_explanation_enabled,

        "student_input":
            (
                student_input
                if record_student_input
                else ""
            ),
    }


# =========================================================
# FEEDBACK RECORD
# =========================================================

def build_feedback_record(
    metadata,
    usefulness,
    trust,
    clarity,
    sense_of_control,
    active_involvement,
    notes="",
):
    """
    Combine system metadata with learner ratings.
    """

    record = dict(metadata)

    record.update(
        {
            "usefulness":
                usefulness,

            "trust":
                trust,

            "clarity":
                clarity,

            "sense_of_control":
                sense_of_control,

            "active_involvement":
                active_involvement,

            "notes":
                notes.strip(),
        }
    )

    return record


# =========================================================
# CSV EXPORT
# =========================================================

def records_to_csv(records):
    """
    Convert evaluation records into CSV text.
    """

    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=EVALUATION_FIELDS,
        extrasaction="ignore",
    )

    writer.writeheader()

    for record in records:

        writer.writerow(
            {
                field:
                    record.get(
                        field,
                        ""
                    )
                for field in EVALUATION_FIELDS
            }
        )

    return output.getvalue()


# =========================================================
# SUMMARY STATISTICS
# =========================================================

def calculate_average(
    records,
    field,
):
    """
    Calculate the average for one numerical rating.
    """

    if not records:
        return None

    values = [
        record[field]
        for record in records
        if isinstance(
            record.get(field),
            (int, float),
        )
    ]

    if not values:
        return None

    return sum(values) / len(values)


def evaluation_summary(records):
    """
    Return average learner ratings.
    """

    return {
        "usefulness":
            calculate_average(
                records,
                "usefulness",
            ),

        "trust":
            calculate_average(
                records,
                "trust",
            ),

        "clarity":
            calculate_average(
                records,
                "clarity",
            ),

        "sense_of_control":
            calculate_average(
                records,
                "sense_of_control",
            ),
    }