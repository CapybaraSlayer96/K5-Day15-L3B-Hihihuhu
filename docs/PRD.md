# TripSwipe — PRD (MVP hackathon)

> Bản 28/11/2026, chốt qua phiên grilling. Phạm vi: chỉ MVP hackathon, chạy hoàn toàn localhost bằng docker compose. Thiết kế chi tiết: [ARCHITECTURE.md](ARCHITECTURE.md) · bài toán, bằng chứng, chỗ khó, chuẩn "đạt": [spec.md](../spec.md).

## Problem Statement

Nhóm bạn đi chơi tự túc một ngày ở Hà Nội. Một người nhận việc lên lịch: tìm và đối chiếu thông tin từ Google Maps, TikTok, review để chọn địa điểm, hỏi cả nhóm qua group chat, rồi tự xếp thứ tự. Kết quả là các điểm xa nhau, đi vòng, đến nơi thì đã đóng hoặc chưa mở cửa, phải bỏ điểm giữa chừng; cả nhóm khó thống nhất chọn nơi nào. Khảo sát (16 phản hồi, 12 người từng lên lịch): 9/12 gặp đi vòng / đến nơi đã đóng / bỏ lỡ địa điểm; 6/12 đến nơi đã đóng hoặc chưa mở; 6/12 nói cả nhóm khó thống nhất. Thời gian lên lịch không dài (trung vị 15–30 phút) — chỗ đau là **lịch hỏng tại chỗ** và **chọn chung**.

## Solution

Trưởng nhóm tạo nhóm trên web, trả lời vài câu cấu hình (tỉnh, phạm vi, ngày đi, khung giờ, điểm xuất phát, budget cả nhóm, phương tiện). Hệ thống lọc địa điểm hợp lệ, AI chọn 20 thẻ hợp sở thích. Mỗi thành viên vào bằng mã nhóm + biệt danh, quẹt thích / bỏ qua từng thẻ (vuốt lên xem chi tiết). Trưởng nhóm bấm "Xếp lịch": hệ thống gộp phiếu theo trung bình, code xếp thứ tự và giờ theo giờ mở cửa, thời gian di chuyển, budget; trả lịch từng khung giờ trên bản đồ, kèm danh sách điểm bị bỏ và lý do. Trưởng nhóm duyệt, sửa (bỏ / ghim điểm, tính lại), sao chép lịch gửi nhóm.

## User Stories

**Tạo nhóm và cấu hình**
1. As a trưởng nhóm, I want tạo nhóm không cần tài khoản, so that bắt đầu ngay.
2. As a trưởng nhóm, I want chọn tỉnh từ danh sách, so that hệ thống biết nơi đi; chỉ Hà Nội được bật, tỉnh khác ghi "sắp có".
3. As a trưởng nhóm, I want chọn phạm vi nội thành / ngoại thành, so that thẻ không quá xa; chỉ nội thành được bật.
4. As a trưởng nhóm, I want nhập ngày đi, so that hệ thống biết điểm nào đóng cửa hôm đó.
5. As a trưởng nhóm, I want nhập giờ bắt đầu và giờ kết thúc, so that lịch nằm trong khung nhóm rảnh.
6. As a trưởng nhóm, I want chọn điểm xuất phát (từ danh sách điểm có sẵn hoặc toạ độ), so that chặng đầu tính đúng.
7. As a trưởng nhóm, I want nhập budget cả nhóm, so that lịch không vượt tiền nhóm có.
8. As a trưởng nhóm, I want chọn một phương tiện cho cả ngày (xe máy / ô tô / đi bộ), so that thời gian di chuyển sát thực tế.
9. As a trưởng nhóm, I want nhận mã nhóm và link chia sẻ, so that gửi cho bạn bè vào quẹt.
10. As a trưởng nhóm, I want bị chặn khi thiếu ngày đi, so that không có lịch dựa trên ngày tự đoán.

