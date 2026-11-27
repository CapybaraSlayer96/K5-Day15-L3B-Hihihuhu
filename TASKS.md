# TASKS — CP2 (19:30 Thứ Sáu 27/11)

> Tự nhận việc: điền tên mình vào cột **Người nhận**, commit, push. Mỗi việc một người.
> Xong thì đổi cột **Trạng thái** thành `xong` kèm link file / commit.
> Mỗi người phải giải thích được phần có tên mình (luật chung).

## BA

| # | Việc | File | Hạn | Người nhận | Trạng thái |
|---|---|---|---|---|---|
| BA1 | Soạn và gửi khảo sát online cho 25 người ngoài nhóm; tổng hợp kết quả, rút trích dẫn nguyên văn (bỏ tên) | `evidence/survey/`, `evidence/summary.md` | gửi trước 17:30 · số đầu tiên 19:15 | Hùng | xong |
| BA2 | Đào review công khai (Google Maps, Tripadvisor, group du lịch Hà Nội): ghi cách chọn mẫu, cách đếm trước khi đọc; x/N, %, ≥5 ví dụ | `evidence/data-mining.md` | 19:00 | Minh, Hải | xong |
| BA3 | Kiểm giờ mở cửa, ngày đóng cửa các địa điểm Hà Nội từ nguồn chính thức, ghi nguồn; viết DATA_CARD bản đầu | `data/DATA_CARD.md` | 18:30 | Minh, Hải | xong |
| BA4 | Viết `spec.md` §0–§3 và §5 (4 lớp chỗ khó, ≥6 kịch bản, 2 tấn công) | `spec.md` | 19:00 | Bảo | xong |
| BA5 | Cập nhật canvas (số bằng chứng đầu, dòng "Đã đổi gì so với CP1"); điền chuẩn "đạt" đã chốt vào `spec.md` §7; nộp CP2 | `canvas.md`, `spec.md` §7 | 19:30 | Hùng | xong |
| BA6 | Chạy tay 10–20 yêu cầu lịch trình qua ChatGPT / Claude, ghi lỗi thấy được (dùng được / sửa được / không chấp nhận) | `eval/README.md` | 18:00 | Bảo | xong |
| BA7 | Viết ≥3 metric từ lỗi ở BA6: định nghĩa kiểm chứng được · cách chấm · ngưỡng | `eval/metric_spec.yaml` | 18:30 | Bảo | xong |
| BA8 | Viết ≥10 câu thử (có `kho`, `tu_choi`), ≥1/3 câu `source` là `nguoi_dung:` hoặc `data_that:` | `eval/benchmark.csv` | 19:00 | Bảo | xong |
| BA9 | Chấm thử độc lập 5 output theo metric (người khác người làm BA7); lệch ≥2/5 → báo viết lại metric | — | 19:00 | Bảo | xong: khớp 5/5 (người chấm 2 là agent độc lập) |

## Engineer

| # | Việc | File | Hạn | Người nhận | Trạng thái |
|---|---|---|---|---|---|
| EN1 | Sơ đồ kiến trúc, bảng công cụ, mức tự động, chỗ chặn rủi ro, chỗ người duyệt | `spec.md` §4 | 18:30 | Bảo | xong: spec §4 đồng bộ code |
| EN2 | Công cụ trả dữ liệu giả (`tra_dia_diem`, `tra_gio_mo_cua`, `uoc_thoi_gian_di`, `kiem_lich_trinh`) + luồng chính chạy hết với AI giả | `codebase/tools.py`, `codebase/agent.py` | 19:15 | Bảo | xong: 4 công cụ + luồng chính, 16 câu chạy hết với AI giả |
| EN3 | Lấy API key, nối model, gọi thử được 1 câu (`python run.py eval --try`) | `.env` (không commit), `codebase/ai.py` | trước khi rời lớp | Bảo | code Gemini xong; chờ API key để chạy eval --try |
| EN4 | Dựng dữ liệu Hà Nội ~20–30 địa điểm (giờ mở cửa, ngày đóng cửa, toạ độ) từ kết quả BA3 | `data/` | 18:45 | Hải | xong |
| EN5 | Chạy `python run.py check` và `python run.py` sạch trước khi nộp | — | 19:15 | Bảo | xong: check + run sạch, tests/test_core.py ok |

## Phụ thuộc

- BA3 → EN4 (giờ mở cửa đã kiểm) · BA1, BA2 → BA8 (trích dẫn làm câu thử) · BA6 → BA7 → BA9 · EN1 → EN2 (tên công cụ khớp `tools.py`).
- **19:00:** cả nhóm chốt chuẩn "đạt" (§7). Sau CP2 không sửa.
- Nhận việc xong: cập nhật cột "Phần việc chính" trong `TEAMS.md` cho khớp.

---

# TASKS — CP3 (10:00) → CP4 (14:30) → hạn chót (23:59) · Thứ Bảy 28/11

