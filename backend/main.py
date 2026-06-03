"""FastAPI service exposing the prompt classifier."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from classifier import classify

app = FastAPI(title="Prompt Classifier", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class ClassifyRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classify")
def classify_prompt(req: ClassifyRequest):
    return classify(req.prompt).as_dict()
