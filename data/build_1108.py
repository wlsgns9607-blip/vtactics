# -*- coding: utf-8 -*-
"""
11월 8일 한국도로공사 vs 흥국생명 V-리그 전 경기 데이터 생성기
- 한국도로공사 (EXP, 홈) 3 : 1 (29:27, 25:19, 23:25, 25:13) 흥국생명 (HKL, 어웨이) -> 총 득점 102 : 84
- 모마 26득점(공격 23, 서브 3), 마미 17득점, 김세빈 15득점(블로킹 7), 강소휘 10득점
- 킨델란 23득점, 자스티스 16득점, 정호영 11득점(블로킹 7)
"""
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent

# 도로공사 선수단 (ID 501~513)
EXP_P = {
    501: ("모마", 99, "OP", "EXP"),
    502: ("마미", 10, "OH", "EXP"),
    503: ("김세빈", 11, "MB", "EXP"),
    504: ("강소휘", 97, "OH", "EXP"),
    505: ("김현지", 17, "MB", "EXP"),
    506: ("이윤정", 6, "S", "EXP"),
    507: ("박정아", 9, "OH", "EXP"),
    508: ("문정원", 12, "L", "EXP"),
    509: ("김세인", 14, "OH", "EXP"),
    510: ("이수연", 3, "S", "EXP"),
    511: ("박윤서", 7, "OH", "EXP"),
    512: ("손혜진", 2, "S", "EXP"),
    513: ("유다은", 19, "MB", "EXP"),
}

# 흥국생명 선수단 (ID 101~116)
HKL_P = {
    101: ("킨델란", 11, "OP", "HKL"),
    102: ("자스티스", 7, "OH", "HKL"),
    103: ("표승주", 19, "OH", "HKL"),
    104: ("정호영", 17, "MB", "HKL"),
    105: ("이고은", 3, "S", "HKL"),
    106: ("김수지", 4, "MB", "HKL"),
    107: ("임혜림", 14, "MB", "HKL"),
    108: ("정윤주", 13, "OH", "HKL"),
    109: ("최은지", 9, "OH", "HKL"),
    110: ("고민지", 8, "L", "HKL"),
    111: ("이나연", 6, "S", "HKL"),
    112: ("박수연", 15, "OH", "HKL"),
    113: ("신연경", 5, "L", "HKL"),
    114: ("박혜진", 2, "S", "HKL"),
    115: ("이신영", 16, "OH", "HKL"),
    116: ("김다은", 10, "OH", "HKL"),
}

def make_kill_rally(set_no, r_no, s_id, rcv_id, set_id, atk_id, sh, sa, act="오픈"):
    s_n, s_num, _, s_t = HKL_P[s_id] if s_id in HKL_P else EXP_P[s_id]
    r_n, r_num, _, r_t = HKL_P[rcv_id] if rcv_id in HKL_P else EXP_P[rcv_id]
    st_n, st_num, _, st_t = HKL_P[set_id] if set_id in HKL_P else EXP_P[set_id]
    a_n, a_num, _, a_t = HKL_P[atk_id] if atk_id in HKL_P else EXP_P[atk_id]
    events = [
        {"n": s_n, "num": s_num, "t": s_t, "a": f"{s_num}{s_n} 서브", "c": "serve", "ok": False, "pid": s_id},
        {"n": r_n, "num": r_num, "t": r_t, "a": f"{r_num}{r_n} 리시브 정확", "c": "receive", "ok": True, "pid": rcv_id},
        {"n": st_n, "num": st_num, "t": st_t, "a": f"{st_num}{st_n} 세트 정확", "c": "set", "ok": True, "pid": set_id},
        {"n": a_n, "num": a_num, "t": a_t, "a": f"{a_num}{a_n} {act} 성공", "c": "attack", "ok": True, "pid": atk_id},
    ]
    return {
        "set_no": set_no, "rally_no": r_no, "scorer": a_t, "server": s_t, "server_team": s_t,
        "cause": "kill", "score_exp": sh, "score_hkl": sa, "score_home": sh, "score_away": sa,
        "score_kgc": sh, "score_hdec": sa,
        "score": {"EXP": sh, "HKL": sa},
        "point_idx": 3, "events": events, "events_json": json.dumps(events, ensure_ascii=False)
    }

def make_block_rally(set_no, r_no, s_id, rcv_id, set_id, atk_id, blk_id, sh, sa):
    s_n, s_num, _, s_t = HKL_P[s_id] if s_id in HKL_P else EXP_P[s_id]
    r_n, r_num, _, r_t = HKL_P[rcv_id] if rcv_id in HKL_P else EXP_P[rcv_id]
    st_n, st_num, _, st_t = HKL_P[set_id] if set_id in HKL_P else EXP_P[set_id]
    a_n, a_num, _, a_t = HKL_P[atk_id] if atk_id in HKL_P else EXP_P[atk_id]
    b_n, b_num, _, b_t = HKL_P[blk_id] if blk_id in HKL_P else EXP_P[blk_id]
    events = [
        {"n": s_n, "num": s_num, "t": s_t, "a": f"{s_num}{s_n} 서브", "c": "serve", "ok": False, "pid": s_id},
        {"n": r_n, "num": r_num, "t": r_t, "a": f"{r_num}{r_n} 리시브 정확", "c": "receive", "ok": True, "pid": rcv_id},
        {"n": st_n, "num": st_num, "t": st_t, "a": f"{st_num}{st_n} 세트", "c": "set", "ok": False, "pid": set_id},
        {"n": a_n, "num": a_num, "t": a_t, "a": f"{a_num}{a_n} 스파이크", "c": "attack", "ok": False, "pid": atk_id},
        {"n": b_n, "num": b_num, "t": b_t, "a": f"{b_num}{b_n} 블로킹 득점", "c": "block", "ok": True, "pid": blk_id},
    ]
    return {
        "set_no": set_no, "rally_no": r_no, "scorer": b_t, "server": s_t, "server_team": s_t,
        "cause": "blockkill", "score_exp": sh, "score_hkl": sa, "score_home": sh, "score_away": sa,
        "score_kgc": sh, "score_hdec": sa,
        "score": {"EXP": sh, "HKL": sa},
        "point_idx": 4, "events": events, "events_json": json.dumps(events, ensure_ascii=False)
    }

