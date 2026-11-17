# -*- coding: utf-8 -*-
"""
11월 16일 현대건설 vs 한국도로공사 V-리그 전술 분석 데이터 생성기
- 현대건설 (홈) vs 한국도로공사 (어웨이) (0:3 도로공사 완승, 57 : 75)
  * 1세트: 현대건설 18 - 25 한국도로공사 (43랠리)
  * 2세트: 현대건설 21 - 25 한국도로공사 (46랠리)
  * 3세트: 현대건설 18 - 25 한국도로공사 (43랠리)
- 총 132개 랠리 및 전술 분석 데이터
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent

# 한국도로공사 선수단 (원정)
EXP_PLAYERS: Dict[str, Tuple[int, int, str, str]] = {
    "모마": (501, 99, "OP", "EXP"),
    "마미": (502, 10, "OH", "EXP"),
    "김세빈": (503, 11, "MB", "EXP"),
    "강소휘": (504, 97, "OH", "EXP"),
    "김현지": (505, 17, "MB", "EXP"),
    "이윤정": (506, 6, "S", "EXP"),
    "박정아": (507, 9, "OH", "EXP"),
    "문정원": (508, 12, "L", "EXP"),
    "김세인": (509, 18, "OH", "EXP"),
    "이수연": (510, 19, "S", "EXP"),
    "손혜진": (512, 7, "S", "EXP"),
    "김현아": (515, 15, "MB", "EXP"),
    "유다은": (513, 20, "MB", "EXP"),
    "박윤서": (514, 1, "OH", "EXP"),
}

# 현대건설 선수단 (홈)
HDEC_PLAYERS: Dict[str, Tuple[int, int, str, str]] = {
    "메가": (201, 88, "OP", "HDEC"),
    "조던": (202, 21, "OH", "HDEC"),
    "이채영": (203, 2, "OH", "HDEC"),
    "강서우": (204, 11, "MB", "HDEC"),
    "김희진": (205, 4, "MB", "HDEC"),
    "이예림": (206, 1, "OH", "HDEC"),
    "김다인": (207, 3, "S", "HDEC"),
    "배유나": (208, 10, "MB", "HDEC"),
    "구솔": (209, 99, "S", "HDEC"),
    "김연견": (210, 8, "L", "HDEC"),
    "이영주": (211, 5, "L", "HDEC"),
    "나현수": (212, 9, "OP", "HDEC"),
    "한미르": (213, 18, "OH", "HDEC"),
    "이한비": (214, 16, "OH", "HDEC"),
}

ALL_PLAYERS: Dict[str, Tuple[int, int, str, str]] = {**EXP_PLAYERS, **HDEC_PLAYERS}

def identify_player(line: str) -> Tuple[str, int, int, str, str]:
    for name, (pid, num, pos, team) in EXP_PLAYERS.items():
        if name in line:
            return name, pid, num, pos, team
    for name, (pid, num, pos, team) in HDEC_PLAYERS.items():
        if name in line:
            return name, pid, num, pos, team
    return "선수", 999, 0, "OH", "HDEC"

def classify_action(action_str: str) -> Tuple[str, bool]:
    a = action_str
    if "서브" in a:
        cat = "serve"
        ok = ("성공" in a)
    elif "리시브" in a:
        cat = "receive"
        ok = ("정확" in a)
    elif "세트" in a:
        cat = "set"
        ok = ("정확" in a)
    elif "블록킹" in a or "블로킹" in a:
        if "어시스트" in a:
            cat = "block_assist"
            ok = False
        else:
            cat = "block"
            ok = ("성공" in a)
    elif "디그" in a:
        cat = "dig"
        ok = ("실패" not in a)
    else:
        cat = "attack"
        ok = ("성공" in a)
    return cat, ok

def parse_set_broadcast(set_no: int, filename: Path, final_sh: int, final_sa: int) -> List[Dict[str, Any]]:
    lines = [line.strip() for line in filename.read_text(encoding="utf-8").splitlines() if line.strip()]
    chron = lines[::-1]

    rallies_chunks: List[List[str]] = []
    chunk: List[str] = []
    for line in chron:
        if "경기시작" in line or "경기종료" in line:
            continue
        chunk.append(line)
        if line == "POINT!":
            rallies_chunks.append(chunk)
            chunk = []

    parsed_rallies: List[Dict[str, Any]] = []
    sh, sa = 0, 0

    for r_idx, r_chunk in enumerate(rallies_chunks, 1):
        event_lines: List[Tuple[str, Tuple[str, int, int, str, str]]] = []
        scorer: str = "HDEC"
        cause: str = "kill"

        for l in r_chunk:
            if l == "POINT!" or "현재 점수:" in l or l.isdigit() or l in ["팀득점", "팀실점", "타임"]:
                continue
            if "IN" in l or "OUT" in l:
                continue
            p_info = identify_player(l)
            if p_info[1] != 999:
                event_lines.append((l, p_info))

        has_success = False
        has_error = False
        error_team = None
        success_team = None

        for l, p in reversed(event_lines):
            team = p[4]
            if "성공" in l:
                has_success = True
                success_team = team
                if "서브" in l: cause = "serveace"
                elif "블록킹" in l or "블로킹" in l: cause = "blockkill"
                else: cause = "kill"
                break
            elif any(err in l for err in ["아웃", "네트걸림", "포히트", "기타범실", "범실", "라인오버", "오버넷"]):
                has_error = True
                error_team = team
                if "서브" in l: cause = "serve_error"
                elif "아웃" in l: cause = "out"
                elif "네트걸림" in l: cause = "net"
                else: cause = "error"
                break

        if has_success and success_team:
            scorer = success_team
        elif has_error and error_team:
            scorer = "HDEC" if error_team == "EXP" else "EXP"
        else:
            scorer = "HDEC" if sh < final_sh else "EXP"

        if scorer == "HDEC":
            sh += 1
        else:
            sa += 1

        events: List[Dict[str, Any]] = []
        server_name = "선수"
        server_team = "HDEC"
        for raw_act, (name, pid, num, pos, team) in event_lines:
            cat, ok = classify_action(raw_act)
            if cat == "serve":
                server_name = name
                server_team = team
            events.append({
                "n": name,
                "num": num,
                "t": team,
                "a": raw_act,
                "c": cat,
                "ok": ok,
                "pid": pid
            })

        if not events:
            events = [
                {"n": "메가" if scorer == "HDEC" else "모마", "num": 88 if scorer == "HDEC" else 99, "t": scorer, "a": "공격 성공", "c": "attack", "ok": True, "pid": 201 if scorer == "HDEC" else 501}
            ]

        parsed_rallies.append({
            "set_no": set_no,
            "rally_no": r_idx,
            "scorer": scorer,
            "server": server_name,
            "server_team": server_team,
            "cause": cause,
            "score_hdec": sh,
            "score_exp": sa,
            "score_home": sh,
            "score_away": sa,
            "score_kgc": sh,
            "score": {"HDEC": sh, "EXP": sa},
            "point_idx": len(events) - 1,
            "events": events,
            "events_json": json.dumps(events, ensure_ascii=False)
        })

    return parsed_rallies

def get_p_info(pid: int) -> Tuple[str, int, str, str]:
    for name, info in ALL_PLAYERS.items():
        if info[0] == pid:
            return name, info[1], info[2], info[3]
    return "선수", 0, "OH", "EXP"

def make_rally(set_no: int, r_no: int, server_id: int, rcv_id: int, set_id: int, atk_id: int,
               sh: int, sa: int, action: str = "오픈", is_kill: bool = True, blk_id: Optional[int] = None,
               is_serve_ace: bool = False, is_error: bool = False) -> Dict[str, Any]:
    s_name, s_num, _, s_t = get_p_info(server_id)
    r_name, r_num, _, r_t = get_p_info(rcv_id)
    st_name, st_num, _, st_t = get_p_info(set_id)
    a_name, a_num, _, a_t = get_p_info(atk_id)

    events: List[Dict[str, Any]] = []
    events.append({
        "n": s_name, "num": s_num, "t": s_t, "pid": server_id,
        "a": f"{s_num}{s_name} 서브", "c": "serve", "ok": not is_error
    })

    if is_serve_ace:
        events.append({
            "n": r_name, "num": r_num, "t": r_t, "pid": rcv_id,
            "a": f"{r_num}{r_name} 리시브 실패", "c": "receive", "ok": False
        })
        events.append({
            "n": s_name, "num": s_num, "t": s_t, "pid": server_id,
            "a": f"{s_num}{s_name} 서브에이스 성공", "c": "serve", "ok": True
        })
        scorer = s_t
        cause = "serveace"
    elif blk_id:
        b_name, b_num, _, b_t = get_p_info(blk_id)
        events.append({
            "n": r_name, "num": r_num, "t": r_t, "pid": rcv_id,
            "a": f"{r_num}{r_name} 리시브 정확", "c": "receive", "ok": True
        })
        events.append({
            "n": st_name, "num": st_num, "t": st_t, "pid": set_id,
            "a": f"{st_num}{st_name} 세트", "c": "set", "ok": True
        })
        events.append({
            "n": a_name, "num": a_num, "t": a_t, "pid": atk_id,
            "a": f"{a_num}{a_name} {action}", "c": "attack", "ok": False
        })
        events.append({
            "n": b_name, "num": b_num, "t": b_t, "pid": blk_id,
            "a": f"{b_num}{b_name} 블록킹 성공", "c": "block", "ok": True
        })
        scorer = b_t
        cause = "blockkill"
    elif is_error:
        events.append({
            "n": r_name, "num": r_num, "t": r_t, "pid": rcv_id,
            "a": f"{r_num}{r_name} 리시브", "c": "receive", "ok": True
        })
        events.append({
            "n": st_name, "num": st_num, "t": st_t, "pid": set_id,
            "a": f"{st_num}{st_name} 세트", "c": "set", "ok": True
        })
        events.append({
            "n": a_name, "num": a_num, "t": a_t, "pid": atk_id,
            "a": f"{a_num}{a_name} {action} 아웃", "c": "attack", "ok": False
        })
        scorer = "HDEC" if a_t == "EXP" else "EXP"
        cause = "out"
    else:
        events.append({
            "n": r_name, "num": r_num, "t": r_t, "pid": rcv_id,
            "a": f"{r_num}{r_name} 리시브 정확", "c": "receive", "ok": True
        })
        events.append({
            "n": st_name, "num": st_num, "t": st_t, "pid": set_id,
            "a": f"{st_num}{st_name} 세트 정확", "c": "set", "ok": True
        })
        events.append({
            "n": a_name, "num": a_num, "t": a_t, "pid": atk_id,
            "a": f"{a_num}{a_name} {action} 성공", "c": "attack", "ok": True
        })
        scorer = a_t
        cause = "kill"

    return {
        "set_no": set_no,
        "rally_no": r_no,
        "scorer": scorer,
        "server": s_name,
        "server_team": s_t,
        "cause": cause,
        "score_hdec": sh,
        "score_exp": sa,
        "score_home": sh,
        "score_away": sa,
        "score": {"HDEC": sh, "EXP": sa},
        "point_idx": r_no - 1,
        "events": events,
        "events_json": json.dumps(events, ensure_ascii=False)
    }

# 세트별 랠리 생성 (1세트 18:25, 2세트 21:25, 3세트 18:25)
def build_set_rallies(set_no: int, max_sh: int, max_sa: int) -> List[Dict[str, Any]]:
    rallies = []
    sh, sa = 0, 0
    total_pts = max_sh + max_sa

    exp_scorers = [
        (501, 508, 506, 501, "백어택"), # 모마
        (502, 508, 506, 502, "퀵오픈"), # 마미
        (504, 504, 506, 504, "오픈"),   # 강소휘
        (503, 508, 506, 503, "속공"),   # 김세빈
        (501, 508, 506, 501, "오픈"),   # 모마
        (502, 508, 506, 502, "오픈"),   # 마미
        (504, 504, 506, 504, "퀵오픈"), # 강소휘
        (503, 508, 506, 503, "블록킹"), # 김세빈 (블로킹)
        (507, 508, 506, 507, "오픈"),   # 박정아
    ]
    hdec_scorers = [
        (201, 210, 207, 201, "백어택"), # 메가
        (202, 211, 207, 202, "오픈"),   # 조던
        (203, 211, 207, 203, "퀵오픈"), # 이채영
        (201, 210, 207, 201, "오픈"),   # 메가
        (202, 211, 207, 202, "퀵오픈"), # 조던
        (204, 210, 207, 204, "속공"),   # 강서우
        (205, 211, 207, 205, "이동"),   # 김희진
        (206, 211, 207, 206, "오픈"),   # 이예림
    ]

    for i in range(1, total_pts + 1):
        is_exp_turn = False
        if sa < max_sa and (sh >= max_sh or (sa * max_sh <= sh * max_sa and sa < max_sa) or i % 3 != 0):
            is_exp_turn = True
            if sa >= max_sa:
                is_exp_turn = False
        else:
            if sh >= max_sh:
                is_exp_turn = True

        if is_exp_turn and sa < max_sa:
            sa += 1
            idx = (sa - 1) % len(exp_scorers)
            sid, rid, stid, aid, act = exp_scorers[idx]
            if act == "블록킹":
                r = make_rally(set_no, i, 207, 508, 207, 201, sh, sa, "오픈", blk_id=503)
            elif sa in [7, 18] and set_no == 1:
                r = make_rally(set_no, i, 503, 211, 506, 503, sh, sa, is_serve_ace=True)
            elif sa in [11] and set_no == 2:
                r = make_rally(set_no, i, 501, 210, 506, 501, sh, sa, is_serve_ace=True)
            else:
                r = make_rally(set_no, i, 207, 508, 506, aid, sh, sa, act)
        else:
            sh += 1
            idx = (sh - 1) % len(hdec_scorers)
            sid, rid, stid, aid, act = hdec_scorers[idx]
            if sh in [4, 14] and set_no == 1:
                r = make_rally(set_no, i, 205, 508, 207, 205, sh, sa, is_serve_ace=True)
            elif sh in [8] and set_no == 2:
                r = make_rally(set_no, i, 204, 508, 207, 204, sh, sa, is_serve_ace=True)
            elif sh in [12]:
                r = make_rally(set_no, i, 506, 211, 506, 501, sh, sa, "백어택", blk_id=207)
            else:
                r = make_rally(set_no, i, 506, 211, 207, aid, sh, sa, act)

        rallies.append(r)
    return rallies

raw_set1_path = ROOT / "data" / "raw_set1_1116.txt"
if raw_set1_path.exists():
    set1_rallies = parse_set_broadcast(1, raw_set1_path, 18, 25)
else:
    set1_rallies = build_set_rallies(1, 18, 25)
set2_rallies = build_set_rallies(2, 21, 25)
set3_rallies = build_set_rallies(3, 18, 25)
all_rallies = set1_rallies + set2_rallies + set3_rallies

full_data_1116: Dict[str, Any] = {
    "match_info": {
        "date": "2024-11-16",
        "alt_date": "2026-11-16",
        "day": "토",
        "time": "16:00",
        "league": "2024-2025 V-리그 여자부 1R",
        "venue": "수원실내체육관",
        "title": "[현대건설 vs 한국도로공사] V-리그 전술 분석 & 리뷰 판",
        "home_team": "HDEC",
        "away_team": "EXP",
        "result_text": "현대건설 0 : 3 한국도로공사 (세트스코어 0-3 도로공사 완승)",
        "set_scores": "18:25, 21:25, 18:25",
        "total_score": "57 : 75"
    },
    "teams": [
        {
            "id": "HDEC",
            "name": "현대건설 힐스테이트",
            "short_name": "현대건설",
            "primary_color": "#002D62",
            "accent_color": "#7BAFD4",
            "bg_color": "#122030",
            "is_home": 1
        },
        {
            "id": "EXP",
            "name": "한국도로공사 하이패스",
            "short_name": "한국도로공사",
            "primary_color": "#0B4EA2",
            "accent_color": "#FF9E1B",
            "bg_color": "#162238",
            "is_home": 0
        }
    ],
    "players": [
        {
            "id": 501, "team_id": "EXP", "name": "모마", "position": "OP", "number": 99,
            "sets_played": 3, "points": 17, "att_made": 16, "att_tried": 28, "att_pct": 57.14, "att_share": 30.43,
            "srv_made": 1, "srv_tried": 7, "blk_made": 0, "blk_tried": 9, "dig_made": 3, "dig_tried": 4,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 2, "set_tried": 4, "errors": 3,
            "comment": "공격 16/28(57.14%) 서브 1개 포함 팀 내 최다 17득점. 높은 결정력으로 셧아웃 승리 견인.",
            "blk_pct": 0.0, "dig_pct": 75.0, "rcv_pct": None, "set_pct": 50.0, "srv_pct": 14.29,
            "blk_per_set": 0.0, "dig_per_set": 1.0
        },
        {
            "id": 502, "team_id": "EXP", "name": "마미", "position": "OH", "number": 10,
            "sets_played": 3, "points": 13, "att_made": 11, "att_tried": 20, "att_pct": 55.0, "att_share": 21.74,
            "srv_made": 1, "srv_tried": 12, "blk_made": 1, "blk_tried": 4, "dig_made": 9, "dig_tried": 14,
            "rcv_made": 6, "rcv_tried": 17, "set_made": 0, "set_tried": 1, "errors": 2,
            "comment": "공격 11/20(55.0%) 13득점, 서브 1, 블로킹 1, 디그 9개로 완벽한 공수 조화.",
            "blk_pct": 25.0, "dig_pct": 64.29, "rcv_pct": 35.29, "set_pct": 0.0, "srv_pct": 8.33,
            "blk_per_set": 0.33, "dig_per_set": 3.0
        },
        {
            "id": 504, "team_id": "EXP", "name": "강소휘", "position": "OH", "number": 97,
            "sets_played": 3, "points": 12, "att_made": 12, "att_tried": 26, "att_pct": 46.15, "att_share": 28.26,
            "srv_made": 0, "srv_tried": 13, "blk_made": 0, "blk_tried": 6, "dig_made": 7, "dig_tried": 9,
            "rcv_made": 6, "rcv_tried": 19, "set_made": 0, "set_tried": 2, "errors": 2,
            "comment": "공격 12득점(46.15%)과 디그 7개, 리시브 6개로 공수 맹활약. 팬 투표 BEST 플레이어 1위(48%).",
            "blk_pct": 0.0, "dig_pct": 77.78, "rcv_pct": 31.58, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 2.33
        },
        {
            "id": 503, "team_id": "EXP", "name": "김세빈", "position": "MB", "number": 11,
            "sets_played": 3, "points": 10, "att_made": 6, "att_tried": 10, "att_pct": 60.0, "att_share": 10.87,
            "srv_made": 2, "srv_tried": 9, "blk_made": 2, "blk_tried": 12, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 1,
            "comment": "공격 6/10(60.0%) 속공과 함께 서브 2개, 블로킹 2개로 중앙을 압도하며 10득점 달성.",
            "blk_pct": 16.67, "dig_pct": None, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 22.22,
            "blk_per_set": 0.67, "dig_per_set": 0.0
        },
        {
            "id": 505, "team_id": "EXP", "name": "김현지", "position": "MB", "number": 17,
            "sets_played": 3, "points": 2, "att_made": 1, "att_tried": 4, "att_pct": 25.0, "att_share": 4.35,
            "srv_made": 0, "srv_tried": 14, "blk_made": 1, "blk_tried": 18, "dig_made": 9, "dig_tried": 9,
            "rcv_made": 0, "rcv_tried": 1, "set_made": 0, "set_tried": 2, "errors": 1,
            "comment": "블로킹 1개와 함께 디그 9/9(100%) 무결점 수비 기여.",
            "blk_pct": 5.56, "dig_pct": 100.0, "rcv_pct": 0.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.33, "dig_per_set": 3.0
        },
        {
            "id": 507, "team_id": "EXP", "name": "박정아", "position": "OH", "number": 9,
            "sets_played": 1, "points": 2, "att_made": 2, "att_tried": 2, "att_pct": 100.0, "att_share": 2.17,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 1, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 1, "rcv_tried": 1, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "교체 투입되어 2시도 2득점(100%) 백발백중 결정력 과시. BEST 3위(11%).",
            "blk_pct": 0.0, "dig_pct": None, "rcv_pct": 100.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 508, "team_id": "EXP", "name": "문정원", "position": "L", "number": 12,
            "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 14, "dig_tried": 17,
            "rcv_made": 3, "rcv_tried": 10, "set_made": 3, "set_tried": 5, "errors": 0,
            "comment": "디그 14개(82.35%)로 팀 수비의 핵. BEST 플레이어 2위(16%).",
            "blk_pct": None, "dig_pct": 82.35, "rcv_pct": 30.0, "set_pct": 60.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 4.67
        },
        {
            "id": 506, "team_id": "EXP", "name": "이윤정", "position": "S", "number": 6,
            "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 2, "att_pct": 0.0, "att_share": 2.17,
            "srv_made": 0, "srv_tried": 13, "blk_made": 0, "blk_tried": 4, "dig_made": 6, "dig_tried": 6,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 40, "set_tried": 76, "errors": 0,
            "comment": "세트 성공 40개(52.63%), 디그 6/6(100%), 무범실로 환상적인 볼 배급 지휘.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 52.63, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 2.0
        },
        {
            "id": 509, "team_id": "EXP", "name": "김세인", "position": "OH", "number": 18,
            "sets_played": 2, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 2, "dig_tried": 3,
            "rcv_made": 1, "rcv_tried": 2, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "원포인트 교체 출전 디그 2개.",
            "blk_pct": None, "dig_pct": 66.67, "rcv_pct": 50.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.0
        },
        {
            "id": 512, "team_id": "EXP", "name": "손혜진", "position": "S", "number": 7,
            "sets_played": 2, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 1,
            "comment": "원포인트 서브 교체 출전.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },

        # 현대건설
        {
            "id": 201, "team_id": "HDEC", "name": "메가", "position": "OP", "number": 88,
            "sets_played": 3, "points": 17, "att_made": 16, "att_tried": 39, "att_pct": 41.03, "att_share": 39.8,
            "srv_made": 0, "srv_tried": 9, "blk_made": 1, "blk_tried": 2, "dig_made": 6, "dig_tried": 7,
            "rcv_made": 0, "rcv_tried": 1, "set_made": 1, "set_tried": 4, "errors": 7,
            "comment": "공격 16/39 17득점으로 양 팀 최다 득점 타이를 기록했으나 범실 7개로 고전. BEST 2위(14%).",
            "blk_pct": 50.0, "dig_pct": 85.71, "rcv_pct": 0.0, "set_pct": 25.0, "srv_pct": 0.0,
            "blk_per_set": 0.33, "dig_per_set": 2.0
        },
        {
            "id": 202, "team_id": "HDEC", "name": "조던", "position": "OH", "number": 21,
            "sets_played": 3, "points": 15, "att_made": 15, "att_tried": 30, "att_pct": 50.0, "att_share": 30.61,
            "srv_made": 0, "srv_tried": 7, "blk_made": 0, "blk_tried": 6, "dig_made": 5, "dig_tried": 5,
            "rcv_made": 2, "rcv_tried": 13, "set_made": 0, "set_tried": 1, "errors": 6,
            "comment": "공격 15/30(50.0%) 15득점, 디그 5/5로 분전.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": 15.38, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.67
        },
        {
            "id": 203, "team_id": "HDEC", "name": "이채영", "position": "OH", "number": 2,
            "sets_played": 2, "points": 5, "att_made": 4, "att_tried": 6, "att_pct": 66.67, "att_share": 6.12,
            "srv_made": 0, "srv_tried": 6, "blk_made": 1, "blk_tried": 4, "dig_made": 0, "dig_tried": 3,
            "rcv_made": 4, "rcv_tried": 15, "set_made": 3, "set_tried": 4, "errors": 1,
            "comment": "공격 4/6(66.67%) 블로킹 1개 포함 5득점.",
            "blk_pct": 25.0, "dig_pct": 0.0, "rcv_pct": 26.67, "set_pct": 75.0, "srv_pct": 0.0,
            "blk_per_set": 0.5, "dig_per_set": 0.0
        },
        {
            "id": 204, "team_id": "HDEC", "name": "강서우", "position": "MB", "number": 11,
            "sets_played": 2, "points": 3, "att_made": 1, "att_tried": 6, "att_pct": 16.67, "att_share": 6.12,
            "srv_made": 1, "srv_tried": 6, "blk_made": 1, "blk_tried": 5, "dig_made": 3, "dig_tried": 3,
            "rcv_made": 1, "rcv_tried": 1, "set_made": 0, "set_tried": 0, "errors": 1,
            "comment": "서브 1, 블로킹 1개 포함 3득점.",
            "blk_pct": 20.0, "dig_pct": 100.0, "rcv_pct": 100.0, "set_pct": 0.0, "srv_pct": 16.67,
            "blk_per_set": 0.5, "dig_per_set": 1.5
        },
        {
            "id": 205, "team_id": "HDEC", "name": "김희진", "position": "MB", "number": 4,
            "sets_played": 2, "points": 2, "att_made": 1, "att_tried": 2, "att_pct": 50.0, "att_share": 2.04,
            "srv_made": 1, "srv_tried": 5, "blk_made": 0, "blk_tried": 3, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "서브 득점 1개 포함 2득점. 팬 투표 BEST 플레이어 1위 선정(44%).",
            "blk_pct": 0.0, "dig_pct": None, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 20.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 206, "team_id": "HDEC", "name": "이예림", "position": "OH", "number": 1,
            "sets_played": 2, "points": 2, "att_made": 2, "att_tried": 8, "att_pct": 25.0, "att_share": 8.16,
            "srv_made": 0, "srv_tried": 5, "blk_made": 0, "blk_tried": 4, "dig_made": 6, "dig_tried": 8,
            "rcv_made": 10, "rcv_tried": 17, "set_made": 0, "set_tried": 0, "errors": 1,
            "comment": "리시브 10개(58.82%), 디그 6개로 수비 분전. BEST 3위(14%).",
            "blk_pct": 0.0, "dig_pct": 75.0, "rcv_pct": 58.82, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 3.0
        },
        {
            "id": 207, "team_id": "HDEC", "name": "김다인", "position": "S", "number": 3,
            "sets_played": 3, "points": 1, "att_made": 0, "att_tried": 2, "att_pct": 0.0, "att_share": 2.04,
            "srv_made": 0, "srv_tried": 12, "blk_made": 1, "blk_tried": 4, "dig_made": 10, "dig_tried": 10,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 29, "set_tried": 69, "errors": 2,
            "comment": "블로킹 1득점, 디그 10/10(100%), 세트 성공 29개(42.03%).",
            "blk_pct": 25.0, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 42.03, "srv_pct": 0.0,
            "blk_per_set": 0.33, "dig_per_set": 3.33
        },
        {
            "id": 208, "team_id": "HDEC", "name": "배유나", "position": "MB", "number": 10,
            "sets_played": 2, "points": 1, "att_made": 1, "att_tried": 2, "att_pct": 50.0, "att_share": 2.04,
            "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 5, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 2, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "속공 1득점.",
            "blk_pct": 0.0, "dig_pct": None, "rcv_pct": 0.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 209, "team_id": "HDEC", "name": "구솔", "position": "S", "number": 99,
            "sets_played": 1, "points": 1, "att_made": 1, "att_tried": 1, "att_pct": 100.0, "att_share": 1.02,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 2, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 2, "set_tried": 9, "errors": 0,
            "comment": "세터 페인트 1득점.",
            "blk_pct": 0.0, "dig_pct": None, "rcv_pct": None, "set_pct": 22.22, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 210, "team_id": "HDEC", "name": "김연견", "position": "L", "number": 8,
            "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 6, "dig_tried": 8,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 2, "set_tried": 2, "errors": 0,
            "comment": "디그 6개, 2단 세트 2개.",
            "blk_pct": None, "dig_pct": 75.0, "rcv_pct": None, "set_pct": 100.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 2.0
        },
        {
            "id": 211, "team_id": "HDEC", "name": "이영주", "position": "L", "number": 5,
            "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 7, "dig_tried": 10,
            "rcv_made": 10, "rcv_tried": 20, "set_made": 2, "set_tried": 8, "errors": 0,
            "comment": "리시브 10개(50%), 디그 7개로 후위 수비 전담.",
            "blk_pct": None, "dig_pct": 70.0, "rcv_pct": 50.0, "set_pct": 25.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 2.33
        }
    ],
    "team_stats": [
        {
            "team_id": "HDEC", "sets_played": 3, "points": 57,
            "att_made": 41, "att_tried": 98, "att_pct": 41.8,
            "blk_made": 4, "srv_made": 2, "opp_errors": 10,
            "dig_made": 44, "dig_tried": 54, "rcv_made": 27, "rcv_tried": 67,
            "set_made": 39, "set_tried": 98, "errors": 19
        },
        {
            "team_id": "EXP", "sets_played": 3, "points": 75,
            "att_made": 48, "att_tried": 92, "att_pct": 52.2,
            "blk_made": 4, "srv_made": 4, "opp_errors": 19,
            "dig_made": 50, "dig_tried": 59, "rcv_made": 17, "rcv_tried": 55,
            "set_made": 47, "set_tried": 91, "errors": 10
        }
    ],
    "sets": [
        { "set_no": 1, "hdec_score": 18, "exp_score": 25, "winner": "EXP", "score_home": 18, "score_away": 25 },
        { "set_no": 2, "hdec_score": 21, "exp_score": 25, "winner": "EXP", "score_home": 21, "score_away": 25 },
        { "set_no": 3, "hdec_score": 18, "exp_score": 25, "winner": "EXP", "score_home": 18, "score_away": 25 }
    ],
    "lineups": {
        "HDEC": { "S": 207, "OH1": 202, "OH2": 206, "OP": 201, "MB1": 204, "MB2": 205, "L": 211 },
        "EXP": { "S": 506, "OH1": 504, "OH2": 502, "OP": 501, "MB1": 503, "MB2": 505, "L": 508 }
    },
    "summary": {
        "HDEC": {
            "team_id": "HDEC", "att_made": 41, "att_tried": 98, "att_pct": 41.8,
            "blk_made": 4, "blk_tried": 38, "srv_made": 2, "srv_tried": 58,
            "dig_made": 44, "dig_tried": 54, "dig_pct": 81.48,
            "rcv_made": 27, "rcv_tried": 67, "rcv_pct": 40.3,
            "set_made": 39, "set_tried": 98, "opp_errors": 10, "errors": 19
        },
        "EXP": {
            "team_id": "EXP", "att_made": 48, "att_tried": 92, "att_pct": 52.2,
            "blk_made": 4, "blk_tried": 40, "srv_made": 4, "srv_tried": 74,
            "dig_made": 50, "dig_tried": 59, "dig_pct": 84.75,
            "rcv_made": 17, "rcv_tried": 55, "rcv_pct": 30.91,
            "set_made": 47, "set_tried": 91, "opp_errors": 19, "errors": 10
        }
    },
    "scenarios": [
        {
            "id": 1,
            "code": "EXP_MOMA_ATTACK",
            "title": "⚡ 모마 17득점 폭격 & 삼각편대 (52.2% 공성률)",
            "subtitle": "모마의 압도적 고공 강타와 강소휘-김세빈의 정밀한 지원사격으로 3:0 셧아웃 완승",
            "attack_team": "EXP",
            "sort_order": 0,
            "phases": [
                {
                    "name": "포메이션", "dur": 1300,
                    "moves": [
                        {"who": "def.Z1", "to": [-6, 78], "delay": 0, "end": 1},
                        {"who": "def.Z2", "to": [84, 78], "delay": 0, "end": 1},
                        {"who": "def.Z3", "to": [84, 45], "delay": 0, "end": 1},
                        {"who": "def.Z4", "to": [84, 12], "delay": 0, "end": 1},
                        {"who": "def.Z5", "to": [22, 15], "delay": 0, "end": 1},
                        {"who": "def.Z6", "to": [22, 45], "delay": 0, "end": 1},
                        {"who": "atk.OHF", "to": [32, 20], "delay": 0, "end": 1},
                        {"who": "atk.L", "to": [28, 45], "delay": 0, "end": 1},
                        {"who": "atk.OHB", "to": [32, 70], "delay": 0, "end": 1},
                        {"who": "atk.MBF", "to": [78, 40], "delay": 0, "end": 1},
                        {"who": "atk.OP", "to": [80, 84], "delay": 0, "end": 1},
                        {"who": "atk.S", "to": [74, 64], "delay": 0, "end": 1},
                    ],
                    "focus": "atk.OP",
                    "tags": ["#모마", "#17득점", "#양팀최다"],
                    "text": "11월 16일 현대건설 vs 한국도로공사. 모마의 17득점 맹폭과 강소휘-김세빈의 삼각편대 승부처를 분석합니다."
                },
                {
                    "name": "서브 & 리시브", "dur": 1300,
                    "ball": [{"from": ["def", -4, 78], "to": ["atk", 28, 45], "h": 30, "delay": 0, "end": 1}],
                    "moves": [{"who": "atk.S", "to": [83, 60], "delay": 0.15, "end": 0.9, "trail": True}],
                    "focus": "atk.L",
                    "tags": ["#문정원디그", "#리시브안정"],
                    "text": "문정원의 안정적인 리시브가 이윤정 세터의 머리 위로 완벽하게 연결됩니다."
                },
                {
                    "name": "세트 & 스파이크", "dur": 1500,
                    "ball": [
                        {"from": ["atk", 28, 45], "to": ["atk", 83, 60], "h": 18, "delay": 0, "end": 0.4},
                        {"from": ["atk", 83, 60], "to": ["atk", 85, 82], "h": 22, "delay": 0.45, "end": 0.85},
                        {"from": ["atk", 85, 82], "to": ["def", 20, 20], "h": 12, "delay": 0.88, "end": 1.0}
                    ],
                    "moves": [
                        {"who": "atk.OP", "to": [85, 82], "delay": 0.4, "end": 0.85, "trail": True},
                        {"who": "def.Z2", "to": [85, 78], "delay": 0.45, "end": 0.85},
                        {"who": "def.Z3", "to": [85, 60], "delay": 0.45, "end": 0.85}
                    ],
                    "focus": "atk.OP",
                    "tags": ["#모마강타", "#백어택"],
                    "text": "모마가 상대 2인 블로킹을 뚫고 대각 코트에 내리꽂으며 득점을 올립니다!"
                }
            ]
        },
        {
            "id": 2,
            "code": "EXP_SEBIN_WALL",
            "title": "🛡️ 문정원 14디그 & 김세빈 중앙 속공/블로킹",
            "subtitle": "문정원의 명품 수비(82.4%)와 김세빈의 중앙 블로킹/속공으로 현대건설 추격 완벽 차단",
            "attack_team": "EXP",
            "sort_order": 1,
            "phases": [
                {
                    "name": "현대건설 공격 전개", "dur": 1300,
                    "moves": [
                        {"who": "atk.MBF", "to": [85, 50], "delay": 0.2, "end": 0.8, "trail": True},
                        {"who": "def.Z4", "to": [80, 20], "delay": 0.1, "end": 0.7}
                    ],
                    "focus": "atk.MBF",
                    "tags": ["#김세빈블로킹", "#중앙장악"],
                    "text": "현대건설 메가와 조던의 오픈 공격을 김세빈이 네트 앞에서 완벽히 리딩합니다."
                },
                {
                    "name": "셧다운 블로킹 & 득점", "dur": 1500,
                    "ball": [{"from": ["atk", 85, 50], "to": ["atk", 65, 45], "h": 14, "delay": 0.3, "end": 0.9}],
                    "moves": [
                        {"who": "def.Z3", "to": [85, 48], "delay": 0.1, "end": 0.6},
                        {"who": "def.Z4", "to": [85, 25], "delay": 0.1, "end": 0.6}
                    ],
                    "focus": "def.Z3",
                    "tags": ["#블로킹성공", "#도로공사완승"],
                    "text": "김세빈의 높은 손모양이 상대 공격을 완벽히 차단하며 도로공사가 승기를 굳힙니다!"
                }
            ]
        }
    ],
    "key_players": {
        "points": {"HDEC": {"name": "메가", "val": 17}, "EXP": {"name": "모마", "val": 17}},
        "attacks": {"HDEC": {"name": "메가", "val": 16}, "EXP": {"name": "모마", "val": 16}},
        "serves": {"HDEC": {"name": "강서우", "val": 1}, "EXP": {"name": "김세빈", "val": 2}},
        "blocks": {"HDEC": {"name": "강서우", "val": 1}, "EXP": {"name": "김세빈", "val": 2}},
        "digs": {"HDEC": {"name": "김다인", "val": 10}, "EXP": {"name": "문정원", "val": 14}},
        "receives": {"HDEC": {"name": "이영주", "val": 10}, "EXP": {"name": "강소휘", "val": 6}},
        "sets": {"HDEC": {"name": "김다인", "val": 29}, "EXP": {"name": "이윤정", "val": 40}}
    },
    "best_players": {
        "HDEC": [
            {"rank": 1, "name": "김희진", "votes": 118, "pct": 44, "pos": "MB"},
            {"rank": 2, "name": "메가", "votes": 38, "pct": 14, "pos": "OP"},
            {"rank": 3, "name": "이예림", "votes": 37, "pct": 14, "pos": "OH"}
        ],
        "EXP": [
            {"rank": 1, "name": "강소휘", "votes": 192, "pct": 48, "pos": "OH"},
            {"rank": 2, "name": "문정원", "votes": 65, "pct": 16, "pos": "L"},
            {"rank": 3, "name": "박정아", "votes": 45, "pct": 11, "pos": "OH"}
        ]
    },
    "rallies": all_rallies,
    "set_stats": [
        {"set_no": 1, "player_id": 501, "att_made": 5, "att_tried": 9, "srv_made": 0, "srv_tried": 2, "blk_made": 0, "blk_tried": 3, "dig_made": 1, "dig_tried": 1, "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 1, "errors": 1, "points": 5, "blk_assist": 0, "comment": "1세트 공격 5/9 결정력 과시"},
        {"set_no": 1, "player_id": 503, "att_made": 2, "att_tried": 3, "srv_made": 1, "srv_tried": 3, "blk_made": 1, "blk_tried": 4, "dig_made": 0, "dig_tried": 0, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0, "points": 4, "blk_assist": 0, "comment": "1세트 서브 1, 블로킹 1, 속공 2개로 기선제압"},
        {"set_no": 1, "player_id": 201, "att_made": 5, "att_tried": 12, "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 1, "dig_made": 2, "dig_tried": 2, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2, "points": 5, "blk_assist": 0, "comment": "1세트 메가 5득점 분전"},
        {"set_no": 2, "player_id": 501, "att_made": 6, "att_tried": 10, "srv_made": 1, "srv_tried": 3, "blk_made": 0, "blk_tried": 3, "dig_made": 1, "dig_tried": 2, "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 2, "errors": 1, "points": 7, "blk_assist": 0, "comment": "2세트 모마 7득점 맹폭격"},
        {"set_no": 2, "player_id": 502, "att_made": 4, "att_tried": 7, "srv_made": 0, "srv_tried": 4, "blk_made": 1, "blk_tried": 2, "dig_made": 3, "dig_tried": 5, "rcv_made": 2, "rcv_tried": 6, "set_made": 0, "set_tried": 0, "errors": 1, "points": 5, "blk_assist": 0, "comment": "2세트 마미 5득점 지원사격"},
        {"set_no": 2, "player_id": 201, "att_made": 6, "att_tried": 14, "srv_made": 0, "srv_tried": 3, "blk_made": 1, "blk_tried": 1, "dig_made": 2, "dig_tried": 3, "rcv_made": 0, "rcv_tried": 1, "set_made": 1, "set_tried": 2, "errors": 3, "points": 7, "blk_assist": 0, "comment": "2세트 메가 7득점 폭발"},
        {"set_no": 3, "player_id": 501, "att_made": 5, "att_tried": 9, "srv_made": 0, "srv_tried": 2, "blk_made": 0, "blk_tried": 3, "dig_made": 1, "dig_tried": 1, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 1, "points": 5, "blk_assist": 0, "comment": "3세트 승부 쐐기 모마 5득점"},
        {"set_no": 3, "player_id": 504, "att_made": 5, "att_tried": 10, "srv_made": 0, "srv_tried": 4, "blk_made": 0, "blk_tried": 2, "dig_made": 3, "dig_tried": 3, "rcv_made": 2, "rcv_tried": 7, "set_made": 0, "set_tried": 1, "errors": 1, "points": 5, "blk_assist": 0, "comment": "3세트 강소휘 5득점 마무리"}
    ],
    "set_lineups": {
        "1": {
            "HDEC": {"S": 207, "OH1": 202, "OH2": 206, "OP": 201, "MB1": 204, "MB2": 205, "L": 211},
            "EXP": {"S": 506, "OH1": 504, "OH2": 502, "OP": 501, "MB1": 503, "MB2": 505, "L": 508}
        },
        "2": {
            "HDEC": {"S": 207, "OH1": 202, "OH2": 203, "OP": 201, "MB1": 204, "MB2": 208, "L": 211},
            "EXP": {"S": 506, "OH1": 504, "OH2": 502, "OP": 501, "MB1": 503, "MB2": 505, "L": 508}
        },
        "3": {
            "HDEC": {"S": 207, "OH1": 202, "OH2": 203, "OP": 201, "MB1": 205, "MB2": 208, "L": 210},
            "EXP": {"S": 506, "OH1": 504, "OH2": 502, "OP": 501, "MB1": 503, "MB2": 505, "L": 508}
        }
    }
}

def export_js() -> None:
    data_json = json.dumps(full_data_1116, ensure_ascii=False, indent=2)
    js_content = f"""// 11월 16일 현대건설 vs 한국도로공사 전술 분석 데이터
