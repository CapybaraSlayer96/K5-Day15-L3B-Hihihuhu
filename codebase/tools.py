"""Bốn công cụ chỉ đọc của TripSwipe. Không công cụ nào tác động ra ngoài (không đặt vé, không gửi tin)."""
from places import PLACES, WEEKDAYS, fmt, travel_minutes, windows
from planner import check
from tracing import tool, TOOLS  # noqa: F401


@tool
def tra_dia_diem(ids: list) -> list:
    """Tra thông tin địa điểm. Input: danh sách ID. Output: [{id, name, district, category, price_max_vnd, inner}] (bỏ ID lạ). Chỉ đọc."""
    return [{"id": i, "name": PLACES[i]["name"], "district": PLACES[i]["district"], "category": PLACES[i]["category"],
             "price_max_vnd": PLACES[i].get("price_max_vnd"), "inner": PLACES[i]["_inner"]} for i in ids if i in PLACES]


@tool
def tra_gio_mo_cua(pid: str, date) -> dict:
    """Giờ mở cửa vào ngày đi. Input: ID, ngày. Output: {id, weekday, windows: ["HH:MM–HH:MM"] | [] (đóng) | None (chưa có dữ liệu)}. Chỉ đọc."""
    w = windows(pid, date)
    return {"id": pid, "weekday": WEEKDAYS[date.weekday()],
            "windows": None if w is None else ["%s–%s" % (fmt(a), fmt(b)) for a, b in w]}


@tool
def uoc_thoi_gian_di(a_id: str, a_xy: tuple, b_id: str, b_xy: tuple, mode: str = "xe_may") -> dict:
    """Ước thời gian đi A → B. Input: ID + toạ độ hai đầu, phương tiện. Output: {minutes, source} (luôn là ước tính). Chỉ đọc."""
    m, src = travel_minutes(a_id, a_xy, b_id, b_xy, mode)
    return {"minutes": m, "source": src}


@tool
def kiem_lich_trinh(items: list, cfg: dict) -> list:
    """Kiểm lịch: giờ mở cửa, ngày đóng, nghỉ trưa, thời gian đi, chồng giờ, khung giờ. Input: lịch + cấu hình. Output: danh sách vi phạm. Chỉ đọc."""
    return check(items, cfg)
