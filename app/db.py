"""Postgres: bảy bảng, transaction theo request và nạp dữ liệu idempotent."""
import json
import re
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = """
CREATE TABLE IF NOT EXISTS places (
    id text PRIMARY KEY,
    data jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS travel_times (
    from_id text NOT NULL,
    to_id text NOT NULL,
    mode text NOT NULL CHECK (mode IN ('xe_may', 'o_to', 'di_bo')),
    duration_mins double precision NOT NULL CHECK (duration_mins >= 0),
    PRIMARY KEY (from_id, to_id, mode)
);
CREATE TABLE IF NOT EXISTS groups (
    id text PRIMARY KEY,
    code varchar(6) NOT NULL UNIQUE,
    config jsonb NOT NULL,
    status text NOT NULL DEFAULT 'swiping' CHECK (status IN ('swiping', 'planned', 'approved')),
    deck_source text,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS members (
    id text PRIMARY KEY,
    group_id text NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    nickname text NOT NULL,
    nickname_key text NOT NULL,
    is_leader boolean NOT NULL DEFAULT false,
    joined_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (group_id, nickname_key),
    UNIQUE (group_id, id)
);
CREATE UNIQUE INDEX IF NOT EXISTS one_leader_per_group ON members(group_id) WHERE is_leader;
CREATE TABLE IF NOT EXISTS deck_cards (
    group_id text NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    place_id text NOT NULL REFERENCES places(id),
    rank integer NOT NULL CHECK (rank > 0),
    ai_reason text NOT NULL,
    PRIMARY KEY (group_id, place_id),
    UNIQUE (group_id, rank)
);
CREATE TABLE IF NOT EXISTS swipes (
    group_id text NOT NULL,
    member_id text NOT NULL,
    place_id text NOT NULL,
    liked boolean NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (member_id, place_id),
    FOREIGN KEY (group_id, member_id) REFERENCES members(group_id, id) ON DELETE CASCADE,
    FOREIGN KEY (group_id, place_id) REFERENCES deck_cards(group_id, place_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS swipes_group_idx ON swipes(group_id);
CREATE TABLE IF NOT EXISTS itineraries (
    id text PRIMARY KEY,
    group_id text NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'stale')),
    data jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
"""


def travel_rows(matrix):
    """Ma trận OSRM ([phút, mét] theo profile car / bike / foot) → phút theo phương tiện, cùng công thức với bộ xếp lịch."""
    from codebase.places import PROFILE, travel_leg
    pairs = {tuple(key.split("|")[:2]) for key in matrix}
    return [(a, b, mode, travel_leg(a, (0, 0), b, (0, 0), mode)[0])
            for a, b in sorted(pairs) for mode in PROFILE if "%s|%s|%s" % (a, b, PROFILE[mode]) in matrix]


class Database:
    def __init__(self, url, schema=None):
        if not url:
            raise ValueError("Cần DATABASE_URL để khởi động backend web.")
        if schema and not re.fullmatch(r"[a-z_][a-z0-9_]*", schema):
            raise ValueError("Tên schema không hợp lệ.")
        self.url = url
        self.schema = schema

    def connect(self):
        options = {"options": "-csearch_path=" + self.schema} if self.schema else {}
        return psycopg.connect(self.url, row_factory=dict_row, connect_timeout=5, **options)

    def initialize(self):
        """Nạp lại nguồn bằng upsert, giữ nguyên nhóm/thành viên/phiếu đã lưu."""
        places = json.loads((ROOT / "data/hanoi_places.json").read_text(encoding="utf-8-sig"))
        matrix = json.loads((ROOT / "data/travel_times.json").read_text(encoding="utf-8"))
        with self.connect() as conn:
            conn.execute("SELECT pg_advisory_xact_lock(790063)")
            conn.execute(SCHEMA)
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO places (id, data) VALUES (%s, %s) "
                    "ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data",
                    [(p["id"], Jsonb(p)) for p in places],
                )
                cur.executemany(
                    "INSERT INTO travel_times (from_id, to_id, mode, duration_mins) VALUES (%s, %s, %s, %s) "
                    "ON CONFLICT (from_id, to_id, mode) DO UPDATE SET duration_mins = EXCLUDED.duration_mins",
                    travel_rows(matrix),
                )
