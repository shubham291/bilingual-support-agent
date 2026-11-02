import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import hashlib


load_dotenv()
GATEWAY = "https://ai-gateway.vercel.sh/v1"
KEY = os.getenv("AI_GATEWAY_API_KEY")



# The "meaning to numbers" machine (same model as Project 1)
embeddings = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    base_url=GATEWAY,
    api_key=KEY,
    check_embedding_ctx_length=False,   # send plain text, not OpenAI-specific tokens (needed for gateways)
)

# The AI that writes answers
llm = ChatOpenAI(model="anthropic/claude-sonnet-5", base_url=GATEWAY, api_key=KEY, temperature=0)

MIN_SCORE = 0.4   # below this similarity, a chunk doesn't count as relevant (same idea as Project 1)

#splits a file into its labels (the part between ---) and its body (the text)
def parse_front_matter(raw: str) -> tuple[dict, str]:
    """Split the '---' labels at the top of a file from its body text."""
    if not raw.startswith("---"):
        return {}, raw                                   # no labels → whole file is the body
    _, header, body = raw.split("---", 2)                # 3 parts: before, between, after the --- lines
    labels = {}
    for line in header.strip().splitlines():             # e.g. "date: 2026-09-15"
        key, value = line.split(":", 1)                  # split at the FIRST colon only
        labels[key.strip()] = value.strip()
    return labels, body.strip()

def fingerprint(text: str) -> str:
    """Same text (ignoring case and extra spaces) → same 12-character ID."""
    normalized = " ".join(text.lower().split())          # "Hello   World" → "hello world"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]

def load_documents(folder: str) -> list[Document]:
    docs = []
    seen = set()                                         # fingerprints we've already loaded
    for path in sorted(Path(folder).glob("*.md")):
        labels, body = parse_front_matter(path.read_text(encoding="utf-8"))
        doc_id = fingerprint(body)

        if doc_id in seen:                               # same content as an earlier file
            print(f"⏭️  Duplicate skipped: {path.name}")
            continue                                     # continue = skip to the next file
        seen.add(doc_id)

        docs.append(Document(page_content=body, metadata={
            "source": path.stem,
            "doc_id": doc_id,
            "title": labels.get("title", path.stem),     # .get(key, default) = value or fallback
            "date": labels.get("date", "unknown"),
            "audience": labels.get("audience", "public"),   # no label → public
        }))
    return docs

def split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        add_start_index=True,                            # records where each chunk starts
    )
    chunks = splitter.split_documents(docs)

    counters = {}                                        # how many chunks each document has so far
    for c in chunks:
        doc_id = c.metadata["doc_id"]
        n = counters.get(doc_id, 0)
        counters[doc_id] = n + 1
        c.metadata["chunk_id"] = f"{doc_id}-{n}"                                  # e.g. a3f9...-0
        c.metadata["end_index"] = c.metadata["start_index"] + len(c.page_content)
    return chunks

def build_store(chunks: list[Document]) -> InMemoryVectorStore:
    return InMemoryVectorStore.from_documents(chunks, embeddings)

# added access checks - staff and public
def retrieve(store: InMemoryVectorStore, question: str, k: int = 3, audience: str = "public") -> list[Document]:
    allowed = {"public"} if audience == "public" else {"public", "staff"}   # staff see everything
    results = store.similarity_search_with_score(
        question,
        k=k,
        filter=lambda d: d.metadata["audience"] in allowed,                  # checked BEFORE ranking
    )
    return [doc for doc, score in results if score >= MIN_SCORE]

#turns a chunk’s metadata into a readable address.
def cite(chunk: Document) -> str:
    m = chunk.metadata
    return f"{m['source']} · chunk {m['chunk_id']} · chars {m['start_index']}-{m['end_index']} · updated {m['date']}"

def answer(question: str, chunks: list[Document]) -> str:
    if not chunks:                                   # nothing relevant found → refuse, without calling the AI
        return "I don't have information about that. Please contact the relevant government authority."

    sources = "\n\n".join(
        f"[{i}] ({c.metadata['source']}) {c.page_content}"      # numbered, with the source name
        for i, c in enumerate(chunks, start=1)                    # enumerate = loop with a counter
    )
    prompt = f"""You are a UAE government services help desk.
Answer ONLY from the sources below, and cite them like [1].
If the sources don't contain the answer, say you don't have that information.
Reply in the same language as the question.

SOURCES:
{sources}

QUESTION: {question}"""

    return llm.invoke(prompt).content               # .invoke = call the AI; .content = its text



# Rough Flow
#PREPARE (once)
#  files ─► load_documents ─────────────► split_documents ──────────────► build_store
#            ├─ parse_front_matter: labels    ├─ add_start_index: positions
 #           └─ fingerprint: doc_id + dedup   └─ chunk_id + end_index

#ANSWER (each question)
# question ─► retrieve (audience filter FIRST, then meaning) ─► answer ─► cite each source