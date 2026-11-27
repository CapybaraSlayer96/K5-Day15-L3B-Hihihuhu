"""Tính ma trận thời gian di chuyển giữa các địa điểm nội thành (+ điểm xuất phát quận) bằng OSRM công cộng (FOSSGIS).

Chạy một lần khi dữ liệu đổi: python scripts/build_travel_matrix.py → data/travel_times.json.
Khoá: "<từ>|<đến>|<phương tiện>" → phút. Xe máy dùng profile ô tô (gần nhất có sẵn), luôn là ước tính.
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
from places import ANCHORS, MATRIX, PLACES  # noqa: E402

PROFILES = {"o_to": "routed-car", "xe_may": "routed-car", "di_bo": "routed-foot"}


def table(profile, src, dst):
    """Ma trận thời gian (giây) src × dst. Server công cộng giới hạn số toạ độ mỗi lần nên gọi theo khối."""
    pts = src + dst
    coords = ";".join("%.6f,%.6f" % (lng, lat) for lat, lng in pts)
    q = "sources=%s&destinations=%s&annotations=duration" % (
        ";".join(map(str, range(len(src)))), ";".join(map(str, range(len(src), len(pts)))))
    url = "https://routing.openstreetmap.de/%s/table/v1/driving/%s?%s" % (profile, coords, q)
    req = urllib.request.Request(url, headers={"User-Agent": "tripswipe-hackathon/0.1"})
    with urllib.request.urlopen(req, timeout=120) as f:
        return json.load(f)["durations"]


CHUNK = 40


def main():
    ids = [i for i, p in PLACES.items() if p["_inner"]] + ["start:" + k for k in ANCHORS]
    pts = [(PLACES[i]["lat"], PLACES[i]["lng"]) if i in PLACES else ANCHORS[i[6:]] for i in ids]
    out = {}
    blocks = [list(range(i, min(i + CHUNK, len(ids)))) for i in range(0, len(ids), CHUNK)]
    for mode in ("o_to", "di_bo"):
        for bi in blocks:
            for bj in blocks:
                d = table(PROFILES[mode], [pts[i] for i in bi], [pts[j] for j in bj])
                for i, row in zip(bi, d):
                    for j, sec in zip(bj, row):
                        if i != j and sec is not None:
                            out["%s|%s|%s" % (ids[i], ids[j], mode)] = round(sec / 60, 1)
                            if mode == "o_to":
                                out["%s|%s|xe_may" % (ids[i], ids[j])] = round(sec / 60, 1)
                time.sleep(1)
    with open(MATRIX, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(len(ids), "điểm,", len(out), "cặp →", MATRIX)


if __name__ == "__main__":
    main()
