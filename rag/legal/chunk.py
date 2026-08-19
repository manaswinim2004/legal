import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.legal.load import load_legal_documents

SECTION_PATTERN=re.compile(r"(?im)^\s*(\d+[A-Za-z]?)\.\s+")
CHAPTER_PATTERN=re.compile(r"(?im)^\s*CHAPTER\s+([IVXLCDM0-9A-Z]+)(?:\s*[-–—:]?\s*(.*))?$")

def extract_chapter(text):
    match=CHAPTER_PATTERN.search(text)
    if not match:
        return None
    number=match.group(1)
    title=(match.group(2) or "").strip()
    return f"Chapter {number} - {title}" if title else f"Chapter {number}"

def split_into_sections(text):
    matches=list(SECTION_PATTERN.finditer(text))

    if not matches:
        return [(text.strip(),None)]

    blocks=[]

    if matches[0].start()>0:
        preamble=text[:matches[0].start()].strip()
        if preamble:
            blocks.append((preamble,None))

    for i,match in enumerate(matches):
        start=match.start()
        end=matches[i+1].start() if i+1<len(matches) else len(text)
        block=text[start:end].strip()

        if block:
            blocks.append((block,match.group(1)))

    return blocks

def chunk_legal_documents(documents):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=3800,
        chunk_overlap=400,
        separators=["\n\n","\n",". ","; ",", "," ",""]
    )

    final_chunks=[]

    for document in documents:
        sections=split_into_sections(document.page_content)
        current_chapter=None

        for block_text,section_number in sections:
            chapter=extract_chapter(block_text)

            if chapter:
                current_chapter=chapter

            metadata=dict(document.metadata)
            metadata["chapter"]=current_chapter

            if section_number:
                metadata["section"]=section_number

            temp=Document(
                page_content=block_text,
                metadata=metadata
            )

            split_chunks=splitter.split_documents([temp])

            for i,chunk in enumerate(split_chunks):
                chunk.metadata["chunk_index"]=i
                chunk.metadata["chunk_count"]=len(split_chunks)
                final_chunks.append(chunk)

    return final_chunks

def main():
    print("========== LEGAL DOCUMENT CHUNKING ==========")

    documents=load_legal_documents()
    print(f"\nActs/PDFs loaded: {len(documents)}")
    print(f"Total pages: {sum(d.metadata['pages'] for d in documents)}")

    chunks=chunk_legal_documents(documents)

    print(f"Generated final chunks: {len(chunks)}")

    print("\n========== SAMPLE CHUNKS ==========")

    for i,chunk in enumerate(chunks[:15],1):
        print(f"\n[{i}]")
        print(f"Act:     {chunk.metadata.get('act')}")
        print(f"Domain:  {chunk.metadata.get('domain')}")
        print(f"Chapter: {chunk.metadata.get('chapter')}")
        print(f"Section: {chunk.metadata.get('section')}")
        print(f"Chunk:   {chunk.metadata.get('chunk_index')+1}/{chunk.metadata.get('chunk_count')}")
        print(f"Chars:   {len(chunk.page_content)}")
        print(chunk.page_content[:700])
        print("-"*70)

if __name__=="__main__":
    main()