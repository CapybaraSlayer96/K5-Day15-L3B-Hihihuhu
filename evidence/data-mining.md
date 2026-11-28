# Đào data — cách đếm và kết quả

> Điền ở guide bước 1.2. Ôn lại: ngày 2, ngày 6 · lab ngày 2, lab ngày 6.
> Không đào data thì xoá file này. Script / công thức đếm để trong repo (vd `evidence/count.py` hoặc ghi công thức Sheets ngay dưới), người khác chạy lại phải ra cùng số.
> Repo chỉ chứa số đã tổng hợp và vài dòng ví dụ — không chép lại nguyên file data.

## 1. Cách đếm — viết TRƯỚC khi chạy

> Viết lúc 18:31 27/11/2026, **trước khi tải bất kỳ review nào** (chỉ mới tra danh sách ứng dụng). Người viết: Hùng (với Claude hỗ trợ).

- **Data dùng:** review công khai của 5 ứng dụng lập lịch trình du lịch trên App Store (kho Mỹ, tiếng Anh), lấy bằng **RSS chính thức của Apple** (`itunes.apple.com/us/rss/customerreviews/.../sortby=mostrecent/json`), không scrape giao diện.
- **Chọn ứng dụng (cố định trước khi đọc):** 5 app trong thể loại Travel mà chức năng chính là *dựng lịch trình theo ngày*, lấy từ kết quả tìm "trip planner itinerary" / "travel itinerary planner": **Wanderlog (1476732439) · Tripomatic (519058033) · Tripsy (1429967544) · Rhyme (6748781672) · TripIt (311035142)**. Loại app đi đường bộ (Roadie), nhật ký (Polarsteps), app đặt phòng.
- **Chọn mẫu:** tối đa **200 review mới nhất / app**, **mọi mức sao**, không lọc theo sao hay từ khoá khi tải. Mẫu nghiêng về người dùng thật của loại sản phẩm gần nhất với lát cắt của nhóm.
- **Đếm gì:** số review nói tới ít nhất một trong 3 loại vấn đề đúng với giả thuyết (định nghĩa chốt sau khi đọc thử 30 review, mục 2): **GIO** (giờ mở cửa / địa điểm đóng cửa sai) · **ROUTE** (xếp lịch đi vòng, quãng đường / thời gian di chuyển không hợp lý) · **TIME** (lên lịch tốn công, phải làm tay).
- **Mẫu số (N):** tổng số review đã tải và gắn nhãn, **kể cả review không liên quan** (khen, lỗi kỹ thuật, giá…). Không bỏ review nào trước khi đếm.
- **Script:** `evidence/count.py` (tải bằng RSS, gắn nhãn bằng quy tắc từ khoá ghi trong file, in x/N). Người khác chạy lại phải ra số tương đương (RSS trả review mới nhất nên N có thể xê dịch; số đã chốt lưu kèm ngày tải ở mục 3 và file `evidence/reviews_labeled.csv`).
- **Dữ liệu thô:** `reviews_raw.csv` / `reviews_labeled.csv` (922 review công khai, không có tên người viết) **không đưa vào repo** (guide: repo chỉ chứa số đã tổng hợp). Bản sao: Drive, sheet nhóm tab "Tài nguyên" STT 6–7. Chạy lại: `python -I -X utf8 evidence/fetch_reviews.py` rồi `python -I -X utf8 evidence/count.py` (RSS trả review mới nhất nên N có thể xê dịch).
- **Giới hạn đã biết trước:** review tiếng Anh ở kho Mỹ, không phải người Việt đi Hà Nội; người viết review thường đang bực; ba nhãn gắn bằng từ khoá sẽ bỏ sót cách diễn đạt khác.

## 2. Đọc trước, đếm sau

