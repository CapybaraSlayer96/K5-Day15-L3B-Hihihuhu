> Đây là khung repo nộp bài. Điền mọi chỗ `____`, giữ nguyên tên các mục.
> Giờ, mốc, luật, rubric: xem `README.md`, `02-guide.md`, `03-rubric.md` trong repo đề (bộ đề BTC phát).

# Hihihuhu — Lịch trình một ngày ở Hà Nội cho nhóm bạn

**Thành viên, lớp, track:** xem [TEAMS.md](TEAMS.md). **Điền TEAMS.md đúng format**: khi chấm và đánh giá, BTC quét file này để ghép điểm cho từng người.

*Lát cắt = phần nhỏ nhất làm xong được trong hackathon: một người dùng · một việc · một quyết định AI · một kết quả.*

---

## Nhóm làm gì, khung làm gì

| Nhóm quyết định và viết | Khung làm sẵn (không cần sửa) |
|---|---|
| Người dùng, pain, bằng chứng, impact (`evidence/`, `spec.md` §1–§2) | — |
| Hình dạng giải pháp, công cụ, prompt, luồng (`spec.md` §4, `codebase/agent.py`, `tools.py`, `ai.py`) | Ghi mọi lần gọi model / công cụ vào trace, cộng token (`codebase/tracing.py`) |
| Bộ câu thử, metric, chuẩn "đạt" (`eval/benchmark.csv`, `eval/metric_spec.yaml`, `spec.md` §7) | Kiểm đủ cột, đủ câu `kho` / `tu_choi`, đủ ≥1/3 câu từ người dùng / data thật (`run.py check`) |
| Chấm cột `pass` theo metric spec | Chạy cả bộ một lệnh, có run ID, model, token từng câu (`run.py eval`) · tính % đạt (`run.py score`) |
| Persona, số người dùng thật, giá model (`cost/personas.yaml`) | Sinh ~50 phiên, chạy thật qua bản chạy thử, tính chi phí / phiên, / task thành công, / tháng 3 kịch bản (`run.py simulate`) |

*Ví dụ track A (ví dụ cỡ, không phải lời giải):* nhóm viết công cụ `search_lesson` tra bài pre-class đã đánh mã đoạn, luồng "tra đoạn → model trả lời kèm mã đoạn, không có thì nói không có", metric "mọi khẳng định có mã đoạn đúng", persona "ôn dồn trước kiểm tra". Khung chạy 25 câu thử ra `run-1.csv`, nhóm chấm `pass`, `score` in % đạt; `simulate` chạy 50 phiên ra chi phí / task thành công cho hai model.

## Chạy trong 3 phút

Bộ khung cần **Python 3.10 trở lên** (Python 3.9 có sẵn trên macOS vẫn chạy được, chỉ in một dòng nhắc). **Không cần `pip install`.**

**Bước 1 — Mở cửa sổ lệnh ngay trong thư mục repo**

| Windows (PowerShell) | macOS |
|---|---|
| Mở thư mục repo bằng File Explorer → bấm vào thanh địa chỉ → gõ `powershell` → Enter | Mở **Terminal** (Cmd + Space, gõ "Terminal") → gõ `cd ` (có dấu cách) → kéo thả thư mục repo vào → Enter |

Gõ `dir` (Windows) hoặc `ls` (macOS / Linux): thấy `run.py` và `README.md` là đang đứng đúng chỗ.

**Bước 2 — Kiểm Python và chạy thử**

| Việc | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Kiểm Python | `python --version` (không được thì `py --version`) | `python3 --version` |
| Chạy bản chạy thử (chế độ giả, chưa gọi model) | `python run.py` | `python3 run.py` |
| Kiểm bộ câu thử | `python run.py check` | `python3 run.py check` |
| Tạo file `.env` để nối model | `copy .env.example .env` | `cp .env.example .env` |

- Windows: gõ `python` mà mở Microsoft Store hoặc báo không có lệnh → dùng `py`. Chưa có Python: cài từ python.org, **tick "Add python.exe to PATH"**, mở lại PowerShell.
- macOS: báo `command not found: python` là bình thường → dùng `python3`.
- `python run.py` in ra "[câu trả lời giả — chưa nối model] …" là khung chạy đúng. Nối model thật: [docs/connect-model.md](docs/connect-model.md).