**Vào nhóm và quẹt**
11. As a thành viên, I want vào nhóm bằng mã / link và biệt danh, so that không phải đăng ký.
12. As a thành viên, I want thấy thẻ tổng quan (ảnh, tên, loại, quận, câu mô tả ngắn, tag, khoảng giá, rating, mở hay đóng vào ngày đi), so that quyết định nhanh.
13. As a thành viên, I want vuốt lên để xem chi tiết (mô tả, lý do nên đi, nên làm gì, giờ mở cả tuần, ngày đóng, thời lượng, mẹo, tóm tắt review, địa chỉ, link bản đồ, nguồn xác minh), so that hiểu kỹ trước khi chọn.
14. As a thành viên, I want kéo thẻ sang phải để thích, sang trái để bỏ qua, so that chọn như Tinder.
15. As a thành viên, I want có nút bấm thay cho kéo, so that dùng chuột dễ.
16. As a thành viên, I want hoàn tác lượt quẹt vừa rồi, so that sửa khi lỡ tay.
17. As a thành viên, I want thấy lý do AI gợi ý thẻ này, so that biết vì sao nó hợp nhóm.
18. As a thành viên, I want thấy nhãn "chưa có dữ liệu giờ" trên thẻ thiếu giờ, so that không tin nhầm.
19. As a thành viên, I want thấy mình còn bao nhiêu thẻ, so that biết sắp xong chưa.

**Phòng chờ và gộp phiếu**
20. As a thành viên, I want thấy ai đã quẹt xong, so that biết khi nào đủ.
21. As a trưởng nhóm, I want bấm "Xếp lịch" bất cứ lúc nào, so that không phải chờ người chậm; chỉ tính phiếu của người đã quẹt.
22. As a trưởng nhóm, I want thẻ được tính theo trung bình phiếu (thích = 1, bỏ qua = 0, cần ≥ 0,5), so that lịch theo ý số đông.
23. As a trưởng nhóm, I want ghim điểm bắt buộc, so that điểm quan trọng không bị bỏ.
24. As a thành viên, I want trang tự cập nhật tiến độ, so that không phải tải lại.

**Lịch trình**
25. As a trưởng nhóm, I want lịch dạng dòng thời gian: mỗi điểm có giờ đến, giờ rời, chặng di chuyển, so that cả nhóm biết đi lúc nào.
26. As a trưởng nhóm, I want mọi điểm trong lịch nằm trong giờ mở cửa của đúng thứ ngày đi, kể cả giờ nghỉ trưa, so that không đến nơi đóng cửa.
27. As a trưởng nhóm, I want lịch tôn trọng giờ theo mùa (vd Lăng Bác mùa lạnh), so that không lệch giờ.
28. As a trưởng nhóm, I want thứ tự ít đi vòng, so that tiết kiệm thời gian di chuyển.
29. As a trưởng nhóm, I want hệ thống tự chèn slot ăn trưa / tối khi khung giờ trùm giờ ăn, lấy từ quán được thích, so that không quên ăn.
30. As a trưởng nhóm, I want thấy chi phí ước tính mỗi người so với budget mỗi người, so that biết có vượt không.
31. As a trưởng nhóm, I want điểm không có giá được ghi "chưa có giá", không cộng vào tổng, so that không tin con số bịa.
32. As a trưởng nhóm, I want danh sách điểm bị bỏ, mỗi điểm có lý do (đóng hôm đó / ngoài giờ mở / không đủ thời gian / vượt budget) và gợi ý nới (đổi ngày, nới giờ, tăng budget, bỏ điểm), so that quyết định tiếp.
33. As a trưởng nhóm, I want một lời giải thích ngắn vì sao chọn từng điểm, so that thuyết phục nhóm.
34. As a trưởng nhóm, I want xem lịch trên bản đồ, so that hình dung cung đường.
35. As a trưởng nhóm, I want thời gian di chuyển gắn nhãn "ước tính", so that biết không phải thời gian thực.
36. As a trưởng nhóm, I want bỏ hoặc ghim điểm rồi tính lại, so that chỉnh theo ý nhóm.
37. As a trưởng nhóm, I want bản cũ bị đánh dấu hết hiệu lực sau mỗi lần tính lại, so that không gửi nhầm.
38. As a trưởng nhóm, I want duyệt lịch, so that chốt bản cuối.
39. As a trưởng nhóm, I want sao chép lịch dạng văn bản kèm nguồn giờ mở cửa, so that dán vào group chat.

