# TripSwipe — Nhận diện thương hiệu

## Ý tưởng

Một nhóm bạn quẹt chung một xấp thẻ, và xấp thẻ đó thành một con đường trong ngày. Logo là hai lá bài chồng lệch (lá sau nghiêng như đang bị quẹt đi), lá trước mang một đường đi ngắn nối từ chấm xuất phát tới chấm đích. Quẹt → lộ trình, trong một hình.

## Tên và logo

- Viết đúng **TripSwipe**: một từ, hai chữ hoa T và S. Không viết "Trip Swipe", "TRIPSWIPE", "Tripswipe".
- File: `app/static/brand/mark.svg` (biểu tượng), `wordmark.svg` (biểu tượng + chữ), `favicon.svg` (biểu tượng trên nền tối, bo góc).
- Kích thước tối thiểu của biểu tượng: 16px (favicon). Trên thanh trên cùng dùng 28px kèm chữ "TripSwipe" bằng Inter 600.
- Khoảng trống quanh logo ≥ ¼ chiều cao biểu tượng. Không đổi màu lá ngọc, không xoay, không thêm bóng hay viền.
- Chỉ dùng trên nền tối (`--ground`, `--surface`). Lá sau `#3a3835` sẽ chìm trên nền sáng; app chưa có chế độ sáng (xem bên dưới).

## Màu (token trong `app/static/base.css`)

| Token | Hex | Vai trò | Tương phản trên `--ground` |
|---|---|---|---|
| `--ground` | `#0e0d0c` | Nền trang, đen ấm | — |
| `--surface` | `#181716` | Panel, thẻ | — |
| `--raised` | `#2a2927` | Hover, khối nổi | — |
| `--rule` | `#23211f` | Vạch chia trong danh sách | trang trí |
| `--text` | `#ffffff` | Chữ chính, nút chính | 19.4:1 |
| `--muted` | `#b4b4b4` | Chữ phụ | 9.4:1 |
| `--faint` | `#949494` | Ghi chú nhỏ | 6.4:1 |
| `--accent` | `#5fd3a6` | Ngọc Hồ Gươm: dữ liệu lộ trình (số điểm, đường đi, thanh tiến độ), logo | 10.5:1; chữ đen trên ngọc 11.4:1 |
| `--positive` | `#5fd3a6` | Mở cửa, xong | như trên |
| `--negative` | `#e5566f` | Đóng cửa, vượt ngân sách, lỗi | 5.4:1 |
| `--warning` | `#e5a93b` | Chưa có dữ liệu giờ, dữ liệu mẫu | 9.3:1 |

Giữ màu ngọc đã có: nó là mặt hồ Hoàn Kiếm, điểm xuất phát mặc định, và đọc rõ cả khi chiếu máy. Ngọc chỉ cho dữ liệu và logo, không phủ lên nút hay điều hướng; nút chính là trắng trên đen.

**Chế độ sáng:** chưa làm. Demo chiếu trong phòng và các trang đã dựng cho nền tối; thêm bộ token sáng khi có nhu cầu dùng ngoài trời.

## Chữ

Một họ chữ: **Inter** (Google Fonts, 400/500/600), số dạng bảng (`tabular-nums`) để giờ và phút thẳng cột.

| Token | Cỡ | Dùng cho |
|---|---|---|
| `--fs-display` | 40px | Mã nhóm trên bảng tổng quan |
| `--fs-title` | 24px | Tiêu đề trang (h1) |
| `--fs-sub` | 18px | h2, dòng chuyến đi |
| `--fs-section` | 16px | Tiêu đề mục, giờ ghé |
| `--fs-body` | 14px | Nội dung |
| `--fs-small` | 12px | Nhãn, ghi chú "ước tính" |

## Khoảng cách, bo góc

- Bậc 4px: `--s-1` 4 · `--s-2` 8 · `--s-3` 12 · `--s-4` 16 · `--s-5` 24 · `--s-6` 32 · `--s-7` 48.
- `--radius-card` 20px (thẻ, panel, bản đồ — gợi lá bài), `--radius-inner` 12px (khối trong panel, ô nhập), `--radius-control` 999px (nút, pill).
- Bề mặt tách nhau bằng bước tông nền, không dùng bóng; chỉ lớp thật sự nổi (chi tiết thẻ) có bóng.

## Biểu tượng

SVG tự vẽ, nét 2px đầu tròn, khối bo góc đồng bộ với logo. Không dùng emoji hay ký tự Unicode thay icon. Marker bản đồ là vòng tròn ngọc có số thứ tự; điểm xuất phát là vòng trắng chữ "XP".

## Giọng văn

- Tiếng Việt, xưng "bạn", câu ngắn, thân thiện như một người bạn trong nhóm đi chơi.
- **Trung thực về độ chắc chắn.** Mọi thời gian đi kèm "ước tính". Không có giờ mở cửa thì ghi "chưa có dữ liệu giờ", không đoán. Không có đường thật thì ghi "đường ước tính". Dữ liệu mẫu luôn có nhãn "Dữ liệu mẫu".
- Nút gọi đúng hành động: "Xếp lịch", "Duyệt lịch", "Sao chép", "Ghim". Không "Bắt đầu ngay!", không chấm than.
- Lỗi nói vấn đề và cách sửa: "Không tìm thấy nhóm." / "Không kết nối được máy chủ, hãy thử lại."
- Điểm bị bỏ luôn có lý do và gợi ý: "Đóng cửa vào ngày đi — gợi ý đổi sang ngày khác."
