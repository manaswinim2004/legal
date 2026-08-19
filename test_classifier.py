from utils.document_processor import DocumentProcessor
from utils.clause_splitter import ClauseSplitter
from tools.clause_classifier import ClauseClassifier


MODEL_PATH = "models/bert"
DOCUMENT_PATH = "NDAA.docx"


def main():

    # ---------------------------------------------
    # 1. Process document
    # ---------------------------------------------

    processor = DocumentProcessor()

    document = processor.process(
        DOCUMENT_PATH
    )

    print(
        f"\nProcessed: {document['source']}"
    )

    # ---------------------------------------------
    # 2. Split document
    # ---------------------------------------------

    splitter = ClauseSplitter()

    clauses = splitter.split(
        document
    )

    print(
        f"Detected clauses: {len(clauses)}"
    )

    # ---------------------------------------------
    # 3. Load BERT
    # ---------------------------------------------

    classifier = ClauseClassifier(
        MODEL_PATH,
        confidence_threshold=0.50,
    )

    # ---------------------------------------------
    # 4. Classify
    # ---------------------------------------------

    results = classifier.classify_clauses(
        clauses
    )

    # ---------------------------------------------
    # 5. Display
    # ---------------------------------------------

    print(
        "\n========== BERT CLASSIFICATION ==========\n"
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"[{index}] {result['title']}"
        )

        print(
            f"Status:     {result['status']}"
        )

        print(
            f"Label:      {result.get('label')}"
        )

        print(
            f"Confidence: {result['confidence']}"
        )

        if result["status"] == "uncertain":

            print(
                f"Best guess: "
                f"{result.get('predicted_label')}"
            )

            print(
                "→ This clause should be handled "
                "by the fallback path."
            )

        print(
            f"Text: {result['text'][:300]}"
        )

        print("-" * 70)


if __name__ == "__main__":
    main()