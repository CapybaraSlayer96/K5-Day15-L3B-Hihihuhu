"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: điền .env (chép từ .env.example), rồi viết nhánh gọi API ở dưới theo docs/connect-model.md
(có ví dụ OpenAI, Claude, model chạy trên máy, và cách nối nhà cung cấp khác). Không dán API key vào file này.
"""
import os

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}

    if MODEL_PROVIDER == "gemini":
        name = MODEL_NAME or "gemini-2.5-flash"
        r = _post("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % name,
                  {"x-goog-api-key": API_KEY},
                  {"systemInstruction": {"parts": [{"text": system or " "}]},
                   "contents": [{"role": "user", "parts": [{"text": user or " "}]}],
                   "generationConfig": {"temperature": 0}})
        u = r.get("usageMetadata", {})
        text = "".join(p.get("text", "") for c in r.get("candidates", [])[:1] for p in c.get("content", {}).get("parts", []))
        return {"text": text, "model": name, "tokens_in": u.get("promptTokenCount", 0),
                "tokens_out": u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)}
    if MODEL_PROVIDER == "anthropic":
        name = MODEL_NAME or "claude-haiku-5-5"
        r = _post("https://api.anthropic.com/v1/messages", {"x-api-key": API_KEY, "anthropic-version": "2023-06-01"},
                  {"model": name, "max_tokens": 1024, "temperature": 0, "system": system or " ",
                   "messages": [{"role": "user", "content": user or " "}]})
        u = r.get("usage", {})
        text = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
        return {"text": text, "model": r.get("model", name), "tokens_in": u.get("input_tokens", 0),
                "tokens_out": u.get("output_tokens", 0)}
    raise NotImplementedError("MODEL_PROVIDER=%s chưa hỗ trợ (dùng gemini | anthropic | fake)" % MODEL_PROVIDER)


def _post(url, headers, body):
    """POST JSON, trả JSON. Lỗi HTTP bay ra kèm nội dung để khung ghi vào cột error."""
    import json
    import urllib.error
    import urllib.request
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"content-type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=60) as f:
            return json.load(f)
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:300])) from None
