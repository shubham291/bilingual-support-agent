from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from triage import Triage, triage
from guardrails import normalize, mask_pii, looks_like_injection
from rag import retrieve, answer                       # NEW
from knowledge import STORE                            # NEW: built once at startup
from fastapi.responses import RedirectResponse

app = FastAPI(title="Support Triage API")

OUT_OF_SCOPE_REPLY = {                                  # NEW: fixed replies, not AI-written
    "en": "Sorry, I can only help with UAE government services such as visas, Emirates ID, bills and fines.",
    "ar": "عذراً، يمكنني المساعدة فقط في الخدمات الحكومية في الإمارات مثل التأشيرات والهوية الإماراتية والفواتير والمخالفات.",
}

class TriageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

class TriageResponse(BaseModel):
    blocked: bool
    reason: Optional[str] = None
    pii_found: List[str] = []
    triage: Optional[Triage] = None
    reply: Optional[str] = None                         # NEW: the drafted answer
    sources: List[str] = []                             # NEW: which policies it used
    needs_human: bool = False                           # NEW: escalate to a person?

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", include_in_schema=False)     # the home address; hidden from the docs page
def home():
    return RedirectResponse("/docs")       # send visitors straight to the test page

@app.post("/triage", response_model=TriageResponse)
def triage_endpoint(body: TriageRequest):
    text = normalize(body.message)

    if looks_like_injection(text):
        return TriageResponse(blocked=True, reason="possible prompt injection")

    masked, pii_found = mask_pii(text)

    try:
        t = triage(masked)

        # NEW: topic guardrail, enforced by code
        if t.category == "other":
            return TriageResponse(
                blocked=False, pii_found=pii_found, triage=t,
                reply=OUT_OF_SCOPE_REPLY[t.language],
            )

        # NEW: RAG, find facts and draft a reply (from the MASKED text)
        chunks = retrieve(STORE, masked)
        reply = answer(masked, chunks)
    except Exception as e:
        print("pipeline failed:", e)
        raise HTTPException(status_code=502, detail="AI service failed, please retry")

    return TriageResponse(
        blocked=False,
        pii_found=pii_found,
        triage=t,
        reply=reply,
        sources=sorted({c.metadata["source"] for c in chunks}),   # NEW: unique source names
        needs_human=(t.urgency == "high"),                         # NEW: escalation rule
    )



# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field
# from triage import Triage, triage
# from guardrails import normalize, mask_pii, looks_like_injection    # ← NEW
# from typing import Optional

# app = FastAPI(title="Support Triage API")

# class TriageRequest(BaseModel):
#     message: str = Field(min_length=1, max_length=2000)

# # ← NEW: the response now also reports what the guardrails did
# class TriageResponse(BaseModel):
#     blocked: bool                      # was the message stopped?
#     reason: Optional[str] = None         # why (if blocked)
#     pii_found: list[str] = []          # what personal data was masked
#     triage: Optional[Triage] = None       # the AI result (None if blocked)

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/triage", response_model=TriageResponse)
# def triage_endpoint(body: TriageRequest):
#     text = normalize(body.message)

#     # Checkpoint 1: injection → stop BEFORE calling the AI (no cost, no risk)
#     if looks_like_injection(text):
#         return TriageResponse(blocked=True, reason="possible prompt injection")

#     # Checkpoint 2: hide personal data BEFORE it reaches the AI
#     masked, pii_found = mask_pii(text)

#     try:
#         result = triage(masked)                     # the AI only sees the masked text
#     except Exception as e:
#         print("triage failed:", e)
#         raise HTTPException(status_code=502, detail="AI service failed, please retry")

#     return TriageResponse(blocked=False, pii_found=pii_found, triage=result)