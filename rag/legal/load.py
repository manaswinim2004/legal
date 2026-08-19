import re
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

LEGAL_KNOWLEDGE_PATH=Path("legal_knowledge")

def clean_page_text(text):
    text=re.sub(r"^\s*SEC\.\s*\d+\s*\]\s*THE GAZETTE OF INDIA.*$", "", text, flags=re.MULTILINE|re.IGNORECASE)
    text=re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def load_legal_documents():
    documents=[]

    for pdf_path in sorted(LEGAL_KNOWLEDGE_PATH.rglob("*.pdf")):
        domain=pdf_path.parent.name
        act=pdf_path.stem

        print(f"Loading: {pdf_path}")

        pages=PyPDFLoader(str(pdf_path)).load()

        if not pages:
            print("  Skipped: no pages")
            continue

        page_texts=[]

        for page in pages:
            text=clean_page_text(page.page_content)
            if text:
                page_texts.append(text)

        text="\n\n".join(page_texts)

        metadata={
            "source":pdf_path.name,
            "act":act,
            "domain":domain,
            "pages":len(pages)
        }

        documents.append(
            Document(
                page_content=text,
                metadata=metadata
            )
        )

        print(f"  Loaded: {len(pages)} pages")

    return documents

def main():
    print("========== LEGAL DOCUMENT LOADING ==========")

    documents=load_legal_documents()

    print(f"\nActs/PDFs loaded: {len(documents)}")
    print(f"Total pages: {sum(d.metadata['pages'] for d in documents)}")

if __name__=="__main__":
    main()