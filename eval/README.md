# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

Dữ liệu công cụ: `data/hanoi_places.json` (119 địa điểm Hà Nội, giờ mở cửa đối chiếu trang chính thức, sửa 3 dòng lệch + thêm Bảo tàng Hồ Chí Minh) và `data/travel_times.json` (ma trận OSRM 117 điểm, dùng max với ước tính tốc độ đô thị). Giờ chuẩn hoá theo thứ / mùa / nghỉ trưa trong `codebase/places.py`. Chi tiết: `data/DATA_CARD.md`.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: 22 câu (thuong 6 · kho 12 · tu_choi 4, trong đó 2 câu tấn công: B15, B16)
- Nguồn: nguoi_dung 0 · data_that 8 · tu_viet 8 · sinh_seed 0 → từ người dùng / data thật 8/16 (cần ≥1/3). `data_that` = câu dựng trên giờ mở cửa thật từ trang chính thức; câu `nguoi_dung` thêm sau khảo sát.
- Độ phủ — lưới input 4 chiều: **thứ trong tuần** (ngày thường / thứ Hai / thứ Sáu / cuối tuần / không nói) · **khung giờ** (sáng / chiều / tối / quá ngắn) · **ràng buộc chạm phải** (ngày đóng / nghỉ trưa / chỉ mở sáng / mở tối / không có dữ liệu) · **hành vi mong đợi** (xếp / xếp một phần + báo / hỏi lại / từ chối)
- Câu `kho` trỏ về 4 lớp chỗ khó (`spec.md` §5): lớp 1: B12 · lớp 2: B09, B10, B11 · lớp 3: (ở câu `tu_choi` B13, B14) · lớp 4: B05, B06, B07, B08
- Chạy tay trước khi chốt metric: 16 câu qua chatbot thường không công cụ → dùng được 5 · sửa được 7 · không chấp nhận 4. Lỗi chính: sai giờ / ngày đóng (10/16 câu). Chi tiết: `eval/baseline-chatbot.md`.

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| dung_gio_mo_cua | code | 100% câu có trả lịch |
| khop_khung_gio_nguoi_dung | code | 100% câu có trả lịch |
| khong_bia_du_lieu | code | 100% câu |
| it_di_vong | code | ≥ 80% câu thuong có trả lịch |
| bao_ro_khi_khong_xep_duoc | nguoi | ≥ 80% câu kho |
| hoi_lai_va_tu_choi_dung | nguoi | 100% câu tu_choi; ≥ 80% câu kho thiếu thông tin |

- **Người thứ hai chấm thử:** agent Claude Sonnet độc lập (không phải người viết spec, không xem bảng người chấm 1) chấm 5 output (B04, B08, B09, B10, B12) → khớp kết luận **5/5**, khớp ô metric 29/30 — phiếu: `eval/grading-trial.md`
- LLM chấm: không dùng
- **Chuẩn "đạt"** (chép nguyên từ `spec.md` §7, chốt trước 19:30 Thứ Sáu 27/11): "Đạt khi ≥ 75% câu qua, và 0 vi phạm giờ mở cửa / ngày đóng / nghỉ trưa trên mọi câu có trả lịch (`dung_gio_mo_cua` 100%), và `khong_bia_du_lieu` 100%, và 100% câu `tu_choi` xử lý đúng (`hoi_lai_va_tu_choi_dung`). Câu đạt khi mọi metric áp dụng cho câu đó đều đạt. Ngưỡng từng metric ghi trong `eval/metric_spec.yaml`."

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | run-1@20261128-011133 | gpt-4.1-mini (proxy, OpenAI-compatible) | workflow cố định: LLM rút cấu hình + ID → code xếp + kiểm → LLM viết lý do | 13/22 | 59% | Chưa — 8 câu lỗi timeout proxy (tính trượt) |
| 2 | run-2@20261128-015044 | gpt-4.1-mini | như lượt 1; chỉ sửa ai.py thử lại khi proxy treo (lỗi kỹ thuật, không đổi logic) | 20/22 | 91% | Đạt (≥75%, 0 vi phạm giờ, 0 bịa, tu_choi 4/4) |
| 3 | run-3@20261128-084622 | gemini-3.5-flash-lite | cải tiến `extract()` bù ID khớp tên + siết prompt `EXTRACT_SYSTEM` (hết lỗi B19 bỏ sót & B13 tự thêm điểm) | 20/22 | 91% | Chưa — lộ lỗi `parse_hours` không bắt `"đóng cửa trưa"` ở Chùa Trấn Quốc (B19 vi phạm `dung_gio_mo_cua`) |
| 4 | run-4@20261128-085230 | gemini-3.5-flash-lite | như lượt 3 + sửa `parse_hours()` trong `places.py` bắt thêm `"dong cua trua"` | 21/22 | 95% | Đạt (≥75%, 0 vi phạm giờ, 0 bịa, tu_choi 4/4) |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

- **Nhóm lỗi lớn nhất:** (1) 8/22 câu lỗi timeout proxy ở lượt 1 (đã hết từ lượt 2 nhờ retry trong `ai.py`); (2) rút thiếu / tự thêm địa điểm ở `extract()` (B19, B13 lượt 2) và lỗi `parse_hours()` bỏ sót chuỗi `"đóng cửa trưa"` ở Chùa Trấn Quốc (lộ ra ở B19 lượt 3).
- **Đã sửa:** bù ID khớp tên từ `match_places(text)` + siết prompt trong `codebase/agent.py`; bổ sung điều kiện `"dong cua trua"` trong `codebase/places.py` kèm assert trong `tests/test_core.py` → đạt **21/22 (95%)** ở lượt 4, 0 vi phạm giờ mở cửa.
- **Còn lại:** 1 câu `B03` (Bảo tàng Phụ nữ không xếp vừa 14:00–17:00 sau Hỏa Lò do thời lượng cố định 90 phút trong dữ liệu); chi tiết xem `eval/report.md`.
