"""Hình đường đi thật (OSRM /route) cho từng chặng của lịch, để vẽ bản đồ.

Phút và mét lấy từ travel_leg (cùng nguồn với bộ xếp lịch) để số trên bản đồ khớp số trong lịch;
OSRM /route chỉ cung cấp hình đường. Lỗi mạng → đường thẳng, nguồn "duong_chim_bay".
"""
import functools
import json
import urllib.parse
import urllib.request

try:
    from places import PROFILE, travel_leg
except ImportError:  # nạp từ app/ (gói codebase)
    from codebase.places import PROFILE, travel_leg

OSRM = "https://routing.openstreetmap.de/routed-%s/route/v1/driving/%s?overview=full&geometries=geojson"
NOTE = "Thời gian đi là ước tính từ đường đi thật (OSRM / OpenStreetMap) cộng hệ số giao thông nội thành; không phải giao thông thời gian thực."


@functools.lru_cache(maxsize=2048)  # ponytail: cache trong RAM, mất khi khởi động lại; chuyển sang bảng Postgres nếu cần
def _geometry(profile, a, b):
    """Toạ độ [(lat, lng)…] theo đường thật giữa a, b. None nếu OSRM không trả lời."""
    coords = "%f,%f;%f,%f" % (a[1], a[0], b[1], b[0])
    req = urllib.request.Request(OSRM % ({"car": "car", "bike": "bike", "foot": "foot"}[profile], urllib.parse.quote(coords, safe=",;.")),
                                 headers={"User-Agent": "tripswipe-hackathon/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=10) as f:
            route = json.load(f)["routes"][0]
        return tuple((round(lat, 6), round(lng, 6)) for lng, lat in route["geometry"]["coordinates"])
    except Exception:
        return None


def route(points, mode="xe_may"):
    """points: [{"id", "lat", "lng"}] theo thứ tự đi. Trả {"legs": [...], "note"} — mỗi chặng có phút, mét, hình đường, nguồn."""
    profile = PROFILE.get(mode, "bike")
    legs = []
    for p, q in zip(points, points[1:]):
        a, b = (p["lat"], p["lng"]), (q["lat"], q["lng"])
        minutes, meters, src = travel_leg(p.get("id") or "", a, q.get("id") or "", b, mode)
        geom = _geometry(profile, a, b)
        legs.append({"from": p.get("id"), "to": q.get("id"), "distance_m": meters, "duration_min": minutes,
                     "geometry": [list(x) for x in geom] if geom else [list(a), list(b)],
                     "source": src if geom else "duong_chim_bay"})
    return {"legs": legs, "note": NOTE}
