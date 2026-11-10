"""
전술 시나리오 정의 (DB scenarios 테이블에 JSON으로 저장됨)

좌표계 (팀 로컬 좌표, 단위 = 10cm)
  - 자기 팀 엔드라인 x=0, 네트 x=90, 3m 라인 x=60
  - y=0 : 자기 팀 기준 왼쪽 사이드라인 (4번 자리 쪽)
  - y=90: 오른쪽 사이드라인 (2번·1번 자리 쪽)
  - 화면에서 팀이 오른쪽 진영이면 앱이 (180-x, 90-y)로 자동 변환

선수 지정 (who)
  - "atk.역할" / "def.역할"  (atk = 시나리오 공격팀, def = 상대팀)
  - 역할: S, OP, OHF(전위 OH), OHB(후위 OH), MBF(전위 MB), L(리베로)
  - 자리: Z1~Z6 (현재 로테이션에서 해당 자리에 있는 선수)
  → 로테이션을 돌리면 같은 전술을 다른 선수가 수행하고, 해설도 자동으로 바뀜

공 (ball): 리스트, 각 구간 {"from":[팀,x,y], "to":[팀,x,y], "h":최고높이, "delay", "end"}
  - delay/end 는 페이즈 시간 대비 0~1 비율

해설 템플릿
  - {atk.OHF.name}, {atk.OHF.attPct}, {atk.L.dig}, {def.team.blk} 등
"""

# 자주 쓰는 위치
SET_SPOT = [83, 60]          # 세터 토스 위치 (2·3번 사이 네트 앞)


def mv(who, to, via=None, delay=0.0, end=1.0, trail=False):
    m = {"who": who, "to": to, "delay": delay, "end": end}
    if via:
        m["via"] = via
    if trail:
        m["trail"] = True
    return m


def ball(f, t, h=20, delay=0.0, end=1.0):
    return {"from": f, "to": t, "h": h, "delay": delay, "end": end}


