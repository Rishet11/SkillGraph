from __future__ import annotations

import json
import os
import re
from urllib import error, request

from .data_loader import Domain, load_skills


GEMINI_MODEL = os.getenv("SKILLGRAPH_GEMINI_MODEL", "gemini-1.5-flash")


def gemini_enabled() -> bool:
    return bool(os.getenv("GEMINI_API_KEY")) and os.getenv("SKILLGRAPH_ENABLE_GEMINI", "0") == "1"


def keyword_fallback_classify(text: str, domain: Domain) -> list[dict]:
    """
    Pure keyword matching fallback when Gemini is unavailable or returns invalid JSON.
    Returns same schema as Gemini: [{skill, mentions, in_recent_experience}]
    - mentions = case-insensitive regex count of skill name in text
    - in_recent_experience = True if skill appears in last 30% of text by character position
    - Only include skills with mentions > 0
    """
    skill_list = load_skills(domain)
    results = []
    text_len = len(text)
    recent_cutoff = int(text_len * 0.7)
    
    for skill in skill_list:
        pattern = re.compile(re.escape(skill), re.IGNORECASE)
        matches = list(pattern.finditer(text))
        mentions = len(matches)
        if mentions > 0:
            in_recent = any(m.start() >= recent_cutoff for m in matches)
            results.append({
                "skill": skill,
                "mentions": mentions,
                "in_recent_experience": in_recent
            })
    return results


def classify_with_gemini(text: str, domain: Domain, mode: str) -> list[dict] | dict | None:
    if not gemini_enabled():
        return None
    skill_list = load_skills(domain)
    
    def get_prompt(stricter: bool):
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
        if stricter:
            system_prompt += " Return ONLY a valid JSON array. No markdown. No explanation. No extra text."
        return system_prompt

    def make_request(stricter: bool):
        system_prompt = get_prompt(stricter)
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
        with request.urlopen(req, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
        text_output = body["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text_output)

    try:
        result = make_request(stricter=False)
        return result
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError):
        try:
            result = make_request(stricter=True)
            return result
        except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError):
            # Fallback to local keyword search
            return keyword_fallback_classify(text, domain)

