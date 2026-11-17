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
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent

# 한국도로공사 선수단 (원정)
EXP_PLAYERS = {
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
    "김현아": (515, 13, "MB", "EXP"),
    "유다은": (513, 20, "MB", "EXP"),
    "박윤서": (514, 1, "OH", "EXP"),
}

# 현대건설 선수단 (홈)
HDEC_PLAYERS = {
    "메가": (201, 99, "OP", "HDEC"),
    "조던": (202, 18, "OH", "HDEC"),
    "이채영": (203, 17, "OH", "HDEC"),
    "강서우": (204, 11, "MB", "HDEC"),
    "김희진": (205, 4, "MB", "HDEC"),
    "이예림": (206, 7, "OH", "HDEC"),
    "김다인": (207, 3, "S", "HDEC"),
    "배유나": (208, 12, "MB", "HDEC"),
    "구솔": (209, 6, "S", "HDEC"),
    "김연견": (210, 8, "L", "HDEC"),
    "이영주": (211, 5, "L", "HDEC"),
    "나현수": (212, 15, "OP", "HDEC"),
    "한미르": (213, 1, "OH", "HDEC"),
    "이한비": (214, 16, "OH", "HDEC"),
}

ALL_PLAYERS = {**EXP_PLAYERS, **HDEC_PLAYERS}

def get_p_info(pid: int) -> Tuple[str, int, str, str]:
    for name, info in ALL_PLAYERS.items():
        if info[0] == pid:
            return name, info[1], info[2], info[3]
    return "선수", 0, "OH", "EXP"

