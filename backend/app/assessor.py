from __future__ import annotations
from typing import Any, Dict, List
import json
from jsonschema import validate
from .azure_openai import AzureOpenAIClient
from .bank import QUESTION_BANK

DOMAINS = ["A","B","C","D","E","F","G"]

LLM_RESPONSE_SCHEMA = {
  "type": "object",
  "properties": {
    "assistant_text": {"type":"string"},
    "next_question_id": {"type":["string","null"]},
    "scores": {"type":"object", "additionalProperties": {"type":"integer","minimum":0,"maximum":3}},
    "evidence": {"type":"array", "items":{"type":"string"}},
    "done": {"type":"boolean"},
    "report": {"type":["object","null"]}
  },
  "required": ["assistant_text","next_question_id","scores","evidence","done","report"],
  "additionalProperties": False
}

SYSTEM_PROMPT = """You are an AI Literacy Assessor for a defense organization.
Run a short interactive assessment and score the user.

Rules:
- Ask ONE question at a time.
- Never request/process sensitive/classified/personal data. If user shares it, interrupt and ask for a generalized description.
- Adapt next question based on persona and prior answers.
- Score domains A–G with levels 0–3:
  0 Unaware/misconceptions; 1 Aware/basic; 2 Practicing with checks; 3 Proficient/sets standards.
- Evidence tags: MISCONCEPTION, SAFE_PRACTICE, RISK_AWARE, GOV_AWARE, VALIDATION, PROMPT_SKILL.

Return STRICT JSON only:
{
  "assistant_text": string,
  "next_question_id": string|null,
  "scores": { "A":0..3, ... },
  "evidence": [string,...],
  "done": boolean,
  "report": object|null
}

If done=true, report must include:
persona, overall_level(0..3), domain_scores, strengths, growth_areas, top_risks, learning_plan(3), notes.
"""

BANK_BY_ID = {q["id"]: q for q in QUESTION_BANK}

def candidate_questions(persona: str, asked: List[str]) -> List[Dict[str, Any]]:
    out = []
    for q in QUESTION_BANK:
        if q["id"] in asked:
            continue
        if q["persona"] == "ALL" or q["persona"] == persona:
            out.append({"id": q["id"], "domain": q["domain"], "type": q["type"], "prompt": q["prompt"]})
    return out

def overall_level(scores: Dict[str,int]) -> int:
    vals = [scores.get(d, 0) for d in DOMAINS]
    return int(round(sum(vals)/len(vals))) if vals else 0

def build_report(persona: str, scores: Dict[str,int], evidence: List[str], notes: List[str]) -> Dict[str, Any]:
    domain_scores = {d: int(scores.get(d, 0)) for d in DOMAINS}
    sorted_domains = sorted(domain_scores.items(), key=lambda kv: kv[1])
    growth = [d for d,_ in sorted_domains[:2]]
    strengths = [d for d,_ in sorted_domains[-2:]][::-1]
    lvl = overall_level(domain_scores)

    mapping = {
        "C": "Complete 'Safe AI use & data handling' micro-module; practice redaction and approved-tool usage.",
        "F": "Complete 'Validation & hallucinations' micro-module; use a 3-step verify checklist on next 5 uses.",
        "E": "Complete 'Prompting patterns' micro-module; practice context + constraints + format + examples.",
        "G": "Complete 'Governance basics' micro-module; learn escalation paths and approvals for AI use cases.",
        "D": "Complete 'Responsible AI' micro-module; apply bias and fairness checks on AI outputs.",
        "B": "Complete 'Use case framing' micro-module; draft 2 use cases with value + risk + owner.",
        "A": "Complete 'AI fundamentals' micro-module; explain GenAI limits (training vs retrieval) to a peer."
    }
    learning = [mapping.get(d, f"Complete the learning module for domain {d}") for d in growth]
    while len(learning) < 3:
        learning.append("Practice: Use AI on a low-risk task and document assumptions, checks, and outcome.")

    return {
        "persona": persona,
        "overall_level": lvl,
        "domain_scores": domain_scores,
        "strengths": strengths,
        "growth_areas": growth,
        "top_risks": list(dict.fromkeys([e for e in evidence if "RISK" in e or "MISCONCEPTION" in e]))[:5],
        "learning_plan": learning[:3],
        "notes": notes[:6],
    }

class Assessor:
    def __init__(self):
        self.client = AzureOpenAIClient()

    async def next(self, persona: str, asked_question_ids: List[str], messages: List[Dict[str,str]],
                   current_scores: Dict[str,int], current_evidence: List[str]) -> Dict[str, Any]:

        candidates = candidate_questions(persona, asked_question_ids)

        # Stop after ~15 asked IDs (the question IDs are appended when selected)
        if len(asked_question_ids) >= 15 or not candidates:
            rep = build_report(persona, current_scores, current_evidence, notes=[])
            return {
                "assistant_text": "Thanks — that completes the assessment. I’ll share your summary report now.",
                "next_question_id": None,
                "scores": {**current_scores},
                "evidence": list(dict.fromkeys(current_evidence)),
                "done": True,
                "report": rep
            }

        ctx = {
            "persona": persona,
            "asked_question_ids": asked_question_ids,
            "current_scores": current_scores,
            "current_evidence": current_evidence,
            "candidates": candidates,
        }

        llm_messages = [
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": "CONTEXT_JSON:\n" + json.dumps(ctx, ensure_ascii=False)},
            {"role":"user","content": "CONVERSATION_SO_FAR:\n" + json.dumps(messages, ensure_ascii=False)},
            {"role":"user","content": "Return STRICT JSON only, no markdown, no extra text."}
        ]

        raw = await self.client.chat_completions(llm_messages)
        text = raw["choices"][0]["message"]["content"]

        parsed = self._parse_json(text)
        validate(instance=parsed, schema=LLM_RESPONSE_SCHEMA)

        nid = parsed.get("next_question_id")
        if nid is not None:
            if nid not in BANK_BY_ID or nid in asked_question_ids:
                nid = candidates[0]["id"]
            parsed["next_question_id"] = nid

        if parsed.get("done") and not parsed.get("report"):
            parsed["report"] = build_report(persona, parsed.get("scores", current_scores), parsed.get("evidence", current_evidence), notes=[])

        return parsed

    def _parse_json(self, s: str) -> Dict[str, Any]:
        s2 = s.strip().replace("```json", "```").replace("```", "")
        start, end = s2.find("{"), s2.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("LLM did not return JSON")
        return json.loads(s2[start:end+1])
