"""Kiểm bộ kiểm lịch và luồng văn bản. Chạy: python tests/test_core.py"""
import datetime as dt
import os
import sys

os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

from agent import answer  # noqa: E402
from places import PLACES  # noqa: E402
from planner import check  # noqa: E402

MON, WED = dt.date(2026, 11, 30), dt.date(2026, 12, 2)
XY = (PLACES["hn_01"]["lat"], PLACES["hn_01"]["lng"])


def cfg(date, t0=8 * 60, t1=17 * 60):
    return {"date": date, "start_min": t0, "end_min": t1, "start_xy": XY, "start_id": "hn_01", "mode": "xe_may"}


def item(pid, a, b):
    return {"id": pid, "arrive": a, "leave": b}


assert check([item("hn_04", 9 * 60, 10 * 60)], cfg(MON)), "Lăng thứ Hai phải vi phạm"
assert not check([item("hn_04", 9 * 60, 10 * 60)], cfg(WED)), "Lăng sáng thứ Tư hợp lệ"
assert check([item("hn_04", 15 * 60, 16 * 60)], cfg(WED)), "Lăng buổi chiều phải vi phạm"
assert check([item("hn_48", 11 * 60, 12 * 60 + 30)], cfg(WED)), "Bảo tàng Lịch sử Quốc gia chạm nghỉ trưa"
assert check([item("hn_46", 9 * 60, 10 * 60)], cfg(MON)), "Bảo tàng Mỹ thuật đóng thứ Hai"
assert check([item("hn_11", 9 * 60, 10 * 60), item("hn_47", 9 * 60 + 30, 10 * 60 + 30)], cfg(WED)), "chồng giờ"
assert check([item("hn_11", 16 * 60, 17 * 60 + 30)], cfg(WED, t1=17 * 60)), "vượt khung giờ"

out = answer("Nhóm mình muốn viếng Lăng Bác rồi đi Bảo tàng Dân tộc học, đi 8:00–16:00 từ Hồ Gươm.")["output"]
assert "thứ mấy" in out and "LICH_JSON" not in out, "thiếu ngày đi phải hỏi lại, không trả lịch"
out = answer("Thứ Hai tuần sau đi 8:00–15:00 từ Hồ Gươm, viếng Lăng Bác, Văn Miếu và Hoàng thành.")["output"]
assert "Lăng Chủ tịch Hồ Chí Minh: đóng cửa Thứ Hai" in out
out = answer("Lên lịch 3 ngày Hà Nội – Hạ Long cho nhóm mình.")["output"]
assert "MỘT ngày" in out and "LICH_JSON" not in out
from places import travel_leg  # noqa: E402

P = {i: (PLACES[i]["lat"], PLACES[i]["lng"]) for i in ("hn_09", "hn_12")}
m, meters, src = travel_leg("hn_09", P["hn_09"], "hn_12", P["hn_12"], "xe_may")
assert src == "osrm" and meters > 1000 and m >= 5, "xe máy dùng ma trận đường thật"
assert travel_leg("x", P["hn_09"], "y", P["hn_12"], "xe_may")[2] == "duong_chim_bay", "điểm lạ → dự phòng"
assert travel_leg("hn_09", P["hn_09"], "hn_12", P["hn_12"], "di_bo")[0] > m, "đi bộ chậm hơn xe máy"
print("ok")
