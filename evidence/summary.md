# Tổng hợp bằng chứng pain

> Guide bước 1.2 · rubric R1. Số đếm lại được bằng `python evidence/survey/count.py` trên `evidence/survey/results.csv`.

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☐ chưa làm | `evidence/data-mining.md` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ không dùng (đổi sang khảo sát ở CP2) | — |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☑ **31 người đúng vai** (38 phiếu hợp lệ) | `evidence/survey/` |

## 2. Số chính

Khảo sát online, 40 phiếu gốc → 38 hợp lệ (loại 1 phiếu thử form, 1 phiếu kể chuyến Đà Lạt) → **31 người từng lên lịch cho nhóm đi chơi một ngày ở Hà Nội trong 3 tháng qua** (mẫu số mọi % dưới đây).

- **23/31 (74%)** gặp ít nhất một trong: đi vòng vèo, đến nơi đã đóng / chưa mở cửa, điểm đóng đúng hôm đó, bỏ lỡ địa điểm cả nhóm muốn đi — vì lịch tự xếp.
- **18/31 (58%)** đến nơi đã đóng / chưa mở cửa hoặc gặp điểm đóng đúng hôm đó.
- 14/31 (45%) đi vòng vèo · 14/31 (45%) xếp quá nhiều điểm nên phải bỏ giữa chừng · 14/31 (45%) cả nhóm khó thống nhất chọn nơi nào · 12/31 (39%) mất quá nhiều thời gian chỉ để lên lịch.
- Thời gian tìm + xếp lịch cho một ngày: trung vị **15–30 phút**; chỉ 8/31 (26%) mất ≥ 1 giờ.
- Mức phiền ≥ 4/5: 12/31 (39%).
- Tần suất lên lịch trong 3 tháng: 1 lần 17 · 2–3 lần 11 · ≥ 4 lần 3.
- Công cụ đang dùng: Google Maps 27/31 · TikTok 23/31 · Facebook / group du lịch 18/31 · hỏi bạn bè 16/31 · ChatGPT / chatbot 8/31.

## 3. Trích nguyên văn (phiếu khảo sát, bỏ tên)

1. "Quán đó đã đóng cửa nên buộc phải tính plan khác khi đang di chuyển trên đường" — phiếu S15
2. "Khi cả nhóm đến nơi do không kiểm tra lại lịch, điểm đó đã đóng cửa. Cả nhóm phải chọn tạm 1 chỗ khác gần đấy" — phiếu S19
3. "Nhóm mình định đi ăn rồi tham quan một bảo tàng nhưng đến nơi thì bảo tàng đã ngừng đón khách. Cả nhóm phải thay đổi kế hoạch buổi chiều." — phiếu S23
4. "Nhóm lên plan nhưng mà đi lại tốn thời gian nhiều hơn dự kiến nên buộc phải bỏ 1 địa điểm và chuyển sang địa điểm khác luôn" — phiếu S10
5. "Nhóm mình đi chơi quanh Hồ Tây và phố cổ nhưng không tìm hiểu trước khoảng cách giữa các địa điểm. Cuối cùng mất nhiều thời gian di chuyển, phải bỏ hai địa điểm đã lên kế hoạch." — phiếu S21
6. "mỗi người gửi một link quán trên TikTok vào group chat rồi tự ghép lại. Lúc đi mới phát hiện quán ăn trưa và quán cà phê chiều nằm ngược hẳn hướng nhau" — phiếu S29
7. "Khó nhất là thống nhất địa điểm thấy thế" — phiếu S11

## 4. Các nguồn có khớp nhau không

Chỉ có một nguồn (khảo sát). Câu chọn nhiều (đếm được) và câu kể tự do khớp nhau: các câu kể lặp lại hai kiểu sự cố — **đến nơi đóng cửa** và **đi xa / vòng nên phải bỏ điểm**. Chưa kiểm chéo bằng data hành vi (đào review công khai chưa làm) — đây là giới hạn của bằng chứng.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`:
- Vế 1 (≥ 60% từng đi vòng / đến ngoài giờ / bỏ lỡ): **đúng** — 23/31 (74%).
- Vế 2 (thời gian lên lịch trung vị ≥ 1 giờ): **sai** — trung vị 15–30 phút.
→ **Phải đổi trọng tâm**: chỗ đau là lịch **hỏng tại chỗ** (đóng cửa, đi vòng, phải bỏ điểm), không phải thời gian ngồi lên lịch. Lát cắt giữ nguyên, metric ưu tiên đúng giờ mở cửa và ít đi vòng.
- Cách giải thích khác có cơ sở: 14/31 (45%) nói cả nhóm khó thống nhất — lý do đưa bước quẹt chọn chung vào sản phẩm.

Điều vẫn chưa biết: số lần sự cố mỗi chuyến và thời gian mất cho mỗi sự cố (khảo sát không hỏi); mẫu thiên về 22–30 tuổi (16/31) và dưới 22 (11/31); chưa có data hành vi kiểm chéo.
