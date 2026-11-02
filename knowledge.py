from rag import load_documents, split_documents, build_store

# This code runs ONCE, when the server starts and first imports this file.
STORE = build_store(split_documents(load_documents("data/policies")))
print(f"Knowledge base ready: {len(STORE.store)} chunks")