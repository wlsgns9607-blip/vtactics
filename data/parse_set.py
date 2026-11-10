"""
KOVO 문자중계 로그 → 세트별 선수/팀 기록, 랠리(득점 단위) 이벤트 추출

  python data/parse_set.py data/sets/set1.txt

로그는 최신 플레이가 위에 오는 역순이라 뒤집어서 시간순으로 읽는다.

집계 기준 (4세트 합산을 경기 전체 기록표와 대조해 198개 항목 전부 일치 확인)
  공격   : 오픈·퀵오픈·속공·시간차·이동·백어택     성공 = '성공'
  블로킹  : 블록킹·블록킹 성공/실패·유효 블로킹     성공 = '블록킹 성공'  (블록킹 어시스트는 시도에서 제외)
  세트   : 세트·세트 정확·세트 범실                성공 = '세트 정확'
  디그   : 디그·디그 실패·디그 범실                성공 = 결과 표시 없는 '디그'
  리시브  : 리시브·리시브 정확·리시브 실패           성공 = '리시브 정확'
  서브   : 서브·스파이크서브                       성공 = '성공'(에이스)

랠리 구분: 서브 이벤트로 시작. 'POINT!' 직전의 마지막 이벤트가 득점 원인
  (성공 → 그 팀 득점, 범실/실패 → 상대 팀 득점). POINT! 뒤에 이어지는 블로킹 기록은 같은 랠리에 포함.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

ROSTER = {
    "KGC": ["종휘", "신은지", "박은진", "박여름", "이지수", "박혜민", "염혜선", "오세인", "최서현",
            "최효서", "김아중", "노란", "이선우", "전다빈", "곽선옥", "김지윤", "도수빈"],
    "HDEC": ["조던", "메가", "이예림", "이채영", "배유나", "김희진", "김다인", "나현수", "김연견",
             "김사랑", "한미르", "이민영", "강서우", "구솔", "이영주", "정지윤"],
}
TEAM_OF = {n: t for t, ns in ROSTER.items() for n in ns}
OTHER = {"KGC": "HDEC", "HDEC": "KGC"}
ATTACKS = ("백어택", "퀵오픈", "시간차", "속공", "이동", "오픈")
SERVES = ("스파이크서브", "서브")
ERR_WORDS = ("아웃", "범실", "네트걸림", "오버넷", "라인오버", "터치넷", "포히트")
EVENT = re.compile(r"^(\d+)([가-힣]+) (.+)$")
CATS = ["attack", "block", "set", "dig", "receive", "serve"]


def merged_lines(path):
    """'88' + '메가 시간차 성공' 처럼 두 줄로 쪼개진 기록을 한 줄로 합친다."""
    raw = [l.strip() for l in Path(path).read_text(encoding="utf-8").splitlines()]
    lines, i = [], 0
    while i < len(raw):
        if raw[i].isdigit() and i + 1 < len(raw) and re.match(r"^[가-힣]+ ", raw[i + 1]):
            lines.append(raw[i] + raw[i + 1]); i += 2
        else:
            lines.append(raw[i]); i += 1
    return lines


def read_events(path):
    lines = merged_lines(path)
    events = []
    for l in reversed(lines):
        m = EVENT.match(l)
        if m and m.group(2) in TEAM_OF:
            events.append((m.group(2), m.group(3)))
    return events, lines


def classify(action):
    """(분류, 성공여부)"""
    if action.startswith(SERVES):
        return "serve", action.endswith("성공")
    if action.startswith(ATTACKS):
        return "attack", action.endswith("성공")
    if action == "블록킹 어시스트":
        return "block_assist", False
    if action.startswith("블록킹") or action == "유효 블로킹":
        return "block", action == "블록킹 성공"
    if action.startswith("세트"):
        return "set", action == "세트 정확"
    if action.startswith("디그"):
        return "dig", action == "디그"
    if action.startswith("리시브"):
        return "receive", action == "리시브 정확"
    return None, False


def aggregate(events):
    stat = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # name -> cat -> [성공, 시도]
    extra = defaultdict(lambda: defaultdict(int))
    for name, action in events:
        cat, ok = classify(action)
        if not cat:
            continue
        if cat == "block_assist":
            extra[name]["blk_assist"] += 1
            continue
        stat[name][cat][1] += 1
        if ok:
            stat[name][cat][0] += 1
        if action.endswith(ERR_WORDS):
            extra[name]["errors"] += 1
    return stat, extra


def final_score(lines):
    nums = [int(l.split(":")[1]) for l in lines[:6] if l.startswith("현재 점수:")]
    return nums[:2]


def pct(m, t):
    return f"{m / t * 100:.1f}%" if t else "-"


# ───────────── 랠리 단위 파싱 ─────────────
def chrono_tokens(path):
    toks = []
    for l in reversed(merged_lines(path)):
        if l == "POINT!":
            toks.append(("P",))
            continue
        m = EVENT.match(l)
        if m and m.group(2) in TEAM_OF:
            toks.append(("E", int(m.group(1)), m.group(2), m.group(3)))
    return toks


def cause_of(ev):
    """득점 원인: kill / blockkill / out / net / overnet / touchnet / drop / fault"""
    a, c = ev["a"], ev["c"]
    if ev["ok"] and c in ("attack", "serve"):
        return "kill"
    if ev["ok"] and c == "block":
        return "blockkill"
    if "라인오버" in a or a.endswith("아웃"):
        return "out"
    if "네트걸림" in a:
        return "net"
    if "오버넷" in a:
        return "overnet"
    if "터치넷" in a:
        return "touchnet"
    if "실패" in a:
        return "drop"
    return "fault"


def parse_rallies(path):
    """랠리 리스트 반환. 각 랠리: events(시간순), point_idx, scorer, cause, 득점 후 점수."""
    rallies, cur = [], None
    for t in chrono_tokens(path):
        if t[0] == "E":
            _, num, name, act = t
            cat, ok = classify(act)
            if cat is None:
                continue
            ev = {"n": name, "num": num, "t": TEAM_OF[name], "a": act, "c": cat, "ok": ok}
            if cat == "serve":
                cur = {"events": [ev], "point_idx": None}
                rallies.append(cur)
            elif cur is not None:
                cur["events"].append(ev)
        elif cur is not None and cur["point_idx"] is None:
            cur["point_idx"] = len(cur["events"])
    score = {"KGC": 0, "HDEC": 0}
    for i, r in enumerate(rallies, 1):
        last = r["events"][r["point_idx"] - 1]
        r["scorer"] = last["t"] if last["ok"] else OTHER[last["t"]]
        r["cause"] = cause_of(last)
        r["server_team"] = r["events"][0]["t"]
        r["no"] = i
        score[r["scorer"]] += 1
        r["score"] = dict(score)
    return rallies


def jersey_numbers(paths):
    nums = {}
    for p in paths:
        for t in chrono_tokens(p):
            if t[0] == "E":
                nums.setdefault(t[2], t[1])
    return nums


def score_check(path):
    rs = parse_rallies(path)
    return rs[-1]["score"] if rs else {"KGC": 0, "HDEC": 0}


def report(path):
    events, lines = read_events(path)
    stat, extra = aggregate(events)
    cats = [("attack", "공격"), ("block", "블로킹"), ("set", "세트"), ("dig", "디그"), ("receive", "리시브")]
    print(f"[{Path(path).stem}] 이벤트 {len(events)}개, 최종 점수 표기 {final_score(lines)}")
    for team in ROSTER:
        print(f"\n== {team} ==")
        tot = defaultdict(lambda: [0, 0])
        for name in ROSTER[team]:
            if name not in stat:
                continue
            s = stat[name]
            row = []
            for c, label in cats:
                m, t = s[c]
                tot[c][0] += m; tot[c][1] += t
                row.append(f"{label} {m}/{t}({pct(m, t)})" if t else f"{label} -")
            print(f"  {name:<4} " + " | ".join(row) + f" | 범실 {extra[name]['errors']}")
        print("  팀합계 " + " | ".join(f"{l} {tot[c][0]}/{tot[c][1]}({pct(*tot[c])})" for c, l in cats))
    return stat, extra


if __name__ == "__main__":
    report(sys.argv[1] if len(sys.argv) > 1 else "data/sets/set1.txt")
