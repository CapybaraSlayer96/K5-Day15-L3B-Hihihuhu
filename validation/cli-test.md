# D4 — Kiểm thử CLI bằng 5 câu lạ (CP4, hạn 11:00 Thứ Bảy 28/11)

> Người làm: Hùng (BA / tester). Mục đích: tìm lỗi bằng câu **chưa có trong `eval/benchmark.csv`** (22 câu B01–B22), không sửa câu cũ.
> **Kỳ vọng viết TRƯỚC khi chạy** (cột "Kỳ vọng"), để không chỉnh cho khớp output. Cột "Output" và "Đúng / sai" chỉ điền sau khi chạy `python run.py`.
> Chạy bằng model thật (cần `.env` của nhóm — xin Bảo/Hải; KHÔNG commit `.env`, không dán key vào chat). Chạy bằng model giả không có giá trị cho D4.
> Câu nào sai → báo Hải. Câu hay có thể **thêm** vào bộ thử (`source: tu_viet`), không sửa câu cũ.

Cách chạy: `python run.py` → gõ từng câu ở dưới → chép nguyên văn output + dòng `(model … token vào / ra)` vào bảng. Token phải > 0 mới tính là chạy thật.

| # | Loại | Input (gõ nguyên văn) | Kỳ vọng (viết trước) | Vì sao câu này khó |
|---|---|---|---|---|
| L1 | Ngày lễ | `Mùng 2 tháng 9 nhóm mình 4 người đi 8:00–16:00, xuất phát Hồ Gươm, muốn viếng Lăng Bác và vào Nhà tù Hỏa Lò.` | Không khẳng định lịch viếng Lăng ngày lễ nếu công cụ không có dữ liệu ngày lễ; hỏi thứ mấy (vì Lăng nghỉ thứ Hai, thứ Sáu theo dữ liệu thường ngày) hoặc nêu rõ giả định; không bịa giờ | Ngày dương lịch không phải thứ trong tuần; ngày lễ có thể khác lịch thường |
| L2 | Ngoại thành | `Chủ nhật nhóm mình đi Chùa Hương rồi sang làng gốm Bát Tràng trong một ngày, xuất phát từ Hồ Gươm.` | Nói sản phẩm chỉ xếp lịch một ngày trong nội thành Hà Nội; không xếp lịch ngoại thành; đề nghị đổi sang điểm nội thành | Hai điểm có trong dữ liệu nhưng ngoài phạm vi (spec §5 lớp 3) |
| L3 | Sai dấu | `thu bay nhom minh di van mieu quoc tu giam roi bao tang dan toc hoc, tu 9h den 16h, bat dau tu ho guom` | Hiểu đúng "thứ Bảy", hai điểm và khung giờ; trả lịch hợp lệ (Văn Miếu 08:00–17:00 mở thứ Bảy; Dân tộc học 08:30–17:30 mở thứ Bảy), hoặc hỏi lại đúng một chi tiết; không bịa điểm khác | Không dấu, tên địa điểm viết sai chuẩn |
| L4 | Khung giờ qua trưa | `Thứ Tư mình rảnh từ 11:30 đến 14:30, xuất phát Cầu Giấy, muốn vào Bảo tàng Hồ Chí Minh và Chùa Một Cột.` | Không xếp Bảo tàng Hồ Chí Minh trong giờ nghỉ trưa 12:00–14:00; nói rõ điểm nào xếp được, điểm nào không và vì sao; nếu Chùa Một Cột không có giờ trong dữ liệu thì nói chưa có dữ liệu, không bịa giờ | Khung giờ cắt ngang giờ nghỉ trưa của bảo tàng |
| L5 | Đặt bàn lẫn trong câu dài | `Chủ nhật nhóm mình 6 người, tụi mình hay đi trễ lắm và thích chụp ảnh, đi từ 8:00 đến 18:00, xuất phát Hồ Gươm, muốn đi Văn Miếu, Hoàng thành Thăng Long và Hỏa Lò, trưa giúp mình đặt luôn bàn bún chả lúc 12:00 nhé, cuối ngày mình tự xem múa rối.` | Từ chối phần đặt bàn (không nói "đã đặt"); vẫn xếp ba điểm hợp lệ; có thể gợi ý khung trưa để nhóm tự đặt; không bị câu dài làm mất ràng buộc giờ | Yêu cầu ngoài phạm vi chen giữa thông tin thừa |

## Kết quả

Chạy lúc: 13:05 28/11/2026 · model: `gpt-4.1-mini` (qua proxy OpenAI-compatible, token > 0 ở cả 5 câu) · `main` tại `21db060` · lệnh: `python run.py`, gõ lần lượt 5 câu. Không sửa code, không sửa `eval/benchmark.csv`.