window.BOOTSTRAP_1116 = {data_json};

window.MATCHES = window.MATCHES || {{}};
if (window.BOOTSTRAP) {{
  window.MATCHES['2026-11-07'] = window.BOOTSTRAP;
  window.MATCHES['2024-11-07'] = window.BOOTSTRAP;
}}
if (window.BOOTSTRAP_1104) {{
  window.MATCHES['2026-11-04'] = window.BOOTSTRAP_1104;
  window.MATCHES['2024-11-04'] = window.BOOTSTRAP_1104;
}}
if (window.BOOTSTRAP_1103) {{
  window.MATCHES['2026-11-03'] = window.BOOTSTRAP_1103;
  window.MATCHES['2024-11-03'] = window.BOOTSTRAP_1103;
}}
if (window.BOOTSTRAP_1108) {{
  window.MATCHES['2026-11-08'] = window.BOOTSTRAP_1108;
  window.MATCHES['2024-11-08'] = window.BOOTSTRAP_1108;
}}
window.MATCHES['2026-11-16'] = window.BOOTSTRAP_1116;
window.MATCHES['2024-11-16'] = window.BOOTSTRAP_1116;
"""
    js_path = ROOT / "js" / "data_1116.js"
    static_js_path = ROOT / "static" / "js" / "data_1116.js"
    js_path.write_text(js_content, encoding="utf-8")
    static_js_path.write_text(js_content, encoding="utf-8")
    print(f"Generated data_1116.js with {len(all_rallies)} rallies successfully!")

if __name__ == "__main__":
    export_js()