**Giới hạn và an toàn**
40. As a người dùng, I want hệ thống từ chối đặt vé, đặt bàn, thanh toán và nói rõ chỉ xếp lịch, so that không hiểu nhầm.
41. As a người dùng, I want yêu cầu nhiều ngày hoặc ngoài Hà Nội bị từ chối kèm đề nghị xếp một ngày ở Hà Nội, so that biết phạm vi.
42. As a người dùng, I want hệ thống không làm theo yêu cầu bỏ qua giờ mở cửa hay tin tự xưng "admin", so that lịch vẫn đúng.
43. As a người dùng, I want thấy cảnh báo khi xếp điểm chưa có dữ liệu giờ, so that tự kiểm trước khi đi.
44. As a người dùng, I want hệ thống báo rõ khi dịch vụ AI lỗi, so that không nhận lịch nửa vời.

**Đường văn bản (eval, CLI)**
45. As a người chấm, I want gõ yêu cầu bằng văn bản ("thứ Bảy, Hồ Gươm, 8–17h, muốn đi A, B, C") và nhận lịch, so that chạy bộ câu thử không cần giao diện.
46. As a người chấm, I want thiếu ngày đi thì nhận câu hỏi lại, không nhận lịch, so that đúng chuẩn "đạt".
47. As a người chấm, I want chạy eval không cần Postgres hay internet, so that clone về là chạy được.
48. As a nhóm phát triển, I want mọi lần gọi model và công cụ có trace, token, so that tính chi phí.

## Implementation Decisions

**Hình dạng và vai AI**
- Workflow cố định, một lõi dùng chung cho web và đường văn bản. AI chỉ ở hai chỗ: (1) đọc yêu cầu / sở thích → cấu hình + danh sách ID địa điểm, hoặc chọn và xếp hạng 20 thẻ từ danh sách ứng viên đã lọc, kèm lý do; (2) viết câu "lý do chọn" từng điểm và lời nhắn khi không xếp được.
- AI **không** tự sắp giờ, không viết số. Giờ, giá, thời gian di chuyển do code điền vào khuôn. Code loại mọi ID AI trả về không có trong danh sách ứng viên.
- Model mặc định Gemini Flash (gói miễn phí); hỗ trợ đổi nhà cung cấp qua cấu hình môi trường. Token lấy từ `usage` của API.

