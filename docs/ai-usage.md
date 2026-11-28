# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Claude Code | Viết `codebase/places.py`, `planner.py`, `tools.py`, `agent.py`, `ai.py`, test | Bảo chạy 22 câu thử + `tests/test_core.py`, duyệt từng commit | Bảo |
| Backend B1–B3 | Codex | Viết FastAPI/Postgres, Docker, API nhóm/quẹt, JSON mẫu và integration test | Codex chạy 8 test Postgres thật, core test, `run.py check`, build/chạy Docker; Minh cần review trước commit | Minh |
| Prompt / thiết kế lời gọi mô hình | Claude Code / Antigravity | Viết prompt đọc yêu cầu, prompt lý do chọn, `codebase/group.py` (`build_deck`, `plan_group`), cải tiến `extract()`, và cấu hình `cost/personas.yaml` | Bảo sửa sau lượt thử; Hải kiểm tra hợp đồng A3, chạy `tests/test_core.py`, `run.py check` và rà số liệu `personas.yaml` khớp `spec.md` §2 | Bảo, Hải |
| Đào data (viết script đếm, gợi ý nhãn) | Claude Code | Viết `evidence/survey/count.py`, tra giờ mở cửa trang chính thức | Đếm lại khớp bảng tổng hợp Google Form; 2 phiếu loại có lý do | Bảo |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | Claude Code | Soạn nháp 22 câu từ kịch bản §5 và trích khảo sát | Kết quả mong đợi đối chiếu giờ chính thức; `source` ghi rõ `tu_viet` / `data_that` | Bảo |
| Sinh data `synthetic` (nếu có) | Không dùng | — | — | — |
| Chấm cột `pass` bằng LLM (nếu có) | Claude Sonnet (agent độc lập) | Chỉ làm người chấm thử thứ hai cho 5 output (BA9) | Khớp người chấm 1: 5/5 câu, 29/30 ô; cột `pass` các lượt do người chấm | Bảo |
| Slide, văn bản | Claude Code | Soạn nháp spec, PRD, data card, TASKS, summary | Số liệu kiểm bằng `count.py` / `score`; trích dẫn đối chiếu nguyên văn phiếu | Bảo, Hùng |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