SCENARIOS = [
    # ─────────────────────────────────────────────────────────
    {
        "code": "A_QUICK",
        "title": "리시브 안정 후 A속공 전개",
        "subtitle": "정관장 리시브 → 세터 → 미들 A속공",
        "attack_team": "KGC",
        "phases": [
            {"name": "포메이션", "dur": 1300,
             "moves": [
                 mv("def.Z1", [-6, 78]),
                 mv("def.Z2", [84, 78]), mv("def.Z3", [84, 45]), mv("def.Z4", [84, 12]),
                 mv("def.Z5", [22, 15]), mv("def.Z6", [22, 45]),
                 mv("atk.OHF", [32, 20]), mv("atk.L", [28, 45]), mv("atk.OHB", [32, 70]),
                 mv("atk.MBF", [78, 40]), mv("atk.OP", [80, 84]), mv("atk.S", [74, 64]),
             ],
             "focus": "atk.L",
             "tags": ["#서브리시브", "#3인리시브"],
             "text": "{def.team.short} {def.Z1.name} 서브 준비. {atk.team.short|은는} {atk.OHF.name}·{atk.L.name}·{atk.OHB.name} 3인 리시브 라인을 세웁니다."},
            {"name": "서브", "dur": 1300,
             "ball": [ball(["def", -4, 78], ["atk", 28, 46], h=32)],
             "moves": [mv("def.Z1", [15, 75], delay=0.35),
                       mv("atk.S", SET_SPOT, delay=0.15, end=0.9, trail=True)],
             "focus": "atk.S",
             "tags": ["#세터침투"],
             "text": "서브가 리베로 {atk.L.name} 쪽으로 향합니다. 세터 {atk.S.name|은는} 서브와 동시에 네트 앞으로 파고듭니다."},
            {"name": "리시브", "dur": 1100,
             "ball": [ball(["atk", 28, 46], ["atk", 83, 60], h=40)],
             "moves": [mv("atk.MBF", [70, 50]), mv("atk.OHF", [58, 6]),
                       mv("atk.OP", [60, 88]), mv("atk.OHB", [44, 58])],
             "focus": "atk.L",
             "tags": ["#정확한리시브"],
             "text": "{atk.L.name}의 정확한 리시브! 공이 세터 머리 위로 그대로 올라갑니다. 이 경기 디그 {atk.L.dig}를 기록한 리베로다운 안정감."},
            {"name": "토스·도움닫기", "dur": 800,
             "ball": [ball(["atk", 83, 60], ["atk", 85, 48], h=6, delay=0.45)],
             "moves": [mv("atk.MBF", [85, 48], via=[78, 42], end=0.6, trail=True),
                       mv("atk.OHF", [80, 10], via=[68, 2], trail=True),
                       mv("atk.OP", [80, 84], via=[70, 90], trail=True),
                       mv("def.Z3", [86.5, 40], delay=0.55)],
             "focus": "atk.MBF",
             "tags": ["#A속공", "#동시다발공격"],
             "text": "토스보다 먼저 {atk.MBF.name} 선수가 뜹니다. A속공! 양 측면의 {atk.OHF.name}·{atk.OP.name}도 함께 도움닫기해 블로커를 묶어둡니다."},
            {"name": "속공", "dur": 700,
             "ball": [ball(["atk", 85, 48], ["def", 40, 34], h=3)],
             "moves": [mv("def.Z6", [34, 38], delay=0.3)],
             "focus": "atk.MBF",
             "tags": ["#템포"],
             "text": "{atk.MBF.name}의 속공이 꽂힙니다! {def.team.short} 미들 블로커는 한 박자 늦게 따라왔습니다. ({atk.MBF.name} 공격 성공률 {atk.MBF.attPctS})"},
            {"name": "분석", "dur": 1800, "result": "atk",
             "moves": [],
             "focus": "atk.MBF",
             "tags": ["#블로킹우회"],
             "text": "{atk.team.short} 득점. 이 경기 {def.team.short}의 팀 블로킹은 {def.team.blk}에 그쳤습니다. 리시브가 세터에게 정확히 가면 빠른 중앙 공격으로 블로킹을 피해 갈 수 있다는 것을 보여준 장면."},
        ],
    },
    # ─────────────────────────────────────────────────────────
    {
        "code": "PIPE",
        "title": "백어택(파이프) 반격 상황",
        "subtitle": "현대건설 디그 → 미들 페이크 → 후위 파이프",
        "attack_team": "HDEC",
        "phases": [
            {"name": "포메이션", "dur": 1300,
             "moves": [
                 mv("def.S", SET_SPOT), mv("def.OHF", [60, 8]), mv("def.MBF", [76, 45]),
                 mv("def.OP", [62, 86]), mv("def.L", [30, 45]), mv("def.OHB", [36, 66]),
                 mv("atk.Z2", [85, 80]), mv("atk.Z3", [85, 60]), mv("atk.Z4", [72, 14]),
                 mv("atk.Z1", [26, 74]), mv("atk.Z6", [24, 48]), mv("atk.Z5", [32, 22]),
             ],
             "ball": [ball(["def", 40, 50], ["def", 83, 60], h=38)],
             "focus": "def.S",
             "tags": ["#수비포메이션"],
             "text": "{def.team.short}의 공격 전개. {atk.team.short|은는} 전위 블로킹과 후위 디그 라인으로 대비합니다."},
            {"name": "상대 공격", "dur": 1200,
             "ball": [ball(["def", 83, 60], ["def", 85, 11], h=42)],
             "moves": [mv("def.OHF", [85, 10], via=[70, 2], delay=0.3, trail=True),
                       mv("atk.Z2", [86.5, 82], delay=0.5), mv("atk.Z3", [86.5, 74], delay=0.4)],
             "focus": "def.OHF",
             "tags": ["#오픈공격"],
             "text": "{def.S.name}의 토스가 레프트 {def.OHF.name}에게. 공격 점유율 {def.OHF.shareS}, 팀 공격의 중심입니다."},
            {"name": "디그", "dur": 900,
             "ball": [ball(["def", 85, 11], ["atk", 32, 24], h=5)],
             "moves": [mv("atk.Z5", [32, 24], end=0.5)],
             "focus": "atk.Z5",
             "tags": ["#디그", "#반격시작"],
             "text": "크로스 공격을 {atk.Z5.name} 선수가 걷어 올립니다! 반격 기회."},
            {"name": "세터 연결", "dur": 1000,
             "ball": [ball(["atk", 32, 24], ["atk", 82, 55], h=38)],
             "moves": [mv("atk.S", [82, 55], end=0.85, trail=True),
                       mv("atk.OHB", [30, 50]), mv("atk.MBF", [74, 46]),
                       mv("atk.OHF", [60, 8]), mv("atk.OP", [60, 86]),
                       mv("def.Z4", [84, 16]), mv("def.Z3", [84, 45]), mv("def.Z2", [84, 76]),
                       mv("def.Z5", [20, 15]), mv("def.Z6", [22, 45]), mv("def.Z1", [20, 76])],
             "focus": "atk.S",
             "tags": ["#트랜지션"],
             "text": "{atk.S.name} 세터에게 연결. 후위의 {atk.OHB.name|은는} 3m 라인 뒤로 물러나 도움닫기 거리를 확보합니다."},
            {"name": "파이프 토스", "dur": 950,
             "ball": [ball(["atk", 82, 55], ["atk", 57, 46], h=24, delay=0.3)],
             "moves": [mv("atk.MBF", [85, 42], via=[80, 38], end=0.45, trail=True),
                       mv("atk.OHB", [56, 46], via=[44, 42], delay=0.15, trail=True),
                       mv("atk.OHF", [80, 10], via=[68, 2], trail=True),
                       mv("atk.OP", [80, 84], via=[70, 90], trail=True),
                       mv("def.Z3", [86.5, 34], end=0.45),
                       mv("def.Z4", [86.5, 40], delay=0.7)],
             "focus": "atk.OHB",
             "tags": ["#파이프", "#미들페이크"],
             "text": "미들 {atk.MBF.name}의 속공 페이크에 상대 미들 블로커가 먼저 뜹니다. 토스는 뒤로! {atk.OHB.name}의 파이프!"},
            {"name": "백어택", "dur": 700,
             "ball": [ball(["atk", 57, 46], ["def", 24, 58], h=4)],
             "moves": [mv("def.Z6", [26, 56], delay=0.35)],
             "focus": "atk.OHB",
             "tags": ["#블로킹분산"],
             "text": "3m 라인 뒤에서 때린 백어택이 블로킹 한 장을 넘어 코트 깊숙이 꽂힙니다!"},
            {"name": "분석", "dur": 1800, "result": "atk",
             "moves": [],
             "focus": "atk.OHB",
             "tags": ["#4인공격"],
             "text": "{atk.team.short} 반격 성공. 전위 3명 + 후위 {atk.OHB.name}까지 4명이 동시에 공격 준비를 하면 상대 블로커는 선택을 강요받습니다. ({atk.OHB.name} 공격 성공률 {atk.OHB.attPctS})"},
        ],
    },
    # ─────────────────────────────────────────────────────────
    {
        "code": "OPEN_VS_DOUBLE",
        "title": "오픈 공격 vs 2인 블로킹",
        "subtitle": "찬스볼 → 레프트 하이볼 → 블록 아웃",
        "attack_team": "HDEC",
        "phases": [
            {"name": "포메이션", "dur": 1300,
             "moves": [
                 mv("atk.L", [30, 45]), mv("atk.S", [74, 62]), mv("atk.OHF", [62, 6]),
                 mv("atk.MBF", [74, 45]), mv("atk.OP", [62, 86]), mv("atk.OHB", [32, 72]),
                 mv("def.Z2", [84, 76]), mv("def.Z3", [84, 45]), mv("def.Z4", [84, 14]),
                 mv("def.Z1", [20, 76]), mv("def.Z6", [24, 45]), mv("def.Z5", [20, 14]),
             ],
             "focus": "atk.L",
             "tags": ["#찬스볼"],
             "text": "{def.team.short|이가} 공을 쉽게 넘겨줍니다. {atk.team.short}에게 찬스볼."},
            {"name": "찬스볼 처리", "dur": 1300,
             "ball": [ball(["def", 62, 50], ["atk", 30, 45], h=40)],
             "moves": [mv("atk.S", SET_SPOT, delay=0.2, trail=True)],
             "focus": "atk.L",
             "tags": ["#언더패스"],
             "text": "{atk.L.name|이가} 안정적으로 받아냅니다. 세터 {atk.S.name|은는} 네트 앞에서 토스를 준비."},
            {"name": "패스", "dur": 1000,
             "ball": [ball(["atk", 30, 45], ["atk", 83, 60], h=38)],
             "moves": [mv("atk.OHF", [60, 4])],
             "focus": "atk.S",
             "tags": [],
             "text": "공이 세터에게. 레프트 {atk.OHF.name|이가} 바깥으로 빠지며 하이볼을 기다립니다."},
            {"name": "오픈 토스", "dur": 1500,
             "ball": [ball(["atk", 83, 60], ["atk", 85, 8], h=52)],
             "moves": [mv("atk.OHF", [85, 9], via=[70, -2], delay=0.35, trail=True),
                       mv("atk.MBF", [85, 42], via=[80, 36], end=0.5, trail=True),
                       mv("def.Z3", [86.5, 72], via=[85, 58], delay=0.45, trail=True),
                       mv("def.Z2", [86.5, 80], delay=0.6)],
             "focus": "atk.OHF",
             "tags": ["#하이볼", "#2인블로킹"],
             "text": "높은 오픈 토스. {def.team.short|은는} 미들이 따라붙어 2인 블로킹을 완성합니다."},
            {"name": "블록 아웃", "dur": 1100,
             "ball": [ball(["atk", 85, 8], ["def", 85, 80], h=8, end=0.3),
                      ball(["def", 85, 80], ["def", 62, 100], h=26, delay=0.3)],
             "moves": [mv("def.Z1", [34, 86], delay=0.4)],
             "focus": "atk.OHF",
             "tags": ["#블록아웃", "#터치아웃"],
             "text": "{atk.OHF.name|이가} 블로커 손끝을 노립니다! 공이 블로킹에 맞고 사이드라인 밖으로 — 블록 아웃!"},
            {"name": "분석", "dur": 1800, "result": "atk",
             "moves": [],
             "focus": "atk.OHF",
             "tags": ["#에이스"],
             "text": "{atk.OHF.name} 공격 성공률 {atk.OHF.attPctS}, 점유율 {atk.OHF.shareS}. 2인 블로킹을 정면 돌파하는 대신 바깥 손을 이용한 영리한 득점. 다만 이 경기 범실 {atk.OHF.err}개는 줄여야 할 숙제."},
        ],
    },
    # ─────────────────────────────────────────────────────────
    {
        "code": "SERVE_PRESSURE",
        "title": "서브 공략 → 하이볼 처리 → 반격",
        "subtitle": "정관장 목적타 서브 → 현대 하이볼 → 디그 후 반격",
        "attack_team": "KGC",
        "phases": [
            {"name": "포메이션", "dur": 1300,
             "moves": [
                 mv("atk.Z1", [-6, 80]),
                 mv("atk.Z2", [84, 76]), mv("atk.Z3", [84, 45]), mv("atk.Z4", [84, 14]),
                 mv("atk.Z5", [22, 14]), mv("atk.Z6", [22, 45]),
                 mv("def.OHF", [32, 20]), mv("def.L", [28, 45]), mv("def.OHB", [32, 70]),
                 mv("def.S", [74, 64]), mv("def.MBF", [78, 40]), mv("def.OP", [80, 84]),
             ],
             "focus": "def.OHB",
             "tags": ["#목적타"],
             "text": "{atk.team.short} {atk.Z1.name} 서브. 노리는 곳은 {def.OHB.name}입니다. (리시브 {def.OHB.rcv})"},
            {"name": "목적타 서브", "dur": 1300,
             "ball": [ball(["atk", -4, 80], ["def", 32, 70], h=30)],
             "moves": [mv("atk.Z1", [18, 76], delay=0.4),
                       mv("def.S", SET_SPOT, delay=0.15)],
             "focus": "def.OHB",
             "tags": ["#서브공략"],
             "text": "강한 서브가 {def.OHB.name} 정면으로 꽂힙니다!"},
            {"name": "리시브 흔들림", "dur": 1100,
             "ball": [ball(["def", 32, 70], ["def", 62, 30], h=30)],
             "moves": [mv("def.S", [62, 32], delay=0.15, trail=True),
                       mv("def.MBF", [70, 42])],
             "focus": "def.S",
             "tags": ["#리시브불안"],
             "text": "리시브가 세터 위치를 크게 벗어납니다. {def.S.name|이가} 3m 라인 근처까지 따라가야 합니다. 속공 옵션이 사라졌습니다."},
            {"name": "하이볼", "dur": 1500,
             "ball": [ball(["def", 62, 32], ["def", 85, 84], h=54)],
             "moves": [mv("def.OP", [85, 84], via=[62, 94], delay=0.2, trail=True),
                       mv("atk.Z4", [86.5, 10], delay=0.4),
                       mv("atk.Z3", [86.5, 17], via=[85, 30], delay=0.35, trail=True),
                       mv("atk.L", [30, 30], delay=0.3)],
             "focus": "def.OP",
             "tags": ["#하이볼", "#읽기블로킹"],
             "text": "어쩔 수 없이 올린 하이볼은 라이트 {def.OP.name}에게. {atk.team.short|은는} 여유 있게 2인 블로킹을 세웁니다."},
            {"name": "디그", "dur": 900,
             "ball": [ball(["def", 85, 84], ["atk", 30, 32], h=5)],
             "moves": [],
             "focus": "atk.L",
             "tags": ["#디그"],
             "text": "{def.OP.name}의 공격을 {atk.L.name|이가} 걷어 올립니다! 이 경기 디그 {atk.L.dig}."},
            {"name": "반격 토스", "dur": 1100,
             "ball": [ball(["atk", 30, 32], ["atk", 83, 60], h=36)],
             "moves": [mv("atk.S", SET_SPOT, end=0.85, trail=True),
                       mv("atk.OHF", [60, 6]), mv("atk.MBF", [72, 48]), mv("atk.OP", [62, 86]),
                       mv("def.S", [80, 60]), mv("def.OP", [78, 80]),
                       mv("def.MBF", [84, 45]), mv("def.OHF", [84, 76])],
             "focus": "atk.S",
             "tags": ["#트랜지션"],
             "text": "반격 찬스. 세터 {atk.S.name}에게 공이 갑니다."},
            {"name": "반격 공격", "dur": 1300,
             "ball": [ball(["atk", 83, 60], ["atk", 85, 10], h=40, end=0.6),
                      ball(["atk", 85, 10], ["def", 30, 22], h=4, delay=0.62)],
             "moves": [mv("atk.OHF", [85, 10], via=[70, 0], delay=0.15, end=0.62, trail=True),
                       mv("atk.MBF", [85, 44], via=[80, 38], end=0.45, trail=True),
                       mv("def.MBF", [86.5, 52], end=0.45),
                       mv("def.OHF", [86.5, 80], delay=0.5)],
             "focus": "atk.OHF",
             "tags": ["#에이스결정"],
             "text": "미들이 속공으로 블로커를 끌고, 레프트 {atk.OHF.name|이가} 마무리!"},
            {"name": "분석", "dur": 1800, "result": "atk",
             "moves": [],
             "focus": "atk.OHF",
             "tags": ["#서브효과"],
             "text": "{atk.team.short} 득점. 서브로 리시브를 흔들면 상대는 하이볼밖에 선택지가 없습니다. 이 경기 {def.team.short} 팀 리시브 정확도는 {def.team.rcv}%."},
        ],
    },
]
