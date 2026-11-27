"""Adapter đọc POI/giờ từ dữ liệu lõi; không nhập module gọi model."""
import datetime as dt

from codebase.places import ANCHORS, ANCHOR_NAMES, INNER_DISTRICTS, windows


def minute(value):
    h, m = value.split(":")
    return int(h) * 60 + int(m)


def clock(value):
    return "%02d:%02d" % divmod(value, 60)


def start_options(places):
    points = [{"id": p["id"], "name": p["name"], "lat": p["lat"], "lng": p["lng"], "approximate": False}
              for p in places if p.get("district") in INNER_DISTRICTS]
    points += [{"id": "start:" + key, "name": ANCHOR_NAMES[key], "lat": xy[0], "lng": xy[1], "approximate": True}
               for key, xy in ANCHORS.items()]
    return points


def planning_config(config, member_count):
    return {"date": dt.date.fromisoformat(config["date"]), "start_min": minute(config["start_time"]),
            "end_min": minute(config["end_time"]), "start_xy": tuple(config["start_xy"]),
            "start_id": config["start_id"], "mode": config["mode"],
            "budget_per_person": config["budget_total"] // member_count}


def eligible(place, cfg):
    if place.get("district") not in INNER_DISTRICTS:
        return False
    spans = windows(place["id"], cfg["date"])
    if not spans or not any(a < cfg["end_min"] and b > cfg["start_min"] for a, b in spans):
        return False
    price = place.get("price_max_vnd")
    # Ngân sách 0 chỉ nhận điểm được ghi rõ miễn phí, không biến giá thiếu thành 0.
    if cfg["budget_per_person"] == 0:
        return price == 0
    return price is None or price <= cfg["budget_per_person"]


def place_view(place, date=None):
    out = dict(place)
    if date:
        spans = windows(place["id"], date)
        out["hours_status"] = "unknown" if spans is None else ("open" if spans else "closed")
        out["opening_windows"] = None if spans is None else [
            {"open": clock(a), "close": clock(b)} for a, b in spans]
        out["hours_for_date"] = date.isoformat()
    return out
