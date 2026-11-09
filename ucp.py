import requests, json, os, sys, time

BASE = "https://nordlicht-bb-3.myshopify.com/api/ucp/mcp"
BASE1 = "https://nordlicht-bb-1.myshopify.com/api/ucp/mcp"
DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_FILE = os.path.join(DIR, "profile_url.txt")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

def get_profile_url(refresh=False):
    if not refresh and os.path.exists(PROFILE_FILE):
        return open(PROFILE_FILE).read().strip()
    profile = {
        "name": "UCP Test Agent",
        "version": "1.0.0",
        "description": "Authorized internal security testing agent for our own Shopify stores.",
        "capabilities": ["catalog", "checkout"],
        "contact": "security@example.com",
        "homepage": "https://example.com",
        "terms": "Testing only",
    }
    r = requests.post("https://jsonblob.com/api/jsonBlob", json=profile,
                      headers={"Content-Type": "application/json", "Accept": "application/json"}, timeout=30)
    loc = r.headers.get("Location") or r.headers.get("location")
    if not loc:
        raise RuntimeError(f"blob create failed {r.status_code}: {r.text[:400]} {dict(r.headers)}")
    if loc.startswith("/"):
        loc = "https://jsonblob.com" + loc
    open(PROFILE_FILE, "w").write(loc)
    return loc

def rpc(tool, arguments=None, base=BASE, extra_meta=None, rid=None, session_id=None, timeout=60, raw_body=None):
    prof = get_profile_url()
    meta = {"ucp-agent": {"profile": prof}}
    if extra_meta:
        meta.update(extra_meta)
    params = {"name": tool, "arguments": arguments or {}}
    if raw_body is not None:
        body = raw_body
    else:
        body = {"jsonrpc": "2.0", "id": rid or 1, "method": "tools/call",
                "params": {"name": tool, "arguments": arguments or {}, "meta": meta}}
    h = dict(HEADERS)
    if session_id:
        h["Mcp-Session-Id"] = session_id
    r = requests.post(base, data=json.dumps(body) if not isinstance(body, str) else body,
                      headers=h, timeout=timeout, allow_redirects=False)
    return r

def show(label, r, limit=4000):
    print("=" * 100)
    print(f"### {label}")
    print(f"HTTP {r.status_code}  ct={r.headers.get('content-type')}  len={len(r.content)}")
    txt = r.text
    print(txt[:limit])
    if len(txt) > limit:
        print(f"...[{len(txt)-limit} chars truncated]")
    return txt

if __name__ == "__main__":
    print(get_profile_url(refresh="--refresh" in sys.argv))
