from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

MAX_CLAUSE_CHARS = 1800
CHUNK_OVERLAP = 150


def chunk_classified_clauses(classified_clauses: list[dict]) -> list[Document]:
    """
    Convert BERT-classified clauses into LangChain Documents,
    sub-chunking any clause that exceeds MAX_CLAUSE_CHARS.

    Each Document carries metadata:
        clause_type  - BERT label  (e.g. "Indemnification")
        confidence   - BERT score
        bert_status  - "classified" | "uncertain"
        title        - clause title from the splitter
        source       - original document filename
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CLAUSE_CHARS,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
    )

    documents: list[Document] = []

    for clause in classified_clauses:

        text = clause.get("text", "").strip()

        if not text:
            continue

        # Metadata from BERT output
        metadata = {
            "clause_type": clause.get("label") or clause.get("predicted_label", "Unknown"),
            "confidence": clause.get("confidence", 0.0),
            "bert_status": clause.get("status", "uncertain"),
            "title": clause.get("title", "Clause"),
            "source": clause.get("source", "uploaded_contract"),
        }

        if len(text) <= MAX_CLAUSE_CHARS:
            documents.append(
                Document(page_content=text, metadata=metadata)
            )
        else:

            sub_chunks = splitter.split_text(text)
            for i, chunk_text in enumerate(sub_chunks):
                chunk_meta = dict(metadata)
                chunk_meta["sub_chunk"] = i
                chunk_meta["sub_chunk_total"] = len(sub_chunks)
                documents.append(
                    Document(page_content=chunk_text, metadata=chunk_meta)
                )

    return documents