> Vai: **Bảo** UI · **Minh** BE · **Hải** AI · **Hùng** BA / tester / tài liệu.
> Thiết kế: `docs/PRD.md` (TS-01…TS-08), `docs/ARCHITECTURE.md`. Ticket chi tiết (local): `.scratch/tripswipe/issues/`.
> Cách dùng: làm theo thứ tự mã trong cột của mình; việc có "Chờ" thì chỉ bắt đầu khi việc kia xong. Xong việc: sửa dòng **Trạng thái** của việc đó thành `xong · <commit>` rồi push.

## Bảng tổng hợp

Chi tiết từng việc (các bước, yêu cầu output) ở mục 4. Song song: các việc cùng giờ, cột "Chờ" trống thì làm ngay.

### Checkpoint 3 · hạn 10:00 hôm nay (28/11)

| Mã | Việc | Người | Chờ | Hạn | Deliverable | DoD | Trạng thái |
|---|---|---|---|---|---|---|---|
| A1 | Chấm cột `pass` lượt 2 + `score`, ghi kết quả vào spec §7 và eval/README mục 5 | Bảo | — | 09:45 | `eval/run-2.csv` đã chấm | Không còn ô `pass` trống; số khớp `score` | xong · 20/22 (91%) |
| U1 | Video 30 giây CLI gọi AI thật (1 câu thường + 1 câu khó) | Bảo | — | 09:45 | link video (ẩn danh mở được) | token > 0 trên màn hình; ≤ 30 giây | |
| B1 | Khung FastAPI + Postgres 7 bảng, nạp dữ liệu lúc khởi động | Minh | — | 10:00 (kéo sang CP4) | `app/` | Khởi động lại không nạp trùng; eval vẫn chạy không cần DB | |
| B2 | Docker compose (`db`, `app`, cổng 8000) | Minh | — | 10:00 (kéo sang CP4) | `Dockerfile`, `docker-compose.yml` | `docker compose up` → mở được localhost:8000 | |
| A2 | Thử mô phỏng chi phí 10 phiên | Hải | — | 09:50 | `cost/simulate-try.csv` (không commit) | token > 0 | |
| A3 | `build_deck` + `plan_group` theo hợp đồng mục 2 | Hải | — | 10:30 (kéo sang CP4) | `codebase/` + assert trong `tests/test_core.py` | Bộ thẻ không có điểm đóng vào ngày đi; lịch luôn 0 vi phạm | |
| D1 | `evidence/summary.md` + kết quả khảo sát đã bỏ cột nhận diện | Hùng → Bảo làm | — | 09:30 | `evidence/summary.md`, `evidence/survey/` | ≥ 20 phản hồi đúng vai; x/N, %; ≥ 5 trích nguyên văn; kết luận giả thuyết | xong · 31 người, 23/31 (74%) |
| D2 | `spec.md` §1 (số khảo sát), §2 (impact có nguồn), §6 (bốn đường đi) | Hùng → Bảo làm | — | 09:45 | `spec.md` | §0–§7 không còn ô trống | xong |
| D3 | Tự soát guide 3.4 + nộp form CP3 | Hùng | D1, D2, U1, A1 | 10:00 | form CP3 | Nộp đúng hạn, khai thật phần chưa xong (web) | |

### Checkpoint 4 · hạn 14:30 hôm nay (28/11)

