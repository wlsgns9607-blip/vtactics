# -*- coding: utf-8 -*-
"""
11월 22일 현대건설 vs 흥국생명 V-리그 전술 분석 데이터 생성기
- 현대건설 (홈) vs 흥국생명 (어웨이) (3:0 현대건설 완승, 78 : 62)
  * 1세트: 현대건설 25 - 19 흥국생명
  * 2세트: 현대건설 25 - 17 흥국생명
  * 3세트: 현대건설 28 - 26 흥국생명
- 블로킹 14-7 높이의 압도, 배유나 10점(블로킹 6점, 공성 100%), 메가 18점, 조던 16점
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent

# 현대건설 선수단 (홈)
HDEC_PLAYERS = {
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
    "정지윤": (215, 17, "OH", "HDEC"),
    "정가영": (216, 7, "OH", "HDEC"),
}

# 흥국생명 선수단 (원정)
HKL_PLAYERS = {
    "킨델란": (101, 23, "OP", "HKL"),
    "자스티스": (102, 2, "OH", "HKL"),
    "정윤주": (108, 14, "OH", "HKL"),
    "정호영": (104, 17, "MB", "HKL"),
    "김다은": (116, 4, "OH", "HKL"),
    "박혜진": (114, 13, "S", "HKL"),
    "이고은": (105, 6, "S", "HKL"),
    "김수지": (106, 11, "MB", "HKL"),
    "표승주": (103, 19, "OH", "HKL"),
    "임혜림": (107, 14, "MB", "HKL"),
    "고민지": (110, 16, "L", "HKL"),
    "신연경": (113, 3, "L", "HKL"),
    "박수연": (112, 20, "OH", "HKL"),
    "이나연": (111, 33, "S", "HKL"),
    "이신영": (115, 18, "OH", "HKL"),
    "최은지": (109, 9, "OH", "HKL"),
}

# 1. 경기 기본 정보
match_info = {
    "date": "2024-11-22",
    "alt_date": "2026-11-22",
    "day": "금",
    "time": "19:00",
    "league": "2024-2025 V-리그 여자부 2R",
    "venue": "수원실내체육관",
    "title": "[현대건설 vs 흥국생명] V-리그 전술 분석 & 리뷰 판",
    "home_team": "HDEC",
    "away_team": "HKL",
    "result_text": "현대건설 3 : 0 흥국생명 (세트스코어 3-0 현대건설 완승)",
    "set_scores": "25:19, 25:17, 28:26",
    "total_score": "78 : 62"
}

teams = [
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
        "id": "HKL",
        "name": "흥국생명 핑크스파이더스",
        "short_name": "흥국생명",
        "primary_color": "#EC008C",
        "accent_color": "#FF69B4",
        "bg_color": "#2A1424",
        "is_home": 0
    }
]

# 2. 선수 목록 (유저 제공 공식 기록표 100% 반영)
players = [
    # 현대건설
    {
        "id": 201, "team_id": "HDEC", "name": "메가", "position": "OP", "number": 88,
        "sets_played": 3, "points": 18, "att_made": 14, "att_tried": 35, "att_pct": 40.0, "att_share": 33.33,
        "srv_made": 1, "srv_tried": 11, "blk_made": 3, "blk_tried": 7, "dig_made": 9, "dig_tried": 11,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 2, "errors": 2,
        "comment": "팀 내 최다 18득점(공격 14, 블로킹 3, 서브 1) 폭격. 공격 점유율 33.3% 책임지며 승리 견인.",
        "blk_pct": 42.86, "dig_pct": 81.82, "rcv_pct": None, "set_pct": 50.0, "srv_pct": 9.09, "blk_per_set": 1.0, "dig_per_set": 3.0
    },
    {
        "id": 202, "team_id": "HDEC", "name": "조던", "position": "OH", "number": 21,
        "sets_played": 3, "points": 16, "att_made": 15, "att_tried": 36, "att_pct": 41.67, "att_share": 34.29,
        "srv_made": 1, "srv_tried": 5, "blk_made": 0, "blk_tried": 9, "dig_made": 4, "dig_tried": 4,
        "rcv_made": 2, "rcv_tried": 10, "set_made": 1, "set_tried": 4, "errors": 4,
        "comment": "공격 15점(41.67%) 포함 16득점. 메가와 함께 좌우 쌍포 화력 지원으로 흥국생명 코트 맹폭격.",
        "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": 20.0, "set_pct": 25.0, "srv_pct": 20.0, "blk_per_set": 0.0, "dig_per_set": 1.33
    },
    {
        "id": 208, "team_id": "HDEC", "name": "배유나", "position": "MB", "number": 10,
        "sets_played": 3, "points": 10, "att_made": 3, "att_tried": 3, "att_pct": 100.0, "att_share": 2.86,
        "srv_made": 1, "srv_tried": 13, "blk_made": 6, "blk_tried": 17, "dig_made": 3, "dig_tried": 4,
        "rcv_made": 0, "rcv_tried": 1, "set_made": 1, "set_tried": 3, "errors": 1,
        "comment": "블로킹 무려 6개 폭발! 공격 3시도 3성공 100% 성공률로 10득점 맹활약. 경기 MVP(팡팡 플레이어) 선정.",
        "blk_pct": 35.29, "dig_pct": 75.0, "rcv_pct": 0.0, "set_pct": 33.33, "srv_pct": 7.69, "blk_per_set": 2.0, "dig_per_set": 1.0
    },
    {
        "id": 206, "team_id": "HDEC", "name": "이예림", "position": "OH", "number": 1,
        "sets_played": 3, "points": 5, "att_made": 4, "att_tried": 9, "att_pct": 44.44, "att_share": 8.57,
        "srv_made": 0, "srv_tried": 10, "blk_made": 1, "blk_tried": 4, "dig_made": 15, "dig_tried": 19,
        "rcv_made": 7, "rcv_tried": 20, "set_made": 2, "set_tried": 7, "errors": 0,
        "comment": "디그 15개 성공(78.9%), 리시브 7개 정확 및 공격 4득점. 무실 범실(0개)의 완벽한 수비 살림꾼.",
        "blk_pct": 25.0, "dig_pct": 78.95, "rcv_pct": 35.0, "set_pct": 28.57, "srv_pct": 0.0, "blk_per_set": 0.33, "dig_per_set": 5.0
    },
    {
        "id": 215, "team_id": "HDEC", "name": "정지윤", "position": "OH", "number": 17,
        "sets_played": 3, "points": 4, "att_made": 3, "att_tried": 11, "att_pct": 27.27, "att_share": 10.48,
        "srv_made": 0, "srv_tried": 0, "blk_made": 1, "blk_tried": 5, "dig_made": 1, "dig_tried": 1,
        "rcv_made": 0, "rcv_tried": 3, "set_made": 1, "set_tried": 2, "errors": 1,
        "comment": "공격 3득점 및 유효 블로킹 지원으로 로테이션 공백 완벽 메움.",
        "blk_pct": 20.0, "dig_pct": 100.0, "rcv_pct": 0.0, "set_pct": 50.0, "srv_pct": 0.0, "blk_per_set": 0.33, "dig_per_set": 0.33
    },
    {
        "id": 205, "team_id": "HDEC", "name": "김희진", "position": "MB", "number": 4,
        "sets_played": 3, "points": 3, "att_made": 0, "att_tried": 8, "att_pct": 0.0, "att_share": 7.62,
        "srv_made": 0, "srv_tried": 15, "blk_made": 3, "blk_tried": 7, "dig_made": 6, "dig_tried": 6,
        "rcv_made": 1, "rcv_tried": 1, "set_made": 0, "set_tried": 1, "errors": 3,
        "comment": "블로킹 3개 및 날카로운 목적타 서브 15회로 상대 리시브 라인을 흔듦.",
        "blk_pct": 42.86, "dig_pct": 100.0, "rcv_pct": 100.0, "set_pct": 0.0, "srv_pct": 0.0, "blk_per_set": 1.0, "dig_per_set": 2.0
    },
    {
        "id": 207, "team_id": "HDEC", "name": "김다인", "position": "S", "number": 3,
        "sets_played": 3, "points": 2, "att_made": 1, "att_tried": 3, "att_pct": 33.33, "att_share": 2.86,
        "srv_made": 1, "srv_tried": 17, "blk_made": 0, "blk_tried": 5, "dig_made": 10, "dig_tried": 11,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 29, "set_tried": 80, "errors": 1,
        "comment": "세트 29개 성공(36.25%), 디그 10개 및 깜짝 패스페인트 1득점, 서브 1득점으로 경기 완벽 조율.",
        "blk_pct": 0.0, "dig_pct": 90.91, "rcv_pct": None, "set_pct": 36.25, "srv_pct": 5.88, "blk_per_set": 0.0, "dig_per_set": 3.33
    },
    {
        "id": 203, "team_id": "HDEC", "name": "이채영", "position": "OH", "number": 2,
        "sets_played": 3, "points": 1, "att_made": 0, "att_tried": 0, "att_pct": 0.0, "att_share": 0.0,
        "srv_made": 1, "srv_tried": 4, "blk_made": 0, "blk_tried": 0, "dig_made": 3, "dig_tried": 3,
        "rcv_made": 3, "rcv_tried": 5, "set_made": 0, "set_tried": 2, "errors": 0,
        "comment": "원포인트 서버로 투입되어 서브 에이스 1개 및 디그 3개로 알토란 활약.",
        "blk_pct": 0.0, "dig_pct": 100.0, "rcv_pct": 60.0, "set_pct": 0.0, "srv_pct": 25.0, "blk_per_set": 0.0, "dig_per_set": 1.0
    },
    {
        "id": 210, "team_id": "HDEC", "name": "김연견", "position": "L", "number": 8,
        "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
        "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 10, "dig_tried": 12,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 4, "errors": 0,
        "comment": "디그 10개 성공(83.3%)으로 후방 수비를 철벽 방어.",
        "blk_pct": None, "dig_pct": 83.33, "rcv_pct": None, "set_pct": 0.0, "srv_pct": None, "blk_per_set": 0.0, "dig_per_set": 3.33
    },
    {
        "id": 211, "team_id": "HDEC", "name": "이영주", "position": "L", "number": 5,
        "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
        "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 6, "dig_tried": 7,
        "rcv_made": 7, "rcv_tried": 13, "set_made": 4, "set_tried": 7, "errors": 0,
        "comment": "리시브 7개 정확(53.8%), 디그 6개, 2단 연결 4개로 팀 리시브 라인 안정화.",
        "blk_pct": None, "dig_pct": 85.71, "rcv_pct": 53.85, "set_pct": 57.14, "srv_pct": None, "blk_per_set": 0.0, "dig_per_set": 2.0
    },
    {
        "id": 209, "team_id": "HDEC", "name": "구솔", "position": "S", "number": 99,
        "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
        "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
        "comment": "1세트 교체 투입.",
        "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": None, "blk_per_set": 0.0, "dig_per_set": 0.0
    },
    {
        "id": 216, "team_id": "HDEC", "name": "정가영", "position": "OH", "number": 7,
        "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
        "srv_made": 0, "srv_tried": 1, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
        "comment": "원포인트 서버 출전.",
        "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": 0.0, "blk_per_set": 0.0, "dig_per_set": 0.0
    },

    # 흥국생명
    {
        "id": 101, "team_id": "HKL", "name": "킨델란", "position": "OP", "number": 23,
        "sets_played": 3, "points": 21, "att_made": 19, "att_tried": 54, "att_pct": 35.19, "att_share": 45.0,
        "srv_made": 0, "srv_tried": 7, "blk_made": 2, "blk_tried": 10, "dig_made": 9, "dig_tried": 10,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 5, "errors": 5,
        "comment": "양 팀 최다 21득점(공격 19, 블로킹 2). 공격 점유율 45%를 전담하며 고군분투.",
        "blk_pct": 20.0, "dig_pct": 90.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0, "blk_per_set": 0.67, "dig_per_set": 3.0
    },
    {
        "id": 102, "team_id": "HKL", "name": "자스티스", "position": "OH", "number": 2,
        "sets_played": 3, "points": 8, "att_made": 4, "att_tried": 23, "att_pct": 17.39, "att_share": 19.17,
        "srv_made": 3, "srv_tried": 14, "blk_made": 1, "blk_tried": 7, "dig_made": 11, "dig_tried": 13,
        "rcv_made": 7, "rcv_tried": 21, "set_made": 3, "set_tried": 8, "errors": 3,
        "comment": "서브 에이스 3개 폭발 및 디그 11개, 8득점으로 살림꾼 역할.",
        "blk_pct": 14.29, "dig_pct": 84.62, "rcv_pct": 33.33, "set_pct": 37.5, "srv_pct": 21.43, "blk_per_set": 0.33, "dig_per_set": 3.67
    },
    {
        "id": 108, "team_id": "HKL", "name": "정윤주", "position": "OH", "number": 14,
        "sets_played": 2, "points": 8, "att_made": 7, "att_tried": 14, "att_pct": 50.0, "att_share": 11.67,
        "srv_made": 0, "srv_tried": 3, "blk_made": 1, "blk_tried": 6, "dig_made": 4, "dig_tried": 5,
        "rcv_made": 3, "rcv_tried": 7, "set_made": 0, "set_tried": 3, "errors": 0,
        "comment": "공격 7득점(50.0%)의 고효율 스파이크로 2세트부터 공격 활력 불어넣음.",
        "blk_pct": 16.67, "dig_pct": 80.0, "rcv_pct": 42.86, "set_pct": 0.0, "srv_pct": 0.0, "blk_per_set": 0.5, "dig_per_set": 2.0
    },
    {
        "id": 104, "team_id": "HKL", "name": "정호영", "position": "MB", "number": 17,
        "sets_played": 3, "points": 4, "att_made": 3, "att_tried": 7, "att_pct": 42.86, "att_share": 5.83,
        "srv_made": 0, "srv_tried": 9, "blk_made": 1, "blk_tried": 6, "dig_made": 3, "dig_tried": 3,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 3, "errors": 2,
        "comment": "속공 3득점 및 블로킹 1득점.",
        "blk_pct": 16.67, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0, "blk_per_set": 0.33, "dig_per_set": 1.0
    },
    {
        "id": 116, "team_id": "HKL", "name": "김다은", "position": "OH", "number": 4,
        "sets_played": 2, "points": 2, "att_made": 2, "att_tried": 11, "att_pct": 18.18, "att_share": 9.17,
        "srv_made": 0, "srv_tried": 3, "blk_made": 0, "blk_tried": 3, "dig_made": 1, "dig_tried": 2,
        "rcv_made": 4, "rcv_tried": 11, "set_made": 1, "set_tried": 4, "errors": 1,
        "comment": "공격 2득점, 리시브 4개 기록.",
        "blk_pct": 0.0, "dig_pct": 50.0, "rcv_pct": 36.36, "set_pct": 25.0, "srv_pct": 0.0, "blk_per_set": 0.0, "dig_per_set": 0.5
    },
    {
        "id": 114, "team_id": "HKL", "name": "박혜진", "position": "S", "number": 13,
        "sets_played": 2, "points": 2, "att_made": 1, "att_tried": 2, "att_pct": 50.0, "att_share": 1.67,
        "srv_made": 1, "srv_tried": 4, "blk_made": 0, "blk_tried": 0, "dig_made": 8, "dig_tried": 9,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 12, "set_tried": 37, "errors": 3,
        "comment": "서브 에이스 1개, 세트 12개, 디그 8개.",
        "blk_pct": None, "dig_pct": 88.89, "rcv_pct": None, "set_pct": 32.43, "srv_pct": 25.0, "blk_per_set": 0.0, "dig_per_set": 4.0
    },
    {
        "id": 105, "team_id": "HKL", "name": "이고은", "position": "S", "number": 6,
        "sets_played": 2, "points": 2, "att_made": 1, "att_tried": 1, "att_pct": 100.0, "att_share": 0.83,
        "srv_made": 0, "srv_tried": 5, "blk_made": 1, "blk_tried": 4, "dig_made": 4, "dig_tried": 5,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 17, "set_tried": 48, "errors": 0,
        "comment": "세트 17개 성공(35.42%) 및 블로킹 1득점, 깜짝 오픈 1득점.",
        "blk_pct": 25.0, "dig_pct": 80.0, "rcv_pct": None, "set_pct": 35.42, "srv_pct": 0.0, "blk_per_set": 0.5, "dig_per_set": 2.0
    },
    {
        "id": 106, "team_id": "HKL", "name": "김수지", "position": "MB", "number": 11,
        "sets_played": 3, "points": 1, "att_made": 0, "att_tried": 3, "att_pct": 0.0, "att_share": 2.5,
        "srv_made": 0, "srv_tried": 9, "blk_made": 1, "blk_tried": 15, "dig_made": 4, "dig_tried": 5,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2,
        "comment": "블로킹 1득점 및 15차례 블로킹 시도로 상대 공격 견제.",
        "blk_pct": 6.67, "dig_pct": 80.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0, "blk_per_set": 0.33, "dig_per_set": 1.33
    },
    {
        "id": 103, "team_id": "HKL", "name": "표승주", "position": "OH", "number": 19,
        "sets_played": 2, "points": 1, "att_made": 1, "att_tried": 2, "att_pct": 50.0, "att_share": 1.67,
        "srv_made": 0, "srv_tried": 5, "blk_made": 0, "blk_tried": 2, "dig_made": 3, "dig_tried": 4,
        "rcv_made": 3, "rcv_tried": 9, "set_made": 0, "set_tried": 2, "errors": 0,
        "comment": "공격 1득점, 리시브 3개, 디그 3개.",
        "blk_pct": 0.0, "dig_pct": 75.0, "rcv_pct": 33.33, "set_pct": 0.0, "srv_pct": 0.0, "blk_per_set": 0.0, "dig_per_set": 1.5
    },
    {
        "id": 107, "team_id": "HKL", "name": "임혜림", "position": "MB", "number": 14,
        "sets_played": 1, "points": 1, "att_made": 1, "att_tried": 3, "att_pct": 33.33, "att_share": 2.5,
        "srv_made": 0, "srv_tried": 1, "blk_made": 0, "blk_tried": 0, "dig_made": 1, "dig_tried": 1,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2,
        "comment": "속공 1득점 기록.",
        "blk_pct": None, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 0.0, "srv_pct": 0.0, "blk_per_set": 0.0, "dig_per_set": 1.0
    },
    {
        "id": 110, "team_id": "HKL", "name": "고민지", "position": "L", "number": 16,
        "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
        "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 9, "dig_tried": 11,
        "rcv_made": 7, "rcv_tried": 21, "set_made": 0, "set_tried": 4, "errors": 0,
        "comment": "디그 9개 성공, 리시브 7개 정확으로 리베로 수비 전담.",
        "blk_pct": None, "dig_pct": 81.82, "rcv_pct": 33.33, "set_pct": 0.0, "srv_pct": None, "blk_per_set": 0.0, "dig_per_set": 3.0
    },
    {
        "id": 113, "team_id": "HKL", "name": "신연경", "position": "L", "number": 3,
        "sets_played": 3, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
        "srv_made": 0, "srv_tried": 0, "blk_made": 0, "blk_tried": 0, "dig_made": 6, "dig_tried": 7,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 2, "errors": 0,
        "comment": "디그 6개 성공으로 수비 라인 보강.",
        "blk_pct": None, "dig_pct": 85.71, "rcv_pct": None, "set_pct": 0.0, "srv_pct": None, "blk_per_set": 0.0, "dig_per_set": 2.0
    },
    {
        "id": 112, "team_id": "HKL", "name": "박수연", "position": "OH", "number": 20,
        "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
        "srv_made": 0, "srv_tried": 1, "blk_made": 0, "blk_tried": 0, "dig_made": 1, "dig_tried": 1,
        "rcv_made": 1, "rcv_tried": 1, "set_made": 0, "set_tried": 1, "errors": 1,
        "comment": "서브 1회, 디그 1개, 리시브 1개.",
        "blk_pct": None, "dig_pct": 100.0, "rcv_pct": 100.0, "set_pct": 0.0, "srv_pct": 0.0, "blk_per_set": 0.0, "dig_per_set": 1.0
    },
    {
        "id": 111, "team_id": "HKL", "name": "이나연", "position": "S", "number": 33,
        "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
        "srv_made": 0, "srv_tried": 2, "blk_made": 0, "blk_tried": 0, "dig_made": 1, "dig_tried": 1,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 3, "set_tried": 6, "errors": 0,
        "comment": "세트 3개, 서브 2회.",
        "blk_pct": None, "dig_pct": 100.0, "rcv_pct": None, "set_pct": 50.0, "srv_pct": 0.0, "blk_per_set": 0.0, "dig_per_set": 1.0
    },
    {
        "id": 115, "team_id": "HKL", "name": "이신영", "position": "OH", "number": 18,
        "sets_played": 1, "points": 0, "att_made": 0, "att_tried": 0, "att_pct": None, "att_share": 0.0,
        "srv_made": 0, "srv_tried": 1, "blk_made": 0, "blk_tried": 0, "dig_made": 0, "dig_tried": 0,
        "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0,
        "comment": "원포인트 서버 출전.",
        "blk_pct": None, "dig_pct": None, "rcv_pct": None, "set_pct": None, "srv_pct": 0.0, "blk_per_set": 0.0, "dig_per_set": 0.0
    }
]

# 3. 세트 정보
sets = [
    {
        "set_no": 1,
        "hdec_score": 25,
        "hkl_score": 19,
        "winner": "HDEC",
        "score_home": 25,
        "score_away": 19
    },
    {
        "set_no": 2,
        "hdec_score": 25,
        "hkl_score": 17,
        "winner": "HDEC",
        "score_home": 25,
        "score_away": 17
    },
    {
        "set_no": 3,
        "hdec_score": 28,
        "hkl_score": 26,
        "winner": "HDEC",
        "score_home": 28,
        "score_away": 26
    }
]

# 4. 세트 라인업
set_lineups = {
    "1": {
        "HDEC": {"S": 207, "OH1": 202, "OH2": 206, "OP": 201, "MB1": 208, "MB2": 205, "L": 211},
        "HKL": {"S": 105, "OH1": 102, "OH2": 103, "OP": 101, "MB1": 104, "MB2": 106, "L": 110}
    },
    "2": {
        "HDEC": {"S": 207, "OH1": 202, "OH2": 206, "OP": 201, "MB1": 208, "MB2": 205, "L": 211},
        "HKL": {"S": 114, "OH1": 102, "OH2": 108, "OP": 101, "MB1": 104, "MB2": 106, "L": 110}
    },
    "3": {
        "HDEC": {"S": 207, "OH1": 202, "OH2": 215, "OP": 201, "MB1": 208, "MB2": 205, "L": 210},
        "HKL": {"S": 105, "OH1": 102, "OH2": 108, "OP": 101, "MB1": 104, "MB2": 106, "L": 110}
    }
}

# 5. 오늘의 키플레이어 & 팬 투표 BEST 플레이어
key_players = {
    "points": {"HDEC": {"name": "메가", "val": 18}, "HKL": {"name": "킨델란", "val": 21}},
    "attacks": {"HDEC": {"name": "조던", "val": 15}, "HKL": {"name": "킨델란", "val": 19}},
    "serves": {"HDEC": {"name": "김다인", "val": 1}, "HKL": {"name": "자스티스", "val": 3}},
    "blocks": {"HDEC": {"name": "배유나", "val": 6}, "HKL": {"name": "킨델란", "val": 2}},
    "digs": {"HDEC": {"name": "이예림", "val": 15}, "HKL": {"name": "자스티스", "val": 11}},
    "receives": {"HDEC": {"name": "이영주", "val": 7}, "HKL": {"name": "고민지", "val": 7}},
    "sets": {"HDEC": {"name": "김다인", "val": 29}, "HKL": {"name": "이고은", "val": 17}}
}

best_players = {
    "HDEC": [
        {"rank": 1, "name": "배유나", "votes": 312, "pct": 48, "pos": "MB"},
        {"rank": 2, "name": "메가", "votes": 208, "pct": 32, "pos": "OP"},
        {"rank": 3, "name": "조던", "votes": 78, "pct": 12, "pos": "OH"}
    ],
    "HKL": [
        {"rank": 1, "name": "킨델란", "votes": 286, "pct": 52, "pos": "OP"},
        {"rank": 2, "name": "자스티스", "votes": 154, "pct": 28, "pos": "OH"},
        {"rank": 3, "name": "정윤주", "votes": 61, "pct": 11, "pos": "OH"}
    ]
}

# 6. 세트별 주요 선수 통계
set_stats = [
    # 1세트
    {"set_no": 1, "player_id": 201, "att_made": 5, "att_tried": 11, "srv_made": 0, "srv_tried": 3, "blk_made": 1, "blk_tried": 2, "dig_made": 3, "dig_tried": 3, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 1, "points": 6, "blk_assist": 0, "comment": "1세트 메가 6득점으로 기선제압"},
    {"set_no": 1, "player_id": 208, "att_made": 1, "att_tried": 1, "srv_made": 1, "srv_tried": 4, "blk_made": 3, "blk_tried": 6, "dig_made": 1, "dig_tried": 1, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 0, "errors": 0, "points": 5, "blk_assist": 0, "comment": "1세트 배유나 블로킹 3개 작렬"},
    {"set_no": 1, "player_id": 101, "att_made": 6, "att_tried": 16, "srv_made": 0, "srv_tried": 2, "blk_made": 1, "blk_tried": 3, "dig_made": 2, "dig_tried": 3, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 2, "points": 7, "blk_assist": 0, "comment": "1세트 킨델란 7득점 분전"},
    # 2세트
    {"set_no": 2, "player_id": 202, "att_made": 6, "att_tried": 12, "srv_made": 1, "srv_tried": 2, "blk_made": 0, "blk_tried": 2, "dig_made": 1, "dig_tried": 1, "rcv_made": 1, "rcv_tried": 3, "set_made": 1, "set_tried": 1, "errors": 1, "points": 7, "blk_assist": 0, "comment": "2세트 조던 7득점 맹폭격"},
    {"set_no": 2, "player_id": 208, "att_made": 1, "att_tried": 1, "srv_made": 0, "srv_tried": 4, "blk_made": 2, "blk_tried": 5, "dig_made": 1, "dig_tried": 1, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 1, "errors": 0, "points": 3, "blk_assist": 0, "comment": "2세트 배유나 리딩 블로킹으로 흐름 압도"},
    {"set_no": 2, "player_id": 101, "att_made": 5, "att_tried": 15, "srv_made": 0, "srv_tried": 2, "blk_made": 0, "blk_tried": 2, "dig_made": 3, "dig_tried": 3, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 2, "errors": 2, "points": 5, "blk_assist": 0, "comment": "2세트 킨델란 5득점"},
    # 3세트
    {"set_no": 3, "player_id": 201, "att_made": 5, "att_tried": 13, "srv_made": 1, "srv_tried": 5, "blk_made": 1, "blk_tried": 3, "dig_made": 4, "dig_tried": 5, "rcv_made": 0, "rcv_tried": 0, "set_made": 1, "set_tried": 1, "errors": 0, "points": 7, "blk_assist": 0, "comment": "3세트 듀스 접전 속 메가 7득점 대폭발"},
    {"set_no": 3, "player_id": 208, "att_made": 1, "att_tried": 1, "srv_made": 0, "srv_tried": 5, "blk_made": 1, "blk_tried": 6, "dig_made": 1, "dig_tried": 2, "rcv_made": 0, "rcv_tried": 1, "set_made": 1, "set_tried": 2, "errors": 1, "points": 2, "blk_assist": 0, "comment": "3세트 27:26 매치포인트 결정적 유효 블로킹"},
    {"set_no": 3, "player_id": 101, "att_made": 8, "att_tried": 23, "srv_made": 0, "srv_tried": 3, "blk_made": 1, "blk_tried": 5, "dig_made": 4, "dig_tried": 4, "rcv_made": 0, "rcv_tried": 0, "set_made": 0, "set_tried": 2, "errors": 1, "points": 9, "blk_assist": 0, "comment": "3세트 듀스까지 끌고 간 킨델란의 9득점 혈투"}
]

# 7. 세트별 대표 전술 랠리 (시뮬레이션 & 리플레이)
rallies = []
r_idx = 1
# 1세트 (25:19)
for sh in range(1, 26):
    sa = int(sh * 19 / 25)
    scorer = "HDEC" if sh <= 25 else "HKL"
    rallies.append({
        "id": r_idx, "set_no": 1, "rally_no": r_idx, "scorer": "HDEC",
        "before": {"HDEC": sh - 1, "HKL": sa}, "after": {"HDEC": sh, "HKL": sa},
        "landing": [85, 20], "events": [
            {"t": "HKL", "n": "자스티스", "a": "서브", "pid": 102},
            {"t": "HDEC", "n": "이영주", "a": "리시브", "pid": 211},
            {"t": "HDEC", "n": "김다인", "a": "세트", "pid": 207},
            {"t": "HDEC", "n": "배유나" if sh % 3 == 0 else "메가", "a": "오픈 득점" if sh % 3 != 0 else "블로킹 득점", "pid": 208 if sh % 3 == 0 else 201}
        ]
    })
    r_idx += 1
# 2세트 (25:17)
for sh in range(1, 26):
    sa = int(sh * 17 / 25)
    rallies.append({
        "id": r_idx, "set_no": 2, "rally_no": r_idx, "scorer": "HDEC",
        "before": {"HDEC": sh - 1, "HKL": sa}, "after": {"HDEC": sh, "HKL": sa},
        "landing": [86, 75], "events": [
            {"t": "HDEC", "n": "김다인", "a": "서브", "pid": 207},
            {"t": "HKL", "n": "고민지", "a": "리시브", "pid": 110},
            {"t": "HKL", "n": "박혜진", "a": "세트", "pid": 114},
            {"t": "HKL", "n": "킨델란", "a": "오픈", "pid": 101},
            {"t": "HDEC", "n": "배유나", "a": "블로킹 득점", "pid": 208}
        ]
    })
    r_idx += 1
# 3세트 (28:26)
for sh in range(1, 29):
    sa = min(26, int(sh * 26 / 28))
    rallies.append({
        "id": r_idx, "set_no": 3, "rally_no": r_idx, "scorer": "HDEC",
        "before": {"HDEC": sh - 1, "HKL": sa}, "after": {"HDEC": sh, "HKL": sa},
        "landing": [82, 45], "events": [
            {"t": "HKL", "n": "킨델란", "a": "서브", "pid": 101},
            {"t": "HDEC", "n": "이예림", "a": "리시브", "pid": 206},
            {"t": "HDEC", "n": "김다인", "a": "세트", "pid": 207},
            {"t": "HDEC", "n": "메가" if sh == 28 else "조던", "a": "퀵오픈 득점", "pid": 201 if sh == 28 else 202}
        ]
    })
    r_idx += 1

# 8. 전술 시나리오 (하이라이트)
scenarios = [
    {
        "id": 1,
        "set_no": 1,
        "code": "SET1_HL1_BAE_BLOCKING",
        "title": "🛡️ [1세트 HL1] 배유나 철벽 블로킹 득점 (8:5)",
        "subtitle": "1세트 8:5 | 킨델란의 강타를 완벽하게 차단하며 기선제압",
        "attack_team": "HDEC",
        "sort_order": 0,
        "phases": [
            {
                "name": "킨델란 오픈 강타 & 배유나 킬블록",
                "dur": 1500,
                "ball": [
                    {"from": ["def", 28, 45], "to": ["atk", 85, 20], "h": 22, "delay": 0, "end": 0.5},
                    {"from": ["atk", 85, 20], "to": ["def", 15, 20], "h": 10, "delay": 0.55, "end": 0.9}
                ],
                "moves": [
                    {"who": "atk.MBF", "to": [85, 20], "delay": 0.2, "end": 0.5, "trail": True},
                    {"who": "def.OP", "to": [84, 22], "delay": 0.1, "end": 0.45}
                ],
                "focus": "atk.MBF",
                "tags": ["#1세트", "#배유나", "#블로킹득점", "#기선제압"],
                "text": "흥국생명 킨델란의 강력한 백어택을 배유나가 완벽한 리딩 블로킹으로 단독 차단! 수원 홈팬들을 열광시킵니다!"
            }
        ]
    },
    {
        "id": 2,
        "set_no": 1,
        "code": "SET1_HL2_MEGA_ATTACK",
        "title": "⚡ [1세트 HL2] 메가 파워 스파이크 & 1세트 승리 (25:19)",
        "subtitle": "1세트 25:19 | 메가의 호쾌한 라이트 오픈 강타로 1세트 마무리",
        "attack_team": "HDEC",
        "sort_order": 1,
        "phases": [
            {
                "name": "김다인 C퀵 세트 & 메가 폭발적 스파이크",
                "dur": 1500,
                "ball": [
                    {"from": ["atk", 83, 60], "to": ["atk", 88, 80], "h": 18, "delay": 0, "end": 0.4},
                    {"from": ["atk", 88, 80], "to": ["def", 12, 85], "h": 12, "delay": 0.45, "end": 0.8}
                ],
                "moves": [
                    {"who": "atk.OP", "to": [88, 80], "delay": 0.2, "end": 0.4, "trail": True}
                ],
                "focus": "atk.OP",
                "tags": ["#1세트마무리", "#메가", "#세트승리"],
                "text": "김다인 세터의 빠른 사이드 토스를 받은 메가가 코트 구석에 내리꽂으며 25:19, 1세트를 현대건설이 가져옵니다!"
            }
        ]
    },
    {
        "id": 3,
        "set_no": 2,
        "code": "SET2_HL1_JORDAN_QUICK",
        "title": "🔥 [2세트 HL1] 조던 날카로운 퀵오픈 맹폭 (18:12)",
        "subtitle": "2세트 18:12 | 조던의 연속 득점으로 점수 차를 벌리는 현대건설",
        "attack_team": "HDEC",
        "sort_order": 2,
        "phases": [
            {
                "name": "조던 터치아웃 퀵오픈 득점",
                "dur": 1400,
                "ball": [
                    {"from": ["atk", 83, 60], "to": ["atk", 86, 18], "h": 18, "delay": 0, "end": 0.4},
                    {"from": ["atk", 86, 18], "to": ["def", -10, 18], "h": 15, "delay": 0.45, "end": 0.8}
                ],
                "moves": [
                    {"who": "atk.OHF", "to": [86, 18], "delay": 0.2, "end": 0.4, "trail": True}
                ],
                "focus": "atk.OHF",
                "tags": ["#2세트", "#조던", "#퀵오픈", "#격차벌리기"],
                "text": "조던의 대각 스파이크가 블로커 손끝을 맞고 코트 밖으로 튕겨 나갑니다! 현대건설 6점 차 리드!"
            }
        ]
    },
    {
        "id": 4,
        "set_no": 3,
        "code": "SET3_HL1_DEUCE_WIN",
        "title": "🏆 [3세트 HL1] 28:26 듀스 혈투 끝 매치포인트 3:0 셧아웃 대승!",
        "subtitle": "3세트 28:26 경기종료 | 메가 마지막 백어택 강타로 셧아웃 완승 완성",
        "attack_team": "HDEC",
        "sort_order": 3,
        "phases": [
            {
                "name": "이예림 디그 → 김다인 토스 → 메가 매치포인트 스파이크",
                "dur": 1600,
                "ball": [
                    {"from": ["def", 85, 20], "to": ["atk", 28, 50], "h": 22, "delay": 0, "end": 0.4},
                    {"from": ["atk", 28, 50], "to": ["atk", 83, 60], "h": 20, "delay": 0.42, "end": 0.7},
                    {"from": ["atk", 83, 60], "to": ["atk", 88, 75], "h": 18, "delay": 0.72, "end": 0.9},
                    {"from": ["atk", 88, 75], "to": ["def", 10, 45], "h": 10, "delay": 0.92, "end": 1.2}
                ],
                "moves": [
                    {"who": "atk.OP", "to": [88, 75], "delay": 0.6, "end": 0.9, "trail": True}
                ],
                "focus": "atk.OP",
                "tags": ["#3세트", "#듀스승리", "#메가18득점", "#3대0셧아웃완승"],
                "text": "27:26 매치포인트에서 메가의 폭발적인 스파이크가 흥국생명 코트를 꿰뚫습니다! 현대건설이 28:26으로 3세트마저 따내며 3:0 셧아웃 대승을 거둡니다!"
            }
        ]
    }
]

full_data_1122 = {
    "match_info": match_info,
    "teams": teams,
    "players": players,
    "sets": sets,
    "set_lineups": set_lineups,
    "key_players": key_players,
    "best_players": best_players,
    "set_stats": set_stats,
    "rallies": rallies,
    "scenarios": scenarios
}

def export_js() -> None:
    data_json = json.dumps(full_data_1122, ensure_ascii=False, indent=2)
    js_content = f"""// 11월 22일 현대건설 vs 흥국생명 전술 분석 데이터
window.BOOTSTRAP_1122 = {data_json};

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
if (window.BOOTSTRAP_1116) {{
  window.MATCHES['2026-11-16'] = window.BOOTSTRAP_1116;
  window.MATCHES['2024-11-16'] = window.BOOTSTRAP_1116;
}}
window.MATCHES['2026-11-22'] = window.BOOTSTRAP_1122;
window.MATCHES['2024-11-22'] = window.BOOTSTRAP_1122;
"""
    js_path = ROOT / "js" / "data_1122.js"
    static_js_path = ROOT / "static" / "js" / "data_1122.js"
    js_path.write_text(js_content, encoding="utf-8")
    static_js_path.write_text(js_content, encoding="utf-8")
    print(f"Generated data_1122.js with {len(rallies)} rallies successfully!")

if __name__ == "__main__":
    export_js()
