"""
AI CV Writer — OpenRouter API
"""
import httpx, logging
from config import OPENROUTER_KEY

log = logging.getLogger(__name__)
MODEL   = "meta-llama/llama-3.1-8b-instruct:free"
TIMEOUT = 30


async def _call(prompt: str, max_tokens: int = 600) -> str:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type":  "application/json",
                    "HTTP-Referer":  "cvbot-myanmar",
                    "X-Title":       "Myanmar CV Builder Bot",
                },
                json={"model": MODEL, "max_tokens": max_tokens,
                      "messages": [{"role":"user","content":prompt}]})
        if r.status_code != 200:
            return ""
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log.error("AI call failed: %s", e)
        return ""


async def polish_objective(raw: str) -> str:
    if not raw or raw == "—": return raw
    prompt = (f"Rewrite this career objective into a professional 2-3 sentence "
              f"English CV statement. Return ONLY the text, no explanation.\n\n"
              f"Raw: {raw}\n\nPolished:")
    result = await _call(prompt, 200)
    return result if result else raw


async def polish_experience(raw: str) -> list:
    if not raw or raw == "—": return []
    prompt = (f"Parse this work experience into a JSON array. Each item: "
              f"title, company, period, duties(list of 2 bullets). "
              f"Return ONLY valid JSON.\n\nInput: {raw}\n\nJSON:")
    result = await _call(prompt, 500)
    if not result: return _parse_exp_simple(raw)
    try:
        import json
        cleaned = result.strip().replace("```json","").replace("```","")
        return json.loads(cleaned)
    except Exception:
        return _parse_exp_simple(raw)


def _parse_exp_simple(raw: str) -> list:
    results = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line: continue
        parts = [p.strip() for p in line.split(",")]
        results.append({"title":parts[0] if parts else line,
                         "company":parts[1] if len(parts)>1 else "",
                         "period":parts[2] if len(parts)>2 else "",
                         "duties":[]})
    return results


def format_skills(raw: str) -> list:
    if not raw or raw == "—": return []
    return [s.strip() for s in raw.replace("،",",").split(",") if s.strip()]


def parse_education(raw: str) -> list:
    results = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line: continue
        parts = [p.strip() for p in line.split(",")]
        results.append({"degree":parts[0] if parts else line,
                         "institution":parts[1] if len(parts)>1 else "",
                         "year":parts[2] if len(parts)>2 else ""})
    return results


def parse_languages(raw: str) -> list:
    results = []
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry: continue
        if "(" in entry:
            lang  = entry[:entry.index("(")].strip()
            level = entry[entry.index("(")+1:entry.index(")")].strip()
        else:
            lang, level = entry, "တတ်သည်"
        results.append({"language":lang,"level":level})
    return results


def parse_references(raw: str) -> list:
    results = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line: continue
        parts = [p.strip() for p in line.split(",")]
        results.append({"name":parts[0] if parts else line,
                         "title":parts[1] if len(parts)>1 else "",
                         "company":parts[2] if len(parts)>2 else "",
                         "phone":parts[3] if len(parts)>3 else ""})
    return results


async def process_cv_data(raw_data: dict) -> dict:
    processed = {}
    for key in ("full_name","dob","nationality","phone","email","address","photo_path","template"):
        processed[key] = raw_data.get(key, "")
    raw_obj = raw_data.get("objective","")
    processed["objective"] = await polish_objective(raw_obj) if raw_obj and raw_obj != "—" else ""
    processed["education"]  = parse_education(raw_data.get("education",""))
    raw_exp = raw_data.get("experience","")
    processed["experience"] = await polish_experience(raw_exp) if raw_exp and raw_exp != "—" else []
    processed["skills"]     = format_skills(raw_data.get("skills",""))
    processed["languages"]  = parse_languages(raw_data.get("languages",""))
    raw_ref = raw_data.get("references","")
    processed["references"] = parse_references(raw_ref) if raw_ref and raw_ref != "—" else []
    return processed