| Mã | Việc | Người | Chờ | Hạn | Deliverable | DoD | Trạng thái |
|---|---|---|---|---|---|---|---|
| U2 | Trang Tạo nhóm (wizard 7 bước) + Vào nhóm | Bảo | — (JSON mẫu) | 11:00 | `app/templates/create.html`, `join.html`, `app/static/` | Đúng TS-01, TS-02; chặn thiếu ngày đi | |
| U3 | Trang Quẹt 2 lớp (tổng quan / vuốt lên chi tiết), kéo + nút, hoàn tác | Bảo | — (JSON mẫu) | 12:00 | `swipe.html`, `swipe.js` | Đúng TS-04 | |
| U4 | Phòng chờ + Lịch trình (dòng thời gian, Leaflet, điểm bị bỏ, duyệt / bỏ / ghim, sao chép) | Bảo | — (JSON mẫu) | 13:00 | `lobby.html`, `itinerary.html` | Đúng TS-05–TS-07; mọi số lấy từ API | |
| U5 | Nối UI với API thật | Bảo | B3, B4 | 13:45 | commit nối API | 2 trình duyệt đi trọn luồng, không lỗi console | |
| U6 | Video demo dự phòng bằng web | Bảo | U5 | 14:20 | link video | 1 trường hợp thường + 1 khó; mở được ẩn danh | |
| B3 | API nhóm, bộ thẻ, quẹt, tiến độ, chi tiết địa điểm + JSON mẫu | Minh | B1 | 11:30 (JSON mẫu 10:30) | `app/`, `docs/api-examples.md` | 409 biệt danh trùng, 422 thiếu ngày, quẹt lại ghi đè | |
| B4 | Gộp phiếu (trung bình ≥ 0,5) + `POST` itinerary + `PATCH` (duyệt / bỏ / ghim, bản cũ `stale`) | Minh | A3 | 13:00 | `app/` | Lịch luôn `violations: []`; 403 nếu không phải trưởng nhóm | |
| B5 | Test end-to-end qua HTTP | Minh | B4 | 13:30 | `tests/test_api.py` | In ok; `tests/test_core.py` vẫn ok | |
| A4 | Lượt cải tiến: gom nhóm lỗi → một cải tiến → eval trọn bộ → chấm → `score` | Hải | A1 | 12:30 | `eval/run-3.csv` đã chấm | Chạy đủ 22 câu (+ câu mới chỉ thêm); ghi cấu hình đổi gì | |
| A5 | `eval/report.md` + `eval/README.md` | Hải | A4 | 13:30 | 2 file | % từng lượt so với chuẩn; ≥ 3 lỗi (input · output · vì sao sai · đã sửa · còn lại) | |
| A6 | Mô phỏng ≥ 50 phiên + `cost/cost-estimate.md` | Hải | A4 | 14:00 | `cost/simulate-N.csv`, `-summary.md`, `cost-estimate.md`, `traces/simulate-N.jsonl` | Chi phí / task thành công; 3 kịch bản; ≥ 2 model; kết luận so với impact | |
| D4 | Kiểm thử CLI 5 câu lạ | Hùng | — | 11:00 | `validation/cli-test.md` | Mỗi câu: input · output · đúng / sai · vì sao | |
| D5 | *(Bonus)* 2–3 người ngoài nhóm dùng thử, 5 nhịp | Hùng | có bản chạy | 13:30 | `validation/log.md` | Đủ cột mỗi người + 4 dòng tổng hợp | |
| D6 | `spec.md` §8 §9 + slide 8 trang | Hùng | A5, A6 | 14:15 | `spec.md`, `slides/demo-slides.pdf` | Mỗi trang slide ≥ 1 số có nguồn, khớp repo | |
| D7 | Kiểm thử luồng web + corner case PRD | Hùng | U5, B5 | 14:10 | `validation/web-test.md` | Không còn lỗi chặn luồng demo | |
| X1 | README hoàn thiện: mục "Chạy web" (`docker compose up`), link video ở bảng "Bảy hạng mục" dòng 7, cập nhật bảng "Phần nào thật / giả" khi web xong | Hùng | U6, B2 | 14:20 | `README.md` | Người ngoài làm theo README chạy được CLI + web; không còn `____` | |
| X2 | `docs/ai-usage.md`: mỗi người thêm dòng phần mình dùng AI (công cụ · AI làm gì · mình kiểm gì) | Cả nhóm | — | 14:20 | `docs/ai-usage.md` | Mỗi người ≥ 1 dòng; giải thích được phần có tên mình | |
| X3 | `spec.md` §10: mỗi thay đổi sau CP2 thêm 1 dòng (giờ · đổi gì · vì sao trỏ câu thử / lỗi) | Người đổi | — | liên tục | `spec.md` §10 | Không có thay đổi nào sau CP2 thiếu dòng | |
| X4 | `docs/ARCHITECTURE.md` đồng bộ code thật (công cụ, thuật toán, ma trận, app) | Minh | B4 | 14:20 | `docs/ARCHITECTURE.md` | Không mô tả thứ code không có | |
| D8 | Tự soát guide 4.4 + nộp form CP4 | Hùng | tất cả CP4 | 14:30 | form CP4 | Đủ 7 hạng mục; lượt 1 → cải tiến; chi phí / task; slide; video; phần chưa xong | |

### Sau CP4 · demo 14:30–18:00 · hạn chót 23:59 hôm nay (28/11)

| Mã | Việc | Người | Chờ | Hạn | Deliverable | DoD | Trạng thái |
|---|---|---|---|---|---|---|---|
| F1 | Demo Zone (14:30–16:00), Demo Phòng nếu vào top (16:00–18:00): Hùng — pain + impact · Bảo — demo web (1 thường + 1 khó) · Minh — kiến trúc + bộ kiểm lịch · Hải — đánh giá + chi phí; chạy câu thử lạ giám khảo đưa, mở trace 1 câu trượt; mạng hỏng thì chiếu video dự phòng | Cả nhóm | D8 | 18:00 | buổi demo | Mỗi người nói ≥ 1 phần; ai cũng trả lời được 4 câu guide 5.2 (vì sao chọn hình dạng này · lỗi nguy hiểm nhất · chi phí / task thành công tính thế nào · phần mình làm) | |
| F2 | Sửa theo góp ý demo; mỗi thay đổi 1 dòng `spec.md` §10 "Sau CP4" (giờ · đổi gì · vì sao); chạy thêm thì thành lượt mới (`run-N` tiếp theo) | Người sở hữu phần bị góp ý | F1 | 23:00 | commit + dòng §10 | Không sửa chuẩn "đạt", câu thử đã có, số bằng chứng, kết quả các lượt đã chạy | |
| F3 | Reflection: mỗi người 1 file `reflection/<ten-khong-dau>.md` theo `reflection/TEMPLATE.md` (vai + phần mình làm trỏ file / commit · AI hỗ trợ thế nào · một bài học từ một câu thử trượt của nhóm) | Bảo, Minh, Hải, Hùng | — | 23:30 | 4 file `reflection/doan-xuan-duy-bao.md`, `nguyen-dinh-minh.md`, `nguyen-dinh-vu-hai.md`, `vu-tien-hung.md` | Đủ 4 file, mỗi file đủ 3 ý | |
| F4 | Checklist cuối guide 5.2: repo đủ thư mục bắt buộc · không có API key / dữ liệu cá nhân thật · video mở được bằng cửa sổ ẩn danh · `TEAMS.md` khớp vai · README không còn `____` · `python run.py check` sạch · commit cuối trước 23:59 | Hùng | F2, F3 | 23:45 | checklist tích đủ (ghi vào `TASKS.md`) | Mọi mục tích; commit cuối đã push trước 23:59 | |