Tải 922 review lúc 18:45 27/11/2026 (`fetch_reviews.py` → `reviews_raw.csv`; Wanderlog 200 · Tripomatic 200 · Tripsy 200 · TripIt 200 · Rhyme 122, vì Rhyme chỉ có 122 review). Đã đọc **30 review ngẫu nhiên** (xáo bằng seed 27) trước khi định nghĩa nhãn. Các *kiểu* nội dung thấy được:
- Phần lớn là **khen** việc gom lịch trình, nhập đặt chỗ từ email, chia sẻ cho nhóm (~2/3 trong 30 review).
- **Lỗi / giá / đăng ký dùng thử** (không liên quan lát cắt).
- Số ít nói về đúng vấn đề của nhóm: giờ mở cửa, xếp lịch đi vòng / quãng đường vô lý, lên lịch tốn công.

**Định nghĩa nhãn** (một câu mỗi nhãn, để người khác gắn lại ra giống):
- **GIO** — người viết nhắc tới giờ mở cửa / ngày đóng cửa của địa điểm: gặp vấn đề, mong có, hoặc khen tính năng cảnh báo.
- **ROUTE** — người viết nhắc tới thứ tự / quãng đường / thời gian di chuyển trong lịch: gặp vấn đề (đi vòng, tuyến vô lý, xếp sai thứ tự), mong có, hoặc khen tính năng tối ưu.
- **TIME** — người viết nói lập lịch **tốn công / mất thời gian** vì phải làm tay.
- Mỗi review gắn thêm **loại phát ngôn**: `PAIN` (kể mình đã gặp vấn đề hoặc đang thiếu thứ đó) · `KHEN` (khen tính năng đã giải quyết vấn đề, không kể mình từng gặp) · loại khác.

**Đã đổi cách đếm sau khi đọc dữ liệu** (ghi lại để minh bạch): bản đầu gắn nhãn bằng quy tắc từ khoá (`count.py`) ra **99/922 (10,7%)** nhưng **nhiễu nặng**. Ví dụ "close to awesome", "nothing comes close", "efficient" khi nói về app, "closes the app" đều bị tính là GIO / ROUTE. Vì vậy quy tắc từ khoá chỉ dùng để **lọc 99 ứng viên**; sau đó **người đọc từng ứng viên và phán loại** (bảng dưới). Số từ khoá thô giữ ở `reviews_labeled.csv` cột `labels`.

## 3. Kết quả

N = **922** review (mẫu số gồm cả review không liên quan). 99 ứng viên được đọc và phán thủ công; **823 review còn lại không có từ khoá nào nên chưa đọc từng cái** (có thể bỏ sót cách diễn đạt khác → số dưới đây là **cận dưới**).

| Đếm gì (sau khi phán thủ công 99 ứng viên) | x / N | % | Ghi chú |
|---|---|---|---|
| Review nói về **GIO** (mọi loại phát ngôn) | 7/922 | 0,8% | 3 PAIN/mong có · 4 KHEN tính năng cảnh báo đóng cửa. ID dòng: 14, 28, 50, 85 (KHEN); 369, 403, 585 (PAIN) |
| Review nói về **ROUTE** — PAIN / mong có | 8/922 | 0,9% | ID: 212, 220, 235, 267, 306, 504, 604, 697 |
| Review nói về **ROUTE** — KHEN tính năng tối ưu / thời gian di chuyển | 18/922 | 2,0% | ID: 37, 45, 53, 54, 64, 75, 98, 139, 140, 151, 170, 178, 223, 303, 325, 332, 393, 483 |
| Review nói về **TIME** — lập lịch tốn công | 10/922 | 1,1% | ID: 134, 149, 235, 294, 434, 438, 517, 518, 857, 881 (235 trùng với ROUTE) |
| **Tổng review kể PAIN đúng vấn đề của nhóm** (GIO ∪ ROUTE ∪ TIME) | **20/922** | **2,2%** | ID duy nhất, không đếm trùng |
| Review khen tính năng giải đúng vấn đề đó (KHEN GIO + KHEN ROUTE) | 22/922 | 2,4% | Là tín hiệu người dùng **coi trọng** tính năng, không phải bằng chứng họ đã gặp lỗi |

