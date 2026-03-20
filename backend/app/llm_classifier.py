from __future__ import annotations

import json
import os
from urllib import error, request

from .data_loader import Domain, load_skills


GEMINI_MODEL = os.getenv("SKILLGRAPH_GEMINI_MODEL", "gemini-1.5-flash")


def gemini_enabled() -> bool:
    return bool(os.getenv("GEMINI_API_KEY")) and os.getenv("SKILLGRAPH_ENABLE_GEMINI", "0") == "1"


def classify_with_gemini(text: str, domain: Domain, mode: str) -> list[dict] | dict | None:
    if not gemini_enabled():
        return None
    skill_list = load_skills(domain)
    if mode == "resume":
        system_prompt = (
            "You are a skill extractor. Given resume text and a skill list, return ONLY valid JSON "
            "matching this schema: [{\"skill\": str, \"mentions\": int, \"in_recent_experience\": bool}]. "
            "Only include skills from the provided list. Do not invent skills."
        )
    else:
        system_prompt = (
            "You are a job-description skill classifier. Given JD text and a skill list, return ONLY valid JSON "
            "matching this schema: {\"required\": [str], \"preferred\": [str]}. "
            "Only include skills from the provided list. Do not invent skills."
        )
    user_prompt = f"Text:\n{text}\n\nSkill list:\n{json.dumps(skill_list)}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {"text": user_prompt},
                ]
            }
        ],
        "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
    }
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        f"?key={os.environ['GEMINI_API_KEY']}"
    )
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    try:
        text_output = body["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text_output)
    except (KeyError, IndexError, json.JSONDecodeError, TypeError):
        return None

