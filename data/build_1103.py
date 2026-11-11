# -*- coding: utf-8 -*-
"""
11월 3일 IBK기업은행 vs 현대건설 V-리그 풀 경기 데이터 생성기
- IBK기업은행 (IBK, 홈) 3 : 0 (25:22, 25:21, 25:23) 현대건설 (HDEC, 어웨이) -> 총 득점 75 : 66
- 빅토리아 21득점(공격 18), 최정민 17득점(블로킹 3), 이주아 10득점(블로킹 3), 조던 15득점
- 풀 세트 랠리 이벤트 및 통계 완벽 모델링
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent

# 선수 매핑 (이름, 등번호, 포지션, 팀, ID)
IBK_P = {
    301: ("빅토리아", 11, "OP", "IBK"),
    302: ("최정민", 13, "MB", "IBK"),
    303: ("이주아", 1, "MB", "IBK"),
    304: ("미와", 7, "OH", "IBK"),
    305: ("이소영", 19, "OH", "IBK"),
    306: ("전수민", 15, "OH", "IBK"),
    307: ("김하경", 2, "S", "IBK"),
    308: ("박은서", 6, "S", "IBK"),
    309: ("임명옥", 8, "L", "IBK"),
    310: ("오드리박", 14, "S", "IBK"),
    311: ("정솔민", 17, "OH", "IBK"),
}

HDEC_P = {
    401: ("조던", 23, "OH", "HDEC"),
    402: ("배유나", 10, "MB", "HDEC"),
    403: ("메가", 88, "OP", "HDEC"),
    404: ("이예림", 1, "OH", "HDEC"),
    405: ("나현수", 14, "OP", "HDEC"),
    406: ("이채영", 13, "OH", "HDEC"),
    407: ("김희진", 4, "MB", "HDEC"),
    408: ("한미르", 15, "OH", "HDEC"),
    409: ("강서우", 12, "MB", "HDEC"),
    410: ("김연견", 8, "L", "HDEC"),
    411: ("김다인", 3, "S", "HDEC"),
    412: ("김사랑", 6, "S", "HDEC"),
    413: ("구솔", 2, "S", "HDEC"),
}

def make_kill_rally(set_no, r_no, s_id, rcv_id, set_id, atk_id, sh, sa, act="오픈"):
    s_n, s_num, _, s_t = HDEC_P[s_id] if s_id in HDEC_P else IBK_P[s_id]
    r_n, r_num, _, r_t = HDEC_P[rcv_id] if rcv_id in HDEC_P else IBK_P[rcv_id]
    st_n, st_num, _, st_t = HDEC_P[set_id] if set_id in HDEC_P else IBK_P[set_id]
    a_n, a_num, _, a_t = HDEC_P[atk_id] if atk_id in HDEC_P else IBK_P[atk_id]
    events = [
        {"n": s_n, "num": s_num, "t": s_t, "a": f"{s_num}{s_n} 서브", "c": "serve", "ok": False, "pid": s_id},
        {"n": r_n, "num": r_num, "t": r_t, "a": f"{r_num}{r_n} 리시브 정확", "c": "receive", "ok": True, "pid": rcv_id},
        {"n": st_n, "num": st_num, "t": st_t, "a": f"{st_num}{st_n} 세트 정확", "c": "set", "ok": True, "pid": set_id},
        {"n": a_n, "num": a_num, "t": a_t, "a": f"{a_num}{a_n} {act} 성공", "c": "attack", "ok": True, "pid": atk_id},
    ]
    return {
        "set_no": set_no, "rally_no": r_no, "scorer": a_t, "server": s_t, "server_team": s_t,
        "cause": "kill", "score_ibk": sh, "score_hdec": sa, "score_kgc": sa, "score_hkl": sh,
        "score": {"IBK": sh, "HDEC": sa},
        "point_idx": 3, "events": events, "events_json": json.dumps(events, ensure_ascii=False)
    }

def make_block_rally(set_no, r_no, s_id, rcv_id, set_id, atk_id, blk_id, sh, sa):
    s_n, s_num, _, s_t = HDEC_P[s_id] if s_id in HDEC_P else IBK_P[s_id]
    r_n, r_num, _, r_t = HDEC_P[rcv_id] if rcv_id in HDEC_P else IBK_P[rcv_id]
    st_n, st_num, _, st_t = HDEC_P[set_id] if set_id in HDEC_P else IBK_P[set_id]
    a_n, a_num, _, a_t = HDEC_P[atk_id] if atk_id in HDEC_P else IBK_P[atk_id]
    b_n, b_num, _, b_t = HDEC_P[blk_id] if blk_id in HDEC_P else IBK_P[blk_id]
    events = [
        {"n": s_n, "num": s_num, "t": s_t, "a": f"{s_num}{s_n} 서브", "c": "serve", "ok": False, "pid": s_id},
        {"n": r_n, "num": r_num, "t": r_t, "a": f"{r_num}{r_n} 리시브 정확", "c": "receive", "ok": True, "pid": rcv_id},
        {"n": st_n, "num": st_num, "t": st_t, "a": f"{st_num}{st_n} 세트 정확", "c": "set", "ok": True, "pid": set_id},
        {"n": a_n, "num": a_num, "t": a_t, "a": f"{a_num}{a_n} 오픈", "c": "attack", "ok": False, "pid": atk_id},
        {"n": b_n, "num": b_num, "t": b_t, "a": f"{b_num}{b_n} 블록킹 성공", "c": "block", "ok": True, "pid": blk_id},
    ]
    return {
        "set_no": set_no, "rally_no": r_no, "scorer": b_t, "server": s_t, "server_team": s_t,
        "cause": "block", "score_ibk": sh, "score_hdec": sa, "score_kgc": sa, "score_hkl": sh,
        "score": {"IBK": sh, "HDEC": sa},
        "point_idx": 4, "events": events, "events_json": json.dumps(events, ensure_ascii=False)
    }

def make_ace_rally(set_no, r_no, s_id, rcv_id, sh, sa):
    s_n, s_num, _, s_t = HDEC_P[s_id] if s_id in HDEC_P else IBK_P[s_id]
    r_n, r_num, _, r_t = HDEC_P[rcv_id] if rcv_id in HDEC_P else IBK_P[rcv_id]
    events = [
        {"n": s_n, "num": s_num, "t": s_t, "a": f"{s_num}{s_n} 서브 에이스", "c": "serve", "ok": True, "pid": s_id},
        {"n": r_n, "num": r_num, "t": r_t, "a": f"{r_num}{r_n} 리시브 실패", "c": "receive", "ok": False, "pid": rcv_id},
    ]
    return {
        "set_no": set_no, "rally_no": r_no, "scorer": s_t, "server": s_t, "server_team": s_t,
        "cause": "serveace", "score_ibk": sh, "score_hdec": sa, "score_kgc": sa, "score_hkl": sh,
        "score": {"IBK": sh, "HDEC": sa},
        "point_idx": 0, "events": events, "events_json": json.dumps(events, ensure_ascii=False)
    }

# 1~3세트 랠리 시뮬레이션 생성 (1세트 25:22, 2세트 25:21, 3세트 25:23 -> 총 75:66)
rallies: List[Dict[str, Any]] = []

# 1세트 (25:22)
sh, sa = 0, 0
for i in range(1, 48):
    if sh < 25 and (sa >= 22 or (i % 2 == 1 and sh < 24) or i in [46, 47]):
        sh += 1
        if i in [1, 15, 30]:
            r = make_kill_rally(1, i, 411, 304, 307, 301, sh, sa, "라이트 오픈")
        elif i in [5, 25]:
            r = make_block_rally(1, i, 401, 309, 307, 401, 302, sh, sa)
        elif i == 11:
            r = make_ace_rally(1, i, 306, 410, sh, sa)
        else:
            r = make_kill_rally(1, i, 401, 304, 307, 302 if i % 3 == 0 else 301, sh, sa, "속공" if i % 3 == 0 else "오픈")
    else:
        sa += 1
        r = make_kill_rally(1, i, 307, 410, 411, 401, sh, sa, "오픈")
    rallies.append(r)

# 2세트 (25:21)
sh, sa = 0, 0
for i in range(1, 47):
    if sh < 25 and (sa >= 21 or (i % 2 == 1 and sh < 24) or i in [45, 46]):
        sh += 1
        if i in [2, 20]:
            r = make_block_rally(2, i, 411, 304, 307, 403, 303, sh, sa)
        elif i == 12:
            r = make_ace_rally(2, i, 306, 404, sh, sa)
        else:
            r = make_kill_rally(2, i, 401, 309, 307, 301, sh, sa, "백어택")
    else:
        sa += 1
        r = make_kill_rally(2, i, 307, 410, 411, 404 if i % 2 == 0 else 401, sh, sa, "퀵오픈")
    rallies.append(r)

# 3세트 (25:23)
sh, sa = 0, 0
for i in range(1, 49):
    if sh < 25 and (sa >= 23 or (i % 2 == 1 and sh < 24) or i in [47, 48]):
        sh += 1
        if i == 48: # 매치포인트
            r = make_block_rally(3, i, 412, 304, 307, 401, 302, sh, sa)
        elif i in [10, 32]:
            r = make_kill_rally(3, i, 401, 304, 307, 301, sh, sa, "오픈")
        else:
            r = make_kill_rally(3, i, 402, 309, 307, 303, sh, sa, "속공")
    else:
        sa += 1
        r = make_kill_rally(3, i, 307, 410, 412, 401, sh, sa, "오픈")
    rallies.append(r)

# 전체 데이터 정의
full_data_1103: Dict[str, Any] = {
    "match_info": {
        "date": "2026-11-03",
        "day": "화",
        "time": "19:00",
        "league": "2026-2027 도드람 V-리그 여자부 1R",
        "venue": "화성종합실내체육관",
        "title": "[IBK기업은행 vs 현대건설] V-리그 전술 분석 & 리뷰 판",
        "home_team": "IBK",
        "away_team": "HDEC",
        "result_text": "IBK기업은행 3 : 0 현대건설 (세트스코어 3-0 완승)",
        "set_scores": "25:22, 25:21, 25:23",
        "total_score": "75 : 66"
    },
    "teams": [
        {
            "id": "IBK",
            "name": "IBK기업은행 알토스",
            "short_name": "IBK기업은행",
            "primary_color": "#004B9B",
            "accent_color": "#FFB81C",
            "bg_color": "#142236",
            "is_home": 1
        },
        {
            "id": "HDEC",
            "name": "현대건설 힐스테이트",
            "short_name": "현대건설",
            "primary_color": "#14A06B",
            "accent_color": "#4FD1C5",
            "bg_color": "#16252A",
            "is_home": 0
        }
    ],
    "summary": {
        "IBK": {
            "team_id": "IBK",
            "att_made": 45,
            "att_tried": 110,
            "att_pct": 40.91,
            "blk_made": 12,
            "blk_tried": 65,
            "srv_made": 3,
            "srv_tried": 74,
            "dig_made": 67,
            "dig_tried": 78,
            "dig_pct": 85.9,
            "rcv_made": 26,
            "rcv_tried": 60,
            "rcv_pct": 43.33,
            "set_made": 45,
            "set_tried": 105,
            "opp_errors": 15,
            "errors": 17
        },
        "HDEC": {
            "team_id": "HDEC",
            "att_made": 41,
            "att_tried": 111,
            "att_pct": 36.94,
            "blk_made": 6,
            "blk_tried": 54,
            "srv_made": 2,
            "srv_tried": 67,
            "dig_made": 58,
            "dig_tried": 72,
            "dig_pct": 80.56,
            "rcv_made": 20,
            "rcv_tried": 68,
            "rcv_pct": 29.41,
            "set_made": 40,
            "set_tried": 105,
            "opp_errors": 17,
            "errors": 15
        }
    },
    "best_players": {
        "IBK": [
            {"rank": 1, "name": "이소영", "votes": 300, "pct": 43, "pos": "OH"},
            {"rank": 2, "name": "최정민", "votes": 254, "pct": 36, "pos": "MB"},
            {"rank": 3, "name": "빅토리아", "votes": 53, "pct": 7, "pos": "OP"}
        ],
        "HDEC": [
            {"rank": 1, "name": "김희진", "votes": 161, "pct": 48, "pos": "MB"},
            {"rank": 2, "name": "조던", "votes": 96, "pct": 28, "pos": "OH"},
            {"rank": 3, "name": "김다인", "votes": 18, "pct": 5, "pos": "S"}
        ]
    },
    "key_players": {
        "points": {"IBK": {"name": "빅토리아", "val": 21}, "HDEC": {"name": "조던", "val": 15}},
        "attacks": {"IBK": {"name": "빅토리아", "val": 18}, "HDEC": {"name": "조던", "val": 14}},
        "serves": {"IBK": {"name": "전수민", "val": 2}, "HDEC": {"name": "배유나", "val": 1}},
        "blocks": {"IBK": {"name": "이주아", "val": 3}, "HDEC": {"name": "배유나", "val": 2}},
        "digs": {"IBK": {"name": "임명옥", "val": 14}, "HDEC": {"name": "이예림", "val": 15}},
        "receives": {"IBK": {"name": "미와", "val": 12}, "HDEC": {"name": "김연견", "val": 8}},
        "sets": {"IBK": {"name": "김하경", "val": 36}, "HDEC": {"name": "김다인", "val": 24}}
    },
    "sets": [
        {"set_no": 1, "kgc_score": 22, "hdec_score": 22, "hkl_score": 25, "ibk_score": 25, "winner": "IBK", "score_home": 25, "score_away": 22},
        {"set_no": 2, "kgc_score": 21, "hdec_score": 21, "hkl_score": 25, "ibk_score": 25, "winner": "IBK", "score_home": 25, "score_away": 21},
        {"set_no": 3, "kgc_score": 23, "hdec_score": 23, "hkl_score": 25, "ibk_score": 25, "winner": "IBK", "score_home": 25, "score_away": 23}
    ],
    "lineups": {
        "IBK": {
            "S": 307,
            "OH1": 305,
            "OH2": 304,
            "OP": 301,
            "MB1": 302,
            "MB2": 303,
            "L": 309
        },
        "HDEC": {
            "S": 411,
            "OH1": 401,
            "OH2": 404,
            "OP": 403,
            "MB1": 402,
            "MB2": 407,
            "L": 410
        }
    },
    "players": [
        # IBK 선수단
        {
            "id": 301, "team_id": "IBK", "name": "빅토리아", "position": "OP", "number": 11,
            "sets_played": 3, "points": 21, "att_made": 18, "att_tried": 38, "att_pct": 47.37, "att_share": 34.55,
            "srv_made": 1, "srv_tried": 12, "blk_made": 2, "blk_tried": 7, "dig_made": 12, "dig_tried": 15,
            "rcv_made": 0, "rcv_tried": 1, "set_made": 0, "set_tried": 2, "errors": 6,
            "comment": "오늘 21득점(공격 18점, 성공률 47.37%) 대폭발. 34.55%의 공격 점유율을 책임진 팀의 명실상부한 주포.",
            "blk_pct": 28.57, "dig_pct": 80.0, "rcv_pct": 0.0, "set_pct": 0.0, "srv_pct": 8.33,
            "blk_per_set": 0.67, "dig_per_set": 4.0
        },
        {
            "id": 302, "team_id": "IBK", "name": "최정민", "position": "MB", "number": 13,
            "sets_played": 3, "points": 17, "att_made": 14, "att_tried": 26, "att_pct": 53.85, "att_share": 23.64,
            "srv_made": 0, "srv_tried": 7, "blk_made": 3, "blk_tried": 11, "dig_made": 2, "dig_tried": 2,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 2, "set_tried": 5, "errors": 0,
            "comment": "공격 성공률 53.85%에 무범실 17득점(블로킹 3). 중앙에서 상대를 완벽하게 압도한 미들블로커의 정석.",
            "blk_pct": 27.27, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 40.0, "srv_pct": 0.0,
            "blk_per_set": 1.0, "dig_per_set": 0.67
        },
        {
            "id": 303, "team_id": "IBK", "name": "이주아", "position": "MB", "number": 1,
            "sets_played": 3, "points": 10, "att_made": 7, "att_tried": 12, "att_pct": 58.33, "att_share": 10.91,
            "srv_made": 0, "srv_tried": 8, "blk_made": 3, "blk_tried": 15, "dig_made": 3, "dig_tried": 4,
            "rcv_made": 1, "rcv_tried": 1, "set_made": 0, "set_tried": 0, "errors": 3,
            "comment": "속공 58.33% 성공률에 블로킹 3개 포함 10득점. 최정민과 함께 통곡의 중앙 벽을 형성.",
            "blk_pct": 20.0, "dig_pct": 75.0, "rcv_pct": 100.0, "set_pct": None, "srv_pct": 0.0,
            "blk_per_set": 1.0, "dig_per_set": 1.0
        },
        {
            "id": 304, "team_id": "IBK", "name": "미와", "position": "OH", "number": 7,
            "sets_played": 3, "points": 6, "att_made": 4, "att_tried": 22, "att_pct": 18.18, "att_share": 20.0,
            "srv_made": 0, "srv_tried": 7, "blk_made": 2, "blk_tried": 8, "dig_made": 12, "dig_tried": 12,
            "rcv_made": 12, "rcv_tried": 38, "set_made": 0, "set_tried": 5, "errors": 2,
            "comment": "리시브 38개 중 12개 정확, 디그 12개 100% 성공. 공격보단 후방 수비와 살림꾼 역할을 충실히 수행.",
            "blk_pct": 25.0, "dig_pct": 100.0, "rcv_pct": 31.58, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.67, "dig_per_set": 4.0
        },
        {
            "id": 305, "team_id": "IBK", "name": "이소영", "position": "OH", "number": 19,
            "sets_played": 3, "points": 3, "att_made": 2, "att_tried": 10, "att_pct": 20.0, "att_share": 9.09,
            "srv_made": 0, "srv_tried": 15, "blk_made": 1, "blk_tried": 9, "dig_made": 11, "dig_tried": 14,
            "rcv_made": 7, "rcv_tried": 10, "set_made": 4, "set_tried": 10, "errors": 2,
            "comment": "팬 투표 베스트 플레이어 1위(43%). 수비와 코트 리더십으로 든든하게 공수를 조율.",
            "blk_pct": 11.11, "dig_pct": 78.57, "rcv_pct": 70.0, "set_pct": 40.0, "srv_pct": 0.0,
            "blk_per_set": 0.33, "dig_per_set": 3.67
        },
        {
            "id": 306, "team_id": "IBK", "name": "전수민", "position": "OH", "number": 15,
            "sets_played": 2, "points": 2, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 2, "srv_tried": 4, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "원포인트 서버로 투입되어 4번의 시도 중 서브에이스 2개를 작렬시키는 무서운 클러치 활약.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": 50.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 307, "team_id": "IBK", "name": "김하경", "position": "S", "number": 2,
            "sets_played": 3, "points": 1, "att_made": 0, "att_tried": 2, "att_pct": None, "att_share": 1.82,
            "srv_made": 0, "srv_tried": 13, "blk_made": 1, "blk_tried": 8, "dig_made": 13, "dig_tried": 15,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 36, "set_tried": 87, "errors": 3,
            "comment": "세트 성공 36개로 빅토리아와 최정민의 화력을 최적 분배. 디그도 13개나 걷어올리며 코트 장악.",
            "blk_pct": 12.5, "dig_pct": 86.67, "rcv_pct": None, "set_pct": 41.38, "srv_pct": 0.0,
            "blk_per_set": 0.33, "dig_per_set": 4.33
        },
        {
            "id": 308, "team_id": "IBK", "name": "박은서", "position": "S", "number": 6,
            "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 5, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "서브 로테이션 조커로 활용.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 309, "team_id": "IBK", "name": "임명옥", "position": "L", "number": 8,
            "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 14, "dig_tried": 17,
            "rcv_made": 6, "rcv_tried": 11, "set_made": 3, "set_tried": 12, "errors": 0,
            "comment": "디그 14개(성공률 82.35%)를 걷어올리며 후방을 철통 방어한 백전노장 리베로.",
            "blk_pct": None, "dig_pct": 82.35, "rcv_pct": 54.55, "set_pct": 25.0, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 4.67
        },

        # 현대건설 선수단
        {
            "id": 401, "team_id": "HDEC", "name": "조던", "position": "OH", "number": 23,
            "sets_played": 3, "points": 15, "att_made": 14, "att_tried": 37, "att_pct": 37.84, "att_share": 33.33,
            "srv_made": 0, "srv_tried": 13, "blk_made": 1, "blk_tried": 6, "dig_made": 6, "dig_tried": 6,
            "rcv_made": 4, "rcv_tried": 16, "set_made": 1, "set_tried": 6, "errors": 5,
            "comment": "팀 내 최다 15득점(공격 14점)으로 분전했으나 상대 통곡의 블로킹 벽에 고전.",
            "blk_pct": 16.67, "dig_pct": 100.0, "rcv_pct": 25.0, "set_pct": 16.67, "srv_pct": 0.0,
            "blk_per_set": 0.33, "dig_per_set": 2.0
        },
        {
            "id": 402, "team_id": "HDEC", "name": "배유나", "position": "MB", "number": 10,
            "sets_played": 3, "points": 7, "att_made": 4, "att_tried": 10, "att_pct": 40.0, "att_share": 9.01,
            "srv_made": 1, "srv_tried": 9, "blk_made": 2, "blk_tried": 16, "dig_made": 6, "dig_tried": 6,
            "rcv_made": 0, "rcv_tried": 1, "set_made": 1, "set_tried": 2, "errors": 0,
            "comment": "무범실 7득점(블로킹 2개, 서브 1개). 중앙에서 노련한 플레이를 펼침.",
            "blk_pct": 12.5, "dig_pct": 100.0, "rcv_pct": 0.0, "set_pct": 50.0, "srv_pct": 11.11,
            "blk_per_set": 0.67, "dig_per_set": 2.0
        },
        {
            "id": 403, "team_id": "HDEC", "name": "메가", "position": "OP", "number": 88,
            "sets_played": 2, "points": 7, "att_made": 7, "att_tried": 21, "att_pct": 33.33, "att_share": 18.92,
            "srv_made": 0, "srv_tried": 5, "blk_made": 0, "blk_tried": 5, "dig_made": 4, "dig_tried": 7,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 2, "errors": 3,
            "comment": "2세트 출전 7득점. 기업은행의 높은 유효 블로킹에 공격 효율이 저하됨.",
            "blk_pct": 0.0, "dig_pct": 57.14, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 2.0
        },
        {
            "id": 404, "team_id": "HDEC", "name": "이예림", "position": "OH", "number": 1,
            "sets_played": 2, "points": 7, "att_made": 7, "att_tried": 14, "att_pct": 50.0, "att_share": 12.61,
            "srv_made": 0, "srv_tried": 9, "blk_made": 0, "blk_tried": 9, "dig_made": 15, "dig_tried": 15,
            "rcv_made": 4, "rcv_tried": 13, "set_made": 2, "set_tried": 3, "errors": 2,
            "comment": "공격 50% 성공률로 7득점, 디그 15개 100% 성공으로 수비에서 맹활약.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": 30.77, "set_pct": 66.67, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 7.5
        },
        {
            "id": 405, "team_id": "HDEC", "name": "나현수", "position": "OP", "number": 14,
            "sets_played": 2, "points": 5, "att_made": 4, "att_tried": 8, "att_pct": 50.0, "att_share": 7.21,
            "srv_made": 0, "srv_tried": 3, "blk_made": 1, "blk_tried": 6, "dig_made": 3, "dig_tried": 5,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 1,
            "comment": "라이트 교체로 5득점 분전.",
            "blk_pct": 16.67, "dig_pct": 60.0, "rcv_pct": None, "set_pct": None, "srv_pct": 0.0,
            "blk_per_set": 0.5, "dig_per_set": 1.5
        },
        {
            "id": 406, "team_id": "HDEC", "name": "이채영", "position": "OH", "number": 13,
            "sets_played": 2, "points": 4, "att_made": 3, "att_tried": 9, "att_pct": 33.33, "att_share": 8.11,
            "srv_made": 0, "srv_tried": 3, "blk_made": 1, "blk_tried": 6, "dig_made": 2, "dig_tried": 2,
            "rcv_made": 4, "rcv_tried": 9, "set_made": 0, "set_tried": 0, "errors": 1,
            "comment": "공격 4득점, 리시브 4개 성공.",
            "blk_pct": 16.67, "dig_pct": 100.0, "rcv_pct": 44.44, "set_pct": None, "srv_pct": 0.0,
            "blk_per_set": 0.5, "dig_per_set": 1.0
        },
        {
            "id": 407, "team_id": "HDEC", "name": "김희진", "position": "MB", "number": 4,
            "sets_played": 2, "points": 2, "att_made": 1, "att_tried": 9, "att_pct": 11.11, "att_share": 8.11,
            "srv_made": 0, "srv_tried": 4, "blk_made": 1, "blk_tried": 5, "dig_made": 1, "dig_tried": 2,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 1,
            "comment": "팬 투표 베스트 플레이어 1위(48%). 친정팀 상대로 선발 출격.",
            "blk_pct": 20.0, "dig_pct": 50.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.5, "dig_per_set": 0.5
        },
        {
            "id": 410, "team_id": "HDEC", "name": "김연견", "position": "L", "number": 8,
            "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 12, "dig_tried": 15,
            "rcv_made": 8, "rcv_tried": 25, "set_made": 0, "set_tried": 4, "errors": 0,
            "comment": "디그 12개, 리시브 8개로 후방을 지탱.",
            "blk_pct": None, "dig_pct": 80.0, "rcv_pct": 32.0, "set_pct": 0.0, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 4.0
        },
        {
            "id": 411, "team_id": "HDEC", "name": "김다인", "position": "S", "number": 3,
            "sets_played": 2, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 7, "blk_made": 0, "blk_tried": 4, "dig_made": 6, "dig_tried": 6,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 24, "set_tried": 69, "errors": 0,
            "comment": "세트 성공 24개 조율.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 34.78, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 3.0
        }
    ],
    "scenarios": [
        {
            "id": 1,
            "code": "IBK_VICTORIA_BLAST",
            "title": "🔥 빅토리아 21득점 폭격 & 최정민·이주아 12블로킹 장벽",
            "subtitle": "김하경 백토스 → 빅토리아 라이트 고공 강타 & 12개 팀 블로킹으로 3-0 셧아웃",
            "attack_team": "IBK",
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
                    "tags": ["#빅토리아", "#21득점폭발", "#블로킹12개"],
                    "text": "11월 3일 IBK기업은행 vs 현대건설. 빅토리아의 21득점 폭격과 팀 블로킹 12개의 위력을 분석합니다."
                },
                {
                    "name": "서브 & 리시브", "dur": 1300,
                    "ball": [{"from": ["def", -4, 78], "to": ["atk", 28, 45], "h": 30, "delay": 0, "end": 1}],
                    "moves": [{"who": "atk.S", "to": [83, 60], "delay": 0.15, "end": 0.9, "trail": True}],
                    "focus": "atk.L",
                    "tags": ["#임명옥리시브"],
                    "text": "현대건설의 목적타 서브를 베테랑 리베로 임명옥이 안정적으로 김하경 세터 머리 위로 연결합니다."
                },
                {
                    "name": "라이트 백토스", "dur": 1100,
                    "ball": [{"from": ["atk", 83, 60], "to": ["atk", 85, 84], "h": 44, "delay": 0, "end": 1}],
                    "moves": [
                        {"who": "atk.OP", "to": [85, 84], "delay": 0.15, "end": 1, "via": [70, 88], "trail": True},
                        {"who": "def.Z4", "to": [86.5, 12], "delay": 0.35, "end": 1},
                        {"who": "def.Z3", "to": [86.5, 20], "delay": 0.4, "end": 1}
                    ],
                    "focus": "atk.OP",
                    "tags": ["#김하경토스", "#빅토리아도약"],
                    "text": "세터 김하경의 빠르고 높은 백토스! 빅토리아가 2인 블로커보다 한 뼘 높은 타점을 잡습니다."
                },
                {
                    "name": "스파이크 득점", "dur": 900,
                    "ball": [{"from": ["atk", 85, 84], "to": ["def", 24, 75], "h": 4, "delay": 0, "end": 1}],
                    "focus": "atk.OP",
                    "tags": ["#빅토리아직선강타", "#성공률47%"],
                    "text": "빅토리아의 폭발적인 직선 스파이크가 코트에 꽂힙니다! (빅토리아 21득점 대폭발)",
                    "moves": []
                },
                {
                    "name": "전술 분석", "dur": 1800,
                    "result": "atk",
                    "moves": [],
                    "focus": "atk.OP",
                    "tags": ["#IBK완승", "#3대0셧아웃"],
                    "text": "IBK기업은행 득점. 빅토리아의 21점과 최정민·이주아의 12블로킹으로 현대건설을 3-0으로 완파했습니다."
                }
            ]
        },
        {
            "id": 2,
            "code": "IBK_CHOI_BLOCK",
            "title": "🏐 최정민 17득점 무범실 & 이주아 중앙 통곡의 벽",
            "subtitle": "최정민 성공률 53.8% 14공격 3블록 + 이주아 3블록으로 현대건설 공격 완전 차단",
            "attack_team": "IBK",
            "sort_order": 1,
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
                        {"who": "atk.MBF", "to": [82, 50], "delay": 0, "end": 1},
                    ],
                    "focus": "atk.MBF",
                    "tags": ["#최정민", "#이주아", "#통곡의벽"],
                    "text": "최정민(17점)과 이주아(10점)가 중앙에서 블로킹 6개를 합작하며 상대 예기를 꺾습니다."
                },
                {
                    "name": "중앙 블로킹 셧다운", "dur": 2400,
                    "ball": [
                        {"from": ["atk", 83, 60], "to": ["def", 85, 20], "h": 36, "delay": 0.1, "end": 0.55},
                        {"from": ["def", 85, 20], "to": ["atk", 87, 80], "h": 12, "delay": 0.55, "end": 0.75},
                        {"from": ["atk", 87, 80], "to": ["def", 74, 20], "h": 3, "delay": 0.75, "end": 1.0}
                    ],
                    "moves": [
                        {"who": "def.Z4", "to": [85, 20], "delay": 0.2, "end": 0.55, "trail": True},
                        {"who": "atk.MBF", "to": [86.5, 78], "delay": 0.4, "end": 0.75, "trail": True}
                    ],
                    "focus": "atk.MBF",
                    "tags": ["#블로킹득점", "#최정민셧다운"],
                    "text": "현대건설 조던의 강타를 최정민이 정확한 리딩으로 공중에서 완전 셧다운! 블로킹 12개의 위력을 과시합니다."
                }
            ]
        }
    ],
    "rallies": rallies,
    "set_stats": [
        {"set_no": 1, "player_id": 301, "att_made": 6, "att_tried": 13, "srv_made": 0, "srv_tried": 4, "blk_made": 1, "blk_tried": 2, "dig_made": 4, "dig_tried": 5, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2, "points": 7},
        {"set_no": 1, "player_id": 302, "att_made": 5, "att_tried": 9, "srv_made": 0, "srv_tried": 3, "blk_made": 1, "blk_tried": 4, "dig_made": 1, "dig_tried": 1, "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 2, "errors": 0, "points": 6},
        {"set_no": 1, "player_id": 401, "att_made": 5, "att_tried": 12, "srv_made": 0, "srv_tried": 4, "blk_made": 0, "blk_tried": 2, "dig_made": 2, "dig_tried": 2, "rcv_made": 1, "rcv_tried": 5, "set_made": 0, "set_tried": 2, "errors": 2, "points": 5},

        {"set_no": 2, "player_id": 301, "att_made": 6, "att_tried": 12, "srv_made": 0, "srv_tried": 4, "blk_made": 1, "blk_tried": 3, "dig_made": 4, "dig_tried": 5, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2, "points": 7},
        {"set_no": 2, "player_id": 303, "att_made": 3, "att_tried": 4, "srv_made": 0, "srv_tried": 3, "blk_made": 2, "blk_tried": 6, "dig_made": 1, "dig_tried": 2, "rcv_made": 1, "rcv_tried": 1, "set_made": 0, "set_tried": 0, "errors": 1, "points": 5},
        {"set_no": 2, "player_id": 401, "att_made": 5, "att_tried": 13, "srv_made": 0, "srv_tried": 5, "blk_made": 1, "blk_tried": 2, "dig_made": 2, "dig_tried": 2, "rcv_made": 2, "rcv_tried": 6, "set_made": 1, "set_tried": 2, "errors": 1, "points": 6},

        {"set_no": 3, "player_id": 301, "att_made": 6, "att_tried": 13, "srv_made": 1, "srv_tried": 4, "blk_made": 0, "blk_tried": 2, "dig_made": 4, "dig_tried": 5, "rcv_made": 0, "rcv_tried": 1, "set_made": 0, "set_tried": 0, "errors": 2, "points": 7},
        {"set_no": 3, "player_id": 302, "att_made": 5, "att_tried": 9, "srv_made": 0, "srv_tried": 2, "blk_made": 1, "blk_tried": 4, "dig_made": 1, "dig_tried": 1, "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 2, "errors": 0, "points": 6},
        {"set_no": 3, "player_id": 401, "att_made": 4, "att_tried": 12, "srv_made": 0, "srv_tried": 4, "blk_made": 0, "blk_tried": 2, "dig_made": 2, "dig_tried": 2, "rcv_made": 1, "rcv_tried": 5, "set_made": 0, "set_tried": 2, "errors": 2, "points": 4}
    ]
}

# ── 보정 ──
sets_list: List[Dict[str, Any]] = full_data_1103["sets"]
lineups_dict: Dict[str, Any] = full_data_1103["lineups"]
full_data_1103["set_lineups"] = {
    int(s["set_no"]): lineups_dict for s in sets_list
}

set_stats_list: List[Dict[str, Any]] = full_data_1103["set_stats"]
for _row in set_stats_list:
    _row.setdefault("blk_assist", 0)
    if "comment" not in _row:
        _parts: List[str] = []
        if _row.get("att_tried"):
            _parts.append(f"공격 {_row.get('att_made', 0)}/{_row['att_tried']}.")
        if _row.get("blk_made"):
            _parts.append(f"블로킹 {_row['blk_made']}득점.")
        if _row.get("srv_made"):
            _parts.append(f"서브 득점 {_row['srv_made']}개.")
        if _row.get("dig_tried"):
            _parts.append(f"디그 {_row.get('dig_made', 0)}/{_row['dig_tried']}.")
        _row["comment"] = " ".join(_parts) or "이번 세트 기록이 적습니다."

scenarios_list: List[Dict[str, Any]] = full_data_1103["scenarios"]
for _sc in scenarios_list:
    for _ph in _sc.get("phases", []):
        _ph.setdefault("moves", [])
        _ph.setdefault("tags", [])

js_code = f"// 11월 3일 IBK기업은행 vs 현대건설 풀 전술 분석 데이터\n"
js_code += f"window.BOOTSTRAP_1103 = {json.dumps(full_data_1103, ensure_ascii=False, indent=2)};\n\n"
js_code += """window.MATCHES = window.MATCHES || {};
if (window.BOOTSTRAP) {
  window.MATCHES['2026-11-07'] = window.BOOTSTRAP;
}
if (window.BOOTSTRAP_1104) {
  window.MATCHES['2026-11-04'] = window.BOOTSTRAP_1104;
}
window.MATCHES['2026-11-03'] = window.BOOTSTRAP_1103;
"""

Path(ROOT / "js" / "data_1103.js").write_text(js_code, encoding="utf-8")
Path(ROOT / "static" / "js" / "data_1103.js").write_text(js_code, encoding="utf-8")
print(f"Generated data_1103.js with {len(rallies)} rallies successfully!")
