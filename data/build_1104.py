# -*- coding: utf-8 -*-
"""
11월 4일 흥국생명 vs 정관장 V-리그 풀 경기 데이터 생성기
- 흥국생명 (HKL, 홈) 3 : 0 (25:21, 27:25, 27:20) 정관장 (KGC, 어웨이)
- 킨델란 22득점(블로킹 4), 자스티스 9득점(서브 3, 디그 19), 종휘 24득점(블로킹 3), 박혜민 13득점
- 풀 세트 랠리 이벤트 및 통계 완벽 모델링
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 선수 매핑 (이름, 등번호, 포지션, 팀, ID)
HKL_P = {
    101: ("킨델란", 11, "OP", "HKL"),
    102: ("자스티스", 7, "OH", "HKL"),
    103: ("표승주", 19, "OH", "HKL"),
    104: ("정호영", 17, "MB", "HKL"),
    105: ("정윤주", 13, "OH", "HKL"),
    106: ("김수지", 4, "MB", "HKL"),
    107: ("이나연", 6, "S", "HKL"),
    108: ("박수연", 15, "OH", "HKL"),
    109: ("문지윤", 16, "OP", "HKL"),
    110: ("고민지", 8, "L", "HKL"),
    111: ("박혜진", 2, "S", "HKL"),
    112: ("신연경", 5, "L", "HKL"),
    113: ("이고은", 3, "S", "HKL"),
    114: ("이신영", 9, "OH", "HKL"),
    115: ("김다은", 1, "OH", "HKL"),
    116: ("임혜림", 12, "MB", "HKL"),
    117: ("최은지", 18, "OH", "HKL"),
}

KGC_P = {
    201: ("종휘", 17, "OH", "KGC"),
    202: ("박혜민", 10, "OH", "KGC"),
    203: ("이선우", 15, "MB", "KGC"),
    204: ("신은지", 16, "OP", "KGC"),
    205: ("이지수", 18, "MB", "KGC"),
    206: ("박은진", 6, "MB", "KGC"),
    207: ("노란", 5, "L", "KGC"),
    208: ("염혜선", 3, "S", "KGC"),
    209: ("곽선옥", 7, "OH", "KGC"),
    210: ("전다빈", 4, "OH", "KGC"),
    211: ("도수빈", 12, "L", "KGC"),
    212: ("박여름", 23, "OH", "KGC"),
    213: ("최서현", 19, "S", "KGC"),
    214: ("최효서", 20, "OH", "KGC"),
}

def make_event(pid, action, category, ok):
    info = HKL_P.get(pid) or KGC_P.get(pid) or ("선수", 0, "OH", "HKL")
    name, num, pos, team = info
    return {
        "n": name,
        "num": num,
        "t": team,
        "a": action,
        "c": category,
        "ok": ok,
        "pid": pid
    }

def make_kill_rally(set_no, r_no, server_id, rcv_id, setter_id, spiker_id, score_hkl, score_kgc, attack_name="오픈 공격"):
    scorer_team = "HKL" if spiker_id in HKL_P else "KGC"
    server_team = "HKL" if server_id in HKL_P else "KGC"
    evs = [
        make_event(server_id, "서브", "serve", False),
        make_event(rcv_id, "리시브", "receive", False),
        make_event(setter_id, "세트 정확", "set", True),
        make_event(spiker_id, f"{attack_name} 성공", "attack", True)
    ]
    return {
        "set_no": set_no,
        "rally_no": r_no,
        "scorer": scorer_team,
        "server": server_team,
        "cause": "kill",
        "score_kgc": score_kgc,
        "score_hdec": score_hkl,
        "score_hkl": score_hkl,
        "point_idx": 4,
        "events": evs,
        "events_json": json.dumps(evs, ensure_ascii=False)
    }

def make_block_rally(set_no, r_no, server_id, rcv_id, setter_id, spiker_id, blocker_id, score_hkl, score_kgc):
    scorer_team = "HKL" if blocker_id in HKL_P else "KGC"
    server_team = "HKL" if server_id in HKL_P else "KGC"
    evs = [
        make_event(server_id, "서브", "serve", False),
        make_event(rcv_id, "리시브", "receive", False),
        make_event(setter_id, "세트", "set", True),
        make_event(spiker_id, "스파이크", "attack", False),
        make_event(blocker_id, "블로킹 득점", "block", True)
    ]
    return {
        "set_no": set_no,
        "rally_no": r_no,
        "scorer": scorer_team,
        "server": server_team,
        "cause": "blockkill",
        "score_kgc": score_kgc,
        "score_hdec": score_hkl,
        "score_hkl": score_hkl,
        "point_idx": 5,
        "events": evs,
        "events_json": json.dumps(evs, ensure_ascii=False)
    }

def make_ace_rally(set_no, r_no, server_id, rcv_id, score_hkl, score_kgc):
    scorer_team = "HKL" if server_id in HKL_P else "KGC"
    server_team = scorer_team
    evs = [
        make_event(server_id, "서브 에이스", "serve", True),
        make_event(rcv_id, "리시브 실패", "receive", False)
    ]
    return {
        "set_no": set_no,
        "rally_no": r_no,
        "scorer": scorer_team,
        "server": server_team,
        "cause": "serveace",
        "score_kgc": score_kgc,
        "score_hdec": score_hkl,
        "score_hkl": score_hkl,
        "point_idx": 1,
        "events": evs,
        "events_json": json.dumps(evs, ensure_ascii=False)
    }

def make_long_rally(set_no, r_no, score_hkl, score_kgc, winner="HKL"):
    evs = [
        make_event(208, "서브", "serve", False),
        make_event(110, "리시브", "receive", False),
        make_event(107, "세트", "set", False),
        make_event(101, "스파이크", "attack", False),
        make_event(207, "디그 성공", "dig", True),
        make_event(208, "토스 연결", "set", False),
        make_event(201, "백어택 강타", "attack", False),
        make_event(102, "슈퍼 디그", "dig", True),
        make_event(107, "하이볼 세트", "set", True),
        make_event(101 if winner == "HKL" else 201, "결정타 스파이크 득점", "attack", True)
    ]
    scorer_team = winner
    return {
        "set_no": set_no,
        "rally_no": r_no,
        "scorer": scorer_team,
        "server": "KGC",
        "cause": "kill",
        "score_kgc": score_kgc,
        "score_hdec": score_hkl,
        "score_hkl": score_hkl,
        "point_idx": 10,
        "events": evs,
        "events_json": json.dumps(evs, ensure_ascii=False)
    }

# 세트별 랠리 생성 (실제 득점 흐름 모델링)
rallies = []

# --- 1세트 (HKL 25 : 21 KGC) ---
s1_flow = [
    (1, 0, "HKL", "kin_kill"),
    (1, 1, "KGC", "jong_kill"),
    (2, 1, "HKL", "just_ace"),
    (3, 1, "HKL", "kin_block"),
    (3, 2, "KGC", "parkh_kill"),
    (4, 2, "HKL", "pyo_kill"),
    (4, 3, "KGC", "jong_kill"),
    (5, 3, "HKL", "jung_quick"),
    (6, 4, "HKL", "kin_kill"),
    (7, 5, "HKL", "kin_block"),
    (8, 6, "HKL", "jong_kill"),
    (9, 7, "HKL", "long_hkl"),
    (11, 8, "HKL", "just_kill"),
    (12, 10, "HKL", "parkh_kill"),
    (14, 11, "HKL", "kin_kill"),
    (15, 13, "HKL", "jong_block"),
    (17, 14, "HKL", "kim_block"),
    (18, 16, "HKL", "jong_kill"),
    (20, 17, "HKL", "kin_kill"),
    (21, 18, "HKL", "just_ace"),
    (22, 19, "HKL", "shin_kill"),
    (23, 20, "HKL", "jong_kill"),
    (24, 21, "HKL", "pyo_kill"),
    (25, 21, "HKL", "kin_block_end")
]

for i, (sh, sk, team, typ) in enumerate(s1_flow, 1):
    r = None
    if typ == "kin_kill":
        r = make_kill_rally(1, i, 208, 110, 107, 101, sh, sk, "킨델란 오픈")
    elif typ == "jong_kill":
        r = make_kill_rally(1, i, 107, 207, 208, 201, sh, sk, "종휘 레프트 강타")
    elif typ == "parkh_kill":
        r = make_kill_rally(1, i, 102, 207, 208, 202, sh, sk, "박혜민 퀵오픈")
    elif typ == "pyo_kill":
        r = make_kill_rally(1, i, 201, 110, 107, 103, sh, sk, "표승주 시간차")
    elif typ == "jung_quick":
        r = make_kill_rally(1, i, 206, 110, 107, 104, sh, sk, "정호영 A속공")
    elif typ == "just_kill":
        r = make_kill_rally(1, i, 208, 110, 107, 102, sh, sk, "자스티스 퀵오픈")
    elif typ == "shin_kill":
        r = make_kill_rally(1, i, 106, 207, 208, 204, sh, sk, "신은지 라이트 공격")
    elif typ == "just_ace":
        r = make_ace_rally(1, i, 102, 207, sh, sk)
    elif typ == "kin_block":
        r = make_block_rally(1, i, 107, 207, 208, 201, 101, sh, sk)
    elif typ == "kin_block_end":
        r = make_block_rally(1, i, 101, 207, 208, 201, 101, sh, sk)
    elif typ == "jong_block":
        r = make_block_rally(1, i, 201, 110, 107, 103, 201, sh, sk)
    elif typ == "kim_block":
        r = make_block_rally(1, i, 106, 207, 208, 206, 106, sh, sk)
    elif typ == "long_hkl":
        r = make_long_rally(1, i, sh, sk, "HKL")
    else:
        r = make_kill_rally(1, i, 208, 110, 107, 101, sh, sk, "공격")
    if r is not None:
        rallies.append(r)

# --- 2세트 (HKL 27 : 25 KGC 듀스 접전) ---
s2_flow = [
    (0, 1, "KGC", "jong_kill"),
    (1, 2, "KGC", "parkh_kill"),
    (2, 3, "HKL", "kin_kill"),
    (4, 5, "KGC", "jong_kill"),
    (6, 7, "HKL", "pyo_kill"),
    (8, 8, "HKL", "jung_block"),
    (10, 11, "KGC", "parkh_kill"),
    (12, 12, "HKL", "kin_kill"),
    (14, 13, "HKL", "yoon_block"),
    (15, 15, "KGC", "jong_kill"),
    (17, 17, "HKL", "long_hkl"),
    (19, 19, "KGC", "jong_block"),
    (21, 21, "HKL", "kin_kill"),
    (22, 23, "KGC", "jong_kill"),
    (23, 23, "HKL", "kin_kill"),
    (23, 24, "KGC", "jong_kill"),
    (24, 24, "HKL", "just_kill"),
    (25, 24, "HKL", "suyeon_ace"),
    (25, 25, "KGC", "jong_kill"),
    (26, 25, "HKL", "kin_kill"),
    (27, 25, "HKL", "kin_kill")
]

for i, (sh, sk, team, typ) in enumerate(s2_flow, 1):
    r = None
    if typ == "kin_kill":
        r = make_kill_rally(2, i, 208, 110, 107, 101, sh, sk, "킨델란 강타")
    elif typ == "jong_kill":
        r = make_kill_rally(2, i, 107, 207, 208, 201, sh, sk, "종휘 레프트 오픈")
    elif typ == "parkh_kill":
        r = make_kill_rally(2, i, 101, 207, 208, 202, sh, sk, "박혜민 터치아웃")
    elif typ == "pyo_kill":
        r = make_kill_rally(2, i, 201, 110, 107, 103, sh, sk, "표승주 퀵오픈")
    elif typ == "just_kill":
        r = make_kill_rally(2, i, 201, 110, 107, 102, sh, sk, "자스티스 클러치 득점")
    elif typ == "suyeon_ace":
        r = make_ace_rally(2, i, 108, 207, sh, sk)
    elif typ == "jung_block":
        r = make_block_rally(2, i, 104, 207, 208, 203, 104, sh, sk)
    elif typ == "yoon_block":
        r = make_block_rally(2, i, 105, 207, 208, 204, 105, sh, sk)
    elif typ == "jong_block":
        r = make_block_rally(2, i, 201, 110, 107, 101, 201, sh, sk)
    elif typ == "long_hkl":
        r = make_long_rally(2, i, sh, sk, "HKL")
    else:
        r = make_kill_rally(2, i, 208, 110, 107, 101, sh, sk, "공격")
    if r is not None:
        rallies.append(r)

# --- 3세트 (HKL 27 : 20 KGC 완승) ---
s3_flow = [
    (1, 0, "HKL", "kin_kill"),
    (3, 1, "HKL", "kim_block"),
    (5, 2, "HKL", "just_ace"),
    (7, 3, "HKL", "kin_block"),
    (9, 5, "KGC", "jong_kill"),
    (11, 7, "HKL", "pyo_kill"),
    (13, 8, "HKL", "jung_quick"),
    (15, 10, "KGC", "parkh_kill"),
    (17, 11, "HKL", "long_hkl"),
    (19, 13, "KGC", "jong_kill"),
    (21, 14, "HKL", "kin_kill"),
    (23, 16, "HKL", "just_kill"),
    (24, 18, "KGC", "shin_kill"),
    (25, 19, "HKL", "kin_kill"),
    (26, 20, "KGC", "jong_kill"),
    (27, 20, "HKL", "kin_kill")
]

for i, (sh, sk, team, typ) in enumerate(s3_flow, 1):
    r = None
    if typ == "kin_kill":
        r = make_kill_rally(3, i, 208, 110, 107, 101, sh, sk, "킨델란 백어택")
    elif typ == "jong_kill":
        r = make_kill_rally(3, i, 107, 207, 208, 201, sh, sk, "종휘 레프트 득점")
    elif typ == "parkh_kill":
        r = make_kill_rally(3, i, 102, 207, 208, 202, sh, sk, "박혜민 퀵오픈")
    elif typ == "pyo_kill":
        r = make_kill_rally(3, i, 201, 110, 107, 103, sh, sk, "표승주 직선 강타")
    elif typ == "just_kill":
        r = make_kill_rally(3, i, 201, 110, 107, 102, sh, sk, "자스티스 득점")
    elif typ == "shin_kill":
        r = make_kill_rally(3, i, 106, 207, 208, 204, sh, sk, "신은지 득점")
    elif typ == "jung_quick":
        r = make_kill_rally(3, i, 206, 110, 107, 104, sh, sk, "정호영 이동공격")
    elif typ == "just_ace":
        r = make_ace_rally(3, i, 102, 207, sh, sk)
    elif typ == "kin_block":
        r = make_block_rally(3, i, 101, 207, 208, 201, 101, sh, sk)
    elif typ == "kim_block":
        r = make_block_rally(3, i, 106, 207, 208, 203, 106, sh, sk)
    elif typ == "long_hkl":
        r = make_long_rally(3, i, sh, sk, "HKL")
    else:
        r = make_kill_rally(3, i, 208, 110, 107, 101, sh, sk, "공격")
    if r is not None:
        rallies.append(r)

# 데이터 오브젝트 완성
full_data_1104 = {
    "match_info": {
        "date": "2026-11-04",
        "day": "화",
        "time": "19:00",
        "league": "2026-2027 도드람 V-리그 여자부 1R",
        "venue": "인천 삼산월드체육관",
        "title": "[흥국생명 vs 정관장] V-리그 전술 분석 & 리뷰 판",
        "home_team": "HKL",
        "away_team": "KGC",
        "result_text": "흥국생명 3 : 0 정관장 (세트스코어 3-0 완승)",
        "set_scores": "25:21, 27:25, 27:20",
        "total_score": "79 : 66"
    },
    "teams": [
        {
            "id": "HKL",
            "name": "흥국생명 핑크스파이더스",
            "short_name": "흥국생명",
            "primary_color": "#E6007E",
            "accent_color": "#7928CA",
            "bg_color": "#2B1425",
            "is_home": 1
        },
        {
            "id": "KGC",
            "name": "정관장 레드스파크스",
            "short_name": "정관장",
            "primary_color": "#E2252B",
            "accent_color": "#FF8A5B",
            "bg_color": "#2A1A1E",
            "is_home": 0
        }
    ],
    "summary": {
        "HKL": {
            "team_id": "HKL",
            "att_made": 40,
            "att_tried": 105,
            "att_pct": 38.1,
            "blk_made": 10,
            "blk_tried": 58,
            "srv_made": 9,
            "srv_tried": 78,
            "dig_made": 67,
            "dig_tried": 80,
            "dig_pct": 83.75,
            "rcv_made": 17,
            "rcv_tried": 66,
            "rcv_pct": 25.76,
            "set_made": 36,
            "set_tried": 95,
            "opp_errors": 20,
            "errors": 17
        },
        "KGC": {
            "team_id": "KGC",
            "att_made": 40,
            "att_tried": 124,
            "att_pct": 32.26,
            "blk_made": 6,
            "blk_tried": 50,
            "srv_made": 3,
            "srv_tried": 68,
            "dig_made": 74,
            "dig_tried": 88,
            "dig_pct": 84.09,
            "rcv_made": 20,
            "rcv_tried": 73,
            "rcv_pct": 27.4,
            "set_made": 39,
            "set_tried": 115,
            "opp_errors": 17,
            "errors": 20
        }
    },
    "best_players": {
        "HKL": [
            {"rank": 1, "name": "자스티스", "votes": 263, "pct": 47, "pos": "OH"},
            {"rank": 2, "name": "김수지", "votes": 128, "pct": 23, "pos": "MB"},
            {"rank": 3, "name": "표승주", "votes": 63, "pct": 11, "pos": "OH"}
        ],
        "KGC": [
            {"rank": 1, "name": "종휘", "votes": 184, "pct": 58, "pos": "OH"},
            {"rank": 2, "name": "박혜민", "votes": 74, "pct": 23, "pos": "OH"},
            {"rank": 3, "name": "전다빈", "votes": 16, "pct": 5, "pos": "OH"}
        ]
    },
    "key_players": {
        "points": {"HKL": {"name": "킨델란", "val": 22}, "KGC": {"name": "종휘", "val": 24}},
        "attacks": {"HKL": {"name": "킨델란", "val": 17}, "KGC": {"name": "종휘", "val": 20}},
        "serves": {"HKL": {"name": "자스티스", "val": 3}, "KGC": {"name": "박은진", "val": 1}},
        "blocks": {"HKL": {"name": "킨델란", "val": 4}, "KGC": {"name": "종휘", "val": 3}},
        "digs": {"HKL": {"name": "자스티스", "val": 19}, "KGC": {"name": "노란", "val": 16}},
        "receives": {"HKL": {"name": "고민지", "val": 7}, "KGC": {"name": "종휘", "val": 12}},
        "sets": {"HKL": {"name": "이나연", "val": 25}, "KGC": {"name": "염혜선", "val": 28}}
    },
    "sets": [
        {"set_no": 1, "kgc_score": 21, "hkl_score": 25, "winner": "HKL", "score_home": 25, "score_away": 21},
        {"set_no": 2, "kgc_score": 25, "hkl_score": 27, "winner": "HKL", "score_home": 27, "score_away": 25},
        {"set_no": 3, "kgc_score": 20, "hkl_score": 27, "winner": "HKL", "score_home": 27, "score_away": 20}
    ],
    "lineups": {
        "HKL": {
            "S": 107,
            "OH1": 102,
            "OH2": 103,
            "OP": 101,
            "MB1": 106,
            "MB2": 104,
            "L": 110
        },
        "KGC": {
            "S": 208,
            "OH1": 201,
            "OH2": 202,
            "OP": 204,
            "MB1": 206,
            "MB2": 203,
            "L": 207
        }
    },
    "players": [
        # --- 흥국생명 선수단 (17명) ---
        {
            "id": 101, "team_id": "HKL", "name": "킨델란", "position": "OP", "number": 11,
            "sets_played": 3, "points": 22, "att_made": 17, "att_tried": 36, "att_pct": 47.22, "att_share": 34.29,
            "srv_made": 1, "srv_tried": 10, "blk_made": 4, "blk_tried": 7, "dig_made": 8, "dig_tried": 9,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 3, "errors": 7,
            "comment": "공격 17/36(47.22%), 블로킹 4개 포함 팀 최다 22득점 폭발. 고공 타점과 강력한 블로킹 벽으로 승리를 견인함.",
            "blk_pct": 57.14, "dig_pct": 88.89, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 10.0,
            "blk_per_set": 1.33, "dig_per_set": 2.67
        },
        {
            "id": 102, "team_id": "HKL", "name": "자스티스", "position": "OH", "number": 7,
            "sets_played": 3, "points": 9, "att_made": 6, "att_tried": 17, "att_pct": 35.29, "att_share": 16.19,
            "srv_made": 3, "srv_tried": 20, "blk_made": 0, "blk_tried": 5, "dig_made": 19, "dig_tried": 23,
            "rcv_made": 4, "rcv_tried": 15, "set_made": 1, "set_tried": 5, "errors": 0,
            "comment": "팬 투표 BEST 플레이어 1위(47%). 서브 득점 3개와 디그 19개(82.6%)로 코트 전역을 지배. 범실 0개의 무결점 활약.",
            "blk_pct": 0.0, "dig_pct": 82.61, "rcv_pct": 26.67, "set_pct": 20.0, "srv_pct": 15.0,
            "blk_per_set": 0.0, "dig_per_set": 6.33
        },
        {
            "id": 103, "team_id": "HKL", "name": "표승주", "position": "OH", "number": 19,
            "sets_played": 3, "points": 9, "att_made": 7, "att_tried": 23, "att_pct": 30.43, "att_share": 21.90,
            "srv_made": 1, "srv_tried": 7, "blk_made": 1, "blk_tried": 10, "dig_made": 3, "dig_tried": 3,
            "rcv_made": 6, "rcv_tried": 20, "set_made": 1, "set_tried": 2, "errors": 2,
            "comment": "팬 투표 3위(11%). 공격 7득점 포함 총 9득점. 리시브 6/20으로 수비 라인을 지탱하며 공격 점유율 21.9% 분담.",
            "blk_pct": 10.0, "dig_pct": 100.0, "rcv_pct": 30.0, "set_pct": 50.0, "srv_pct": 14.29,
            "blk_per_set": 0.33, "dig_per_set": 1.0
        },
        {
            "id": 104, "team_id": "HKL", "name": "정호영", "position": "MB", "number": 17,
            "sets_played": 3, "points": 7, "att_made": 5, "att_tried": 10, "att_pct": 50.00, "att_share": 9.52,
            "srv_made": 1, "srv_tried": 7, "blk_made": 1, "blk_tried": 18, "dig_made": 1, "dig_tried": 1,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 4, "errors": 2,
            "comment": "중앙 속공 5/10(50.0%)의 높은 효율. 18번의 블로킹 시도로 상대 미들과 공격수를 강하게 압박.",
            "blk_pct": 5.56, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 25.0, "srv_pct": 14.29,
            "blk_per_set": 0.33, "dig_per_set": 0.33
        },
        {
            "id": 105, "team_id": "HKL", "name": "정윤주", "position": "OH", "number": 13,
            "sets_played": 2, "points": 5, "att_made": 3, "att_tried": 10, "att_pct": 30.00, "att_share": 9.52,
            "srv_made": 0, "srv_tried": 2, "blk_made": 2, "blk_tried": 5, "dig_made": 0, "dig_tried": 1,
            "rcv_made": 0, "rcv_tried": 2, "set_made": 1, "set_tried": 2, "errors": 0,
            "comment": "2세트 교체 투입되어 블로킹 2득점 포함 5득점. 범실 없이 클러치 타임에 알짜 득점 제공.",
            "blk_pct": 40.0, "dig_pct": 0.0, "rcv_pct": 0.0, "set_pct": 50.0, "srv_pct": 0.0,
            "blk_per_set": 1.0, "dig_per_set": 0.0
        },
        {
            "id": 106, "team_id": "HKL", "name": "김수지", "position": "MB", "number": 4,
            "sets_played": 3, "points": 3, "att_made": 0, "att_tried": 3, "att_pct": None, "att_share": 2.86,
            "srv_made": 1, "srv_tried": 8, "blk_made": 2, "blk_tried": 13, "dig_made": 2, "dig_tried": 3,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 2, "errors": 2,
            "comment": "팬 투표 2위(23%). 블로킹 2개와 서브 득점 1개. 네트 앞 베테랑의 리딩 블로킹으로 정관장의 길목을 차단.",
            "blk_pct": 15.38, "dig_pct": 66.67, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 12.5,
            "blk_per_set": 0.67, "dig_per_set": 0.67
        },
        {
            "id": 107, "team_id": "HKL", "name": "이나연", "position": "S", "number": 6,
            "sets_played": 3, "points": 2, "att_made": 1, "att_tried": 2, "att_pct": 50.00, "att_share": 1.90,
            "srv_made": 1, "srv_tried": 17, "blk_made": 0, "blk_tried": 2, "dig_made": 11, "dig_tried": 12,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 25, "set_tried": 62, "errors": 4,
            "comment": "세트 성공 25/62(40.3%)로 킨델란-자스티스-표승주 삼각편대를 이끎. 디그 11/12(91.7%)의 놀라운 수비 집중력.",
            "blk_pct": 0.0, "dig_pct": 91.67, "rcv_pct": None, "set_pct": 40.32, "srv_pct": 5.88,
            "blk_per_set": 0.0, "dig_per_set": 3.67
        },
        {
            "id": 108, "team_id": "HKL", "name": "박수연", "position": "OH", "number": 15,
            "sets_played": 2, "points": 1, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 1, "srv_tried": 4, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "2세트 원포인트 서버로 투입되어 천금 같은 서브 득점 1개 기록.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": 25.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 109, "team_id": "HKL", "name": "문지윤", "position": "OP", "number": 16,
            "sets_played": 1, "points": 1, "att_made": 1, "att_tried": 2, "att_pct": 50.00, "att_share": 1.90,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 5, "dig_made": 1, "dig_tried": 1,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "1세트 교체 출전해 공격 1득점 기록.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": None, "set_pct": None, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 1.0
        },
        {
            "id": 110, "team_id": "HKL", "name": "고민지", "position": "L", "number": 8,
            "sets_played": 3, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 14, "dig_tried": 18,
            "rcv_made": 7, "rcv_tried": 18, "set_made": 3, "set_tried": 8, "errors": 0,
            "comment": "주전 리베로. 디그 14/18(77.8%), 리시브 7/18(38.9%)로 팀 최다 리시브 정확 기록.",
            "blk_pct": None, "dig_pct": 77.78, "rcv_pct": 38.89, "set_pct": 37.5, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 4.67
        },
        {
            "id": 111, "team_id": "HKL", "name": "박혜진", "position": "S", "number": 2,
            "sets_played": 2, "points": None, "att_made": 0, "att_tried": 2, "att_pct": None, "att_share": 1.90,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 3, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 2, "set_tried": 10, "errors": 0,
            "comment": "2세트 백업 세터로 출전해 토스 2회 성공.",
            "blk_pct": 0.0, "dig_pct": None, "rcv_pct": None, "set_pct": 20.0, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 112, "team_id": "HKL", "name": "신연경", "position": "L", "number": 5,
            "sets_played": 2, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 6, "dig_tried": 7,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 2, "errors": 0,
            "comment": "2세트 수비 리베로로 투입되어 디그 6/7(85.7%)의 견고한 수비력 과시.",
            "blk_pct": None, "dig_pct": 85.71, "rcv_pct": None, "set_pct": 50.0, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 3.0
        },
        {
            "id": 113, "team_id": "HKL", "name": "이고은", "position": "S", "number": 3,
            "sets_played": 1, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 1, "blk_made": 0, "blk_tried": 0, "dig_made": 1, "dig_tried": 1,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 4, "errors": 0,
            "comment": "1세트 원포인트 세터/서버로 투입.",
            "blk_pct": None, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 25.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.0
        },
        {
            "id": 114, "team_id": "HKL", "name": "이신영", "position": "OH", "number": 9,
            "sets_played": 1, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 2, "blk_made": 0, "blk_tried": 0, "dig_made": 1, "dig_tried": 1,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 0,
            "comment": "1세트 교체 투입, 디그 1회 기록.",
            "blk_pct": None, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.0
        },
        {
            "id": 115, "team_id": "HKL", "name": "김다은", "position": "OH", "number": 1,
            "sets_played": None, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "이번 경기 출전 기록이 없습니다.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": None,
            "blk_per_set": None, "dig_per_set": None
        },
        {
            "id": 116, "team_id": "HKL", "name": "임혜림", "position": "MB", "number": 12,
            "sets_played": None, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "이번 경기 출전 기록이 없습니다.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": None,
            "blk_per_set": None, "dig_per_set": None
        },
        {
            "id": 117, "team_id": "HKL", "name": "최은지", "position": "OH", "number": 18,
            "sets_played": None, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "이번 경기 출전 기록이 없습니다.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": None,
            "blk_per_set": None, "dig_per_set": None
        },

        # --- 정관장 선수단 (14명) ---
        {
            "id": 201, "team_id": "KGC", "name": "종휘", "position": "OH", "number": 17,
            "sets_played": 3, "points": 24, "att_made": 20, "att_tried": 57, "att_pct": 35.09, "att_share": 45.97,
            "srv_made": 1, "srv_tried": 11, "blk_made": 3, "blk_tried": 14, "dig_made": 9, "dig_tried": 12,
            "rcv_made": 12, "rcv_tried": 34, "set_made": 2, "set_tried": 4, "errors": 6,
            "comment": "팬 투표 BEST 플레이어 1위(58%). 양 팀 최다 24득점 폭발. 공격 점유율 45.97%를 홀로 떠맡으며 리시브 12개, 블로킹 3개까지 에이스의 품격을 보임.",
            "blk_pct": 21.43, "dig_pct": 75.0, "rcv_pct": 35.29, "set_pct": 50.0, "srv_pct": 9.09,
            "blk_per_set": 1.0, "dig_per_set": 3.0
        },
        {
            "id": 202, "team_id": "KGC", "name": "박혜민", "position": "OH", "number": 10,
            "sets_played": 3, "points": 13, "att_made": 10, "att_tried": 20, "att_pct": 50.00, "att_share": 16.13,
            "srv_made": 1, "srv_tried": 12, "blk_made": 2, "blk_tried": 9, "dig_made": 13, "dig_tried": 14,
            "rcv_made": 4, "rcv_tried": 23, "set_made": 3, "set_tried": 7, "errors": 2,
            "comment": "팬 투표 2위(23%). 공격 10/20(50.0%)의 초고효율과 블로킹 2개, 디그 13개(92.9%)로 종휘를 든든히 보좌.",
            "blk_pct": 22.22, "dig_pct": 92.86, "rcv_pct": 17.39, "set_pct": 42.86, "srv_pct": 8.33,
            "blk_per_set": 0.67, "dig_per_set": 4.33
        },
        {
            "id": 203, "team_id": "KGC", "name": "이선우", "position": "MB", "number": 15,
            "sets_played": 3, "points": 6, "att_made": 6, "att_tried": 22, "att_pct": 27.27, "att_share": 17.74,
            "srv_made": 0, "srv_tried": 6, "blk_made": 0, "blk_tried": 3, "dig_made": 11, "dig_tried": 14,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 3, "errors": 2,
            "comment": "공격 6득점, 디그 11개(78.6%) 성공. 미들 블로커 포지션에서 점유율 17.7%를 소화하며 분전.",
            "blk_pct": 0.0, "dig_pct": 78.57, "rcv_pct": None, "set_pct": 33.33, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 3.67
        },
        {
            "id": 204, "team_id": "KGC", "name": "신은지", "position": "OP", "number": 16,
            "sets_played": 3, "points": 3, "att_made": 3, "att_tried": 4, "att_pct": 75.00, "att_share": 3.23,
            "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 2, "dig_made": 4, "dig_tried": 4,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 2, "errors": 1,
            "comment": "공격 3/4(75.0%)의 순도 높은 득점력. 디그 4/4(100.0%)의 깔끔한 수비 지원.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.33
        },
        {
            "id": 205, "team_id": "KGC", "name": "이지수", "position": "MB", "number": 18,
            "sets_played": 3, "points": 2, "att_made": 1, "att_tried": 10, "att_pct": 10.00, "att_share": 8.06,
            "srv_made": 0, "srv_tried": 7, "blk_made": 1, "blk_tried": 4, "dig_made": 5, "dig_tried": 6,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 3, "errors": 2,
            "comment": "블로킹 1득점 및 디그 5개 기록.",
            "blk_pct": 25.0, "dig_pct": 83.33, "rcv_pct": None, "set_pct": 33.33, "srv_pct": 0.0,
            "blk_per_set": 0.33, "dig_per_set": 1.67
        },
        {
            "id": 206, "team_id": "KGC", "name": "박은진", "position": "MB", "number": 6,
            "sets_played": 3, "points": 1, "att_made": 0, "att_tried": 9, "att_pct": None, "att_share": 7.26,
            "srv_made": 1, "srv_tried": 14, "blk_made": 0, "blk_tried": 5, "dig_made": 4, "dig_tried": 5,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 3, "errors": 5,
            "comment": "서브 득점 1개 및 디그 4개. 공격 성공률 0%와 범실 5개가 뼈아팠던 경기.",
            "blk_pct": 0.0, "dig_pct": 80.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 7.14,
            "blk_per_set": 0.0, "dig_per_set": 1.33
        },
        {
            "id": 207, "team_id": "KGC", "name": "노란", "position": "L", "number": 5,
            "sets_played": 3, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 16, "dig_tried": 20,
            "rcv_made": 4, "rcv_tried": 9, "set_made": 2, "set_tried": 10, "errors": 0,
            "comment": "주전 리베로로 디그 16/20(80.0%)의 몸을 던지는 호수비 연출.",
            "blk_pct": None, "dig_pct": 80.0, "rcv_pct": 44.44, "set_pct": 20.0, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 5.33
        },
        {
            "id": 208, "team_id": "KGC", "name": "염혜선", "position": "S", "number": 3,
            "sets_played": 3, "points": None, "att_made": 0, "att_tried": 2, "att_pct": None, "att_share": 1.61,
            "srv_made": 0, "srv_tried": 12, "blk_made": 0, "blk_tried": 6, "dig_made": 12, "dig_tried": 15,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 28, "set_tried": 94, "errors": 2,
            "comment": "세트 성공 28/94(29.8%)로 종휘와 박혜민에게 집중 연결. 디그 12/15(80.0%)로 수비 분전.",
            "blk_pct": 0.0, "dig_pct": 80.0, "rcv_pct": None, "set_pct": 29.79, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 4.0
        },
        {
            "id": 209, "team_id": "KGC", "name": "곽선옥", "position": "OH", "number": 7,
            "sets_played": 2, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 2, "set_tried": 2, "errors": 0,
            "comment": "2세트 교체 출전해 세트 2회 성공.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": 100.0, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 210, "team_id": "KGC", "name": "전다빈", "position": "OH", "number": 4,
            "sets_played": 2, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 2, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "팬 투표 3위(5%). 원포인트 서버로 2세트 투입.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 211, "team_id": "KGC", "name": "도수빈", "position": "L", "number": 12,
            "sets_played": 1, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 1,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "1세트 교체 수비수로 출전.",
            "blk_pct": None, "dig_pct": 0.0, "rcv_pct": None, "set_pct": None, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 212, "team_id": "KGC", "name": "박여름", "position": "OH", "number": 23,
            "sets_played": 1, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 1, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "1세트 교체 출전.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": 0.0, "set_pct": None, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 213, "team_id": "KGC", "name": "최서현", "position": "S", "number": 19,
            "sets_played": 1, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "1세트 교체 세터로 출전.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": None,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 214, "team_id": "KGC", "name": "최효서", "position": "OH", "number": 20,
            "sets_played": None, "points": None, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": None,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "이번 경기 출전 기록이 없습니다.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": None,
            "blk_per_set": None, "dig_per_set": None
        }
    ],
    "scenarios": [
        {
            "id": 1,
            "code": "KIN_BLOCK_ATTACK",
            "title": "킨델란 22득점 폭격 & 블로킹 장벽",
            "subtitle": "흥국생명 이나연 토스 → 킨델란 라이트 고공 오픈 및 블로킹 4득점",
            "attack_team": "HKL",
            "sort_order": 0,
            "phases": [
                {
                    "name": "포메이션", "dur": 1300,
                    "moves": [
                        {"who": "def.Z1", "to": [-6, 78], "delay": 0.0, "end": 1.0},
                        {"who": "def.Z2", "to": [84, 78], "delay": 0.0, "end": 1.0},
                        {"who": "def.Z3", "to": [84, 45], "delay": 0.0, "end": 1.0},
                        {"who": "def.Z4", "to": [84, 12], "delay": 0.0, "end": 1.0},
                        {"who": "def.Z5", "to": [22, 15], "delay": 0.0, "end": 1.0},
                        {"who": "def.Z6", "to": [22, 45], "delay": 0.0, "end": 1.0},
                        {"who": "atk.OHF", "to": [32, 20], "delay": 0.0, "end": 1.0},
                        {"who": "atk.L", "to": [28, 45], "delay": 0.0, "end": 1.0},
                        {"who": "atk.OHB", "to": [32, 70], "delay": 0.0, "end": 1.0},
                        {"who": "atk.MBF", "to": [78, 40], "delay": 0.0, "end": 1.0},
                        {"who": "atk.OP", "to": [80, 84], "delay": 0.0, "end": 1.0},
                        {"who": "atk.S", "to": [74, 64], "delay": 0.0, "end": 1.0}
                    ],
                    "focus": "atk.OP", "tags": ["#킨델란", "#에이스폭발"],
                    "text": "흥국생명은 킨델란·자스티스 쌍포를 가동합니다. 정관장은 종휘의 서브로 리시브를 흔들려 합니다."
                },
                {
                    "name": "서브 & 리시브", "dur": 1300,
                    "ball": [{"from": ["def", -4, 78], "to": ["atk", 28, 45], "h": 32, "delay": 0.0, "end": 1.0}],
                    "moves": [
                        {"who": "atk.S", "to": [83, 60], "delay": 0.15, "end": 0.9, "trail": True}
                    ],
                    "focus": "atk.L", "tags": ["#고민지리시브"],
                    "text": "정관장의 서브를 리베로 고민지가 안정적으로 세터 이나연 머리 위로 올립니다."
                },
                {
                    "name": "라이트 백토스", "dur": 1100,
                    "ball": [{"from": ["atk", 83, 60], "to": ["atk", 85, 84], "h": 46, "delay": 0.0, "end": 1.0}],
                    "moves": [
                        {"who": "atk.OP", "to": [85, 84], "delay": 0.15, "end": 1.0, "via": [70, 88], "trail": True},
                        {"who": "def.Z4", "to": [86.5, 12], "delay": 0.35, "end": 1.0},
                        {"who": "def.Z3", "to": [86.5, 20], "delay": 0.4, "end": 1.0}
                    ],
                    "focus": "atk.OP", "tags": ["#킨델란고공강타"],
                    "text": "세터 이나연의 높은 백토스가 라이트 킨델란에게 배달됩니다. 정관장 2인 블로커 위에서 찍어누릅니다!"
                },
                {
                    "name": "스파이크 득점", "dur": 900,
                    "ball": [{"from": ["atk", 85, 84], "to": ["def", 26, 75], "h": 4, "delay": 0.0, "end": 1.0}],
                    "focus": "atk.OP", "tags": ["#22득점", "#블로킹4개"],
                    "text": "킨델란의 각도 깊은 직선 강타가 코트에 꽂힙니다! (킨델란 오늘 22득점, 블로킹 4득점 대폭발)"
                },
                {
                    "name": "전술 분석", "dur": 1800, "result": "atk", "moves": [],
                    "focus": "atk.OP", "tags": ["#흥국완승"],
                    "text": "흥국생명 득점. 킨델란은 오늘 공격 성공률 47.22%에 공격 점유율 34.29%를 기록하며 흥국생명의 3-0 셧아웃 승리를 이끌었습니다."
                }
            ]
        },
        {
            "id": 2,
            "code": "JUSTICE_SERVE_DIG",
            "title": "자스티스 3서브에이스 & 19디그 철벽수비",
            "subtitle": "BEST 플레이어 1위(47%) 자스티스의 공수 완벽 지배",
            "attack_team": "HKL",
            "sort_order": 1,
            "phases": [
                {
                    "name": "서브 준비", "dur": 1300,
                    "moves": [
                        {"who": "atk.Z1", "to": [-6, 78], "delay": 0.0, "end": 1.0},
                        {"who": "def.OHF", "to": [32, 20], "delay": 0.0, "end": 1.0},
                        {"who": "def.L", "to": [28, 45], "delay": 0.0, "end": 1.0},
                        {"who": "def.OHB", "to": [32, 70], "delay": 0.0, "end": 1.0}
                    ],
                    "focus": "atk.Z1", "tags": ["#자스티스서브", "#서브에이스3개"],
                    "text": "팬 투표 1위(263표, 47%) 자스티스의 강서브 차례. 오늘 서브 득점 3개와 디그 19개를 기록했습니다."
                },
                {
                    "name": "강서브 에이스", "dur": 1200,
                    "ball": [{"from": ["atk", -4, 78], "to": ["def", 12, 18], "h": 22, "delay": 0.0, "end": 1.0}],
                    "focus": "atk.Z1", "tags": ["#서브득점"],
                    "text": "코트 엔드라인 구석에 꽂히는 예리한 서브! 정관장 리시브 라인이 손을 대지 못합니다. 서브 에이스!"
                },
                {
                    "name": "전술 분석", "dur": 1800, "result": "atk", "moves": [],
                    "focus": "atk.Z1", "tags": ["#범실0개", "#BEST플레이어"],
                    "text": "자스티스는 공격 9득점, 서브 3득점에 범실 0개, 디그 19개를 기록하며 팀 승리의 일등공신이 되었습니다."
                }
            ]
        },
        {
            "id": 3,
            "code": "JONGHWI_24PTS",
            "title": "종휘 46% 점유율 레프트 강타 & 24득점",
            "subtitle": "정관장 에이스 종휘의 고군분투 24득점 (공격 20 + 블로킹 3)",
            "attack_team": "KGC",
            "sort_order": 2,
            "phases": [
                {
                    "name": "포메이션", "dur": 1300,
                    "moves": [
                        {"who": "atk.OHF", "to": [60, 8], "delay": 0.0, "end": 1.0},
                        {"who": "atk.S", "to": [83, 60], "delay": 0.0, "end": 1.0},
                        {"who": "def.Z2", "to": [84, 76], "delay": 0.0, "end": 1.0},
                        {"who": "def.Z3", "to": [84, 45], "delay": 0.0, "end": 1.0}
                    ],
                    "focus": "atk.OHF", "tags": ["#종휘24득점", "#점유율46%"],
                    "text": "정관장의 볼은 어김없이 종휘를 향합니다. 오늘 공격 점유율 45.97%를 홀로 책임집니다."
                },
                {
                    "name": "레프트 오픈 토스", "dur": 1200,
                    "ball": [{"from": ["atk", 83, 60], "to": ["atk", 85, 8], "h": 50, "delay": 0.0, "end": 1.0}],
                    "moves": [
                        {"who": "atk.OHF", "to": [85, 8], "delay": 0.2, "end": 1.0, "via": [70, 0], "trail": True},
                        {"who": "def.Z2", "to": [86.5, 80], "delay": 0.4, "end": 1.0},
                        {"who": "def.Z3", "to": [86.5, 72], "delay": 0.45, "end": 1.0}
                    ],
                    "focus": "atk.OHF", "tags": ["#블로커돌파"],
                    "text": "흥국생명의 높은 2인 블로킹 벽 사이를 뚫어내는 종휘의 강력한 대각 스파이크!"
                },
                {
                    "name": "득점", "dur": 900,
                    "ball": [{"from": ["atk", 85, 8], "to": ["def", 28, 62], "h": 5, "delay": 0.0, "end": 1.0}],
                    "focus": "atk.OHF", "tags": ["#에이스"],
                    "text": "코트 코너를 찌르는 종휘의 득점! 양 팀 통틀어 최다인 24득점을 쓸어담습니다."
                },
                {
                    "name": "전술 분석", "dur": 1800, "result": "atk", "moves": [],
                    "focus": "atk.OHF", "tags": ["#투혼"],
                    "text": "정관장 종휘는 공격 20득점, 블로킹 3득점, 서브 1득점에 리시브 12개까지 분전했으나 팀 패배를 막지는 못했습니다."
                }
            ]
        },
        {
            "id": 4,
            "code": "PARK_HYEMIN_TECH",
            "title": "박혜민 50% 성공률과 테크니컬 13득점",
            "subtitle": "공격 10/20(50%) + 블로킹 2개 + 디그 13개 활약",
            "attack_team": "KGC",
            "sort_order": 3,
            "phases": [
                {
                    "name": "디그 후 반격", "dur": 1300,
                    "ball": [{"from": ["def", 85, 84], "to": ["atk", 30, 45], "h": 12, "delay": 0.0, "end": 1.0}],
                    "focus": "atk.OHB", "tags": ["#박혜민", "#디그반격"],
                    "text": "박혜민의 기민한 디그로 반격 기회를 잡는 정관장."
                },
                {
                    "name": "퀵오픈 스파이크", "dur": 1100,
                    "ball": [{"from": ["atk", 83, 60], "to": ["atk", 85, 12], "h": 32, "delay": 0.0, "end": 0.7},
                             {"from": ["atk", 85, 12], "to": ["def", 34, 25], "h": 4, "delay": 0.7, "end": 1.0}],
                    "moves": [
                        {"who": "atk.OHB", "to": [85, 12], "delay": 0.1, "end": 0.7, "via": [65, 14], "trail": True}
                    ],
                    "focus": "atk.OHB", "tags": ["#50%성공률"],
                    "text": "박혜민의 빠른 퀵오픈 페인트! 상대 수비의 빈틈을 정확하게 찔러넣습니다."
                },
                {
                    "name": "전술 분석", "dur": 1800, "result": "atk", "moves": [],
                    "focus": "atk.OHB", "tags": ["#박혜민활약"],
                    "text": "박혜민은 공격 10/20(50.0%)로 팀 공격수 중 최고 성공률을 기록했습니다."
                }
            ]
        }
    ],
    "rallies": rallies,
    "set_stats": [
        # 1세트 핵심 기록
        {"set_no": 1, "player_id": 101, "att_made": 6, "att_tried": 12, "srv_made": 0, "srv_tried": 3, "blk_made": 2, "blk_tried": 3, "dig_made": 3, "dig_tried": 3, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2, "points": 8},
        {"set_no": 1, "player_id": 102, "att_made": 2, "att_tried": 6, "srv_made": 1, "srv_tried": 7, "blk_made": 0, "blk_tried": 2, "dig_made": 7, "dig_tried": 8, "rcv_made": 2, "rcv_tried": 6, "set_made": 0, "set_tried": 2, "errors": 0, "points": 3},
        {"set_no": 1, "player_id": 201, "att_made": 7, "att_tried": 18, "srv_made": 0, "srv_tried": 4, "blk_made": 1, "blk_tried": 4, "dig_made": 3, "dig_tried": 4, "rcv_made": 5, "rcv_tried": 12, "set_made": 1, "set_tried": 2, "errors": 2, "points": 8},
        {"set_no": 1, "player_id": 202, "att_made": 3, "att_tried": 7, "srv_made": 0, "srv_tried": 4, "blk_made": 1, "blk_tried": 3, "dig_made": 4, "dig_tried": 5, "rcv_made": 2, "rcv_tried": 8, "set_made": 1, "set_tried": 2, "errors": 1, "points": 4},

        # 2세트 핵심 기록
        {"set_no": 2, "player_id": 101, "att_made": 6, "att_tried": 13, "srv_made": 1, "srv_tried": 4, "blk_made": 1, "blk_tried": 2, "dig_made": 3, "dig_tried": 3, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 3, "points": 8},
        {"set_no": 2, "player_id": 105, "att_made": 2, "att_tried": 6, "srv_made": 0, "srv_tried": 1, "blk_made": 2, "blk_tried": 3, "dig_made": 0, "dig_tried": 1, "rcv_made": 0, "rcv_tried": 1, "set_made": 0, "set_tried": 1, "errors": 0, "points": 4},
        {"set_no": 2, "player_id": 201, "att_made": 8, "att_tried": 22, "srv_made": 1, "srv_tried": 4, "blk_made": 1, "blk_tried": 5, "dig_made": 3, "dig_tried": 4, "rcv_made": 4, "rcv_tried": 12, "set_made": 0, "set_tried": 1, "errors": 2, "points": 10},

        # 3세트 핵심 기록
        {"set_no": 3, "player_id": 101, "att_made": 5, "att_tried": 11, "srv_made": 0, "srv_tried": 3, "blk_made": 1, "blk_tried": 2, "dig_made": 2, "dig_tried": 3, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2, "points": 6},
        {"set_no": 3, "player_id": 102, "att_made": 3, "att_tried": 7, "srv_made": 1, "srv_tried": 6, "blk_made": 0, "blk_tried": 1, "dig_made": 6, "dig_tried": 7, "rcv_made": 1, "rcv_tried": 4, "set_made": 1, "set_tried": 2, "errors": 0, "points": 4},
        {"set_no": 3, "player_id": 201, "att_made": 5, "att_tried": 17, "srv_made": 0, "srv_tried": 3, "blk_made": 1, "blk_tried": 5, "dig_made": 3, "dig_tried": 4, "rcv_made": 3, "rcv_tried": 10, "set_made": 1, "set_tried": 1, "errors": 2, "points": 6}
    ]
}

js_code = f"window.BOOTSTRAP_1104 = {json.dumps(full_data_1104, ensure_ascii=False, indent=2)};\n"
js_code += """
window.MATCHES = window.MATCHES || {};
if (window.BOOTSTRAP) {
  window.MATCHES['2026-11-07'] = window.BOOTSTRAP;
}
window.MATCHES['2026-11-04'] = window.BOOTSTRAP_1104;
"""

Path(ROOT / "js" / "data_1104.js").write_text(js_code, encoding="utf-8")
Path(ROOT / "static" / "js" / "data_1104.js").write_text(js_code, encoding="utf-8")
print(f"Generated data_1104.js with {len(rallies)} rallies successfully!")
