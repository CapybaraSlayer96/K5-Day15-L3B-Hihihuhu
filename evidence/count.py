"""Gắn nhãn + đếm review. Chạy sau fetch_reviews.py:  python -I -X utf8 count.py
Nhãn định nghĩa sau khi đọc thử 30 review (seed 27), xem data-mining.md mục 2."""
import csv, re, collections
LABELS = {
 "GIO":   r"opening hours?|open(ing)? times?|hours of operation|business hours|\bclosed\b|\bcloses?\b|closing time|wrong hours|outdated hours|not open",
 "ROUTE": r"\broute|routing|zig-?zag|optimi[sz]|travel time|drive time|driving time|walking time|\bdistance|too far|back-?track|out of the way|efficient|order of (the )?(stops|places|days)",
 "TIME":  r"waste[sd]? (of )?(my |our )?(time|half|hours|a day)|too much time|took (me )?(hours|forever)|hours of|time[- ]consuming|tedious|painful|so much effort|difficult to (add|plan|use)|hard to (add|plan|use)|spent too much",
}
rx = {k: re.compile(v, re.I) for k, v in LABELS.items()}
rows = list(csv.DictReader(open("reviews_raw.csv", encoding="utf-8-sig")))
cnt = collections.Counter(); out = []
for r in rows:
    t = r["title"] + " " + r["text"]
    labs = [k for k, p in rx.items() if p.search(t)]
    for k in labs: cnt[k] += 1
    if labs: cnt["ANY"] += 1
    r["labels"] = ";".join(labs); out.append(r)
N = len(rows)
print("N =", N)
for k in ["GIO", "ROUTE", "TIME", "ANY"]: print(f"{k}: {cnt[k]}/{N} ({100*cnt[k]/N:.1f}%)")
for app in sorted({r["app"] for r in rows}):
    sub = [r for r in out if r["app"] == app]
    print(f"  {app}: {sum(1 for r in sub if r['labels'])}/{len(sub)}")
with open("reviews_labeled.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