## 0. Luật chung cho mọi việc

- Không sửa chuẩn "đạt" (`spec.md` §7), không sửa / xoá câu thử đã có, không sửa `expected` cho khớp output. Câu thử chỉ được **thêm**.
- Không sửa tay `eval/run-*.csv`, `cost/simulate-*.csv`, `traces/*` — chỉ điền cột `pass`, `ghi_chu`. Lượt lỗi kỹ thuật → chạy lại thành lượt mới.
- Không commit file chứa API key, dữ liệu cá nhân thật, bản khảo sát còn tên / email / SĐT.
- Mọi con số trong tài liệu phải trỏ được về file / nguồn; không có nguồn ghi *(tự ước tính)*.
- Branch, commit theo `CONVENTIONS.md`. `python run.py check` sạch trước mỗi lần push vào `main`.
- Sau 14:30: mọi thay đổi ghi `spec.md` §10 (giờ · đổi gì · vì sao).

## 1. Hiện trạng (sáng 28/11)

- Lõi chạy thật trong `codebase/`: `answer(text)` + 4 công cụ + bộ xếp lịch + bộ kiểm lịch; model gpt-4.1-mini qua proxy (`MODEL_PROVIDER=openai`).
- Bộ câu thử 22 câu (thuong 6 · kho 12 · tu_choi 4).
- **Lượt 1** `run-1@20261128-011133`: 13/22 (59%), 8 câu lỗi timeout proxy (đã chấm).
- **Lượt 2** `run-2@20261128-015044`: chạy lại sau sửa timeout, 22/22 câu không lỗi — **20/22 (91%), đạt chuẩn**. Trượt: B03 (thời lượng dữ liệu), B19 (model không rút được Chùa Trấn Quốc).
- Chưa có: web (`app/`), docker, evidence/summary, §6 §8 §9, report, cost, slide, video, reflection.

## 2. Hợp đồng để 4 người làm song song

Ba "mặt tiếp giáp" chốt trước, mỗi bên làm theo hợp đồng, không chờ nhau:

| Mặt tiếp giáp | Bên cung cấp | Bên dùng | Hợp đồng |
|---|---|---|---|
| Hàm lõi cho web | Hải | Minh | `build_deck(cfg) -> [{"id", "rank", "reason"}]` (20 thẻ) · `plan_group(cfg, scores: {id: float}, pinned: [id]) -> {"items": [{id, name, arrive, leave, travel_min, no_hours}], "dropped": [{id, name, reason}], "violations": []}` · `cfg = {date, start_min, end_min, start_xy, start_id, mode, budget_per_person}`. Đặt trong `codebase/`, dùng lại `planner.plan`, `planner.check`. |
| HTTP API | Minh | Bảo | 10 endpoint ở PRD mục Technical Requirements; JSON mẫu mỗi endpoint ghi vào `docs/api-examples.md` **trước 10:30** để Bảo dựng UI trên dữ liệu mẫu. |
| Số liệu cho tài liệu | Hải | Hùng | Run ID + % đạt mỗi lượt (`eval/README.md` mục 5), chi phí / task thành công + 3 kịch bản (`cost/cost-estimate.md`). Hùng chép vào spec / slide, không tự tính lại. |

## 3. Thứ tự và phần chạy song song

