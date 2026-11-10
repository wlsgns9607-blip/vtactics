-- ============================================================
--  V-리그 전술 분석 시뮬레이터 - SQLite 스키마
--  정관장 레드스파크스 vs 현대건설
-- ============================================================
PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS v_set_team_summary;
DROP VIEW  IF EXISTS v_set_player_stats;
DROP VIEW  IF EXISTS v_team_summary;
DROP VIEW  IF EXISTS v_player_stats;
DROP TABLE IF EXISTS rallies;
DROP TABLE IF EXISTS set_lineups;
DROP TABLE IF EXISTS set_stats;
DROP TABLE IF EXISTS sets;
DROP TABLE IF EXISTS scenarios;
DROP TABLE IF EXISTS lineups;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS teams;

-- ── 팀 ───────────────────────────────────────────────────────
CREATE TABLE teams (
    id            TEXT PRIMARY KEY,          -- 'KGC', 'HDEC'
    name          TEXT NOT NULL,
    short_name    TEXT NOT NULL,
    primary_color TEXT NOT NULL,             -- 홈 테마 메인 컬러
    accent_color  TEXT NOT NULL,             -- 포인트 컬러
    bg_color      TEXT NOT NULL,             -- 홈일 때 배경 틴트
    is_home       INTEGER NOT NULL DEFAULT 0 -- 기본 홈팀 여부
);

-- ── 선수 + 경기 기록 ──────────────────────────────────────────
-- 성공/시도 기록은 made/tried 두 칸으로 저장 (기록표 '-' → NULL)
CREATE TABLE players (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id      TEXT NOT NULL REFERENCES teams(id),
    name         TEXT NOT NULL,
    position     TEXT NOT NULL CHECK (position IN ('S','OH','OP','MB','L')),
    number       INTEGER,
    sets_played  INTEGER,
    points       INTEGER,
    att_made     INTEGER NOT NULL DEFAULT 0,
    att_tried    INTEGER NOT NULL DEFAULT 0,
    att_pct      REAL,                       -- 기록표 원본 값
    att_share    REAL,                       -- 기록표 원본 값
    srv_made     INTEGER NOT NULL DEFAULT 0,
    srv_tried    INTEGER NOT NULL DEFAULT 0,
    blk_made     INTEGER NOT NULL DEFAULT 0,
    blk_tried    INTEGER NOT NULL DEFAULT 0,
    dig_made     INTEGER NOT NULL DEFAULT 0,
    dig_tried    INTEGER NOT NULL DEFAULT 0,
    rcv_made     INTEGER NOT NULL DEFAULT 0,
    rcv_tried    INTEGER NOT NULL DEFAULT 0,
    set_made     INTEGER NOT NULL DEFAULT 0,
    set_tried    INTEGER NOT NULL DEFAULT 0,
    errors       INTEGER,
    comment      TEXT,                       -- 분석 코멘트
    UNIQUE (team_id, name)
);

-- ── 기본 라인업 (슬롯 → 선수) ─────────────────────────────────
-- slot: S, OH1, OH2, OP, MB1, MB2, L
CREATE TABLE lineups (
    team_id   TEXT    NOT NULL REFERENCES teams(id),
    slot      TEXT    NOT NULL,
    player_id INTEGER NOT NULL REFERENCES players(id),
    PRIMARY KEY (team_id, slot)
);

-- ── 전술 시나리오 (페이즈 타임라인은 JSON) ─────────────────────
CREATE TABLE scenarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT UNIQUE NOT NULL,
    title       TEXT NOT NULL,
    subtitle    TEXT,
    attack_team TEXT NOT NULL REFERENCES teams(id),
    sort_order  INTEGER NOT NULL,
    phases_json TEXT NOT NULL
);

-- ── 뷰: 성공률 자동 계산 ──────────────────────────────────────
CREATE VIEW v_player_stats AS
SELECT
    p.*,
    ROUND(100.0 * blk_made / NULLIF(blk_tried, 0), 2) AS blk_pct,
    ROUND(100.0 * dig_made / NULLIF(dig_tried, 0), 2) AS dig_pct,
    ROUND(100.0 * rcv_made / NULLIF(rcv_tried, 0), 2) AS rcv_pct,
    ROUND(100.0 * set_made / NULLIF(set_tried, 0), 2) AS set_pct,
    ROUND(100.0 * srv_made / NULLIF(srv_tried, 0), 2) AS srv_pct,
    ROUND(1.0 * blk_made / NULLIF(sets_played, 0), 2) AS blk_per_set,
    ROUND(1.0 * dig_made / NULLIF(sets_played, 0), 2) AS dig_per_set
FROM players p;

-- ── 뷰: 팀 합계 ───────────────────────────────────────────────
CREATE VIEW v_team_summary AS
SELECT
    team_id,
    SUM(att_made)  AS att_made,  SUM(att_tried) AS att_tried,
    ROUND(100.0 * SUM(att_made) / NULLIF(SUM(att_tried), 0), 2) AS att_pct,
    SUM(blk_made)  AS blk_made,  SUM(blk_tried) AS blk_tried,
    SUM(srv_made)  AS srv_made,  SUM(srv_tried) AS srv_tried,
    SUM(dig_made)  AS dig_made,  SUM(dig_tried) AS dig_tried,
    ROUND(100.0 * SUM(dig_made) / NULLIF(SUM(dig_tried), 0), 2) AS dig_pct,
    SUM(rcv_made)  AS rcv_made,  SUM(rcv_tried) AS rcv_tried,
    ROUND(100.0 * SUM(rcv_made) / NULLIF(SUM(rcv_tried), 0), 2) AS rcv_pct,
    SUM(COALESCE(errors, 0)) AS errors
FROM players
GROUP BY team_id;

