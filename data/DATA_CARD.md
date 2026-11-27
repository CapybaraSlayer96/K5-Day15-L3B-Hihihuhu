# Data card — dữ liệu bản chạy thử dùng

> Bản đầu (CP2) cho ứng dụng lập lịch trình du lịch kiểu quẹt thẻ (Tinder-style), tập trung bản chạy thử tại **Hà Nội** và mở rộng 11 tỉnh/thành. Toàn bộ dữ liệu chạy thử lưu trong thư mục `data/`.

---

## Dataset · `data/hanoi_places.json` (Bộ POI Hà Nội chi tiết — dữ liệu chạy thử chính)

| | |
|---|---|
| **Dùng để làm gì** | Nguồn dữ liệu chính cho luồng quẹt thẻ (Tinder-style), bộ lọc `about` kiểu Google Maps (trời mưa, ngân sách, gia đình, vibe) và thuật toán lập lịch trình theo khung giờ / tránh ngày đóng cửa tại Hà Nội |
| **Từ đâu** | (1) 75 địa điểm cốt lõi tại Hà Nội (gồm 5 nhà hàng chay xác thực từ nguồn chính thức) đối chiếu giờ mở cửa/ngày đóng cửa từ **20 nguồn chính thức** (`bqllang.gov.vn`, `mod.gov.vn`, `vanmieu.gov.vn`, `hoangthanhthanglong.vn`, `hoalo.vn`, `vme.org.vn`, `vnfam.vn`, `baotangphunu.org.vn`, `baotanglichsu.vn`, `thanglongwaterpuppet.com`, `hanoi.gov.vn`, `uudamchay.vn`, `vilai.vn`, `nangtam.com.vn`, `comchayanphuc.net`); (2) 43 quán ăn/cà phê bản địa lọc từ `data/friend_hanoi_raw.csv`; (3) Ảnh từ Wikipedia tiếng Việt (khớp đúng tiêu đề) và kho ảnh Unsplash tuyển chọn |
| **Xử lý những bước gì** | Lọc dòng đủ trường · loại dòng ngoài Hà Nội/trùng lặp/đóng cửa · đối chiếu & sửa lệch tọa độ theo tâm quận (**0/118 điểm nội thành lệch > 3.5 km**) · gắn `google_maps_url` (Place Card), `closed_days`/`closed_weekdays`, `time_slots`, `cluster`, `price_min_vnd`/`price_max_vnd`, `card_hook`, `swipe_tags`, `nearby_ids` (< 1.5 km), `dietary`, `parking`, `weather_suitability`, `review_summary`, `video_links`, `about`, `search_text` · kiểm `HTTP 200` cho 100% ảnh (**64 ảnh duy nhất, 0 ảnh lỗi**) (script: `build_hanoi_dataset.py`) |
| **Số dòng / số đoạn** | **118 POI** (`food_drink: 66`, `culture: 17`, `landmark: 15`, `nature: 10`, `show_experience: 10`) phủ **19 quận/huyện** và **9 cụm di chuyển** (`ho_guom_pho_co: 47`, `dong_da_hai_ba_trung: 29`, `ba_dinh_di_tich: 15`, `ho_tay_truc_bach: 14`, ...) |
| **Phiên bản / ngày lấy** | `v2.0.0` · `2026-11-28` *(nâng cấp từ `v1.0.0` ngày `2026-11-27`)* |
| **Nhãn** | **Thật** (tên địa điểm, địa chỉ số nhà, tọa độ, giờ mở cửa & ngày đóng cửa chính thức) · **`synthetic` một phần** (nội dung tóm tắt quẹt thẻ `card_hook`/`why_visit`/`what_to_do`, `review_summary` tổng hợp từ dữ liệu thật và nhãn lọc `about` do nhóm/script chuẩn hóa) |
| **Giới hạn** | Tỷ trọng nghiêng về nội thành (`Hoàn Kiếm` + `Ba Đình` chiếm 55.9%) và nhóm `food_drink` (55.9%); 43 quán bản địa từ sheet và 5 quán chay dùng ảnh đại diện món ăn thay vì ảnh mặt tiền quán; tọa độ quán trong ngõ sâu có thể lệch 50–300m ra đầu phố (đã bù bằng `google_maps_url` mở thẳng Place Card). Giờ mở cửa các dịp Lễ/Tết hoặc bảo dưỡng Lăng Bác có thể thay đổi theo thông báo từng năm. |