**Lõi (giữ hợp đồng khung BTC)**
- Điểm vào `answer(text) → {"output": str}` giữ nguyên. Luồng văn bản: LLM rút cấu hình + ID → code kiểm thiếu thông tin (thiếu ngày đi → hỏi lại, dừng; thiếu điểm xuất phát → giả định nói rõ) → kiểm phạm vi (nhiều ngày, ngoài Hà Nội, đặt vé → từ chối phần đó) → bộ xếp lịch → bộ kiểm → khuôn output + lý do từ LLM.
- Bốn công cụ có `@tool`, chỉ đọc: tra địa điểm, tra giờ mở cửa theo ngày, ước thời gian đi giữa hai điểm, kiểm lịch (trả danh sách vi phạm).
- Mô-đun giờ mở cửa: chuẩn hoá chuỗi `opening_hours` + `closed_weekdays` (0 = thứ Hai) thành lịch theo từng thứ, nhiều khung / ngày (nghỉ trưa), có bộ giờ theo mùa chọn theo ngày đi. Chuỗi không đọc được → "chưa có dữ liệu giờ": vẫn cho quẹt, xếp thì gắn cảnh báo, không tính là đã kiểm.
- Bộ xếp lịch: mục tiêu theo thứ tự — đủ điểm ghim → tổng điểm thích cao nhất → ít thời gian di chuyển nhất. ≤ 8 điểm vét cạn; nhiều hơn chèn tham lam + 2-opt. Thời gian ở mỗi điểm lấy `estimated_duration_mins`, thiếu thì 60 phút gắn "ước tính". Tự chèn slot ăn trưa (trùm 11:00–13:00) và ăn tối (trùm 18:00–20:00) từ quán được thích; không có thì slot "tự chọn".
- Budget: tổng nhóm chia số thành viên đã vào; chi phí mỗi người = tổng `price_max_vnd` của điểm có giá; ràng buộc cứng; điểm không giá không cộng, gắn "chưa có giá".
- Gộp phiếu: điểm = trung bình phiếu của người đã quẹt thẻ đó; vào ứng viên khi ≥ 0,5 và có ≥ 1 phiếu; hoà xếp theo rating; điểm ghim luôn vào.
- Khi không xếp hết: một lịch hợp lệ + danh sách điểm bị bỏ, mỗi điểm một lý do + ≥ 1 gợi ý nới. Không trả nhiều phương án.

**Dữ liệu**
- Nguồn sự thật: file JSON 118 địa điểm Hà Nội. Lệch với nguồn chính thức thì sửa theo nguồn chính thức, ghi vào data card (Hoàng thành mở mọi ngày; Bảo tàng Mỹ thuật đóng thứ Hai; Chùa Một Cột xoá giờ — chưa có nguồn). Văn Miếu ban ngày và tour đêm là hai địa điểm riêng.
- Ma trận thời gian di chuyển: tính trước một lần bằng OSRM (server công cộng FOSSGIS, profile ô tô cho xe máy / ô tô, profile đi bộ cho đi bộ), lưu file JSON trong repo. Thiếu cặp hoặc lỗi mạng → đường chim bay × 1,3 ÷ tốc độ (xe máy 20, ô tô 15, đi bộ 4,5 km/h). Mọi thời gian di chuyển gắn "ước tính". Không gọi API bản đồ lúc người dùng đang dùng.

**Web app**
- Backend Python FastAPI, Postgres 16, giao diện HTML render phía server + JavaScript thuần (quẹt bằng pointer events), bản đồ Leaflet nền OpenStreetMap. Giao diện tiếng Việt, tối ưu cho máy tính.
- Docker compose hai dịch vụ: `db` (Postgres, có volume) và `app` (cổng 8000; khởi động tạo bảng, nạp địa điểm + ma trận từ JSON). Key model đọc từ `.env`. Chỉ chạy localhost.
- Đồng bộ nhóm bằng polling 3 giây.
- Schema (7 bảng):
  - `places(id, name, category, district, lat, lng, price_min_vnd, price_max_vnd, estimated_duration_mins, opening_hours JSONB, closed_weekdays INT[], card JSONB, detail JSONB, source)`
  - `travel_times(from_id, to_id, mode, minutes, source)`
  - `groups(id, code UNIQUE, province, scope, start_label, start_lat, start_lng, trip_date, start_time, end_time, budget_total_vnd, mode, status, created_at)`
  - `members(id, group_id, nickname, is_leader, joined_at)`
  - `deck_cards(group_id, place_id, rank, ai_reason)`
  - `swipes(group_id, member_id, place_id, liked, created_at)` — `UNIQUE(member_id, place_id)`
  - `itineraries(id, group_id, version, status ∈ {draft, approved, stale}, items JSONB, dropped JSONB, total_cost_vnd, model, created_at)`
