import uuid

from langchain_chroma import Chroma
from langchain_core.documents import Document

from rag.contract.embed import get_embeddings
from rag.contract.chunk import chunk_classified_clauses

TOP_K = 5


class ContractRetriever:
    """
    Per-session, in-memory vector store for an uploaded contract.

    Lifecycle:
        1. Create one instance per uploaded contract.
        2. Call ingest() once after BERT classification.
        3. Call query() for every user message in that session.
        4. The store is garbage-collected when the instance is discarded.

    The BERT clause_type label stored in metadata enables optional
    filtered retrieval — e.g. surface only "Indemnification" clauses
    when the question is clearly about liability.
    """

    def __init__(self, session_id: str | None = None):
        self.session_id = session_id or str(uuid.uuid4())
        self._collection_name = f"contract_{self.session_id.replace('-', '_')}"
        self._store: Chroma | None = None
        self._doc_count: int = 0

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest(self, classified_clauses: list[dict], source: str = "uploaded_contract") -> int:
        """
        Chunk and embed a list of BERT-classified clauses.
        Annotates each clause dict with the source filename before chunking.

        Returns the number of embedded documents.
        """
        for clause in classified_clauses:
            clause.setdefault("source", source)
        documents: list[Document] = chunk_classified_clauses(classified_clauses)
        if documents:
            self._store = Chroma.from_documents(
                documents=documents,
                embedding=get_embeddings(),
                collection_name=self._collection_name,
            )
        else:
            # No clauses extracted — still mark ready so session is valid
            self._store = Chroma(
                embedding_function=get_embeddings(),
                collection_name=self._collection_name,
            )
        self._doc_count = len(documents)
        return self._doc_count

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def query(
        self,
        text: str,
        top_k: int = TOP_K,
        clause_type: str | None = None,
    ) -> list[Document]:
        """
        Retrieve the most relevant contract chunks for a query.

        Args:
            text:        The user's natural-language question.
            top_k:       Number of results.
            clause_type: If provided (from BERT query-time inference),
                         attempt a filtered search first; fall back to
                         unfiltered if no results.
        """
        if self._store is None:
            return []

        retriever_kwargs: dict = {"k": top_k}

        # Try filtered retrieval when a clause type hint is available
        if clause_type:
            try:
                results = self._store.similarity_search(
                    text,
                    k=top_k,
                    filter={"clause_type": clause_type},
                )
                if results:
                    return results
                # No hits with this filter — fall through to unfiltered
            except Exception:
                pass

        return self._store.similarity_search(text, **retriever_kwargs)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def doc_count(self) -> int:
        return self._doc_count

    def is_ready(self) -> bool:
        return self._store is not None

    def clause_type_summary(self) -> dict[str, int]:
        """
        Return a count of clauses by BERT label.
        Useful for the /upload response summary.
        """
        if self._store is None:
            return {}

        try:
            collection = self._store._collection
            results = collection.get(include=["metadatas"])
            counts: dict[str, int] = {}
            for meta in results.get("metadatas", []):
                label = meta.get("clause_type", "Unknown")
                counts[label] = counts.get(label, 0) + 1
            return counts
        except Exception:
            return {}


# ------------------------------------------------------------------
# Session registry — maps session_id → ContractRetriever
# Lives in memory for the lifetime of the FastAPI process.
# ------------------------------------------------------------------

_sessions: dict[str, ContractRetriever] = {}


def create_session() -> ContractRetriever:
    """Create and register a new contract session."""
    retriever = ContractRetriever()
    _sessions[retriever.session_id] = retriever
    return retriever


def get_session(session_id: str) -> ContractRetriever | None:
    """Look up an active session by ID."""
    return _sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """Remove a session (frees memory)."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False
