# =============================================================
# NEXUS v5 — Gemini Client Wrapper
# All Gemini calls route through this module.
# =============================================================

import json
import re
import google.genai as genai
from config import GEMINI_API_KEY


def call_gemini(prompt: str, json_mode: bool = False, fast: bool = False) -> str:
    """
    Core Gemini call.

    Args:
        prompt    : the full prompt string
        json_mode : if True, wraps prompt with JSON-only instruction
        fast      : if True, uses flash model (cheaper, faster)

    Returns:
        Raw text response from Gemini.
    """
    if json_mode:
        prompt = (
            "IMPORTANT: Respond with ONLY valid JSON. "
            "No markdown, no code fences, no explanation.\n\n"
            + prompt
        )

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    return response.text.strip()


def call_gemini_json(prompt: str, fast: bool = False) -> dict | list:
    """
    Call Gemini and parse JSON response.
    Strips ```json ``` fences if present.
    """
    raw = call_gemini(prompt, json_mode=True, fast=fast)

    # Strip markdown code fences if Gemini wraps anyway
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\nRaw output:\n{raw}")
    
    import time

def call_gemini(prompt: str, json_mode: bool = False, fast: bool = False) -> str:
    if json_mode:
        prompt = (
            "IMPORTANT: Respond with ONLY valid JSON. "
            "No markdown, no code fences, no explanation.\n\n"
            + prompt
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                print(f"[Gemini] Rate limited, retrying in 30s...")
                time.sleep(30)
            else:
                raise