- API (10 endpoint): `GET /api/config/options` · `POST /api/groups` · `GET /api/groups/{code}` · `POST /api/groups/{code}/members` · `POST /api/groups/{code}/deck` · `GET /api/groups/{code}/deck?member_id=` · `POST /api/groups/{code}/swipes` · `GET /api/groups/{code}/progress` · `POST /api/groups/{code}/itinerary` (chỉ trưởng nhóm) · `PATCH /api/itineraries/{id}` (duyệt / bỏ / ghim → tính lại) · `GET /api/places/{id}`.
- Trang (5): Tạo nhóm (wizard cấu hình) · Vào nhóm (biệt danh) · Quẹt (thẻ tổng quan, vuốt lên xem chi tiết, kéo / nút, hoàn tác) · Phòng chờ (tiến độ, nút "Xếp lịch" cho trưởng nhóm) · Lịch trình (dòng thời gian, bản đồ, điểm bị bỏ, duyệt / sửa, sao chép).
- Tạo bộ thẻ: code lọc theo phạm vi, mở vào thứ của ngày đi và giao với khung giờ, giá trong budget mỗi người → AI chọn và xếp hạng 20 thẻ kèm lý do.

**Thứ tự build** (theo mốc): (1) lõi + `answer(text)` + nối model + ma trận → eval lượt 1, video CLI cho CP3; (2) backend + Postgres + docker compose; (3) 5 trang; (4) mô phỏng chi phí.

## Testing Decisions

- Test chỉ hành vi bên ngoài: đầu vào → lịch / câu hỏi lại / lời từ chối và danh sách vi phạm. Không test hàm nội bộ của bộ tối ưu.
- **Seam 1 — `answer(text)`** (seam có sẵn của khung BTC): bộ câu thử `eval/benchmark.csv` chạy qua `python run.py eval`; chấm bằng 6 metric trong `eval/metric_spec.yaml` (4 metric chấm bằng code đọc lịch có cấu trúc, 2 chấm bằng người). Chuẩn "đạt" ở `spec.md` §7.
- **Seam 2 — HTTP API** của web app: một test end-to-end bằng test client — tạo nhóm → 2 thành viên vào → quẹt → xếp lịch → lịch không vi phạm giờ mở cửa, chi phí ≤ budget mỗi người. Model chạy chế độ giả trong test.
- Bộ kiểm lịch là thứ quyết định đúng sai, nên kiểm thêm một số lịch dựng tay có vi phạm đã biết (đóng thứ Hai, nghỉ trưa, chồng giờ) qua công cụ kiểm lịch.
- Prior art: khung eval / score / simulate có sẵn trong repo; output chạy tay chatbot ở `eval/baseline-chatbot.md` làm mức so sánh.

## Out of Scope

- Mọi thứ ngoài MVP hackathon: tài khoản đăng nhập, triển khai lên internet, tối ưu cho điện thoại.
- Tỉnh khác Hà Nội, ngoại thành, lịch nhiều ngày, lưu trú.
- Đặt vé, đặt bàn, giữ chỗ, thanh toán, tự gửi lịch ra dịch vụ ngoài, chia tiền.
- Dẫn đường, giao thông / thời tiết / hàng đợi thời gian thực; gọi API bản đồ lúc chạy.
- "Siêu thích", trả nhiều phương án lịch, WebSocket.
- Dùng LLM làm nguồn dữ kiện giờ, giá, toạ độ.

## Further Notes

- Bằng chứng: khảo sát đang thu (16/25 phản hồi lúc 19:17 27/11). Số trong Problem Statement cần cập nhật khi đủ mẫu.
- Server OSRM công cộng chỉ dùng cho demo, giới hạn tốc độ gọi; ma trận tính một lần và commit để chạy không cần mạng.
- Ảnh thẻ lấy từ `image_url` (Wikimedia); không có mạng thì hiện ảnh trống.
- Chuẩn "đạt" chốt tại CP2: ≥ 75% câu qua + 100% không vi phạm giờ mở cửa + 0 bịa dữ liệu + 100% câu từ chối qua.
