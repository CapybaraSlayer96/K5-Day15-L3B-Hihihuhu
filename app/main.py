"""HTTP B1–B3: cấu hình, nhóm, bộ thẻ tạm, phiếu quẹt và tiến độ."""
import datetime as dt
import os
import re
import secrets
import string
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from psycopg.types.json import Jsonb
from starlette.concurrency import run_in_threadpool

from app.catalogue import eligible, minute, place_view, planning_config, start_options
from app.db import Database
from app.schemas import CreateGroup, DeckRequest, JoinGroup, RouteRequest, SwipeRequest, UndoRequest
from codebase.routing import route as build_route

APP_DIR = Path(__file__).resolve().parent


def connection(request: Request):
    with request.app.state.database.connect() as conn:
        yield conn


def load_group(conn, code, lock=False):
    code = code.upper()
    if not re.fullmatch(r"[A-Z0-9]{6}", code):
        raise HTTPException(404, "Không tìm thấy nhóm.")
    row = conn.execute("SELECT * FROM groups WHERE code = %s" + (" FOR UPDATE" if lock else ""), (code,)).fetchone()
    if not row:
        raise HTTPException(404, "Không tìm thấy nhóm.")
    return row


def writable(conn, group):
    approved = conn.execute("SELECT 1 FROM itineraries WHERE group_id = %s AND status = 'approved' LIMIT 1",
                            (group["id"],)).fetchone()
    if group["status"] == "approved" or approved:
        raise HTTPException(409, "Nhóm đã duyệt lịch, hiện chỉ có thể xem.")


def member(conn, group, member_id, leader=False):
    row = conn.execute("SELECT * FROM members WHERE group_id = %s AND id = %s", (group["id"], member_id)).fetchone()
    if not row or (leader and not row["is_leader"]):
        raise HTTPException(403, "Thành viên không thuộc nhóm hoặc không có quyền thực hiện.")
    return row


def member_count(conn, group):
    return conn.execute("SELECT count(*) AS n FROM members WHERE group_id = %s", (group["id"],)).fetchone()["n"]


def places(conn):
    return [r["data"] for r in conn.execute("SELECT data FROM places ORDER BY id").fetchall()]


def config_for(conn, group):
    return planning_config(group["config"], member_count(conn, group))


def group_view(conn, group):
    people = conn.execute("SELECT nickname, is_leader FROM members WHERE group_id = %s ORDER BY joined_at, id",
                          (group["id"],)).fetchall()
    cfg = group["config"]
    warnings = []
    if minute(cfg["end_time"]) - minute(cfg["start_time"]) < 60:
        warnings.append("Khung giờ dưới một giờ, có thể không xếp được lịch.")
    if cfg.get("start_approximate"):
        warnings.append("Điểm xuất phát là tọa độ trung tâm quận, chỉ xấp xỉ.")
    return {"code": group["code"], "status": group["status"], "config": cfg,
            "member_count": len(people), "members": people,
            "budget_per_person": cfg["budget_total"] // len(people),
            "join_url": "/join?code=" + group["code"], "deck_source": group["deck_source"], "warnings": warnings}


def invalidate_drafts(conn, group):
    conn.execute("UPDATE itineraries SET status = 'stale' WHERE group_id = %s AND status = 'draft'", (group["id"],))
    conn.execute("UPDATE groups SET status = 'swiping' WHERE id = %s AND status = 'planned'", (group["id"],))
    if group["status"] == "planned":
        group["status"] = "swiping"


