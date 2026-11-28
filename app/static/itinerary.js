// Lịch trình (TS-06, TS-07): dòng thời gian, bản đồ, điểm bị bỏ, bỏ / ghim / duyệt, sao chép.
(async () => {
  const { api, h, dateVi, getMember, hoursSource, header, toast, CATEGORY } = TS;
  const code = document.body.dataset.code;
  const me = getMember(code);
  const leader = !!(me && me.is_leader);
  header(code);
  const $ = (id) => document.getElementById(id);
  const places = {};
  let deckCards = [];
  let swapOpen = null;
  let group = null;
  let list = Itin.versions(code);
  let shown = list.length - 1;
  let map = null, layer = null;

  function error(msg) { $("itin-error").textContent = msg || ""; $("itin-error").hidden = !msg; }

  try {
    group = await api("GET", "/api/groups/" + code);
    $("trip-line").textContent = `${dateVi(group.config.date)} · ${group.config.start_time}–${group.config.end_time} · xuất phát ${group.config.start_name}` +
      (group.config.start_approximate ? " (xấp xỉ)" : "");
    const deck = await api("GET", `/api/groups/${code}/deck`);
    for (const c of deck.cards) places[c.id] = c;
    deckCards = deck.cards;
    list = Itin.sync(code, await Itin.latest(code));
    shown = list.length - 1;
  } catch (e) {
    error(e.status === 404 ? "Không tìm thấy nhóm." : e.message);
  }

  async function place(id) {
    if (!places[id]) {
      try { places[id] = await api("GET", `/api/places/${encodeURIComponent(id)}` + (group ? "?date=" + group.config.date : "")); }
      catch { places[id] = null; }
    }
    return places[id];
  }

  const STATUS = { draft: ["Bản nháp", "neutral"], approved: ["Đã duyệt", "pos"], stale: ["Hết hiệu lực", "warn"] };

  async function render() {
    const it = list[shown];
    $("version").replaceChildren(...list.map((v, i) => h("option", { value: i, selected: i === shown },
      `Bản ${i + 1} · ${(STATUS[v.status] || [v.status])[0]}` + (v.mock ? " · mẫu" : ""))));
    $("version").disabled = list.length < 2;
    if (!it) {
      $("timeline").replaceChildren(h("li.empty-line", {}, leader
        ? h("span", {}, "Chưa có lịch. ", h("a", { href: `/g/${code}/lobby` }, "Về phòng chờ để bấm Xếp lịch"))
        : "Trưởng nhóm chưa xếp lịch. Mở lại trang này sau khi trưởng nhóm bấm Xếp lịch."));
      $("dropped").replaceChildren();
      $("copy").disabled = true;
      $("approve").hidden = true;
      drawMap([]);
      return;
    }
    const [label, tone] = STATUS[it.status] || [it.status, "neutral"];
    $("status").replaceChildren(h("span.pill." + tone, {}, label));
    $("mock-banner").hidden = !it.mock;
    const editable = leader && it.status === "draft" && shown === list.length - 1;
    $("approve").hidden = !leader;
    $("approve").disabled = !editable;
    $("copy").disabled = false;

    await Promise.all([...it.items, ...it.dropped].map((x) => place(x.id)));

    if (it.violations && it.violations.length) error("Bộ kiểm báo vi phạm: " + it.violations.join("; "));
    else error("");

    const order = it.items.map((x) => x.id);
    const n = order.length;
    const movable = editable && n > 1;
    $("move-hint").hidden = !movable;
    $("timeline").replaceChildren(...(n ? it.items.flatMap((x, i) => {
      const p = places[x.id];
      const li = h("li.stop" + (movable ? ".movable" : ""), { "data-id": x.id, draggable: movable ? "true" : null },
        movable ? h("span.grip", { title: "Kéo để đổi thứ tự", "aria-hidden": "true" }) : null,
        h("span.num", { "aria-hidden": "true" }, String(i + 1)),
        h("div.stop-main", {},
          x.travel_min != null ? h("p.travel", {}, `Đi ${x.travel_min} phút (ước tính)`) : null,
          h("p.stop-time", {}, `${x.arrive}–${x.leave}`),
          h("h3", {}, x.name),
          h("p.muted.small", {}, p ? `Giờ mở cửa: ${p.opening_hours || "chưa có dữ liệu giờ"} · nguồn ${hoursSource(p)}` : ""),
          x.no_hours ? h("span.pill.warn", {}, "chưa có dữ liệu giờ, chưa kiểm") : null),
        editable ? h("div.stop-tools", {},
          n > 1 ? h("button.btn.small.move", { type: "button", disabled: i === 0, "aria-label": `Đưa ${x.name} lên trước`,
            onclick: () => move(order, i, i - 1) }, arrow("up")) : null,
          n > 1 ? h("button.btn.small.move", { type: "button", disabled: i === n - 1, "aria-label": `Đưa ${x.name} xuống sau`,
            onclick: () => move(order, i, i + 1) }, arrow("down")) : null,
          h("button.btn.small", { type: "button", "aria-expanded": swapOpen === x.id ? "true" : "false",
            onclick: () => { swapOpen = swapOpen === x.id ? null : x.id; render(); } }, "Đổi địa điểm"),
          h("button.btn.small", { type: "button", onclick: () => act("drop", x.id) }, "Bỏ điểm")) : null);
      if (movable) { li.querySelector(".grip").innerHTML = GRIP; dragRow(li, order); }
      return editable && swapOpen === x.id ? [li, swapPanel(it, x)] : [li];
    }) : [h("li.empty-line", {}, "Không có điểm nào xếp vừa khung giờ. Xem gợi ý ở danh sách điểm bị bỏ.")]));

    $("dropped").replaceChildren(...(it.dropped.length ? it.dropped.map((d) => {
      const [reason, hint] = d.reason.split(/\s+—\s+/);
      return h("li", {},
        h("div", {}, h("strong", {}, d.name), h("p", {}, reason), hint ? h("p.muted.small", {}, "Gợi ý: " + hint) : null),
        editable ? h("button.btn.small", { type: "button", onclick: () => act("pin", d.id) }, "Ghim") : null);
    }) : [h("li.muted", {}, "Không có điểm nào bị bỏ.")]));

    drawMap(it.items);
  }

  function drawMap(items) {
    if (!window.L) { $("map").replaceChildren(h("p.muted", {}, "Không tải được bản đồ.")); return; }
    if (!map) {
      map = L.map("map", { scrollWheelZoom: false });
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap contributors" }).addTo(map);
      layer = L.layerGroup().addTo(map);
    }
    layer.clearLayers();
    const pts = [];
    if (group) {
      const s = group.config.start_xy;
      pts.push(s);
      L.marker(s, { icon: L.divIcon({ className: "pin start", html: "XP", iconSize: [30, 30] }), title: "Xuất phát" })
        .bindTooltip("Xuất phát: " + group.config.start_name).addTo(layer);
    }
    items.forEach((x, i) => {
      const p = places[x.id];
      if (!p || p.lat == null) return;
      pts.push([p.lat, p.lng]);
      L.marker([p.lat, p.lng], { icon: L.divIcon({ className: "pin", html: String(i + 1), iconSize: [30, 30] }), title: x.name })
        .bindTooltip(`${i + 1}. ${x.name} · ${x.arrive}–${x.leave}`).addTo(layer);
    });
    if (pts.length > 1) L.polyline(pts, { color: getComputedStyle(document.body).getPropertyValue("--accent").trim(), weight: 4 }).addTo(layer);
    if (pts.length) map.fitBounds(pts, { padding: [40, 40], maxZoom: 15 });
    else map.setView([21.0285, 105.8542], 13);
  }

  const GRIP = '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="6" r="1.6"/><circle cx="15" cy="6" r="1.6"/><circle cx="9" cy="12" r="1.6"/><circle cx="15" cy="12" r="1.6"/><circle cx="9" cy="18" r="1.6"/><circle cx="15" cy="18" r="1.6"/></svg>';
  function arrow(dir) {
    const span = h("span", { "aria-hidden": "true" });
    span.innerHTML = dir === "up"
      ? '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 15 6-6 6 6"/></svg>'
      : '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>';
    return span;
  }

  function move(order, from, to) {
    if (to < 0 || to >= order.length || from === to) return;
    const next = [...order];
    next.splice(to, 0, next.splice(from, 1)[0]);
    act("reorder", undefined, { order: next });
  }

  // Kéo thả trên máy tính; điện thoại và bàn phím dùng nút lên / xuống.
  let dragId = null;
  // Trình duyệt không tự cuộn khi kéo thả HTML5: con trỏ sát mép trên / dưới thì tự cuộn trang.
  let dragY = null, scrollTimer = null;
  const EDGE = 90;
  document.addEventListener("dragover", (ev) => { if (dragId) dragY = ev.clientY; });
  function autoScroll() {
    if (!dragId) { scrollTimer = null; return; }
    if (dragY != null) {
      if (dragY < EDGE) window.scrollBy(0, -Math.ceil((EDGE - dragY) / 4));
      else if (dragY > innerHeight - EDGE) window.scrollBy(0, Math.ceil((dragY - innerHeight + EDGE) / 4));
    }
    scrollTimer = requestAnimationFrame(autoScroll);
  }
  function dragRow(li, order) {
    li.addEventListener("dragstart", (ev) => {
      dragId = li.dataset.id;
      dragY = null;
      document.body.classList.add("itin-dragging");
      if (!scrollTimer) scrollTimer = requestAnimationFrame(autoScroll);
      li.classList.add("dragging");
      ev.dataTransfer.effectAllowed = "move";
      ev.dataTransfer.setData("text/plain", dragId);
    });
    li.addEventListener("dragend", () => {
      dragId = null;
      document.body.classList.remove("itin-dragging");
      document.querySelectorAll(".stop").forEach((x) => x.classList.remove("dragging", "drop-before", "drop-after"));
    });
    li.addEventListener("dragover", (ev) => {
      if (!dragId || dragId === li.dataset.id) return;
      ev.preventDefault();
      const r = li.getBoundingClientRect();
      const after = ev.clientY > r.top + r.height / 2;
      li.classList.toggle("drop-after", after);
      li.classList.toggle("drop-before", !after);
    });
    li.addEventListener("dragleave", () => li.classList.remove("drop-before", "drop-after"));
    li.addEventListener("drop", (ev) => {
      ev.preventDefault();
      const after = li.classList.contains("drop-after");
      li.classList.remove("drop-before", "drop-after");
      if (!dragId || dragId === li.dataset.id) return;
      const next = order.filter((id) => id !== dragId);
      next.splice(next.indexOf(li.dataset.id) + (after ? 1 : 0), 0, dragId);
      if (next.join() !== order.join()) act("reorder", undefined, { order: next });
    });
  }

  // Danh sách radio các điểm trong bộ thẻ chưa có trong lịch, mở ngay dưới điểm cần đổi.
  function swapPanel(it, x) {
    const inPlan = new Set(it.items.map((i) => i.id));
    const score = Object.fromEntries((it.votes || []).map((v) => [v.place_id, v]));
    const options = deckCards.filter((c) => !inPlan.has(c.id) && c.hours_status !== "closed")
      .sort((a, b) => ((score[b.id]?.like_score ?? -1) - (score[a.id]?.like_score ?? -1)) || a.name.localeCompare(b.name, "vi"));
    const name = "swap-" + x.id;
    const apply = h("button.btn.primary.small", { type: "button", disabled: true }, "Đổi");
    const panel = h("li.swap-panel", {},
      options.length ? h("fieldset", {},
        h("legend", {}, `Đổi ${x.name} sang`),
        options.map((c) => {
          const v = score[c.id];
          return h("label.swap-option", {},
            h("input", { type: "radio", name, value: c.id, onchange: () => (apply.disabled = false) }),
            h("span", {}, c.name),
            h("span.muted.small", {}, v ? `${v.likes}/${v.swiped} thích` : (CATEGORY[c.category] || "")));
        })) : h("p.muted", {}, "Không còn điểm nào trong bộ thẻ để đổi."),
      h("div.row", {},
        options.length ? apply : null,
        h("button.btn.small", { type: "button", onclick: () => { swapOpen = null; render(); } }, "Huỷ")));
    apply.addEventListener("click", () => {
      const picked = panel.querySelector("input:checked");
      if (picked) act("replace", x.id, { new_place_id: picked.value });
    });
    return panel;
  }

  async function act(action, place_id, extra) {
    const it = list[shown];
    error("");
    document.body.classList.add("itin-busy");
    try {
      list = await Itin.patch(code, it, me.member_id, action, place_id, extra);
      shown = list.length - 1;
      swapOpen = null;
      await render();
      if (action === "approve") toast("Đã duyệt lịch", "Cả nhóm mở trang Lịch trình sẽ thấy bản này. Lịch giờ chỉ xem, không sửa được nữa.");
    } catch (e) {
      error(e.message);
    } finally {
      document.body.classList.remove("itin-busy");
    }
  }
  window.addEventListener("themechange", () => render());

  function plainText(it) {
    const lines = [`Lịch TripSwipe nhóm ${code}`];
    if (group) lines.push(`${dateVi(group.config.date)}, ${group.config.start_time}–${group.config.end_time}, xuất phát ${group.config.start_name}`);
    if (it.mock) lines.push("(Dữ liệu mẫu, chưa phải lịch thật)");
    lines.push("");
    it.items.forEach((x, i) => {
      const p = places[x.id];
      lines.push(`${i + 1}. ${x.arrive}–${x.leave} ${x.name}` + (x.travel_min != null ? ` (đi ${x.travel_min} phút, ước tính)` : ""));
      if (p) lines.push(`   Giờ mở cửa: ${p.opening_hours || "chưa có dữ liệu giờ"} — nguồn: ${hoursSource(p)}`);
    });
    if (it.dropped.length) {
      lines.push("", "Không đi:");
      for (const d of it.dropped) lines.push(`- ${d.name}: ${d.reason}`);
    }
    lines.push("", "Lưu ý: thời gian đi là ước tính.");
    return lines.join("\n");
  }

  $("copy").addEventListener("click", async () => {
    const text = plainText(list[shown]);
    try { await navigator.clipboard.writeText(text); }
    catch {
      const ta = h("textarea", { "aria-hidden": "true" }, text);
      document.body.append(ta); ta.select(); document.execCommand("copy"); ta.remove();
    }
    $("copy").textContent = "Đã sao chép";
    setTimeout(() => ($("copy").textContent = "Sao chép"), 2000);
  });
  $("approve").addEventListener("click", () => act("approve"));
  $("version").addEventListener("change", (e) => { shown = Number(e.target.value); render(); });

  render();
})();
