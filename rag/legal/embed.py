import os

os.environ["TOKENIZERS_PARALLELISM"]="false"
os.environ["OMP_NUM_THREADS"]="1"
os.environ["MKL_NUM_THREADS"]="1"

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from rag.legal.load import load_legal_documents
from rag.legal.chunk import chunk_legal_documents

EMBEDDING_MODEL="BAAI/bge-small-en-v1.5"
VECTOR_STORE_PATH="vector-store/legal"
COLLECTION_NAME="legal_laws"
BATCH_SIZE=64

def main():
    print("Loading legal documents...")
    documents=load_legal_documents()
    print(f"Acts/PDFs loaded: {len(documents)}")

    print("Creating legal chunks...")
    chunks=chunk_legal_documents(documents)
    print(f"Chunks created: {len(chunks)}")

    print(f"Loading embedding model: {EMBEDDING_MODEL}")

    embeddings=HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device":"cpu"},
        encode_kwargs={"normalize_embeddings":True}
    )

    vector_store=Chroma(
        embedding_function=embeddings,
        persist_directory=VECTOR_STORE_PATH,
        collection_name=COLLECTION_NAME
    )

    total=len(chunks)

    for start in range(0,total,BATCH_SIZE):
        end=min(start+BATCH_SIZE,total)
        batch=chunks[start:end]
        ids=[f"legal_{i}" for i in range(start,end)]

        vector_store.add_documents(
            documents=batch,
            ids=ids
        )

        print(f"Embedded {end}/{total}")

    print("========== EMBEDDING COMPLETE ==========")
    print(f"Embedded: {total}")
    print(f"Database: {VECTOR_STORE_PATH}")

if __name__=="__main__":
    main()