// Vào nhóm bằng mã + biệt danh (TS-02).
(() => {
  const { api, h, vnd, dateVi, getMember, setMember } = TS;
  const form = document.getElementById("join");
  const code = document.getElementById("code");
  const nick = document.getElementById("nickname");
  const info = document.getElementById("group-info");
  const codeErr = document.getElementById("code-err");
  const nickErr = document.getElementById("nick-err");
  const formError = document.getElementById("form-error");
  const submit = document.getElementById("submit");
  let group = null;

  const norm = () => code.value.trim().toUpperCase();

  async function lookup() {
    group = null;
    info.hidden = true;
    codeErr.textContent = "";
    const c = norm();
    if (!/^[A-Z0-9]{6}$/.test(c)) return;
    const saved = getMember(c);
    if (saved) return location.replace("/g/" + c + "/swipe");
    try {
      group = await api("GET", "/api/groups/" + c);
    } catch (e) {
      codeErr.textContent = e.status === 404 ? "Không tìm thấy nhóm. Kiểm lại mã." : e.message;
      return;
    }
    info.replaceChildren(
      h("p", {}, h("strong", {}, dateVi(group.config.date)), " · " + group.config.start_time + "–" + group.config.end_time),
      h("p.muted", {}, "Xuất phát " + group.config.start_name + " · " + group.member_count + " người đã vào · ngân sách mỗi người hiện " + vnd(group.budget_per_person)));
    if (group.status === "approved") {
      info.append(h("p.hint", {}, "Nhóm đã duyệt lịch, chỉ có thể xem. ", h("a", { href: "/g/" + group.code + "/itinerary" }, "Xem lịch trình")));
      submit.disabled = true;
    } else submit.disabled = false;
    info.hidden = false;
  }

  code.addEventListener("input", () => { code.value = code.value.toUpperCase(); lookup(); });

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    nickErr.textContent = "";
    formError.hidden = true;
    const c = norm();
    if (!/^[A-Z0-9]{6}$/.test(c)) { codeErr.textContent = "Mã nhóm gồm 6 chữ hoặc số."; return code.focus(); }
    const name = nick.value.trim();
    if (!name) { nickErr.textContent = "Nhập biệt danh."; return nick.focus(); }
    submit.disabled = true;
    try {
      const res = await api("POST", "/api/groups/" + c + "/members", { nickname: name });
      setMember(c, { member_id: res.member_id, is_leader: res.is_leader, nickname: name });
      location.href = "/g/" + c + "/swipe";
    } catch (e) {
      if (e.status === 404) codeErr.textContent = "Không tìm thấy nhóm. Kiểm lại mã.";
      else if (e.status === 409 && /duyệt/.test(e.message)) {
        formError.replaceChildren(e.message + " ", h("a", { href: "/g/" + c + "/itinerary" }, "Xem lịch trình"));
        formError.hidden = false;
      } else if (e.status === 409) { nickErr.textContent = e.message; nick.select(); }
      else if (e.status === 422 && Array.isArray(e.detail)) nickErr.textContent = e.detail.map((d) => d.msg.replace(/^Value error, /, "")).join(" ");
      else { formError.textContent = e.message; formError.hidden = false; }
    } finally {
      submit.disabled = false;
    }
  });

  if (code.value) lookup(); else code.focus();
  if (code.value) nick.focus();
})();
