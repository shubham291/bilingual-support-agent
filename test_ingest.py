from rag import load_documents, split_documents, build_store, retrieve, cite

docs = load_documents("data/policies")                       # should skip the copy
chunks = split_documents(docs)
print(f"{len(docs)} documents → {len(chunks)} chunks\n")

# 1. Prove the character positions are EXACT
bodies = {d.metadata["doc_id"]: d.page_content for d in docs}   # dict comprehension: doc_id → full text
for c in chunks:
    m = c.metadata
    assert bodies[m["doc_id"]][m["start_index"]:m["end_index"]] == c.page_content
print("✅ Every chunk's position points to its exact text\n")

store = build_store(chunks)

# 2. Access filter: same question, two audiences
q = "How are visa cases escalated to a supervisor?"
print("Customer sees:", [cite(c) for c in retrieve(store, q, audience="public")])
print("\nStaff sees:   ", [cite(c) for c in retrieve(store, q, audience="staff")])