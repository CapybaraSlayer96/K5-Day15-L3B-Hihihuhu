// Wizard tạo nhóm (TS-01).
(async () => {
  const { api, h, vnd, todayHanoi, dateVi, setMember } = TS;
  const form = document.getElementById("wizard");
  const steps = [...form.querySelectorAll(".step")];
  const progress = document.getElementById("progress");
  const back = document.getElementById("back");
  const next = document.getElementById("next");
  const formError = document.getElementById("form-error");
  const $ = (id) => document.getElementById(id);
  let at = 0;
  let opts;

  steps.forEach((s, i) => progress.append(h("li", { "data-i": i }, s.dataset.step)));

  function radios(slot, name, items, selected) {
    for (const it of items) {
      const enabled = it.enabled !== false;
      slot.append(h("label.choice" + (enabled ? "" : ".off"), {},
        h("input", { type: "radio", name, value: it.id, disabled: !enabled, checked: it.id === selected }),
        h("span", {}, it.name.replace(/\s*—\s*sắp có$/, "")),
        enabled ? null : h("span.tag", {}, "sắp có")));
    }
  }

  try {
    opts = await api("GET", "/api/config/options");
  } catch (e) {
    showError(e.message);
    next.disabled = true;
    return;
  }
  // API chỉ liệt kê tỉnh đang hỗ trợ; thêm một mục tắt để báo tỉnh khác sắp có.
  const cities = [...opts.cities, { id: "soon", name: "Tỉnh khác", enabled: false }];
  radios($("cities"), "city_id", cities, opts.cities.find((c) => c.enabled)?.id);
  radios($("scopes"), "scope", opts.scopes, opts.scopes.find((s) => s.enabled)?.id);
  radios($("modes"), "mode", opts.transport_modes, opts.defaults.mode);

  const today = todayHanoi();
  $("date").min = today;
  $("start_time").value = opts.defaults.start_time;
  $("end_time").value = opts.defaults.end_time;

  const exact = opts.start_locations.filter((p) => !p.approximate);
  const approx = opts.start_locations.filter((p) => p.approximate);
  const sel = $("start_id");
  sel.append(h("optgroup", { label: "Địa điểm cụ thể" }, exact.map((p) => h("option", { value: p.id }, p.name))));
  sel.append(h("optgroup", { label: "Trung tâm quận (tọa độ xấp xỉ)" },
    approx.map((p) => h("option", { value: p.id }, p.name + " · xấp xỉ"))));
  sel.value = opts.defaults.start_id;
  const startNote = () => {
    const p = opts.start_locations.find((x) => x.id === sel.value);
    $("start-note").textContent = p && p.approximate ? "Đây là tọa độ trung tâm quận, chỉ xấp xỉ; thời gian đi chặng đầu có thể lệch." : "";
  };
  sel.addEventListener("change", startNote);
  startNote();

  const budget = $("budget_total");
  budget.addEventListener("input", () => {
    const n = Number(budget.value);
    $("budget-note").textContent = budget.value === "" ? "Chia đều theo số thành viên." :
      n === 0 ? "Ngân sách 0: chỉ gợi ý điểm ghi rõ miễn phí." : "Tổng " + vnd(n) + ", chia đều theo số thành viên.";
  });

  function showError(msg) {
    formError.textContent = msg;
    formError.hidden = !msg;
  }
  function fieldError(name, msg) {
    const p = form.querySelector(`.field-error[data-for~="${name}"]`);
    if (p) p.textContent = msg;
    const input = form.elements[name];
    if (input && input.setAttribute) input.setAttribute("aria-invalid", msg ? "true" : "false");
  }
  function clearErrors() {
    form.querySelectorAll(".field-error").forEach((p) => (p.textContent = ""));
    form.querySelectorAll("[aria-invalid]").forEach((i) => i.removeAttribute("aria-invalid"));
    showError("");
  }

  // Trả false nếu bước hiện tại chưa hợp lệ.
  function validate(i) {
    const name = steps[i].dataset.step;
    if (name === "Ngày đi") {
      const v = $("date").value;
      if (!v) return fieldError("date", "Hãy chọn ngày đi."), false;
      if (v < today) return fieldError("date", "Ngày đi đã qua, hãy chọn hôm nay hoặc sau này."), false;
    }
    if (name === "Khung giờ") {
      const a = $("start_time").value, b = $("end_time").value;
      if (!a || !b) return fieldError("end_time", "Nhập đủ giờ bắt đầu và kết thúc."), false;
      if (b <= a) return fieldError("end_time", "Giờ kết thúc phải sau giờ bắt đầu, trong cùng một ngày."), false;
    }
    if (name === "Xuất phát" && !sel.value) return fieldError("start_id", "Hãy chọn điểm xuất phát."), false;
    if (name === "Ngân sách") {
      const v = budget.value;
      if (v === "" || !Number.isInteger(Number(v)) || Number(v) < 0)
        return fieldError("budget_total", "Nhập số tiền nguyên, không âm."), false;
    }
    if (name === "Phương tiện" && !$("nickname").value.trim())
      return fieldError("nickname", "Nhập biệt danh để cả nhóm nhận ra bạn."), false;
    return true;
  }

  function minutes(t) { const [x, y] = t.split(":").map(Number); return x * 60 + y; }
  for (const id of ["start_time", "end_time"]) $(id).addEventListener("input", () => {
    const a = $("start_time").value, b = $("end_time").value;
    $("time-warn").hidden = !(a && b && b > a && minutes(b) - minutes(a) < 60);
  });

  function show(i) {
    at = i;
    steps.forEach((s, j) => (s.hidden = j !== i));
    [...progress.children].forEach((li, j) => {
      li.classList.toggle("done", j < i);
      li.toggleAttribute("aria-current", j === i);
    });
    back.disabled = i === 0;
    next.textContent = i === steps.length - 1 ? "Tạo nhóm" : "Tiếp tục";
    const first = steps[i].querySelector("input:not([disabled]), select");
    if (first) first.focus({ preventScroll: true });
  }

  back.addEventListener("click", () => { clearErrors(); show(Math.max(0, at - 1)); });

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    clearErrors();
    if (!validate(at)) return;
    if (at < steps.length - 1) return show(at + 1);
    const data = new FormData(form);
    const body = {
      nickname: $("nickname").value.trim(), city_id: data.get("city_id"), scope: data.get("scope"),
      date: $("date").value, start_time: $("start_time").value, end_time: $("end_time").value,
      start_id: sel.value, budget_total: Number(budget.value), mode: data.get("mode"),
    };
    next.disabled = true;
    next.textContent = "Đang tạo…";
    try {
      const res = await api("POST", "/api/groups", body);
      setMember(res.group.code, { member_id: res.member_id, is_leader: res.is_leader, nickname: body.nickname });
      done(res.group);
    } catch (e) {
      handleApiError(e);
    } finally {
      next.disabled = false;
      next.textContent = "Tạo nhóm";
    }
  });

  const STEP_OF = { date: "Ngày đi", start_time: "Khung giờ", end_time: "Khung giờ", start_id: "Xuất phát",
    budget_total: "Ngân sách", mode: "Phương tiện", nickname: "Phương tiện" };

  function handleApiError(e) {
    if (e.status === 422 && Array.isArray(e.detail)) {
      let jump = null;
      for (const d of e.detail) {
        const field = d.loc[d.loc.length - 1];
        const name = STEP_OF[field] ? field : "end_time"; // lỗi cấp body là lỗi thứ tự giờ
        fieldError(name, d.msg.replace(/^Value error, /, ""));
        const idx = steps.findIndex((s) => s.dataset.step === STEP_OF[name]);
        if (jump === null || idx < jump) jump = idx;
      }
      if (jump !== null && jump >= 0) show(jump);
      return;
    }
    if (e.status === 422) {
      fieldError("start_id", e.message);
      return show(steps.findIndex((s) => s.dataset.step === "Xuất phát"));
    }
    showError(e.message);
  }

  function done(group) {
    form.hidden = true;
    progress.hidden = true;
    const section = $("done");
    section.hidden = false;
    $("done-code").textContent = group.code;
    const link = location.origin + group.join_url;
    $("done-link").value = link;
    $("copy-link").addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(link); } catch { $("done-link").select(); document.execCommand("copy"); }
      $("copy-link").textContent = "Đã sao chép";
    });
    for (const w of group.warnings) $("done-warn").append(h("li", {}, w));
    const c = group.config;
    const mode = opts.transport_modes.find((m) => m.id === c.mode);
    const facts = [
      ["Ngày đi", dateVi(c.date)], ["Khung giờ", c.start_time + "–" + c.end_time],
      ["Xuất phát", c.start_name + (c.start_approximate ? " (xấp xỉ)" : "")],
      ["Ngân sách cả nhóm", vnd(c.budget_total)], ["Mỗi người hiện tại", vnd(group.budget_per_person)],
      ["Phương tiện", mode ? mode.name : c.mode],
    ];
    for (const [k, v] of facts) $("done-facts").append(h("dt", {}, k), h("dd", {}, v));
    $("go-swipe").href = "/g/" + group.code + "/swipe";
    $("go-swipe").focus();
  }

  show(0);
})();