def make_rally(set_no: int, r_no: int, server_id: int, rcv_id: int, set_id: int, atk_id: int,
               sh: int, sa: int, action: str = "오픈", is_kill: bool = True, blk_id: int = None,
               is_serve_ace: bool = False, is_error: bool = False) -> Dict[str, Any]:
    s_name, s_num, _, s_t = get_p_info(server_id)
    r_name, r_num, _, r_t = get_p_info(rcv_id)
    st_name, st_num, _, st_t = get_p_info(set_id)
    a_name, a_num, _, a_t = get_p_info(atk_id)

    events = []
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
    step = 0

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
        # 득점 팀 결정
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
                r = make_rally(set_no, i, 501, 210, 506, 501, is_serve_ace=True)
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
        # 한국도로공사 (원정 승리팀)
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
            "id": 201, "team_id": "HDEC", "name": "메가", "position": "OP", "number": 99,
            "sets_played": 3, "points": 17, "att_made": 16, "att_tried": 39, "att_pct": 41.03, "att_share": 39.8,
            "srv_made": 0, "srv_tried": 9, "blk_made": 1, "blk_tried": 2, "dig_made": 6, "dig_tried": 7,
            "rcv_made": 0, "rcv_tried": 1, "set_made": 1, "set_tried": 4, "errors": 7,
            "comment": "공격 16/39 17득점으로 양 팀 최다 득점 타이를 기록했으나 범실 7개로 고전. BEST 2위(14%).",
            "blk_pct": 50.0, "dig_pct": 85.71, "rcv_pct": 0.0, "set_pct": 25.0, "srv_pct": 0.0,
            "blk_per_set": 0.33, "dig_per_set": 2.0
        },
        {
            "id": 202, "team_id": "HDEC", "name": "조던", "position": "OH", "number": 18,
            "sets_played": 3, "points": 15, "att_made": 15, "att_tried": 30, "att_pct": 50.0, "att_share": 30.61,
            "srv_made": 0, "srv_tried": 7, "blk_made": 0, "blk_tried": 6, "dig_made": 5, "dig_tried": 5,
            "rcv_made": 2, "rcv_tried": 13, "set_made": 0, "set_tried": 1, "errors": 6,
            "comment": "공격 15/30(50.0%) 15득점, 디그 5/5로 분전.",
            "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": 15.38, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 1.67
        },
        {
            "id": 203, "team_id": "HDEC", "name": "이채영", "position": "OH", "number": 17,
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
            "id": 206, "team_id": "HDEC", "name": "이예림", "position": "OH", "number": 7,
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
            "id": 208, "team_id": "HDEC", "name": "배유나", "position": "MB", "number": 12,
            "sets_played": 2, "points": 1, "att_made": 1, "att_tried": 2, "att_pct": 50.0, "att_share": 2.04,
            "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 5, "dig_made": 0, "dig_tried": 0,
            "rcv_made": 0, "rcv_tried": 2, "set_made": 0, "set_tried": 0, "errors": 0,
            "comment": "속공 1득점.",
            "blk_pct": 0.0, "dig_pct": None, "rcv_pct": 0.0, "set_pct": 0.0, "srv_pct": 0.0,
            "blk_per_set": 0.0, "dig_per_set": 0.0
        },
        {
            "id": 209, "team_id": "HDEC", "name": "구솔", "position": "S", "number": 6,
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
    "key_players": [
        {
            "label": "득점",
            "home": {"name": "메가", "value": "17"},
            "away": {"name": "모마", "value": "17"}
        },
        {
            "label": "공격",
            "home": {"name": "메가", "value": "16"},
            "away": {"name": "모마", "value": "16"}
        },
        {
            "label": "서브",
            "home": {"name": "강서우", "value": "1"},
            "away": {"name": "김세빈", "value": "2"}
        },
        {
            "label": "블로킹",
            "home": {"name": "강서우", "value": "1"},
            "away": {"name": "김세빈", "value": "2"}
        },
        {
            "label": "디그",
            "home": {"name": "김다인", "value": "10"},
            "away": {"name": "문정원", "value": "14"}
        },
        {
            "label": "리시브",
            "home": {"name": "이영주", "value": "10"},
            "away": {"name": "강소휘", "value": "6"}
        },
        {
            "label": "세트",
            "home": {"name": "김다인", "value": "29"},
            "away": {"name": "이윤정", "value": "40"}
        }
    ],
    "best_players": [
        {
            "team": "현대건설",
            "rank": 1,
            "name": "김희진",
            "votes": 118,
            "pct": 44,
            "desc": "서브에이스 및 알토란 활약 (44% 최다 득표)"
        },
        {
            "team": "현대건설",
            "rank": 2,
            "name": "메가",
            "votes": 38,
            "pct": 14,
            "desc": "17득점 폭격 (14%)"
        },
        {
            "team": "현대건설",
            "rank": 3,
            "name": "이예림",
            "votes": 37,
            "pct": 14,
            "desc": "리시브 10개 및 수비 분전 (14%)"
        },
        {
            "team": "한국도로공사",
            "rank": 1,
            "name": "강소휘",
            "votes": 192,
            "pct": 48,
            "desc": "공격 12득점 & 디그 7개 살림꾼 활약 (48% 압도적 1위)"
        },
        {
            "team": "한국도로공사",
            "rank": 2,
            "name": "문정원",
            "votes": 65,
            "pct": 16,
            "desc": "디그 14개 명품 수비 (16%)"
        },
        {
            "team": "한국도로공사",
            "rank": 3,
            "name": "박정아",
            "votes": 45,
            "pct": 11,
            "desc": "원포인트 스파이커 100% 득점 (11%)"
        }
    ],
    "rallies": all_rallies,
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

def export_js():
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
    # 루트 js/data_1116.js 및 static/js/data_1116.js 둘 다 저장
    js_path = ROOT / "js" / "data_1116.js"
    static_js_path = ROOT / "static" / "js" / "data_1116.js"
    js_path.write_text(js_content, encoding="utf-8")
    static_js_path.write_text(js_content, encoding="utf-8")
    print(f"Generated data_1116.js with {len(all_rallies)} rallies successfully!")

if __name__ == "__main__":
    export_js()
