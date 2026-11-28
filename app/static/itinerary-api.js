// Lớp gọi API lịch trình (B4). Khi endpoint chưa có, dùng dữ liệu mẫu có nhãn để U5 nối sau.
const Itin = (() => {
  const { api, getJSON, setJSON } = TS;
  const versionsKey = (code) => "tripswipe:itin:" + code;
  const pinsKey = (code) => "tripswipe:pins:" + code;

  // 404 "Not Found" là route chưa có; 404 nghiệp vụ có detail tiếng Việt riêng.
  const notBuilt = (e) => (e.status === 404 && e.detail === "Not Found") || e.status === 405;

  async function mock() {
    const res = await fetch("/static/mock-itinerary.json");
    return { ...(await res.json()), mock: true };
  }

  function versions(code) { return getJSON(versionsKey(code), []); }

  // Lưu bản mới, đánh dấu các bản nháp cũ hết hiệu lực.
  function push(code, itin) {
    const list = versions(code).map((v) => (v.status === "draft" ? { ...v, status: "stale" } : v));
    list.push({ ...itin, saved_at: new Date().toISOString() });
    setJSON(versionsKey(code), list);
    return list;
  }

  async function create(code, member_id, pinned) {
    try {
      return push(code, await api("POST", `/api/groups/${code}/itinerary`, { member_id, pinned }));
    } catch (e) {
      if (!notBuilt(e)) throw e;
      return push(code, await mock());
    }
  }

  async function patch(code, itin, member_id, action, place_id) {
    if (!itin.mock) {
      try {
        return push(code, await api("PATCH", `/api/itineraries/${itin.id}`, { member_id, action, place_id }));
      } catch (e) {
        if (!notBuilt(e)) throw e;
      }
    }
    return push(code, mockPatch(itin, action, place_id));
  }

  // Dữ liệu mẫu không có bộ xếp lịch: chỉ chuyển trạng thái, không tự bịa giờ mới.
  function mockPatch(itin, action, place_id) {
    const next = { ...itin, id: "mock-" + Date.now(), mock: true, items: [...itin.items], dropped: [...itin.dropped] };
    if (action === "approve") return { ...next, status: "approved" };
    if (action === "drop") {
      const item = next.items.find((i) => i.id === place_id);
      next.items = next.items.filter((i) => i.id !== place_id);
      next.dropped.push({ id: place_id, name: item ? item.name : place_id, reason: "Trưởng nhóm bỏ khỏi lịch — gợi ý ghim lại nếu đổi ý." });
      return { ...next, status: "draft" };
    }
    if (action === "pin") {
      const d = itin.dropped.find((x) => x.id === place_id);
      const err = new Error(d && /đóng/i.test(d.reason)
        ? "Không ghim được: " + d.reason
        : "Dữ liệu mẫu không tính lại được giờ khi ghim; cần API xếp lịch (B4).");
      err.status = 409;
      throw err;
    }
    return next;
  }

  // Lịch mới nhất: GET B4 nếu có, không thì bản lưu trên trình duyệt này.
  async function latest(code) {
    try {
      return await api("GET", `/api/groups/${code}/itinerary`);
    } catch (e) {
      if (!notBuilt(e) && e.status !== 404) throw e;
      return versions(code).at(-1) || null;
    }
  }

  return {
    versions, create, patch, latest,
    pins: (code) => getJSON(pinsKey(code), []),
    setPins: (code, ids) => setJSON(pinsKey(code), ids),
  };
})();
