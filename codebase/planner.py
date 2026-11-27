"""Xếp lịch một ngày và kiểm vi phạm. Toàn bộ giờ / phút do code tính, không qua model."""
from places import PLACES, WEEKDAYS, fmt, travel_minutes, windows

DEFAULT_STAY = 60
NODE_LIMIT = 200_000
# ponytail: vét cạn có cắt nhánh, dừng ở NODE_LIMIT nút (lấy lịch tốt nhất đã thấy); bộ thẻ lớn cần thêm heuristic


def stay(pid):
    d = PLACES[pid].get("estimated_duration_mins")
    return (int(d), False) if d else (DEFAULT_STAY, True)


def _fit(arrive, dur, wins):
    """Giờ bắt đầu sớm nhất ≥ arrive để ở trọn `dur` phút trong một khung mở. None nếu không vừa."""
    for a, b in sorted(wins):
        start = max(arrive, a)
        if start + dur <= b:
            return start
    return None


def simulate(order, cfg):
    """Chạy thử một thứ tự. Trả (items, tổng phút đi) hoặc None nếu vi phạm."""
    t, here, here_xy, items, moving = cfg["start_min"], cfg.get("start_id", "start"), cfg["start_xy"], [], 0
    for pid in order:
        p = PLACES[pid]
        xy = (p["lat"], p["lng"])
        mins, src = travel_minutes(here, here_xy, pid, xy, cfg["mode"])
        wins = windows(pid, cfg["date"])
        dur, est = stay(pid)
        if wins is None:
            wins = [(0, 24 * 60)]  # chưa có dữ liệu giờ: cho xếp nhưng gắn cảnh báo
        start = _fit(t + mins, dur, wins)
        if start is None or start + dur > cfg["end_min"]:
            return None
        items.append({"id": pid, "name": p["name"], "travel_min": mins, "travel_src": src,
                      "arrive": start, "leave": start + dur, "stay_estimated": est,
                      "no_hours": windows(pid, cfg["date"]) is None})
        moving += mins
        t, here, here_xy = start + dur, pid, xy
    return items, moving


def plan(cfg, wanted, pinned=()):
    """Chọn tập con lớn nhất (ưu tiên điểm ghim, rồi nhiều điểm, rồi ít đi) xếp được trong khung giờ."""
    wanted = list(dict.fromkeys(wanted))
    open_today = [p for p in wanted if windows(p, cfg["date"]) != []]
    best, nodes = None, [0]

    def key(r, order):
        return (sum(p in order for p in pinned), len(order), -r[1])

    def dfs(order, r):
        nonlocal best
        nodes[0] += 1
        if order and (best is None or key(r, order) > key(best, [i["id"] for i in best[0]])):
            best = r
        if nodes[0] > NODE_LIMIT:
            return
        for pid in open_today:
            if pid not in order:
                nr = simulate(order + [pid], cfg)
                if nr:  # tiền tố vi phạm thì mọi thứ tự kéo dài cũng vi phạm → cắt nhánh
                    dfs(order + [pid], nr)

    dfs([], None)
    items = best[0] if best else []
    placed = {i["id"] for i in items}
    dropped = [{"id": p, "name": PLACES[p]["name"], "reason": reason(p, cfg)} for p in wanted if p not in placed]
    return items, dropped


def reason(pid, cfg):
    """Lý do một điểm không vào lịch."""
    wins = windows(pid, cfg["date"])
    day = WEEKDAYS[cfg["date"].weekday()]
    if wins == []:
        return "đóng cửa %s" % day
    if wins is not None and not any(a < cfg["end_min"] and b > cfg["start_min"] for a, b in wins):
        return "ngoài giờ mở cửa (%s mở %s)" % (day, ", ".join("%s–%s" % (fmt(a), fmt(b)) for a, b in wins))
    if wins is not None:
        dur, _ = stay(pid)
        if not any(min(b, cfg["end_min"]) - max(a, cfg["start_min"]) >= dur for a, b in wins):
            return "khung mở cửa trùng với khung giờ của nhóm quá ngắn (cần %d phút)" % dur
    return "không đủ thời gian trong khung %s–%s" % (fmt(cfg["start_min"]), fmt(cfg["end_min"]))


def check(items, cfg):
    """Kiểm một lịch bất kỳ. Trả danh sách vi phạm (rỗng = hợp lệ)."""
    bad, prev_leave, here, here_xy = [], cfg["start_min"], cfg.get("start_id", "start"), cfg["start_xy"]
    for it in items:
        pid = it["id"]
        if pid not in PLACES:
            bad.append("%s: không có trong dữ liệu" % pid)
            continue
        p = PLACES[pid]
        wins = windows(pid, cfg["date"])
        if wins == []:
            bad.append("%s: đóng cửa %s" % (p["name"], WEEKDAYS[cfg["date"].weekday()]))
        elif wins is not None and not any(a <= it["arrive"] and it["leave"] <= b for a, b in wins):
            bad.append("%s: %s–%s nằm ngoài giờ mở cửa" % (p["name"], fmt(it["arrive"]), fmt(it["leave"])))
        mins, _ = travel_minutes(here, here_xy, pid, (p["lat"], p["lng"]), cfg["mode"])
        if it["arrive"] < prev_leave + mins:
            bad.append("%s: đến lúc %s, không đủ thời gian di chuyển hoặc chồng giờ" % (p["name"], fmt(it["arrive"])))
        if it["arrive"] < cfg["start_min"] or it["leave"] > cfg["end_min"]:
            bad.append("%s: vượt khung giờ %s–%s" % (p["name"], fmt(cfg["start_min"]), fmt(cfg["end_min"])))
        prev_leave, here, here_xy = it["leave"], pid, (p["lat"], p["lng"])
    return bad
