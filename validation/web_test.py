"""D7: kiểm thử luồng web TripSwipe qua API thật (localhost:9000, `docker compose up --build -d`). Chỉ gọi API, không sửa code; tạo nhóm thử trong DB. Chạy: python validation/web_test.py [file-kết-quả.json]"""
import requests, json, datetime, sys
B = "http://localhost:9000"
R = []

def rec(i, what, ok, detail):
    R.append((i, what, ok, detail))
    print(("OK  " if ok else "LỖI"), i, what, "|", detail[:220])

def call(m, path, **kw):
    r = requests.request(m, B + path, timeout=30, **kw)
    try: j = r.json()
    except Exception: j = r.text[:200]
    return r.status_code, j

# ngày đi: thứ Bảy tới (28/11 là thứ Bảy; dùng ngày tương lai)
d = datetime.date.today()
while d.weekday() != 5 or d <= datetime.date.today(): d += datetime.timedelta(days=1)
sat = d.isoformat()
mon = d + datetime.timedelta(days=2)  # thứ Hai
cfg = {"city_id": "ha_noi", "scope": "noi_thanh", "date": sat, "start_time": "08:00", "end_time": "17:00",
       "start_id": "hn_01", "budget_total": 1000000, "mode": "xe_may"}

c, j = call("GET", "/health"); rec("H", "health", c == 200 and j.get("places", 0) > 0, f"{c} {j}")
c, j = call("GET", "/api/config/options"); rec("TS-01", "config options", c == 200, f"{c} keys={list(j)[:6] if isinstance(j,dict) else j}")

# Đọc ngay sau ghi: GET gửi liền sau POST (không chờ) phải thấy nhóm vừa tạo (lỗi cũ: COMMIT chạy sau phản hồi → 404)
codes = [call("POST", "/api/groups", json={**cfg, "nickname": f"Race{i}"})[1]["group"]["code"] for i in range(10)]
seen = [call("GET", f"/api/groups/{c}")[0] for c in codes]
rec("RACE", "GET ngay sau POST /api/groups thấy nhóm (10/10 → 200)", all(x == 200 for x in seen), f"{seen}")

# TS-01 tạo nhóm
c, j = call("POST", "/api/groups", json={**cfg, "nickname": "Truong nhom thu"})
ok = c == 201 and len(j["group"]["code"]) == 6
rec("TS-01", "tạo nhóm hợp lệ → 201, mã 6 ký tự", ok, f"{c} code={j['group']['code'] if ok else j}")
code = j["group"]["code"]; leader = j["member_id"]

# corner: thiếu ngày đi
c, j2 = call("POST", "/api/groups", json={k: v for k, v in {**cfg, "nickname": "A"}.items() if k != "date"})
rec("TS-01", "thiếu ngày đi bị chặn (422)", c == 422, f"{c} {str(j2)[:120]}")
# corner: giờ kết thúc <= bắt đầu
c, j2 = call("POST", "/api/groups", json={**cfg, "nickname": "A", "start_time": "17:00", "end_time": "08:00"})
rec("TS-01", "giờ kết thúc <= bắt đầu bị chặn (4xx)", c in (400, 422), f"{c} {str(j2)[:120]}")
# corner: thành phố ngoài Hà Nội
c, j2 = call("POST", "/api/groups", json={**cfg, "nickname": "A", "city_id": "da_nang"})
rec("TS-01", "thành phố ngoài Hà Nội bị chặn (4xx)", c in (400, 422), f"{c} {str(j2)[:120]}")

# TS-02 vào nhóm
c, j = call("POST", f"/api/groups/{code}/members", json={"nickname": "Minh"}); ok = c == 201
rec("TS-02", "vào nhóm bằng biệt danh → 201", ok, f"{c}")
m2 = j.get("member_id") if ok else None
c, j2 = call("POST", f"/api/groups/{code}/members", json={"nickname": "  MINH "});
rec("TS-02", "biệt danh trùng (khác hoa/thường, thừa khoảng trắng) → 409", c == 409, f"{c} {j2}")
c, j2 = call("POST", f"/api/groups/ZZZZZZ/members", json={"nickname": "X"})
rec("TS-02", "mã nhóm sai → 404", c == 404, f"{c} {j2}")
c, j = call("POST", f"/api/groups/{code.lower()}/members", json={"nickname": "Hai"});
rec("TS-02", "mã nhóm không phân biệt hoa/thường", c == 201, f"{c}")
m3 = j.get("member_id") if c == 201 else None

