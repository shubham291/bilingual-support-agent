import os
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()                                    # reads .env into the environment

# Talk to Vercel AI Gateway (same key as your Next.js projects)
client = OpenAI(
    api_key=os.getenv("AI_GATEWAY_API_KEY"),
    base_url="https://ai-gateway.vercel.sh/v1",
)

# The form we want the AI to fill (from Step 4)
class Triage(BaseModel):
    language: Literal["en", "ar"]
    category: Literal["visa", "emirates_id", "bills", "fines", "other"]
    urgency: Literal["low", "medium", "high"]
    summary: str

def triage(message: str) -> Triage:
    response = client.chat.completions.parse(
        model="anthropic/claude-sonnet-5",
        messages=[
            {"role": "system", "content": (
    "You triage UAE government service messages. Write the summary in English. "
    "Urgency: high = the user is blocked or a deadline is within 48 hours "
    "(expiring visa, locked account, can't pay); medium = a problem but not blocking; low = a general question."
)},
            {"role": "user", "content": message},
        ],
        response_format=Triage,                  # ← "fill in THIS form"
    )
    return response.choices[0].message.parsed    # already a Triage object, validated

result = triage("حسابي مقفول وما أقدر أدفع المخالفة")
print(result)
print("Urgency:", result.urgency)