def make_ace_rally(set_no, r_no, s_id, rcv_id, sh, sa):
    s_n, s_num, _, s_t = HKL_P[s_id] if s_id in HKL_P else EXP_P[s_id]
    r_n, r_num, _, r_t = HKL_P[rcv_id] if rcv_id in HKL_P else EXP_P[rcv_id]
    events = [
        {"n": s_n, "num": s_num, "t": s_t, "a": f"{s_num}{s_n} 서브 에이스", "c": "serve", "ok": True, "pid": s_id},
        {"n": r_n, "num": r_num, "t": r_t, "a": f"{r_num}{r_n} 리시브 실패", "c": "receive", "ok": False, "pid": rcv_id},
    ]
    return {
        "set_no": set_no, "rally_no": r_no, "scorer": s_t, "server": s_t, "server_team": s_t,
        "cause": "serveace", "score_exp": sh, "score_hkl": sa, "score_home": sh, "score_away": sa,
        "score_kgc": sh, "score_hdec": sa,
        "score": {"EXP": sh, "HKL": sa},
        "point_idx": 0, "events": events, "events_json": json.dumps(events, ensure_ascii=False)
    }

rallies: List[Dict[str, Any]] = []

# --- 1세트: 29:27 도로공사 승 (총 56 랠리 듀스 접전) ---
sh, sa = 0, 0
# 듀스 전개 시퀀스 (점수 흐름)
for i in range(1, 57):
    # 마지막 2점 28, 29는 도로공사 득점으로 세트 획득
    if i in [55, 56]:
        sh += 1
        if i == 56:
            r = make_block_rally(1, i, 506, 110, 111, 101, 503, sh, sa) # 김세빈 블로킹으로 1세트 마무리
        else:
            r = make_kill_rally(1, i, 111, 508, 506, 501, sh, sa, "라이트 백어택")
    elif sh < 27 and (sa >= 27 or (i % 2 == 1 and sh < 26) or i in [1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53]):
        sh += 1
        if i in [1, 25, 49]:
            r = make_kill_rally(1, i, 111, 508, 506, 501, sh, sa, "오픈 강타")
        elif i in [5, 33]:
            r = make_block_rally(1, i, 101, 508, 506, 102, 503, sh, sa) # 김세빈 블로킹
        elif i == 9:
            r = make_ace_rally(1, i, 501, 110, sh, sa) # 모마 서브에이스
        elif i in [13, 37]:
            r = make_kill_rally(1, i, 102, 504, 506, 502, sh, sa, "퀵오픈") # 마미
        elif i in [17, 41]:
            r = make_kill_rally(1, i, 103, 508, 506, 504, sh, sa, "시간차") # 강소휘
        else:
            r = make_kill_rally(1, i, 111, 508, 506, 501, sh, sa, "라이트 오픈")
    else:
        sa += 1
        if i in [2, 26]:
            r = make_kill_rally(1, i, 506, 110, 111, 101, sh, sa, "오픈") # 킨델란
        elif i in [6, 30]:
            r = make_block_rally(1, i, 501, 110, 111, 501, 104, sh, sa) # 정호영 블로킹
        elif i in [10, 34]:
            r = make_kill_rally(1, i, 502, 110, 111, 102, sh, sa, "퀵오픈") # 자스티스
        elif i in [14, 38]:
            r = make_kill_rally(1, i, 504, 110, 111, 103, sh, sa, "오픈") # 표승주
        else:
            r = make_kill_rally(1, i, 506, 110, 111, 101, sh, sa, "백어택")
    rallies.append(r)

# --- 2세트: 25:19 도로공사 승 (총 44 랠리) ---
sh, sa = 0, 0
for i in range(1, 45):
    if sh < 25 and (sa >= 19 or (i % 2 == 1 and sh < 24) or i in [43, 44]):
        sh += 1
        if i in [1, 15, 29]:
            r = make_kill_rally(2, i, 111, 508, 506, 501, sh, sa, "라이트 강타")
        elif i in [5, 23]:
            r = make_block_rally(2, i, 101, 508, 506, 102, 503, sh, sa) # 김세빈 블로킹
        elif i == 11:
            r = make_ace_rally(2, i, 501, 110, sh, sa) # 모마 서브에이스
        elif i in [19, 37]:
            r = make_kill_rally(2, i, 102, 504, 506, 502, sh, sa, "레프트 퀵오픈")
        else:
            r = make_kill_rally(2, i, 111, 508, 506, 504, sh, sa, "오픈")
    else:
        sa += 1
        if i in [2, 16]:
            r = make_kill_rally(2, i, 506, 110, 111, 101, sh, sa, "오픈")
        elif i in [8, 24]:
            r = make_kill_rally(2, i, 501, 110, 111, 102, sh, sa, "퀵오픈")
        elif i == 14:
            r = make_block_rally(2, i, 504, 110, 111, 504, 104, sh, sa) # 정호영 블로킹
        else:
            r = make_kill_rally(2, i, 506, 110, 111, 103, sh, sa, "오픈")
    rallies.append(r)

