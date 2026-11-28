# Reflection — Vũ Tiến Hùng

> Làm ở guide bước 5.3. Bản nháp: câu 1 và 2 chép từ việc đã làm (có commit / file), **câu 3 để trống cho Hùng tự viết** (bài học cá nhân, không để AI viết hộ).

1. Vai trò + phần mình làm (trỏ tới file / commit):
   Vai BA / kiểm thử / tài liệu, nộp checkpoint.
   - BA1: soạn và gửi form khảo sát người từng lên lịch đi chơi một ngày ở Hà Nội cho nhóm (link ở sheet nhóm). Kết quả 31 người do Bảo đếm lại trong `evidence/summary.md`.
   - BA2: đào review công khai App Store — `evidence/data-mining.md`, `evidence/fetch_reviews.py`, `evidence/count.py` (commit `0723380`): 20/922 (2,2%) review kể đúng vấn đề; không đạt ngưỡng 60% nên chỉ dùng tham khảo.
   - BA3 (phần kiểm giờ mở cửa 6 địa điểm từ trang chính thức, ghi ở tab "Tài nguyên" STT 8 của sheet nhóm, chưa đưa vào repo).
   - BA5: `canvas.md`, `spec.md` §7 bản dự thảo (commit `1bfef4e`; chuẩn "đạt" cuối cùng trong form CP2 là 75%, Bảo đã khớp lại trong `spec.md`).
   - D6: `spec.md` §8 §9 (commit `41faf19`) và `demo-slides.pdf` 8 trang (commit `44ee65d`).
   - Chưa làm xong khi viết bản nháp này: D4 (5 câu lạ chạy CLI — cần `.env`), D5, D7, X1.

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
   Công cụ: Claude Code. Dùng để viết script tải và đếm review, dựng form khảo sát bằng Apps Script, kiểm giờ mở cửa ở trang chính thức, soạn nháp slide và `spec.md` §8 §9 từ file của nhóm (khai ở `docs/ai-usage.md`). Chỗ phải sửa lại:
   - Đếm review bằng từ khoá ra 99/922 nhưng nhiễu ("close to awesome" bị tính là giờ đóng cửa) → phải đọc từng ứng viên, kết quả đúng là 20/922.
   - Ba file dataset du lịch tìm được: một file không có Hà Nội, một file là dữ liệu giả → không dùng.
   - Chuẩn "đạt" AI đề xuất 80% khác con số đã nộp (75%) → khớp lại về 75% để không bị coi là sửa chuẩn sau CP2.
   - Lăng Bác: giờ và ngày nghỉ viếng chỉ có từ báo, các nguồn chưa thống nhất → để mức "thứ cấp", không coi là đã kiểm.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
   **[Hùng tự viết 3–6 dòng.]** Gợi ý chỉ để chọn câu: B03 (trượt cả 4 lượt, thời lượng tham quan cố định 90 phút), B19 lượt 3 (xếp vào giờ đóng cửa trưa vì `parse_hours()`), hoặc 8 câu timeout ở lượt 1. Xem `eval/report.md` mục 2–3.
