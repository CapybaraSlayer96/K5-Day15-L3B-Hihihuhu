# TripSwipe — Hợp đồng và ví dụ API B1–B3

Backend: FastAPI + Postgres, base URL `http://localhost:9000`; OpenAPI tại `/docs` và `/openapi.json`. Các mã nhóm, biệt danh và ID thành viên dưới đây chỉ là ví dụ. Sửa ngày đi thành hôm nay hoặc ngày tương lai theo giờ Hà Nội khi thử lại.

## 1. Quy ước chung cho UI

- Request/response dùng JSON, thời gian `HH:MM`, ngày ISO `YYYY-MM-DD`, tiền VND nguyên không âm, múi giờ `Asia/Ho_Chi_Minh`.
- `member_id` là chuỗi ngẫu nhiên được cấp riêng khi tạo/vào nhóm. Lưu ở trình duyệt theo mã nhóm; đây là quyền thao tác của thành viên trong demo localhost, không chia sẻ nó trong link nhóm. API xem nhóm/tiến độ không công khai ID của thành viên khác. Chưa có đăng nhập hay cơ chế khôi phục ID bị mất.
- Tạo/vào nhóm trả 201; thao tác khác trả 200. Mã nhóm không phân biệt hoa/thường. Biệt danh được chuẩn hóa Unicode, bỏ khoảng trắng thừa và kiểm trùng không phân biệt hoa/thường trong một nhóm.
- Lỗi nghiệp vụ: `{"detail": "Thông báo tiếng Việt"}`. Lỗi kiểm schema 422 dùng `detail` là danh sách lỗi chuẩn FastAPI, có `loc`, `msg`, `type`; UI đọc `loc` để gắn lỗi vào trường tương ứng.
- Lịch đã duyệt chỉ xem: vào nhóm/quẹt/hoàn tác/tạo bộ thẻ trả 409. `POST` bộ thẻ chỉ trưởng nhóm được gọi; thành viên khác trả 403.
- B3 chưa có endpoint tạo/duyệt/ghim lịch B4. `join_url` là đường dẫn dành cho màn U2 sẽ được Bảo triển khai; hiện chưa có trang `/join`.

## 2. Cấu hình — `GET /api/config/options`

Response gồm:

```json
{
  "cities": [{"id": "ha_noi", "name": "Hà Nội", "enabled": true}],
  "scopes": [
    {"id": "noi_thanh", "name": "Nội thành", "enabled": true},
    {"id": "ngoai_thanh", "name": "Ngoại thành — sắp có", "enabled": false}
  ],
  "timezone": "Asia/Ho_Chi_Minh",
  "start_locations": [{"id": "hn_01", "name": "Hồ Hoàn Kiếm (Hồ Gươm)", "lat": 21.028774, "lng": 105.852336, "approximate": false}],
  "transport_modes": [{"id": "xe_may", "name": "Xe máy"}, {"id": "o_to", "name": "Ô tô"}, {"id": "di_bo", "name": "Đi bộ"}],
  "defaults": {"start_time": "08:00", "end_time": "17:00", "start_id": "hn_01", "mode": "xe_may"},
  "deck_limit": 20,
  "deck_strategy": "provisional_rating"
}
```

`start_locations` thực tế chứa đầy đủ điểm xuất phát nội thành và mốc trung tâm quận. Mốc quận có `approximate: true`; UI cần nêu rõ tọa độ xấp xỉ. Ví dụ trên rút ngắn danh sách, không phải toàn bộ options.

## 3. Tạo nhóm — `POST /api/groups`

Request:

```json
{
  "nickname": "Trưởng nhóm demo",
  "city_id": "ha_noi",
  "scope": "noi_thanh",
  "date": "2026-12-05",
  "start_time": "08:00",
  "end_time": "17:00",
  "start_id": "hn_01",
  "budget_total": 1000000,
  "mode": "xe_may"
}
```

Response 201, ví dụ:

```json
{
  "group": {
    "code": "HN7K2Q",
    "status": "swiping",
    "config": {
      "city_id": "ha_noi", "scope": "noi_thanh", "date": "2026-12-05",
      "start_time": "08:00", "end_time": "17:00", "start_id": "hn_01",
      "budget_total": 1000000, "mode": "xe_may",
      "start_xy": [21.028774, 105.852336],
      "start_name": "Hồ Hoàn Kiếm (Hồ Gươm)", "start_approximate": false
    },
    "member_count": 1,
    "members": [{"nickname": "Trưởng nhóm demo", "is_leader": true}],
    "budget_per_person": 1000000,
    "join_url": "/join?code=HN7K2Q",
    "deck_source": null,
    "warnings": []
  },
  "member_id": "11111111111111111111111111111111",
  "is_leader": true
}
```

`date`, giờ, xuất phát, ngân sách, phương tiện và biệt danh bắt buộc. Thiếu ngày, ngày quá khứ, giờ không hợp lệ/kết thúc không sau bắt đầu, budget âm, phương tiện không hỗ trợ hoặc xuất phát ngoài danh sách → 422. Khung dưới một giờ vẫn được tạo, có cảnh báo. `budget_total = 0` chỉ chọn thẻ được ghi rõ miễn phí.

## 4. Xem nhóm — `GET /api/groups/{code}`

Trả chính object `group` ở mục 3, cập nhật `member_count`, danh sách biệt danh và `budget_per_person`. Mã nhóm sai → 404. Không trả `member_id` của người khác.

## 5. Vào nhóm — `POST /api/groups/{code}/members`

Request:

```json
{"nickname": "Thành viên demo"}
```

Response 201:

```json
{
  "member_id": "22222222222222222222222222222222",
  "is_leader": false,
  "group": {
    "code": "HN7K2Q", "status": "swiping", "member_count": 2,
    "budget_per_person": 500000,
    "members": [{"nickname": "Trưởng nhóm demo", "is_leader": true}, {"nickname": "Thành viên demo", "is_leader": false}]
  }
}
```

Object `group` thực tế còn đủ các trường như mục 3. Biệt danh trùng → 409; nhóm không tồn tại → 404. Ngân sách mỗi người được tính lại theo số thành viên hiện tại, làm tròn xuống VND.

## 6. Bộ thẻ — `POST|GET /api/groups/{code}/deck`

Tạo bộ thẻ (chỉ trưởng nhóm):

```http
POST /api/groups/HN7K2Q/deck
Content-Type: application/json

{"member_id":"11111111111111111111111111111111"}
```

```json
{"code": "HN7K2Q", "source": "provisional_rating", "total": 20}
```

Lấy bộ thẻ và trạng thái quẹt cá nhân:

```http
GET /api/groups/HN7K2Q/deck?member_id=22222222222222222222222222222222
```

```json
{
  "code": "HN7K2Q",
  "source": "provisional_rating",
  "total": 20,
  "remaining": 19,
  "budget_per_person": 500000,
  "warnings": ["Bộ thẻ tạm theo rating trong dữ liệu, chưa phải lựa chọn của AI."],
  "cards": [{
    "id": "hn_01", "name": "Hồ Hoàn Kiếm (Hồ Gươm)", "rank": 1,
    "ai_reason": "Điểm đủ điều kiện, tạm sắp theo đánh giá trong dữ liệu.",
    "hours_status": "open", "opening_windows": [{"open": "00:00", "close": "24:00"}],
    "hours_for_date": "2026-12-05", "swiped": true, "liked": false
  }]
}
```

Ví dụ rút ngắn `cards` và trường POI. Mỗi thẻ thực tế có **đầy đủ trường JSON địa điểm**, gồm ảnh, loại, quận, tag, khoảng giá, rating, mô tả, mẹo, review tổng hợp và nguồn, cộng các trường trạng thái trên. `liked: null` khi chưa quẹt; `false` nghĩa đã bỏ qua. `remaining` là số thẻ chưa quẹt của thành viên yêu cầu. Không truyền `member_id` thì xem danh mục chung, mọi thẻ có trạng thái chưa quẹt.