```
Giờ      Bảo (UI)              Minh (BE)                 Hải (AI)                     Hùng (BA / test / docs)
08:30 ─ U1 video CP3 (CLI) ─┐  B1 khung FastAPI+DB ─┐    (A1 → Bảo, đã xong)     ┐    D1 evidence/summary ─┐
09:45 ─ U2 Tạo nhóm/Vào nhóm  │  B2 docker compose     │    A2 simulate --try        │    D2 spec §1 §2 §6      │
10:00 ════════════════ CP3 (Hùng nộp: D3) ════════════════════════════════════════════════════════════════
10:00 ─ U3 trang Quẹt         │  B3 API nhóm/thẻ/quẹt  │    A3 build_deck + plan_group│    D4 kiểm thử CLI lạ    │
12:00 ─ U4 Phòng chờ+Lịch trình  B4 gộp phiếu, itinerary  A4 lượt cải tiến (run-3)  │    D5 người dùng thử     │
13:30 ─ U5 nối UI ↔ API thật   B5 test e2e HTTP        A5 report + eval README      │    D6 spec §8 §9, slide  │
14:00 ─ U6 video demo web      (hỗ trợ U5)              A6 cost simulate + estimate  │    D7 test luồng web     │
14:30 ════════════════ CP4 (Hùng nộp: D8) ════════════════════════════════════════════════════════════════
14:30–18:00 demo (F1) · sau 18:00: F2 sửa theo góp ý · F3 reflection · 23:45 F4 checklist cuối
```

- **Song song hoàn toàn từ 08:30:** U1/U2 · B1/B2 · A1/A2 · D1/D2 — không ai chờ ai.
- **Phụ thuộc cứng:** U5 chờ B3, B4 · B4 chờ A3 · A5 chờ A4 · A6 chờ A4 (lấy tỉ lệ đạt lượt cải tiến) · D6 chờ A5, A6 · D7 chờ U5, B5 · D8 chờ tất cả việc CP4.

## 4. Việc chi tiết

### Bảo · UI

**U1 · Video CP3 30 giây** — Trạng thái:
- Làm: sửa file cấu hình môi trường thành `MODEL_PROVIDER=openai`, `MODEL_NAME=gpt-4.1-mini` → `python run.py` → gõ 1 câu thường (B01) và 1 câu khó (Lăng Bác thứ Hai) → quay màn hình.
- Deliverable: link video (YouTube "Không công khai" hoặc Drive "Bất kỳ ai có link") gửi Hùng; ghi link vào `README.md` mục "Bảy hạng mục" dòng 7.
- DoD: mở được bằng cửa sổ ẩn danh; thấy dòng `(model: gpt-4.1-mini · token vào … / ra …)` với token > 0; thấy câu khó bị loại đúng lý do.
- Yêu cầu output: ≤ 30 giây, thao tác thật, AI trả kết quả thật (README CP3). Không lộ key trên màn hình.

**U2 · Trang Tạo nhóm + Vào nhóm (TS-01, TS-02)** — Chờ: không (dùng JSON mẫu) — Trạng thái:
- Làm: wizard 7 bước (tỉnh — chỉ Hà Nội bật, tỉnh khác "sắp có"; phạm vi — chỉ nội thành; ngày đi; giờ bắt đầu / kết thúc; điểm xuất phát chọn từ danh sách; budget cả nhóm; phương tiện) → màn mã + link nhóm. Trang vào nhóm: nhập biệt danh, lưu `member_id` trong trình duyệt.
- Deliverable: `app/templates/create.html`, `join.html`, `app/static/*.js|css`.
- DoD: không qua được bước ngày đi khi trống; giờ kết thúc > giờ bắt đầu; tiếng Việt; vừa màn hình máy tính 1366×768.
- Yêu cầu output: đúng acceptance criteria TS-01, TS-02 trong PRD.

**U3 · Trang Quẹt 2 lớp (TS-04)** — Chờ: không (JSON mẫu) — Trạng thái:
- Làm: thẻ tổng quan (ảnh, tên, loại, quận, `card_hook`, tag, khoảng giá, rating, "mở / đóng vào ngày đi", lý do AI) · vuốt lên / bấm "Chi tiết" → lớp chi tiết (mô tả, `why_visit`, `what_to_do`, giờ cả tuần, ngày đóng, thời lượng, `tips`, review, địa chỉ, link bản đồ, nguồn xác minh) · kéo phải = thích, trái = bỏ qua (pointer events) + 2 nút · hoàn tác · đếm thẻ còn lại.
- Deliverable: `app/templates/swipe.html`, `app/static/swipe.js`.
- DoD: quẹt được bằng chuột và bằng nút; hoàn tác xoá lượt vừa rồi; ảnh lỗi không vỡ bố cục; thẻ thiếu giờ có nhãn "chưa có dữ liệu giờ".
- Yêu cầu output: đúng TS-04; không gọi API bản đồ ngoài.

**U4 · Phòng chờ + Lịch trình (TS-05, TS-06, TS-07)** — Chờ: không (JSON mẫu) — Trạng thái:
- Làm: phòng chờ (danh sách thành viên, ai xong, polling 3 giây; nút "Xếp lịch" chỉ hiện với trưởng nhóm; ghim điểm) · lịch trình (dòng thời gian giờ đến / rời / phút đi "ước tính"; bản đồ Leaflet nền OpenStreetMap có đường nối theo thứ tự; danh sách điểm bị bỏ + lý do + gợi ý; nút bỏ / ghim / duyệt; nút sao chép văn bản).
- Deliverable: `app/templates/lobby.html`, `itinerary.html`, `app/static/*.js`.
- DoD: bản đồ hiện đúng thứ tự điểm; bản cũ hiện nhãn "hết hiệu lực" sau khi sửa; văn bản sao chép có giờ, tên, nguồn giờ mở cửa, câu "thời gian đi là ước tính".
- Yêu cầu output: không hiển thị con số nào không đến từ API.

