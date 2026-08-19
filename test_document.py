import sys

from utils.document_processor import DocumentProcessor
from utils.clause_splitter import ClauseSplitter


def main():

    if len(sys.argv) < 2:
        print("Usage: python test_document.py <file>")
        return

    file_path = sys.argv[1]

    processor = DocumentProcessor()
    splitter = ClauseSplitter()

    # --------------------------------------------------
    # DOCUMENT PROCESSING
    # --------------------------------------------------

    print("\n========== DOCUMENT PROCESSING ==========\n")

    document = processor.process(file_path)

    print(f"Source: {document['source']}")
    print(f"Type:   {document['file_type']}")
    print(f"Characters extracted: {len(document['text'])}")
    print(f"Blocks extracted: {len(document['blocks'])}")

    # --------------------------------------------------
    # STRUCTURED BLOCKS
    # --------------------------------------------------

    print("\n========== STRUCTURED BLOCKS ==========\n")

    for i, block in enumerate(
        document["blocks"][:30],
        start=1,
    ):
        print(
            f"[{i}] "
            f"type={block['type']} "
            f"→ {block['text'][:200]}"
        )

    if len(document["blocks"]) > 30:
        print("\n... remaining blocks omitted ...")

    # --------------------------------------------------
    # CLAUSE SPLITTING
    # --------------------------------------------------

    clauses = splitter.split(document)

    print("\n========== CLAUSE DETECTION ==========\n")

    print(f"Detected clauses: {len(clauses)}")

    for i, clause in enumerate(
        clauses,
        start=1,
    ):
        print(f"\n[{i}] {clause['title']}")
        print("-" * 70)
        print(clause["text"][:700])


if __name__ == "__main__":
    main()