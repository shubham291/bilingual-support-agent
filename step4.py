from typing import Literal                    # Literal = "only these exact values allowed"
from pydantic import BaseModel, ValidationError

# The SHAPE of a triage result (like a Zod schema)
class Triage(BaseModel):
    language: Literal["en", "ar"]                             # like z.enum(['en', 'ar'])
    category: Literal["visa", "emirates_id", "bills", "fines", "other"]
    urgency: Literal["low", "medium", "high"]
    summary: str                                              # like z.string()

# 1. Good data → becomes a Triage object
good = Triage(language="en", category="visa", urgency="high", summary="Visa expires tomorrow")
print(good)
print(good.urgency)                          # dot access, like a TypeScript object

# 2. Bad data → Pydantic refuses it
try:
    bad = Triage(language="fr", category="visa", urgency="super high", summary="...")
except ValidationError as e:                 # try/except = try/catch
    print("❌ Rejected:")
    print(e)