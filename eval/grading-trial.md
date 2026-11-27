# Chấm thử 5 output — kiểm metric có rõ không (guide 2.4 bước 4)

Hai người chấm **độc lập** cùng 5 output theo `eval/metric_spec.yaml`. Lệch ≥2/5 câu (kết luận đạt / trượt cả câu) → định nghĩa metric còn mơ hồ, viết lại trước 19:30.

- Output: `eval/baseline-chatbot.md` (mục "Output nguyên văn"), câu **B04, B08, B09, B10, B12** — chọn đủ loại: nghỉ trưa, ngày đóng, quá nhiều điểm, thiếu ngày, điểm không có dữ liệu.
- Giờ chuẩn để đối chiếu: đầu file `eval/baseline-chatbot.md`.
- Ký hiệu: `Đ` đạt · `T` trượt · `—` metric không áp dụng cho câu này. Câu **đạt** khi mọi metric áp dụng đều `Đ`.

## Người chấm 2 — điền trước, **chưa xem bảng người chấm 1 ở dưới**

Người chấm: __ (không phải người viết `metric_spec.yaml`)

| Câu | dung_gio_mo_cua | khop_khung_gio_nguoi_dung | khong_bia_du_lieu | it_di_vong | bao_ro_khi_khong_xep_duoc | hoi_lai_va_tu_choi_dung | Cả câu | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| B04 | | | | | | | | |
| B08 | | | | | | | | |
| B09 | | | | | | | | |
| B10 | | | | | | | | |
| B12 | | | | | | | | |

## Kết quả so khớp

- Khớp kết luận cả câu: __/5 (cần ≥4/5)
- Metric lệch nhiều nhất: __ → sửa định nghĩa: __
- Ghi vào `eval/README.md` mục 3.

---

<details>
<summary>Người chấm 1 (người viết metric) — chỉ mở sau khi người chấm 2 điền xong</summary>

| Câu | dung_gio_mo_cua | khop_khung_gio_nguoi_dung | khong_bia_du_lieu | it_di_vong | bao_ro_khi_khong_xep_duoc | hoi_lai_va_tu_choi_dung | Cả câu | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| B04 | T | Đ | Đ | Đ | — | — | **T** | Bảo tàng Lịch sử Quốc gia 11:00–12:30 chạm nghỉ trưa 12:00–13:30 |
| B08 | T | Đ | T | Đ | T | — | **T** | Nói Bảo tàng Mỹ thuật mở cả tuần, xếp vào thứ Hai (đóng); không báo điểm này phải bỏ |
| B09 | Đ | Đ | Đ | Đ | T | — | **T** | 3 điểm hợp lệ; 7 điểm bị bỏ không có lý do từng điểm. "Dân tộc học đóng thứ Hai" đúng nhưng thừa |
| B10 | Đ | Đ | T | Đ | — | Đ | **T** | Nói Lăng mở "đến khoảng 10:30" (mùa lạnh 11:00). Theo metric: có nói giả định → `Đ`; theo `pass_criterion` B10 ("không trả lịch dựa trên ngày tự đoán") → trượt. **Mâu thuẫn cần sửa** |
| B12 | T | Đ | T | Đ | — | — | **T** | Bịa giờ Chùa Một Cột "7:00–18:00"; không có nguồn nên không kiểm được giờ đến |

Chỗ người chấm 1 thấy khó quyết, đáng so kỹ: `hoi_lai_va_tu_choi_dung` ở B10 (giả định có nói rõ có tính là đạt?), `khong_bia_du_lieu` ở B09 (thông tin đúng nhưng thừa), `dung_gio_mo_cua` ở B12 (không có dữ liệu giờ thì tính trượt hay không áp dụng).

</details>
