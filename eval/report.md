# Báo cáo đánh giá — lượt 1 → cải tiến → lượt 4

> Số liệu khớp nguyên văn đầu ra `python run.py score eval/run-N.csv` trên cùng bộ 22 câu thử (`eval/benchmark.csv`) và cùng 6 metric (`eval/metric_spec.yaml`, chốt trước CP2). Không sửa chuẩn "đạt", không bỏ câu trượt, không sửa kết quả các lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Model | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" (`spec.md` §7) |
|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | `run-1@20261128-011133` | `gpt-4.1-mini` | 13/22 | 59% | 3/6 (50%) | 6/12 (50%) | 4/4 (100%) | **Chưa đạt** (< 75%; 8 câu lỗi kỹ thuật timeout proxy, tính trượt) |
| 2 | `run-2@20261128-015044` | `gpt-4.1-mini` | 20/22 | 91% | 4/6 (67%) | 12/12 (100%) | 4/4 (100%) | **Đạt** (≥ 75%, `dung_gio_mo_cua` 100%, `khong_bia_du_lieu` 100%, `tu_choi` 4/4) |
| 3 | `run-3@20261128-084622` | `gemini-3.5-flash-lite` | 20/22 | 91% | 4/6 (67%) | 12/12 (100%) | 4/4 (100%) | **Chưa đạt** (tổng 91% nhưng **vi phạm `dung_gio_mo_cua` ở B19**: lộ lỗi `parse_hours` không bắt `"đóng cửa trưa"`) |
| 4 | `run-4@20261128-085230` | `gemini-3.5-flash-lite` | 21/22 | 95% | 5/6 (83%) | 12/12 (100%) | 4/4 (100%) | **Đạt** (≥ 75%, `dung_gio_mo_cua` 100%, `khong_bia_du_lieu` 100%, `tu_choi` 4/4) |

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`, `eval/run-3.csv`, `eval/run-4.csv`. Trace: `traces/run-1.jsonl` … `traces/run-4.jsonl`.

## 2. Lỗi qua các lượt — gom thành nhóm có tên

| Nhóm lỗi | Số câu bị ảnh hưởng | Câu | Ghi chú |
|---|---:|---|---|
| Lỗi kỹ thuật timeout kết nối proxy (lượt 1) | 8 | B02, B06, B07, B09, B17, B18, B20, B21 | Lỗi hạ tầng, không phải lỗi logic; hết sau khi thêm retry ở `ai.py` (lượt 2: 0/22 lỗi) |
| Rút thiếu hoặc tự thêm địa điểm khi đọc yêu cầu (`extract`) | 2 | B19 (trượt lượt 2), B13 (lỗi phụ lượt 2) | B19 model bỏ sót Chùa Trấn Quốc; B13 model tự thêm quán "Lẩu gà lá é" không có trong yêu cầu |
| Bỏ qua giờ nghỉ trưa do chuẩn hoá chuỗi giờ (`parse_hours`) | 1 | B19 (lộ ra ở lượt 3) | Chuỗi `"đóng cửa trưa 11:30 - 13:30"` không khớp từ khoá `"nghi trua"` → xếp 12:55–13:55 vào giờ nghỉ trưa |
| Không xếp vừa do thời lượng tham quan cố định trong dữ liệu | 1 | B03 (trượt cả 4 lượt) | Hỏa Lò (90 phút) + Bảo tàng Phụ nữ (90 phút) + di chuyển vượt 17:00 trong khung 14:00–17:00 |

**Chi tiết 4 lỗi cụ thể (≥ 3 lỗi bắt buộc):**

| Câu | Input | Output (tóm tắt) | Vì sao sai | Đã sửa gì | Lỗi còn lại |
|---|---|---|---|---|---|
| **B19** *(lượt 2)* | "Chủ nhật 8:00–17:00 xuất phát Hồ Gươm, đi Chùa Trấn Quốc, Nhà tù Hỏa Lò, Văn Miếu, Bảo tàng Phụ nữ. Xếp sao cho đỡ chạy qua chạy lại." | Chỉ xếp 3 điểm (BT Phụ nữ, Hỏa Lò, Văn Miếu); không có Chùa Trấn Quốc trong lịch lẫn danh sách bị bỏ | Model bỏ sót `hn_12` khi rút yêu cầu → người dùng bị mất điểm đã chọn mà không có lý do | Kết hợp `match_places(text)` bù ID khớp tên vào `extract()` và siết prompt `EXTRACT_SYSTEM` (`codebase/agent.py`) | Đã hết ở lượt 3 & 4 |
| **B19** *(lượt 3)* | *(như trên)* | Đủ 4 điểm nhưng xếp `12:55–13:55 Chùa Trấn Quốc` | Chùa Trấn Quốc đóng cửa trưa 11:30–13:30; `parse_hours()` trong `codebase/places.py` chỉ kiểm `"nghi trua"`, bỏ sót `"dong cua trua"` → vi phạm `dung_gio_mo_cua` | Mở rộng điều kiện `parse_hours()` bắt cả `"dong cua trua"` + thêm assert vào `tests/test_core.py` | Đã hết ở lượt 4 (`13:30–14:30`, 0 vi phạm) |
| **B13** *(lượt 2)* | "Xếp lịch thứ Bảy cho nhóm 5 người rồi đặt luôn vé xem múa rối nước và đặt bàn ăn tối giúp mình nhé." | Từ chối đặt vé đúng, nhưng tự xếp thêm `LẨU GÀ LÁ É 79K - CỎ GÀ` (`hn_local_42`) | Người dùng không nêu tên quán; tự thêm địa điểm ngoài yêu cầu dễ gây hiểu nhầm (lỗi phụ, phần từ chối vẫn đạt) | Siết prompt `EXTRACT_SYSTEM`: không tự thêm quán khi người dùng chỉ nói chung "ăn tối" | Đã hết ở lượt 3 & 4 (chỉ còn Nhà hát Múa rối Thăng Long) |
| **B03** *(lượt 1–4)* | "Chủ nhật nhóm mình rảnh từ 14:00 đến 21:00, xuất phát Hồ Gươm. Muốn đi Nhà tù Hỏa Lò, Bảo tàng Phụ nữ, và tham quan Văn Miếu buổi tối." | Xếp Hỏa Lò (14:05–15:35) và Tour Đêm Văn Miếu (18:30–20:00); bỏ Bảo tàng Phụ nữ (`không đủ thời gian`) | Dữ liệu ghi thời lượng cố định 90 phút cho cả Hỏa Lò và BT Phụ nữ, cộng 2 chặng đi (~5 phút/chặng) thành 190 phút > 180 phút (14:00–17:00) | Chưa sửa (giữ nguyên dữ liệu và không nới luật cứng) | Còn lại ở lượt 4; cần hỗ trợ khoảng thời lượng linh hoạt (min–max) cho bảo tàng |

## 3. Quá trình cải tiến (lượt 2 → lượt 3 → lượt 4)

- **Nhóm lỗi chọn sửa (đau nhất với người dùng):**
  1. **Rút thiếu / tự thêm địa điểm khi đọc yêu cầu (B19, B13)** — người dùng đã chọn điểm nhưng bị biến mất không có lý do.
  2. **Chuẩn hoá giờ đóng cửa trưa (B19 ở lượt 3)** — lỗi đắt nhất theo `spec.md` §5 lớp 4 vì đưa cả nhóm đến nơi đúng giờ đóng cửa trưa.
- **Đã sửa gì:**
  - `codebase/agent.py`: siết `EXTRACT_SYSTEM` (không tự thêm địa điểm không nêu tên, không bỏ sót điểm đã nhắc) + bù ID khớp tên từ `match_places(text)` trong `extract()` (loại điểm xuất phát và tránh trùng Văn Miếu ngày/đêm).
  - `codebase/places.py`: sửa `parse_hours()` nhận thêm chuỗi `"dong cua trua"` bên cạnh `"nghi trua"`.
  - Đổi model chạy từ `gpt-4.1-mini` (lượt 2) sang `gemini-3.5-flash-lite` (lượt 3 & 4) để đồng bộ với mô phỏng chi phí A6.
- **Kết quả:**
  - Nhóm lỗi rút địa điểm (B19, B13): **0/1 → 1/1** (hết lỗi bỏ sót ở B19 và hết tự thêm quán ở B13).
  - Nhóm lỗi giờ nghỉ trưa (`dung_gio_mo_cua`): phát hiện lỗi ẩn ở lượt 3 (**21/22**) → sửa triệt để ở lượt 4 (**22/22 = 100%**).
  - Tổng bộ câu thử: **13/22 (59%, lượt 1)** → **20/22 (91%, lượt 2)** → **20/22 (91%, lượt 3)** → **21/22 (95%, lượt 4)**.
- **Câu nào tệ đi sau khi sửa:** không có câu nào ở lượt 2 đạt mà trượt ở lượt 4 (0 hồi quy).

## 4. Còn lại

- **Lỗi chưa sửa + mức nguy hiểm:**
  - **B03 (thời lượng tham quan cứng 90 phút):** mức độ **thấp–trung bình** — hệ thống không hề đưa người dùng tới nơi đóng cửa mà báo rõ "không đủ thời gian" và gợi ý nới khung giờ. Tuy nhiên trong thực tế nhóm có thể đi nhanh hơn 75–80 phút/bảo tàng để kịp cả 2 điểm trước 17:00.
  - **Lý do chọn đôi khi lệch nhẹ ngữ cảnh giờ** (vd B19 lượt 4: Chùa Trấn Quốc xếp 13:30–14:30 nhưng lý do LLM viết "ngắm hoàng hôn" lấy từ `why_visit`): không vi phạm metric cứng nhưng cần truyền khung giờ dự kiến vào prompt `reasons` để mô tả khớp buổi.
- **Nếu có thêm 1 tuần:**
  - Thêm trường `min_duration_mins` để bộ xếp lịch co giãn thời lượng trong ngưỡng hợp lý khi khung giờ hơi sát (giải quyết B03).
  - Bổ sung kiểm tra tự động mọi chuỗi `opening_hours` trong `data/hanoi_places.json` bằng unit test khi nạp dữ liệu để không còn chuỗi giờ bị parse thiếu.
  - Truyền buổi đi (sáng / trưa / chiều / tối) vào bước viết lý do để câu giới thiệu khớp khung giờ thật.
