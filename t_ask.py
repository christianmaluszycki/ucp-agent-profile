import client as c, json, os, time

OUT = os.path.join(c.DIR, "logs", "ask")
os.makedirs(OUT, exist_ok=True)
RESULTS = []

def ask(name, query, ids=None, base=None, context=None, note=""):
    base = base or c.BASE1
    a = {"ask": {"query": query}}
    if ids:
        a["ask"]["ids"] = ids
    if context:
        a["ask"]["context"] = context
    r = c.call("ask_business", a, base=base)
    txt = c.text_of(r)
    # extract answer
    ans = None
    try:
        j = json.loads(txt)
        ans = (j.get("answer") or {}).get("plain") or (j.get("answer") or {}).get("markdown")
        extra = {k: v for k, v in j.items() if k not in ("ucp", "answer")}
    except Exception:
        ans, extra = txt, {}
    rec = {"test": name, "note": note, "store": base, "query": query, "ids": ids,
           "http": r["http"], "isError": (r["json"].get("result") or {}).get("isError"),
           "answer": ans, "extra": extra, "raw_text": txt[:6000]}
    RESULTS.append(rec)
    print("=" * 95)
    print(f"[{name}] {note}")
    print("  Q:", query[:220].replace("\n", " "))
    print("  A:", (ans or "")[:700].replace("\n", " "))
    if extra:
        print("  EXTRA:", json.dumps(extra)[:300])
    return rec

def save(fname="ask-results.json"):
    p = os.path.join(c.DIR, "logs", fname)
    json.dump(RESULTS, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("\nsaved", p, "count:", len(RESULTS))
    return p
