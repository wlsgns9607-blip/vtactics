"""
여자배구 V-리그 전술 분석 시뮬레이터 - 선수 데이터
정관장 레드스파크스 vs 현대건설

- 기록은 사용자가 제공한 기록표(스크린샷)를 그대로 옮긴 것입니다.
- 성공/시도 형태의 기록은 (성공, 시도) 튜플로 저장합니다.
- 기록표에서 '-'로 표시된 값은 None으로 저장합니다.
- 등번호 등 기록표에 없는 정보는 None으로 두었습니다 (추후 입력).
"""

import json

# ─────────────────────────────────────────────
# 포지션 코드
# ─────────────────────────────────────────────
POSITIONS = {
    "S": "세터",
    "OH": "아웃사이드 히터",
    "OP": "아포짓",
    "MB": "미들 블로커",
    "L": "리베로",
}

# ─────────────────────────────────────────────
# 팀 정보
# ─────────────────────────────────────────────
TEAMS = {
    "KGC": {
        "name": "정관장 레드스파크스",
        "short": "정관장",
        # 홈 테마 색상: 공식 컬러 확인 후 확정
        "theme": {"primary": None, "accent": None},
    },
    "HDEC": {
        "name": "현대건설 힐스테이트",
        "short": "현대건설",
        "theme": {"primary": None, "accent": None},
    },
}

