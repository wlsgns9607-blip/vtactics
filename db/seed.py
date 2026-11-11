"""
DB 생성 스크립트

  python db/seed.py

1) db/schema.sql 실행 → 테이블/뷰 생성
2) data/players_data.py 의 경기 전체 기록 입력 (+ 자동 분석 코멘트)
3) data/sets/set1~4.txt (문자중계) 파싱 → 세트별 기록·라인업·득점 랠리 입력, 등번호 채우기
4) data/scenarios.py 의 전술 시나리오 입력
5) static/js/data.js 생성 (서버 없이 index.html을 바로 열 때 쓰는 폴백 데이터)

※ 사용자가 작성한 최종 리뷰(reviews 테이블)는 DB를 다시 만들 때도 그대로 보존합니다.
"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))

from typing import Any, Dict, List                        # noqa: E402

import players_data as _pd                                # noqa: E402  # type: ignore
from scenarios import SCENARIOS                           # noqa: E402  # type: ignore
import parse_set                                          # noqa: E402  # type: ignore

# 선수 기록 dict 는 값 타입이 섞여 있어(str/int/tuple/None) Pylance 가 유니온으로 추론해
# 언패킹(*p["attack"])·대입에서 빨간 밑줄을 표시함 → 명시적으로 Any 로 지정
PLAYERS: Dict[str, List[Dict[str, Any]]] = _pd.PLAYERS
STARTING_LINEUP: Dict[str, Dict[str, Any]] = _pd.STARTING_LINEUP
TEAMS: Dict[str, Dict[str, Any]] = _pd.TEAMS

DB_PATH = ROOT / "db" / "volleyball.db"
SCHEMA = ROOT / "db" / "schema.sql"
FALLBACK_JS = ROOT / "static" / "js" / "data.js"
SET_DIR = ROOT / "data" / "sets"

# 홈 테마 색상 (근사값 — 공식 컬러 확정 시 여기만 수정)
THEME = {
    "KGC":  {"primary": "#E2252B", "accent": "#FF8A5B", "bg": "#2A1A1E"},
    "HDEC": {"primary": "#14A06B", "accent": "#4FD1C5", "bg": "#16252A"},
}
DEFAULT_HOME = "KGC"


def pct(m, t):
    return round(m / t * 100, 1) if t else None


# ───────────── 경기 전체 코멘트 ─────────────
def make_comment(p):
    """기록 수치만으로 분석 코멘트를 만든다."""
    if not p["sets"]:
        return "이번 경기 출전 기록이 없습니다."
    out = []
    am, at = p["attack"]
    if at >= 10:
        line = f"공격 {am}/{at}(성공률 {p['attack_pct']}%), 점유율 {p['attack_share']}%."
        if p["attack_share"] and p["attack_share"] >= 25:
            line += " 팀 공격의 중심축."
        if p["attack_pct"] and p["attack_pct"] >= 40:
            line += " 효율 높은 결정력."
        elif p["attack_pct"] and p["attack_pct"] < 33:
            line += " 공격 효율 개선이 과제."
        out.append(line)
    bm, bt = p["block"]
    if bm >= 3:
        out.append(f"블로킹 {bm}득점({bm}/{bt})으로 네트를 장악.")
    elif p["pos"] == "MB" and bt >= 10 and bm == 0:
        out.append(f"블로킹 득점 0/{bt} — 네트에서 상대 공격을 끊어내지 못함.")
    sm, st = p["set"]
    if p["pos"] == "S" and st >= 20:
        out.append(f"세트 {sm}/{st}({pct(sm, st)}%)로 공격 배분을 책임.")
    rm, rt = p["receive"]
    if rt >= 9:
        r = pct(rm, rt)
        if r is not None:
            if p["pos"] == "L":
                out.append(f"리시브 정확 {rm}/{rt}({r}%).")
            elif r < 35:
                out.append(f"리시브 정확 {rm}/{rt}({r}%) — 상대 목적타 서브의 표적이 될 수 있음.")
            else:
                out.append(f"리시브 정확 {rm}/{rt}({r}%)로 리시브 라인을 지탱.")
    dm, dt = p["dig"]
    if dt >= 8:
        d = pct(dm, dt)
        if d is not None:
            out.append(f"디그 {dm}/{dt}({d}%)" + (" — 후위 수비의 핵심." if d >= 85 else "."))
    vm, vt = p["serve"]
    if vm >= 2:
        out.append(f"서브 득점 {vm}개.")
    if p["errors"] and p["errors"] >= 6:
        out.append(f"범실 {p['errors']}개는 경계해야 할 부분.")
    if not out:
        out.append(f"{p['sets']}세트 출전, 교체·로테이션 자원으로 활용.")
    return " ".join(out)


# ───────────── 세트별 코멘트 ─────────────
def make_set_comment(p, r, errors, team_att):
    out = []
    am, at = r["attack"]
    if at >= 5:
        rate = am / at * 100
        s = f"공격 {am}/{at}({rate:.1f}%)"
        full = p["attack_pct"]
        if full is not None and abs(rate - full) >= 12:
            s += f", 경기 평균({full:.1f}%) 대비 {rate - full:+.1f}%p"
        share = at / team_att * 100 if team_att else 0
        if share >= 30:
            s += f" · 팀 공격의 {share:.0f}% 담당"
        out.append(s + ".")
    elif at > 0:
        out.append(f"공격 {am}/{at}.")
    bm, bt = r["block"]
    if bm >= 1:
        out.append(f"블로킹 {bm}득점.")
    elif bt >= 5:
        out.append(f"블로킹 시도 {bt}회, 득점 없음.")
    sm, st = r["set"]
    if p["pos"] == "S" and st >= 8:
        out.append(f"세트 {sm}/{st}({sm / st * 100:.1f}%)로 공격 배분.")
    rm, rt = r["receive"]
    if rt >= 4:
        rr = rm / rt * 100
        txt = f"리시브 정확 {rm}/{rt}({rr:.1f}%)"
        txt += " — 서브 공략의 표적." if (p["pos"] != "L" and rr < 35) else "."
        out.append(txt)
    dm, dt = r["dig"]
    if dt >= 4:
        out.append(f"디그 {dm}/{dt}({dm / dt * 100:.1f}%).")
    vm, vt = r["serve"]
    if vm >= 1:
        out.append(f"서브 득점 {vm}개.")
    if errors >= 2:
        out.append(f"범실 {errors}개.")
    if not out:
        busy = any(r[c][1] for c in parse_set.CATS) or errors
        out.append("이번 세트 기록이 적습니다." if busy else "이번 세트 출전 기록 없음.")
    return " ".join(out)


# ───────────── 세트별 주전 7인 추정 ─────────────
def derive_lineup(team, st):
    plist = PLAYERS[team]
    tr = lambda p, c: st[p["name"]][c][1] if p["name"] in st else 0  # noqa: E731
    used, chosen = set(), {}

    def pick(pos, key, n):
        cand = sorted([p for p in plist if p["pos"] == pos and p["name"] not in used], key=key, reverse=True)
        res = cand[:n]
        used.update(p["name"] for p in res)
        return res

    chosen["S"] = (pick("S", lambda p: tr(p, "set"), 1) or [None])[0]
    chosen["L"] = (pick("L", lambda p: tr(p, "dig") + tr(p, "receive"), 1) or [None])[0]
    chosen["OP"] = (pick("OP", lambda p: tr(p, "attack"), 1) or [None])[0]
    oh = pick("OH", lambda p: tr(p, "attack") + tr(p, "receive"), 2)
    mb = pick("MB", lambda p: tr(p, "block") + tr(p, "attack"), 2)
    chosen["OH1"], chosen["OH2"] = (oh + [None, None])[:2]
    chosen["MB1"], chosen["MB2"] = (mb + [None, None])[:2]
    return {slot: p["name"] for slot, p in chosen.items() if p}


# ───────────── DB 생성 ─────────────
def build():
    old_review = None
    if DB_PATH.exists():
        try:
            c = sqlite3.connect(DB_PATH)
            old_review = c.execute("SELECT content_json, updated_at FROM reviews WHERE id=1").fetchone()
            c.close()
        except sqlite3.Error:
            pass
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))

    for tid, t in TEAMS.items():
        th = THEME[tid]
        con.execute(
            "INSERT INTO teams VALUES (?,?,?,?,?,?,?)",
            (tid, t["name"], t["short"], th["primary"], th["accent"], th["bg"],
             1 if tid == DEFAULT_HOME else 0),
        )

    set_files = sorted(SET_DIR.glob("set[0-9].txt"))
    numbers: Dict[str, Any] = parse_set.jersey_numbers(set_files)

    name_to_id: Dict[str, Any] = {}
    by_name: Dict[str, Dict[str, Any]] = {}
    for tid, plist in PLAYERS.items():
        for p in plist:
            p["number"] = p["number"] or numbers.get(p["name"])
            player_vals = (
                tid, p["name"], p["pos"], p["number"], p["sets"], p["points"],
                p["attack"][0], p["attack"][1], p["attack_pct"], p["attack_share"],
                p["serve"][0], p["serve"][1], p["block"][0], p["block"][1],
                p["dig"][0], p["dig"][1], p["receive"][0], p["receive"][1],
                p["set"][0], p["set"][1], p["errors"], make_comment(p)
            )
            cur = con.execute(
                """INSERT INTO players (team_id,name,position,number,sets_played,points,
                   att_made,att_tried,att_pct,att_share,srv_made,srv_tried,blk_made,blk_tried,
                   dig_made,dig_tried,rcv_made,rcv_tried,set_made,set_tried,errors,comment)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                player_vals,
            )
            name_to_id[p["name"]] = cur.lastrowid
            by_name[p["name"]] = p

    for tid, slots in STARTING_LINEUP.items():
        for slot, name in slots.items():
            con.execute("INSERT INTO lineups VALUES (?,?,?)", (tid, slot, name_to_id[name]))

    for i, s in enumerate(SCENARIOS):
        con.execute(
            "INSERT INTO scenarios (code,title,subtitle,attack_team,sort_order,phases_json) "
            "VALUES (?,?,?,?,?,?)",
            (s["code"], s["title"], s["subtitle"], s["attack_team"], i,
             json.dumps(s["phases"], ensure_ascii=False)),
        )

    # ── 세트별 기록 ──
    for f in set_files:
        n = int(f.stem[3:])
        rallies = parse_set.parse_rallies(f)
        events, _ = parse_set.read_events(f)
        st, ex = parse_set.aggregate(events)
        score = rallies[-1]["score"]
        winner = "KGC" if score["KGC"] > score["HDEC"] else "HDEC"
        con.execute("INSERT INTO sets VALUES (?,?,?,?)", (n, score["KGC"], score["HDEC"], winner))

        team_att = {t: sum(st[p["name"]]["attack"][1] for p in PLAYERS[t] if p["name"] in st) for t in PLAYERS}
        for tid, plist in PLAYERS.items():
            for p in plist:
                nm = p["name"]
                if nm not in st and not ex[nm]["errors"]:
                    continue
                r = {c: st[nm][c] for c in parse_set.CATS}
                errs = ex[nm]["errors"]
                points = r["attack"][0] + r["serve"][0] + r["block"][0]
                set_stat_vals = (
                    n, name_to_id[nm],
                    r["attack"][0], r["attack"][1],
                    r["serve"][0], r["serve"][1],
                    r["block"][0], r["block"][1],
                    r["dig"][0], r["dig"][1],
                    r["receive"][0], r["receive"][1],
                    r["set"][0], r["set"][1],
                    ex[nm]["blk_assist"], errs, points,
                    make_set_comment(p, r, errs, team_att[tid]),
                )
                con.execute(
                    """INSERT INTO set_stats VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    set_stat_vals,
                )
            for slot, nm in derive_lineup(tid, st).items():
                con.execute("INSERT INTO set_lineups VALUES (?,?,?,?)", (n, tid, slot, name_to_id[nm]))

        for r in rallies:
            evs = [{**e, "pid": name_to_id[e["n"]]} for e in r["events"]]
            con.execute(
                "INSERT INTO rallies VALUES (?,?,?,?,?,?,?,?,?)",
                (n, r["no"], r["scorer"], r["server_team"], r["cause"], r["score"]["KGC"],
                 r["score"]["HDEC"], r["point_idx"], json.dumps(evs, ensure_ascii=False)),
            )

    if old_review:
        con.execute("INSERT INTO reviews VALUES (1,?,?)", old_review)
    con.commit()
    return con


def bootstrap_payload(con):
    """서버의 /api/bootstrap 과 동일한 구조 (server.py 에서도 재사용). 사용자 리뷰는 포함하지 않음."""
    con.row_factory = sqlite3.Row
    teams = [dict(r) for r in con.execute("SELECT * FROM teams")]
    players = [dict(r) for r in con.execute("SELECT * FROM v_player_stats ORDER BY team_id, id")]
    lineups = {}
    for r in con.execute("SELECT team_id, slot, player_id FROM lineups"):
        lineups.setdefault(r["team_id"], {})[r["slot"]] = r["player_id"]
    summary = {r["team_id"]: dict(r) for r in con.execute("SELECT * FROM v_team_summary")}
    scenarios = []
    for r in con.execute("SELECT * FROM scenarios ORDER BY sort_order"):
        d = dict(r)
        d["phases"] = json.loads(d.pop("phases_json"))
        scenarios.append(d)

    sets = [dict(r) for r in con.execute("SELECT * FROM sets ORDER BY set_no")]
    set_stats = [dict(r) for r in con.execute("SELECT * FROM set_stats ORDER BY set_no, player_id")]
    set_lineups = {}
    for r in con.execute("SELECT set_no, team_id, slot, player_id FROM set_lineups"):
        set_lineups.setdefault(r["set_no"], {}).setdefault(r["team_id"], {})[r["slot"]] = r["player_id"]
    rallies = []
    for r in con.execute("SELECT * FROM rallies ORDER BY set_no, rally_no"):
        d = dict(r)
        d["events"] = json.loads(d.pop("events_json"))
        rallies.append(d)
    return {"teams": teams, "players": players, "lineups": lineups, "summary": summary,
            "scenarios": scenarios, "sets": sets, "set_stats": set_stats,
            "set_lineups": set_lineups, "rallies": rallies}


def write_fallback(payload):
    FALLBACK_JS.write_text(
        "// 자동 생성 파일 (db/seed.py) — 서버 없이 열 때 사용하는 폴백 데이터\n"
        "window.BOOTSTRAP = " + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    con = build()
    payload = bootstrap_payload(con)
    write_fallback(payload)
    print(f"DB 생성 완료: {DB_PATH}")
    print(f"  선수 {len(payload['players'])}명 · 시나리오 {len(payload['scenarios'])}개 · "
          f"세트 {len(payload['sets'])}개 · 랠리 {len(payload['rallies'])}개")
    for s in payload["sets"]:
        print(f"  {s['set_no']}세트 정관장 {s['kgc_score']} : {s['hdec_score']} 현대건설 ({s['winner']} 승)")
    for tid, s in payload["summary"].items():
        print(f"  {tid}: 공격 {s['att_made']}/{s['att_tried']} · 블로킹 {s['blk_made']}/{s['blk_tried']}"
              f" · 리시브 {s['rcv_made']}/{s['rcv_tried']} ({s['rcv_pct']}%)")
    print(f"폴백 데이터: {FALLBACK_JS} ({FALLBACK_JS.stat().st_size // 1024}KB)")