# --- 3세트: 23:25 흥국생명 승 (총 48 랠리) ---
sh, sa = 0, 0
for i in range(1, 49):
    if sa < 25 and (sh >= 23 or (i % 2 == 0 and sa < 24) or i in [47, 48]):
        sa += 1
        if i in [2, 20]:
            r = make_kill_rally(3, i, 506, 110, 111, 101, sh, sa, "백어택")
        elif i in [8, 26]:
            r = make_block_rally(3, i, 501, 110, 111, 501, 104, sh, sa) # 정호영 블로킹
        elif i == 14:
            r = make_ace_rally(3, i, 102, 508, sh, sa) # 자스티스 서브에이스
        elif i in [32, 48]:
            r = make_kill_rally(3, i, 502, 110, 111, 102, sh, sa, "터치아웃 퀵오픈")
        else:
            r = make_kill_rally(3, i, 506, 110, 111, 101, sh, sa, "오픈")
    else:
        sh += 1
        if i in [1, 15]:
            r = make_kill_rally(3, i, 111, 508, 506, 501, sh, sa, "오픈 강타")
        elif i in [7, 21]:
            r = make_kill_rally(3, i, 101, 504, 506, 502, sh, sa, "퀵오픈")
        elif i == 11:
            r = make_block_rally(3, i, 102, 508, 506, 103, 503, sh, sa) # 김세빈 블로킹
        else:
            r = make_kill_rally(3, i, 111, 508, 506, 504, sh, sa, "오픈")
    rallies.append(r)

# --- 4세트: 25:13 도로공사 승 (총 38 랠리 압승) ---
sh, sa = 0, 0
for i in range(1, 39):
    if sh < 25 and (sa >= 13 or (i % 3 != 0 and sh < 24) or i in [37, 38]):
        sh += 1
        if i == 38: # 매치포인트
            r = make_block_rally(4, i, 506, 110, 111, 101, 503, sh, sa) # 김세빈 매치포인트 블로킹!
        elif i in [1, 10, 22]:
            r = make_kill_rally(4, i, 111, 508, 506, 501, sh, sa, "라이트 오픈 강타")
        elif i in [4, 16, 28]:
            r = make_block_rally(4, i, 101, 508, 506, 102, 503, sh, sa) # 김세빈 블로킹
        elif i == 7:
            r = make_ace_rally(4, i, 501, 110, sh, sa) # 모마 서브에이스
        elif i in [13, 25]:
            r = make_kill_rally(4, i, 102, 504, 506, 502, sh, sa, "레프트 시간차")
        else:
            r = make_kill_rally(4, i, 111, 508, 506, 504, sh, sa, "퀵오픈")
    else:
        sa += 1
        if i in [3, 15]:
            r = make_kill_rally(4, i, 506, 110, 111, 101, sh, sa, "오픈")
        elif i == 9:
            r = make_block_rally(4, i, 501, 110, 111, 501, 104, sh, sa)
        else:
            r = make_kill_rally(4, i, 502, 110, 111, 102, sh, sa, "퀵오픈")
    rallies.append(r)

