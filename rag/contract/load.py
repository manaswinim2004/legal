from utils.document_processor import DocumentProcessor
from utils.clause_splitter import ClauseSplitter
from tools.clause_classifier import ClauseClassifier

_classifier: ClauseClassifier | None = None
_MODEL_PATH = "models/bert"


def _get_classifier() -> ClauseClassifier:
    global _classifier
    if _classifier is None:
        _classifier = ClauseClassifier(model_path=_MODEL_PATH)
    return _classifier


def load_contract(file_path: str, source_name: str | None = None) -> dict:
    processor = DocumentProcessor()
    document = processor.process(file_path)

    splitter = ClauseSplitter()
    clauses = splitter.split(document)

    classifier = _get_classifier()
    classified = classifier.classify_clauses(clauses)

    return {
        "source": source_name or document["source"],
        "clauses": classified,
    }
