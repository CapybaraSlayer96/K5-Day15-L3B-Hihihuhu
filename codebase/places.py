"""Dữ liệu địa điểm Hà Nội: nạp JSON, chuẩn hoá giờ mở cửa theo thứ / mùa, ước thời gian di chuyển."""
import datetime as dt
import json
import math
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "hanoi_places.json")
MATRIX = os.path.join(ROOT, "data", "travel_times.json")

INNER_DISTRICTS = {"Ba Đình", "Hoàn Kiếm", "Đống Đa", "Hai Bà Trưng", "Tây Hồ", "Cầu Giấy", "Thanh Xuân",
                   "Hoàng Mai", "Long Biên", "Nam Từ Liêm", "Bắc Từ Liêm", "Hà Đông"}
WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]
SPEED_KMH = {"xe_may": 20, "o_to": 15, "di_bo": 4.5}
DAY = 24 * 60

# Chuỗi giờ không đọc được bằng luật chung → khai tay. Mỗi giá trị: {thứ (0=T2): [(mở, đóng) phút]}.
_ALL = range(7)


def _w(days, *spans):
    return {d: [(_m(a), _m(b)) for a, b in spans] for d in days}


def _m(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


OVERRIDES = {
    "hn_06": None,  # theo lịch biểu diễn, không có giờ cố định
    "hn_32": {**_w(range(6), *[(t, e) for t, e in [("15:00", "15:50"), ("16:10", "17:00"), ("17:20", "18:10"),
                                                     ("18:30", "19:20"), ("20:00", "20:50")]]),
              6: [(_m(a), _m(b)) for a, b in [("09:30", "10:20"), ("15:00", "15:50"), ("16:10", "17:00"), ("17:20", "18:10"),
                                               ("18:30", "19:20"), ("20:00", "20:50"), ("21:15", "22:05")]]},
    "hn_33": {4: [(_m("19:00"), DAY)], 5: [(0, DAY)], 6: [(0, DAY)]},
    "hn_36": _w([5, 6], ("19:00", "20:30")),
    "hn_37": _w([4, 5, 6], ("19:00", "21:00")),
    "hn_67": _w([2, 5, 6], ("19:30", "20:30")),
    "hn_68": _w([2, 5, 6], ("18:30", "22:00")),
    "hn_local_01": {**_w(_ALL, ("17:00", "23:00")), **{d: [(_m("11:00"), _m("14:00")), (_m("17:00"), _m("23:00"))] for d in range(1, 6)}},
    "hn_local_27": _w(_ALL, ("14:00", "17:00")),
    "hn_local_28": _w(_ALL, ("09:00", "11:30")),
}
# Giờ theo mùa (Lăng Bác): mùa nóng 1/4–31/10, mùa lạnh 1/11–31/3. Nguồn: bqllang.gov.vn/lich-vieng.html
SEASONAL = {
    "hn_04": {"nong": {**_w([1, 2, 3], ("07:30", "10:30")), **_w([5, 6], ("07:30", "11:00"))},
              "lanh": {**_w([1, 2, 3], ("08:00", "11:00")), **_w([5, 6], ("08:00", "11:30"))}},
}
_RANGE = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*[-–]\s*(\d{1,2})(?::(\d{2}))?")


def _plain(s):
    s = unicodedata.normalize("NFD", (s or "").lower().replace("đ", "d"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def parse_hours(text, closed_weekdays):
    """Chuỗi giờ + thứ đóng → {thứ: [(mở, đóng)]}. None nếu không đọc được."""
    t = (text or "").strip()
    if not t:
        return None
    p = _plain(t)
    if "ca ngay" in p or re.search(r"\b24h\b", p) or "24/7" in p:
        spans = [(0, DAY)]
    else:
        spans = []
        for h1, m1, h2, m2 in _RANGE.findall(t):
            a, b = int(h1) * 60 + int(m1 or 0), int(h2) * 60 + int(m2 or 0)
            if b <= a:  # qua nửa đêm → cắt ở 24:00 (lịch chỉ trong một ngày)
                b = DAY
            spans.append((a, b))
        if not spans:
            return None
        if ("nghi trua" in p or "dong cua trua" in p) and "khong nghi trua" not in p and len(spans) == 2 and spans[1][0] > spans[0][0]:
            (a, b), (c, d) = spans  # "08:00 - 16:00 (đóng cửa trưa 11:30 - 13:30)"
            if a < c < d < b:
                spans = [(a, c), (d, b)]
    return {d: list(spans) for d in _ALL if d not in set(closed_weekdays or [])}


def _load():
    with open(DATA, encoding="utf-8-sig") as f:
        rows = json.load(f)
    out = {}
    for r in rows:
        pid = r["id"]
        if pid in SEASONAL:
            weekly = SEASONAL[pid]
        elif pid in OVERRIDES:
            weekly = OVERRIDES[pid]
        else:
            weekly = parse_hours(r.get("opening_hours"), r.get("closed_weekdays"))
        r["_weekly"] = weekly
        r["_inner"] = r.get("district") in INNER_DISTRICTS
        out[pid] = r
    return out


PLACES = _load()


def _matrix():
    if not os.path.exists(MATRIX):
        return {}
    with open(MATRIX, encoding="utf-8") as f:
        return json.load(f)


MATRIX_DATA = _matrix()


def windows(pid, date):
    """Khung mở cửa của địa điểm vào ngày đi. None = chưa có dữ liệu giờ; [] = đóng cửa hôm đó."""
    p = PLACES[pid]
    w = p["_weekly"]
    if w is None:
        return None
    if pid in SEASONAL:
        w = w["nong"] if 4 <= date.month <= 10 else w["lanh"]
    return list(w.get(date.weekday(), []))


def km(a, b):
    """Khoảng cách đường chim bay (km) giữa hai toạ độ (lat, lng)."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def travel_minutes(a_id, a_xy, b_id, b_xy, mode="xe_may"):
    """Phút đi từ A đến B (ước tính) và nguồn. Lấy max(OSRM, đường chim bay × 1,3 ÷ tốc độ), tối thiểu 5 phút."""
    est = km(a_xy, b_xy) * 1.3 / SPEED_KMH.get(mode, 20) * 60
    osrm = MATRIX_DATA.get("%s|%s|%s" % (a_id, b_id, mode))
    # ponytail: OSRM công cộng không tính kẹt xe nội thành nên quá lạc quan; lấy max với ước tính tốc độ đô thị
    if osrm is not None and osrm >= est:
        return max(5, int(round(osrm))), "osrm"
    return max(5, int(math.ceil(est))), "duong_chim_bay"


def fmt(minutes):
    return "%02d:%02d" % divmod(int(minutes), 60)


def next_date(weekday, today=None):
    """Ngày gần nhất (kể cả hôm nay) rơi vào thứ `weekday` (0 = thứ Hai)."""
    today = today or dt.date.today()
    return today + dt.timedelta(days=(weekday - today.weekday()) % 7)


def match_places(text):
    """Tìm ID địa điểm được nhắc trong văn bản (khớp tên / tên gọi khác, không dấu). Dùng khi model ở chế độ giả."""
    p = " " + re.sub(r"[^a-z0-9 ]", " ", _plain(text)) + " "
    found = []
    for pid, alias in ALIASES:
        if " " + alias + " " in p and pid not in found:
            found.append(pid)
            p = p.replace(" " + alias + " ", " ", 1)
    return found


def _aliases():
    pairs = []
    extra = {"hn_04": ["lang bac", "lang chu tich ho chi minh"], "hn_10": ["hoang thanh"], "hn_11": ["hoa lo", "nha tu hoa lo"],
             "hn_15": ["bao tang dan toc hoc"], "hn_46": ["bao tang my thuat"], "hn_47": ["bao tang phu nu"],
             "hn_48": ["bao tang lich su quoc gia"], "hn_09": ["van mieu"], "hn_01": ["ho guom", "ho hoan kiem"],
             "hn_12": ["chua tran quoc"], "hn_13": ["chua mot cot"], "hn_14": ["den ngoc son"], "hn_40": ["cho dong xuan"],
             "hn_76": ["bao tang ho chi minh"], "hn_33": ["pho di bo"], "hn_32": ["mua roi"], "hn_68": ["van mieu buoi toi", "van mieu toi"]}
    for pid, r in PLACES.items():
        names = [re.sub(r"\(.*?\)", "", r["name"])] + extra.get(pid, [])
        for n in names:
            a = re.sub(r"[^a-z0-9 ]", " ", _plain(n))
            a = " ".join(a.split())
            if len(a) >= 5:
                pairs.append((pid, a))
    return sorted(pairs, key=lambda x: -len(x[1]))  # tên dài khớp trước ("van mieu buoi toi" trước "van mieu")


ALIASES = _aliases()
# Điểm xuất phát không phải địa điểm tham quan: toạ độ trung tâm quận (xấp xỉ).
ANCHORS = {"cau giay": (21.0333, 105.7940), "ba dinh": (21.0340, 105.8150), "dong da": (21.0180, 105.8290),
           "hai ba trung": (21.0060, 105.8570), "tay ho": (21.0700, 105.8190), "thanh xuan": (20.9940, 105.8100)}
ANCHOR_NAMES = {"cau giay": "Cầu Giấy", "ba dinh": "Ba Đình", "dong da": "Đống Đa", "hai ba trung": "Hai Bà Trưng",
                "tay ho": "Tây Hồ", "thanh xuan": "Thanh Xuân"}