full_data_1108: Dict[str, Any] = {
    "match_info": {
        "date": "2024-11-08",
        "alt_date": "2026-11-08",
        "day": "금",
        "time": "19:00",
        "league": "2024-2025 V-리그 여자부 1R",
        "venue": "김천실내체육관",
        "title": "[한국도로공사 vs 흥국생명] V-리그 전술 분석 & 리뷰 판",
        "home_team": "EXP",
        "away_team": "HKL",
        "result_text": "한국도로공사 3 : 1 흥국생명 (세트스코어 3-1 도로공사 승)",
        "set_scores": "29:27, 25:19, 23:25, 25:13",
        "total_score": "102 : 84"
    },
    "teams": [
        {
            "id": "EXP",
            "name": "한국도로공사 하이패스",
            "short_name": "한국도로공사",
            "primary_color": "#0B4EA2",
            "accent_color": "#FF9E1B",
            "bg_color": "#162238",
            "is_home": 1
        },
        {
            "id": "HKL",
            "name": "흥국생명 핑크스파이더스",
            "short_name": "흥국생명",
            "primary_color": "#E6007E",
            "accent_color": "#9C27B0",
            "bg_color": "#2D1525",
            "is_home": 0
        }
    ],
    "players": [
        # --- 도로공사 선수단 (13명) ---
        {
            "id": 501, "team_id": "EXP", "name": "모마", "position": "OP", "number": 99,
            "sets_played": 4, "points": 26, "att_made": 23, "att_tried": 53, "att_pct": 43.4, "att_share": 31.18,
            "srv_made": 3, "srv_tried": 15, "blk_made": 0, "blk_tried": 10, "dig_made": 7, "dig_tried": 7,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 2, "set_tried": 7, "errors": 5,
            "comment": "공격 23/53(43.4%), 서브 3개 포함 양 팀 최다 26득점 대폭발. 고공 타점으로 팀 승리를 완벽 견인.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 28.57, "srv_pct": 20.0,
            "blk_per_set": 0.0, "dig_per_set": 1.75
        },
        {
            "id": 502, "team_id": "EXP", "name": "마미", "position": "OH", "number": 10,
            "sets_played": 4, "points": 17, "att_made": 16, "att_tried": 45, "att_pct": 35.56, "att_share": 26.47,
            "srv_made": 0, "srv_tried": 25, "blk_made": 1, "blk_tried": 8, "dig_made": 13, "dig_tried": 15,
            "rcv_made": 12, "rcv_tried": 31, "set_made": 1, "set_tried": 7, "errors": 4,
            "comment": "공격 16/45(35.56%) 17득점. 리시브 12개, 디그 13개로 공수 밸런스의 중추 역할 수행.",
            "blk_pct": 12.5, "dig_pct": 86.67, "rcv_pct": 38.71, "set_pct": 14.29, "srv_pct": 0.0,
            "blk_per_set": 0.25, "dig_per_set": 3.25
        },
        {
            "id": 503, "team_id": "EXP", "name": "김세빈", "position": "MB", "number": 11,
            "sets_played": 4, "points": 15, "att_made": 8, "att_tried": 18, "att_pct": 44.44, "att_share": 10.59,
            "srv_made": 0, "srv_tried": 7, "blk_made": 7, "blk_tried": 18, "dig_made": 9, "dig_tried": 9,
            "rcv_made": 0, "rcv_tried": 1, "set_made": 0, "set_tried": 3, "errors": 1,
            "comment": "블로킹 7득점(38.89%) 대폭발! 공격 8/18(44.44%) 포함 총 15득점으로 네트를 완전히 장악.",
            "blk_pct": 38.89, "dig_pct": 100.0, "rcv_pct": 0.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 1.75, "dig_per_set": 2.25
        },
        {
            "id": 504, "team_id": "EXP", "name": "강소휘", "position": "OH", "number": 97,
            "sets_played": 4, "points": 10, "att_made": 10, "att_tried": 37, "att_pct": 27.03, "att_share": 21.76,
            "srv_made": 0, "srv_tried": 21, "blk_made": 0, "blk_tried": 13, "dig_made": 23, "dig_tried": 24,
            "rcv_made": 13, "rcv_tried": 26, "set_made": 0, "set_tried": 3, "errors": 3,
            "comment": "공격 10득점과 함께 디그 23개(95.8%), 리시브 13개로 살림꾼 활약. 팬 투표 BEST 플레이어 1위(38%).",
            "blk_pct": 0.0, "dig_pct": 95.83, "rcv_pct": 50.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 5.75
        },
        {
            "id": 505, "team_id": "EXP", "name": "김현지", "position": "MB", "number": 17,
            "sets_played": 4, "points": 4, "att_made": 2, "att_tried": 9, "att_pct": 22.22, "att_share": 5.29,
            "srv_made": 0, "srv_tried": 10, "blk_made": 2, "blk_tried": 19, "dig_made": 6, "dig_tried": 7,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 4,
            "comment": "블로킹 2개 포함 4득점. 중앙 유효 블로킹으로 후위 수비 부담 경감.",
            "blk_pct": 10.53, "dig_pct": 85.71, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.5, "dig_per_set": 1.5
        },
        {
            "id": 506, "team_id": "EXP", "name": "이윤정", "position": "S", "number": 6,
            "sets_played": 4, "points": 4, "att_made": 2, "att_tried": 6, "att_pct": 33.33, "att_share": 3.53,
            "srv_made": 1, "srv_tried": 15, "blk_made": 1, "blk_tried": 8, "dig_made": 19, "dig_tried": 21,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 42, "set_tried": 123, "errors": 1,
            "comment": "세트 성공 42개로 정밀한 공격 배분. 서브 1, 블로킹 1, 디그 19개(90.5%)로 공수 전방위 활약.",
            "blk_pct": 12.5, "dig_pct": 90.48, "rcv_pct": None, "set_pct": 34.15, "srv_pct": 6.67,
            "blk_per_set": 0.25, "dig_per_set": 4.75
        },
        {
            "id": 507, "team_id": "EXP", "name": "박정아", "position": "OH", "number": 9,
            "sets_played": 3, "points": 2, "att_made": 2, "att_tried": 2, "att_pct": 100.0, "att_share": 1.18,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 1, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "원포인트 스파이커로 2시도 2득점 100% 결정력! 팬 투표 2위(29%).",
            "blk_pct": 0.0, "dig_pct": None, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 508, "team_id": "EXP", "name": "문정원", "position": "L", "number": 12,
            "sets_played": 4, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 35, "dig_tried": 35,
            "rcv_made": 9, "rcv_tried": 19, "set_made": 5, "set_tried": 20, "errors": 0,
            "comment": "디그 35/35(100%) 무결점 수비! 코트를 뒤덮는 슈퍼 디그로 도로공사의 뒷문을 지탱.",
            "blk_pct": None, "dig_pct": 100.0, "rcv_pct": 47.37, "set_pct": 25.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 8.75
        },
        {
            "id": 509, "team_id": "EXP", "name": "김세인", "position": "OH", "number": 14,
            "sets_played": 2, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 1,
            "comment": "원포인트 서브 교체 출전.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 510, "team_id": "EXP", "name": "이수연", "position": "S", "number": 3,
            "sets_played": 2, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 2, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 1,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 6, "set_tried": 12, "errors": 0,
            "comment": "세터 백업 세트 성공 6개 기록.",
            "blk_pct": None, "dig_pct": 0.0, "rcv_pct": None, "set_pct": 50.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 511, "team_id": "EXP", "name": "박윤서", "position": "OH", "number": 7,
            "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 1, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 1,
            "comment": "원포인트 교체 투입.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 512, "team_id": "EXP", "name": "손혜진", "position": "S", "number": 2,
            "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 1, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "원포인트 서브 투입.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 513, "team_id": "EXP", "name": "유다은", "position": "MB", "number": 19,
            "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 1, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 1,
            "comment": "원포인트 블로커/서브 투입.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },

        # --- 흥국생명 선수단 (16명) ---
        {
            "id": 101, "team_id": "HKL", "name": "킨델란", "position": "OP", "number": 11,
            "sets_played": 4, "points": 23, "att_made": 22, "att_tried": 65, "att_pct": 33.85, "att_share": 38.69,
            "srv_made": 1, "srv_tried": 14, "blk_made": 0, "blk_tried": 9, "dig_made": 15, "dig_tried": 19,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 6, "errors": 8,
            "comment": "팀 최다 23득점(공격 22). 높은 점유율(38.69%) 속에서 도로공사 블로킹 벽에 맞서 분전.",
            "blk_pct": 0.0, "dig_pct": 78.95, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 7.14,
            "blk_per_set": 0.0, "dig_per_set": 3.75
        },
        {
            "id": 102, "team_id": "HKL", "name": "자스티스", "position": "OH", "number": 7,
            "sets_played": 4, "points": 16, "att_made": 13, "att_tried": 41, "att_pct": 31.71, "att_share": 24.4,
            "srv_made": 1, "srv_tried": 14, "blk_made": 2, "blk_tried": 4, "dig_made": 17, "dig_tried": 21,
            "rcv_made": 6, "rcv_tried": 22, "set_made": 1, "set_tried": 3, "errors": 2,
            "comment": "16득점(공격 13, 블로킹 2, 서브 1), 디그 17개. BEST 플레이어 1위(46%)의 공수 맹활약.",
            "blk_pct": 50.0, "dig_pct": 80.95, "rcv_pct": 27.27, "set_pct": 33.33, "srv_pct": 7.14,
            "blk_per_set": 0.5, "dig_per_set": 4.25
        },
        {
            "id": 104, "team_id": "HKL", "name": "정호영", "position": "MB", "number": 17,
            "sets_played": 4, "points": 11, "att_made": 4, "att_tried": 15, "att_pct": 26.67, "att_share": 8.93,
            "srv_made": 0, "srv_tried": 13, "blk_made": 7, "blk_tried": 25, "dig_made": 3, "dig_tried": 4,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 5, "errors": 1,
            "comment": "블로킹 7득점 폭발(7/25, 28.0%). 네트 중앙 높이에서 김세빈과 불꽃 튀는 블로킹 맞대결.",
            "blk_pct": 28.0, "dig_pct": 75.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 1.75, "dig_per_set": 0.75
        },
        {
            "id": 103, "team_id": "HKL", "name": "표승주", "position": "OH", "number": 19,
            "sets_played": 4, "points": 8, "att_made": 7, "att_tried": 22, "att_pct": 31.82, "att_share": 13.1,
            "srv_made": 0, "srv_tried": 8, "blk_made": 1, "blk_tried": 7, "dig_made": 7, "dig_tried": 9,
            "rcv_made": 1, "rcv_tried": 17, "set_made": 1, "set_tried": 4, "errors": 2,
            "comment": "8득점(공격 7, 블로킹 1). 팬 투표 2위(31%).",
            "blk_pct": 14.29, "dig_pct": 77.78, "rcv_pct": 5.88, "set_pct": 25.0, "srv_pct": 0.0,
            "blk_per_set": 0.25, "dig_per_set": 1.75
        },
        {
            "id": 105, "team_id": "HKL", "name": "이고은", "position": "S", "number": 3,
            "sets_played": 3, "points": 1, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 1, "blk_made": 1, "blk_tried": 6, "dig_made": 7, "dig_tried": 9,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 9, "set_tried": 44, "errors": 2,
            "comment": "블로킹 1득점, 세트 9개 성공, 디그 7개.",
            "blk_pct": 16.67, "dig_pct": 77.78, "rcv_pct": None, "set_pct": 20.45, "srv_pct": 0.0,
            "blk_per_set": 0.33, "dig_per_set": 2.33
        },
        {
            "id": 106, "team_id": "HKL", "name": "김수지", "position": "MB", "number": 4,
            "sets_played": 2, "points": 1, "att_made": 1, "att_tried": 4, "att_pct": 25.0, "att_share": 2.38,
            "srv_made": 0, "srv_tried": 7, "blk_made": 0, "blk_tried": 9, "dig_made": 4, "dig_tried": 5,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 1,
            "comment": "1득점, 디그 4개, 팬 투표 3위(7%).",
            "blk_pct": 0.0, "dig_pct": 80.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 2.0
        },
        {
            "id": 107, "team_id": "HKL", "name": "임혜림", "position": "MB", "number": 14,
            "sets_played": 2, "points": 1, "att_made": 0, "att_tried": 3, "att_pct": 0.0, "att_share": 1.79,
            "srv_made": 0, "srv_tried": 2, "blk_made": 1, "blk_tried": 7, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 1, "rcv_tried": 3, "set_made": 0, "set_tried": 2, "errors": 1,
            "comment": "블로킹 1득점 기록.",
            "blk_pct": 14.29, "dig_pct": None, "rcv_pct": 33.33, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.5, "dig_per_set": 0.0
        },
        {
            "id": 108, "team_id": "HKL", "name": "정윤주", "position": "OH", "number": 13,
            "sets_played": 2, "points": 1, "att_made": 1, "att_tried": 8, "att_pct": 12.5, "att_share": 4.76,
            "srv_made": 0, "srv_tried": 2, "blk_made": 0, "blk_tried": 2, "dig_made": 3, "dig_tried": 3,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 1,
            "comment": "공격 1득점, 디그 3개.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.5
        },
        {
            "id": 109, "team_id": "HKL", "name": "최은지", "position": "OH", "number": 9,
            "sets_played": 2, "points": 1, "att_made": 1, "att_tried": 8, "att_pct": 12.5, "att_share": 4.76,
            "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 3, "dig_made": 2, "dig_tried": 2,
            "rcv_made": 2, "rcv_tried": 7, "set_made": 1, "set_tried": 2, "errors": 1,
            "comment": "공격 1득점, 리시브 2개, 디그 2개.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": 28.57, "set_pct": 50.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.0
        },
        {
            "id": 110, "team_id": "HKL", "name": "고민지", "position": "L", "number": 8,
            "sets_played": 4, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 15, "dig_tried": 19,
            "rcv_made": 10, "rcv_tried": 37, "set_made": 4, "set_tried": 11, "errors": 0,
            "comment": "디그 15개(78.95%), 리시브 10개로 후위 수비 담당.",
            "blk_pct": None, "dig_pct": 78.95, "rcv_pct": 27.03, "set_pct": 36.36, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 3.75
        },
        {
            "id": 111, "team_id": "HKL", "name": "이나연", "position": "S", "number": 6,
            "sets_played": 4, "points": 0, "att_made": 0, "att_tried": 2, "att_pct": 0.0, "att_share": 1.19,
            "srv_made": 0, "srv_tried": 14, "blk_made": 0, "blk_tried": 6, "dig_made": 12, "dig_tried": 14,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 24, "set_tried": 73, "errors": 4,
            "comment": "세트 24개 성공, 디그 12/14(85.71%).",
            "blk_pct": 0.0, "dig_pct": 85.71, "rcv_pct": None, "set_pct": 32.88, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 3.0
        },
        {
            "id": 112, "team_id": "HKL", "name": "박수연", "position": "OH", "number": 15,
            "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 4, "blk_made": 0, "blk_tried": 0, "dig_made": 5, "dig_tried": 5,
            "rcv_made": 3, "rcv_tried": 5, "set_made": 0, "set_tried": 3, "errors": 1,
            "comment": "디그 5개 100%, 리시브 3개.",
            "blk_pct": None, "dig_pct": 100.0, "rcv_pct": 60.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.67
        },
        {
            "id": 113, "team_id": "HKL", "name": "신연경", "position": "L", "number": 5,
            "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 4, "dig_tried": 5,
            "rcv_made": 0, "rcv_tried": 1, "set_made": 0, "set_tried": 3, "errors": 0,
            "comment": "디그 4개 기록.",
            "blk_pct": None, "dig_pct": 80.0, "rcv_pct": 0.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.33
        },
        {
            "id": 114, "team_id": "HKL", "name": "박혜진", "position": "S", "number": 2,
            "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 2, "blk_made": 0, "blk_tried": 1, "dig_made": 3, "dig_tried": 3,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 4, "set_tried": 15, "errors": 0,
            "comment": "세트 4개 성공, 디그 3개 100%.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 26.67, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 3.0
        },
        {
            "id": 115, "team_id": "HKL", "name": "이신영", "position": "OH", "number": 16,
            "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 1, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 1, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "교체 출전.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": 0.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 116, "team_id": "HKL", "name": "김다은", "position": "OH", "number": 10,
            "sets_played": 0, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
            "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "웜업존 대기.",
            "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        }
    ],
    "summary": {
        "EXP": {
            "team_id": "EXP",
            "att_made": 63,
            "att_tried": 170,
            "att_pct": 37.1,
            "blk_made": 11,
            "blk_tried": 77,
            "srv_made": 4,
            "srv_tried": 99,
            "dig_made": 112,
            "dig_tried": 120,
            "dig_pct": 93.33,
            "rcv_made": 34,
            "rcv_tried": 77,
            "rcv_pct": 44.16,
            "set_made": 56,
            "set_tried": 163,
            "opp_errors": 24,
            "errors": 21
        },
        "HKL": {
            "team_id": "HKL",
            "att_made": 49,
            "att_tried": 168,
            "att_pct": 29.2,
            "blk_made": 12,
            "blk_tried": 70,
            "srv_made": 2,
            "srv_tried": 85,
            "dig_made": 97,
            "dig_tried": 115,
            "dig_pct": 84.35,
            "rcv_made": 23,
            "rcv_tried": 90,
            "rcv_pct": 25.56,
            "set_made": 44,
            "set_tried": 160,
            "opp_errors": 21,
            "errors": 24
        }
    },
    "best_players": {
        "EXP": [
            {"rank": 1, "name": "강소휘", "votes": 182, "pct": 38, "pos": "OH"},
            {"rank": 2, "name": "박정아", "votes": 141, "pct": 29, "pos": "OH"},
            {"rank": 3, "name": "모마", "votes": 40, "pct": 8, "pos": "OP"}
        ],
        "HKL": [
            {"rank": 1, "name": "자스티스", "votes": 166, "pct": 46, "pos": "OH"},
            {"rank": 2, "name": "표승주", "votes": 113, "pct": 31, "pos": "OH"},
            {"rank": 3, "name": "김수지", "votes": 27, "pct": 7, "pos": "MB"}
        ]
    },
    "key_players": {
        "points": {"EXP": {"name": "모마", "val": 26}, "HKL": {"name": "킨델란", "val": 23}},
        "attacks": {"EXP": {"name": "모마", "val": 23}, "HKL": {"name": "킨델란", "val": 22}},
        "serves": {"EXP": {"name": "모마", "val": 3}, "HKL": {"name": "자스티스", "val": 1}},
        "blocks": {"EXP": {"name": "김세빈", "val": 7}, "HKL": {"name": "정호영", "val": 7}},
        "digs": {"EXP": {"name": "문정원", "val": 35}, "HKL": {"name": "자스티스", "val": 17}},
        "receives": {"EXP": {"name": "강소휘", "val": 13}, "HKL": {"name": "고민지", "val": 10}},
        "sets": {"EXP": {"name": "이윤정", "val": 42}, "HKL": {"name": "이나연", "val": 24}}
    },
    "sets": [
        {"set_no": 1, "kgc_score": 27, "hdec_score": 27, "hkl_score": 27, "ibk_score": 29, "exp_score": 29, "winner": "EXP", "score_home": 29, "score_away": 27},
        {"set_no": 2, "kgc_score": 19, "hdec_score": 19, "hkl_score": 19, "ibk_score": 25, "exp_score": 25, "winner": "EXP", "score_home": 25, "score_away": 19},
        {"set_no": 3, "kgc_score": 25, "hdec_score": 25, "hkl_score": 25, "ibk_score": 23, "exp_score": 23, "winner": "HKL", "score_home": 23, "score_away": 25},
        {"set_no": 4, "kgc_score": 13, "hdec_score": 13, "hkl_score": 13, "ibk_score": 25, "exp_score": 25, "winner": "EXP", "score_home": 25, "score_away": 13}
    ],
    "lineups": {
        "EXP": {
            "S": 506,
            "OH1": 504,
            "OH2": 502,
            "OP": 501,
            "MB1": 503,
            "MB2": 505,
            "L": 508
        },
        "HKL": {
            "S": 111,
            "OH1": 102,
            "OH2": 103,
            "OP": 101,
            "MB1": 104,
            "MB2": 106,
            "L": 110
        }
    },
    "scenarios": [
        {
            "id": 1,
            "code": "EXP_MOMA_POWER",
            "title": "⚡ 모마 26득점 폭발 & 이윤정 토스워크",
            "subtitle": "이윤정의 정밀한 세트와 모마의 압도적 고공 강타로 세트스코어 3-1 승리",
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
                    "tags": ["#모마", "#26득점", "#양팀최다"],
                    "text": "11월 8일 도로공사 vs 흥국생명. 모마의 26득점 대폭발과 김세빈의 블로킹 7득점 승부처를 분석합니다."
                },
                {
                    "name": "서브 & 리시브", "dur": 1300,
                    "ball": [{"from": ["def", -4, 78], "to": ["atk", 28, 45], "h": 30, "delay": 0, "end": 1}],
                    "moves": [{"who": "atk.S", "to": [83, 60], "delay": 0.15, "end": 0.9, "trail": True}],
                    "focus": "atk.L",
                    "tags": ["#문정원디그", "#리시브"],
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
                    "tags": ["#모마폭격", "#백어택"],
                    "text": "모마가 상대 2인 블로킹을 뚫고 대각 코트에 내리꽂으며 득점을 올립니다!"
                }
            ]
        },
        {
            "id": 2,
            "code": "EXP_SEBIN_WALL",
            "title": "🛡️ 김세빈 7블로킹 철벽 & 문정원 35디그",
            "subtitle": "김세빈의 결정적 7블로킹과 문정원의 100% 디그 성공률로 흥국생명 추격 차단",
            "attack_team": "EXP",
            "sort_order": 1,
            "phases": [
                {
                    "name": "흥국생명 공격 전개", "dur": 1300,
                    "moves": [
                        {"who": "atk.MBF", "to": [85, 50], "delay": 0.2, "end": 0.8, "trail": True},
                        {"who": "def.Z4", "to": [80, 20], "delay": 0.1, "end": 0.7}
                    ],
                    "focus": "atk.MBF",
                    "tags": ["#김세빈블로킹", "#7득점"],
                    "text": "흥국생명 킨델란과 정호영의 오픈 공격을 김세빈이 네트 앞에서 완벽히 리딩합니다."
                },
                {
                    "name": "셧다운 블로킹", "dur": 1400,
                    "ball": [
                        {"from": ["def", 80, 20], "to": ["atk", 86, 50], "h": 15, "delay": 0, "end": 0.45},
                        {"from": ["atk", 86, 50], "to": ["def", 75, 45], "h": 8, "delay": 0.46, "end": 0.85}
                    ],
                    "moves": [
                        {"who": "atk.MBF", "to": [87, 50], "delay": 0.35, "end": 0.55},
                        {"who": "def.Z3", "to": [75, 45], "delay": 0.5, "end": 0.9}
                    ],
                    "focus": "atk.MBF",
                    "tags": ["#김세빈셧다운", "#문정원35디그"],
                    "text": "김세빈의 단독 블로킹 셧다운! 문정원의 디그와 김세빈의 블로킹 7개가 경기 승부를 갈랐습니다."
                }
            ]
        }
    ],
    "rallies": rallies,
    "set_stats": [
        # 1세트 핵심 기록
        {"set_no": 1, "player_id": 501, "att_made": 7, "att_tried": 14, "srv_made": 1, "srv_tried": 4, "blk_made": 0, "blk_tried": 2, "dig_made": 2, "dig_tried": 2, "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 2, "errors": 2, "points": 8},
        {"set_no": 1, "player_id": 503, "att_made": 2, "att_tried": 4, "srv_made": 0, "srv_tried": 2, "blk_made": 2, "blk_tried": 5, "dig_made": 3, "dig_tried": 3, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 0, "points": 4},
        {"set_no": 1, "player_id": 101, "att_made": 6, "att_tried": 18, "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 2, "dig_made": 4, "dig_tried": 5, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 2, "errors": 2, "points": 6},
        {"set_no": 1, "player_id": 104, "att_made": 1, "att_tried": 3, "srv_made": 0, "srv_tried": 3, "blk_made": 2, "blk_tried": 7, "dig_made": 1, "dig_tried": 1, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 0, "points": 3},

        # 2세트 핵심 기록
        {"set_no": 2, "player_id": 501, "att_made": 6, "att_tried": 13, "srv_made": 1, "srv_tried": 4, "blk_made": 0, "blk_tried": 3, "dig_made": 2, "dig_tried": 2, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 2, "errors": 1, "points": 7},
        {"set_no": 2, "player_id": 502, "att_made": 5, "att_tried": 11, "srv_made": 0, "srv_tried": 6, "blk_made": 1, "blk_tried": 3, "dig_made": 4, "dig_tried": 4, "rcv_made": 3, "rcv_tried": 8, "set_made": 0, "set_tried": 2, "errors": 1, "points": 6},
        {"set_no": 2, "player_id": 101, "att_made": 5, "att_tried": 15, "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 2, "dig_made": 3, "dig_tried": 4, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2, "points": 5},

        # 3세트 핵심 기록
        {"set_no": 3, "player_id": 101, "att_made": 6, "att_tried": 17, "srv_made": 0, "srv_tried": 4, "blk_made": 0, "blk_tried": 2, "dig_made": 4, "dig_tried": 5, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2, "points": 6},
        {"set_no": 3, "player_id": 102, "att_made": 4, "att_tried": 12, "srv_made": 1, "srv_tried": 5, "blk_made": 1, "blk_tried": 2, "dig_made": 5, "dig_tried": 6, "rcv_made": 2, "rcv_tried": 6, "set_made": 1, "set_tried": 1, "errors": 0, "points": 6},
        {"set_no": 3, "player_id": 501, "att_made": 5, "att_tried": 13, "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 2, "dig_made": 1, "dig_tried": 1, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 1, "points": 5},

        # 4세트 핵심 기록
        {"set_no": 4, "player_id": 501, "att_made": 5, "att_tried": 13, "srv_made": 1, "srv_tried": 4, "blk_made": 0, "blk_tried": 3, "dig_made": 2, "dig_tried": 2, "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 2, "errors": 1, "points": 6},
        {"set_no": 4, "player_id": 503, "att_made": 3, "att_tried": 6, "srv_made": 0, "srv_tried": 2, "blk_made": 3, "blk_tried": 6, "dig_made": 3, "dig_tried": 3, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0, "points": 6},
        {"set_no": 4, "player_id": 101, "att_made": 5, "att_tried": 15, "srv_made": 1, "srv_tried": 4, "blk_made": 0, "blk_tried": 3, "dig_made": 4, "dig_tried": 5, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 2, "errors": 2, "points": 6}
    ]
}

# 세트 라인업 매핑
sets_list: List[Dict[str, Any]] = full_data_1108["sets"]
lineups_dict: Dict[str, Any] = full_data_1108["lineups"]
full_data_1108["set_lineups"] = {
    int(s["set_no"]): lineups_dict for s in sets_list
}

set_stats_list: List[Dict[str, Any]] = full_data_1108["set_stats"]
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
        _row["comment"] = " ".join(_parts) or "세트 활약."

scenarios_list: List[Dict[str, Any]] = full_data_1108["scenarios"]
for _sc in scenarios_list:
    for _ph in _sc.get("phases", []):
        _ph.setdefault("moves", [])
        _ph.setdefault("tags", [])

js_code = f"// 11월 8일 한국도로공사 vs 흥국생명 전 전술 분석 데이터\n"
js_code += f"window.BOOTSTRAP_1108 = {json.dumps(full_data_1108, ensure_ascii=False, indent=2)};\n\n"
js_code += """window.MATCHES = window.MATCHES || {};
if (window.BOOTSTRAP) {
  window.MATCHES['2026-11-07'] = window.BOOTSTRAP;
  window.MATCHES['2024-11-07'] = window.BOOTSTRAP;
}
if (window.BOOTSTRAP_1104) {
  window.MATCHES['2026-11-04'] = window.BOOTSTRAP_1104;
  window.MATCHES['2024-11-04'] = window.BOOTSTRAP_1104;
}
if (window.BOOTSTRAP_1103) {
  window.MATCHES['2026-11-03'] = window.BOOTSTRAP_1103;
  window.MATCHES['2024-11-03'] = window.BOOTSTRAP_1103;
}
window.MATCHES['2026-11-08'] = window.BOOTSTRAP_1108;
window.MATCHES['2024-11-08'] = window.BOOTSTRAP_1108;
"""

Path(ROOT / "js" / "data_1108.js").write_text(js_code, encoding="utf-8")
Path(ROOT / "static" / "js" / "data_1108.js").write_text(js_code, encoding="utf-8")
print(f"Generated data_1108.js with {len(rallies)} rallies successfully!")
