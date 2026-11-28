"""Integration B1–B4 trên Postgres thật, dùng schema ngẫu nhiên và xóa sau test.

TEST_DATABASE_URL=postgresql://... .venv/bin/python tests/test_api.py
Không gọi LLM hay sửa benchmark/eval/traces.
"""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import psycopg
from psycopg import sql
from fastapi.testclient import TestClient

from app.db import Database, ROOT
from app.main import create_app
from app.schemas import today_hanoi


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = os.environ["TEST_DATABASE_URL"]
        cls.schema = "test_tripswipe_" + uuid.uuid4().hex
        with psycopg.connect(cls.url) as conn:
            conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(cls.schema)))
        cls.database = Database(cls.url, schema=cls.schema)
        cls.client = TestClient(create_app(database=cls.database))
        try:
            cls.client.__enter__()
        except Exception:
            cls.drop_schema()
            raise

    @classmethod
    def drop_schema(cls):
        with psycopg.connect(cls.url) as conn:
            conn.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(cls.schema)))

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)
        cls.drop_schema()

    def payload(self, **changes):
        monday = today_hanoi() + dt.timedelta(days=(7 - today_hanoi().weekday()) % 7 + 7)
        data = {"nickname": "Minh", "date": monday.isoformat(), "start_time": "08:00", "end_time": "17:00",
                "start_id": "hn_01", "budget_total": 1_000_000, "mode": "xe_may"}
        return {**data, **changes}

    def group(self, **changes):
        r = self.client.post("/api/groups", json=self.payload(**changes))
        self.assertEqual(r.status_code, 201, r.text)
        data = r.json()
        return data["group"]["code"], data["member_id"]

    def test_startup_and_seed_are_idempotent(self):
        before = self.client.get("/health").json()
        self.assertEqual(before["places"], len(json.loads((ROOT / "data/hanoi_places.json").read_text())))
        self.assertEqual(before["travel_times"], len(json.loads((ROOT / "data/travel_times.json").read_text())))
        code, mid = self.group()
        self.database.initialize()
        self.assertEqual(before, self.client.get("/health").json())
        self.assertEqual(self.client.get("/api/groups/" + code).json()["member_count"], 1)
        with self.database.connect() as conn:
            tables = conn.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s", (self.schema,)).fetchall()
        self.assertEqual({r["tablename"] for r in tables},
                         {"places", "travel_times", "groups", "members", "deck_cards", "swipes", "itineraries"})
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/static/base.css").status_code, 200)

    def test_validation_and_config_options(self):
        options = self.client.get("/api/config/options").json()
        self.assertEqual(options["timezone"], "Asia/Ho_Chi_Minh")
        self.assertIn("hn_01", [x["id"] for x in options["start_locations"]])
        for changes in [{"date": None}, {"date": "2000-01-01"}, {"end_time": "08:00"},
                        {"start_time": "25:00"}, {"budget_total": -1}, {"budget_total": True},
                        {"nickname": "  "}, {"mode": "bay"}, {"start_id": "not-real"}, {"city_id": "ha_long"}]:
            with self.subTest(changes=changes):
                self.assertEqual(self.client.post("/api/groups", json=self.payload(**changes)).status_code, 422)
        missing = self.payload()
        del missing["date"]
        self.assertEqual(self.client.post("/api/groups", json=missing).status_code, 422)

    def test_join_nickname_and_membership(self):
        code, leader = self.group(nickname="  Minh   Nguyễn  ")
        self.assertRegex(code, r"^[A-Z0-9]{6}$")
        self.assertEqual(self.client.get("/api/groups/" + code.lower()).status_code, 200)
        self.assertEqual(self.client.post(f"/api/groups/{code}/members", json={"nickname": "minh nguyễn"}).status_code, 409)
        joined = self.client.post(f"/api/groups/{code}/members", json={"nickname": "Bảo"})
        self.assertEqual(joined.status_code, 201)
        self.assertEqual(joined.json()["group"]["budget_per_person"], 500_000)
        group = self.client.get("/api/groups/" + code).json()
        self.assertEqual(group["member_count"], 2)
        self.assertNotIn(leader, json.dumps(group))
        self.assertEqual(self.client.get("/api/groups/INVALID").status_code, 404)
        self.assertEqual(self.client.post(f"/api/groups/{code}/deck", json={"member_id": joined.json()["member_id"]}).status_code, 403)
        other_code, other_mid = self.group()
        self.assertEqual(self.client.get(f"/api/groups/{code}/deck", params={"member_id": other_mid}).status_code, 403)

    def test_deck_swipe_overwrite_undo_and_progress(self):
        code, mid = self.group()
        base = f"/api/groups/{code}"
        deck = self.client.get(base + "/deck", params={"member_id": mid}).json()
        self.assertEqual(deck["source"], "provisional_rating")
        self.assertTrue(deck["warnings"])
        ids = [p["id"] for p in deck["cards"]]
        self.assertGreater(len(ids), 0)
        self.assertLessEqual(len(ids), 20)
        self.assertFalse({"hn_04", "hn_15", "hn_46", "hn_13"} & set(ids))
        self.assertTrue(all(p["hours_status"] == "open" for p in deck["cards"]))
        pid = ids[0]
        payload = {"member_id": mid, "place_id": pid, "liked": True}
        with ThreadPoolExecutor(max_workers=4) as pool:
            responses = list(pool.map(lambda _: self.client.post(base + "/swipes", json=payload), range(4)))
        self.assertTrue(all(r.status_code == 200 for r in responses))
        self.assertEqual(self.client.post(base + "/swipes", json={**payload, "liked": False}).status_code, 200)
        progress = self.client.get(base + "/progress").json()
        self.assertEqual(progress["members"][0]["swiped_count"], 1)
        after = self.client.get(base + "/deck", params={"member_id": mid}).json()
        self.assertEqual([p["id"] for p in after["cards"]], ids)
        self.assertFalse(next(p["liked"] for p in after["cards"] if p["id"] == pid))
        self.assertEqual(after["remaining"], len(ids) - 1)
        self.assertEqual(self.client.post(base + "/swipes", json={**payload, "place_id": "hn_04"}).status_code, 422)
        self.assertEqual(self.client.post(base + "/swipes", json={**payload, "liked": "false"}).status_code, 422)
        self.assertEqual(self.client.post(base + "/swipes", json={**payload, "member_id": "unknown"}).status_code, 403)
        undo = {"member_id": mid, "place_id": pid}
        self.assertTrue(self.client.request("DELETE", base + "/swipes", json=undo).json()["removed"])
        self.assertFalse(self.client.request("DELETE", base + "/swipes", json=undo).json()["removed"])
        self.assertEqual(self.client.get(base + "/progress").json()["members"][0]["swiped_count"], 0)

    def test_budget_zero_detail_and_restart_preserves_votes(self):
        code, mid = self.group(budget_total=0)
        base = f"/api/groups/{code}"
        cards = self.client.get(base + "/deck").json()["cards"]
        self.assertTrue(cards)
        self.assertTrue(all(p["price_max_vnd"] == 0 for p in cards))
        pid = cards[0]["id"]
        self.client.post(base + "/swipes", json={"member_id": mid, "place_id": pid, "liked": True})
        with TestClient(create_app(database=self.database)) as restarted:
            self.assertEqual(restarted.get(base + "/progress").json()["members"][0]["swiped_count"], 1)
        date = self.payload()["date"]
        detail = self.client.get("/api/places/hn_13", params={"date": date}).json()
        self.assertEqual(detail["hours_status"], "unknown")
        self.assertIsNone(detail["opening_windows"])
        self.assertIn("verification", detail)
        self.assertEqual(self.client.get("/api/places/no-place").status_code, 404)

    def test_new_member_rechecks_budget_without_deleting_votes(self):
        code, mid = self.group(budget_total=100_000)
        base = f"/api/groups/{code}"
        cards = self.client.get(base + "/deck").json()["cards"]
        paid = next(p for p in cards if p.get("price_max_vnd") and p["price_max_vnd"] > 0)
        self.assertEqual(self.client.post(base + "/swipes", json={"member_id": mid, "place_id": paid["id"], "liked": True}).status_code, 200)
        for n in range(5):
            self.assertEqual(self.client.post(base + "/members", json={"nickname": "Bạn " + str(n)}).status_code, 201)
        current = self.client.get(base + "/deck").json()
        self.assertEqual(current["budget_per_person"], 100_000 // 6)
        self.assertNotIn(paid["id"], [p["id"] for p in current["cards"]])
        with self.database.connect() as conn:
            self.assertEqual(conn.execute("SELECT count(*) AS n FROM swipes WHERE member_id = %s", (mid,)).fetchone()["n"], 1)
        self.assertEqual(self.client.post(base + "/swipes", json={"member_id": mid, "place_id": paid["id"], "liked": False}).status_code, 422)

    def test_approved_group_is_read_only(self):
        code, mid = self.group()
        base = f"/api/groups/{code}"
        cards = self.client.get(base + "/deck").json()["cards"]
        with self.database.connect() as conn:
            conn.execute("UPDATE groups SET status = 'approved' WHERE code = %s", (code,))
        self.assertEqual(self.client.post(base + "/members", json={"nickname": "Bảo"}).status_code, 409)
        self.assertEqual(self.client.post(base + "/swipes", json={"member_id": mid, "place_id": cards[0]["id"], "liked": True}).status_code, 409)
        self.assertEqual(self.client.post(base + "/deck", json={"member_id": mid}).status_code, 409)
        self.assertEqual(self.client.get(base).status_code, 200)
        self.assertEqual(self.client.get(base + "/deck").status_code, 200)

    def test_ai_builder_failure_never_silently_falls_back(self):
        def broken(cfg):
            raise RuntimeError("API model lỗi")
        code, _ = self.group()
        with TestClient(create_app(database=self.database, deck_builder=broken)) as client:
            self.assertEqual(client.get(f"/api/groups/{code}/deck").status_code, 502)
        self.assertIsNone(self.client.get(f"/api/groups/{code}").json()["deck_source"])

    def test_itinerary_vote_plan_patch_and_approve(self):
        code, leader = self.group()
        base = f"/api/groups/{code}"
        friend = self.client.post(base + "/members", json={"nickname": "Bảo"}).json()["member_id"]
        self.assertEqual(self.client.get(base + "/itinerary").json(), {"detail": "Nhóm chưa có lịch."})
        ids = [p["id"] for p in self.client.get(base + "/deck").json()["cards"]][:6]
        for n, pid in enumerate(ids):
            self.client.post(base + "/swipes", json={"member_id": leader, "place_id": pid, "liked": True})
            self.client.post(base + "/swipes", json={"member_id": friend, "place_id": pid, "liked": n % 3 != 2})
        self.assertEqual(self.client.post(base + "/itinerary", json={"member_id": friend}).status_code, 403)
        r = self.client.post(base + "/itinerary", json={"member_id": leader})
        self.assertEqual(r.status_code, 201, r.text)
        first = r.json()
        self.assertEqual(first["status"], "draft")
        self.assertEqual(first["violations"], [])
        self.assertTrue(first["items"])
        self.assertRegex(first["items"][0]["arrive"], r"^\d\d:\d\d$")
        self.assertEqual({v["place_id"] for v in first["votes"]}, set(ids))
        self.assertTrue(all(v["swiped"] == 2 for v in first["votes"]))
        self.assertTrue({i["id"] for i in first["items"]} <= {v["place_id"] for v in first["votes"] if v["like_score"] >= 0.5})
        self.assertEqual(self.client.get(base + "/itinerary").json()["id"], first["id"])
        self.assertEqual(self.client.get(base).json()["status"], "planned")

        url = "/api/itineraries/"
        drop = first["items"][0]["id"]
        self.assertEqual(self.client.patch(url + first["id"], json={"member_id": friend, "action": "approve"}).status_code, 403)
        second = self.client.patch(url + first["id"], json={"member_id": leader, "action": "drop", "place_id": drop}).json()
        self.assertEqual(second["version"], first["version"] + 1)
        self.assertNotIn(drop, [i["id"] for i in second["items"]])
        self.assertIn(drop, [d["id"] for d in second["dropped"]])
        self.assertEqual(self.client.patch(url + first["id"], json={"member_id": leader, "action": "approve"}).status_code, 409)
        closed = self.client.patch(url + second["id"], json={"member_id": leader, "action": "pin", "place_id": "hn_04"})
        self.assertEqual(closed.status_code, 422)
        self.assertIn("Không ghim được", closed.json()["detail"])
        third = self.client.patch(url + second["id"], json={"member_id": leader, "action": "pin", "place_id": drop}).json()
        self.assertIn(drop, [i["id"] for i in third["items"]])
        self.assertEqual(third["violations"], [])
        self.assertEqual(self.client.patch(url + third["id"], json={"member_id": leader, "action": "drop"}).status_code, 422)
        approved = self.client.patch(url + third["id"], json={"member_id": leader, "action": "approve"}).json()
        self.assertEqual(approved["status"], "approved")
        self.assertEqual(self.client.get(base + "/itinerary").json()["id"], third["id"])
        self.assertEqual(self.client.post(base + "/itinerary", json={"member_id": leader}).status_code, 409)
        self.assertEqual(self.client.post(base + "/swipes", json={"member_id": leader, "place_id": ids[0], "liked": False}).status_code, 409)
        self.assertEqual(self.client.patch(url + "it_missing", json={"member_id": leader, "action": "approve"}).status_code, 404)

    def test_new_swipe_marks_draft_stale(self):
        code, leader = self.group()
        base = f"/api/groups/{code}"
        pid = self.client.get(base + "/deck").json()["cards"][0]["id"]
        self.client.post(base + "/swipes", json={"member_id": leader, "place_id": pid, "liked": True})
        draft = self.client.post(base + "/itinerary", json={"member_id": leader}).json()
        self.client.post(base + "/swipes", json={"member_id": leader, "place_id": pid, "liked": False})
        self.assertEqual(self.client.get(base + "/itinerary").status_code, 404)
        r = self.client.patch("/api/itineraries/" + draft["id"], json={"member_id": leader, "action": "approve"})
        self.assertEqual(r.status_code, 409)


if __name__ == "__main__":
    if not os.environ.get("TEST_DATABASE_URL"):
        sys.exit("Cần TEST_DATABASE_URL trỏ đến Postgres dùng cho test; xem README mục Kiểm thử backend.")
    unittest.main(verbosity=2)
