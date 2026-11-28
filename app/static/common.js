// Tiện ích dùng chung: gọi API, lưu thành viên theo mã nhóm, dựng DOM an toàn.
const TS = (() => {
  class ApiError extends Error {
    constructor(status, detail) {
      super(typeof detail === "string" ? detail : "Dữ liệu chưa hợp lệ.");
      this.status = status;
      this.detail = detail;
    }
  }

  async function api(method, url, body) {
    const opts = { method, headers: {} };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    let res;
    try {
      res = await fetch(url, opts);
    } catch {
      throw new ApiError(0, "Không kết nối được máy chủ, hãy thử lại.");
    }
    const data = await res.json().catch(() => null);
    if (!res.ok) throw new ApiError(res.status, data && data.detail !== undefined ? data.detail : res.statusText);
    return data;
  }

  const key = (code) => "tripswipe:" + code.toUpperCase();
  function getMember(code) {
    try { return JSON.parse(localStorage.getItem(key(code))); } catch { return null; }
  }
  function setMember(code, value) {
    try { localStorage.setItem(key(code), JSON.stringify(value)); } catch { /* chế độ riêng tư */ }
  }
  function clearMember(code) {
    try { localStorage.removeItem(key(code)); } catch { /* bỏ qua */ }
  }
  function getJSON(name, fallback) {
    try { return JSON.parse(localStorage.getItem(name)) ?? fallback; } catch { return fallback; }
  }
  function setJSON(name, value) {
    try { localStorage.setItem(name, JSON.stringify(value)); } catch { /* bỏ qua */ }
  }

  // h("p.cls", {attr}, ...children): chuỗi con luôn thành textNode, không dùng innerHTML.
  function h(tag, attrs, ...kids) {
    const [name, ...classes] = tag.split(".");
    const node = document.createElement(name || "div");
    if (classes.length) node.className = classes.join(" ");
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
      else if (k === "text") node.textContent = v;
      else node.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat()) {
      if (kid === null || kid === undefined || kid === false) continue;
      node.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
    }
    return node;
  }

  const vnd = (n) => (n === null || n === undefined ? "chưa có giá" : n.toLocaleString("vi-VN") + "đ");

  const todayHanoi = () => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Ho_Chi_Minh" }).format(new Date());

  function dateVi(iso) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("vi-VN", { weekday: "long", day: "2-digit", month: "2-digit", year: "numeric" });
  }

  const CATEGORY = {
    landmark: "Danh thắng", culture: "Văn hoá", nature: "Thiên nhiên",
    food_drink: "Ăn uống", show_experience: "Trải nghiệm",
  };

  function hoursSource(place) {
    const v = place && place.verification;
    return (v && (v.official_source || v.source)) || "chưa rõ nguồn";
  }

  // Cập nhật thanh trên cùng: mã nhóm và biệt danh.
  function header(code) {
    const m = code && getMember(code);
    const slot = document.getElementById("who");
    if (slot && m) slot.textContent = m.nickname + (m.is_leader ? " · trưởng nhóm" : "");
  }

  return { api, ApiError, getMember, setMember, clearMember, getJSON, setJSON, h, vnd, todayHanoi, dateVi, CATEGORY, hoursSource, header };
})();