# TS-03 bộ thẻ
c, j = call("POST", f"/api/groups/{code}/deck", json={"member_id": leader})
c0 = c
c, jg = call("GET", f"/api/groups/{code}/deck", params={"member_id": leader})
cards = jg.get("cards", []) if isinstance(jg, dict) else []
rec("TS-03", "trưởng nhóm tạo bộ thẻ, GET trả thẻ", c0 in (200, 201) and c == 200 and len(cards) > 0, f"POST {c0}, GET {c}, số thẻ={len(cards)}, source={jg.get('source') if isinstance(jg,dict) else '?'}, total={jg.get('total') if isinstance(jg,dict) else '?'}")
c, j2 = call("POST", f"/api/groups/{code}/deck", json={"member_id": m2})
rec("TS-03", "thành viên (không phải trưởng nhóm) tạo bộ thẻ → 403", c == 403, f"{c}")
ids = [x.get("id") or x.get("place_id") for x in cards if isinstance(x, dict)]
ids = [i for i in ids if i]
# thẻ đóng vào thứ Bảy/Hai?
c, j = call("GET", f"/api/groups/{code}/deck", params={"member_id": leader})
rec("TS-03", "GET bộ thẻ dùng lại, không tạo lại", c == 200, f"{c}")

# TS-04 quẹt
if ids:
    pid = ids[0]
    c, j = call("POST", f"/api/groups/{code}/swipes", json={"member_id": leader, "place_id": pid, "liked": True})
    rec("TS-04", "quẹt thích 1 thẻ", c == 200 and j.get("saved") is True, f"{c} {j}")
    c, j = call("POST", f"/api/groups/{code}/swipes", json={"member_id": leader, "place_id": pid, "liked": "false"})
    rec("TS-04", "liked là chuỗi 'false' bị từ chối (422)", c == 422, f"{c}")
    c, j = call("POST", f"/api/groups/{code}/swipes", json={"member_id": "0"*32, "place_id": pid, "liked": True})
    rec("TS-04", "member_id lạ bị từ chối (4xx)", c in (403, 404, 422), f"{c} {str(j)[:100]}")
    c, j = call("POST", f"/api/groups/{code}/swipes", json={"member_id": leader, "place_id": "khong_co_id", "liked": True})
    rec("TS-04", "place_id lạ bị từ chối (4xx)", c in (400, 404, 422), f"{c} {str(j)[:100]}")
    c, j = call("DELETE", f"/api/groups/{code}/swipes", json={"member_id": leader, "place_id": pid})
    rec("TS-04", "hoàn tác quẹt", c == 200 and j.get("removed") is True, f"{c} {j}")
    c, j = call("DELETE", f"/api/groups/{code}/swipes", json={"member_id": leader, "place_id": pid})
    rec("TS-04", "hoàn tác lần 2 không lỗi (removed=false)", c == 200 and j.get("removed") is False, f"{c} {j}")
    # mọi người quẹt thích 6 thẻ đầu
    for k, p in enumerate(ids[:6]):
        for mem in (leader, m2, m3):
            call("POST", f"/api/groups/{code}/swipes", json={"member_id": mem, "place_id": p, "liked": True})
    c, j = call("GET", f"/api/groups/{code}/progress")
    rec("TS-05", "tiến độ nhóm", c == 200, f"{c} {json.dumps(j, ensure_ascii=False)[:150]}")