**U5 · Nối UI với API thật** — Chờ: B3, B4 — Trạng thái:
- Làm: thay JSON mẫu bằng gọi API; xử lý lỗi (mã nhóm sai, AI lỗi → thông báo + nút thử lại).
- Deliverable: commit nối API.
- DoD: `docker compose up` → đi trọn luồng 2 trình duyệt (2 thành viên) từ tạo nhóm đến duyệt lịch không lỗi console.

**U6 · Video demo dự phòng bằng web** — Chờ: U5 — Trạng thái:
- Deliverable: link video ~2 phút gửi Hùng (cho form CP4).
- DoD: có 1 trường hợp thường + 1 trường hợp khó (điểm đóng cửa bị loại có lý do); mở được ẩn danh.

### Minh · BE

**B1 · Khung FastAPI + Postgres** — Chờ: không — Trạng thái:
- Làm: `app/main.py` (FastAPI, phục vụ template + static), `app/db.py`; 7 bảng theo PRD (`places`, `travel_times`, `groups`, `members`, `deck_cards`, `swipes UNIQUE(member_id, place_id)`, `itineraries status draft|approved|stale`); lúc khởi động tự tạo bảng và nạp `data/hanoi_places.json` + `data/travel_times.json`.
- Deliverable: `app/`, `requirements.txt` (fastapi, uvicorn, psycopg / psycopg2, jinja2).
- DoD: khởi động lại không nạp trùng; `SELECT count(*) FROM places` = số dòng JSON.
- Yêu cầu output: lõi `codebase/` vẫn chạy **không cần Postgres** (`python run.py eval` không đổi).

**B2 · Docker compose** — Chờ: không — Trạng thái:
- Làm: `Dockerfile` (Python 3.12), `docker-compose.yml` (`db` postgres:16 có volume, `app` cổng 8000, đọc file cấu hình môi trường), thêm mục "Chạy web" vào `README.md`.
- DoD: máy sạch chạy `docker compose up` → mở `http://localhost:8000` được; key không nằm trong image hay compose.

**B3 · API nhóm, bộ thẻ, quẹt** — Chờ: B1 (gọi `build_deck` của Hải; khi A3 chưa xong dùng tạm 20 điểm rating cao nhất đã lọc) — Trạng thái:
- Làm: `GET /api/config/options` · `POST /api/groups` · `GET /api/groups/{code}` · `POST /api/groups/{code}/members` · `POST|GET /api/groups/{code}/deck` · `POST /api/groups/{code}/swipes` · `GET /api/groups/{code}/progress` · `GET /api/places/{id}`. Ghi JSON mẫu từng endpoint vào `docs/api-examples.md` trước 10:30.
- DoD: mã nhóm 6 ký tự duy nhất; biệt danh trùng trả 409; thiếu ngày đi trả 422; quẹt lại ghi đè phiếu cũ.

**B4 · Gộp phiếu + lịch trình** — Chờ: A3 — Trạng thái:
- Làm: `POST /api/groups/{code}/itinerary` (chỉ trưởng nhóm; điểm = trung bình phiếu của người đã quẹt thẻ đó, lấy ≥ 0,5 và ≥ 1 phiếu, hoà theo rating, cộng điểm ghim → `plan_group`) · `PATCH /api/itineraries/{id}` (`approve` / `drop` / `pin` → tính lại, bản cũ `stale`).
- DoD: lịch trả về luôn có `violations: []`; người không phải trưởng nhóm gọi → 403; ghim điểm đóng vào ngày đi → báo lỗi có lý do.

**B5 · Test end-to-end qua HTTP** — Chờ: B4 — Trạng thái:
- Làm: `tests/test_api.py` dùng test client: tạo nhóm → 2 thành viên vào → quẹt → xếp lịch → kiểm 0 vi phạm, chi phí mỗi người ≤ budget mỗi người; model chế độ giả.
- DoD: `python tests/test_api.py` (hoặc pytest) in ok; `tests/test_core.py` vẫn ok.

### Hải · AI

**A1 · Chấm lượt 2** (người làm: **Bảo**) — Chờ: không — Trạng thái: xong · 20/22 (91%), `run-2@20261128-015044`
- Làm: mở `eval/run-2.csv`, điền `pass` (1 / 0) theo `pass_criterion` + `eval/metric_spec.yaml`, ghi lý do câu trượt vào `ghi_chu` → `python run.py score eval/run-2.csv` → chép run ID + % vào `spec.md` §7 dòng "Kết quả" và bảng mục 5 `eval/README.md` (ghi rõ: lượt 1 có 8 câu lỗi timeout, lượt 2 là chạy lại).
- DoD: không còn ô `pass` trống; `score` in % tổng và theo type.

