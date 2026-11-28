"""Kiểm bộ kiểm lịch và luồng văn bản. Chạy: python tests/test_core.py"""
import datetime as dt
import os
import sys

os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

from agent import answer  # noqa: E402
from group import build_deck, plan_group  # noqa: E402
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
assert check([item("hn_12", 12 * 60 + 55, 13 * 60 + 55)], cfg(WED)), "Chùa Trấn Quốc chạm đóng cửa trưa 11:30-13:30"
assert not check([item("hn_12", 13 * 60 + 30, 14 * 60 + 30)], cfg(WED)), "Chùa Trấn Quốc chiều 13:30-14:30 hợp lệ"
assert check([item("hn_46", 9 * 60, 10 * 60)], cfg(MON)), "Bảo tàng Mỹ thuật đóng thứ Hai"
assert check([item("hn_11", 9 * 60, 10 * 60), item("hn_47", 9 * 60 + 30, 10 * 60 + 30)], cfg(WED)), "chồng giờ"
assert check([item("hn_11", 16 * 60, 17 * 60 + 30)], cfg(WED, t1=17 * 60)), "vượt khung giờ"

out = answer("Nhóm mình muốn viếng Lăng Bác rồi đi Bảo tàng Dân tộc học, đi 8:00–16:00 từ Hồ Gươm.")["output"]
assert "thứ mấy" in out and "LICH_JSON" not in out, "thiếu ngày đi phải hỏi lại, không trả lịch"
out = answer("Thứ Hai tuần sau đi 8:00–15:00 từ Hồ Gươm, viếng Lăng Bác, Văn Miếu và Hoàng thành.")["output"]
assert "Lăng Chủ tịch Hồ Chí Minh: đóng cửa Thứ Hai" in out
out = answer("Lên lịch 3 ngày Hà Nội – Hạ Long cho nhóm mình.")["output"]
assert "MỘT ngày" in out and "LICH_JSON" not in out
# Kiểm A3: build_deck + plan_group (TS-03, TS-06)
mon_cfg = {**cfg(MON), "budget_per_person": 500_000}
deck_mon = build_deck(mon_cfg)
deck_ids = [c["id"] for c in deck_mon]
assert 0 < len(deck_mon) <= 20, "bộ thẻ phải có 1–20 thẻ"
assert len(deck_ids) == len(set(deck_ids)), "bộ thẻ không được trùng ID"
assert not ({"hn_04", "hn_15", "hn_46"} & set(deck_ids)), "thứ Hai không được có Lăng Bác, BT Dân tộc học, BT Mỹ thuật"
assert all(isinstance(c["reason"], str) and c["reason"] and not any(ch.isdigit() for ch in c["reason"]) for c in deck_mon), "lý do không được chứa số"

free_deck = build_deck({**cfg(WED), "budget_per_person": 0})
assert free_deck and all(PLACES[c["id"]].get("price_max_vnd") == 0 for c in free_deck), "budget 0 chỉ nhận điểm miễn phí"

scores_mon = {"hn_04": 1.0, "hn_09": 0.9, "hn_10": 0.8, "hn_11": 0.7, "hn_22": 0.8}
res_mon = plan_group(mon_cfg, scores_mon, pinned=["hn_09"])
assert res_mon["violations"] == [], "plan_group không bao giờ trả lịch vi phạm"
placed_ids = [it["id"] for it in res_mon["items"]]
assert "hn_04" not in placed_ids and "hn_09" in placed_ids, "Lăng thứ Hai phải bị loại, điểm ghim phải có trong lịch"
assert any(d["id"] == "hn_04" and "Thứ Hai" in d["reason"] for d in res_mon["dropped"])

tight_budget = {**cfg(WED), "budget_per_person": 50_000}
res_budget = plan_group(tight_budget, {"hn_09": 0.9, "hn_10": 0.9, "hn_11": 0.9, "hn_01": 0.8})
assert res_budget["violations"] == []
total_price = sum((PLACES[it["id"]].get("price_max_vnd") or 0) for it in res_budget["items"])
assert total_price <= 50_000, "tổng chi phí lịch không được vượt budget mỗi người"

full_day = {**cfg(WED, t0=8 * 60, t1=21 * 60), "budget_per_person": 1_000_000}
res_meals = plan_group(full_day, {"hn_09": 0.9, "hn_10": 0.9, "hn_11": 0.9, "hn_47": 0.9, "hn_14": 0.9,
                                  "hn_22": 0.9, "hn_25": 0.9, "hn_23": 0.9, "hn_28": 0.9, "hn_29": 0.9})
assert res_meals["violations"] == []
cats = [it["category"] for it in res_meals["items"]]
assert not any(a == b == "food_drink" for a, b in zip(cats, cats[1:])), "không được xếp 2 quán ăn liền kề nhau"
assert len({it["meal_slot"] for it in res_meals["items"] if it["meal_slot"]}) >= 2, "phải chia quán ăn theo nhiều bữa"

from places import travel_leg  # noqa: E402

P = {i: (PLACES[i]["lat"], PLACES[i]["lng"]) for i in ("hn_09", "hn_12")}
m, meters, src = travel_leg("hn_09", P["hn_09"], "hn_12", P["hn_12"], "xe_may")
assert src == "osrm" and meters > 1000 and m >= 5, "xe máy dùng ma trận đường thật"
assert travel_leg("x", P["hn_09"], "y", P["hn_12"], "xe_may")[2] == "duong_chim_bay", "điểm lạ → dự phòng"
assert travel_leg("hn_09", P["hn_09"], "hn_12", P["hn_12"], "di_bo")[0] > m, "đi bộ chậm hơn xe máy"
print("ok")
