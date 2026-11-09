import requests, json, os, sys, time

DIR = os.path.dirname(os.path.abspath(__file__))
BASE = "https://nordlicht-bb-3.myshopify.com/api/ucp/mcp"
BASE1 = "https://nordlicht-bb-1.myshopify.com/api/ucp/mcp"
PROFILE_FILE = os.path.join(DIR, "profile_url.txt")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

def prof():
    return open(PROFILE_FILE).read().strip()

def call(tool, args=None, base=BASE, timeout=90, rid=1):
    a = dict(args or {})
    a["meta"] = {"ucp-agent": {"profile": prof()}}
    body = {"jsonrpc": "2.0", "id": rid, "method": "tools/call",
            "params": {"name": tool, "arguments": a}}
    r = requests.post(base, json=body, headers=HEADERS, timeout=timeout)
    try:
        j = r.json()
    except Exception:
        j = {"_raw": r.text[:3000]}
    return {"http": r.status_code, "json": j, "text": r.text, "body": body}

def text_of(res):
    j = res.get("json") or {}
    if "error" in j:
        return "ERROR " + json.dumps(j["error"])
    c = (j.get("result") or {}).get("content")
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return res.get("text", "")

def brief(res, limit=2000):
    flag = (res["json"].get("result") or {}).get("isError")
    return f"HTTP {res['http']} isError={flag}\n{text_of(res)[:limit]}"

def log(name, payload):
    p = os.path.join(DIR, "logs", name + ".json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return p