| # | Output (tóm tắt nguyên văn) | Token > 0? | Đúng / sai | Vì sao | Báo Hải? |
|---|---|---|---|---|---|
| L1 | "Lịch **Chủ nhật**, 08:00–16:00, xuất phát Hồ Gươm, xe máy: 08:10–10:10 Lăng Chủ tịch Hồ Chí Minh · 10:18–11:48 Nhà tù Hỏa Lò". Không hỏi lại, không nói giả định về ngày. *(2756 vào / 122 ra)* | Có | **Sai** | Đầu vào chỉ có "Mùng 2 tháng 9", không có thứ trong tuần. Hệ thống tự đọc thành Chủ nhật và trả lịch, trái PRD ("thiếu ngày đi → chỉ hỏi lại, không trả lịch") và kỳ vọng của tôi. Vì Lăng đóng thứ Hai / thứ Sáu, đoán sai ngày là đúng loại lỗi đắt nhất (`spec.md` §5 lớp 2, 4) | **Có** |
| L2 | "Bạn chưa nói khung giờ — mình tạm tính 08:00–17:00. Không xếp được: Chùa Hương (ngoài phạm vi nội thành), Làng gốm Bát Tràng (ngoài phạm vi nội thành). Gợi ý: đổi sang ngày khác, nới khung giờ, hoặc bỏ bớt điểm." Lịch rỗng. *(2580 / 75)* | Có | **Đúng một phần** | Không xếp ngoại thành, nêu đúng lý do, nói rõ giả định khung giờ. Nhưng **gợi ý chung chung** ("đổi ngày, nới khung giờ") không hợp với lý do ngoại thành, không đề nghị chọn điểm nội thành như kỳ vọng | Có (nhẹ) |
| L3 | "Lịch Thứ Bảy, 09:00–16:00, xuất phát Hồ Gươm: 09:09–10:39 Văn Miếu · 10:56–12:56 Bảo tàng Dân tộc học". *(2748 / 121)* | Có | **Đúng** | Đọc đúng "thu bay" = thứ Bảy, hai điểm và khung giờ dù gõ không dấu; cả hai điểm mở thứ Bảy, giờ nằm trong giờ mở | Không |
| L4 | "Lịch Thứ Tư, 11:30–14:30, xuất phát Cầu Giấy (xấp xỉ): 11:48–12:28 Chùa Một Cột · *chưa có dữ liệu giờ mở cửa, kiểm lại trước khi đi*. Không xếp được: Bảo tàng Hồ Chí Minh — khung mở cửa trùng khung giờ nhóm quá ngắn (cần 60 phút)". *(2708 / 100)* | Có | **Đúng** | Không xếp Bảo tàng Hồ Chí Minh vào giờ nghỉ trưa, không bịa giờ cho Chùa Một Cột mà ghi rõ chưa có dữ liệu. Lý do nói "khung quá ngắn" thay vì "nghỉ trưa" nhưng đúng về nội dung | Không |
| L5 | Mở đầu "Mình chỉ xếp lịch, không đặt vé, đặt bàn hay thanh toán…". Lịch Chủ nhật 08:00–18:00: **08:06–08:56 Bún Chả Hương Liên** · 09:30–10:20 **Nhà hát Múa rối** · 10:25 Hỏa Lò · 12:01 Văn Miếu · 13:37 Hoàng thành. *(2909 / 194)* | Có | **Đúng một phần** | Từ chối đặt bàn đúng; ba điểm người dùng muốn (Hỏa Lò, Văn Miếu, Hoàng thành) xếp hợp lệ, trong giờ mở. Nhưng **tự thêm hai điểm** không nằm trong "muốn đi": bún chả xếp lúc 08:06 thay vì trưa 12:00 người dùng nhắc, và múa rối dù người dùng nói "tự xem". Cùng nhóm lỗi "tự thêm địa điểm" ở B13 (`eval/report.md` mục 2) | Có |

**Tổng kết:** đúng 2/5 (L3, L4) · đúng một phần 2/5 (L2, L5) · sai 1/5 (L1). Cả 5 câu chạy bằng model thật (token > 0). Không câu nào vi phạm giờ mở cửa (chuẩn cứng `dung_gio_mo_cua`), nhưng L1 đoán sai ngày đi mà không hỏi.

**Lỗi lặp lại:** (1) đọc ngày đi: câu chỉ có ngày dương lịch / ngày lễ bị gán một thứ trong tuần (L1); (2) tự thêm địa điểm không được yêu cầu khi câu dài có nhắc quán / hoạt động (L5, giống B13).

**Câu đáng thêm vào `eval/benchmark.csv`** (`source: tu_viet`, chỉ thêm, không sửa câu cũ — việc của người sở hữu bộ câu thử, tôi chưa thêm): L1 (ngày dương lịch, không có thứ) và L5 (đặt bàn lẫn trong câu dài). Hai câu này **chưa nằm trong bộ 22 câu** nên không làm đổi số lượt đã chạy.
