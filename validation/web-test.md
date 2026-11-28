# D7 — Kiểm thử luồng web TripSwipe

> Người làm: Hùng (BA / tester), chạy bằng Claude Code. Hạn 14:10 Thứ Bảy 28/11. Không sửa code; chỉ ghi kết quả và báo lỗi cho Bảo / Minh.

**Môi trường:** `main` tại `d8d431d` (commit gộp PR #13) · Docker Desktop · `docker compose up --build -d` · web `http://localhost:9000` · Postgres 16 trong container · chạy lúc 12:40 28/11/2026 · **không có `.env`**, nên bộ thẻ là `source: provisional_rating` (xếp theo rating trong dữ liệu, **chưa gọi AI chọn thẻ**).

**Cách kiểm:** script [`validation/web_test.py`](web_test.py) gọi API thật theo `docs/api-examples.md` và PRD (TS-01 → TS-07), cộng 7 trang giao diện. Thêm một lượt mở 7 trang bằng Edge không đầu (headless) để xem lỗi console. Chạy lại: `docker compose up --build -d` rồi `python validation/web_test.py`.

## Kết quả: 40/40 kiểm tra API đạt, 0 lỗi console

| Bước | Kiểm | Kết quả |
|---|---|---|
| TS-01 tạo nhóm | Tạo hợp lệ → 201, mã 6 ký tự · thiếu ngày đi → 422 · giờ kết thúc ≤ bắt đầu → 422 · thành phố ngoài Hà Nội → 422 | Đạt |
| TS-02 vào nhóm | Vào bằng biệt danh → 201 · biệt danh trùng (khác hoa/thường, thừa khoảng trắng) → 409 · mã sai → 404 · mã không phân biệt hoa/thường | Đạt |
| TS-03 bộ thẻ | Trưởng nhóm tạo, GET trả 20 thẻ · thành viên tạo → 403 · GET lại dùng bộ thẻ cũ | Đạt |
| TS-04 quẹt | Thích 1 thẻ · `liked` là chuỗi `"false"` → 422 · `member_id` lạ → 403 · `place_id` lạ → 422 · hoàn tác · hoàn tác lần 2 không lỗi (`removed: false`) | Đạt |
| TS-05 tiến độ | `GET /progress` sau khi 3 người quẹt thích 6 thẻ | Đạt |
| TS-06 xếp lịch | Thành viên xếp → 403 · trưởng nhóm xếp → 201, 4 điểm, `violations` rỗng, giờ không chồng và nằm trong 08:00–17:00 | Đạt |
| TS-07 duyệt | Thành viên duyệt → 403 · bỏ 1 điểm → bản `version + 1`, điểm biến mất · duyệt bản cũ (stale) → 409 · duyệt bản mới → `approved` · mọi người xem được · lịch đã duyệt thì vào nhóm / xếp lại → 409 | Đạt |
| Giao diện | `/`, `/create`, `/join`, `/g/{mã}/swipe`, `/lobby`, `/itinerary`, `/dashboard` đều 200, tiêu đề đúng, **0 lỗi console / pageerror** (Edge headless) | Đạt |

## Điều quan sát (chưa phải lỗi chặn, cần Bảo / Minh xem)

1. **Không thẻ nào đủ phiếu:** xếp lịch cho nhóm chưa ai quẹt trả **201 với `items: []`, `dropped: []`** và không có trường nào giải thích. API đúng hợp đồng (không 500, `violations: []`), nhưng người dùng có thể thấy một lịch trống không rõ vì sao. **Chưa xem giao diện hiển thị ra sao** — Bảo kiểm màn Lịch trình lúc lịch rỗng, và có nên báo "chưa đủ phiếu" không.
2. **Ghim điểm đóng cửa qua `POST /itinerary`:** ghim Lăng Bác vào ngày thứ Hai trả **201**, điểm nằm trong `dropped` (lý do đóng cửa), không có trong `items`. An toàn (không xếp điểm đóng cửa) nhưng khác hợp đồng `PATCH pin` (422). Hai đường hành xử khác nhau — chỉ cần biết để demo đúng.
3. **Bộ thẻ chưa qua AI** trong lượt này vì không có `.env`: kiểm thử chưa chạm `build_deck` có model thật.

## Chưa kiểm (khai thật)

- Luồng 2 trình duyệt có bấm chuột (quẹt kéo, nút "Xếp lịch", ghim trên giao diện): đã qua tay Bảo (`TASKS.md` U5), tôi **chưa tự bấm**; mới kiểm ở tầng API + tải trang.
- Giao diện điện thoại, chế độ AI chọn thẻ, bản đồ OSRM, kiểm tra hiển thị tiếng Việt, tốc độ xếp lịch (< 2 giây theo PRD).
- Check "nhóm chưa có lịch → 404" của script **không có giá trị**: nhóm thử đó đã có bản nháp rỗng từ lần xếp lịch ở mục 1, nên trả 200. Chưa kiểm được 404 riêng.

## Dọn dẹp

Chạy xong dùng `docker compose down` (không `-v`); dữ liệu nhóm thử còn trong volume `postgres-data` trên máy này.
