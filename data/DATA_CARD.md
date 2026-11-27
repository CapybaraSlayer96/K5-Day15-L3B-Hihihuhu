# Data card — dữ liệu bản chạy thử dùng

> Bản đầu (CP2) cho ứng dụng lập lịch trình du lịch kiểu quẹt thẻ (Tinder-style), tập trung bản chạy thử tại **Hà Nội** và mở rộng 11 tỉnh/thành. Toàn bộ dữ liệu chạy thử lưu trong thư mục `data/`.

---

## Dataset 1 · `data/hanoi_places.json` (Bộ POI Hà Nội chi tiết — dữ liệu chạy thử chính)

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

---

## Dataset 2 · `data/friend_hanoi_raw.csv` (Danh sách quán ăn & cà phê Hà Nội từ thành viên nhóm)

| | |
|---|---|
| **Dùng để làm gì** | Nguồn bổ sung các quán ăn, cà phê, bar bản địa thực tế (được giới trẻ Hà Nội đánh giá) để hợp nhất vào `data/hanoi_places.json` |
| **Từ đâu** | Bảng tính tổng hợp cá nhân của thành viên nhóm (trích lọc từ file `.xlsx`, không chứa dữ liệu cá nhân người dùng) |
| **Xử lý những bước gì** | Chuẩn hóa địa chỉ & tên thương hiệu · loại 21 dòng thiếu giờ mở cửa/giá/ngoài Hà Nội (Nam Định, Hưng Yên)/lỗi giờ Excel `1899`/trùng lặp/nghi đóng cửa · đối chiếu tọa độ qua Photon API (script: `build_hanoi_dataset.py`) |
| **Số dòng / số đoạn** | **64 dòng đầu vào** -> giữ **43 dòng đạt chuẩn** (loại 21 dòng) |
| **Phiên bản / ngày lấy** | `v1.0` · `2026-11-27` |
| **Nhãn** | **Thật** (địa chỉ, khung giờ, khoảng giá do người đi thực tế ghi nhận) |
| **Giới hạn** | Thiếu trường `closed_days` chính thức và một số quán trong ngõ nhỏ không có đánh giá chuẩn hóa từ nguồn chính thống; chưa kiểm chứng lại trực tiếp tại quán với toàn bộ 43 dòng (chỉ xác thực tồn tại địa chỉ/phố qua Photon). |

---

## Dataset 3 · `data/enriched_places.json` (Bộ POI mở rộng 11 tỉnh/thành — phục vụ mở rộng toàn quốc)

| | |
|---|---|
| **Dùng để làm gì** | Dữ liệu mở rộng toàn quốc (11 tỉnh trọng điểm: Hà Nội, Lâm Đồng, Ninh Bình, TP. HCM, Cần Thơ, Phú Thọ, Vĩnh Long, Khánh Hòa, Đà Nẵng, Lào Cai, An Giang) để kiểm thử khả năng scale đa tỉnh |
| **Từ đâu** | File gốc `places.csv` (315 dòng, 34 tỉnh) + làm giàu nội dung & sinh Micro-POIs bằng **Gemini API (`gemini-3.5-flash-lite`)** + xác thực tọa độ qua **Photon Geocoding API** |
| **Xử lý những bước gì** | Gom batch theo tỉnh (≤ 5 RPM, lưu checkpoint `data/checkpoint.json`) · phân loại `category` · đối chiếu tọa độ Photon & lọc bán kính ≤ 150 km quanh tâm tỉnh · loại 23 Micro-POIs không xác thực được trên OSM · sửa 8 tọa độ Bước A lệch tỉnh (`--fix-outliers`) · kiểm định tự động ra `data/audit_report.json` (script: `build_dataset.py`) |
| **Số dòng / số đoạn** | **178 POI** (`135` gốc từ `places.csv` + `43` Micro-POIs xác thực qua Photon; loại `23` Micro-POIs ảo) |
| **Phiên bản / ngày lấy** | `v1.0` · `2026-11-27` |
| **Nhãn** | **Thật** (135 địa danh gốc + tọa độ Photon) · **`synthetic`** (trường `why_visit`, `what_to_do`, `best_time_of_day`, `ideal_season` và 43 Micro-POIs sinh bởi LLM) |
| **Giới hạn** | Mới chạy 11/34 tỉnh (`--all` để mở rộng đủ 34 tỉnh); gói miễn phí không mở Google Search Grounding nên phần Micro-POIs chưa có link review trích dẫn tự động; 9/178 điểm Bước A dùng tọa độ ước lượng do Photon không khớp. |

**Data `synthetic` (nhóm tự sinh):**
- **Cách sinh:** Script `build_dataset.py` (prompt chuẩn hóa JSON theo từng tỉnh, model `gemini-3.5-flash-lite`, `temperature=0.3`, không dùng seed cố định).
- **Kiểm chứng:** Kiểm tự động 100% qua `audit_dataset()` (`data/audit_report.json`: `PASS`, `0` lỗi, `1` cảnh báo hợp lệ là Côn Đảo xa bờ 234 km); kiểm tay mẫu Hà Nội (11/11 dòng) và phát hiện 1 điểm lệch tọa độ (`Xôi Cầu Gỗ`) nên đã tách riêng bộ Hà Nội chuẩn hóa thủ công (`Dataset 1`). Data tự sinh **không dùng làm bằng chứng pain của người dùng**.