**Thay đổi từ `v1.0.0` -> `v2.0.0`:**
- **Bổ sung nguồn thật (+5 POI -> 118 POI, 20 nguồn chính thức):** Thêm 5 nhà hàng chay nổi tiếng đã kiểm chứng địa chỉ mới nhất & tọa độ thật (*Ưu Đàm Chay 55 Nguyễn Du*, *Chay Vị Lai*, *Chay Sadhu*, *Cơm Chay Nàng Tấm*, *Cơm Chay An Phúc 20 ngõ 113 Hoàng Cầu*) để lấp khoảng trống persona ăn chay.
- **Thêm lớp kiểm chứng sau khi Match (không bịa quote giả):** Thêm `review_summary` (`pros`/`cons` rút từ dữ liệu thật) và `video_links` (`tiktok_search`, `youtube_search` — 0% link chết).
- **Thêm 3 nhu cầu ẩn có căn cứ thực tế:** `dietary` (`vegan`/`vegetarian`/`vegetarian_friendly`/`contains_shrimp_paste`), `parking` (`on_site`/`street_or_nearby_lot`/`check_ahead`), và `weather_suitability` (`good_for`/`avoid` theo khí hậu Hà Nội).
- **Số hóa hoàn chỉnh cho AI Agent & UX quẹt thẻ:** Thêm `card_hook`, `swipe_tags` (3 badge), `cluster` (9 cụm di chuyển), `time_slots`, `closed_weekdays` (ISO `0–6`), `price_min_vnd`/`price_max_vnd`, `nearby_ids` (< 1.5 km), và `search_text` (cho BM25/RAG/Tool-calling).
- **Sửa lỗi chất lượng dữ liệu:** Rà và sửa chuẩn 5 điểm lệch quận từ sheet bạn gửi (`0/118` điểm nội thành lệch > 3.5 km), mở rộng kho ảnh từ 45 lên **64 URL ảnh duy nhất** và kiểm chứng trực tiếp **`118/118` ảnh `HTTP 200` (`Broken: 0`)**.

**Kiểm giờ mở cửa & ngày đóng cửa chính thức (trích các điểm dễ lập lịch nhầm ngày nghỉ):**
- **Nghỉ Thứ 2 & Thứ 6:** Lăng Chủ tịch Hồ Chí Minh (`bqllang.gov.vn`), Bảo tàng Lịch sử Quân sự VN cơ sở mới — khách lẻ (`mod.gov.vn`).
- **Nghỉ Thứ 2:** Hoàng Thành Thăng Long (`hoangthanhthanglong.vn`), Cột Cờ Hà Nội (`hoangthanhthanglong.vn`), Bảo tàng Dân tộc học VN (`vme.org.vn`), Bảo tàng Lịch sử Quốc gia (`baotanglichsu.vn`).
- **Mở hàng ngày (kể cả Thứ 2):** Văn Miếu (`vanmieu.gov.vn`), Nhà tù Hỏa Lò (`hoalo.vn`), Bảo tàng Mỹ thuật VN (`vnfam.vn`), Bảo tàng Phụ nữ VN (`baotangphunu.org.vn`), Nhà hát Múa rối Thăng Long (`thanglongwaterpuppet.com`).
- **Chỉ mở cuối tuần / tối định kỳ:** Phố đi bộ Hồ Gươm & Chợ Đêm Phố Cổ (`T6–CN`, `hanoi.gov.vn`), Tour Đêm Hỏa Lò (`T6–CN`, `hoalo.vn`), Tour Đêm Hoàng Thành (`T7–CN`, `hoangthanhthanglong.vn`), Tour Đêm Văn Miếu 3D Mapping (`T4, T7, CN`, `vanmieu.gov.vn`).


## Thay đổi để khớp nguồn chính thức (28/11/2026)

- `hn_10` Hoàng thành Thăng Long: mở mọi ngày 08:00–17:00 (trang chủ hoangthanhthanglong.vn), bỏ "đóng thứ Hai".
- `hn_46` Bảo tàng Mỹ thuật Việt Nam: đóng thứ Hai (vnfam.vn/en/visiting).
- `hn_13` Chùa Một Cột: xoá giờ mở cửa (không có nguồn chính thức), coi là "chưa có dữ liệu giờ".
- Thêm `hn_76` Bảo tàng Hồ Chí Minh: 08:00–12:00, 14:00–16:30, đóng thứ Hai và thứ Sáu (baotanghochiminh.vn/gio-mo-cua.htm); toạ độ xấp xỉ.

## Dataset 2 · Ma trận thời gian di chuyển (`data/travel_times.json`)

| | |
|---|---|
| Dùng để làm gì | Nguồn cho công cụ `uoc_thoi_gian_di` |
| Từ đâu | OSRM server công cộng FOSSGIS (`routing.openstreetmap.de`), profile ô tô (dùng cho cả xe máy) và đi bộ; script `scripts/build_travel_matrix.py` |
| Xử lý | Chỉ điểm nội thành + 6 điểm xuất phát trung tâm quận; giây → phút. Khi dùng: lấy max(OSRM, đường chim bay × 1,3 ÷ tốc độ), tối thiểu 5 phút, vì OSRM không tính kẹt xe |
| Số dòng | 117 điểm · 40.716 cặp có hướng |
| Phiên bản / ngày lấy | 28/11/2026 |
| Nhãn | ước tính (không phải thời gian thực) |
| Giới hạn | Không có giờ cao điểm, chỗ gửi xe, đường một chiều theo giờ |