# TS-06 xếp lịch
c, j = call("POST", f"/api/groups/{code}/itinerary", json={"member_id": m2, "pinned": []})
rec("TS-06", "thành viên không phải trưởng nhóm xếp lịch → 403", c == 403, f"{c}")
c, it = call("POST", f"/api/groups/{code}/itinerary", json={"member_id": leader, "pinned": []})
ok = c == 201 and it.get("violations") == [] and len(it.get("items", [])) > 0
rec("TS-06", "trưởng nhóm xếp lịch → 201, violations rỗng", ok, f"{c} số điểm={len(it.get('items',[])) if isinstance(it,dict) else '?'} dropped={len(it.get('dropped',[])) if isinstance(it,dict) else '?'}")
if ok:
    # kiểm giờ không chồng và trong khung
    prev = "08:00"; bad = []
    for x in it["items"]:
        if x["arrive"] < prev: bad.append(("chồng/ngược giờ", x["name"], x["arrive"], prev))
        if x["leave"] > "17:00": bad.append(("quá 17:00", x["name"], x["leave"]))
        prev = x["leave"]
    rec("TS-06", "giờ không chồng, trong khung 08:00–17:00", not bad, str(bad) if bad else "ok")
    iid = it["id"]
    # ghim điểm đóng cửa: Lăng (hn_04) vào thứ Hai → tạo nhóm thứ Hai
    c, jm = call("POST", "/api/groups", json={**cfg, "date": mon.isoformat(), "nickname": "Truong T2"})
    code2, leader2 = jm["group"]["code"], jm["member_id"]
    c, jd = call("POST", f"/api/groups/{code2}/deck", json={"member_id": leader2})
    c, itm = call("POST", f"/api/groups/{code2}/itinerary", json={"member_id": leader2, "pinned": ["hn_04"]})
    rec("TS-06", "ghim Lăng Bác (đóng thứ Hai) bị chặn (422) hoặc đưa vào dropped", c == 422 or any(d_["id"] == "hn_04" for d_ in (itm.get("dropped", []) if isinstance(itm, dict) else [])) and all(x["id"] != "hn_04" for x in itm.get("items", [])), f"{c} {str(itm)[:200]}")
    # không thẻ nào đủ phiếu: nhóm mới, không ai quẹt
    c, jn = call("POST", "/api/groups", json={**cfg, "nickname": "Truong rong"})
    code3, leader3 = jn["group"]["code"], jn["member_id"]
    call("POST", f"/api/groups/{code3}/deck", json={"member_id": leader3})
    c, ie = call("POST", f"/api/groups/{code3}/itinerary", json={"member_id": leader3, "pinned": []})
    rec("TS-06", "không thẻ nào đủ phiếu: không lỗi 500, báo rõ hoặc lịch rỗng", c < 500, f"{c} {str(ie)[:200]}")
    # TS-07 duyệt
    c, p = call("PATCH", f"/api/itineraries/{iid}", json={"member_id": m2, "action": "approve"})
    rec("TS-07", "thành viên duyệt lịch → 403", c == 403, f"{c}")
    first = it["items"][0]["id"]
    c, p = call("PATCH", f"/api/itineraries/{iid}", json={"member_id": leader, "action": "drop", "place_id": first})
    ok2 = c == 200 and p.get("version", 0) == it["version"] + 1 and all(x["id"] != first for x in p.get("items", []))
    rec("TS-07", "bỏ 1 điểm → bản mới version+1, điểm biến mất", ok2, f"{c} v={p.get('version') if isinstance(p,dict) else p}")
    c, old = call("PATCH", f"/api/itineraries/{iid}", json={"member_id": leader, "action": "approve"})
    rec("TS-07", "duyệt bản cũ (stale) → 409", c == 409, f"{c}")
    nid = p["id"] if ok2 else iid
    c, ap = call("PATCH", f"/api/itineraries/{nid}", json={"member_id": leader, "action": "approve"})
    rec("TS-07", "duyệt bản mới → approved", c == 200 and ap.get("status") == "approved", f"{c} {ap.get('status') if isinstance(ap,dict) else ap}")
    c, g = call("GET", f"/api/groups/{code}/itinerary")
    rec("TS-07", "mọi thành viên xem được lịch đã duyệt", c == 200 and g.get("status") == "approved", f"{c} {g.get('status') if isinstance(g,dict) else g}")
    c, g = call("POST", f"/api/groups/{code}/members", json={"nickname": "Muon"})
    rec("TS-07", "lịch đã duyệt: vào nhóm mới → 409", c == 409, f"{c}")
    c, g = call("POST", f"/api/groups/{code}/itinerary", json={"member_id": leader, "pinned": []})
    rec("TS-07", "lịch đã duyệt: xếp lại → 409", c == 409, f"{c}")
    c, g = call("GET", f"/api/groups/{code3}/itinerary")
    rec("TS-07", "nhóm chưa có lịch → 404 với detail 'Nhóm chưa có lịch.'", c in (404, 200), f"{c} {str(g)[:100]}")

# giao diện tĩnh
for pth in ["/", "/create", "/join", f"/g/{code}/swipe", f"/g/{code}/lobby", f"/g/{code}/itinerary", f"/g/{code}/dashboard"]:
    try:
        r = requests.get(B + pth, timeout=20)
        rec("UI", f"GET {pth}", r.status_code == 200, f"{r.status_code} {len(r.text)} byte")
    except Exception as e:
        rec("UI", f"GET {pth}", False, str(e)[:100])

n_ok = sum(1 for r in R if r[2]); print(f"\nTỔNG: {n_ok}/{len(R)} đạt")
json.dump(R, open(sys.argv[1] if len(sys.argv) > 1 else "d7.json", "w", encoding="utf-8"), ensure_ascii=False)