**A2 · Thử mô phỏng chi phí** — Chờ: không — Trạng thái:
- Làm: kiểm `cost/personas.yaml` (≥ 3 persona: dùng ít / vừa / nhiều; tần suất lấy từ khảo sát: 6/12 lên lịch 1 lần, 6/12 lên lịch 2–3 lần trong 3 tháng); khai giá gpt-4.1-mini và ≥ 1 model khác → `python run.py simulate --try`.
- DoD: `cost/simulate-try.csv` có token > 0 (file thử, không commit).

**A3 · `build_deck` + `plan_group` (TS-03, TS-06)** — Chờ: không — Trạng thái:
- Làm: `build_deck(cfg)`: code lọc ứng viên (nội thành, mở vào thứ ngày đi, giao khung giờ, `price_max_vnd` ≤ budget mỗi người nếu có giá) → model chọn + xếp hạng 20 ID kèm lý do (JSON) → loại ID lạ, bỏ lý do có chữ số. `plan_group(cfg, scores, pinned)`: chọn ứng viên theo điểm → `planner.plan` (ưu tiên ghim) → `planner.check` → trả theo hợp đồng mục 2; thêm ràng buộc budget và slot ăn trưa / tối (TS-06).
- DoD: thêm assert vào `tests/test_core.py`: thứ Hai không có Lăng Bác / Bảo tàng Dân tộc học / Bảo tàng Mỹ thuật trong bộ thẻ; `plan_group` không bao giờ trả lịch có vi phạm.

**A4 · Lượt cải tiến (guide 4.1)** — Chờ: A1 — Trạng thái:
- Làm: cùng Hùng đọc các câu trượt lượt 2 → gom nhóm lỗi có tên (tên ở `eval/baseline-chatbot.md`) → chọn **một** nhóm lỗi đau nhất với người dùng → sửa → `python run.py eval` **trọn bộ 22 câu** (thêm câu mới thì chỉ thêm, không sửa) → chấm `pass` → `score`.
- DoD: có `eval/run-3.csv` đã chấm; ghi rõ cấu hình đổi gì so với lượt trước.

**A5 · Báo cáo đánh giá** — Chờ: A4 — Trạng thái:
- Deliverable: `eval/report.md` + `eval/README.md` (mục 1, 5, 6).
- Yêu cầu output: % đạt từng lượt so với chuẩn "đạt" §7 (đạt / chưa đạt, vì sao) · **≥ 3 lỗi**, mỗi lỗi có input · output · vì sao sai · đã sửa gì · lỗi còn lại · bảng các lượt (run ID · model · cấu hình · đạt / tổng · %). Người ngoài đọc `eval/README.md` hiểu được đo gì, bằng gì, ra số nào.
- DoD: mọi số trùng với `python run.py score`.

**A6 · Mô phỏng chi phí khi dùng thật (guide 4.2)** — Chờ: A4 — Trạng thái:
- Làm: `python run.py simulate --rate-from eval/run-3.csv` (≥ 50 phiên, seed cố định) → `cost/cost-estimate.md`.
- Yêu cầu output: chi phí / task thành công = chi phí trung bình / phiên ÷ tỉ lệ đạt (không dùng 100%) · 3 kịch bản thấp / cơ sở / cao · ≥ 2 mức model (rẻ, mạnh) · số người dùng thật có nguồn hoặc *(tự ước tính)* · một dòng kết luận đáng làm hay không so với impact. Ghi "đo token trên gpt-4.1-mini, tính giá model X".
- Deliverable: `cost/simulate-N.csv`, `cost/simulate-N-summary.md`, `cost/cost-estimate.md`, `traces/simulate-N.jsonl` (commit hết).

### Hùng · BA / tester / tài liệu

**D1 · Tổng hợp bằng chứng (CP3)** — Chờ: không — Trạng thái:
- Làm: đóng hoặc chụp số khảo sát (mục tiêu ≥ 20 người đúng vai) → xuất CSV **đã xoá** cột thời gian và mọi cột nhận diện → `evidence/survey/results.csv` + điền `evidence/survey/TEMPLATE.md` (câu hỏi, cách gửi, số phản hồi) → `evidence/summary.md`.
- Yêu cầu output: x/N và % cho từng con số chính (vd 9/12 = 75% gặp đi vòng / đóng cửa / bỏ lỡ) · **≥ 5 trích nguyên văn** có nguồn (số phiếu), bỏ tên · kết luận giả thuyết: vế 1 đạt, vế 2 (thời gian ≥ 1 giờ) **không đạt** — ghi đúng như vậy · nếu có đào review thì ghi `evidence/data-mining.md` (cách chọn mẫu, cách đếm, x/N).
- DoD: ≥ 1 nguồn đạt ngưỡng (khảo sát ≥ 20 người); không còn ô `__` trong `summary.md`.

