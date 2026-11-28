"""Tính ma trận thời gian di chuyển giữa các địa điểm nội thành (+ điểm xuất phát quận) bằng OSRM công cộng (FOSSGIS).

Chạy một lần khi dữ liệu đổi: python scripts/build_travel_matrix.py → data/travel_times.json.
Khoá: "<từ>|<đến>|<profile>" → [phút OSRM, mét], profile ∈ car | bike | foot.
Cách quy ra thời gian theo phương tiện nằm ở codebase/places.py (travel_leg); mọi giá trị là ước tính.
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
from places import ANCHORS, MATRIX, PLACES  # noqa: E402

PROFILES = {"car": "routed-car", "bike": "routed-bike", "foot": "routed-foot"}


def table(profile, src, dst):
    """Ma trận thời gian (giây) src × dst. Server công cộng giới hạn số toạ độ mỗi lần nên gọi theo khối."""
    pts = src + dst
    coords = ";".join("%.6f,%.6f" % (lng, lat) for lat, lng in pts)
    q = "sources=%s&destinations=%s&annotations=duration,distance" % (
        ";".join(map(str, range(len(src)))), ";".join(map(str, range(len(src), len(pts)))))
    url = "https://routing.openstreetmap.de/%s/table/v1/driving/%s?%s" % (profile, coords, q)
    req = urllib.request.Request(url, headers={"User-Agent": "tripswipe-hackathon/0.1"})
    with urllib.request.urlopen(req, timeout=120) as f:
        d = json.load(f)
        return d["durations"], d["distances"]


CHUNK = 40


def main():
    ids = [i for i, p in PLACES.items() if p["_inner"]] + ["start:" + k for k in ANCHORS]
    pts = [(PLACES[i]["lat"], PLACES[i]["lng"]) if i in PLACES else ANCHORS[i[6:]] for i in ids]
    out = {}
    blocks = [list(range(i, min(i + CHUNK, len(ids)))) for i in range(0, len(ids), CHUNK)]
    for prof in PROFILES:
        for bi in blocks:
            for bj in blocks:
                dur, dist = table(PROFILES[prof], [pts[i] for i in bi], [pts[j] for j in bj])
                for i, drow, mrow in zip(bi, dur, dist):
                    for j, sec, m in zip(bj, drow, mrow):
                        if i != j and sec is not None:
                            out["%s|%s|%s" % (ids[i], ids[j], prof)] = [round(sec / 60, 1), round(m)]
                time.sleep(1)
    with open(MATRIX, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(len(ids), "điểm,", len(out), "cặp →", MATRIX)


if __name__ == "__main__":
    main()
