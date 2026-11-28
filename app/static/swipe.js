// Quẹt thẻ 2 lớp (TS-04): tổng quan, kéo lên xem chi tiết, phải = thích, trái = bỏ qua, hoàn tác.
(() => {
  const { api, h, vnd, dateVi, getMember, clearMember, CATEGORY, hoursSource, header } = TS;
  const code = document.body.dataset.code;
  const me = getMember(code);
  if (!me) return location.replace("/join?code=" + code);
  header(code);

  const $ = (id) => document.getElementById(id);
  const stage = $("stage");
  const detail = $("detail");
  const btn = { like: $("btn-like"), skip: $("btn-skip"), detail: $("btn-detail"), undo: $("btn-undo") };
  const histKey = "tripswipe:history:" + code;
  let history = [];
  try { history = JSON.parse(sessionStorage.getItem(histKey)) || []; } catch { /* bỏ qua */ }
  let deck = null;
  let group = null;
  let current = null;
  let busy = false;
  let preferId = null;

  const saveHistory = () => { try { sessionStorage.setItem(histKey, JSON.stringify(history)); } catch { /* bỏ qua */ } };

  function error(msg) {
    $("swipe-error").textContent = msg || "";
    $("swipe-error").hidden = !msg;
  }

  function onAuthError(e) {
    if (e.status === 403) { clearMember(code); location.replace("/join?code=" + code); return true; }
    if (e.status === 409) { readOnly(e.message); return true; }
    return false;
  }

  function readOnly(msg) {
    Object.values(btn).forEach((b) => (b.disabled = true));
    stage.replaceChildren(h("div.empty", {}, h("h2", {}, "Chỉ xem"), h("p", {}, msg),
      h("a.btn.primary", { href: "/g/" + code + "/itinerary" }, "Xem lịch trình")));
  }

  function hoursBadge(card) {
    if (card.hours_status === "unknown" || card.opening_windows == null) return h("span.pill.warn", {}, "chưa có dữ liệu giờ");
    if (card.hours_status === "closed") return h("span.pill.neg", {}, "Đóng vào ngày đi");
    const spans = card.opening_windows.map((w) => w.open + "–" + w.close).join(", ");
    return h("span.pill.pos", {}, "Mở vào ngày đi · " + spans);
  }

  function image(card, cls) {
    const frame = h("div." + cls, {});
    if (card.image_url) {
      const img = h("img", { src: card.image_url, alt: card.name, loading: "lazy", draggable: "false", referrerpolicy: "no-referrer" });
      img.addEventListener("error", () => { img.remove(); frame.classList.add("broken"); frame.append(h("span.muted.small", {}, "Chưa tải được ảnh")); });
      frame.append(img);
    } else {
      frame.classList.add("broken");
      frame.append(h("span.muted.small", {}, "Chưa có ảnh"));
    }
    return frame;
  }

  function renderCard(card) {
    const el = h("div.card", { tabindex: "0", "aria-label": card.name + ". Kéo phải để thích, trái để bỏ qua." },
      image(card, "card-img"),
      h("div.card-body", {},
        h("div.card-meta", {}, h("span", {}, CATEGORY[card.category] || card.category), h("span", {}, card.district),
          card.rating != null ? h("span.rating", {}, "★ " + card.rating.toLocaleString("vi-VN")) : null),
        h("h2.card-name", {}, card.name),
        h("p.card-hook", {}, card.card_hook || ""),
        h("div.tags", {}, (card.swipe_tags || []).map((t) => h("span.tag", {}, t))),
        h("p.card-line", {}, h("strong", {}, card.price_range || vnd(card.price_max_vnd)), " · ", hoursBadge(card)),
        card.ai_reason ? h("p.reason", {}, h("span.muted", {}, deck.source === "ai" ? "Lý do AI chọn: " : "Lý do vào bộ thẻ: "), card.ai_reason) : null),
      h("div.stamp.like-stamp", { "aria-hidden": "true" }, "Thích"),
      h("div.stamp.skip-stamp", { "aria-hidden": "true" }, "Bỏ qua"));
    attachDrag(el);
    return el;
  }

  function attachDrag(el) {
    let sx = 0, sy = 0, dx = 0, dy = 0, dragging = false;
    el.addEventListener("pointerdown", (e) => {
      if (busy || e.button !== 0) return;
      dragging = true; sx = e.clientX; sy = e.clientY; dx = dy = 0;
      el.setPointerCapture(e.pointerId);
      el.classList.add("dragging");
    });
    el.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      dx = e.clientX - sx; dy = e.clientY - sy;
      el.style.transform = `translate(${dx}px, ${Math.min(dy, 40)}px) rotate(${dx / 20}deg)`;
      el.style.setProperty("--like", Math.max(0, Math.min(1, dx / 120)));
      el.style.setProperty("--skip", Math.max(0, Math.min(1, -dx / 120)));
    });
    const end = () => {
      if (!dragging) return;
      dragging = false;
      el.classList.remove("dragging");
      const limit = Math.min(140, el.offsetWidth / 3);
      if (dx > limit) return vote(true);
      if (dx < -limit) return vote(false);
      el.style.transform = "";
      el.style.setProperty("--like", 0);
      el.style.setProperty("--skip", 0);
      if (dy < -80 && Math.abs(dx) < 60) openDetail();
    };
    el.addEventListener("pointerup", end);
    el.addEventListener("pointercancel", end);
  }

  function render() {
    $("remaining").textContent = deck.remaining;
    $("total").textContent = deck.total;
    const open = deck.cards.filter((c) => !c.swiped);
    current = open.find((c) => c.id === preferId) || open[0] || null;
    preferId = null;
    btn.undo.disabled = !history.length;
    renderHistory();
    for (const k of ["like", "skip", "detail"]) btn[k].disabled = !current;
    if (!current) {
      const msg = deck.total ? "Bạn đã quẹt hết bộ thẻ." : "Bộ thẻ chưa có địa điểm nào hợp lệ với cấu hình nhóm.";
      stage.replaceChildren(h("div.empty", {}, h("h2", {}, msg),
        h("p.muted", {}, "Sang phòng chờ để xem cả nhóm đã xong chưa."),
        h("a.btn.primary", { href: "/g/" + code + "/lobby" }, "Sang phòng chờ")));
      return;
    }
    const next = open.find((c) => c !== current);
    const nodes = [];
    if (next) nodes.push(h("div.card.behind", { "aria-hidden": "true" }, image(next, "card-img")));
    nodes.push(renderCard(current));
    stage.replaceChildren(...nodes);
  }

  function renderHistory() {
    const byId = Object.fromEntries((deck?.cards || []).map((c) => [c.id, c]));
    $("history").replaceChildren(...history.slice(-6).reverse().map((it) =>
      h("li", {}, h("span.pill." + (it.liked ? "pos" : "neutral"), {}, it.liked ? "Thích" : "Bỏ qua"), " ", byId[it.id]?.name || it.id)));
  }

  async function load() {
    try {
      deck = await api("GET", `/api/groups/${code}/deck?member_id=${encodeURIComponent(me.member_id)}`);
    } catch (e) {
      if (onAuthError(e)) return;
      $("stage-msg").classList.remove("skel", "skel-card");
      $("stage-msg").textContent = e.message;
      return;
    }
    $("deck-warn").replaceChildren(...deck.warnings.map((w) => h("li", {}, w)));
    render();
  }

  async function vote(liked) {
    if (!current || busy) return;
    busy = true;
    error("");
    const card = current;
    const el = stage.querySelector(".card:not(.behind)");
    if (el) { el.classList.add(liked ? "fly-right" : "fly-left"); }
    try {
      await api("POST", `/api/groups/${code}/swipes`, { member_id: me.member_id, place_id: card.id, liked });
      history.push({ id: card.id, liked });
      saveHistory();
      closeDetail();
    } catch (e) {
      if (!onAuthError(e)) error(e.message);
    }
    busy = false;
    await load();
  }

  async function undo() {
    const last = history[history.length - 1];
    if (!last || busy) return;
    busy = true;
    error("");
    try {
      await api("DELETE", `/api/groups/${code}/swipes`, { member_id: me.member_id, place_id: last.id });
      history.pop();
      saveHistory();
      preferId = last.id;
    } catch (e) {
      if (!onAuthError(e)) error(e.message);
    }
    busy = false;
    await load();
  }

  function section(title, ...content) {
    const kids = content.flat().filter(Boolean);
    return kids.length ? h("section", {}, h("h3", {}, title), ...kids) : null;
  }

  async function openDetail() {
    if (!current) return;
    const card = current;
    detail.hidden = false;
    requestAnimationFrame(() => detail.classList.add("open"));
    const body = $("detail-body");
    body.replaceChildren(h("p.muted", {}, "Đang tải chi tiết…"));
    detail.focus();
    let p;
    try {
      const date = card.hours_for_date || (group && group.config.date);
      p = await api("GET", `/api/places/${encodeURIComponent(card.id)}` + (date ? "?date=" + date : ""));
    } catch (e) {
      body.replaceChildren(h("p.form-error", {}, e.message));
      return;
    }
    if (current !== card) return;
    const rs = p.review_summary || {};
    const WEEKDAY = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]; // 0 = Thứ 2, như date.weekday()
    const closedWeek = (p.closed_weekdays || []).map((d) => WEEKDAY[d] ?? d).join(", ");
    const closedDays = (p.closed_days || []).join(", ");
    body.replaceChildren(
      h("h2", {}, p.name),
      h("p.muted", {}, [CATEGORY[p.category] || p.category, p.district].join(" · ")),
      h("p.card-line", {}, hoursBadge(p)),
      section("Mô tả", p.description ? h("p", {}, p.description) : null),
      section("Vì sao nên đi", p.why_visit ? h("p", {}, p.why_visit) : null),
      section("Nên làm gì", (p.what_to_do || []).length ? h("ul", {}, p.what_to_do.map((t) => h("li", {}, t))) : null),
      h("dl.facts", {},
        h("dt", {}, "Giờ mở cửa"), h("dd", {}, p.opening_hours || "chưa có dữ liệu giờ"),
        h("dt", {}, "Ngày đóng"), h("dd", {}, [closedWeek, closedDays].filter(Boolean).join("; ") || "Không ghi ngày đóng"),
        h("dt", {}, "Thời lượng gợi ý"), h("dd", {}, p.estimated_duration_mins != null ? p.estimated_duration_mins + " phút" : "chưa có"),
        h("dt", {}, "Giá"), h("dd", {}, p.price_range || vnd(p.price_max_vnd)),
        h("dt", {}, "Địa chỉ"), h("dd", {}, p.address || "chưa có"),
        h("dt", {}, "Nguồn xác minh"), h("dd", {}, hoursSource(p))),
      section("Mẹo", p.tips ? h("p", {}, p.tips) : null),
      section("Tóm tắt review",
        (rs.pros || []).length ? h("ul.pros", {}, rs.pros.map((t) => h("li", {}, t))) : null,
        (rs.cons || []).length ? h("ul.cons", {}, rs.cons.map((t) => h("li", {}, t))) : null),
      p.google_maps_url ? h("p", {}, h("a", { href: p.google_maps_url, target: "_blank", rel: "noopener" }, "Mở trên Google Maps")) : null);
  }

  function closeDetail() {
    detail.classList.remove("open");
    detail.hidden = true;
  }

  btn.like.addEventListener("click", () => vote(true));
  btn.skip.addEventListener("click", () => vote(false));
  btn.undo.addEventListener("click", undo);
  btn.detail.addEventListener("click", openDetail);
  $("detail-close").addEventListener("click", () => { closeDetail(); btn.detail.focus(); });
  document.addEventListener("keydown", (e) => {
    if (e.target.matches("input, textarea, select")) return;
    if (e.key === "Escape" && !detail.hidden) return closeDetail();
    if (e.key === "ArrowRight") vote(true);
    else if (e.key === "ArrowLeft") vote(false);
    else if (e.key === "ArrowUp") { e.preventDefault(); openDetail(); }
    else if (e.key === "z" && (e.ctrlKey || e.metaKey)) undo();
  });

  api("GET", "/api/groups/" + code).then((g) => {
    group = g;
    $("trip-line").textContent = dateVi(g.config.date) + " · " + g.config.start_time + "–" + g.config.end_time;
  }).catch(() => {});
  load();
})();
