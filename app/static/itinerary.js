// Lịch trình (TS-06, TS-07): dòng thời gian, bản đồ, điểm bị bỏ, bỏ / ghim / duyệt, sao chép.
(async () => {
  const { api, h, dateVi, getMember, hoursSource, header } = TS;
  const code = document.body.dataset.code;
  const me = getMember(code);
  const leader = !!(me && me.is_leader);
  header(code);
  const $ = (id) => document.getElementById(id);
  const places = {};
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
        : "Chưa có lịch trên trình duyệt này. Trưởng nhóm sẽ gửi bản sao chép khi đã duyệt."));
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

    $("timeline").replaceChildren(...(it.items.length ? it.items.map((x, i) => {
      const p = places[x.id];
      return h("li.stop", {},
        h("span.num", { "aria-hidden": "true" }, String(i + 1)),
        h("div.stop-main", {},
          x.travel_min != null ? h("p.travel", {}, `Đi ${x.travel_min} phút (ước tính)`) : null,
          h("p.stop-time", {}, `${x.arrive}–${x.leave}`),
          h("h3", {}, x.name),
          h("p.muted.small", {}, p ? `Giờ mở cửa: ${p.opening_hours || "chưa có dữ liệu giờ"} · nguồn ${hoursSource(p)}` : ""),
          x.no_hours ? h("span.pill.warn", {}, "chưa có dữ liệu giờ, chưa kiểm") : null),
        editable ? h("button.btn.small", { type: "button", onclick: () => act("drop", x.id) }, "Bỏ điểm") : null);
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
    if (pts.length > 1) L.polyline(pts, { color: getComputedStyle(document.body).getPropertyValue("--accent").trim(), weight: 3 }).addTo(layer);
    if (pts.length) map.fitBounds(pts, { padding: [40, 40], maxZoom: 15 });
    else map.setView([21.0285, 105.8542], 13);
  }

  async function act(action, place_id) {
    const it = list[shown];
    error("");
    try {
      list = await Itin.patch(code, it, me.member_id, action, place_id);
      shown = list.length - 1;
      await render();
    } catch (e) {
      error(e.message);
    }
  }

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
