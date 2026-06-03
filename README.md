# Prompt Classifier

Classifies a prompt as **convergent** (one correct answer — facts, math, code)
vs. **divergent** (open-ended — brainstorming, opinion, creative), and raises
an **overreliance warning** when a prompt is verifiable *and* high-stakes.

![stack](https://img.shields.io/badge/stack-Python%20·%20FastAPI%20·%20React-1f6feb)

## Why

People over-trust AI exactly where it's most dangerous: confident-sounding
answers to *checkable, high-stakes* questions (a medication dose, a legal
deadline, a tax figure). This tool flags those cases so a UI can nudge the user
to verify — while leaving genuinely open-ended creative prompts alone.

## How it classifies

A transparent logistic-style scorer over interpretable features — no training
data, every decision explainable:

- convergent cues (`what is`, `calculate`, `define`, `solve`, …)
- divergent cues (`brainstorm`, `imagine`, `opinion`, `write a story`, …)
- presence of numbers, list requests, question marks, length
- high-stakes domain terms (`dosage`, `legal`, `deadline`, `voltage`, …)

Output: `label`, `convergent_probability`, `confidence`,
`overreliance_risk` (low/moderate/high), and a `warning` string when relevant.

## Run it

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # http://localhost:5173  (proxies /api -> :8000)
```

## API
```http
POST /classify   { "prompt": "What dose of ibuprofen for a child?" }
->  { "label": "convergent", "overreliance_risk": "high", "warning": "..." , ... }
```

## Tests
```bash
cd backend && python test_classifier.py    # or: pytest
```

Covers convergent facts/math, divergent brainstorm/creative, the high-stakes
overreliance warning, and probability bounds.