def ensure_deck(conn, group, builder):
    """Tạo đúng một bộ thẻ; không thay phiếu đã quẹt khi đọc hoặc thành viên mới vào."""
    if group["deck_source"]:
        return
    cfg = config_for(conn, group)
    candidates = [p for p in places(conn) if eligible(p, cfg)]
    by_id = {p["id"]: p for p in candidates}
    if builder is None:
        candidates.sort(key=lambda p: (-(p.get("rating") or 0), p["id"]))
        cards = [{"id": p["id"], "rank": n, "reason": "Điểm đủ điều kiện, tạm sắp theo đánh giá trong dữ liệu."}
                 for n, p in enumerate(candidates[:20], 1)]
        source = "provisional_rating"
    else:
        try:
            cards = builder(cfg)
            if not isinstance(cards, list):
                raise ValueError("Bộ thẻ phải là danh sách.")
            seen = set()
            for card in cards:
                if (card["id"] not in by_id or card["id"] in seen or not isinstance(card["reason"], str)
                        or re.search(r"\d", card["reason"])):
                    raise ValueError("Thẻ không hợp lệ.")
                seen.add(card["id"])
            cards = sorted(cards, key=lambda c: c["rank"])[:20]
        except Exception as exc:
            raise HTTPException(502, "Chưa tạo được bộ thẻ AI, hãy thử lại.") from exc
        source = "ai"
    with conn.cursor() as cur:
        cur.executemany("INSERT INTO deck_cards (group_id, place_id, rank, ai_reason) VALUES (%s, %s, %s, %s)",
                        [(group["id"], card["id"], n, card["reason"]) for n, card in enumerate(cards, 1)])
    conn.execute("UPDATE groups SET deck_source = %s WHERE id = %s", (source, group["id"]))
    group["deck_source"] = source


def active_cards(conn, group):
    cfg = config_for(conn, group)
    rows = conn.execute("SELECT d.place_id, d.rank, d.ai_reason, p.data FROM deck_cards d "
                        "JOIN places p ON p.id = d.place_id WHERE d.group_id = %s ORDER BY d.rank", (group["id"],)).fetchall()
    # Ngân sách/người giảm khi thêm thành viên: ẩn thẻ vượt ngân sách nhưng giữ lịch sử phiếu.
    return [r for r in rows if eligible(r["data"], cfg)]


