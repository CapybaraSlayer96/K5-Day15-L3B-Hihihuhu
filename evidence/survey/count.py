"""Đếm số chính của khảo sát từ results.csv (bản đã ẩn danh). Chạy: python evidence/survey/count.py"""
import csv
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
rows = list(csv.DictReader(open(os.path.join(os.path.dirname(__file__), "results.csv"), encoding="utf-8-sig")))
cols = list(rows[0])
Q_ROLE, Q_FREQ, Q_TOOLS, Q_TIME, Q_ISSUES, _, Q_ANNOY = cols[1:8]
plan = [r for r in rows if r[Q_ROLE] == "Có"]  # mẫu số: người từng lên lịch cho nhóm trong 3 tháng qua
n = len(plan)


def pct(k):
    return "%d/%d (%d%%)" % (k, n, round(100 * k / n))


def has(r, *keys):
    return any(k in r[Q_ISSUES] for k in keys)


print("Phản hồi hợp lệ:", len(rows), "· người lên lịch cho nhóm (mẫu số):", n)
print("Gặp ≥1 trong: đi vòng / đến nơi đóng cửa / đóng đúng hôm đó / bỏ lỡ:",
      pct(sum(has(r, "Đi vòng", "đã đóng cửa", "Điểm đóng cửa đúng", "Bỏ lỡ") for r in plan)))
print("Đến nơi đã đóng / chưa mở hoặc đóng đúng hôm đó:", pct(sum(has(r, "đã đóng cửa", "Điểm đóng cửa đúng") for r in plan)))
for label, key in [("Đi vòng vèo", "Đi vòng"), ("Xếp quá nhiều điểm phải bỏ", "Xếp quá nhiều"),
                   ("Cả nhóm khó thống nhất", "khó thống nhất"), ("Mất quá nhiều thời gian lên lịch", "Mất quá nhiều thời gian")]:
    print(label + ":", pct(sum(has(r, key) for r in plan)))
order = ["Dưới 15 phút", "15–30 phút", "30–60 phút", "1–2 giờ", "2–3 giờ", "Trên 3 giờ"]
t = sorted(order.index(r[Q_TIME]) for r in plan)
print("Thời gian tìm + xếp lịch, trung vị:", order[t[(n - 1) // 2]], "· ≥1 giờ:", pct(sum(i >= 3 for i in t)))
print("Mức phiền ≥4/5:", pct(sum(int(r[Q_ANNOY]) >= 4 for r in plan)))
freq = {}
for r in plan:
    freq[r[Q_FREQ]] = freq.get(r[Q_FREQ], 0) + 1
print("Số lần lên lịch / 3 tháng:", freq)
