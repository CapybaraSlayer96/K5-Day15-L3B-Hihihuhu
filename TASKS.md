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

> Vai: **Bảo** UI · **Minh** BE · **Hải** AI · **Hùng** BA / tester / tài liệu. Thiết kế: `docs/PRD.md` (TS-01…TS-08), `docs/ARCHITECTURE.md`. Ticket chi tiết (local): `.scratch/tripswipe/issues/`.
> Luật giữ nguyên: không sửa chuẩn "đạt" §7, không sửa / xoá câu thử, không sửa tay `eval/run-*.csv` (trừ cột `pass`, `ghi_chu`), không commit file chứa API key.

## Hiện trạng (sáng 28/11)

- Lõi chạy thật: `answer(text)` + 4 công cụ + xếp lịch + kiểm lịch; model gpt-4.1-mini qua proxy (`MODEL_PROVIDER=openai`).
- Bộ câu thử 22 câu. **Lượt 1:** `run-1@20261128-011133` — 13/22 (59%), 8 câu lỗi timeout proxy. Lượt chạy lại sau khi sửa timeout đang chạy.
- Web (ticket 05–08) chưa có.

## CP3 · 10:00

| # | Việc | Người | File | Hạn | Trạng thái |
|---|---|---|---|---|---|
| C3-1 | `evidence/summary.md`: khảo sát x/N, %, ≥5 trích nguyên văn (bỏ tên), kết luận giả thuyết (vế 1 đạt, vế 2 không đạt); xuất kết quả khảo sát **đã bỏ cột nhận diện** vào `evidence/survey/` | Hùng | `evidence/` | 09:30 | |
| C3-2 | `spec.md` §1 số khảo sát, §2 bảng impact có nguồn, §6 bốn đường đi trải nghiệm | Hùng | `spec.md` | 09:45 | |
| C3-3 | Chấm cột `pass` lượt chạy lại, `python run.py score`, ghi run ID vào `spec.md` §7 + bảng các lượt ở `eval/README.md` mục 5 | Hải | `eval/` | 09:45 | |
| C3-4 | Video 30 giây: `python run.py` gọi AI thật (1 câu thường + 1 câu khó, vd Lăng Bác thứ Hai); YouTube "Không công khai" / Drive "Bất kỳ ai có link", thử ẩn danh | Bảo | link | 09:45 | |
| C3-5 | `python run.py simulate --try` (10 phiên) để kiểm khung chi phí | Hải | `cost/` | 09:50 | |
| C3-6 | Tự soát guide 3.4, nộp form CP3 (khai thật phần chưa xong: web) | Hùng | form | 10:00 | |

## CP4 · 14:30

| # | Việc | Người | File | Hạn | Trạng thái |
|---|---|---|---|---|---|
| C4-1 | Backend FastAPI + Postgres 16: 7 bảng, nạp `places` + ma trận lúc khởi động, 10 endpoint (PRD Technical Requirements) | Minh | `app/` | 12:00 | |
| C4-2 | `docker-compose.yml` + `Dockerfile` (`db`, `app`, cổng 8000), README có lệnh `docker compose up` | Minh | gốc repo | 12:00 | |
| C4-3 | Gộp phiếu trung bình ≥ 0,5, quyền trưởng nhóm, polling tiến độ, `PATCH` itinerary (bỏ / ghim / duyệt, bản cũ `stale`) + 1 test end-to-end qua HTTP | Minh | `app/`, `tests/` | 13:30 | |
| C4-4 | Trang **Tạo nhóm** (wizard: tỉnh, phạm vi, ngày, giờ, xuất phát, budget, phương tiện) + **Vào nhóm** | Bảo | `app/templates`, `app/static` | 12:00 | |
| C4-5 | Trang **Quẹt**: thẻ tổng quan, vuốt lên xem chi tiết, kéo trái / phải + nút, hoàn tác, đếm thẻ còn lại | Bảo | `app/templates`, `app/static` | 13:00 | |
| C4-6 | Trang **Phòng chờ** + **Lịch trình** (dòng thời gian, bản đồ Leaflet, điểm bị bỏ + lý do, nút duyệt / bỏ / ghim, sao chép) | Bảo | `app/templates`, `app/static` | 14:00 | |
| C4-7 | AI tạo bộ 20 thẻ (TS-03): code lọc ứng viên → model chọn + lý do không số; loại ID lạ | Hải | `codebase/` | 12:00 | |
| C4-8 | Đọc câu trượt lượt trước → gom nhóm lỗi → **một** cải tiến → `python run.py eval` trọn bộ → lượt mới → `score` | Hải | `codebase/`, `eval/` | 13:00 | |
| C4-9 | `eval/report.md` (lượt 1 → lượt 2, ≥3 lỗi: input · output · vì sao sai, đã sửa gì, còn gì) + `eval/README.md` (hồ sơ một trang) | Hải | `eval/` | 13:30 | |
| C4-10 | `cost/personas.yaml` (≥3 persona, tần suất từ khảo sát) → `python run.py simulate` ≥ 50 phiên → `cost/cost-estimate.md` (chi phí / task thành công, 3 kịch bản, ≥2 model, so với impact) | Hải | `cost/` | 14:00 | |
| C4-11 | Kiểm thử thủ công cả luồng web + 5 câu thử lạ qua CLI; báo lỗi cho Bảo / Minh / Hải | Hùng | — | 14:00 | |
| C4-12 | *(Bonus)* 2–3 người ngoài nhóm dùng thử theo 5 nhịp → `validation/log.md` | Hùng | `validation/` | 14:00 | |
| C4-13 | Slide 8 trang theo guide 5.1 (mỗi trang ≥1 số có nguồn) → `slides/demo-slides.pdf` | Hùng | `slides/` | 14:15 | |
| C4-14 | `spec.md` §8 (chi phí, lấy từ C4-10) và §9 (rủi ro & an toàn) | Hùng | `spec.md` | 14:15 | |
| C4-15 | Video demo dự phòng quay bằng web | Bảo | link | 14:20 | |
| C4-16 | Tự soát guide 4.4, nộp form CP4 (phòng demo, link repo, lượt 1 → 2, chi phí / task, slide, video, phần chưa xong) | Hùng | form | 14:30 | |

## Demo & hạn chót · 23:59

| # | Việc | Người | Hạn | Trạng thái |
|---|---|---|---|---|
| F-1 | Demo: mỗi người nói ≥1 phần (Hùng: pain + impact · Bảo: demo web · Minh: kiến trúc + kiểm lịch · Hải: đánh giá + chi phí); ai cũng trả lời được 4 câu ở guide 5.2 | Cả nhóm | 14:30–18:00 | |
| F-2 | Sửa theo góp ý; mọi thay đổi ghi `spec.md` §10 (giờ · đổi gì · vì sao); chạy thêm thì thành lượt mới | Người sở hữu phần đó | 23:00 | |
| F-3 | Mỗi người 1 file `reflection/<ten-khong-dau>.md` (vai, phần mình làm, AI hỗ trợ thế nào, một bài học từ một câu thử trượt) | Cả nhóm | 23:30 | |
| F-4 | Checklist cuối guide 5.2: không có API key / dữ liệu cá nhân trong repo, video mở được ẩn danh, `TEAMS.md` cột "Phần việc chính" khớp vai mới, `python run.py check` sạch | Hùng | 23:45 | |