- Lần GET đầu tiên tự tạo bộ thẻ nếu chưa có; các lần GET/POST sau dùng lại bộ thẻ đã lưu, không xóa phiếu, không tự gọi lại AI.
- Bộ thẻ tạm lọc nội thành, có giờ đã đọc được, không đóng vào ngày đi, khung mở giao khung giờ nhóm, giá tối đa không vượt budget/người nếu biết giá; sau đó lấy tối đa 20 điểm theo rating. Đây là tạm thời theo TASKS B3, không giả làm AI.
- Thẻ không có giờ được loại khỏi bộ thẻ; API chi tiết vẫn có thể trả `hours_status: unknown`.
- Khi có thành viên mới, tính lại budget/người và **ẩn thẻ vượt budget hiện tại**. Phiếu lịch sử vẫn giữ trong DB; `total`, `remaining`, tiến độ chỉ tính các thẻ đang hợp lệ. UI nên tải lại deck sau khi tiến độ báo số thành viên thay đổi. Bộ thẻ không tự bổ sung thẻ mới để thay các thẻ bị ẩn.
- Backend nhận `deck_builder` qua `create_app(database=..., deck_builder=build_deck)` để Hải nối hàm A3. Hàm nhận `cfg` đúng TASKS, trả `[{id, rank, reason}]`. ID/giờ/giá và lý do được kiểm lại; AI lỗi trả 502, không âm thầm đổi sang bộ thẻ tạm. Khởi chạy mặc định hiện dùng bộ thẻ tạm.

## 7. Chi tiết địa điểm — `GET /api/places/{id}?date=YYYY-MM-DD`

Trả toàn bộ bản ghi POI gốc từ DB. Khi có `date`, thêm `hours_for_date`, `hours_status` (`open`/`closed`/`unknown`) và `opening_windows`. Ngày đóng trả `[]`; chưa có dữ liệu giờ trả `null`, không gán mở cả ngày. `hours_status: open` nghĩa có khoảng mở trong ngày, không có nghĩa đang mở tại thời điểm gọi API. Địa điểm không tồn tại → 404; ngày không đúng định dạng → 422.

## 8. Lưu phiếu — `POST /api/groups/{code}/swipes`

```json
{"member_id": "22222222222222222222222222222222", "place_id": "hn_01", "liked": true}
```

Response:

```json
{"member_id": "22222222222222222222222222222222", "place_id": "hn_01", "liked": true, "saved": true}
```

Quẹt lại cặp thành viên/địa điểm **ghi đè** một phiếu, không tăng bộ đếm. `liked` phải là boolean thật, không nhận chuỗi `"false"`. ID thành viên không thuộc nhóm → 403; điểm không nằm trong deck hợp lệ hiện tại → 422. Thay đổi lựa chọn làm lịch nháp cũ (nếu có từ B4 sau này) thành `stale`.

Hoàn tác: `DELETE /api/groups/{code}/swipes` với body `{member_id, place_id}`. Trả `{place_id, removed: true|false}`; xóa lại trả `false`, không lỗi. UI giữ lịch sử lượt quẹt trong phiên để chọn thẻ cần hoàn tác.

## 9. Tiến độ — `GET /api/groups/{code}/progress`

```json
{
  "code": "HN7K2Q", "status": "swiping",
  "deck_ready": true, "deck_source": "provisional_rating", "total_cards": 20,
  "member_count": 2, "finished_count": 0, "all_finished": false,
  "budget_per_person": 500000,
  "members": [
    {"nickname": "Trưởng nhóm demo", "is_leader": true, "swiped_count": 1, "remaining": 19, "finished": false},
    {"nickname": "Thành viên demo", "is_leader": false, "swiped_count": 0, "remaining": 20, "finished": false}
  ]
}
```

UI có thể polling mỗi 3 giây. Chưa tạo deck thì `deck_ready: false`, tổng thẻ 0 và `all_finished: false`; bộ thẻ rỗng cũng không coi mọi người đã hoàn thành. Chưa gộp điểm/vote thành lịch vì thuộc B4.

## 9b. Hợp đồng B4 — lịch trình nhóm (CHƯA LÀM, giao diện đã code theo đúng hợp đồng này)

Giao diện (`app/static/itinerary-api.js`, `itinerary.js`, `dashboard.js`) gọi 3 endpoint dưới. Khi endpoint trả 404 với `detail` đúng là `"Not Found"` (route chưa có) hoặc 405, giao diện tự dùng dữ liệu mẫu; mọi 404 khác phải có `detail` tiếng Việt để giao diện hiện lỗi thật.

