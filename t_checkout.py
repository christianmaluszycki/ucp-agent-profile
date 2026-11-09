import client as c, json, os, sys, time

OUT = os.path.join(c.DIR, "logs")
os.makedirs(OUT, exist_ok=True)
RESULTS = []

V_A = "gid://shopify/ProductVariant/50026700112027"  # 60000 USD
V_B = "gid://shopify/ProductVariant/50026699686043"  # 78595 USD

def core(res):
    try:
        j = json.loads(c.text_of(res))
    except Exception:
        return {"_raw": c.text_of(res)[:1000]}
    j.pop("ucp", None)
    return j

def summarize(j):
    items = []
    for li in (j.get("line_items") or []):
        items.append({
            "variant": (li.get("item") or {}).get("id"),
            "qty": li.get("quantity"),
            "price": (li.get("item") or {}).get("price"),
            "line_total": next((t["amount"] for t in (li.get("totals") or []) if t.get("type") == "total"), None),
        })
    tot = {t.get("type"): t.get("amount") for t in (j.get("totals") or [])}
    return {"id": j.get("id"), "status": j.get("status"), "currency": j.get("currency"),
            "items": items, "totals": tot,
            "discounts": j.get("discounts"),
            "msg_codes": [(m.get("code"), m.get("severity")) for m in (j.get("messages") or [])]}

def run(name, tool, args, base=None, note=""):
    base = base or c.BASE1
    r = c.call(tool, args, base=base)
    j = core(r)
    rec = {"test": name, "note": note, "tool": tool, "base": base,
           "request_arguments": args, "http": r["http"],
           "isError": (r["json"].get("result") or {}).get("isError"),
           "summary": summarize(j) if isinstance(j, dict) else j,
           "raw": j}
    RESULTS.append(rec)
    print("=" * 90)
    print(f"[{name}] {note}")
    print("  req:", json.dumps(args)[:300])
    print("  ->", json.dumps(rec["summary"], ensure_ascii=False)[:700])
    return rec, j

def save():
    p = os.path.join(OUT, "checkout-tests.json")
    json.dump(RESULTS, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    return p
