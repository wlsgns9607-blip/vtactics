"""
V-리그 전술 분석 시뮬레이터 - API 서버 (Python 표준 라이브러리만 사용)

  python server.py            → http://localhost:8000
  python server.py 9000       → 포트 변경

DB가 없으면 자동으로 db/seed.py 를 실행해 생성합니다.

API
  GET /api/bootstrap            앱 초기 데이터 전체 (팀·선수·라인업·세트·랠리·시나리오)
  GET /api/teams                팀 목록 + 테마 컬러
  GET /api/players?team=KGC     선수 기록 (성공률 계산 포함, v_player_stats 뷰)
  GET /api/players/<id>         선수 1명
  GET /api/summary              팀 합계 (v_team_summary 뷰)
  GET /api/scenarios            전술 시나리오
  GET /api/sets                 세트 스코어 + 세트별 팀 합계 (v_set_team_summary 뷰)
  GET /api/sets/<n>/players     세트별 선수 기록 (v_set_player_stats 뷰)
  GET /api/rallies?set=1        세트의 득점 랠리 (리플레이용)
  GET /api/review               저장된 최종 리뷰
  PUT /api/review               최종 리뷰 저장 (JSON 객체)
"""
import json
import sqlite3
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DB_PATH = ROOT / "db" / "volleyball.db"
sys.path.insert(0, str(ROOT / "db"))

import seed  # noqa: E402  # type: ignore

MAX_BODY = 1_000_000  # 리뷰 본문 최대 1MB


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def rows(sql, args=()):
    con = db()
    try:
        return [dict(r) for r in con.execute(sql, args)]
    finally:
        con.close()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    # ── GET ──
    def do_GET(self):
        url = urlparse(self.path)
        if not url.path.startswith("/api/"):
            return super().do_GET()

        parts = url.path.strip("/").split("/")[1:]
        q = parse_qs(url.query)
        try:
            if parts == ["bootstrap"]:
                con = db()
                try:
                    return self.send_json(seed.bootstrap_payload(con))
                finally:
                    con.close()
            if parts == ["teams"]:
                return self.send_json(rows("SELECT * FROM teams"))
            if parts == ["summary"]:
                return self.send_json(rows("SELECT * FROM v_team_summary"))
            if parts == ["players"]:
                team = q.get("team", [None])[0]
                if team:
                    return self.send_json(rows(
                        "SELECT * FROM v_player_stats WHERE team_id=? ORDER BY id", (team,)))
                return self.send_json(rows("SELECT * FROM v_player_stats ORDER BY team_id, id"))
            if len(parts) == 2 and parts[0] == "players" and parts[1].isdigit():
                r = rows("SELECT * FROM v_player_stats WHERE id=?", (int(parts[1]),))
                return self.send_json(r[0]) if r else self.send_json({"error": "not found"}, 404)
            if parts == ["scenarios"]:
                out = rows("SELECT * FROM scenarios ORDER BY sort_order")
                for s in out:
                    s["phases"] = json.loads(s.pop("phases_json"))
                return self.send_json(out)
            if parts == ["sets"]:
                sets = rows("SELECT * FROM sets ORDER BY set_no")
                summ = rows("SELECT * FROM v_set_team_summary ORDER BY set_no, team_id")
                for s in sets:
                    s["teams"] = {r["team_id"]: r for r in summ if r["set_no"] == s["set_no"]}
                return self.send_json(sets)
            if len(parts) == 3 and parts[0] == "sets" and parts[1].isdigit() and parts[2] == "players":
                return self.send_json(rows(
                    "SELECT * FROM v_set_player_stats WHERE set_no=? ORDER BY team_id, player_id",
                    (int(parts[1]),)))
            if parts == ["rallies"]:
                n = q.get("set", [None])[0]
                sql = "SELECT * FROM rallies" + (" WHERE set_no=?" if n else "") + " ORDER BY set_no, rally_no"
                out = rows(sql, (int(n),) if n else ())
                for r in out:
                    r["events"] = json.loads(r.pop("events_json"))
                return self.send_json(out)
            if parts == ["review"]:
                r = rows("SELECT content_json, updated_at FROM reviews WHERE id=1")
                if not r:
                    return self.send_json({"content": {}, "updated_at": None})
                return self.send_json({"content": json.loads(r[0]["content_json"]),
                                       "updated_at": r[0]["updated_at"]})
            return self.send_json({"error": "unknown endpoint"}, 404)
        except (sqlite3.Error, ValueError) as e:
            return self.send_json({"error": str(e)}, 500)

    # ── PUT: 최종 리뷰 저장 ──
    def do_PUT(self):
        url = urlparse(self.path)
        if url.path.rstrip("/") != "/api/review":
            return self.send_json({"error": "unknown endpoint"}, 404)
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n <= 0 or n > MAX_BODY:
                return self.send_json({"error": "invalid body size"}, 413 if n > MAX_BODY else 400)
            data = json.loads(self.rfile.read(n).decode("utf-8"))
            if not isinstance(data, dict):
                return self.send_json({"error": "JSON object required"}, 400)
            con = db()
            try:
                con.execute(
                    "INSERT INTO reviews (id, content_json, updated_at) "
                    "VALUES (1, ?, datetime('now','localtime')) "
                    "ON CONFLICT(id) DO UPDATE SET content_json=excluded.content_json, "
                    "updated_at=excluded.updated_at",
                    (json.dumps(data, ensure_ascii=False),))
                con.commit()
                ts = con.execute("SELECT updated_at FROM reviews WHERE id=1").fetchone()[0]
            finally:
                con.close()
            return self.send_json({"ok": True, "updated_at": ts})
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self.send_json({"error": "invalid JSON"}, 400)
        except sqlite3.Error as e:
            return self.send_json({"error": str(e)}, 500)

    do_POST = do_PUT

    def log_message(self, fmt, *args):
        try:
            msg = fmt % args if args else fmt
            if "/api/" in str(msg):
                sys.stderr.write("[api] " + str(msg) + "\n")
        except Exception:
            pass


if __name__ == "__main__":
    if not DB_PATH.exists():
        print("DB가 없어 새로 생성합니다…")
        con = seed.build()
        seed.write_fallback(seed.bootstrap_payload(con))
        con.close()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"전술 분석 시뮬레이터 실행 중 → http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
