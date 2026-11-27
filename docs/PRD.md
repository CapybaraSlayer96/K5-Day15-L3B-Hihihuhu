# TripSwipe — Tài liệu yêu cầu sản phẩm

> Track C · Nhóm Hihihuhu · Thiết kế phục vụ CP2 ngày 27/11/2026.
> Đây là yêu cầu cho bản triển khai tiếp theo, không phải xác nhận tính năng đã chạy. Phạm vi tài liệu: một ngày tham quan tại Hà Nội. Kiến trúc tương ứng: [ARCHITECTURE.md](ARCHITECTURE.md); thiết kế nộp BTC: [spec.md §4](../spec.md#4-thiết-kế-guide-22-32).

## 1. Tổng quan sản phẩm

TripSwipe giúp người phụ trách lên lịch cho nhóm bạn đi du lịch tự túc tại Hà Nội chọn địa điểm qua thẻ và nhận lịch trình nháp theo giờ. Người dùng chọn khu vực, quẹt thích/bỏ qua địa điểm, nhập ngày đi, điểm xuất phát, phương tiện và khung thời gian. LLM hiểu sở thích, đề xuất tập điểm và giải thích lựa chọn; thuật toán tính thứ tự, giờ đến/rời và code kiểm ràng buộc trước khi hiển thị. Người dùng duyệt lịch và các điểm phải bỏ trước khi chia sẻ thủ công với nhóm.

**Lát cắt:** Một người lên lịch cho nhóm bạn chọn các địa điểm yêu thích trong Hà Nội, nhận một lịch trình tham quan một ngày đã kiểm giờ mở cửa và thời gian di chuyển, hoặc thông báo cụ thể về phần chưa xếp được.

## 2. Vấn đề và căn cứ

Người lên lịch phải tìm và đối chiếu thông tin rời rạc để chọn điểm, rồi tự xếp thứ tự. Lịch ngược đường, tới ngoài giờ mở cửa hoặc nhồi quá nhiều điểm có thể làm nhóm mất thời gian và bỏ lỡ nơi muốn đến. Đây là giả thuyết sản phẩm đang được nhóm kiểm chứng, chưa có số liệu đủ để khẳng định mức độ phổ biến hay thời gian tiết kiệm.

| Căn cứ trong repo | Điều có thể sử dụng | Giới hạn |
|---|---|---|
| [canvas.md](../canvas.md), [spec.md §0–§2](../spec.md) | Vai người dùng, pain và phạm vi nhóm đã mô tả | Luồng hiện tại chưa được kiểm chứng với người ngoài nhóm |
| Canvas CP2 được nhóm cập nhật trên `main` | Ghi nhận kết quả đào review app sơ bộ và khảo sát đã gửi | Tệp evidence tương ứng trong checkout chưa có kết quả để tái kiểm; không suy tỷ lệ gặp pain của nhóm du lịch Hà Nội từ review app |
| [evidence/hypothesis.md](../evidence/hypothesis.md) | Giả thuyết và kế hoạch khảo sát 25 người; ngưỡng giả thuyết do nhóm tự chọn | Không phải kết quả khảo sát |
| [evidence/summary.md](../evidence/summary.md), [evidence/data-mining.md](../evidence/data-mining.md) | Mẫu tổng hợp và cách lưu bằng chứng | Chưa có kết quả điền vào |
| [eval/baseline-chatbot.md](../eval/baseline-chatbot.md) | Repo ghi nhận lỗi giờ, nghỉ trưa, thiếu ngày và thông tin không nguồn khi thử chatbot | Không phải bằng chứng pain người dùng; một số giờ chuẩn đang mâu thuẫn dataset |
| [data/hanoi_places.json](../data/hanoi_places.json) | 113 bản ghi địa điểm; có tọa độ, sở thích và thời lượng tham quan | Có dữ liệu biên tập; thiếu chứng cứ theo từng trường và giờ có cấu trúc |

Không đưa số người gặp pain, mức giảm thời gian hoặc trích dẫn khảo sát vào báo cáo như kết quả thật trước khi có bằng chứng. Các ngưỡng giả thuyết vẫn thuộc tài liệu bằng chứng gốc.

## 3. Chân dung người dùng và điểm vướng

**Persona theo vai, chưa phải người đã được phỏng vấn:** Người nhận việc lên lịch cho nhóm 3–6 bạn, đi tự túc một ngày tại Hà Nội. Họ cần gom sở thích, biết điểm nào ghép được trong ngày và gửi một lịch dễ hiểu vào nhóm chat. Họ có thể là người địa phương hoặc khách từ tỉnh khác; không giả định tuổi, thu nhập hay mức am hiểu Hà Nội.

| Điểm vướng giả định | Nhu cầu sản phẩm |
|---|---|
| Nhiều lựa chọn, phải mở từng trang để so sánh | Thẻ địa điểm có dữ kiện ngắn, nguồn và trạng thái dữ liệu |
| Khó biến sở thích chung thành tập điểm | Quẹt thích/bỏ qua, xem lại, đánh dấu điểm bắt buộc |
| Khó ghép vị trí với ngày/giờ mở cửa | Lịch tính bằng code, gồm cả chặng đi và thời gian chờ |
| Không biết nên bỏ điểm nào khi quá tải | Liệt kê điểm bị bỏ, lý do và lựa chọn nới ràng buộc |
| Lịch chatbot có vẻ hợp lý nhưng khó tin | Nguồn theo dữ kiện, trạng thái kiểm tra và giả định hiển thị rõ |

Một người đại diện nhập lựa chọn; MVP không thu phiếu hay đồng bộ sở thích của từng thành viên.

## 4. Mục tiêu và phạm vi

### 4.1. Mục tiêu

- Rút ngắn thao tác chọn điểm và xếp lịch; mức cải thiện phải đo qua dùng thử.
- Mọi lịch được trình bày là đã kiểm phải vượt qua bộ kiểm ràng buộc bằng code.
- Giải thích được vì sao chọn, đổi thứ tự hoặc bỏ một địa điểm.
- Tái sử dụng dataset và hợp đồng chạy thử/eval/mô phỏng của repo.

### 4.2. Phạm vi MVP

| Trong phạm vi | Hành vi |
|---|---|
| Địa lý | Hà Nội; bản chạy đầu ưu tiên tập điểm nội thành đã chuẩn hóa và cho phép bằng cấu hình. Các điểm ngoại thành trong dataset chỉ hiện để xếp lịch khi được bật và đủ dữ liệu tuyến/giờ |
| Thời gian | Một ngày lịch, giờ địa phương `Asia/Ho_Chi_Minh`; không kéo qua nửa đêm |
| Chọn điểm | Chọn khu vực, quẹt thích/bỏ qua, hoàn tác, xem danh sách đã chọn; nút bấm tương đương quẹt |
| Cá nhân hóa | Sở thích, nhịp độ, thời lượng tham quan, điểm thích và điểm bắt buộc do người dùng xác nhận |
| Phương tiện | Một chế độ cho cả lịch: đi bộ hoặc ô tô khi có dữ liệu định tuyến tương ứng; không tự chuyển giữa các phương tiện |
| Kết quả | Thứ tự điểm, giờ đến/rời, chặng di chuyển, chờ/nghỉ đã tính, nguồn, điểm bị bỏ và cảnh báo |
| Sửa lịch | Bỏ/thêm điểm hoặc yêu cầu đổi thứ tự; tính lại và kiểm lại toàn bộ |
| Hai đường nhập | Giao diện thẻ và đầu vào văn bản dùng chung workflow; CLI phục vụ lệnh BTC, không yêu cầu quẹt trước |

Điểm xuất phát cần được xác định tọa độ hoặc chọn từ dữ liệu. Điểm kết thúc mặc định là điểm tham quan cuối, không mặc định quay về nơi xuất phát; nếu người dùng yêu cầu quay lại thì phải tính thêm chặng về trong khung giờ.

### 4.3. Không làm trong MVP

- Lịch nhiều ngày, ngoài Hà Nội, lưu trú và tối ưu liên tỉnh.
- Đặt vé, đặt bàn, giữ chỗ, thanh toán hoặc tự gửi lịch ra dịch vụ ngoài.
- Dẫn đường trực tiếp, dự báo ùn tắc, hàng đợi, thời tiết thời gian thực.
- Tài khoản, cộng tác thời gian thực, biểu quyết nhiều người và chia tiền.
- Cam kết ngân sách chính xác khi thiếu giá vé/chi phí; `price_range` chỉ dùng tham khảo có nguồn.
- Thu thập tự động mọi địa điểm trên Internet hoặc dùng LLM làm nguồn dữ kiện địa lý.

## 5. Hành trình người dùng

1. **Thiết lập:** Xác nhận Hà Nội, ngày đi, khung giờ, điểm xuất phát và phương tiện; bổ sung điểm kết thúc nếu cần. Thiếu ngày/thứ phải hỏi trước khi lập lịch.
2. **Khám phá:** Chọn khu vực được hỗ trợ và xem thẻ lấy từ dataset. Thẻ thể hiện tên, loại, vị trí, thời lượng ước tính, giờ/giá nếu có nguồn và cảnh báo dữ liệu.
3. **Chọn:** Quẹt thích/bỏ qua, hoàn tác; xem lại tập điểm, đánh dấu điểm bắt buộc. Quẹt thích là ưu tiên mềm, không đồng nghĩa tất cả bắt buộc phải xếp.
4. **Đề xuất:** AI chuyển sở thích thành danh sách ID hợp lệ; hệ thống tra giờ, tuyến và tính lịch. Không có lượt thích thì hỏi người dùng cho phép gợi ý theo sở thích trước khi tự thêm điểm.
5. **Kiểm tra:** Chỉ hiển thị lịch đã qua bộ kiểm. Nếu thiếu dữ liệu hoặc không xếp hết, hiển thị rõ điểm bị bỏ và cách điều chỉnh.
6. **Duyệt:** Người phụ trách đọc lịch nháp, nguồn và giả định; đồng ý hoặc sửa. Sau mỗi sửa phải kiểm lại; bản cũ bị đánh dấu không còn hiện hành.
7. **Sử dụng:** Người dùng sao chép lịch đã duyệt và tự gửi cho nhóm. Nguồn giờ mở cửa và điều kiện cần xác nhận trước khi đi đi kèm bản sao.

## 6. Câu chuyện người dùng và tiêu chí chấp nhận

| ID | Câu chuyện | Tiêu chí chấp nhận |
|---|---|---|
| US-01 | Là người lên lịch, tôi muốn chọn nhanh điểm theo khu vực và sở thích | Thẻ chỉ chứa ID trong dữ liệu thuộc phạm vi; thích/bỏ qua/hoàn tác cập nhật đúng danh sách, không nhân đôi điểm |
| US-02 | Tôi muốn giữ điểm mình nhất định phải đi | Điểm được đánh dấu bắt buộc không bị bỏ âm thầm; nếu không thể ghép đủ thì báo chưa có lịch đáp ứng và hỏi người dùng |
| US-03 | Tôi muốn nhận lịch vừa khung giờ | Khi có đủ dữ kiện, lịch bắt đầu từ xuất phát, tính cả chặng đầu và chặng về nếu có, không chồng giờ và không vượt giờ kết thúc |
| US-04 | Tôi muốn tới nơi khi còn mở cửa | Toàn bộ thời gian tham quan nằm trong một khoảng mở hợp lệ; không đi xuyên giờ nghỉ trưa hoặc suy giờ tour đêm từ giờ tham quan ngày |
| US-05 | Tôi muốn biết vì sao không đi được tất cả điểm | Mỗi điểm đã chọn không có trong lịch xuất hiện trong danh sách bị bỏ với lý do đúng dữ kiện và ít nhất một hướng điều chỉnh |
| US-06 | Tôi muốn sửa lịch theo ý nhóm | Mỗi lần sửa tạo phiên bản mới, tính lại tuyến và kiểm lại; bản sửa chưa kiểm không có nhãn đã kiểm |
| US-07 | Tôi muốn tin được thông tin AI nêu | Không có ID lạ; giờ, ngày đóng, giá và tuyến truy được đến kết quả công cụ; trường chưa biết hiển thị chưa có dữ liệu |
| US-08 | Tôi muốn biết hệ thống đang thiếu gì | Thiếu ngày/thứ trả câu hỏi, chưa trả lịch; lỗi tuyến/giờ không bị biến thành thời gian bằng 0 hoặc mở cửa cả ngày |
| US-09 | Tôi muốn tự quyết trước khi dùng lịch | Lịch luôn là bản nháp cho tới khi người dùng duyệt; đặt vé, thanh toán và gửi tin không được thực hiện |

## 7. Yêu cầu chức năng

| ID | Yêu cầu | Mức |
|---|---|---|
| FR-01 | Chuẩn hóa đầu vào từ thẻ hoặc văn bản thành một yêu cầu chuyến đi; kiểm phạm vi, ngày, giờ, tọa độ và phương tiện | Bắt buộc |
| FR-02 | Lọc theo khu vực/cấu hình, loại, nhãn sở thích; không dùng lựa chọn mềm thay cho điều kiện cứng | Bắt buộc |
| FR-03 | Quản lý lượt thích/bỏ qua/hoàn tác và tập điểm bắt buộc; dữ liệu lựa chọn giữ trong phiên | Bắt buộc cho giao diện thẻ |
| FR-04 | LLM phân tích sở thích và đề xuất ID, ưu tiên và lý do từ danh sách được cấp | Bắt buộc |
| FR-05 | Tra thông tin địa điểm, giờ theo ngày/hoạt động, thời lượng và nguồn; trả rõ dữ liệu thiếu/xung đột | Bắt buộc |
| FR-06 | Lấy ma trận thời gian theo phương tiện, cache có nguồn/phiên bản; phân biệt tuyến thật, cache thật và mock | Bắt buộc |
| FR-07 | Tính thứ tự, thời điểm ghé, chờ và nghỉ bằng code; không dùng giờ model tự tính | Bắt buộc |
| FR-08 | Kiểm ràng buộc bằng `kiem_lich_trinh`; trả vi phạm có mã và đối tượng, sửa có giới hạn | Bắt buộc |
| FR-09 | Phân biệt đủ lịch, một phần, thiếu thông tin, không khả thi, thiếu dữ liệu và ngoài phạm vi | Bắt buộc |
| FR-10 | Giữ lịch có cấu trúc trong chuỗi `output`, kèm bản tiếng Việt dựng từ cùng dữ liệu đã kiểm để chấm được | Bắt buộc |
| FR-11 | Ghi mọi lời gọi model/công cụ qua decorator sẵn có; token lấy từ API, không ước lượng | Bắt buộc |
| FR-12 | Hiển thị bản nháp, nguồn, giả định và kiểm lại khi sửa trước khi người dùng duyệt | Bắt buộc |

## 8. Quy tắc nghiệp vụ

| ID | Quy tắc |
|---|---|
| BR-01 | Chỉ lập lịch trong phạm vi Hà Nội được cấu hình, một ngày và một múi giờ; schema vẫn dùng mã thành phố/khu vực thay vì cố định chuỗi Hà Nội trong thuật toán |
| BR-02 | Không có ngày hoặc thứ thì hỏi lại, không trả lịch giả định. Chỉ có thứ được xử lý như kịch bản tuần; nếu cần mùa/ngày lễ thì hỏi ngày cụ thể trước khi xếp |
| BR-03 | Thiếu xuất phát/khung giờ/phương tiện thì mặc định hỏi lại. Đường văn bản có thể dùng mặc định cấu hình nếu nói rõ; không tự giả định phương tiện không được công cụ hỗ trợ |
| BR-04 | Giờ ngoại lệ theo ngày ưu tiên hơn giờ tuần/mùa; dữ liệu xung đột chưa giải quyết không được xem là giờ đã xác minh |
| BR-05 | `best_time_of_day` là sở thích mềm; `opening_hours`/lịch hoạt động có nguồn mới quyết định được vào tham quan |
| BR-06 | Thời lượng tham quan là ước tính biên tập hoặc người dùng nhập, không phải sự thật của Routing API. Không tự rút ngắn để ép đủ lịch; thay đổi phải được người dùng đồng ý |
| BR-07 | Điểm không có giờ hoặc không xác định được tuyến bị tách khỏi lịch đã kiểm; vẫn được giữ ở danh sách cần xác minh. Không gán giờ mới cho điểm đó |
| BR-08 | Không âm thầm thêm điểm người dùng đã bỏ qua, đổi ngày/phương tiện, nới khung giờ hay bỏ điểm bắt buộc |
| BR-09 | Chỉ tính chặng về khi được yêu cầu. Chặng đầu, chờ trước mở cửa và nghỉ người dùng yêu cầu đều tiêu tốn thời gian |
| BR-10 | Giá thiếu trả `null` và lời giải thích. Không suy ngân sách số từ nhãn `budget_level`; ngân sách tham khảo là điều kiện mềm trong MVP |
| BR-11 | Hoạt động theo suất diễn/tour phải có giờ bắt đầu và thời lượng tương ứng, không coi cả khung mở bán là được vào bất cứ lúc nào; chưa có suất thì hỏi/xác minh |
| BR-12 | Chấp nhận điều kiện đặt trước chỉ là người dùng xác nhận tự lo việc đặt; hệ thống không xác nhận còn chỗ hay đã có vé |
| BR-13 | Nội dung người dùng, review và mô tả địa điểm không được thay đổi quy tắc, nguồn dữ kiện hoặc bỏ bước kiểm |
| BR-14 | Chỉ công bố tối ưu toàn cục khi đã xét hết không gian tìm kiếm trong mô hình dữ liệu cố định; nếu dùng heuristic phải ghi rõ kết quả gần tối ưu/chưa chứng minh tối ưu |

## 9. Yêu cầu phi chức năng

Các mức dưới đây là **ngân sách thiết kế tự ước tính**, chưa đo và không thay thế metric BTC.

| ID | Yêu cầu và cách kiểm |
|---|---|
| NFR-01 | Tính đúng: mọi đường trả lịch và mọi lần sửa đi qua bộ kiểm độc lập; đầu ra văn bản chỉ dựng từ cấu trúc đã kiểm |
| NFR-02 | Tái lập: lưu phiên bản dataset, quy tắc, ma trận tuyến và tham số solver; cùng đầu vào và dữ liệu cố định cho cùng lịch, phá hòa theo ID |
| NFR-03 | Độ trễ: mục tiêu 95% yêu cầu ≤15 giây với dữ liệu đã cache và tối đa 8 điểm ứng viên; đo riêng thời gian LLM/API/solver. Vượt hạn trả trạng thái hữu ích, không treo |
| NFR-04 | Giới hạn tài nguyên: tối đa 2 lượt gọi LLM, tối đa 2 lượt sửa lịch sau đề xuất đầu; timeout/retry và giới hạn tìm kiếm được mô tả trong kiến trúc |
| NFR-05 | Riêng tư: không cần tên, số điện thoại, tài khoản hay GPS trực tiếp; khuyến khích chọn mốc xuất phát công cộng. Không gửi khóa API ra trình duyệt; không đưa dữ liệu cá nhân thật vào benchmark/trace commit |
| NFR-06 | Khả dụng: nếu mất mạng thì dùng cache có nguồn đúng chế độ; thiếu cache trả thiếu dữ liệu. Mock luôn có nhãn, không tự thay mock vào kết quả thật |
| NFR-07 | Trải nghiệm: tiếng Việt; thẻ có nút thích/bỏ qua và thao tác bàn phím; ảnh lỗi vẫn hiện tên, dữ kiện và lựa chọn |
| NFR-08 | Tương thích: giữ `answer(text) -> {"output": str}`, `call_model`, `@model_call`, `@tool`; không sửa các file khung BTC |
| NFR-09 | Truy vết: mỗi dữ kiện quan trọng mang nguồn và thời điểm kiểm khi có; không biến trạng thái biên tập của cả POI thành xác minh mọi trường |

## 10. Thước đo thành công

### 10.1. Thước đo kỹ thuật đã có trong repo

Chép để tham chiếu từ [eval/metric_spec.yaml](../eval/metric_spec.yaml), không điều chỉnh định nghĩa, mẫu số hoặc ngưỡng tại tài liệu này:

| Metric | Ngưỡng đang ghi |
|---|---|
| `dung_gio_mo_cua` | 100% câu có trả lịch, 0 vi phạm |
| `khop_khung_gio_nguoi_dung` | 100% câu có trả lịch |
| `khong_bia_du_lieu` | 100% câu |
| `it_di_vong` | ≥80% câu thường có trả lịch; tổng di chuyển ≤1,2 lần tối thiểu của cùng tập điểm khả thi |
| `bao_ro_khi_khong_xep_duoc` | ≥80% câu khó |
| `hoi_lai_va_tu_choi_dung` | 100% câu từ chối; ≥80% câu khó thuộc loại thiếu thông tin |

Chuẩn tổng thể đã được nhóm cập nhật tại `spec.md` §7 trên `main`: ≥80% câu qua, 0 vi phạm giờ mở/ngày đóng/nghỉ trưa trên câu có lịch, không bịa dữ liệu 100% và xử lý đúng 100% câu từ chối; mỗi câu đạt khi mọi metric áp dụng đều đạt. Tài liệu này chỉ tham chiếu, không sửa chuẩn hoặc tuyên bố đã đạt CP2. Bộ câu thử hiện có 16 câu; chưa có kết quả chạy thật của TripSwipe trong phạm vi công việc này.

### 10.2. Thước đo sản phẩm cần thu

| Thước đo | Cách đo dự kiến | Mục tiêu |
|---|---|---|
| Thời gian tạo lịch chấp nhận được | Từ bắt đầu chọn đến người phụ trách duyệt; so với cách tự làm trên tác vụ tương đương | Chốt sau đo baseline; chưa có số |
| Tỷ lệ hoàn thành | Số phiên có lịch được người dùng duyệt / số phiên có đủ đầu vào trong phạm vi; báo riêng số thiếu dữ liệu, thiếu thông tin, từ chối | Chưa chốt |
| Công sức chỉnh sửa | Số lần sửa trước khi duyệt; phân loại sửa vì dữ liệu sai, sở thích hoặc quá tải | Chưa chốt |
| Mức đáp ứng điểm mong muốn | Số điểm thích được xếp / tổng điểm thích; báo riêng điểm bắt buộc và lý do bị bỏ | Theo dõi, không thay metric BTC |
| Chi phí tác vụ thành công | Token API thực + chi phí dịch vụ ngoài / số phiên được duyệt; tách chi phí LLM và Routing API | Đo CP3/CP4; không dùng bảng giá mẫu làm giá thật |

## 11. Trường hợp biên và hành vi chấp nhận

| Tình huống | Hành vi |
|---|---|
| Không thích điểm nào hoặc bỏ qua hết | Hỏi sở thích/đề nghị xem lại khu vực, chưa gọi tối ưu với tập rỗng |
| Thích quá nhiều điểm | Ưu tiên điểm bắt buộc và sở thích, báo mọi điểm không xếp; không ép đủ bằng giảm thời lượng |
| Điểm bắt buộc đóng cửa | Báo không đáp ứng, đề nghị đổi ngày/bỏ bắt buộc; chỉ trình bày phương án thay thế như một đề xuất cần duyệt |
| Thiếu ngày đi | Hỏi lại và chưa trả lịch; tương ứng B10 |
| Thiếu giờ/nguồn hoặc dữ liệu xung đột | Giữ điểm cần xác minh ngoài lịch đã kiểm, không bịa giờ; tương ứng ý định kiểm B12 |
| Nghỉ trưa, hai khoảng mở, giờ theo mùa | Mỗi lần ghé nằm trọn một khoảng; hỏi ngày cụ thể khi chỉ có thứ không đủ quyết định |
| Mưa, đông người, ngày lễ/bảo dưỡng | Không khẳng định trạng thái thời gian thực; báo giới hạn và cần kiểm nguồn ngoại lệ trước khi đi |
| Tên trùng/địa chỉ không rõ | Đưa các ID ứng viên để chọn, không lấy tùy ý kết quả đầu |
| Tuyến không có hoặc tọa độ sai | Chặn chặng, thử cache hợp lệ; không dùng khoảng cách thẳng như thời gian đường đi |
| Hết giờ tìm kiếm | Nói chưa tìm được lịch trong giới hạn; không khẳng định chắc chắn vô nghiệm |
| Người dùng kéo đổi thứ tự | Tính lại và cảnh báo vi phạm; không giữ nhãn đã kiểm của bản trước |
| Yêu cầu đặt chỗ, nhiều ngày hoặc bỏ kiểm | Từ chối phần ngoài phạm vi, đề nghị phần làm được; tương ứng B13–B16 |

## 12. Rủi ro, giới hạn và việc cần chốt

| Rủi ro/điểm chưa thống nhất | Cách xử lý thiết kế và việc còn lại |
|---|---|
| Chưa có kết quả khảo sát đúng vai người dùng và bằng chứng chi tiết chưa đồng bộ | Canvas đã ghi số review app sơ bộ nhưng evidence chưa có hồ sơ để tái kiểm; tiếp tục khảo sát/đào dữ liệu đúng kế hoạch, không tự điền số vào evidence |
| Dataset và benchmark mâu thuẫn | B05 muốn xếp Hoàng thành thứ Hai trong khi `hn_10` ghi đóng thứ Hai; B08 coi Mỹ thuật đóng thứ Hai trong khi `hn_46` ghi mở; B12 dự kiến thiếu giờ Một Cột trong khi `hn_13` có chuỗi giờ nhưng thiếu nguồn chính thức. Ghi nhận để người phụ trách đối soát nguồn và báo ảnh hưởng; không sửa `expected` để khớp output |
| Dữ liệu hoạt động đêm tách ID | B03 nói Văn Miếu buổi tối; dataset có `hn_09` tham quan ngày và `hn_68` tour đêm. Cần xác nhận hoạt động người dùng muốn, không nhập nhằng hai dịch vụ |
| Thiếu hoặc không đủ xuất xứ | Data card nêu file CSV gốc và script xây dataset nhưng các file đó chưa có trong checkout. Chưa thể kiểm lại quy trình xây dữ liệu từ repo này |
| Data card chưa khớp thống kê | JSON có 20 giá trị `district` khác nhau, data card ghi 19; đây là nhãn trong file, không xác nhận địa giới hành chính hiện hành |
| Nhãn `verified` dễ gây hiểu nhầm | Chỉ 59/113 bản ghi có `verification.official_source` không rỗng; URL cấp miền và nhãn biên tập chưa đủ chứng minh từng giờ/giá |
| Thời lượng, tuyến và giờ không phản ánh hiện trường | Công bố đây là lịch theo dữ liệu đã kiểm và ước tính tuyến, không cam kết tới nơi chắc chắn còn mở/còn chỗ |
| Màn quẹt và tích hợp API chưa tồn tại | CP2 phân biệt sơ đồ/mock với tính năng thật; CP3 nối model thật, dữ liệu giờ chuẩn hóa và tuyến có nguồn trước khi đánh giá |

Tài liệu này không sửa `canvas.md`, evidence, data, bộ câu thử, metric, chuẩn đạt §7 hay các file khung. Các mục chưa hoàn tất được giữ là việc cần xử lý, không coi là đã được nghiệm thu.
