from pypdf import PdfReader


def extract_pdf_text(uploaded_file):
    """
    Extract text from an uploaded PDF.

    Returns:
        dict containing:
        - pages
        - full_text
        - page_count
        - character_count
    """

    reader = PdfReader(uploaded_file)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append(
            {
                "page": page_number,
                "text": text.strip(),
            }
        )

    full_text = "\n\n".join(
        page["text"]
        for page in pages
        if page["text"]
    )

    return {
        "pages": pages,
        "full_text": full_text,
        "page_count": len(reader.pages),
        "character_count": len(full_text),
    }


def extract_txt_text(uploaded_file):
    """
    Extract text from an uploaded TXT file.
    """

    raw_content = uploaded_file.getvalue()

    text = raw_content.decode(
        "utf-8",
        errors="ignore",
    )

    text = text.strip()

    return {
        "pages": [
            {
                "page": 1,
                "text": text,
            }
        ],
        "full_text": text,
        "page_count": 1,
        "character_count": len(text),
    }


def process_uploaded_document(uploaded_file):
    """
    Detect file type and send it to
    the appropriate processor.
    """

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_pdf_text(uploaded_file)

    if file_name.endswith(".txt"):
        return extract_txt_text(uploaded_file)

    raise ValueError(
        "Unsupported file type. "
        "Please upload a PDF or TXT file."
    )
