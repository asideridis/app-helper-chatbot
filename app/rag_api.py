from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="App Helper Chatbot")


class Question(BaseModel):
    question: str


@app.post("/chat")
async def chat(question: Question) -> dict[str, list[str] | str]:
    """Dummy chat endpoint returning a placeholder response in Greek."""
    return {
        "answer": "Δεν βρέθηκε σχετική πληροφορία",
        "sources": [],
    }
