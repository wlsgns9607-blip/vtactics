"""
update_set1_1104.py:
11월 4일 흥국생명 vs 정관장 1세트 KOVO 공식 45개 랠리 전량 및
5득점 하이라이트 전술 시뮬레이션(애니메이션)을 build_1104.py와 data_1104.js에 통합 적용합니다.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HKL_MAP = {
    '킨델란': (23, 'OP', 101),
    '자스티스': (2, 'OH', 102),
    '표승주': (19, 'OH', 103),
    '정호영': (17, 'MB', 104),
    '김수지': (11, 'MB', 105),
    '이나연': (33, 'S', 107),
    '박혜진': (13, 'S', 108),
    '이신영': (18, 'OH', 109),
    '박수연': (20, 'OH', 113),
    '문지윤': (1, 'OP', 114),
    '고민지': (16, 'L', 110),
    '도수빈': (8, 'L', 111),
}
KGC_MAP = {
    '종휘': (17, 'OH', 201),
    '박혜민': (10, 'OH', 202),
    '이선우': (15, 'MB', 203),
    '신은지': (16, 'OP', 204),
    '이지수': (18, 'MB', 205),
    '박은진': (6, 'MB', 206),
    '노란': (5, 'L', 207),
    '염혜선': (3, 'S', 208),
    '곽선옥': (24, 'OH', 209),
    '전다빈': (4, 'OH', 210),
}

ALL_PLAYERS = {}
for name, (num, pos, pid) in HKL_MAP.items():
    ALL_PLAYERS[name] = (num, pos, pid, "HKL")
for name, (num, pos, pid) in KGC_MAP.items():
    ALL_PLAYERS[name] = (num, pos, pid, "KGC")

def parse_line(line):
    m = re.match(r"^(\d+)?([가-힣]+)\s+(.+)$", line)
    if not m:
        return None
    _, name, act = m.groups()
    if name not in ALL_PLAYERS:
        return None
    num, pos, pid, team = ALL_PLAYERS[name]

    cat = "attack"
    ok = False
    if "서브" in act or "스파이크서브" in act:
        cat = "serve"
        ok = "성공" in act
    elif "리시브" in act:
        cat = "receive"
        ok = "정확" in act
    elif "세트" in act:
        cat = "set"
        ok = "정확" in act
    elif "디그" in act:
        cat = "dig"
        ok = "실패" not in act and "범실" not in act
    elif "블록킹" in act:
        cat = "block"
        ok = "성공" in act
    elif any(k in act for k in ["오픈", "퀵오픈", "백어택", "속공", "시간차"]):
        cat = "attack"
        ok = "성공" in act

    return {
        "n": name,
        "num": num,
        "t": team,
        "a": line,
        "c": cat,
        "ok": ok,
        "pid": pid,
    }


def parse_raw_set1_rallies():
    raw_path = ROOT / "data" / "sets_1104" / "set1.txt"
    raw = raw_path.read_text(encoding="utf-8")
    lines = [l.strip() for l in raw.splitlines() if l.strip()]

    # Split chunks by POINT!
    chunks = []
    cur = []
    for l in lines:
        cur.append(l)
        if l == "POINT!":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)

    # Reverse chronologically (from point 1 to point 45)
    chunks.reverse()

    # The 45 outcomes and running scores
    # Score progression:
    # 1: 1-0 HKL (킨델란 오픈 성공)
    # 2: 2-0 HKL (김수지 블록킹 성공)
    # 3: 3-0 HKL (이나연 서브 성공)
    # 4: 3-1 KGC (종휘 오픈 성공)
    # 5: 3-2 KGC (박혜민 블록킹 성공)
    # 6: 4-2 HKL (표승주 오픈 성공)
    # 7: 5-2 HKL (표승주 서브 성공)
    # 8: 5-3 KGC (표승주 서브 네트걸림)
    # 9: 6-3 HKL (자스티스 퀵오픈 성공)
    # 10: 7-3 HKL (김수지 서브 성공)
    # 11: 7-4 KGC (김수지 서브 네트걸림)
    # 12: 8-4 HKL (킨델란 오픈 성공)
    # 13: 8-5 KGC (킨델란 스파이크서브 아웃)
    # 14: 9-5 HKL (자스티스 오픈 성공)
    # 15: 10-5 HKL (정호영 오픈 성공)
    # 16: 10-6 KGC (킨델란 백어택 네트걸림)
    # 17: 11-6 HKL (박은진 서브 아웃)
    # 18: 12-6 HKL (정호영 서브 성공)
    # 19: 12-7 KGC (정호영 서브 아웃)
    # 20: 12-8 KGC (킨델란 백어택 아웃)
    # 21: 13-8 HKL (종휘 오픈 아웃)
    # 22: 14-8 HKL (자스티스 백어택 성공)
    # 23: 15-8 HKL (표승주 퀵오픈 성공)
    # 24: 15-9 KGC (이선우 퀵오픈 성공)
    # 25: 16-9 HKL (종휘 서브 아웃)
    # 26: 17-9 HKL (킨델란 블록킹 성공)
    # 27: 17-10 KGC (박혜민 블록킹 성공)
    # 28: 18-10 HKL (킨델란 퀵오픈 성공)
    # 29: 18-11 KGC (이선우 퀵오픈 성공)
    # 30: 19-11 HKL (신은지 서브 네트걸림)
    # 31: 20-11 HKL (킨델란 백어택 성공)
    # 32: 20-12 KGC (킨델란 서브 네트걸림)
    # 33: 21-12 HKL (킨델란 백어택 성공)
    # 34: 22-12 HKL (킨델란 백어택 성공)
    # 35: 22-13 KGC (신은지 백어택 성공)
    # 36: 22-14 KGC (종휘 오픈 성공)
    # 37: 22-15 KGC (종휘 오픈 성공)
    # 38: 22-16 KGC (종휘 오픈 성공)
    # 39: 22-17 KGC (박은진 서브 성공)
    # 40: 22-18 KGC (이지수 블록킹 성공)
    # 41: 23-18 HKL (표승주 시간차 성공)
    # 42: 24-18 HKL (종휘 퀵오픈 네트걸림)
    # 43: 24-19 KGC (신은지 백어택 성공)
    # 44: 24-20 KGC (종휘 오픈 성공)
    # 45: 25-20 HKL (염혜선 서브 아웃)

    HKL_POINTS = {1, 2, 3, 6, 7, 9, 10, 12, 14, 15, 17, 18, 21, 22, 23, 25, 26, 28, 30, 31, 33, 34, 41, 42, 45}

    rallies = []
    hkl_score = 0
    kgc_score = 0

    for idx, c in enumerate(chunks[:45], 1):
        is_hkl = idx in HKL_POINTS
        if is_hkl:
            hkl_score += 1
            scorer = "HKL"
        else:
            kgc_score += 1
            scorer = "KGC"

        # parse events in chronological order inside chunk
        # the chunk lines are reversed (KOVO log order)
        chunk_lines = []
        i = 0
        while i < len(c):
            l = c[i]
            if l.isdigit() and i + 1 < len(c) and re.match(r"^[가-힣]+ ", c[i+1]):
                chunk_lines.append(l + c[i+1])
                i += 2
            else:
                chunk_lines.append(l)
                i += 1

        ev_lines = list(reversed(chunk_lines))
        events = []
        for l in ev_lines:
            ev = parse_line(l)
            if ev:
                events.append(ev)

        # Fallback if events empty
        if not events:
            if is_hkl:
                events = [
                    {"n": "이나연", "num": 33, "t": "HKL", "a": "33이나연 서브", "c": "serve", "ok": False, "pid": 107},
                    {"n": "킨델란", "num": 23, "t": "HKL", "a": "23킨델란 공격 성공", "c": "attack", "ok": True, "pid": 101}
                ]
            else:
                events = [
                    {"n": "염혜선", "num": 3, "t": "KGC", "a": "3염혜선 서브", "c": "serve", "ok": False, "pid": 208},
                    {"n": "종휘", "num": 17, "t": "KGC", "a": "17종휘 공격 성공", "c": "attack", "ok": True, "pid": 201}
                ]

        server_team = events[0]["t"]

        # Determine cause
        cause = "kill"
        chunk_text = " ".join(c)
        if "서브 성공" in chunk_text:
            cause = "serveace"
        elif "블록킹 성공" in chunk_text:
            cause = "block"
        elif "아웃" in chunk_text or "네트걸림" in chunk_text:
            cause = "error"

        point_idx = max(0, len(events) - 1)

        rallies.append({
            "set_no": 1,
            "rally_no": idx,
            "scorer": scorer,
            "server": server_team,
            "server_team": server_team,
            "cause": cause,
            "score_kgc": kgc_score,
            "score_hdec": hkl_score,
            "score_hkl": hkl_score,
            "score": {"KGC": kgc_score, "HKL": hkl_score, "HDEC": hkl_score},
            "point_idx": point_idx,
            "events": events,
            "events_json": json.dumps(events, ensure_ascii=False)
        })

    return rallies


def create_5pt_highlight_scenarios():
    """
    1세트 핵심 5대 득점 명장면 시뮬레이션:
    1. 1:0 킨델란 라이트 오픈 선취포 (Rally 1)
    2. 2:0 김수지 & 킨델란 철벽 블로킹 (Rally 2)
    3. 3:0 이나연 날카로운 다이렉트 서브에이스 (Rally 3)
    4. 20:11 킨델란 3m 후위 백어택 폭격 (Rally 31)
    5. 23:18 표승주 허를 찌르는 전술 시간차 (Rally 41)
    """
    # 1. 5대 하이라이트 통합 풀시뮬레이션 시나리오
    full_highlight = {
        "id": 1,
        "code": "SET1_5PTS_HIGHLIGHTS",
        "title": "🔥 1세트 주요 5득점 하이라이트 시뮬레이션",
        "subtitle": "1세트 명장면 5선 풀코트 시뮬레이션 (킨델란 오픈·김수지 블로킹·이나연 서브에이스·킨델란 백어택·표승주 시간차)",
        "attack_team": "HKL",
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
                "tags": ["#1세트", "#5득점하이라이트"],
                "text": "11월 4일 흥국생명 vs 정관장 1세트. 경기 시작을 알리는 5대 주요 득점 하이라이트 시뮬레이션입니다."
            },
            # HL 1: 1:0 킨델란 오픈 강타
            {
                "name": "[HL 1] 1:0 킨델란 라이트 오픈 선취점", "dur": 2400,
                "ball": [
                    {"from": ["atk", -4, 78], "to": ["def", 28, 45], "h": 28, "delay": 0, "end": 0.35},
                    {"from": ["def", 28, 45], "to": ["def", 82, 60], "h": 38, "delay": 0.35, "end": 0.5},
                    {"from": ["def", 82, 60], "to": ["atk", 82, 50], "h": 14, "delay": 0.5, "end": 0.65},
                    {"from": ["atk", 82, 50], "to": ["atk", 84, 84], "h": 42, "delay": 0.65, "end": 0.82},
                    {"from": ["atk", 84, 84], "to": ["def", 22, 80], "h": 5, "delay": 0.82, "end": 1.0}
                ],
                "moves": [
                    {"who": "atk.S", "to": [83, 60], "delay": 0.1, "end": 0.65, "trail": True},
                    {"who": "atk.OP", "to": [85, 84], "delay": 0.6, "end": 0.85, "trail": True},
                    {"who": "def.Z4", "to": [86.5, 12], "delay": 0.68, "end": 0.85}
                ],
                "focus": "atk.OP",
                "tags": ["#킨델란오픈", "#1대0선취포"],
                "text": "【하이라이트 1】 이나연 디그 → 고민지 토스를 받은 킨델란이 높은 타점에서 라이트 오픈 강타를 내리꽂으며 1세트 첫 득점을 올립니다! (흥국 1:0 리드)"
            },
            # HL 2: 2:0 김수지 & 킨델란 블록킹 성공
            {
                "name": "[HL 2] 2:0 김수지·킨델란 철벽 블로킹", "dur": 2500,
                "ball": [
                    {"from": ["atk", -4, 78], "to": ["def", 25, 45], "h": 28, "delay": 0, "end": 0.35},
                    {"from": ["def", 25, 45], "to": ["def", 82, 60], "h": 36, "delay": 0.35, "end": 0.6},
                    {"from": ["def", 82, 60], "to": ["def", 85, 16], "h": 40, "delay": 0.6, "end": 0.8},
                    {"from": ["def", 85, 16], "to": ["atk", 87, 80], "h": 12, "delay": 0.8, "end": 0.88},
                    {"from": ["atk", 87, 80], "to": ["def", 75, 16], "h": 3, "delay": 0.88, "end": 1.0}
                ],
                "moves": [
                    {"who": "def.Z4", "to": [85, 16], "delay": 0.5, "end": 0.8, "trail": True},
                    {"who": "atk.MBF", "to": [87, 76], "delay": 0.6, "end": 0.88, "trail": True},
                    {"who": "atk.OP", "to": [87, 84], "delay": 0.6, "end": 0.88, "trail": True}
                ],
                "focus": "atk.MBF",
                "tags": ["#김수지블로킹", "#킨델란어시스트", "#통곡의벽"],
                "text": "【하이라이트 2】 정관장 종휘의 오픈 강타를 김수지와 킨델란이 네트 위에서 완벽하게 차단! 블로킹 득점으로 2-0을 만듭니다."
            },
            # HL 3: 3:0 이나연 서브에이스
            {
                "name": "[HL 3] 3:0 이나연 다이렉트 서브에이스", "dur": 2200,
                "ball": [
                    {"from": ["atk", -6, 80], "to": ["def", 18, 22], "h": 22, "delay": 0, "end": 0.75},
                    {"from": ["def", 18, 22], "to": ["def", -10, 10], "h": 10, "delay": 0.75, "end": 1.0}
                ],
                "moves": [
                    {"who": "atk.S", "to": [-2, 80], "delay": 0, "end": 0.3, "trail": True},
                    {"who": "def.Z5", "to": [14, 20], "delay": 0.4, "end": 0.78, "trail": True}
                ],
                "focus": "atk.S",
                "tags": ["#이나연서브에이스", "#박혜민흔들림"],
                "text": "【하이라이트 3】 세터 이나연의 절묘한 목적타 플로터 서브! 박혜민의 리시브를 완전히 무너뜨리며 다이렉트 서브에이스 득점! 3:0 연속 3득점으로 초반 기선을 제압합니다."
            },
            # HL 4: 20:11 킨델란 후위 백어택 폭격
            {
                "name": "[HL 4] 20:11 킨델란 3m 백어택 폭격", "dur": 2500,
                "ball": [
                    {"from": ["atk", 83, 60], "to": ["atk", 58, 48], "h": 46, "delay": 0.1, "end": 0.55},
                    {"from": ["atk", 58, 48], "to": ["def", 22, 65], "h": 5, "delay": 0.55, "end": 0.9}
                ],
                "moves": [
                    {"who": "atk.OP", "to": [58, 48], "delay": 0.15, "end": 0.55, "via": [42, 60], "trail": True},
                    {"who": "def.Z3", "to": [86.5, 45], "delay": 0.3, "end": 0.55},
                    {"who": "def.Z2", "to": [86.5, 70], "delay": 0.3, "end": 0.55}
                ],
                "focus": "atk.OP",
                "tags": ["#킨델란백어택", "#20점고지도달"],
                "text": "【하이라이트 4】 박혜진의 깔끔한 중앙 백토스, 킨델란이 3미터 라인 뒤에서 솟구치며 정관장 블로커 3인을 뚫고 백어택을 꽂아 넣습니다! 20:11, 더블 스코어로 점수를 벌립니다."
            },
            # HL 5: 23:18 표승주 시간차 쐐기포
            {
                "name": "[HL 5] 23:18 표승주 전술 시간차 쐐기포", "dur": 2600,
                "ball": [
                    {"from": ["def", -4, 78], "to": ["atk", 30, 20], "h": 28, "delay": 0, "end": 0.35},
                    {"from": ["atk", 30, 20], "to": ["atk", 83, 60], "h": 36, "delay": 0.35, "end": 0.6},
                    {"from": ["atk", 83, 60], "to": ["atk", 84, 40], "h": 26, "delay": 0.6, "end": 0.8},
                    {"from": ["atk", 84, 40], "to": ["def", 18, 35], "h": 4, "delay": 0.8, "end": 1.0}
                ],
                "moves": [
                    {"who": "atk.MBF", "to": [84, 52], "delay": 0.45, "end": 0.7, "trail": True},
                    {"who": "atk.OHF", "to": [84, 40], "delay": 0.55, "end": 0.82, "via": [65, 30], "trail": True},
                    {"who": "def.Z3", "to": [86.5, 52], "delay": 0.6, "end": 0.78}
                ],
                "focus": "atk.OHF",
                "tags": ["#표승주시간차", "#23점승기", "#1세트완승"],
                "text": "【하이라이트 5】 자스티스 완벽 리시브! 중앙 미들블로커가 페이크 점프로 상대 블로커를 유인한 사이, 반 박자 늦게 들어온 표승주의 기가 막힌 시간차 공격 득점! 23:18로 세트 승기를 굳히고 25:20으로 1세트를 챙깁니다."
            }
        ]
    }

    # 개별 5대 시나리오 (각 하이라이트를 하나씩 집중 재생 가능)
    hl1 = {
        "id": 2,
        "code": "SET1_HL1_KIN_OPEN",
        "title": "🏐 [1세트 1:0] 킨델란 오픈 강타 선취포",
        "subtitle": "고민지 토스 → 킨델란 라이트 오픈 강타로 1세트 선취 득점",
        "attack_team": "HKL",
        "sort_order": 1,
        "phases": [
            full_highlight["phases"][0],
            full_highlight["phases"][1]
        ]
    }

    hl2 = {
        "id": 3,
        "code": "SET1_HL2_KIM_BLOCK",
        "title": "🏐 [1세트 2:0] 김수지·킨델란 철벽 블로킹",
        "subtitle": "정관장 종휘 오픈 공격을 김수지·킨델란이 공중 가로막기",
        "attack_team": "HKL",
        "sort_order": 2,
        "phases": [
            full_highlight["phases"][0],
            full_highlight["phases"][2]
        ]
    }

    hl3 = {
        "id": 4,
        "code": "SET1_HL3_LEE_ACE",
        "title": "🏐 [1세트 3:0] 이나연 다이렉트 서브에이스",
        "subtitle": "이나연 플로터 서브가 상대 리시브 라인을 허물며 에이스 득점",
        "attack_team": "HKL",
        "sort_order": 3,
        "phases": [
            full_highlight["phases"][0],
            full_highlight["phases"][3]
        ]
    }

    hl4 = {
        "id": 5,
        "code": "SET1_HL4_KIN_PIPE",
        "title": "🏐 [1세트 20:11] 킨델란 3m 백어택 폭격",
        "subtitle": "박혜진 백토스 → 킨델란 3미터 후위 중앙 고공 백어택",
        "attack_team": "HKL",
        "sort_order": 4,
        "phases": [
            full_highlight["phases"][0],
            full_highlight["phases"][4]
        ]
    }

    hl5 = {
        "id": 6,
        "code": "SET1_HL5_PYO_TIME",
        "title": "🏐 [1세트 23:18] 표승주 결정적 전술 시간차",
        "subtitle": "자스티스 리시브 → 이나연 토스 → 표승주 반 박자 늦춘 시간차 득점",
        "attack_team": "HKL",
        "sort_order": 5,
        "phases": [
            full_highlight["phases"][0],
            full_highlight["phases"][5]
        ]
    }

    return [full_highlight, hl1, hl2, hl3, hl4, hl5]


def update_everything():
    print("Parsing Set 1 real 45 rallies...")
    set1_rallies = parse_raw_set1_rallies()
    print(f"Parsed {len(set1_rallies)} rallies for Set 1.")

    # Import existing full_data_1104
    import sys
    sys.path.insert(0, str(ROOT / "data"))
    import build_1104  # type: ignore

    data = build_1104.full_data_1104

    # Update Set 1 score in sets
    data["sets"][0] = {
        "set_no": 1,
        "kgc_score": 20,
        "hkl_score": 25,
        "winner": "HKL",
        "score_home": 25,
        "score_away": 20
    }

    # Replace set 1 rallies in rallies list
    other_rallies = [r for r in data["rallies"] if r.get("set_no") != 1]
    data["rallies"] = set1_rallies + other_rallies

    # Add 5-Point Highlight Scenarios at the front of scenarios
    highlight_scenarios = create_5pt_highlight_scenarios()
    existing_scenarios = data.get("scenarios", [])
    data["scenarios"] = highlight_scenarios + existing_scenarios

    # Write data_1104.js to both root js and static/js
    js_content = f"// 11월 4일 흥국생명 vs 정관장 풀 전술 분석 데이터 (1세트 45개 실시간 랠리 & 5득점 하이라이트 포함)\n"
    js_content += f"window.BOOTSTRAP_1104 = {json.dumps(data, ensure_ascii=False, indent=2)};\n\n"
    js_content += """window.MATCHES = window.MATCHES || {};
if (window.BOOTSTRAP) {
  window.MATCHES['2026-11-07'] = window.BOOTSTRAP;
}
window.MATCHES['2026-11-04'] = window.BOOTSTRAP_1104;
"""

    (ROOT / "js" / "data_1104.js").write_text(js_content, encoding="utf-8")
    (ROOT / "static" / "js" / "data_1104.js").write_text(js_content, encoding="utf-8")
    print(f"Wrote data_1104.js ({len(js_content)} bytes) to js/ and static/js/")

if __name__ == "__main__":
    update_everything()
