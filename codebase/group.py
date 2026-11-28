"""Luồng nhóm cho web (TS-03 bộ thẻ AI · TS-06 xếp lịch nhóm theo phiếu quẹt).

Hợp đồng (TASKS.md mục 2):
    build_deck(cfg) -> [{"id", "rank", "reason"}]   (tối đa 20 thẻ)
    plan_group(cfg, scores: {id: float}, pinned: [id]) -> {
        "items": [{"id", "name", "arrive", "leave", "travel_min", "no_hours", ...}],
        "dropped": [{"id", "name", "reason"}],
        "violations": [],
    }
    cfg = {date, start_min, end_min, start_xy, start_id, mode, budget_per_person}

Chạy hoàn toàn không cần Postgres; có thể import từ cả `codebase.group` lẫn `group`.
"""
import datetime as dt
import json
import os
import re
import sys

_CODEBASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _CODEBASE_DIR not in sys.path:
    sys.path.insert(0, _CODEBASE_DIR)

from ai import MODEL_PROVIDER, call_model  # noqa: E402
from places import INNER_DISTRICTS, PLACES, travel_minutes, windows  # noqa: E402
from planner import _fit, check, reason, stay  # noqa: E402

DECK_LIMIT = 20
MAX_SEARCH_CANDIDATES = 12
GROUP_NODE_LIMIT = 40_000
BREAKFAST_WINDOW = (6 * 60, 10 * 60)
LUNCH_WINDOW = (11 * 60, 14 * 60)
DINNER_WINDOW = (17 * 60 + 30, 20 * 60 + 30)
FALLBACK_REASON = "Địa điểm nổi bật, phù hợp lịch trình một ngày ở Hà Nội."

DECK_SYSTEM = """Bạn chọn và xếp hạng tối đa 20 địa điểm từ DANH SÁCH ỨNG VIÊN cho nhóm bạn đi chơi một ngày ở nội thành Hà Nội.
Yêu cầu:
- Chỉ dùng ID có trong DANH SÁCH ỨNG VIÊN. Không tự bịa ID.
- Cân bằng cả điểm tham quan (culture, landmark, nature, show_experience) và quán ăn / đồ uống (food_drink) nếu danh sách có đủ.
- Mỗi địa điểm viết lý do ngắn (≤ 20 chữ, tiếng Việt) vì sao nhóm nên ghé.
- TUYỆT ĐỐI không viết bất kỳ chữ số nào (0–9) trong lý do.
Trả về đúng JSON và không thêm chữ nào khác:
{"cards": [{"id": "<id>", "reason": "<lý do không chứa chữ số>"}]}"""


def _parse_date(value):
    if isinstance(value, dt.date) and not isinstance(value, dt.datetime):
        return value
    if isinstance(value, dt.datetime):
        return value.date()
    return dt.date.fromisoformat(str(value))


def _norm_cfg(cfg):
    out = dict(cfg)
    out["date"] = _parse_date(cfg["date"])
    out["start_xy"] = tuple(cfg["start_xy"])
    out.setdefault("start_id", "start")
    out.setdefault("mode", "xe_may")
    return out


def _clean_reason(text, pid):
    """Đảm bảo lý do là chuỗi tiếng Việt không rỗng và không chứa chữ số."""
    if isinstance(text, str):
        cleaned = " ".join(text.strip().split())
        if cleaned and not re.search(r"\d", cleaned):
            return cleaned
    hook = PLACES[pid].get("card_hook") or ""
    if isinstance(hook, str):
        hook = " ".join(hook.strip().split())
        if hook and not re.search(r"\d", hook):
            return hook
    return FALLBACK_REASON


def _json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except ValueError:
        return {}


def is_eligible(place, cfg):
    """Kiểm một địa điểm đủ điều kiện vào bộ thẻ (khớp app/catalogue.py::eligible)."""
    if place.get("district") not in INNER_DISTRICTS:
        return False
    spans = windows(place["id"], cfg["date"])
    if not spans or not any(a < cfg["end_min"] and b > cfg["start_min"] for a, b in spans):
        return False
    budget = cfg.get("budget_per_person")
    if budget is None:
        return True
    price = place.get("price_max_vnd")
    if budget == 0:
        return price == 0
    return price is None or price <= budget