**Lõi đã có:** `codebase/group.py` · `plan_group(cfg, scores, pinned) -> {"items", "dropped", "violations"}` (Hải, A3). `cfg` lấy từ `app.catalogue.planning_config(config, member_count)`.

### `POST /api/groups/{code}/itinerary` — trưởng nhóm xếp lịch

Request: `{"member_id": "…", "pinned": ["hn_09", "hn_76"]}`

1. 403 nếu không phải trưởng nhóm; 409 nếu nhóm đã có lịch `approved`.
2. Điểm mỗi địa điểm = trung bình phiếu (thích = 1, bỏ qua = 0) của những người đã quẹt thẻ đó; chỉ giữ điểm ≥ 0,5 và có ≥ 1 phiếu; điểm ghim luôn giữ.
3. `plan_group(cfg, scores, pinned)` → lưu bảng `itineraries` (`status = draft`), các bản `draft` cũ chuyển `stale`.

Response 201 (giao diện đọc đúng các khoá này):

```json
{
  "id": "it_…", "version": 2, "status": "draft", "created_at": "2026-12-05T08:00:00+07:00",
  "items": [{"id": "hn_09", "name": "Văn Miếu - Quốc Tử Giám", "arrive": "08:15", "leave": "09:45",
             "travel_min": 15, "no_hours": false, "meal": null}],
  "dropped": [{"id": "hn_04", "name": "Lăng Chủ tịch Hồ Chí Minh", "reason": "đóng cửa Thứ Hai — đổi sang ngày khác hoặc bỏ điểm"}],
  "violations": [],
  "cost_per_person": 155000,
  "votes": [{"place_id": "hn_09", "likes": 2, "swiped": 3, "like_score": 0.67}]
}
```

- `dropped[].reason`: phần sau `" — "` là gợi ý, giao diện tách ra dòng "Gợi ý".
- `cost_per_person`: tổng `price_max_vnd` (giá vé theo người) của các điểm có giá trong lịch, so với `budget_per_person` của nhóm (PRD TS-06); `null` nếu không điểm nào có giá.
- `violations` luôn `[]` khi trả 201; nếu khác rỗng là lỗi, trả 500 kèm danh sách.

### `PATCH /api/itineraries/{id}` — duyệt / bỏ / ghim

Request: `{"member_id": "…", "action": "approve" | "drop" | "pin", "place_id": "hn_09"}` (`place_id` bỏ trống khi `approve`).
- `approve` → bản đó thành `approved`, trả lại bản đó.
- `drop` / `pin` → xếp lại với điểm đó bị loại / ghim thêm → bản mới (`version + 1`, `draft`), bản cũ `stale`; trả bản mới (cùng dạng response ở trên).
- 403 không phải trưởng nhóm · 409 bản đã `stale` / nhóm đã duyệt · 422 ghim điểm đóng vào ngày đi (`detail` nêu lý do).

### `GET /api/groups/{code}/itinerary` — lịch mới nhất cho mọi thành viên

Trả bản `approved` nếu có, không thì bản `draft` mới nhất (cùng dạng response). Chưa có lịch → 404 `{"detail": "Nhóm chưa có lịch."}` (không dùng `"Not Found"`).

## 10. Database, chạy lại và giới hạn

- Bảy bảng: `places`, `travel_times`, `groups`, `members`, `deck_cards`, `swipes`, `itineraries`. Nạp lại nguồn bằng upsert lúc startup, không nhân đôi POI/tuyến hay xóa nhóm/phiếu.
- Giao dịch khóa dòng nhóm khi vào nhóm/tạo deck/quẹt để chống đua đồng thời; ràng buộc DB bảo vệ biệt danh, một trưởng nhóm và duy nhất một phiếu/thành viên/điểm.
- `/health` kiểm được DB và trả số POI/tuyến. Không lộ DSN trong lỗi 503.
- Chỉ B1–B3 đã triển khai; trang tạo nhóm/quẹt, API itinerary và AI chọn thẻ A3 còn chờ phần việc tương ứng. CLI/eval hiện có giữ nguyên.
- Nguồn kỹ thuật đã tham khảo: [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/), [Psycopg transaction](https://www.psycopg.org/psycopg3/docs/basic/transactions.html), [Compose startup và healthcheck](https://docs.docker.com/compose/how-tos/startup-order/).
