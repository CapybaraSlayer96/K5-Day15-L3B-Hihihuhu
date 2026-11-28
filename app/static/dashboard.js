// Bảng tổng quan nhóm: bản đồ lộ trình, dòng thời gian đồng bộ, số tóm tắt, điểm bị bỏ, phiếu.
(async () => {
  const { api, h, vnd, dateVi, header } = TS;
  const code = document.body.dataset.code;
  header(code);
  const $ = (id) => document.getElementById(id);
  const MODE = { xe_may: "Xe máy", o_to: "Ô tô", di_bo: "Đi bộ" };
  const HOURS = { open: ["Mở cửa ngày đi", "pos"], closed: ["Đóng cửa ngày đi", "neg"], unknown: ["Chưa có dữ liệu giờ", "warn"] };
  const accent = getComputedStyle(document.body).getPropertyValue("--accent").trim();
  const places = {};
  const markers = [];
  const lines = [];

  function error(msg) { $("dash-error").textContent = msg || ""; $("dash-error").hidden = !msg; }
  const hue = (s) => { let x = 0; for (const c of s) x = (x * 31 + c.codePointAt(0)) % 360; return x; };

  let group, progress, itin;
  try {
    [group, progress, itin] = await Promise.all([
      api("GET", "/api/groups/" + code),
      api("GET", `/api/groups/${code}/progress`).catch(() => null),
      Itin.latest(code),
    ]);
    const deck = await api("GET", `/api/groups/${code}/deck`).catch(() => ({ cards: [] }));
    for (const c of deck.cards) places[c.id] = c;
  } catch (e) {
    error(e.status === 404 ? "Không tìm thấy nhóm." : e.message);
    $("trip").textContent = "";
    return;
  }

  const cfg = group.config;
  $("trip").replaceChildren(
    `${dateVi(cfg.date)} · ${cfg.start_time}–${cfg.end_time}`,
    h("br"),
    h("span.muted", {}, `Xuất phát ${cfg.start_name}${cfg.start_approximate ? " (xấp xỉ)" : ""} · ${MODE[cfg.mode] || cfg.mode}`));

  const total = progress ? progress.total_cards : 0;
  $("members").replaceChildren(...(progress ? progress.members : group.members).map((m) =>
    h("li.dash-member", {},
      h("span.avatar", { "aria-hidden": "true", style: `--hue:${hue(m.nickname)}` }, m.nickname.slice(0, 1).toUpperCase()),
      h("span", {}, m.nickname + (m.is_leader ? " · trưởng nhóm" : "")),
      m.swiped_count != null ? h("span.pill." + (m.finished ? "pos" : "neutral"), {}, m.finished ? "Xong" : `${m.swiped_count}/${total}`) : null)));

  if (!itin) {
    $("rail").replaceChildren(h("li.empty-line", {}, "Chưa có lịch trên trình duyệt này. ",
      h("a", { href: `/g/${code}/lobby` }, "Về phòng chờ"), " để trưởng nhóm bấm Xếp lịch."));
    $("route-note").textContent = "";
    figures(null, null);
    initMap([]);
    return;
  }
  $("mock-banner").hidden = !itin.mock;

  await Promise.all([...itin.items, ...itin.dropped].filter((x) => !places[x.id]).map(async (x) => {
    try { places[x.id] = await api("GET", `/api/places/${encodeURIComponent(x.id)}?date=${cfg.date}`); }
    catch { places[x.id] = null; }
  }));

  const stops = itin.items.filter((x) => places[x.id] && places[x.id].lat != null);
  const points = [{ id: null, lat: cfg.start_xy[0], lng: cfg.start_xy[1] },
    ...stops.map((x) => ({ id: x.id, lat: places[x.id].lat, lng: places[x.id].lng }))];

  let route = null;
  if (stops.length) {
    try { route = await api("POST", "/api/route", { mode: cfg.mode, points }); }
    catch { route = null; }
  }
  const legs = route && Array.isArray(route.legs) && route.legs.length === stops.length ? route.legs : null;
  $("route-note").textContent = legs
    ? route.note || "Thời gian đi là ước tính."
    : "Đường ước tính: nét đứt nối thẳng theo thứ tự ghé, chưa có dữ liệu đường đi.";

  figures(itin, legs);
  initMap(points, legs);
  rail(itin.items, legs);
  dropped(itin.dropped);
  votes(itin);

  function figures(it, legs) {
    const items = it ? it.items : [];
    const travel = legs ? legs.reduce((a, l) => a + l.duration_min, 0)
      : items.some((x) => x.travel_min != null) ? items.reduce((a, x) => a + (x.travel_min || 0), 0) : null;
    const dist = legs ? legs.reduce((a, l) => a + l.distance_m, 0) : null;
    const lo = items.reduce((a, x) => a + ((places[x.id] || {}).price_min_vnd || 0), 0);
    const hi = items.reduce((a, x) => a + ((places[x.id] || {}).price_max_vnd || 0), 0);
    const cost = it && it.cost_per_person != null ? vnd(it.cost_per_person) : hi > lo ? `${vnd(lo)}–${vnd(hi)}` : vnd(hi);
    const over = (it && it.cost_per_person != null ? it.cost_per_person : hi) > group.budget_per_person;
    const fig = (label, value, note, cls) => h("div.figure", {}, h("dt", {}, label), h("dd", { class: cls || null }, value, note ? h("small", {}, " " + note) : null));
    $("figures").replaceChildren(
      fig("Điểm ghé", String(items.length)),
      fig("Tổng thời gian đi", travel == null ? "—" : `${travel} phút`, "ước tính"),
      fig("Tổng quãng đường", dist == null ? "—" : `${(dist / 1000).toLocaleString("vi-VN", { maximumFractionDigits: 1 })} km`, dist == null ? "chưa có dữ liệu" : "ước tính"),
      fig("Chi phí mỗi người", it ? cost : "—", `/ ngân sách ${vnd(group.budget_per_person)}`, over ? "over" : null),
      fig("Điểm bị bỏ", String(it ? it.dropped.length : 0)));
  }

  function initMap(points, legs) {
    if (!window.L) { $("dash-map").replaceChildren(h("p.muted.empty-line", {}, "Không tải được bản đồ.")); return; }
    const map = L.map("dash-map", { scrollWheelZoom: false });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap contributors" }).addTo(map);
    points.forEach((p, i) => {
      const m = L.marker([p.lat, p.lng], {
        icon: L.divIcon({ className: i ? "pin" : "pin start", html: i ? String(i) : "XP", iconSize: [30, 30] }),
        title: i ? stops[i - 1].name : "Xuất phát",
      }).bindTooltip(i ? `${i}. ${stops[i - 1].name} · ${stops[i - 1].arrive}–${stops[i - 1].leave}` : "Xuất phát: " + cfg.start_name).addTo(map);
      m.on("mouseover", () => focus(i));
      m.on("click", () => focus(i, true));
      markers.push(m);
    });
    for (let i = 1; i < points.length; i++) {
      const geo = legs && legs[i - 1].geometry && legs[i - 1].geometry.length > 1 ? legs[i - 1].geometry : null;
      const line = L.polyline(geo || [[points[i - 1].lat, points[i - 1].lng], [points[i].lat, points[i].lng]],
        { color: accent, weight: 4, opacity: 0.75, dashArray: geo ? null : "6 8" }).addTo(map);
      if (!geo) line.bindTooltip("đường ước tính");
      lines.push(line);
    }
    if (points.length) map.fitBounds(points.map((p) => [p.lat, p.lng]), { padding: [48, 48], maxZoom: 15 });
    else map.setView([21.0285, 105.8542], 13);
  }

  function legLine(i, legs, item) {
    const l = legs && legs[i];
    const text = l ? `Đi ${l.duration_min} phút · ${(l.distance_m / 1000).toLocaleString("vi-VN", { maximumFractionDigits: 1 })} km · ước tính`
      : item.travel_min != null ? `Đi ${item.travel_min} phút · ước tính` : "Chưa có dữ liệu đường đi";
    return h("li.leg", { "data-leg": i + 1 }, text, l && l.source === "duong_chim_bay" ? h("span.pill.warn", {}, "đường chim bay") : null);
  }

  function rail(items, legs) {
    const rows = [h("li", {}, h("button.rail-stop.start", { type: "button", "data-stop": 0, onclick: () => focus(0, true), onmouseenter: () => focus(0) },
      h("span.num", { "aria-hidden": "true" }, "XP"),
      h("div", {}, h("p.stop-time", {}, cfg.start_time), h("h3", {}, "Xuất phát: " + cfg.start_name))))];
    let n = 0;
    for (const x of items) {
      const p = places[x.id];
      if (!p || p.lat == null) continue;
      const [label, tone] = x.no_hours ? HOURS.unknown : HOURS[p.hours_status] || HOURS.unknown;
      const stay = minutes(x.leave) - minutes(x.arrive);
      rows.push(legLine(n, legs, x));
      n++;
      const i = n;
      rows.push(h("li", {}, h("button.rail-stop", { type: "button", "data-stop": i, onclick: () => focus(i, true), onmouseenter: () => focus(i) },
        h("span.num", { "aria-hidden": "true" }, String(i)),
        h("div", {},
          h("p.stop-time", {}, `${x.arrive}–${x.leave}`, h("span.muted.small", {}, ` · ở ${stay} phút`)),
          h("h3", {}, x.name),
          h("p.muted.small", {}, "Giờ mở cửa: " + (p.opening_hours || "chưa có dữ liệu giờ")),
          h("p", {}, h("span.pill." + tone, {}, label))))));
    }
    if (n === 0) rows.push(h("li.empty-line", {}, "Không có điểm nào xếp vừa khung giờ."));
    $("rail").replaceChildren(...rows);
  }

  function minutes(t) { const [a, b] = t.split(":").map(Number); return a * 60 + b; }

  let pinned = null;
  function focus(i, click) {
    if (click) pinned = pinned === i ? null : i;
    const on = click ? pinned : i;
    document.querySelectorAll("[data-stop]").forEach((el) => el.classList.toggle("on", Number(el.dataset.stop) === on));
    document.querySelectorAll("[data-leg]").forEach((el) => el.classList.toggle("on", Number(el.dataset.leg) === on));
    markers.forEach((m, k) => { const el = m.getElement(); if (el) el.classList.toggle("on", k === on); });
    lines.forEach((l, k) => l.setStyle({ weight: k + 1 === on ? 7 : 4, opacity: on == null || k + 1 === on ? 0.9 : 0.35 }));
    if (click && on != null) document.querySelector(`[data-stop="${on}"]`).scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function dropped(list) {
    $("dropped").replaceChildren(...(list.length ? list.map((d) => {
      const [reason, hint] = d.reason.split(/\s+—\s+/);
      return h("li", {}, h("div", {}, h("strong", {}, d.name), h("p", {}, reason), hint ? h("p.muted.small", {}, "Gợi ý: " + hint) : null));
    }) : [h("li.muted", {}, "Không có điểm nào bị bỏ.")]));
  }

  // Chỉ hiện khi B4 trả phiếu gộp; API hiện tại không lộ phiếu của người khác.
  function votes(it) {
    const rows = (it.votes || []).filter((v) => v.place_id);
    if (!rows.length) return;
    $("vote-section").hidden = false;
    $("votes").replaceChildren(...rows.map((v) => {
      const p = places[v.place_id];
      const score = v.like_score != null ? v.like_score : v.swiped ? v.likes / v.swiped : null;
      return h("li.vote-row", {},
        h("span", {}, p ? p.name : v.place_id),
        h("div.meter", { role: "img", "aria-label": score == null ? "chưa có phiếu" : `điểm thích ${Math.round(score * 100)}%` },
          h("span", { style: `--p:${score || 0}` })),
        h("span.small.muted", {}, `${v.swiped ?? "?"}/${group.member_count} đã quẹt`));
    }));
  }
})();
