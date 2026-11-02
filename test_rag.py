from rag import load_documents, split_documents, build_store, retrieve, answer

# PHASE 1: prepare (once)
docs = load_documents("data/policies")
chunks = split_documents(docs)
store = build_store(chunks)
print(f"Loaded {len(docs)} documents → {len(chunks)} chunks")

# PHASE 2: answer (per question)
questions = [
    "How do I renew my Emirates ID?",
    "My visa expires tomorrow, what happens?",
    "هل يجب أن أرسل رقم هويتي في المحادثة؟",   # "Should I send my ID number in the chat?"
    "What's the best pizza in Dubai?",
]

for q in questions:
    found = retrieve(store, q)
    print(f"\nQ: {q}")
    print("Sources:", [c.metadata["source"] for c in found])
    print("A:", answer(q, found))