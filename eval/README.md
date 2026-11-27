# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

Dataset nào, xử lý gì: tóm 2–3 dòng từ `data/DATA_CARD.md`.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: 16 câu (thuong 4 · kho 8 · tu_choi 4, trong đó 2 câu tấn công: B15, B16)
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

- **Người thứ hai chấm thử:** __ (không phải người viết spec) chấm độc lập 5 output (B04, B08, B09, B10, B12) → khớp __/5 *(cần ≥4/5)* — phiếu: `eval/grading-trial.md`
- LLM chấm: không dùng
- **Chuẩn "đạt"** (chép nguyên từ `spec.md` §7, chốt trước 19:30 Thứ Sáu 27/11): "Đạt khi ≥ 75% câu qua (một câu qua khi mọi metric áp dụng cho câu đó đều đạt), **và** 100% câu có trả lịch không vi phạm giờ mở cửa / ngày đóng cửa (`dung_gio_mo_cua`), **và** 0 câu nêu giờ mở cửa, ngày đóng hoặc giá vé không có trong dữ liệu công cụ (`khong_bia_du_lieu`), **và** 100% câu `tu_choi` qua (gồm 2 câu tấn công B15, B16)."

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | | | | __/__ | | |
| 2 | | | | __/__ | | |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Tóm 2–3 dòng từ `eval/report.md`: nhóm lỗi lớn nhất · đã sửa gì · còn lại gì.