def _balanced_pick(candidates, limit=DECK_LIMIT):
    """Chọn tối đa `limit` ứng viên theo rating, cân bằng tham quan và ăn uống."""
    ranked = sorted(candidates, key=lambda p: (-(p.get("rating") or 0), p["id"]))
    sight = [p for p in ranked if p.get("category") != "food_drink"]
    food = [p for p in ranked if p.get("category") == "food_drink"]
    target_food = min(len(food), max(0, limit // 3))
    target_sight = min(len(sight), limit - target_food)
    picked = sight[:target_sight] + food[:target_food]
    picked_ids = {p["id"] for p in picked}
    if len(picked) < limit:
        for p in ranked:
            if p["id"] not in picked_ids:
                picked.append(p)
                picked_ids.add(p["id"])
                if len(picked) >= limit:
                    break
    picked.sort(key=lambda p: (-(p.get("rating") or 0), p["id"]))
    return picked[:limit]


def build_deck(cfg: dict) -> list:
    """Lọc ứng viên hợp lệ theo cấu hình nhóm → gọi model chọn & xếp hạng tối đa 20 thẻ (TS-03)."""
    cfg = _norm_cfg(cfg)
    candidates = [p for p in PLACES.values() if is_eligible(p, cfg)]
    if not candidates:
        return []
    by_id = {p["id"]: p for p in candidates}

    if MODEL_PROVIDER == "fake":
        call_model(DECK_SYSTEM, "")
        picked = _balanced_pick(candidates, DECK_LIMIT)
        return [{"id": p["id"], "rank": i, "reason": _clean_reason(p.get("card_hook"), p["id"])}
                for i, p in enumerate(picked, 1)]

    # Gửi danh sách gọn (id|tên|loại|quận|tag) để tiết kiệm token; lỗi API để bay ra theo TS-03.
    ordered = sorted(candidates, key=lambda p: (-(p.get("rating") or 0), p["id"]))
    lines = ["%s|%s|%s|%s|%s" % (
        p["id"], p["name"], p.get("category") or "", p.get("district") or "",
        ", ".join((p.get("swipe_tags") or [])[:3])
    ) for p in ordered]
    user_msg = "DANH SÁCH ỨNG VIÊN (%d điểm):\n%s" % (len(lines), "\n".join(lines))
    raw = _json(call_model(DECK_SYSTEM, user_msg)["text"])

    cards = []
    seen = set()
    for entry in raw.get("cards") or []:
        if not isinstance(entry, dict):
            continue
        pid = entry.get("id")
        if pid in by_id and pid not in seen:
            seen.add(pid)
            cards.append({"id": pid, "reason": _clean_reason(entry.get("reason"), pid)})
            if len(cards) >= DECK_LIMIT:
                break

    if len(cards) < min(DECK_LIMIT, len(candidates)):
        remaining = [p for p in candidates if p["id"] not in seen]
        for p in _balanced_pick(remaining, DECK_LIMIT - len(cards)):
            cards.append({"id": p["id"], "reason": _clean_reason(p.get("card_hook"), p["id"])})

    return [{"id": c["id"], "rank": i, "reason": c["reason"]} for i, c in enumerate(cards[:DECK_LIMIT], 1)]


def _overlaps(a, b, win):
    return a < win[1] and b > win[0]


def _meal_tag(pid, arrive, leave, need_breakfast, need_lunch, need_dinner):
    if PLACES[pid].get("category") != "food_drink":
        return None
    if need_breakfast and _overlaps(arrive, leave, BREAKFAST_WINDOW):
        return "breakfast"
    if need_lunch and _overlaps(arrive, leave, LUNCH_WINDOW):
        return "lunch"
    if need_dinner and _overlaps(arrive, leave, DINNER_WINDOW):
        return "dinner"
    return None


def _select_pool(open_ids, scores, pinned_set, need_meal):
    """Giới hạn tập đưa vào vét cạn để luôn < 2 giây, ưu tiên ghim + điểm cao + xen kẽ ăn uống."""
    def sort_key(pid):
        return (pid not in pinned_set, -float(scores.get(pid, 0.0)), -(PLACES[pid].get("rating") or 0.0), pid)

    ranked = sorted(open_ids, key=sort_key)
    if len(ranked) > MAX_SEARCH_CANDIDATES:
        pool = ranked[:MAX_SEARCH_CANDIDATES]
        if need_meal and not any(PLACES[pid].get("category") == "food_drink" for pid in pool):
            food = [pid for pid in ranked[MAX_SEARCH_CANDIDATES:] if PLACES[pid].get("category") == "food_drink"]
            if food:
                for idx in range(len(pool) - 1, -1, -1):
                    if pool[idx] not in pinned_set:
                        pool[idx] = food[0]
                        break
    else:
        pool = ranked
    # Xen kẽ điểm tham quan và quán ăn trong thứ tự duyệt để DFS sớm tìm được lịch đủ 3 bữa.
    sight = [pid for pid in pool if PLACES[pid].get("category") != "food_drink"]
    food = [pid for pid in pool if PLACES[pid].get("category") == "food_drink"]
    interleaved = []
    for i in range(max(len(sight), len(food))):
        if i < len(food):
            interleaved.append(food[i])
        if i < len(sight):
            interleaved.append(sight[i])
    return interleaved


def plan_group(cfg: dict, scores: dict, pinned=()) -> dict:
    """Xếp lịch nhóm từ điểm phiếu quẹt + điểm ghim, giữ ràng buộc giờ, budget và slot ăn (TS-06)."""
    cfg = _norm_cfg(cfg)
    scores = dict(scores or {})
    pinned_list = list(dict.fromkeys(pinned or ()))
    pinned_set = set(pinned_list)
    wanted = list(dict.fromkeys(pinned_list + list(scores.keys())))

    budget = cfg.get("budget_per_person")
    dropped = []
    schedulable = []
    pre_dropped = set()

    for pid in wanted:
        if pid not in PLACES:
            dropped.append({"id": pid, "name": pid, "reason": "không có trong dữ liệu"})
            pre_dropped.add(pid)
            continue
        p = PLACES[pid]
        if not p["_inner"]:
            dropped.append({"id": pid, "name": p["name"], "reason": "ngoài phạm vi nội thành"})
            pre_dropped.add(pid)
            continue
        wins = windows(pid, cfg["date"])
        if wins == []:
            dropped.append({"id": pid, "name": p["name"], "reason": reason(pid, cfg)})
            pre_dropped.add(pid)
            continue
        price = p.get("price_max_vnd")
        if budget is not None:
            if budget == 0 and price != 0:
                msg = "chưa có dữ liệu giá (ngân sách 0đ)" if price is None else "vượt ngân sách mỗi người"
                dropped.append({"id": pid, "name": p["name"], "reason": msg})
                pre_dropped.add(pid)
                continue
            if budget > 0 and price is not None and price > budget:
                dropped.append({"id": pid, "name": p["name"], "reason": "vượt ngân sách mỗi người"})
                pre_dropped.add(pid)
                continue
        schedulable.append(pid)

    need_breakfast = cfg["start_min"] <= 9 * 60 + 30 and cfg["end_min"] >= 8 * 60
    need_lunch = cfg["start_min"] <= 12 * 60 and cfg["end_min"] >= 13 * 60
    need_dinner = cfg["start_min"] <= 18 * 60 + 30 and cfg["end_min"] >= 19 * 60 + 30
    pool = _select_pool(schedulable, scores, pinned_set, need_breakfast or need_lunch or need_dinner)

    # Chuẩn bị trước khung mở và thời lượng cho từng ứng viên trong pool để DFS nhanh hơn.
    info = {}
    for pid in pool:
        p = PLACES[pid]
        raw_wins = windows(pid, cfg["date"])
        dur, est = stay(pid)
        info[pid] = {
            "name": p["name"],
            "xy": (p["lat"], p["lng"]),
            "wins": [(0, 24 * 60)] if raw_wins is None else raw_wins,
            "no_hours": raw_wins is None,
            "dur": dur,
            "est": est,
            "price": p.get("price_max_vnd"),
            "score": float(scores.get(pid, 1.0 if pid in pinned_set else 0.0)),
            "pinned": pid in pinned_set,
            "category": p.get("category"),
        }

    best = None  # (rank_key, items_list)
    nodes = [0]

    def dfs(items, used, t, here, here_xy, moving, spent, pin_cnt, score_sum, meals, snack_cnt):
        nonlocal best
        nodes[0] += 1
        if items:
            rank_key = (pin_cnt, round(score_sum + 0.8 * len(meals), 4), len(items), -moving)
            if best is None or rank_key > best[0]:
                best = (rank_key, list(items))
        if nodes[0] > GROUP_NODE_LIMIT:
            return
        prev_food = bool(items and items[-1]["category"] == "food_drink")
        for pid in pool:
            if pid in used:
                continue
            meta = info[pid]
            is_food = meta["category"] == "food_drink"
            # Không xếp 2 quán ăn liền kề nhau (trừ điểm trưởng nhóm ghim).
            if is_food and prev_food and not meta["pinned"]:
                continue
            add_price = meta["price"] or 0
            if budget is not None and spent + add_price > budget:
                continue
            mins, src = travel_minutes(here, here_xy, pid, meta["xy"], cfg["mode"])
            start = _fit(t + mins, meta["dur"], meta["wins"])
            if start is None or start + meta["dur"] > cfg["end_min"]:
                continue
            leave = start + meta["dur"]
            mtag = _meal_tag(pid, start, leave, need_breakfast, need_lunch, need_dinner)
            if is_food and not meta["pinned"]:
                if mtag is not None and mtag in meals:
                    continue  # mỗi bữa (sáng/trưa/tối) chỉ xếp tối đa 1 quán
                if mtag is None and snack_cnt >= 1:
                    continue  # tối đa 1 quán ăn nhẹ / cà phê ngoài 3 bữa chính
            new_meals = meals | ({mtag} if mtag else set())
            new_snack = snack_cnt + (1 if (is_food and mtag is None) else 0)
            item = {
                "id": pid,
                "name": meta["name"],
                "arrive": start,
                "leave": leave,
                "travel_min": mins,
                "travel_src": src,
                "no_hours": meta["no_hours"],
                "stay_estimated": meta["est"],
                "price_max_vnd": meta["price"],
                "price_missing": meta["price"] is None,
                "category": meta["category"],
                "meal_slot": mtag,
            }
            items.append(item)
            used.add(pid)
            dfs(items, used, leave, pid, meta["xy"], moving + mins, spent + add_price,
                pin_cnt + (1 if meta["pinned"] else 0), score_sum + meta["score"], new_meals, new_snack)
            used.remove(pid)
            items.pop()

    dfs([], set(), cfg["start_min"], cfg["start_id"], cfg["start_xy"], 0, 0, 0, 0.0, set(), 0)

    items = best[1] if best else []
    placed = {it["id"] for it in items}
    spent_total = sum((it["price_max_vnd"] or 0) for it in items)

    for pid in schedulable:
        if pid in placed or pid in pre_dropped:
            continue
        p = PLACES[pid]
        price = p.get("price_max_vnd")
        if budget is not None and price is not None and spent_total + price > budget:
            why = "vượt ngân sách mỗi người khi gộp lịch"
        else:
            why = reason(pid, cfg)
        dropped.append({"id": pid, "name": p["name"], "reason": why})

    violations = check(items, cfg)
    if budget is not None and spent_total > budget:
        violations.append("tổng chi phí mỗi người (%dđ) vượt ngân sách (%dđ)" % (spent_total, budget))
    if violations:
        return {"items": [], "dropped": dropped, "violations": violations}
    return {"items": items, "dropped": dropped, "violations": []}
