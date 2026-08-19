from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

EMBEDDING_MODEL="BAAI/bge-small-en-v1.5"
VECTOR_STORE_PATH="vector-store/legal"
COLLECTION_NAME="legal_laws"
TOP_K=5

def get_retriever():
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

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k":TOP_K}
    )

def main():
    query=input("\nEnter legal question: ")

    retriever=get_retriever()
    results=retriever.invoke(query)

    print(f"\n========== TOP {len(results)} RESULTS ==========")

    for i,document in enumerate(results,1):
        print(f"\n[{i}]")
        print(f"Act: {document.metadata.get('act')}")
        print(f"Domain: {document.metadata.get('domain')}")
        print(f"Chapter: {document.metadata.get('chapter')}")
        print(f"Section: {document.metadata.get('section')}")
        print(f"\n{document.page_content[:1500]}")
        print("-"*70)

if __name__=="__main__":
    main()