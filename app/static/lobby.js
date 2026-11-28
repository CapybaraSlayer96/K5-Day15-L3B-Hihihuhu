// Phòng chờ (TS-05): polling tiến độ 3 giây, ghim điểm, nút Xếp lịch chỉ cho trưởng nhóm.
(() => {
  const { api, h, vnd, getMember, header, CATEGORY } = TS;
  const code = document.body.dataset.code;
  const me = getMember(code);
  header(code);
  const $ = (id) => document.getElementById(id);
  const leader = !!(me && me.is_leader);
  let lastCount = null;

  function error(msg) { $("lobby-error").textContent = msg || ""; $("lobby-error").hidden = !msg; }

  if (!me) {
    $("member-note").hidden = false;
    $("member-note").prepend(h("p", {}, "Bạn chưa vào nhóm này trên trình duyệt này. ", h("a", { href: "/join?code=" + code }, "Vào nhóm")));
  } else if (!leader) $("member-note").hidden = false;

  function renderMembers(p) {
    $("summary").textContent = p.deck_ready
      ? `${p.finished_count}/${p.member_count} người đã quẹt xong · ${p.total_cards} thẻ · ngân sách mỗi người ${vnd(p.budget_per_person)}`
      : `${p.member_count} người trong nhóm · bộ thẻ chưa được tạo`;
    $("members").replaceChildren(...p.members.map((m) => {
      const pct = p.total_cards ? Math.round((m.swiped_count / p.total_cards) * 100) : 0;
      return h("li.member", {},
        h("span.avatar", { "aria-hidden": "true", style: `--hue:${hue(m.nickname)}` }, m.nickname.slice(0, 1).toUpperCase()),
        h("div.member-main", {},
          h("p", {}, h("strong", {}, m.nickname), m.is_leader ? h("span.muted", {}, " · trưởng nhóm") : null,
            me && m.nickname === me.nickname ? h("span.muted", {}, " (bạn)") : null),
          h("div.meter", { role: "progressbar", "aria-valuemin": "0", "aria-valuemax": String(p.total_cards), "aria-valuenow": String(m.swiped_count), "aria-label": "Đã quẹt" },
            h("span", { style: `--p:${pct / 100}` }))),
        h("span.member-count", {}, `${m.swiped_count}/${p.total_cards}`),
        m.finished ? h("span.pill.pos", {}, "Xong") : h("span.pill.neutral", {}, "Đang quẹt"));
    }));
    $("updated").textContent = "Cập nhật lúc " + new Date().toLocaleTimeString("vi-VN") + ", tự làm mới mỗi 3 giây.";
    if (p.status === "approved") {
      $("plan").hidden = true;
      error("");
      $("summary").textContent += " · lịch đã duyệt";
    }
  }

  function hue(s) { let x = 0; for (const c of s) x = (x * 31 + c.codePointAt(0)) % 360; return x; }

  let reelSeen = "";
  function person(name, tone) {
    return h("span.pill." + tone, {}, h("span.dot", { "aria-hidden": "true" }), name);
  }
  async function loadReel() {
    let data;
    try { data = await api("GET", `/api/groups/${code}/votes`); } catch { return; }
    const sig = JSON.stringify(data.cards);
    if (sig === reelSeen) return;
    reelSeen = sig;
    const cards = [...data.cards].sort((a, b) =>
      (b.liked_by.length - a.liked_by.length) || (a.skipped_by.length - b.skipped_by.length));
    const voted = cards.filter((c) => c.liked_by.length + c.skipped_by.length).length;
    $("reel-note").textContent = cards.length
      ? `${voted}/${cards.length} thẻ đã có phiếu · xếp theo số người thích`
      : "Bộ thẻ chưa được tạo.";
    $("reel").replaceChildren(...cards.map((c) => {
      const frame = h("div.card-img", {});
      if (c.image_url) {
        const img = h("img", { src: c.image_url, alt: "", loading: "lazy", referrerpolicy: "no-referrer" });
        img.addEventListener("error", () => { img.remove(); frame.classList.add("broken"); });
        frame.append(img);
      } else frame.classList.add("broken");
      const none = !c.liked_by.length && !c.skipped_by.length;
      return h("li.reel-card", {},
        frame,
        h("div.reel-body", {},
          h("div", {}, h("h3", {}, c.name),
            h("p.muted.small", {}, [CATEGORY[c.category] || c.category, c.district].filter(Boolean).join(" · "))),
          h("p.reel-tally", {}, `${c.liked_by.length} thích · ${c.skipped_by.length} bỏ qua`),
          none ? h("p.reel-empty", {}, "Chưa ai quẹt thẻ này.") : null,
          c.liked_by.length ? h("div.who", { "aria-label": "Thích" }, c.liked_by.map((n) => person(n, "pos"))) : null,
          c.skipped_by.length ? h("div.who", { "aria-label": "Bỏ qua" }, c.skipped_by.map((n) => person(n, "neg"))) : null));
    }));
  }
  const reel = $("reel");
  const step = (dir) => {
    const card = reel.querySelector(".reel-card");
    const w = card ? card.getBoundingClientRect().width + 14 : 280;
    reel.scrollBy({ left: dir * w, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  };
  $("reel-prev").addEventListener("click", () => step(-1));
  $("reel-next").addEventListener("click", () => step(1));
  reel.addEventListener("keydown", (ev) => {
    if (ev["key"] === "ArrowRight") { ev.preventDefault(); step(1); }
    if (ev["key"] === "ArrowLeft") { ev.preventDefault(); step(-1); }
  });

  async function poll() {
    loadReel();
    try {
      const p = await api("GET", `/api/groups/${code}/progress`);
      renderMembers(p);
      if (leader && lastCount !== null && lastCount !== p.member_count) loadPins();
      lastCount = p.member_count;
      error("");
    } catch (e) {
      error(e.status === 404 ? "Không tìm thấy nhóm." : e.message);
    }
  }

  async function loadPins() {
    let deck;
    try { deck = await api("GET", `/api/groups/${code}/deck?member_id=${encodeURIComponent(me.member_id)}`); }
    catch (e) { return error(e.message); }
    const pinned = new Set(Itin.pins(code).filter((id) => deck.cards.some((c) => c.id === id)));
    Itin.setPins(code, [...pinned]);
    $("pins").replaceChildren(...deck.cards.map((c) => {
      const closed = c.hours_status === "closed";
      const box = h("input", { type: "checkbox", value: c.id, checked: pinned.has(c.id), disabled: closed });
      box.addEventListener("change", () => {
        box.checked ? pinned.add(c.id) : pinned.delete(c.id);
        Itin.setPins(code, [...pinned]);
      });
      return h("li", {}, h("label.pin-row", {}, box, h("span", {}, c.name),
        c.liked === true ? h("span.pill.pos", {}, "bạn thích") : null,
        closed ? h("span.pill.neg", {}, "đóng ngày đi") : null));
    }));
  }

  if (leader) {
    $("plan").hidden = false;
    $("pins-section").hidden = false;
    loadPins();
    $("plan").addEventListener("click", async () => {
      $("plan").disabled = true;
      $("plan").textContent = "Đang xếp lịch…";
      try {
        await Itin.create(code, me.member_id, Itin.pins(code));
        location.href = `/g/${code}/itinerary`;
      } catch (e) {
        error(e.message);
        $("plan").disabled = false;
        $("plan").textContent = "Xếp lịch";
      }
    });
  }

  poll();
  setInterval(() => { if (!document.hidden) poll(); }, 3000);
})();
