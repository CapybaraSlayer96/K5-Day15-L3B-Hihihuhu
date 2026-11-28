# Chi phí khi dùng thật

> Số liệu chạy thật bằng `python run.py simulate --rate-from eval/run-4.csv` từ `cost/personas.yaml` — không điền tay. Tính theo **giá gói trả phí** để phản ánh chi phí khi đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): 3 kiểu người dùng từ khảo sát 31 người lên lịch (`evidence/summary.md`, `spec.md` §2); số lượt hỏi / phiên là *(tự ước tính)*:
  - `dung_it`: tỉ lệ 55% (17/31), 0,33 phiên / người / tháng (1 lần / 3 tháng), 1 lượt hỏi / phiên.
  - `dung_vua`: tỉ lệ 35% (11/31), 0,83 phiên / người / tháng (2–3 lần / 3 tháng), 2 lượt hỏi / phiên.
  - `dung_nhieu`: tỉ lệ 10% (3/31), 1,33 phiên / người / tháng (≥ 4 lần / 3 tháng), 3 lượt hỏi / phiên.
- **Số người dùng thật** 3 kịch bản (khớp mốc cơ sở 1.000 người lên lịch trong `spec.md` §2; cả 3 kịch bản là *(tự ước tính)*): thấp **500** · cơ sở **1.000** · cao **3.000** người lên lịch / tháng.
- **Giá** 4 mức model (USD / 1M token, xem 28/11/2026):
  - `gemini-3.5-flash-lite` (rẻ): vào \$0.25 · ra \$1.50 ([ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing), nhóm Flash Lite tham chiếu mẫu khung)
  - `gemini-4-hydrogen` (mạnh): vào \$1.50 · ra \$7.50 ([ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing), tham chiếu mẫu khung)
  - `gpt-4.1-mini` (rẻ): vào \$0.40 · ra \$1.60 ([openai.com/api/pricing](https://openai.com/api/pricing/))
  - `gpt-4.1` (mạnh): vào \$2.00 · ra \$8.00 ([openai.com/api/pricing](https://openai.com/api/pricing/))
- **Tỉ lệ đạt** dùng để tính: **21/22 (95%)** — lượt `run-4@20261128-085230` (`eval/run-4.csv`).
- **Đo token trên model `gemini-3.5-flash-lite`, tính giá model `gemini-3.5-flash-lite`, `gemini-4-hydrogen`, `gpt-4.1-mini` và `gpt-4.1`** (model khác bộ tách token có thể lệch nhẹ số token thực tế).
- Tỷ giá tham khảo: 1 USD = 25.400 ₫ *(tự ước tính, 28/11/2026)*.

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-1.csv` · run ID `simulate-1@20261128-085836` · **50 phiên** (0/50 lỗi) · `seed: 42` · trace: `traces/simulate-1.jsonl`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 27 | 1 | 2785 | 158 | 1.9 | 5.3 |
| dung_vua | 21 | 2 | 5594 | 330 | 3.8 | 10.8 |
| dung_nhieu | 2 | 3 | 8348 | 450 | 6.0 | 14.0 |

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (500 người) | Chi phí / tháng — cơ sở (1.000 người) | Chi phí / tháng — cao (3.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemini-3.5-flash-lite (vào 0.25 · ra 1.5 \$/1M) | \$0.0014 (≈ 36 ₫) | \$0.0015 (≈ 38 ₫) | \$0.00098 (≈ 25 ₫) | \$0.5435 (≈ 13.805 ₫) | \$1.09 (≈ 27.609 ₫) | \$3.26 (≈ 82.828 ₫) | \$0.0011 (≈ 28 ₫) |
| gemini-4-hydrogen (vào 1.5 · ra 7.5 \$/1M) | \$0.0081 (≈ 206 ₫) | \$0.0085 (≈ 215 ₫) | \$0.0057 (≈ 144 ₫) | \$3.12 (≈ 79.312 ₫) | \$6.25 (≈ 158.624 ₫) | \$18.74 (≈ 475.872 ₫) | \$0.0062 (≈ 159 ₫) |
| gpt-4.1-mini (vào 0.4 · ra 1.6 \$/1M) | \$0.0021 (≈ 52 ₫) | \$0.0022 (≈ 55 ₫) | \$0.0014 (≈ 37 ₫) | \$0.7958 (≈ 20.212 ₫) | \$1.59 (≈ 40.425 ₫) | \$4.77 (≈ 121.274 ₫) | \$0.0016 (≈ 40 ₫) |
| gpt-4.1 (vào 2.0 · ra 8.0 \$/1M) | \$0.0103 (≈ 262 ₫) | \$0.0108 (≈ 274 ₫) | \$0.0072 (≈ 183 ₫) | \$3.98 (≈ 101.062 ₫) | \$7.96 (≈ 202.123 ₫) | \$23.87 (≈ 606.370 ₫) | \$0.0080 (≈ 202 ₫) |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt (21/22 = 95%) — **không coi như đạt 100%**.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): **~20 phút / người lên lịch / tháng** (~340 giờ / tháng ở mốc cơ sở 1.000 người, chưa tính thời gian tránh hỏng chuyến của 3–6 bạn đi cùng).
- Chi phí / người / tháng (cơ sở, model `gemini-3.5-flash-lite`): **\$0.0011 (≈ 28 ₫ / người / tháng)**; tổng mốc cơ sở 1.000 người chỉ **\$1.09 / tháng (≈ 27.609 ₫)** — kể cả dùng model mạnh `gpt-4.1` vẫn chỉ **\$7.96 / tháng (≈ 202.123 ₫)** cho 1.000 người.
- **Kết luận một dòng — đáng làm không:** **Rất đáng làm** — chi phí AI chỉ khoảng 28–202 ₫ / người / tháng (~38 ₫ mỗi lịch thành công với model nhẹ), gần như không đáng kể so với ~20 phút và trải nghiệm cả nhóm 3–6 người tiết kiệm được mỗi tháng.

## 4. Ghi chú vận hành & tối ưu thêm

- **Cần gạt giảm token lớn nhất:** ~90% token nằm ở danh mục 119 địa điểm gửi vào bước `extract()` (~2.600 token vào / lượt); nếu bật prompt caching cho phần danh mục tĩnh hoặc lọc sơ bộ theo từ khoá trước khi gửi, chi phí input có thể giảm thêm ~50–70% *(tự ước tính)*.
- **Chi phí ngoài model:** hạ tầng chính khi chạy thực tế sẽ là VPS / managed Postgres (khoảng \$10–\$20 / tháng *(tự ước tính)*), lớn hơn chi phí API model ở mốc 1.000–3.000 người dùng.