Ghi dạng "x/N (y%)". Số theo từng app của danh sách ứng viên (từ khoá): Wanderlog 28/200 · Tripomatic 29/200 · Tripsy 28/200 · Rhyme 8/122 · TripIt 6/200.

**Đọc kết quả thế nào (trung thực):**
- Giả thuyết của nhóm: **≥60%** người từng gặp sự cố. **Mẫu review App Store này không ủng hộ con số đó** (2,2%), và **không bác bỏ** nó. Review app là nơi người ta nói về *app*, ít khi kể chuyện lịch trình bị hỏng ở chỗ. Nguồn kiểm chính của nhóm vẫn là **khảo sát 25 người**.
- Điều đo được thật: trong 922 review, người nhắc **giờ mở cửa** rất ít (7), người nhắc **quãng đường / thứ tự** nhiều hơn (26, gồm PAIN + KHEN), và **không review nào** kể chuyện "tới nơi mới biết đóng cửa" thật sự đã xảy ra (chỉ có 1 người than hours không hiện và 2 người mong có cảnh báo).
- Nghĩa là: nếu khảo sát cũng ra thấp ở câu "đến ngoài giờ mở cửa", nên cân nhắc **chuyển trọng tâm lát cắt sang xếp lịch theo quãng đường / thứ tự**, vì đây là phần review nhắc nhiều hơn.

## 4. ≥5 ví dụ cụ thể (nguồn: App Store US, RSS Apple, tải 27/11/2026; không có tên người viết)

Mã = số dòng trong `reviews_labeled.csv` (đếm từ 0, không tính dòng tiêu đề).

1. **[#403 · Tripsy · 2★ · 03/11/2026 · GIO/PAIN]** "…the hours of operation don't pull into this app, so if you're out and about in an area hoping to hit some of your hotspots, you have to switch to a different app anyway to see what's open."
2. **[#306 · Tripomatic · 4★ · 11/05/2018 · ROUTE/PAIN]** "…walking routes [are] similar to driving routes. Instead of taking a direct path, the map is directing me to go 2 or more blocks out of the way, doubling back, etc."
3. **[#235 · Tripomatic · 1★ · 10/02/2020 · ROUTE/TIME/PAIN]** "To build an itinerary is painful. … Even if you input the time for each site the app will not move the items in the correct order."
4. **[#604 · Rhyme · 1★ · 14/11/2026 · ROUTE/PAIN]** "…one day it had me shopping from 8 am until 6 am the next day. No breaks just shopping."
5. **[#369 · Tripomatic · 5★ · 26/04/2017 · GIO/mong có]** "My only issue so far is that I would have an alert that tells you if a place is closed on that day."
6. **[#14 · Wanderlog · 5★ · 14/11/2026 · GIO/KHEN]** "I love that it warns me if I'm scheduling a museum/restaurant on a day they're closed…" *(khen tính năng — cho thấy người dùng coi trọng, không kể mình từng gặp lỗi.)*

## 5. Giới hạn của data

Data cho biết người ta **làm gì / nói gì**, không cho biết **vì sao**. Thiếu gì, lệch về phía nào:
- **Không phải người Việt đi Hà Nội**: review tiếng Anh trên App Store Mỹ, về app lập lịch chung, không phải về lịch trình Hà Nội.
- **Review nói về app, không nói về chuyến đi**: tỷ lệ kể vấn đề chuyến đi (đi vòng, đóng cửa) rất thấp theo bản chất kênh này.
- **Lệch về phía người bực / người mê**: người viết review thường ở hai cực.
- **Mới đọc kỹ 99 ứng viên + 30 ngẫu nhiên**; 823 review còn lại chỉ lọc bằng từ khoá nên **số trên là cận dưới**; phán loại do một người (Hùng + Claude), **chưa có người thứ hai chấm độc lập** (BA9).
- Review mới nhất tại ngày tải; app khác (Google Maps, Tripadvisor) chưa đào do điều khoản không cho scrape.
→ **Kiểm lại bằng:** khảo sát 25 người (`evidence/survey/`) và ≥3 phỏng vấn.
