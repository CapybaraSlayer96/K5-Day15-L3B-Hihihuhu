# Tóm tắt mô phỏng simulate-1@20261128-085836

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 27 | 1 | 2785 | 158 | 1.9 | 5.3 |
| dung_vua | 21 | 2 | 5594 | 330 | 3.8 | 10.8 |
| dung_nhieu | 2 | 3 | 8348 | 450 | 6.0 | 14.0 |

Tỉ lệ đạt dùng để tính: 21/22 (95%) — lượt run-4@20261128-085230

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-4.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (500 người) | Chi phí / tháng — cơ sở (1.000 người) | Chi phí / tháng — cao (3.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemini-3.5-flash-lite (vào 0.25 · ra 1.5 $/1M) | $0.0014 (≈ 36 ₫) | $0.0015 (≈ 38 ₫) | $0.00098 (≈ 25 ₫) | $0.5435 (≈ 13.805 ₫) | $1.09 (≈ 27.609 ₫) | $3.26 (≈ 82.828 ₫) | $0.0011 (≈ 28 ₫) |
| gemini-4-hydrogen (vào 1.5 · ra 7.5 $/1M) | $0.0081 (≈ 206 ₫) | $0.0085 (≈ 215 ₫) | $0.0057 (≈ 144 ₫) | $3.12 (≈ 79.312 ₫) | $6.25 (≈ 158.624 ₫) | $18.74 (≈ 475.872 ₫) | $0.0062 (≈ 159 ₫) |
| gpt-4.1-mini (vào 0.4 · ra 1.6 $/1M) | $0.0021 (≈ 52 ₫) | $0.0022 (≈ 55 ₫) | $0.0014 (≈ 37 ₫) | $0.7958 (≈ 20.212 ₫) | $1.59 (≈ 40.425 ₫) | $4.77 (≈ 121.274 ₫) | $0.0016 (≈ 40 ₫) |
| gpt-4.1 (vào 2.0 · ra 8.0 $/1M) | $0.0103 (≈ 262 ₫) | $0.0108 (≈ 274 ₫) | $0.0072 (≈ 183 ₫) | $3.98 (≈ 101.062 ₫) | $7.96 (≈ 202.123 ₫) | $23.87 (≈ 606.370 ₫) | $0.0080 (≈ 202 ₫) |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.5) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gemini-3.5-flash-lite. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
- Tỷ giá: 1 USD = 25.400 ₫ (Tỷ giá tham khảo (tự ước tính) · 28/11/2026).
