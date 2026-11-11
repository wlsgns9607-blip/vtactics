"""
11월 4일 흥국생명 vs 정관장 1세트 상세 45개 랠리 및 5득점 하이라이트 시뮬레이션 생성기
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
    # e.g. "33이나연 서브", "23킨델란 오픈 성공", "11김수지 블록킹 성공"
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


def parse_set1():
    raw = (ROOT / "data" / "sets_1104" / "set1.txt").read_text(encoding="utf-8")
    lines = [l.strip() for l in raw.splitlines() if l.strip()]

    combined = []
    i = 0
    while i < len(lines):
        l = lines[i]
        if l.isdigit() and i + 1 < len(lines) and re.match(r"^[가-힣]+ ", lines[i+1]):
            combined.append(l + lines[i+1])
            i += 2
        else:
            combined.append(l)
            i += 1

    rev = list(reversed(combined))
    point_indices = [idx for idx, l in enumerate(rev) if l == "POINT!"]

    rallies = []
    start = 0
    hkl_score = 0
    kgc_score = 0

    for r_idx, pi in enumerate(point_indices, 1):
        chunk = rev[start:pi+1]
        start = pi + 1

        # Check for trailing lines that belong to this point before the next serve/point
        # e.g. blocker who failed or assist
        # look ahead until next serve or next event
        events = []
        scores_found = []
        for l in chunk:
            if "현재 점수:" in l:
                scores_found.append(int(l.split(":")[-1]))
            ev = parse_line(l)
            if ev:
                events.append(ev)

        # Determine scorer and point outcome
        # If there are two score numbers, high one or diff from previous gives current score
        # Let's inspect the last action before POINT!
        last_ev = events[-1] if events else None
        last_line = chunk[-2] if len(chunk) >= 2 else ""

        scorer = "HKL"
        cause = "kill"
        if "서브 아웃" in chunk or "서브 네트걸림" in chunk:
            cause = "error"
            # error by who?
            for ev in events:
                if ev["c"] == "serve":
                    scorer = "KGC" if ev["t"] == "HKL" else "HKL"
        elif "스파이크서브 아웃" in chunk or "스파이크서브 네트걸림" in chunk:
            cause = "error"
            for ev in events:
                if ev["c"] == "serve":
                    scorer = "KGC" if ev["t"] == "HKL" else "HKL"
        elif "네트걸림" in chunk or "아웃" in chunk:
            cause = "error"
            for l in reversed(chunk):
                if "네트걸림" in l or "아웃" in l:
                    ev = parse_line(l)
                    if ev:
                        scorer = "KGC" if ev["t"] == "HKL" else "HKL"
                    break
        elif any("블록킹 성공" in l for l in chunk):
            cause = "block"
            for l in reversed(chunk):
                if "블록킹 성공" in l:
                    ev = parse_line(l)
                    if ev:
                        scorer = ev["t"]
                    break
        elif any("서브 성공" in l for l in chunk):
            cause = "serveace"
            for l in reversed(chunk):
                if "서브 성공" in l:
                    ev = parse_line(l)
                    if ev:
                        scorer = ev["t"]
                    break
        elif any("성공" in l for l in chunk):
            cause = "kill"
            for l in reversed(chunk):
                if "성공" in l:
                    ev = parse_line(l)
                    if ev:
                        scorer = ev["t"]
                    break

        if scorer == "HKL":
            hkl_score += 1
        else:
            kgc_score += 1

        server_team = events[0]["t"] if events else ("HKL" if scorer == "HKL" else "KGC")

        point_idx = max(0, len(events) - 1)
        rallies.append({
            "set_no": 1,
            "rally_no": r_idx,
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
            "events_json": json.dumps(events, ensure_ascii=False),
        })

    return rallies

if __name__ == "__main__":
    rallies = parse_set1()
    print(f"Generated {len(rallies)} rallies.")
    print(f"Final Set 1 Score: HKL {rallies[-1]['score_hkl']} : KGC {rallies[-1]['score_kgc']}")