**D2 · spec §1 §2 §6 (CP3)** — Chờ: không — Trạng thái:
- Làm: §1 số khảo sát + 1–2 trích dẫn · §2 bảng impact: điền ô `__` bằng số khảo sát (người lên lịch, lần / tháng, phút / lần), công thức impact / tháng, mỗi thừa số có nguồn hoặc *(tự ước tính)* · §6 bốn đường đi (suôn sẻ / không chắc / không có căn cứ / người dùng sửa / ngoài phạm vi / đặc thù) — lấy từ kịch bản §5.
- DoD: `spec.md` §0–§7 không còn ô trống trừ dòng kết quả do Hải điền.

**D3 · Nộp CP3** — Chờ: D1, D2, U1, A1 — Trạng thái:
- Làm: tự soát guide 3.4 → form CP3: link `evidence/summary.md`, số câu thử (22; kho 12; tu_choi 4), link video, kết quả lượt (x/22 + run ID), link `spec.md`, phần chưa xong (web).
- DoD: nộp trước 10:00.

**D4 · Kiểm thử CLI bằng câu lạ** — Chờ: không — Trạng thái:
- Làm: tự viết 5 câu chưa có trong bộ thử (ngày lễ, điểm ngoại thành, tên viết sai dấu, khung giờ qua trưa, yêu cầu đặt bàn lẫn trong câu dài) → chạy `python run.py` → ghi kết quả vào `validation/cli-test.md` → câu nào lỗi thì báo Hải.
- Yêu cầu output: mỗi câu: input · output tóm tắt · đúng / sai · vì sao. Câu hay có thể **thêm** vào bộ thử (`source: tu_viet`), không sửa câu cũ.

**D5 · Người dùng thử (bonus, guide 4.3)** — Chờ: có bản chạy được (CLI hoặc web) — Trạng thái:
- Làm: 2–3 người ngoài nhóm đúng vai (từng lên lịch đi chơi cho nhóm) · 5 nhịp, 10 phút / người · không thuyết minh.
- Deliverable: `validation/log.md`: mỗi người `vai | việc giao | quan sát | trích nguyên văn | mức nghiêm trọng` + 4 dòng tổng hợp (chủ đề lặp · sửa gì trước demo → §10 · giữ gì vì sao · để sau).

**D6 · spec §8 §9 + slide** — Chờ: A5, A6 — Trạng thái:
- Làm: §8 chép số từ `cost/cost-estimate.md` · §9 rủi ro & an toàn (lấy từ §4 chỗ chặn rủi ro + §5) · slide 8 trang theo guide 5.1 (pain · vì sao chọn · giải pháp · demo · đánh giá · chi phí · kết luận go / iterate / stop · nếu có thêm 1 tuần).
- Deliverable: `slides/demo-slides.pdf` (+ nguồn slide).
- Yêu cầu output: **mỗi trang ≥ 1 con số / trích dẫn có nguồn / kết quả đo**; số trùng với repo.

**D7 · Kiểm thử luồng web** — Chờ: U5, B5 — Trạng thái:
- Làm: 2 trình duyệt, đi trọn TS-01 → TS-07; thử corner case PRD (mã sai, biệt danh trùng, không thẻ nào ≥ 0,5, ghim điểm đóng cửa) → ghi lỗi vào `validation/web-test.md`, báo Bảo / Minh.
- DoD: không còn lỗi chặn luồng demo.

**D8 · Nộp CP4** — Chờ: tất cả việc CP4 — Trạng thái:
- Làm: tự soát guide 4.4 → form CP4: phòng demo, link repo, tích 7 hạng mục, lượt 1 → lượt cải tiến (x/22 → y/22), chi phí / task thành công + tên model, link slide, link video dự phòng, phần chưa xong (khai thật).
- DoD: nộp trước 14:30.

## 5. Demo & hạn chót · 23:59

| # | Việc | Người | Hạn | DoD | Trạng thái |
|---|---|---|---|---|---|
| F1 | Demo: Hùng — pain + impact · Bảo — demo web (1 thường + 1 khó) · Minh — kiến trúc + bộ kiểm lịch · Hải — đánh giá + chi phí. Chạy được 1 câu thử lạ giám khảo đưa; mở được trace 1 câu trượt | Cả nhóm | 14:30–18:00 | Ai cũng trả lời được 4 câu guide 5.2 | |
| F2 | Sửa theo góp ý; ghi `spec.md` §10 (giờ · đổi gì · vì sao); chạy thêm thì thành lượt mới | Người sở hữu phần đó | 23:00 | Không đụng chuẩn "đạt", câu thử, lượt cũ | |
| F3 | `reflection/<ten-khong-dau>.md`: vai + phần mình làm (trỏ file / commit) · AI hỗ trợ thế nào · một bài học từ một câu thử trượt của nhóm | Cả nhóm | 23:30 | 4 file | |
| F4 | Checklist guide 5.2: không có key / dữ liệu cá nhân trong repo, video mở được ẩn danh, `TEAMS.md` khớp vai, `docs/ai-usage.md` + README mục "Dùng AI vào việc gì" điền đủ, `python run.py check` sạch | Hùng | 23:45 | Checklist tích đủ | |
