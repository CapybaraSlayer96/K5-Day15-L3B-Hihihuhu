# Data card — dữ liệu bản chạy thử dùng

> Bản đầu (CP2) cho ứng dụng lập lịch trình du lịch kiểu quẹt thẻ (Tinder-style), tập trung bản chạy thử tại **Hà Nội** và mở rộng 11 tỉnh/thành. Toàn bộ dữ liệu chạy thử lưu trong thư mục `data/`.

---

## Dataset · `data/hanoi_places.json` (Bộ POI Hà Nội chi tiết — dữ liệu chạy thử chính)

| | |
|---|---|
| **Dùng để làm gì** | Nguồn dữ liệu chính cho luồng quẹt thẻ (Tinder-style), bộ lọc `about` kiểu Google Maps (trời mưa, ngân sách, gia đình, vibe) và thuật toán lập lịch trình theo khung giờ / tránh ngày đóng cửa tại Hà Nội |
| **Từ đâu** | (1) 70 địa điểm cốt lõi tại Hà Nội do nhóm biên tập và đối chiếu giờ mở cửa/ngày đóng cửa từ **16 nguồn chính thức** (`bqllang.gov.vn`, `mod.gov.vn`, `vanmieu.gov.vn`, `hoangthanhthanglong.vn`, `hoalo.vn`, `vme.org.vn`, `vnfam.vn`, `baotangphunu.org.vn`, `baotanglichsu.vn`, `thanglongwaterpuppet.com`, `hanoi.gov.vn`); (2) 43 quán ăn/cà phê bản địa lọc từ `data/friend_hanoi_raw.csv`; (3) Ảnh từ Wikipedia tiếng Việt (khớp đúng tiêu đề) và kho ảnh Unsplash tuyển chọn |
| **Xử lý những bước gì** | Lọc dòng đủ trường (tên, địa chỉ Hà Nội, giờ mở cửa hợp lệ, `Giá max > 0`) · loại dòng ngoài Hà Nội/trùng lặp/đóng cửa · đối chiếu tọa độ thật qua **Photon/OSM** trong khung Hà Nội (`20.85–21.25, 105.65–106.00`) · gắn `google_maps_url` (Place Card) & `closed_days` chính thức · sinh bộ lọc `about` · kiểm `HTTP 200` cho 100% ảnh (script: `build_hanoi_dataset.py`) |
| **Số dòng / số đoạn** | **113 POI** (`food_drink: 61`, `culture: 17`, `landmark: 15`, `nature: 10`, `show_experience: 10`) phủ **19 quận/huyện** Hà Nội (`Hoàn Kiếm: 41`, `Ba Đình: 21`, `Đống Đa: 15`, `Hai Bà Trưng: 11`, `Tây Hồ: 8`, và các điểm ngoại thành/day-trip) |
| **Phiên bản / ngày lấy** | `v1.0.0` · `2026-11-27` |
| **Nhãn** | **Thật** (tên địa điểm, địa chỉ số nhà, tọa độ, giờ mở cửa & ngày đóng cửa chính thức) · **`synthetic` một phần** (nội dung tóm tắt quẹt thẻ `why_visit`/`what_to_do` và nhãn lọc `about` do nhóm/script chuẩn hóa) |
| **Giới hạn** | Tỷ trọng nghiêng về nội thành (`Hoàn Kiếm` + `Ba Đình` chiếm 54.9%) và nhóm `food_drink` (54%); 43 quán bản địa từ sheet dùng ảnh đại diện món ăn thay vì ảnh mặt tiền quán; tọa độ quán trong ngõ sâu có thể lệch 50–300m ra đầu phố (đã bù bằng `google_maps_url` mở thẳng Place Card). Giờ mở cửa các dịp Lễ/Tết hoặc bảo dưỡng Lăng Bác có thể thay đổi theo thông báo từng năm. |

**Kiểm giờ mở cửa & ngày đóng cửa chính thức (trích các điểm dễ lập lịch nhầm ngày nghỉ):**
- **Nghỉ Thứ 2 & Thứ 6:** Lăng Chủ tịch Hồ Chí Minh (`bqllang.gov.vn`), Bảo tàng Lịch sử Quân sự VN cơ sở mới — khách lẻ (`mod.gov.vn`).
- **Nghỉ Thứ 2:** Hoàng Thành Thăng Long (`hoangthanhthanglong.vn`), Cột Cờ Hà Nội (`hoangthanhthanglong.vn`), Bảo tàng Dân tộc học VN (`vme.org.vn`), Bảo tàng Lịch sử Quốc gia (`baotanglichsu.vn`).
- **Mở hàng ngày (kể cả Thứ 2):** Văn Miếu (`vanmieu.gov.vn`), Nhà tù Hỏa Lò (`hoalo.vn`), Bảo tàng Mỹ thuật VN (`vnfam.vn`), Bảo tàng Phụ nữ VN (`baotangphunu.org.vn`), Nhà hát Múa rối Thăng Long (`thanglongwaterpuppet.com`).
- **Chỉ mở cuối tuần / tối định kỳ:** Phố đi bộ Hồ Gươm & Chợ Đêm Phố Cổ (`T6–CN`, `hanoi.gov.vn`), Tour Đêm Hỏa Lò (`T6–CN`, `hoalo.vn`), Tour Đêm Hoàng Thành (`T7–CN`, `hoangthanhthanglong.vn`), Tour Đêm Văn Miếu 3D Mapping (`T4, T7, CN`, `vanmieu.gov.vn`).