# ─────────────────────────────────────────────
# 선수 기록
# 필드: name, pos, number, sets, points, attack, attack_pct, attack_share,
#       serve, block, dig, receive, set, errors
# ─────────────────────────────────────────────
PLAYERS = {
    "KGC": [
        {"name": "종휘",   "pos": "OH", "number": None, "sets": 4, "points": 20,
         "attack": (17, 54), "attack_pct": 31.48, "attack_share": 36.0,
         "serve": (1, 17), "block": (2, 9), "dig": (12, 15),
         "receive": (15, 30), "set": (0, 2), "errors": 4},
        {"name": "신은지", "pos": "OP", "number": None, "sets": 4, "points": 11,
         "attack": (10, 20), "attack_pct": 50.0, "attack_share": 13.33,
         "serve": (1, 17), "block": (0, 11), "dig": (14, 18),
         "receive": (0, 0), "set": (0, 5), "errors": 4},
        {"name": "박은진", "pos": "MB", "number": None, "sets": 4, "points": 10,
         "attack": (7, 20), "attack_pct": 35.0, "attack_share": 13.33,
         "serve": (2, 14), "block": (1, 15), "dig": (3, 4),
         "receive": (0, 0), "set": (1, 3), "errors": 3},
        {"name": "박여름", "pos": "OH", "number": None, "sets": 3, "points": 9,
         "attack": (8, 24), "attack_pct": 33.33, "attack_share": 16.0,
         "serve": (0, 5), "block": (1, 3), "dig": (4, 5),
         "receive": (6, 21), "set": (1, 3), "errors": 3},
        {"name": "이지수", "pos": "MB", "number": None, "sets": 4, "points": 6,
         "attack": (1, 6), "attack_pct": 16.67, "attack_share": 4.0,
         "serve": (0, 9), "block": (5, 18), "dig": (5, 6),
         "receive": (0, 0), "set": (3, 10), "errors": 4},
        {"name": "박혜민", "pos": "OH", "number": None, "sets": 4, "points": 5,
         "attack": (5, 16), "attack_pct": 31.25, "attack_share": 10.67,
         "serve": (0, 7), "block": (0, 6), "dig": (6, 6),
         "receive": (2, 13), "set": (0, 4), "errors": 2},
        {"name": "염혜선", "pos": "S",  "number": None, "sets": 3, "points": 2,
         "attack": (0, 2), "attack_pct": None, "attack_share": 1.33,
         "serve": (1, 11), "block": (1, 1), "dig": (2, 2),
         "receive": (0, 0), "set": (12, 43), "errors": 2},
        {"name": "오세인", "pos": "OH", "number": None, "sets": 3, "points": 2,
         "attack": (1, 4), "attack_pct": 25.0, "attack_share": 2.67,
         "serve": (0, 0), "block": (1, 3), "dig": (1, 1),
         "receive": (0, 0), "set": (0, 0), "errors": None},
        {"name": "최서현", "pos": "S",  "number": None, "sets": 3, "points": 1,
         "attack": (1, 3), "attack_pct": 33.33, "attack_share": 2.0,
         "serve": (0, 13), "block": (0, 6), "dig": (12, 13),
         "receive": (0, 0), "set": (26, 67), "errors": 1},
        {"name": "최효서", "pos": "OH", "number": None, "sets": 2, "points": 1,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (1, 3), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 1), "errors": None},
        {"name": "김아중", "pos": "L",  "number": None, "sets": 4, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (20, 22),
         "receive": (3, 9), "set": (4, 7), "errors": None},
        {"name": "노란",   "pos": "L",  "number": None, "sets": 2, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (5, 7),
         "receive": (4, 6), "set": (0, 1), "errors": 1},
        {"name": "이선우", "pos": "MB", "number": None, "sets": 2, "points": None,
         "attack": (0, 1), "attack_pct": None, "attack_share": 0.67,
         "serve": (0, 0), "block": (0, 2), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": None},
        {"name": "전다빈", "pos": "OH", "number": None, "sets": 1, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 1), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": 1},
        {"name": "곽선옥", "pos": "OH", "number": None, "sets": None, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": None},
        {"name": "김지윤", "pos": "OH", "number": None, "sets": None, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": None},
        {"name": "도수빈", "pos": "OH", "number": None, "sets": None, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": None},
    ],

    "HDEC": [
        {"name": "조던",   "pos": "OH", "number": None, "sets": 4, "points": 21,
         "attack": (20, 50), "attack_pct": 40.0, "attack_share": 33.11,
         "serve": (0, 8), "block": (1, 10), "dig": (9, 11),
         "receive": (1, 3), "set": (1, 4), "errors": 10},
        {"name": "메가",   "pos": "OP", "number": None, "sets": 4, "points": 18,
         "attack": (16, 42), "attack_pct": 38.1, "attack_share": 27.81,
         "serve": (1, 13), "block": (1, 13), "dig": (4, 8),
         "receive": (0, 0), "set": (0, 3), "errors": 6},
        {"name": "이예림", "pos": "OH", "number": None, "sets": 4, "points": 9,
         "attack": (9, 25), "attack_pct": 36.0, "attack_share": 16.56,
         "serve": (0, 7), "block": (0, 6), "dig": (13, 13),
         "receive": (11, 40), "set": (0, 2), "errors": 4},
        {"name": "이채영", "pos": "OH", "number": None, "sets": 4, "points": 6,
         "attack": (6, 14), "attack_pct": 42.86, "attack_share": 9.27,
         "serve": (0, 10), "block": (0, 4), "dig": (7, 9),
         "receive": (7, 21), "set": (0, 2), "errors": 2},
        {"name": "배유나", "pos": "MB", "number": None, "sets": 4, "points": 4,
         "attack": (3, 9), "attack_pct": 33.33, "attack_share": 5.96,
         "serve": (1, 14), "block": (0, 15), "dig": (4, 5),
         "receive": (0, 0), "set": (1, 2), "errors": 1},
        {"name": "김희진", "pos": "MB", "number": None, "sets": 4, "points": 3,
         "attack": (3, 6), "attack_pct": 50.0, "attack_share": 3.97,
         "serve": (0, 11), "block": (0, 14), "dig": (3, 4),
         "receive": (0, 1), "set": (0, 1), "errors": 1},
        {"name": "김다인", "pos": "S",  "number": None, "sets": 4, "points": 1,
         "attack": (0, 1), "attack_pct": None, "attack_share": 0.66,
         "serve": (1, 20), "block": (0, 10), "dig": (20, 22),
         "receive": (0, 1), "set": (46, 116), "errors": 6},
        {"name": "나현수", "pos": "OP", "number": None, "sets": 2, "points": 1,
         "attack": (1, 4), "attack_pct": 25.0, "attack_share": 2.65,
         "serve": (0, 0), "block": (0, 2), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": None},
        {"name": "김연견", "pos": "L",  "number": None, "sets": 4, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (27, 30),
         "receive": (3, 20), "set": (5, 18), "errors": None},
        {"name": "김사랑", "pos": "S",  "number": None, "sets": 2, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 2), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (3, 10), "errors": 1},
        {"name": "한미르", "pos": "OH", "number": None, "sets": 2, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 3), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (1, 2), "errors": None},
        {"name": "이민영", "pos": "OH", "number": None, "sets": 1, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 1), "block": (0, 0), "dig": (1, 1),
         "receive": (0, 0), "set": (0, 0), "errors": None},
        {"name": "강서우", "pos": "MB", "number": None, "sets": None, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": None},
        {"name": "구솔",   "pos": "S",  "number": None, "sets": None, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": None},
        {"name": "이영주", "pos": "L",  "number": None, "sets": None, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": None},
        {"name": "정지윤", "pos": "OH", "number": None, "sets": None, "points": None,
         "attack": (0, 0), "attack_pct": None, "attack_share": None,
         "serve": (0, 0), "block": (0, 0), "dig": (0, 0),
         "receive": (0, 0), "set": (0, 0), "errors": None},
    ],
}

# ─────────────────────────────────────────────
# 시뮬레이터 기본 라인업 (출전 세트·기록 기준 제안안)
# ─────────────────────────────────────────────
STARTING_LINEUP = {
    "KGC": {
        "S": "염혜선",
        "OH1": "종휘",
        "OH2": "박여름",
        "OP": "신은지",
        "MB1": "박은진",
        "MB2": "이지수",
        "L": "김아중",
    },
    "HDEC": {
        "S": "김다인",
        "OH1": "조던",
        "OH2": "이예림",
        "OP": "메가",
        "MB1": "배유나",
        "MB2": "김희진",
        "L": "김연견",
    },
}


# ─────────────────────────────────────────────
# 유틸 함수
# ─────────────────────────────────────────────
def rate(stat):
    """(성공, 시도) 튜플 → 성공률(%). 시도가 0이면 None."""
    made, tried = stat
    return round(made / tried * 100, 2) if tried else None


def get_player(team, name):
    for p in PLAYERS[team]:
        if p["name"] == name:
            return p
    return None


def player_summary(p):
    """시뮬레이터 사이드 패널에 표시할 요약 지표."""
    return {
        "이름": p["name"],
        "포지션": POSITIONS[p["pos"]],
        "출전세트": p["sets"],
        "득점": p["points"],
        "공격성공률": p["attack_pct"],
        "공격점유율": p["attack_share"],
        "블로킹 성공률": rate(p["block"]),
        "디그 성공률": rate(p["dig"]),
        "리시브 효율": rate(p["receive"]),
        "세트 성공률": rate(p["set"]),
    }


def export_json(path="players_data.json"):
    """HTML 앱에서 바로 불러 쓸 수 있도록 JSON으로 내보내기."""
    data = {"teams": TEAMS, "positions": POSITIONS,
            "players": PLAYERS, "lineup": STARTING_LINEUP}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


if __name__ == "__main__":
    for team, players in PLAYERS.items():
        print(f"\n[{TEAMS[team]['short']}] {len(players)}명")
        for p in players:
            s = player_summary(p)
            print(f"  {s['이름']:<4} {p['pos']:<2}  득점 {s['득점'] or '-':>3}  "
                  f"공격 {s['공격성공률'] or '-':>6}%  점유 {s['공격점유율'] or '-':>6}%  "
                  f"디그 {s['디그 성공률'] or '-':>6}%")
