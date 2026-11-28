// Phòng chờ (TS-05): polling tiến độ 3 giây, ghim điểm, nút Xếp lịch chỉ cho trưởng nhóm.
(() => {
  const { api, h, vnd, getMember, header } = TS;
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

  async function poll() {
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
