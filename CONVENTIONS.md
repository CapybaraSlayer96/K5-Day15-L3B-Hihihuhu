# CONVENTIONS — đặt tên file, folder, biến, branch

> Mọi thành viên và coding agent (Claude Code, Cursor, Codex…) đọc file này trước khi tạo file / branch / code mới.
> Tên do khung BTC cố định thì **giữ nguyên**, không đổi theo quy ước dưới đây.

## 1. Tên cố định của khung — không đổi tên, không di chuyển

`README.md` · `TEAMS.md` · `AGENTS.md` · `canvas.md` · `spec.md` · `run.py` · `Makefile` · `requirements.txt` · `.env.example`
`codebase/{agent,ai,tools,tracing,app}.py` · `eval/{benchmark.csv,metric_spec.yaml,report.md,README.md,run_eval.py}`
`cost/{personas.yaml,cost-estimate.md,simulate.py}` · `data/DATA_CARD.md` · `evidence/{hypothesis,data-mining,summary}.md`
`validation/log.md` · `slides/outline.md` · `docs/{ai-usage,connect-model}.md`

File do `run.py` sinh ra giữ đúng tên khung đặt: `eval/run-N.csv`, `traces/run-N.jsonl`, `cost/simulate-N.csv`, `cost/simulate-N-summary.md`. Không tự đổi tên, không xoá.

## 2. File và folder mới

| Loại | Quy ước | Ví dụ |
|---|---|---|
| Folder | `kebab-case`, chữ thường, không dấu | `data/lesson-notes/` |
| File Python | `snake_case.py` | `codebase/lesson_search.py` |
| File Markdown / CSV / YAML / JSON | `kebab-case` | `evidence/survey-results.md` |
| Phỏng vấn | `evidence/interviews/P1.md`, `P2.md`… (theo template) | `P3.md` |
| Khảo sát gốc còn thông tin cá nhân | tiền tố `raw-` (đã gitignore, không commit) | `evidence/survey/raw-export.csv` |
| Reflection | `reflection/<ten-khong-dau>.md` | `reflection/doan-xuan-duy-bao.md` |
| Slide | `slides/demo-slides.pdf` | — |
| Data BTC gốc | để trong `data-btc/` (đã gitignore) | `data-btc/preclass/` |

Tên file/folder: không dấu tiếng Việt, không khoảng trắng.

## 3. Code Python

| Thứ | Quy ước | Ví dụ |
|---|---|---|
| Biến, hàm, tham số | `snake_case` | `lesson_id`, `search_lesson()` |
| Hằng số | `UPPER_SNAKE_CASE` | `MAX_RESULTS = 5` |
| Class | `PascalCase` | `LessonIndex` |
| Hàm/biến nội bộ | tiền tố `_` | `_load_index()` |
| Công cụ của agent | động từ + danh từ, có `@tool` | `search_lesson`, `get_schedule` |
| Cột CSV / key YAML | `snake_case` | `expected`, `tu_choi` |

- Tên biến, hàm bằng tiếng Anh. Chuỗi trả lời người dùng, docstring, comment được dùng tiếng Việt.
- Giữ nguyên hợp đồng trong `AGENTS.md`: `answer(text)`, `call_model(system, user)`, `@model_call`, `@tool`.
- Docstring ngắn, một dòng cho hàm đơn giản. Comment chỉ giải thích *vì sao*, không kể lịch sử thay đổi.
- Chỉ dùng thư viện chuẩn; thêm thư viện thì ghi vào `requirements.txt`.

## 4. Branch

`main` luôn chạy được (`python run.py` và `python run.py check` không lỗi). Không push thẳng việc dở lên `main`.

Mẫu: `<loai>/<ten-github>-<mo-ta-ngan>` — chữ thường, `kebab-case`, không dấu.

| `<loai>` | Dùng khi | Ví dụ |
|---|---|---|
| `feat` | thêm tính năng / công cụ / luồng | `feat/haivuuu-search-tool` |
| `fix` | sửa lỗi | `fix/minhh25-empty-answer` |
| `eval` | bộ câu thử, metric, chạy lượt đánh giá | `eval/capybaraslayer96-benchmark-v1` |
| `docs` | spec, evidence, canvas, slide, README | `docs/hungvueducation-hash-evidence` |
| `chore` | cấu hình, gitignore, dọn dẹp | `chore/minhh25-gitignore` |

GitHub của nhóm: `minhh25` · `HaiVuuu` · `CapybaraSlayer96` · `hungvueducation-hash` (viết thường trong tên branch).

## 5. Commit

Mẫu: `<loai>: <mô tả ngắn>` — cùng `<loai>` như branch, mô tả tiếng Việt hoặc Anh, ≤ 72 ký tự.
Ví dụ: `feat: thêm công cụ search_lesson`, `eval: chạy lượt 1 (14/24 đạt)`.

- Không commit `.env`, API key, dữ liệu cá nhân thật, nguyên file data BTC.
- Chạy `python run.py check` trước khi push.
- Merge vào `main` qua Pull Request; ít nhất 1 người khác xem trước khi merge.