-- ============================================================
--  세트별 기록 (문자중계 로그에서 집계)
-- ============================================================
CREATE TABLE sets (
    set_no     INTEGER PRIMARY KEY,
    kgc_score  INTEGER NOT NULL,
    hdec_score INTEGER NOT NULL,
    winner     TEXT NOT NULL REFERENCES teams(id)
);

-- 세트별 선수 기록 (성공/시도). 기록 없는 선수는 행이 없음
CREATE TABLE set_stats (
    set_no     INTEGER NOT NULL REFERENCES sets(set_no),
    player_id  INTEGER NOT NULL REFERENCES players(id),
    att_made   INTEGER NOT NULL DEFAULT 0,  att_tried INTEGER NOT NULL DEFAULT 0,
    srv_made   INTEGER NOT NULL DEFAULT 0,  srv_tried INTEGER NOT NULL DEFAULT 0,
    blk_made   INTEGER NOT NULL DEFAULT 0,  blk_tried INTEGER NOT NULL DEFAULT 0,
    dig_made   INTEGER NOT NULL DEFAULT 0,  dig_tried INTEGER NOT NULL DEFAULT 0,
    rcv_made   INTEGER NOT NULL DEFAULT 0,  rcv_tried INTEGER NOT NULL DEFAULT 0,
    set_made   INTEGER NOT NULL DEFAULT 0,  set_tried INTEGER NOT NULL DEFAULT 0,
    blk_assist INTEGER NOT NULL DEFAULT 0,
    errors     INTEGER NOT NULL DEFAULT 0,
    points     INTEGER NOT NULL DEFAULT 0,  -- 공격 + 서브 + 블로킹 득점
    comment    TEXT,
    PRIMARY KEY (set_no, player_id)
);

-- 세트별 코트 위 주전 구성 (출전 기록으로 추정한 7인)
CREATE TABLE set_lineups (
    set_no    INTEGER NOT NULL REFERENCES sets(set_no),
    team_id   TEXT    NOT NULL REFERENCES teams(id),
    slot      TEXT    NOT NULL,
    player_id INTEGER NOT NULL REFERENCES players(id),
    PRIMARY KEY (set_no, team_id, slot)
);

-- 득점 랠리 (리플레이용). events_json = 시간순 터치 목록
CREATE TABLE rallies (
    set_no     INTEGER NOT NULL REFERENCES sets(set_no),
    rally_no   INTEGER NOT NULL,
    scorer     TEXT    NOT NULL REFERENCES teams(id),
    server     TEXT    NOT NULL REFERENCES teams(id),
    cause      TEXT    NOT NULL,   -- kill / blockkill / out / net / overnet / touchnet / drop / fault
    score_kgc  INTEGER NOT NULL,   -- 이 랠리 득점 후 스코어
    score_hdec INTEGER NOT NULL,
    point_idx  INTEGER NOT NULL,   -- 득점을 결정한 터치의 위치(1부터)
    events_json TEXT   NOT NULL,
    PRIMARY KEY (set_no, rally_no)
);

-- 사용자가 직접 쓰는 최종 리뷰 (1행). seed.py 재실행 시에도 보존됨
CREATE TABLE IF NOT EXISTS reviews (
    id           INTEGER PRIMARY KEY CHECK (id = 1),
    content_json TEXT NOT NULL DEFAULT '{}',
    updated_at   TEXT
);

-- ── 뷰: 세트별 팀 합계 ─────────────────────────────────────────
CREATE VIEW v_set_team_summary AS
SELECT
    s.set_no, p.team_id,
    SUM(s.att_made) AS att_made, SUM(s.att_tried) AS att_tried,
    ROUND(100.0 * SUM(s.att_made) / NULLIF(SUM(s.att_tried), 0), 2) AS att_pct,
    SUM(s.blk_made) AS blk_made, SUM(s.blk_tried) AS blk_tried,
    SUM(s.srv_made) AS srv_made, SUM(s.srv_tried) AS srv_tried,
    SUM(s.dig_made) AS dig_made, SUM(s.dig_tried) AS dig_tried,
    ROUND(100.0 * SUM(s.dig_made) / NULLIF(SUM(s.dig_tried), 0), 2) AS dig_pct,
    SUM(s.rcv_made) AS rcv_made, SUM(s.rcv_tried) AS rcv_tried,
    ROUND(100.0 * SUM(s.rcv_made) / NULLIF(SUM(s.rcv_tried), 0), 2) AS rcv_pct,
    SUM(s.set_made) AS set_made, SUM(s.set_tried) AS set_tried,
    ROUND(100.0 * SUM(s.set_made) / NULLIF(SUM(s.set_tried), 0), 2) AS set_pct,
    SUM(s.errors) AS errors, SUM(s.points) AS points
FROM set_stats s JOIN players p ON p.id = s.player_id
GROUP BY s.set_no, p.team_id;

-- ── 뷰: 세트별 선수 기록 + 성공률 ───────────────────────────────
CREATE VIEW v_set_player_stats AS
SELECT
    s.*, p.team_id, p.name, p.position,
    ROUND(100.0 * s.att_made / NULLIF(s.att_tried, 0), 2) AS att_pct,
    ROUND(100.0 * s.blk_made / NULLIF(s.blk_tried, 0), 2) AS blk_pct,
    ROUND(100.0 * s.dig_made / NULLIF(s.dig_tried, 0), 2) AS dig_pct,
    ROUND(100.0 * s.rcv_made / NULLIF(s.rcv_tried, 0), 2) AS rcv_pct,
    ROUND(100.0 * s.set_made / NULLIF(s.set_tried, 0), 2) AS set_pct
FROM set_stats s JOIN players p ON p.id = s.player_id;
