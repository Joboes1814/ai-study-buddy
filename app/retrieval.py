from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def chunk_document(pages, chunk_size=900, overlap=150):
    """
    Split document pages into smaller overlapping passages.

    Each chunk keeps its original page number so that
    retrieved evidence can be traced back to the source.
    """

    chunks = []

    for page in pages:
        page_number = page["page"]
        text = page["text"].strip()

        if not text:
            continue

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "page": page_number,
                        "text": chunk_text,
                    }
                )

            if end >= len(text):
                break

            start += chunk_size - overlap

    return chunks


def retrieve_relevant_chunks(
    question,
    document,
    top_k=3,
):
    """
    Retrieve the document passages most relevant
    to the student's question using TF-IDF and
    cosine similarity.
    """

    chunks = chunk_document(
        document["pages"]
    )

    if not chunks:
        return []

    chunk_texts = [
        chunk["text"]
        for chunk in chunks
    ]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
    )

    try:
        chunk_matrix = vectorizer.fit_transform(
            chunk_texts
        )

        question_vector = vectorizer.transform(
            [question]
        )

    except ValueError:
        return []

    similarities = cosine_similarity(
        question_vector,
        chunk_matrix,
    ).flatten()

    ranked_indices = similarities.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:

        score = float(
            similarities[index]
        )

        # Ignore passages with zero similarity
        if score <= 0:
            continue

        result = {
            "page": chunks[index]["page"],
            "text": chunks[index]["text"],
            "score": score,
        }

        results.append(result)

    return results