Trong README này lệnh viết là `python …`; máy nhóm cần `python3` hay `py` thì gõ thay.

## Lệnh

### Chạy backend web B1–B3

Cần Docker Desktop đang chạy, Docker Compose v2. Từ thư mục repo:

```sh
docker compose up --build -d
```

Mở [localhost:9000](http://localhost:9000) và [tài liệu API](http://localhost:9000/docs). Đây là backend cấu hình/tạo và vào nhóm/bộ thẻ/quẹt/tiến độ; giao diện quẹt và API xếp lịch nhóm B4 đang chờ triển khai. JSON mẫu và hợp đồng nối UI: [docs/api-examples.md](docs/api-examples.md).

- Compose chờ Postgres khỏe, tạo bảy bảng và upsert dữ liệu lúc khởi động. Dữ liệu nhóm/phiếu lưu trong volume `postgres-data`, giữ qua `docker compose restart` và `docker compose down`.
- Web chỉ mở trên `127.0.0.1:9000`; Postgres mặc định không mở cổng ra máy host. Kiểm tra: `docker compose ps`, `docker compose logs app`, hoặc `GET /health`.
- Bộ thẻ hiện là phương án **tạm theo rating trong dữ liệu** sau lọc ngày/giờ/giá; response có `source: provisional_rating`. Chưa gọi AI chọn thẻ; có adapter chờ hàm `build_deck` của Hải. Không cần API key để thử B1–B3.
- Image chỉ chép thư mục app/codebase/data, không chép `.env`, khảo sát hoặc trace. Compose dùng mật khẩu DB mẫu chỉ cho demo nội bộ và `MODEL_PROVIDER=fake`; không đọc key vào image. Có thể đổi cổng qua `TRIPSWIPE_PORT` và mật khẩu qua `TRIPSWIPE_DB_PASSWORD` (dùng ký tự an toàn trong URL: chữ/số/gạch dưới/gạch ngang).
- Dừng: `docker compose down`. Tránh thêm `-v` nếu muốn giữ dữ liệu nhóm.

Nếu chạy Python trực tiếp với Postgres riêng:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export DATABASE_URL='postgresql://tripswipe:tripswipe_local_only@127.0.0.1:54329/tripswipe'
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 9000
```

`DATABASE_URL` phải trỏ DB của bạn đang chạy; ví dụ trên dùng cổng test localhost. Backend đọc URL từ môi trường, không tự nạp `.env`. Lõi `python run.py`, eval và simulate vẫn chạy theo cách cũ, không cần Postgres hoặc các gói web.

### Kiểm thử backend

Integration test dùng Postgres thật, tạo schema ngẫu nhiên và tự xóa sau test; không gọi model, không sửa benchmark hoặc lượt eval:

```sh
docker compose -f docker-compose.yml -f docker-compose-test.yml up -d db
.venv/bin/python -m pip install -r requirements-dev.txt
TEST_DATABASE_URL='postgresql://tripswipe:tripswipe_local_only@127.0.0.1:54329/tripswipe' .venv/bin/python tests/test_api.py
python3 tests/test_core.py
python3 run.py check
```

Nếu chưa có `.venv`, tạo theo hướng dẫn chạy Python trực tiếp ở trên. Override test chỉ mở Postgres trên `127.0.0.1:54329`; URL test cần dùng đúng mật khẩu nếu bạn đã đổi. Sau khi test, chạy lại `docker compose up -d db` để bỏ cổng DB trên host.

### Lệnh CLI và đánh giá của BTC

| Lệnh | Làm gì |
|---|---|
| `python run.py` | Chạy bản chạy thử (gõ đầu vào, nhận kết quả, kèm số lần gọi model / token) |
| `python run.py check` | Kiểm `eval/benchmark.csv` (6 cột, số câu, `kho` / `tu_choi`, mã `source`, ô trống, dòng mẫu) `eval/metric_spec.yaml` (≥3 metric điền đủ) và `TEAMS.md` (đúng format để BTC quét). Chỉ cảnh báo, không sửa file |
| `python run.py eval --try` | **Thử nối model:** chạy 3 câu đầu (`--try 5` = 5 câu) → `eval/run-try.csv`. Thấy "Nối model được" là xong. Không tính là một lượt |
| `python run.py eval` | Chạy cả bộ qua `codebase/agent.py` → `eval/run-1.csv` (lần sau `run-2.csv`…) + `traces/run-1.jsonl`. Mỗi dòng có run ID, model, số lần gọi model / công cụ, token. Model còn giả → chỉ ghi `run-mock.csv`; mọi câu lỗi → `run-error.csv`; Ctrl+C → `run-stopped.csv` — đều **không** được đánh số |
| `python run.py eval --fake` | Thử riêng bộ chạy, không gọi agent → `eval/run-fake.csv` |
| `python run.py score eval/run-1.csv` | Sau khi điền cột `pass` (1 / 0): in % đạt tổng và theo `type`. Còn ô trống → "CHƯA CHẤM XONG", không in % |
| `python run.py simulate --try` | Thử mô phỏng chi phí 10 phiên (làm trước CP3) → `cost/simulate-try.csv` |
| `python run.py simulate` | Mô phỏng chi phí khi dùng thật theo `cost/personas.yaml` (≥50 phiên) → `cost/simulate-N.csv` + `cost/simulate-N-summary.md` |
| `python run.py simulate --rate-from eval/run-2.csv` | Như trên, lấy tỉ lệ đạt từ đúng lượt chỉ định. Không ghi thì khung lấy lượt `run-N` mới nhất đã chấm, cùng model, và ghi rõ đã lấy lượt nào trong bản tóm tắt |

Gói miễn phí báo hết lượt: thêm `--wait 4` sau `eval` hoặc `simulate` (nghỉ 4 giây giữa hai lượt gọi). Sửa CSV bằng Excel: *File → Save As → CSV UTF-8*; Google Sheets: *Tệp → Tải xuống → CSV*.

**Lượt có lỗi kỹ thuật** (cột `error` có chữ): không sửa tay file đó, chạy lại thành lượt mới và ghi vào bảng các lượt ở `eval/README.md`. Không xoá file lượt nào.

Nhóm dùng stack khác (Node, Streamlit, notebook…): sửa hàm `run_app()` trong `run.py` để `python run.py` vẫn chạy được bản chạy thử, và giữ `answer()` trong `codebase/agent.py` để `eval`, `simulate` chạy được.

## Bản chạy thử — viết ở đâu

| File | Viết gì | Bước guide |
|---|---|---|
| `codebase/agent.py` | `answer(text)` — luồng chính, đúng hình dạng ở `spec.md` §4. Khung có sẵn một workflow 2 bước *ví dụ* | 3.2 |
| `codebase/tools.py` | Công cụ của bài toán, mỗi công cụ một hàm có `@tool` | 2.2, 3.2 |
| `codebase/ai.py` | `call_model(system, user)` — chỗ duy nhất gọi model. Chưa điền `.env` thì chạy **chế độ giả** | 3.3 |

- **Trước CP2:** để chế độ giả, công cụ trả dữ liệu giả — `python run.py` đi hết luồng là đủ.
- **Trước CP3:** nối model thật theo [docs/connect-model.md](docs/connect-model.md), `eval --try` thấy token > 0 rồi mới `eval`.
- Bộ chạy gửi **nguyên ô `input`** của câu thử vào `answer(text)`. Dữ liệu nền (bài học, thông báo, lịch…) để trong `data/`, đọc qua công cụ.

## Phần nào thật, phần nào giả

| Thành phần | Thật / Giả | Ghi chú |
|---|---|---|
| Lời gọi AI ở quyết định trung tâm | **Thật** (bắt buộc từ CP3) | Model: gpt-4.1-mini qua endpoint tương thích OpenAI (`MODEL_PROVIDER=openai`); đọc yêu cầu → cấu hình + ID địa điểm, viết lý do chọn |
| Giờ mở cửa, ngày đóng, giá | **Thật** (dữ liệu công khai) | `data/hanoi_places.json`, đối chiếu trang chính thức (nguồn từng điểm ở `data/DATA_CARD.md`) |
| Thời gian di chuyển | **Ước tính** | Ma trận OSRM tính sẵn, lấy max với tốc độ đô thị; không phải giao thông thời gian thực |
| Xếp lịch, kiểm lịch | **Thật** (code) | `codebase/planner.py`, không qua model |
| Backend nhóm / phiếu quẹt | **Thật** (B1–B3) | FastAPI + Postgres + Docker; bộ thẻ tạm có nhãn, API mẫu trong `docs/api-examples.md` |
| Giao diện nhóm / quẹt thẻ và API lịch nhóm | Đang build (CP4) | U2–U5, A3, B4 — xem `TASKS.md` |
| Chế độ `MODEL_PROVIDER=fake` | Giả | Chỉ để chạy khung khi chưa có key; không tính lượt |

## Dùng AI vào việc gì

2–3 dòng (bắt buộc): nhóm dùng công cụ AI nào để làm gì, người kiểm lại phần nào. Chi tiết: [docs/ai-usage.md](docs/ai-usage.md). Coding agent đọc [AGENTS.md](AGENTS.md).

Nhóm dùng Claude (Claude Code) để soạn tài liệu (spec, PRD, data card), viết khung code lõi, tra giờ mở cửa từ trang chính thức, chạy tay chatbot làm mức so sánh và chấm thử độc lập; ChatGPT / Claude để rà câu hỏi khảo sát. Người trong nhóm duyệt từng commit, đối chiếu lại nguồn giờ mở cửa, tự chấm cột `pass`. Không dùng AI để tạo câu trả lời khảo sát hay sửa kết quả các lượt đã chạy.

## File mẫu — điền ở bước nào

| File | Điền ở bước guide | Mốc |
|---|---|---|
| `TEAMS.md` | 1.0 | CP1 · **đúng format**, BTC quét khi chấm |
| `canvas.md` | 1.4 | CP1, cập nhật CP2 |
| `evidence/hypothesis.md` | 1.1 | trước khi tìm bằng chứng |
| `evidence/data-mining.md` · `evidence/interviews/TEMPLATE.md` → `P1.md`… · `evidence/survey/TEMPLATE.md` | 1.2 | bắt đầu sau Zoom, xong CP3 |
| `evidence/summary.md` | 1.2 | CP3 |
| `spec.md` | §0–§2: 1.1–1.3 · §3–§5: 2.1–2.3 · §7: 2.4 · §8: 4.2 · §10: suốt | §7 chốt CP2 · §0–§7 CP3 · đủ CP4 |
| `data/DATA_CARD.md` | 2.4 | bản đầu CP2 |
| `eval/benchmark.csv` · `eval/metric_spec.yaml` | 2.4 | ≥10 câu + metric chốt CP2 · 20–30 câu CP3 |
| `codebase/` | 3.2, 3.3 | khung CP2 · AI thật CP3 |
| `eval/report.md` · `eval/README.md` | 4.1 (README mục 1–4 từ 2.4) | CP4 |
| `cost/personas.yaml` · `cost/cost-estimate.md` | 4.2 | thử 10 phiên CP3 · đủ CP4 |
| `validation/log.md` *(bonus)* | 4.3 | CP4 |
| `slides/outline.md` → `demo-slides.pdf` | 5.1 | CP4 |
| `reflection/TEMPLATE.md` → `reflection/<ten>.md` | 5.3 | 23:59 Thứ Bảy 28/11 |
| `AGENTS.md` · `docs/ai-usage.md` | khi dùng coding agent / AI | suốt |

## Bảy hạng mục bắt buộc — nằm ở file nào

| # | Hạng mục | File |
|---|---|---|
| 1 | Bằng chứng pain | `evidence/` (tổng hợp ở `evidence/summary.md`) |
| 2 | Impact có số | `spec.md` §2 |
| 3 | Thiết kế giải pháp | `spec.md` §4 |
| 4 | Bản chạy thử làm trọn lát cắt | `codebase/` · lệnh ở mục "Lệnh" |
| 5 | Định nghĩa "tốt" + bộ câu thử | `data/DATA_CARD.md` · `eval/` |
| 6 | Mô phỏng chi phí khi dùng thật | `cost/` |
| 7 | Slide + demo + video dự phòng | slide trong repo (PDF, PPTX, HTML…) hoặc link slide ở form CP4 · link video: ____ |
| + | *Bonus:* người dùng thử | `validation/log.md` |
