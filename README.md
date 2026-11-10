# V-리그 전술 분석 & 리뷰 판
정관장 레드스파크스 vs 현대건설 — 실제 경기 기록 기반 전술 시뮬레이터

## 실행 방법

**1) 서버로 실행 (권장 · Python 3.9 이상, 추가 설치 없음)**
```bash
python server.py          # → http://localhost:8000
```
DB가 없으면 자동으로 만듭니다.

**2) 서버 없이 바로 열기**
`static/index.html` 을 브라우저로 열면 `static/js/data.js` 의 내장 데이터로 동작합니다.

기록이나 시나리오를 고친 뒤에는 `python db/seed.py` 를 다시 실행하세요. DB와 data.js가 함께 갱신됩니다.

## 폴더 구조
```
vtactics/
├─ server.py              Python API 서버 (http.server + sqlite3)
├─ data/
│  ├─ players_data.py     선수 기록 원본 (기록표 그대로)
│  └─ scenarios.py        전술 시나리오 (페이즈·좌표·해설 대본)
├─ db/
│  ├─ schema.sql          테이블 + 성공률 계산 뷰
│  ├─ seed.py             DB 생성, 분석 코멘트 자동 작성, data.js 생성
│  └─ volleyball.db       SQLite DB
└─ static/
   ├─ index.html
   ├─ css/style.css       홈팀 테마(CSS 변수), 다크/라이트
   └─ js/
      ├─ app.js           코트·애니메이션 엔진·패널
      └─ data.js          서버 없이 열 때 쓰는 데이터 (자동 생성)
```

## DB 구조 (SQLite)
| 테이블/뷰 | 내용 |
|---|---|
| `teams` | 팀 이름, 테마 컬러, 기본 홈팀 |
| `players` | 선수 기록 (성공/시도 = made/tried), 분석 코멘트 |
| `lineups` | 기본 라인업 (S, OH1, OH2, OP, MB1, MB2, L) |
| `scenarios` | 전술 시나리오 (페이즈 타임라인 JSON) |
| `v_player_stats` | 블로킹·디그·리시브·세트 성공률, 세트당 기록 자동 계산 |
| `v_team_summary` | 팀 합계 |

## API
| 엔드포인트 | 설명 |
|---|---|
| `GET /api/bootstrap` | 앱 초기 데이터 전체 |
| `GET /api/teams` | 팀 + 테마 컬러 |
| `GET /api/players?team=KGC` | 팀별 선수 기록 |
| `GET /api/players/<id>` | 선수 1명 |
| `GET /api/summary` | 팀 합계 |
| `GET /api/scenarios` | 전술 시나리오 |

## 조작
- **▶ 재생 / ⏸ 일시정지**: Space
- **↻ 로테이션**: R. 사이드 패널에서 선택한 팀이 시계 방향으로 한 자리 돕니다. 시나리오의 역할(전위 OH, 전위 MB 등)이 로테이션에 따라 다른 선수에게 넘어가고, 해설도 자동으로 바뀝니다.
- **↺ 초기화**: Esc. 로테이션과 위치를 처음으로 되돌립니다.
- **시나리오 선택**: 1~4 키
- **🏠 HOME**: 홈팀 전환. 테마 색이 바뀌고 홈팀이 왼쪽 진영으로 옵니다.
- **◐**: 다크/라이트 전환
- 페이즈 칩을 클릭하면 해당 장면으로 바로 이동합니다.

## 수정 포인트
- 팀 컬러: `db/seed.py` 의 `THEME` (현재 근사값)
- 등번호: `data/players_data.py` 의 `number` (기록표에 없어 비어 있음)
- 새 시나리오: `data/scenarios.py` 에 같은 형식으로 추가한 뒤 `python db/seed.py`

## 세트 버튼 · 리플레이 · 최종리뷰 (추가)
- 상단 **전체 / 1~4세트** 버튼: 선택한 세트 기준으로 선수 기록·라인업·분석 문구·시나리오 해설 수치가 바뀝니다 (키보드 0~4).
- **세트 리플레이**(하단 탭): 문자중계에서 파싱한 득점 랠리를 순서대로 재현. 스코어보드 실시간 갱신, 랠리 목록/필터, ←/→ 로 랠리 이동. 위치·공 궤적은 터치 순서 기반 근사 연출입니다.
- **📝 최종리뷰**: 왼쪽 자동 데이터 요약 + 오른쪽 직접 작성 에디터. `PUT /api/review` 로 SQLite `reviews` 테이블에 자동 저장(서버 없으면 localStorage), 복사 / .md 저장 / 인쇄.
- 데이터 재생성: `python data/parse_set.py data/sets/setN.txt`(검증), `python db/seed.py`(DB·data.js 재생성, 리뷰는 보존).