def create_app(database=None, deck_builder=None):
    @asynccontextmanager
    async def lifespan(app):
        app.state.database = database or Database(os.environ.get("DATABASE_URL"))
        app.state.deck_builder = deck_builder
        await run_in_threadpool(app.state.database.initialize)
        yield

    app = FastAPI(title="TripSwipe API", version="0.1.0", lifespan=lifespan,
                  description="Backend B1–B3. Bộ thẻ tạm được gắn nhãn; chưa có API xếp lịch B4.")
    app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
    templates = Jinja2Templates(directory=APP_DIR / "templates")

    @app.exception_handler(psycopg.OperationalError)
    async def database_unavailable(request, exc):
        return JSONResponse(status_code=503, content={"detail": "Database tạm thời không sẵn sàng, hãy thử lại."})

    @app.get("/", include_in_schema=False)
    def home(request: Request):
        return templates.TemplateResponse(request=request, name="index.html", context={})

    @app.get("/create", include_in_schema=False)
    def create_page(request: Request):
        return templates.TemplateResponse(request=request, name="create.html", context={})

    @app.get("/join", include_in_schema=False)
    def join_page(request: Request, code: str = ""):
        code = code.strip().upper()
        return templates.TemplateResponse(request=request, name="join.html",
                                          context={"join_code": code if re.fullmatch(r"[A-Z0-9]{6}", code) else ""})

    @app.get("/g/{code}/{page}", include_in_schema=False)
    def group_page(request: Request, code: str, page: str):
        code = code.upper()
        if page not in ("swipe", "lobby", "itinerary", "dashboard") or not re.fullmatch(r"[A-Z0-9]{6}", code):
            raise HTTPException(404, "Không tìm thấy trang.")
        return templates.TemplateResponse(request=request, name=page + ".html", context={"code": code, "page": page})

    @app.get("/health", tags=["Hệ thống"])
    def health(conn=Depends(connection)):
        counts = conn.execute("SELECT (SELECT count(*) FROM places) AS places, "
                              "(SELECT count(*) FROM travel_times) AS travel_times").fetchone()
        return {"status": "ok", **counts}

    @app.get("/api/config/options", tags=["Cấu hình"])
    def options(conn=Depends(connection)):
        return {"cities": [{"id": "ha_noi", "name": "Hà Nội", "enabled": True}],
                "scopes": [{"id": "noi_thanh", "name": "Nội thành", "enabled": True},
                           {"id": "ngoai_thanh", "name": "Ngoại thành — sắp có", "enabled": False}],
                "timezone": "Asia/Ho_Chi_Minh", "start_locations": start_options(places(conn)),
                "transport_modes": [{"id": "xe_may", "name": "Xe máy"}, {"id": "o_to", "name": "Ô tô"},
                                    {"id": "di_bo", "name": "Đi bộ"}],
                "defaults": {"start_time": "08:00", "end_time": "17:00", "start_id": "hn_01", "mode": "xe_may"},
                "deck_limit": 20, "deck_strategy": "ai" if deck_builder else "provisional_rating"}

    @app.post("/api/groups", status_code=201, tags=["Nhóm"])
    def create_group(payload: CreateGroup, conn=Depends(connection)):
        starts = {p["id"]: p for p in start_options(places(conn))}
        if payload.start_id not in starts:
            raise HTTPException(422, "Điểm xuất phát không hợp lệ hoặc ngoài nội thành.")
        start = starts[payload.start_id]
        cfg = payload.model_dump(mode="json", exclude={"nickname"})
        cfg.update(start_xy=[start["lat"], start["lng"]], start_name=start["name"], start_approximate=start["approximate"])
        gid = uuid.uuid4().hex
        for _ in range(10):
            code = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            try:
                with conn.transaction():
                    row = conn.execute("INSERT INTO groups (id, code, config) VALUES (%s, %s, %s) RETURNING *",
                                       (gid, code, Jsonb(cfg))).fetchone()
                break
            except psycopg.errors.UniqueViolation:
                continue
        else:
            raise HTTPException(503, "Chưa tạo được mã nhóm, hãy thử lại.")
        mid = uuid.uuid4().hex
        conn.execute("INSERT INTO members (id, group_id, nickname, nickname_key, is_leader) VALUES (%s,%s,%s,%s,true)",
                     (mid, gid, payload.nickname, payload.nickname.casefold()))
        return {"group": group_view(conn, row), "member_id": mid, "is_leader": True}

    @app.get("/api/groups/{code}", tags=["Nhóm"])
    def get_group(code: str, conn=Depends(connection)):
        return group_view(conn, load_group(conn, code))

    @app.post("/api/groups/{code}/members", status_code=201, tags=["Nhóm"])
    def join_group(code: str, payload: JoinGroup, conn=Depends(connection)):
        group = load_group(conn, code, lock=True)
        writable(conn, group)
        mid = uuid.uuid4().hex
        try:
            conn.execute("INSERT INTO members (id, group_id, nickname, nickname_key) VALUES (%s,%s,%s,%s)",
                         (mid, group["id"], payload.nickname, payload.nickname.casefold()))
        except psycopg.errors.UniqueViolation as exc:
            raise HTTPException(409, "Biệt danh đã có trong nhóm, hãy chọn tên khác.") from exc
        invalidate_drafts(conn, group)
        return {"member_id": mid, "is_leader": False, "group": group_view(conn, group)}

    @app.get("/api/places/{place_id}", tags=["Địa điểm"])
    def detail(place_id: str, date: dt.date | None = None, conn=Depends(connection)):
        row = conn.execute("SELECT data FROM places WHERE id = %s", (place_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Không tìm thấy địa điểm.")
        return place_view(row["data"], date)

    @app.post("/api/route", tags=["Chỉ đường"])
    def route_legs(payload: RouteRequest):
        """Hình đường đi thật + phút / mét từng chặng (ước tính) cho bản đồ lịch trình."""
        return build_route([p.model_dump() for p in payload.points], payload.mode)

    @app.get("/api/groups/{code}/deck", tags=["Bộ thẻ"])
    def get_deck(code: str, request: Request, member_id: str | None = Query(default=None, max_length=64),
                 conn=Depends(connection)):
        group = load_group(conn, code, lock=True)
        if member_id:
            member(conn, group, member_id)
        if not group["deck_source"]:
            writable(conn, group)
            ensure_deck(conn, group, request.app.state.deck_builder)
        votes = {}
        if member_id:
            votes = {r["place_id"]: r["liked"] for r in conn.execute(
                "SELECT place_id, liked FROM swipes WHERE group_id = %s AND member_id = %s",
                (group["id"], member_id)).fetchall()}
        date = dt.date.fromisoformat(group["config"]["date"])
        cards = [{**place_view(r["data"], date), "rank": r["rank"], "ai_reason": r["ai_reason"],
                  "swiped": r["place_id"] in votes, "liked": votes.get(r["place_id"])} for r in active_cards(conn, group)]
        return {"code": group["code"], "source": group["deck_source"], "cards": cards, "total": len(cards),
                "remaining": sum(not c["swiped"] for c in cards),
                "budget_per_person": config_for(conn, group)["budget_per_person"],
                "warnings": (["Bộ thẻ tạm theo rating trong dữ liệu, chưa phải lựa chọn của AI."]
                             if group["deck_source"] == "provisional_rating" else [])}

    @app.post("/api/groups/{code}/deck", tags=["Bộ thẻ"])
    def build_deck(code: str, payload: DeckRequest, request: Request, conn=Depends(connection)):
        group = load_group(conn, code, lock=True)
        writable(conn, group)
        member(conn, group, payload.member_id, leader=True)
        ensure_deck(conn, group, request.app.state.deck_builder)
        return {"code": group["code"], "source": group["deck_source"], "total": len(active_cards(conn, group))}

    @app.post("/api/groups/{code}/swipes", tags=["Quẹt"])
    def swipe(code: str, payload: SwipeRequest, conn=Depends(connection)):
        group = load_group(conn, code, lock=True)
        writable(conn, group)
        member(conn, group, payload.member_id)
        if payload.place_id not in {r["place_id"] for r in active_cards(conn, group)}:
            raise HTTPException(422, "Địa điểm không có trong bộ thẻ đang hợp lệ của nhóm.")
        conn.execute("INSERT INTO swipes (group_id, member_id, place_id, liked) VALUES (%s,%s,%s,%s) "
                     "ON CONFLICT (member_id, place_id) DO UPDATE SET liked = EXCLUDED.liked, updated_at = now()",
                     (group["id"], payload.member_id, payload.place_id, payload.liked))
        invalidate_drafts(conn, group)
        return {"member_id": payload.member_id, "place_id": payload.place_id, "liked": payload.liked, "saved": True}

    @app.delete("/api/groups/{code}/swipes", tags=["Quẹt"])
    def undo(code: str, payload: UndoRequest, conn=Depends(connection)):
        group = load_group(conn, code, lock=True)
        writable(conn, group)
        member(conn, group, payload.member_id)
        row = conn.execute("DELETE FROM swipes WHERE group_id = %s AND member_id = %s AND place_id = %s RETURNING place_id",
                           (group["id"], payload.member_id, payload.place_id)).fetchone()
        invalidate_drafts(conn, group)
        return {"place_id": payload.place_id, "removed": bool(row)}

    @app.get("/api/groups/{code}/progress", tags=["Tiến độ"])
    def progress(code: str, conn=Depends(connection)):
        group = load_group(conn, code, lock=True)
        active_ids = [r["place_id"] for r in active_cards(conn, group)]
        rows = conn.execute("SELECT m.nickname, m.is_leader, count(s.place_id) FILTER (WHERE s.place_id = ANY(%s)) AS swiped_count "
                            "FROM members m LEFT JOIN swipes s ON s.member_id = m.id AND s.group_id = m.group_id "
                            "WHERE m.group_id = %s GROUP BY m.id ORDER BY m.joined_at, m.id",
                            (active_ids, group["id"])).fetchall()
        total = len(active_ids)
        for row in rows:
            row["remaining"] = total - row["swiped_count"]
            row["finished"] = total > 0 and row["remaining"] == 0
        return {"code": group["code"], "status": group["status"], "deck_ready": group["deck_source"] is not None,
                "deck_source": group["deck_source"], "total_cards": total, "members": rows,
                "member_count": len(rows), "finished_count": sum(r["finished"] for r in rows),
                "all_finished": bool(total) and all(r["finished"] for r in rows),
                "budget_per_person": config_for(conn, group)["budget_per_person"]}

    return app


app = create_app()
