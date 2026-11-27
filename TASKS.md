# TASKS — CP2 (19:30 Thứ Sáu 27/11)

> Tự nhận việc: điền tên mình vào cột **Người nhận**, commit, push. Mỗi việc một người.
> Xong thì đổi cột **Trạng thái** thành `xong` kèm link file / commit.
> Mỗi người phải giải thích được phần có tên mình (luật chung).

## BA

| # | Việc | File | Hạn | Người nhận | Trạng thái |
|---|---|---|---|---|---|
| BA1 | Soạn và gửi khảo sát online cho 25 người ngoài nhóm; tổng hợp kết quả, rút trích dẫn nguyên văn (bỏ tên) | `evidence/survey/`, `evidence/summary.md` | gửi trước 17:30 · số đầu tiên 19:15 | | |
| BA2 | Đào review công khai (Google Maps, Tripadvisor, group du lịch Hà Nội): ghi cách chọn mẫu, cách đếm trước khi đọc; x/N, %, ≥5 ví dụ | `evidence/data-mining.md` | 19:00 | | |
| BA3 | Kiểm giờ mở cửa, ngày đóng cửa các địa điểm Hà Nội từ nguồn chính thức, ghi nguồn; viết DATA_CARD bản đầu | `data/DATA_CARD.md` | 18:30 | | |
| BA4 | Viết `spec.md` §0–§3 và §5 (4 lớp chỗ khó, ≥6 kịch bản, 2 tấn công) | `spec.md` | 19:00 | | xong (bản đầu): `spec.md` §0–§3, §5 |
| BA5 | Cập nhật canvas (số bằng chứng đầu, dòng "Đã đổi gì so với CP1"); điền chuẩn "đạt" đã chốt vào `spec.md` §7; nộp CP2 | `canvas.md`, `spec.md` §7 | 19:30 | | canvas + chuẩn "đạt" §7 xong; còn nộp form CP2 |
| BA6 | Chạy tay 10–20 yêu cầu lịch trình qua ChatGPT / Claude, ghi lỗi thấy được (dùng được / sửa được / không chấp nhận) | `eval/README.md` | 18:00 | | xong: 16 câu, `eval/baseline-chatbot.md` |
| BA7 | Viết ≥3 metric từ lỗi ở BA6: định nghĩa kiểm chứng được · cách chấm · ngưỡng | `eval/metric_spec.yaml` | 18:30 | | xong (bản đầu, 6 metric): `eval/metric_spec.yaml` — rà lại theo lỗi BA6 trước 19:30 |
| BA8 | Viết ≥10 câu thử (có `kho`, `tu_choi`), ≥1/3 câu `source` là `nguoi_dung:` hoặc `data_that:` | `eval/benchmark.csv` | 19:00 | | xong (bản đầu, 16 câu): `eval/benchmark.csv` — CP3 cần thêm câu `nguoi_dung` từ khảo sát, lên 20–30 câu |
| BA9 | Chấm thử độc lập 5 output theo metric (người khác người làm BA7); lệch ≥2/5 → báo viết lại metric | — | 19:00 | | phiếu sẵn + người chấm 1 xong: `eval/grading-trial.md` — còn người chấm 2 |

## Engineer

| # | Việc | File | Hạn | Người nhận | Trạng thái |
|---|---|---|---|---|---|
| EN1 | Sơ đồ kiến trúc, bảng công cụ, mức tự động, chỗ chặn rủi ro, chỗ người duyệt | `spec.md` §4 | 18:30 | | |
| EN2 | Công cụ trả dữ liệu giả (`tra_dia_diem`, `tra_gio_mo_cua`, `uoc_thoi_gian_di`, `kiem_lich_trinh`) + luồng chính chạy hết với AI giả | `codebase/tools.py`, `codebase/agent.py` | 19:15 | | |
| EN3 | Lấy API key, nối model, gọi thử được 1 câu (`python run.py eval --try`) | `.env` (không commit), `codebase/ai.py` | trước khi rời lớp | | |
| EN4 | Dựng dữ liệu Hà Nội ~20–30 địa điểm (giờ mở cửa, ngày đóng cửa, toạ độ) từ kết quả BA3 | `data/` | 18:45 | | |
| EN5 | Chạy `python run.py check` và `python run.py` sạch trước khi nộp | — | 19:15 | | |

## Phụ thuộc

- BA3 → EN4 (giờ mở cửa đã kiểm) · BA1, BA2 → BA8 (trích dẫn làm câu thử) · BA6 → BA7 → BA9 · EN1 → EN2 (tên công cụ khớp `tools.py`).
- **19:00:** cả nhóm chốt chuẩn "đạt" (§7). Sau CP2 không sửa.
- Nhận việc xong: cập nhật cột "Phần việc chính" trong `TEAMS.md` cho khớp.
