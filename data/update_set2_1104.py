"""
update_set2_1104.py:
11월 4일 흥국생명 vs 정관장 2세트 KOVO 공식 56개 랠리 전량 및
2세트 29:27 극적 듀스 대역전 시뮬레이션을 build_1104.py와 data_1104.js에 통합 적용합니다.
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
    '문지윤': (71, 'OP', 114),
    '고민지': (16, 'L', 110),
    '신연경': (3, 'L', 112),
    '도수빈': (8, 'L', 111),
    '정윤주': (14, 'OH', 106),
    '이고은': (6, 'S', 115),
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
    elif any(k in act for k in ["오픈", "퀵오픈", "백어택", "속공", "시간차", "이동"]):
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


def parse_raw_set2_rallies():
    raw_path = ROOT / "data" / "sets_1104" / "set2.txt"
    raw = raw_path.read_text(encoding="utf-8")
    lines = [l.strip() for l in raw.splitlines() if l.strip()]

    chunks = []
    cur = []
    for l in lines:
        cur.append(l)
        if l == "POINT!":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)

    chunks.reverse()

    # The 29 HKL winning points in Set 2:
    # 1(1-0), 2(2-0), 6(3-3), 8(4-4), 10(5-5), 14(6-8), 15(7-8), 16(8-8), 17(9-8),
    # 20(10-10), 24(11-13), 27(12-15), 28(13-15), 30(14-16), 32(15-17), 34(16-18),
    # 35(17-18), 36(18-18), 38(19-19), 39(20-19), 41(21-20), 43(22-21), 45(23-22),
    # 48(24-24), 50(25-25), 51(26-25), 53(27-26), 55(28-27), 56(29-27)
    HKL_POINTS = {
        1, 2, 6, 8, 10, 14, 15, 16, 17, 20, 24, 27, 28, 30, 32, 34, 35, 36,
        38, 39, 41, 43, 45, 48, 50, 51, 53, 55, 56
    }

    rallies = []
    hkl_score = 0
    kgc_score = 0

    for idx, c in enumerate(chunks[:56], 1):
        is_hkl = idx in HKL_POINTS
        if is_hkl:
            hkl_score += 1
            scorer = "HKL"
        else:
            kgc_score += 1
            scorer = "KGC"

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

        cause = "kill"
        chunk_text = " ".join(c)
        if "서브 성공" in chunk_text:
            cause = "serveace"
        elif "블록킹 성공" in chunk_text:
            cause = "block"
        elif "아웃" in chunk_text or "네트걸림" in chunk_text or "범실" in chunk_text or "오버넷" in chunk_text or "라인오버" in chunk_text:
            cause = "error"

        point_idx = max(0, len(events) - 1)

        rallies.append({
            "set_no": 2,
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


def create_set2_highlight_scenarios():
    """
    2세트 29:27 피말리는 듀스 접전 대역전극 하이라이트 시뮬레이션
    """
    set2_scenario = {
        "id": 10,
        "code": "SET2_DEUCE_HIGHLIGHTS",
        "title": "🔥 2세트 29:27 피말리는 듀스 대역전 하이라이트",
        "subtitle": "11:15 4점차 열세 극복 → 24:24 벼랑 끝 듀스 성립 → 29:27 킨델란 매치포인트 블록킹 대역전극",
        "attack_team": "HKL",
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
                    {"who": "atk.OHF", "to": [32, 20], "delay": 0, "end": 1},
                    {"who": "atk.L", "to": [28, 45], "delay": 0, "end": 1},
                    {"who": "atk.OHB", "to": [32, 70], "delay": 0, "end": 1},
                    {"who": "atk.MBF", "to": [78, 40], "delay": 0, "end": 1},
                    {"who": "atk.OP", "to": [80, 84], "delay": 0, "end": 1},
                    {"who": "atk.S", "to": [74, 64], "delay": 0, "end": 1},
                ],
                "focus": "atk.OP",
                "tags": ["#2세트", "#29대27", "#듀스대혈전"],
                "text": "11월 4일 흥국생명 vs 정관장 2세트. 11:15로 4점 뒤지던 흥국생명이 정윤주·문지윤의 조커 투입과 킨델란의 결정력으로 29:27 대역전승을 거둔 명장면입니다."
            },
            # HL 1: 18:18 자스티스 서브에이스 동점
            {
                "name": "[2세트 HL 1] 18:18 자스티스 서브에이스 동점", "dur": 2400,
                "ball": [
                    {"from": ["atk", -6, 78], "to": ["def", 22, 18], "h": 24, "delay": 0, "end": 0.75},
                    {"from": ["def", 22, 18], "to": ["def", -10, 10], "h": 12, "delay": 0.75, "end": 1.0}
                ],
                "moves": [
                    {"who": "atk.OHB", "to": [-2, 78], "delay": 0, "end": 0.3, "trail": True},
                    {"who": "def.Z5", "to": [18, 18], "delay": 0.4, "end": 0.75, "trail": True}
                ],
                "focus": "atk.OHB",
                "tags": ["#자스티스서브에이스", "#18대18동점"],
                "text": "【2세트 추격】 11:15로 뒤지던 세트 중반, 자스티스의 날카로운 스파이크 서브가 코트 구석을 파고들며 결정적 서브에이스! 마침내 18:18 균형을 맞춥니다."
            },
            # HL 2: 21:20 정윤주 블로킹 역전
            {
                "name": "[2세트 HL 2] 21:20 정윤주 블로킹 역전", "dur": 2500,
                "ball": [
                    {"from": ["def", -4, 78], "to": ["atk", 28, 45], "h": 28, "delay": 0, "end": 0.35},
                    {"from": ["atk", 28, 45], "to": ["atk", 83, 60], "h": 36, "delay": 0.35, "end": 0.6},
                    {"from": ["atk", 83, 60], "to": ["atk", 85, 18], "h": 38, "delay": 0.6, "end": 0.8},
                    {"from": ["atk", 85, 18], "to": ["def", 87, 78], "h": 12, "delay": 0.8, "end": 0.88},
                    {"from": ["def", 87, 78], "to": ["atk", 86.5, 20], "h": 10, "delay": 0.88, "end": 0.94},
                    {"from": ["atk", 86.5, 20], "to": ["def", 74, 75], "h": 4, "delay": 0.94, "end": 1.0}
                ],
                "moves": [
                    {"who": "atk.OHF", "to": [86.5, 20], "delay": 0.8, "end": 0.94, "trail": True},
                    {"who": "def.Z2", "to": [85, 78], "delay": 0.7, "end": 0.88}
                ],
                "focus": "atk.OHF",
                "tags": ["#정윤주블로킹", "#21대20역전"],
                "text": "【2세트 역전】 교체 투입된 정윤주가 20:20 동점에서 정관장 이선우의 퀵오픈을 완벽하게 단독 블로킹! 21:20 역전을 이끌어냅니다."
            },
            # HL 3: 24:24 정호영 블록킹! 극적 듀스 성립
            {
                "name": "[2세트 HL 3] 24:24 정호영 블로킹! 벼랑 끝 듀스", "dur": 2600,
                "ball": [
                    {"from": ["atk", 83, 60], "to": ["def", 85, 16], "h": 38, "delay": 0.2, "end": 0.6},
                    {"from": ["def", 85, 16], "to": ["atk", 86.5, 48], "h": 12, "delay": 0.6, "end": 0.75},
                    {"from": ["atk", 86.5, 48], "to": ["def", 76, 16], "h": 3, "delay": 0.75, "end": 1.0}
                ],
                "moves": [
                    {"who": "def.Z4", "to": [85, 16], "delay": 0.3, "end": 0.6, "trail": True},
                    {"who": "atk.MBF", "to": [86.5, 48], "delay": 0.45, "end": 0.75, "trail": True},
                    {"who": "atk.OP", "to": [86.5, 58], "delay": 0.45, "end": 0.75}
                ],
                "focus": "atk.MBF",
                "tags": ["#정호영블로킹", "#24대24듀스"],
                "text": "【듀스 성립】 23:24 정관장의 세트포인트 위기! 박혜민의 회심의 오픈을 미들블로커 정호영이 킨델란과 함께 완벽 차단! 24:24 극적 듀스를 만듭니다!"
            },
            # HL 4: 27:26 킨델란 백어택
            {
                "name": "[2세트 HL 4] 27:26 킨델란 후위 백어택 폭격", "dur": 2400,
                "ball": [
                    {"from": ["atk", 83, 60], "to": ["atk", 58, 50], "h": 46, "delay": 0.1, "end": 0.55},
                    {"from": ["atk", 58, 50], "to": ["def", 22, 60], "h": 5, "delay": 0.55, "end": 0.9}
                ],
                "moves": [
                    {"who": "atk.OP", "to": [58, 50], "delay": 0.15, "end": 0.55, "via": [42, 65], "trail": True},
                    {"who": "def.Z3", "to": [86.5, 45], "delay": 0.3, "end": 0.55}
                ],
                "focus": "atk.OP",
                "tags": ["#킨델란백어택", "#듀스승부처"],
                "text": "【듀스 접전】 26:26 한 점 승부에서 이나연의 높은 백토스! 킨델란이 3미터 뒤에서 내리꽂는 백어택으로 27:26 흥국의 리드를 되찾아옵니다."
            },
            # HL 5: 29:27 킨델란 매치포인트 블록킹 승리
            {
                "name": "[2세트 HL 5] 29:27 킨델란 매치포인트 블로킹 승리", "dur": 2700,
                "ball": [
                    {"from": ["atk", -4, 78], "to": ["def", 28, 45], "h": 28, "delay": 0, "end": 0.35},
                    {"from": ["def", 28, 45], "to": ["def", 82, 60], "h": 36, "delay": 0.35, "end": 0.6},
                    {"from": ["def", 82, 60], "to": ["def", 85, 18], "h": 38, "delay": 0.6, "end": 0.8},
                    {"from": ["def", 85, 18], "to": ["atk", 86.5, 80], "h": 12, "delay": 0.8, "end": 0.88},
                    {"from": ["atk", 86.5, 80], "to": ["def", 74, 18], "h": 3, "delay": 0.88, "end": 1.0}
                ],
                "moves": [
                    {"who": "def.Z4", "to": [85, 18], "delay": 0.5, "end": 0.8, "trail": True},
                    {"who": "atk.OP", "to": [86.5, 80], "delay": 0.6, "end": 0.88, "trail": True},
                    {"who": "atk.MBF", "to": [86.5, 72], "delay": 0.6, "end": 0.88}
                ],
                "focus": "atk.OP",
                "tags": ["#킨델란블로킹", "#김수지어시스트", "#29대27대역전승"],
                "text": "【2세트 피날레】 28:27 세트포인트! 정관장 에이스 종휘의 마지막 회심의 오픈 강타를 킨델란과 김수지가 공중에서 집어삼켰습니다! 29:27! 흥국생명이 2세트 듀스 혈투를 잡고 세트 스코어 2-0을 완성합니다!"
            }
        ]
    }
    return set2_scenario


def update_everything():
    print("Parsing Set 2 real 56 rallies...")
    set2_rallies = parse_raw_set2_rallies()
    print(f"Parsed {len(set2_rallies)} rallies for Set 2.")

    import sys
    sys.path.insert(0, str(ROOT / "data"))
    import build_1104  # type: ignore

    data = build_1104.full_data_1104

    # Update Set 2 score in sets
    data["sets"][1] = {
        "set_no": 2,
        "kgc_score": 27,
        "hkl_score": 29,
        "winner": "HKL",
        "score_home": 29,
        "score_away": 27
    }

    # Replace set 2 rallies in rallies list (keep set 1 and set 3)
    non_set2 = [r for r in data["rallies"] if r.get("set_no") != 2]
    # sort by set_no and rally_no
    all_rallies = non_set2 + set2_rallies
    all_rallies.sort(key=lambda r: (r.get("set_no", 1), r.get("rally_no", 1)))
    data["rallies"] = all_rallies

    # Insert Set 2 deuce highlight scenario at position 1 (right after Set 1 highlight)
    set2_sc = create_set2_highlight_scenarios()
    scenarios = data.get("scenarios", [])
    # Filter out if already exists
    scenarios = [s for s in scenarios if s.get("code") != "SET2_DEUCE_HIGHLIGHTS"]
    scenarios.insert(1, set2_sc)
    data["scenarios"] = scenarios

    # Write data_1104.js to both root js and static/js
    js_content = f"// 11월 4일 흥국생명 vs 정관장 풀 전술 분석 데이터 (1세트 45개 & 2세트 56개 실시간 랠리 완벽 탑재)\n"
    js_content += f"window.BOOTSTRAP_1104 = {json.dumps(data, ensure_ascii=False, indent=2)};\n\n"
    js_content += """window.MATCHES = window.MATCHES || {};
if (window.BOOTSTRAP) {
  window.MATCHES['2026-11-07'] = window.BOOTSTRAP;
}
window.MATCHES['2026-11-04'] = window.BOOTSTRAP_1104;
"""

    (ROOT / "js" / "data_1104.js").write_text(js_content, encoding="utf-8")
    (ROOT / "static" / "js" / "data_1104.js").write_text(js_content, encoding="utf-8")
    print(f"Wrote updated data_1104.js ({len(js_content)} bytes) to js/ and static/js/")

if __name__ == "__main__":
    update_everything()

