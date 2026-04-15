import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def detect_intent(query):
    query = query.lower()

    if any(x in query for x in ["phạt", "bao nhiêu tiền", "mức phạt"]):
        return "penalty"
    if any(x in query for x in ["là gì", "nghĩa là", "định nghĩa"]):
        return "definition"

    return "general"
