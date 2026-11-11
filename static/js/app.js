/* ============================================================
   V-리그 전술 분석 시뮬레이터 - 프론트엔드 엔진
   - 데이터: /api/bootstrap (Python 서버) → 실패 시 window.BOOTSTRAP (data.js)
   - 좌표: 코트 180 x 90 (단위 10cm), 네트 x=90, 홈팀은 항상 왼쪽
   - 보기: 전체(0) / 1~4세트. 세트를 고르면 선수 기록·라인업·해설 수치가 그 세트 기준으로 바뀜
   - 모드: 전술 시나리오(역할 기반 시뮬레이션) / 세트 리플레이(실제 문자중계 랠리 재현)
   ============================================================ */
(() => {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';
  const $ = (id) => document.getElementById(id);
  const ZONES = { 1: [20, 75], 2: [72, 75], 3: [72, 45], 4: [72, 15], 5: [20, 15], 6: [20, 45] };
  const BASE_ROT = ['S', 'OH1', 'MB2', 'OP', 'OH2', 'MB1']; // 1~6번 자리
  const SLOTS = ['S', 'OH1', 'OH2', 'OP', 'MB1', 'MB2', 'L'];
  const POS_KO = { S: '세터', OH: '아웃사이드 히터', OP: '아포짓', MB: '미들 블로커', L: '리베로' };
  const CAT_KO = { serve: '서브', receive: '리시브', set: '토스', attack: '공격', block: '블로킹', block_assist: '블로킹', dig: '디그' };

  let D = null;   // 현재 보기 기준 데이터 (선수·요약·라인업은 useView 가 교체)
  let V = null;   // 보기별 데이터 {0:전체, 1:1세트, ...}
  let RAW = null; // 서버에서 받은 원본
  let typeTimer = null; // 해설 타이핑 타이머
  let resolveReady;
  const ready = new Promise((r) => (resolveReady = r));

  const S = {
    home: 'KGC', theme: 'dark', rot: {}, rotCount: {}, panelTeam: 'KGC',
    selected: null, focusKey: null, scenario: 0, phase: -1, t: 0,
    playing: false, finished: false, speed: 1, autoFocus: true,
    mode: 'scenario', rf: 'hl', live: null, rp: null,
    pos: {}, ball: { x: 0, y: 0, h: 0, show: false }, run: null, tween: null,
    typing: null, el: {}, lastScore: {},
    searchQuery: '', matchDate: '2026-11-07',
  };

  // ───────────────────────── 공용 유틸 ─────────────────────────
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const clamp01 = (v) => clamp(v, 0, 1);
  const ease = (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
  const lerp = (a, b, p) => a + (b - a) * p;
  const quad = (a, c, b, p) => (1 - p) * (1 - p) * a + 2 * (1 - p) * p * c + p * p * b;
  const pct = (m, t) => (t ? Math.round((m / t) * 10000) / 100 : null);
  const hash = (a, b, c) => {
    let x = Math.imul(a + 1, 73856093) ^ Math.imul(b + 1, 19349663) ^ Math.imul(c + 1, 83492791);
    x = Math.imul(x ^ (x >>> 13), 1274126177);
    return ((x ^ (x >>> 16)) >>> 0) % 1000 / 1000;
  };

  const other = (t) => D.teamIds.find((x) => x !== t);
  const away = () => other(S.home);
  const color = (t) => D.teams[t].primary_color;
  const short = (t) => D.teams[t].short_name;
  const playerOf = (team, slot) => D.players[D.lineups[team][slot]];
  const scen = () => D.scenarios[S.scenario];
  const setInfo = (n) => RAW.sets.find((s) => s.set_no === n);

  // ───────────────────────── 데이터 ─────────────────────────
  async function loadData() {
    try {
      const url = S.matchDate ? `api/bootstrap?date=${S.matchDate}` : 'api/bootstrap';
      const r = await fetch(url, { cache: 'no-store' });
      if (!r.ok) throw new Error(r.status);
      const d = await r.json();
      d.source = 'Python API · SQLite';
      d.serverMode = true;
      return d;
    } catch (e) {
      const key = S.matchDate || '2024-11-04';
      if (window.MATCHES) {
        const found = window.MATCHES[key] || window.MATCHES[key.replace('2024-', '2026-')] || window.MATCHES[key.replace('2026-', '2024-')];
        if (found) return { ...found, source: '내장 전술 데이터', serverMode: false };
      }
      if (window.BOOTSTRAP) return { ...window.BOOTSTRAP, source: '내장 데이터 (서버 미연결)', serverMode: false };
      throw e;
    }
  }

  function computeSummary(players) {
    const out = {};
    D.teamIds.forEach((t) => {
      const ps = players.filter((p) => p.team_id === t);
      const sum = (k) => ps.reduce((a, p) => a + (p[k] || 0), 0);
      out[t] = {
        team_id: t,
        att_made: sum('att_made'), att_tried: sum('att_tried'), att_pct: pct(sum('att_made'), sum('att_tried')),
        blk_made: sum('blk_made'), blk_tried: sum('blk_tried'),
        srv_made: sum('srv_made'), srv_tried: sum('srv_tried'),
        dig_made: sum('dig_made'), dig_tried: sum('dig_tried'), dig_pct: pct(sum('dig_made'), sum('dig_tried')),
        rcv_made: sum('rcv_made'), rcv_tried: sum('rcv_tried'), rcv_pct: pct(sum('rcv_made'), sum('rcv_tried')),
        set_made: sum('set_made'), set_tried: sum('set_tried'), set_pct: pct(sum('set_made'), sum('set_tried')),
        errors: sum('errors'), points: sum('points'),
      };
    });
    return out;
  }

  function makeView(n) {
    const lineups = n === 0 ? RAW.lineups : ((RAW.set_lineups && RAW.set_lineups[n]) || RAW.lineups);
    let list;
    if (n === 0) {
      list = RAW.players.map((p) => ({ ...p }));
    } else {
      const rows = {};
      RAW.set_stats.filter((r) => r.set_no === n).forEach((r) => (rows[r.player_id] = r));
      const teamAtt = {};
      D.teamIds.forEach((t) => (teamAtt[t] = 0));
      RAW.players.forEach((p) => { if (rows[p.id]) teamAtt[p.team_id] += rows[p.id].att_tried; });
      list = RAW.players.map((p) => {
        const r = rows[p.id]; const g = (k) => (r ? r[k] || 0 : 0);
        const q = { ...p, active: !!r };
        ['att', 'srv', 'blk', 'dig', 'rcv', 'set'].forEach((k) => {
          q[k + '_made'] = g(k + '_made'); q[k + '_tried'] = g(k + '_tried');
          q[k + '_pct'] = pct(q[k + '_made'], q[k + '_tried']);
        });
        q.att_share = teamAtt[p.team_id] ? pct(q.att_tried, teamAtt[p.team_id]) : null;
        q.points = r ? g('points') : null;
        q.errors = r ? g('errors') : null;
        q.sets_played = r ? 1 : 0;
        q.blk_per_set = q.blk_made; q.dig_per_set = q.dig_made;
        q.comment = r ? r.comment : '이번 세트 출전 기록 없음.';
        return q;
      });
    }
    const players = {}; const byTeam = {};
    list.forEach((p) => { players[p.id] = p; (byTeam[p.team_id] ||= []).push(p); });
    return { setNo: n, label: n === 0 ? '전체' : `${n}세트`, players, byTeam, lineups, summary: computeSummary(list) };
  }

  function indexData(raw) {
    const teams = {}; raw.teams.forEach((t) => (teams[t.id] = t));
    D = { ...raw, teams, teamIds: raw.teams.map((t) => t.id), setNo: 0 };
    // 리플레이용: 세트별 랠리 + 득점 전/후 스코어
    D.ralliesBySet = {};
    const tHome = raw.teams[0].id;
    const tAway = raw.teams[1].id;
    raw.rallies.forEach((r) => {
      (D.ralliesBySet[r.set_no] ||= []).push(r);
    });
    Object.values(D.ralliesBySet).forEach((list) => {
      let prev = { [tHome]: 0, [tAway]: 0 };
      list.forEach((r) => {
        r.before = prev;
        // 팀 ID 기준으로 점수 필드 선택 (score_kgc / score_hdec / score_hkl ...)
        const sc = (t) => r['score_' + t.toLowerCase()] ?? 0;
        r.after = { [tHome]: sc(tHome), [tAway]: sc(tAway) };
        prev = r.after;
      });
    });
    // 레이더 정규화 최대값 (경기 전체 기준)
    const act = raw.players.filter((p) => p.sets_played);
    const max = (f) => Math.max(...act.map(f).filter((v) => v != null && isFinite(v)), 0.0001);
    D.radarMax = {
      att: max((p) => p.att_pct), share: max((p) => p.att_share), blk: max((p) => p.blk_per_set),
      dig: max((p) => p.dig_per_set), rcv: max((p) => (p.rcv_tried >= 3 ? p.rcv_pct : 0)),
      set: max((p) => p.set_made / p.sets_played),
    };
    RAW = raw;
    V = { 0: makeView(0) };
    raw.sets.forEach((s) => (V[s.set_no] = makeView(s.set_no)));
    useView(0);
  }

  function useView(n) {
    const v = V[n];
    D.setNo = n; D.view = v; D.players = v.players; D.byTeam = v.byTeam; D.summary = v.summary; D.lineups = v.lineups;
  }

  // ───────────────────────── 분석 문장 (헤드라인·인사이트) ─────────────────────────
  const METRICS = [
    { k: 'att_pct', label: '공격 성공률', unit: '%p', scale: 8 },
    { k: 'rcv_pct', label: '리시브 정확', unit: '%p', scale: 10 },
    { k: 'blk_made', label: '블로킹 득점', unit: '개', scale: 1.5 },
    { k: 'srv_made', label: '서브 득점', unit: '개', scale: 1.5 },
    { k: 'dig_pct', label: '디그 성공률', unit: '%p', scale: 10 },
    { k: 'errors', label: '범실', unit: '개', scale: 3, inv: true },
  ];
  const fmtD = (m, d) => (m.unit === '%p' ? `${d > 0 ? '+' : ''}${d.toFixed(1)}%p` : `${d > 0 ? '+' : ''}${d}개`);
  function compare(a, b) {
    return METRICS.map((m) => {
      const d = ((a[m.k] || 0) - (b[m.k] || 0)) * (m.inv ? -1 : 1);
      return { m, d, z: d / m.scale };
    }).sort((x, y) => y.z - x.z);
  }
  const topBy = (n, team, f) => Object.values(V[n].players).filter((p) => p.team_id === team)
    .reduce((b, p) => (!b || f(p) > f(b) ? p : b), null);
  const trend = (team, k, suffix = '') => [1, 2, 3, 4].filter((s) => V[s]).map((s) => `${V[s].summary[team][k]}${suffix}`).join(' → ');

  const getSetScore = (st, tid) => {
    if (!st) return 0;
    if (st.score_home !== undefined) return tid === RAW.teams[0].id ? st.score_home : st.score_away;
    if (st.hkl_score !== undefined) return tid === 'HKL' ? st.hkl_score : st.kgc_score;
    return tid === 'KGC' ? st.kgc_score : (st.hdec_score ?? 0);
  };

  function analyze(n) {
    let w, l, headTitle, chips = [];
    if (n === 0) {
      const wins = {}; D.teamIds.forEach((t) => (wins[t] = RAW.sets.filter((s) => s.winner === t).length));
      w = D.teamIds.reduce((a, b) => (wins[a] >= wins[b] ? a : b)); l = other(w);
      headTitle = `${short(w)} 세트 스코어 ${wins[w]} : ${wins[l]} 승리`;
      chips = [`${RAW.sets.length}세트`, `득점 랠리 ${RAW.rallies.length}개`];
    } else {
      const s = setInfo(n);
      w = s.winner; l = other(w);
      const sw = getSetScore(s, w); const sl = getSetScore(s, l);
      headTitle = `${n}세트 · ${short(w)} ${sw} : ${sl} 승`;
      chips = [`SET ${n}`, `득점 랠리 ${(D.ralliesBySet[n] || []).length}개`];
    }
    const adv = compare(V[n].summary[w], V[n].summary[l]);
    const good = adv.filter((x) => x.z >= 0.2).slice(0, 2);
    const bad = adv.filter((x) => x.z <= -0.25).slice(-2).reverse();
    let main = headTitle;
    if (good.length) main += ` — 우세: ${good.map((x) => `${x.m.label} ${fmtD(x.m, x.d)}`).join(', ')}`;
    if (bad.length) main += ` · 열세: ${bad.map((x) => `${x.m.label} ${fmtD(x.m, x.d)}`).join(', ')}`;

    // 사이드 인사이트
    const b = [];
    const sorted = D.teamIds;
    b.push(`<b>득점 1위</b> ${sorted.map((t) => { const p = topBy(n, t, (x) => x.points || 0); return `${esc(short(t))} <b>${esc(p ? p.name : '-')}</b> ${p ? (p.points || 0) : 0}점`; }).join(' · ')}`);
    b.push(`<b>공격 중심</b> ${sorted.map((t) => { const p = topBy(n, t, (x) => x.att_tried); return `${esc(short(t))} <b>${esc(p ? p.name : '-')}</b> ${p ? `${p.att_made}/${p.att_tried}` : '-'}${p && p.att_pct != null ? ` (${p.att_pct}%)` : ''}`; }).join(' · ')}`);
    const rc = Object.values(V[n].players).filter((p) => p.rcv_tried >= (n === 0 ? 15 : 5) && p.position !== 'L').sort((a, c) => a.rcv_pct - c.rcv_pct)[0];
    b.push(`<b>리시브</b> 팀 ${sorted.map((t) => `${esc(short(t))} ${V[n].summary[t].rcv_pct}%`).join(' · ')}${rc ? ` · 가장 흔들린 선수 <b>${esc(rc.name)}</b> ${rc.rcv_made}/${rc.rcv_tried}` : ''}`);
    b.push(`<b>블로킹·서브</b> 블로킹 득점 ${sorted.map((t) => V[n].summary[t].blk_made).join(' : ')} · 서브 득점 ${sorted.map((t) => V[n].summary[t].srv_made).join(' : ')}`);
    const rl = n === 0 ? RAW.rallies : (D.ralliesBySet[n] || []);
    if (rl.length) {
      const lr = rl.reduce((a, c) => (c.events.length > a.events.length ? c : a), rl[0]);
      b.push(`<b>최장 랠리</b> ${n === 0 ? `${lr.set_no}세트 ` : ''}#${lr.rally_no} — ${lr.events.length}터치, ${esc(short(lr.scorer))} 득점`);
    }
    if (n === 0) {
      const t1 = D.teamIds[0], t2 = D.teamIds[1];
      b.splice(1, 0, `<b>세트별 흐름</b> ${RAW.sets.map((s) => `${s.set_no}세트 ${getSetScore(s, t1)}:${getSetScore(s, t2)}`).join(' · ')} (${short(t1)[0]}:${short(t2)[0]})`);
      b.splice(2, 0, `<b>공격 성공률 추이</b> ${D.teamIds.map((t) => `${esc(short(t))} ${trend(t, 'att_pct')}`).join(' / ')}`);
    }
    return { headline: main, chips, bullets: b, winner: w };
  }

  // ───────────────────────── 로테이션/역할 ─────────────────────────
  function roles(team) {
    const r = S.rot[team];
    const front = [r[1], r[2], r[3]];
    const ohf = front.includes('OH1') ? 'OH1' : 'OH2';
    const mbf = front.includes('MB1') ? 'MB1' : 'MB2';
    const m = {
      S: 'S', OP: 'OP', L: 'L', OHF: ohf, OHB: ohf === 'OH1' ? 'OH2' : 'OH1',
      MBF: mbf, MBB: mbf === 'MB1' ? 'MB2' : 'MB1',
    };
    for (let z = 1; z <= 6; z++) m['Z' + z] = r[z - 1] === m.MBB ? 'L' : r[z - 1];
    return m;
  }
  function zoneOfSlot(team, slot) {
    const R = roles(team);
    for (let z = 1; z <= 6; z++) if (R['Z' + z] === slot) return z;
    return null; // 벤치(후위 미들 ↔ 리베로 교체)
  }

  const toGlobal = (team, [x, y]) => (team === S.home ? { x, y } : { x: 180 - x, y: 90 - y });

  function baseFormation() {
    const pos = {};
    D.teamIds.forEach((team) => {
      const R = roles(team);
      for (let z = 1; z <= 6; z++) pos[`${team}.${R['Z' + z]}`] = toGlobal(team, ZONES[z]);
      const left = team === S.home;
      pos[`${team}.${R.MBB}`] = { x: left ? 22 : 158, y: -8, bench: true };
    });
    return pos;
  }

  // ───────────────────────── 코트 그리기 ─────────────────────────
  const svgEl = (tag, attrs = {}, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };

  function drawFloor() {
    const g = $('layer-floor'); g.innerHTML = '';
    svgEl('rect', { x: -14, y: -14, width: 208, height: 118, rx: 4, style: 'fill:var(--freezone)' }, g);
    svgEl('rect', { x: 0, y: 0, width: 180, height: 90, style: 'fill:var(--floor)' }, g);
    svgEl('rect', { x: 0, y: 0, width: 90, height: 90, style: 'fill:var(--floor-home)' }, g);
    svgEl('rect', { x: 60, y: 0, width: 60, height: 90, fill: '#000', opacity: 0.06 }, g);
    const line = (x1, y1, x2, y2, w = 0.6, extra = {}) =>
      svgEl('line', { x1, y1, x2, y2, stroke: '#fff', 'stroke-width': w, ...extra }, g);
    svgEl('rect', { x: 0, y: 0, width: 180, height: 90, fill: 'none', stroke: '#fff', 'stroke-width': 0.7 }, g);
    line(60, 0, 60, 90, 0.5); line(120, 0, 120, 90, 0.5);
    [60, 120].forEach((x) => { line(x, -6, x, -1, 0.4, { 'stroke-dasharray': '1 1' }); line(x, 91, x, 96, 0.4, { 'stroke-dasharray': '1 1' }); });
    [[0, -3, 0, -6], [0, 93, 0, 96], [180, -3, 180, -6], [180, 93, 180, 96]].forEach((a) => line(...a, 0.5));
    D.teamIds.forEach((team) => {
      for (let z = 1; z <= 6; z++) {
        const p = toGlobal(team, ZONES[z]);
        const t = svgEl('text', { x: p.x, y: p.y + 1.8, 'text-anchor': 'middle', 'font-size': 6, 'font-weight': 800, fill: '#fff', opacity: 0.14, 'font-family': 'JetBrains Mono' }, g);
        t.textContent = z;
      }
      const left = team === S.home;
      const lbl = svgEl('text', { x: left ? 1 : 179, y: 101.5, 'text-anchor': left ? 'start' : 'end', 'font-size': 3.8, 'font-weight': 800, fill: '#fff', opacity: 0.85 }, g);
      lbl.textContent = `${left ? 'HOME' : 'AWAY'} · ${D.teams[team].short_name}`;
      const b = svgEl('text', { x: left ? 8 : 172, y: -9.5, 'text-anchor': 'middle', 'font-size': 2.6, fill: '#fff', opacity: 0.6 }, g);
      b.textContent = '교체 대기';
    });
    svgEl('line', { x1: 90, y1: -4, x2: 90, y2: 94, stroke: '#0e1320', 'stroke-width': 1.6, opacity: 0.55 }, g);
    svgEl('line', { x1: 90, y1: -4, x2: 90, y2: 94, stroke: '#eef2f8', 'stroke-width': 0.9 }, g);
    [0, 90].forEach((y) => svgEl('line', { x1: 90, y1: y - 0.5, x2: 90, y2: y + 0.5, stroke: '#ff3b3b', 'stroke-width': 1.8 }, g));
    [-5, 95].forEach((y) => svgEl('circle', { cx: 90, cy: y, r: 1.3, fill: '#d6dbe4' }, g));
  }

  function buildTokens() {
    const g = $('layer-tokens'); g.innerHTML = ''; S.el = {};
    D.teamIds.forEach((team) => {
      SLOTS.forEach((slot) => {
        const p = playerOf(team, slot);
        const key = `${team}.${slot}`;
        const isL = slot === 'L';
        const tg = svgEl('g', { class: 'token', 'data-key': key }, g);
        tg.dataset.pid = p.id;
        svgEl('circle', { class: 'ring', r: 5, cx: 0, cy: 0 }, tg);
        svgEl('circle', {
          class: 'body', r: 4.2,
          fill: isL ? '#f4f5f8' : color(team),
          stroke: isL ? color(team) : '#fff', 'stroke-width': isL ? 1.1 : 0.7,
        }, tg);
        const txtFill = isL ? `fill:${color(team)}` : '';
        const num = svgEl('text', { class: 'num', y: p.number != null ? -0.5 : 0.1, style: txtFill }, tg);
        num.textContent = p.number != null ? p.number : p.position;
        if (p.number != null) {
          const p2 = svgEl('text', { class: 'pos2', y: 2.5, style: txtFill }, tg);
          p2.textContent = p.position;
        }
        const w = p.name.length * 3.2 + 3;
        svgEl('rect', { class: 'label-bg', x: -w / 2, y: 4.9, width: w, height: 4.4, rx: 2.2 }, tg);
        const lb = svgEl('text', { class: 'label', y: 7.1 }, tg);
        lb.textContent = p.name;
        tg.addEventListener('click', () => {
          const pid = tg.dataset.pid ? +tg.dataset.pid : p.id;
          selectPlayer(pid);
        });
        S.el[key] = tg;
      });
    });
    const bg = $('layer-ball'); bg.innerHTML = '';
    S.el.shadow = svgEl('ellipse', { rx: 1.7, ry: 1, fill: '#000', opacity: 0.35 }, bg);
    S.el.ball = svgEl('circle', { r: 1.6, fill: 'url(#ballGrad)', stroke: '#7a5200', 'stroke-width': 0.25 }, bg);
  }

  function updateTokenPlayer(key, player, isSub = false) {
    const tg = S.el[key];
    if (!tg || !player) return;
    tg.dataset.pid = player.id;
    const [team, slot] = key.split('.');
    const isL = slot === 'L';
    const numEl = tg.querySelector('.num');
    const pos2El = tg.querySelector('.pos2');
    const labelEl = tg.querySelector('.label');
    const labelBg = tg.querySelector('.label-bg');
    let subBadge = tg.querySelector('.sub-badge');

    if (numEl) numEl.textContent = player.number != null ? player.number : player.position;
    if (pos2El) pos2El.textContent = player.position;
    if (labelEl) labelEl.textContent = player.name;
    if (labelBg) {
      const w = player.name.length * 3.2 + 3;
      labelBg.setAttribute('x', -w / 2);
      labelBg.setAttribute('width', w);
    }

    tg.classList.toggle('is-sub', isSub);

    if (isSub) {
      if (!subBadge) {
        subBadge = svgEl('g', { class: 'sub-badge' }, tg);
        svgEl('rect', { x: 2, y: -6.4, width: 7.2, height: 3.6, rx: 1.2, fill: '#ff9800', stroke: '#fff', 'stroke-width': 0.4 }, subBadge);
        const st = svgEl('text', { x: 5.6, y: -3.8, 'text-anchor': 'middle', 'font-size': 2.3, 'font-weight': 800, fill: '#fff', 'font-family': 'Pretendard' }, subBadge);
        st.textContent = '교체';
      }
      subBadge.style.display = '';
    } else if (subBadge) {
      subBadge.style.display = 'none';
    }

    tg.onclick = () => selectPlayer(player.id);
  }

  function resetAllTokens() {
    if (!D || !D.teamIds) return;
    D.teamIds.forEach((team) => {
      SLOTS.forEach((slot) => {
        const key = `${team}.${slot}`;
        const p = playerOf(team, slot);
        if (p) updateTokenPlayer(key, p, false);
      });
    });
  }

  function renderCourt() {
    for (const key in S.pos) {
      const tg = S.el[key]; if (!tg) continue;
      const p = S.pos[key];
      tg.setAttribute('transform', `translate(${p.x.toFixed(2)},${p.y.toFixed(2)})${p.bench ? ' scale(.7)' : ''}`);
      tg.classList.toggle('bench', !!p.bench);
      const [team, slot] = key.split('.');
      const currentPid = tg.dataset.pid ? +tg.dataset.pid : D.lineups[team][slot];
      tg.classList.toggle('selected', currentPid === S.selected);
      tg.classList.toggle('focus', key === S.focusKey);
    }
    const b = S.ball;
    S.el.ball.style.display = S.el.shadow.style.display = b.show ? '' : 'none';
    if (b.show) {
      S.el.shadow.setAttribute('cx', b.x); S.el.shadow.setAttribute('cy', b.y);
      S.el.shadow.setAttribute('opacity', Math.max(0.12, 0.38 - b.h * 0.005));
      S.el.ball.setAttribute('cx', b.x); S.el.ball.setAttribute('cy', b.y - b.h * 0.35);
      S.el.ball.setAttribute('r', 1.5 + b.h * 0.014);
    }
  }

  function clearTrails() { $('layer-trails').innerHTML = ''; }
  function clearCall() { $('layer-call').innerHTML = ''; }
  function drawTrails(run) {
    clearTrails();
    const g = $('layer-trails');
    run.moves.filter((m) => m.trail).forEach((m) => {
      const d = m.via ? `M${m.from.x},${m.from.y} Q${m.via.x},${m.via.y} ${m.to.x},${m.to.y}` : `M${m.from.x},${m.from.y} L${m.to.x},${m.to.y}`;
      svgEl('path', { class: 'trail', d, stroke: color(m.team) }, g);
      svgEl('circle', { cx: m.to.x, cy: m.to.y, r: 1, fill: 'none', stroke: color(m.team), 'stroke-width': 0.5 }, g);
    });
    run.balls.forEach((b) => {
      const mx = (b.from.x + b.to.x) / 2, my = (b.from.y + b.to.y) / 2 - b.h * 0.35;
      svgEl('path', { class: 'ball-trail', d: `M${b.from.x},${b.from.y} Q${mx},${my} ${b.to.x},${b.to.y}` }, g);
    });
  }

  function showCall(text, tone, g) {
    const L = $('layer-call'); L.innerHTML = '';
    const w = text.length * 3.15 + 5.5;
    const x = clamp(g.x, -11 + w / 2, 191 - w / 2);
    let y = g.y - 9.5; if (y < -10) y = g.y + 9.5;
    y = clamp(y, -10, 100);
    const c = svgEl('g', { class: `call ${tone}`, transform: `translate(${x.toFixed(1)},${y.toFixed(1)})` }, L);
    svgEl('rect', { x: -w / 2, y: -3.4, width: w, height: 6.8, rx: 3.4 }, c);
    const t = svgEl('text', { y: 0.2 }, c); t.textContent = text;
  }

  // ───────────────────────── 시나리오 엔진 ─────────────────────────
  function buildRun(i) {
    const sc = scen(); const ph = sc.phases[i];
    const T = { atk: sc.attack_team, def: other(sc.attack_team) };
    const R = { atk: roles(T.atk), def: roles(T.def) };
    const byKey = new Map();
    ph.moves.forEach((m) => {
      const [side, role] = m.who.split('.');
      const team = T[side]; const key = `${team}.${R[side][role]}`;
      byKey.set(key, {
        key, team, from: { ...S.pos[key], bench: false }, to: toGlobal(team, m.to),
        via: m.via ? toGlobal(team, m.via) : null, delay: m.delay || 0, end: m.end ?? 1, trail: !!m.trail,
      });
    });
    const balls = (ph.ball || []).map((b) => ({
      from: toGlobal(T[b.from[0]], b.from.slice(1)), to: toGlobal(T[b.to[0]], b.to.slice(1)),
      h: b.h || 0, delay: b.delay || 0, end: b.end ?? 1,
    }));
    const focus = ph.focus ? (() => { const [s, r] = ph.focus.split('.'); return `${T[s]}.${R[s][r]}`; })() : null;
    return { i, ph, T, R, moves: [...byKey.values()], balls, focus, dur: ph.dur };
  }

  function applyRun(run, f) {
    run.moves.forEach((m) => {
      const p = ease(clamp01((f - m.delay) / Math.max(0.001, m.end - m.delay)));
      S.pos[m.key] = m.via
        ? { x: quad(m.from.x, m.via.x, m.to.x, p), y: quad(m.from.y, m.via.y, m.to.y, p) }
        : { x: lerp(m.from.x, m.to.x, p), y: lerp(m.from.y, m.to.y, p) };
    });
    if (run.balls.length) {
      let seg = run.balls[0];
      for (const b of run.balls) if (f >= b.delay) seg = b;
      const p = clamp01((f - seg.delay) / Math.max(0.001, seg.end - seg.delay));
      S.ball = { show: true, x: lerp(seg.from.x, seg.to.x, p), y: lerp(seg.from.y, seg.to.y, p), h: 4 * seg.h * p * (1 - p) };
    }
  }

  function startPhase(i) {
    S.phase = i; S.t = 0;
    S.run = buildRun(i);
    S.focusKey = S.run.focus;
    drawTrails(S.run);
    if (S.autoFocus && S.run.focus) {
      const [team, slot] = S.run.focus.split('.');
      selectPlayer(D.lineups[team][slot], { silent: true });
    }
    narrate(S.run);
    renderTimeline();
  }

  function jumpTo(i) {
    stopTween();
    S.pos = baseFormation(); S.ball.show = false; S.finished = false;
    for (let k = 0; k < i; k++) applyRun(buildRun(k), 1);
    startPhase(i);
    renderCourt(); updateControls();
  }

  // ───────────────────────── 세트 리플레이 엔진 ─────────────────────────
  const ZY = { 1: 75, 2: 75, 3: 45, 4: 15, 5: 15, 6: 45 };
  const BAD_RE = /아웃|네트걸림|라인오버|터치넷|포히트|오버넷|범실|실패/;

  function resolveSlotForSubstitute(team, pl, ev) {
    const R = roles(team);
    const pos = pl ? pl.position : 'OH';

    // 1) 서브 이벤트: 서버는 항상 자리 1번(zone 1)
    if (ev && ev.c === 'serve') {
      return R.Z1 || 'OHB';
    }

    // 2) 세터 교체 (예: 김사랑, 최서현, 구솔 등)
    if (pos === 'S') return R.S || 'S';
    // 3) 아포짓 교체 (예: 신은지, 나현수 등)
    if (pos === 'OP') return R.OP || 'OP';
    // 4) 리베로 교체 (예: 노란, 이영주, 도수빈 등)
    if (pos === 'L') return 'L';
    // 5) 미들블로커 교체 (예: 이선우, 강서우 등) - 코트 위 전위 MBF 슬롯으로 배치
    if (pos === 'MB') {
      return R.MBF || 'MB1';
    }
    // 6) 아웃사이드 히터(OH) 교체 (예: 박혜민, 이민영, 이채영, 박여름, 오세인, 전다빈 등)
    if (ev && ['attack', 'block', 'block_assist'].includes(ev.c)) return R.OHF || 'OH1';
    return R.OHB || 'OH2';
  }

  function infoOf(team, pid, ev) {
    const lu = D.lineups[team] || {};
    let slot = null;
    let isSub = false;

    // 선발 라인업에 있는지 확인
    for (const s in lu) {
      if (lu[s] === pid) {
        slot = s;
        break;
      }
    }

    const pl = D.players[pid] || (RAW && RAW.players ? RAW.players.find((p) => p.id === pid || p.name === (ev && ev.n)) : null);

    // 선발 라인업에 없는 교체 선수인 경우: 해당 포지션/상황에 맞는 코트 슬롯으로 교체 배치!
    if (!slot) {
      isSub = true;
      slot = resolveSlotForSubstitute(team, pl, ev);
    }

    let zone = slot ? zoneOfSlot(team, slot) : null;
    // 만약 slot이 벤치 슬롯이라 zone이 null인 경우 코트 위 활성 슬롯으로 강제 보정
    if (slot && !zone) {
      const R = roles(team);
      if (slot === 'MB1' || slot === 'MB2') {
        slot = R.MBF || 'MB1';
        zone = zoneOfSlot(team, slot) || 3;
      } else {
        slot = R.Z1 || 'OHB';
        zone = zoneOfSlot(team, slot) || 1;
      }
    }

    return {
      slot,
      zone,
      pos: pl ? pl.position : null,
      key: slot ? `${team}.${slot}` : null,
      isSub,
      player: pl,
    };
  }
  const attackName = (a) => a.replace(/ ?(성공|아웃|네트걸림|포히트|터치넷|기타범실|오버넷|라인오버)$/, '');
  const resultWord = (a) => a.slice(attackName(a).length).trim();
  const evTone = (ev) => (BAD_RE.test(ev.a) ? 'bad' : (ev.ok && ['attack', 'serve', 'block'].includes(ev.c)) || /정확/.test(ev.a) ? 'good' : 'neutral');

  function recvLocal(info, deep, h) {
    if (info.zone) {
      const [zx, zy] = ZONES[info.zone];
      return info.zone >= 2 && info.zone <= 4 ? [60, zy] : [zx + (deep ? 4 : 12), zy];
    }
    const d = { L: [deep ? 24 : 30, 45], OH: [30, 22], OP: [30, 72], MB: [40, 45], S: [44, 58] }[info.pos] || [32, 45];
    return [d[0], d[1] + (h - 0.5) * 8];
  }
  function attackLocal(info) {
    if (info.zone) return info.zone >= 2 && info.zone <= 4 ? [85, ZY[info.zone]] : [57, ZY[info.zone]];
    return { OH: [85, 14], OP: [85, 78], MB: [85, 45], S: [85, 58], L: [57, 45] }[info.pos] || [85, 45];
  }
  function touchLocal(ev, info, seed, k) {
    const h = hash(seed, k, 7);
    switch (ev.c) {
      case 'serve': return [-5, 62 + Math.round(h * 22)];
      case 'receive': return recvLocal(info, false, h);
      case 'dig': return recvLocal(info, true, h);
      case 'set':
        if (info.pos === 'S') return [83, 58];
        return info.zone ? [ZONES[info.zone][0] + (info.zone >= 2 && info.zone <= 4 ? -12 : 10), ZONES[info.zone][1]] : [40, 50];
      case 'attack': return attackLocal(info);
      default: return [60, 45];
    }
  }
  function tempoOf(nx) {
    if (nx && nx.c === 'attack') {
      if (/퀵오픈|속공/.test(nx.a)) return { dur: 380, h: 6 };
      if (/시간차/.test(nx.a)) return { dur: 520, h: 16 };
      if (/이동/.test(nx.a)) return { dur: 480, h: 12 };
      if (/백어택/.test(nx.a)) return { dur: 760, h: 38 };
      if (/오픈/.test(nx.a)) return { dur: 800, h: 46 };
    }
    return { dur: 600, h: 26 };
  }

  function landingPoint(r, pts, seed) {
    const scoreIdx = r.point_idx - 1;
    const lg = pts[scoreIdx];
    const loser = other(r.scorer);
    const h = hash(seed, 99, 3), h2 = hash(seed, 98, 5);
    const inb = (team, xr, yr) => toGlobal(team, [lerp(xr[0], xr[1], h), lerp(yr[0], yr[1], h2)]);
    switch (r.cause) {
      case 'kill': return inb(loser, [14, 70], [10, 80]);
      case 'blockkill': return inb(loser, [58, 76], [12, 78]);
      case 'out': return h < 0.55 ? toGlobal(r.scorer, [-3 - h2 * 3, 8 + h2 * 74]) : toGlobal(r.scorer, [10 + h * 70, h2 < 0.5 ? -3 : 93]);
      case 'net': case 'touchnet': return { x: 90, y: clamp(lg.y, 4, 86) };
      case 'overnet': return toGlobal(r.scorer, [76, 20 + h * 50]);
      case 'drop': return { x: lg.x + (h - 0.5) * 8, y: lg.y + (h2 - 0.5) * 8 };
      default: return { x: lg.x, y: lg.y };
    }
  }

  function planRally(r) {
    const seed = r.set_no * 100 + r.rally_no;
    const n = r.events.length;
    const infos = [], pts = [];
    let lastAtk = null;
    r.events.forEach((ev, k) => {
      const info = infoOf(ev.t, ev.pid, ev); infos.push(info);
      let g;
      if (ev.c === 'block' || ev.c === 'block_assist') {
        const y = lastAtk ? lastAtk.y : (info.zone ? toGlobal(ev.t, [0, ZY[info.zone]]).y : 45);
        g = { x: toGlobal(ev.t, [87.5, 0]).x, y: clamp(y + (hash(seed, k, 1) - 0.5) * 6, 6, 84) };
      } else {
        g = toGlobal(ev.t, touchLocal(ev, info, seed, k));
      }
      if (ev.c === 'attack') lastAtk = g;
      pts.push(g);
    });
    const landing = landingPoint(r, pts, seed);
    const flights = r.events.map((ev, k) => {
      const nx = r.events[k + 1];
      const from = pts[k], to = k + 1 < n ? pts[k + 1] : landing;
      let base, h = 8;
      switch (ev.c) {
        case 'serve': base = 900; h = 30; break;
        case 'receive': case 'dig': base = 700; h = 34; break;
        case 'set': { const t = tempoOf(nx); base = t.dur; h = t.h; break; }
        case 'attack': base = nx && /^block/.test(nx.c) ? 240 : 430; h = 4; break;
        case 'block': base = 330; h = 8; break;
        default: base = 220; h = 6;
      }
      const dist = Math.hypot(to.x - from.x, to.y - from.y);
      return { from, to, h, dur: Math.max(200, base * Math.min(1, 0.35 + dist / 80)) };
    });
    return { infos, pts, landing, flights };
  }

  const josa = (w, pair) => `${w}${hasBatchim(w) ? pair[0] : pair[1]}`;
  function touchText(r, k) {
    const ev = r.events[k]; const team = short(ev.t); const nm = ev.n; const res = resultWord(ev.a);
    const info = S.rp && S.rp.infos ? S.rp.infos[k] : null;
    const subPfx = (info && info.isSub) ? '🔄(교체 투입) ' : '';
    switch (ev.c) {
      case 'serve':
        return `${subPfx}${team} ${nm}의 ${ev.a.startsWith('스파이크') ? '스파이크 서브' : '서브'}` +
          (ev.ok ? ' — 서브 에이스!' : BAD_RE.test(ev.a) ? ` — 서브 범실(${res}).` : '.');
      case 'receive':
        return `${subPfx}${nm}의 리시브` + (res === '정확' ? ' — 정확하게 세터 앞으로!' : res === '실패' ? ' — 리시브가 무너집니다.' : '.');
      case 'set':
        return `${subPfx}${nm}의 토스` + (res === '정확' ? ' — 공격수에게 정확한 연결.' : BAD_RE.test(ev.a) ? ` — 토스 범실(${res}).` : '.');
      case 'attack': {
        const an = attackName(ev.a);
        if (ev.ok) return `${subPfx}${nm}의 ${an}! 득점 성공!`;
        if (/아웃|라인오버/.test(res)) return `${subPfx}${nm}의 ${an}, 공이 코트 밖으로 벗어납니다.`;
        if (/네트걸림/.test(res)) return `${subPfx}${nm}의 ${an}, 네트에 걸립니다.`;
        if (/포히트/.test(res)) return `${subPfx}${nm}의 ${an}, 더블 컨택 범실.`;
        return `${subPfx}${nm}의 ${an}! 상대가 반응합니다.`;
      }
      case 'block':
        if (ev.ok) return `${subPfx}${nm}의 블로킹 — 득점!`;
        if (/터치넷/.test(res)) return `${subPfx}${nm}의 블로킹, 네트 터치 범실.`;
        if (/실패/.test(res)) return `${subPfx}${nm}의 블로킹이 공을 잡지 못합니다.`;
        if (ev.a === '유효 블로킹') return `${subPfx}${nm}의 유효 블로킹 — 공의 속도를 줄입니다.`;
        return `${subPfx}${nm}의 블로킹, 공을 건드립니다.`;
      case 'block_assist': return `${subPfx}${nm}, 블로킹에 가담합니다.`;
      case 'dig':
        if (/실패/.test(res)) return `${subPfx}${josa(nm, '이가')} 디그에 실패합니다.`;
        if (/범실/.test(res)) return `${subPfx}${nm}의 디그 범실.`;
        return `${subPfx}${nm}의 디그 — 걷어 올립니다!`;
      default: return `${subPfx}${nm} ${ev.a}`;
    }
  }
  const tagOf = (ev) => ({ serve: '#서브', receive: '#리시브', set: '#토스', attack: '#' + attackName(ev.a), block: '#블로킹', block_assist: '#블로킹', dig: '#디그' }[ev.c]);

  function resultSummary(r) {
    const last = r.events[r.point_idx - 1];
    if (r.cause === 'kill' || r.cause === 'blockkill') return `${last.n} ${last.a}`;
    return `${short(last.t)} ${last.n} ${last.a} → 상대 득점`;
  }

  // 세트별 주요 득점 장면 5개 자동 선정 (긴 랠리·블로킹·서브 에이스·접전·세트 마무리)
  const HL = {};
  function highlightsOf(n) {
    if (HL[n]) return HL[n];
    const all = D.ralliesBySet[n] || [];
    const win = setInfo(n).winner;
    const sc = all.map((r, idx) => {
      const last = r.events[r.point_idx - 1]; const why = []; let v = r.events.length * 0.9;
      if (r.events.length >= 9) why.push(`${r.events.length}터치 장기 랠리`);
      if (r.cause === 'blockkill') { v += 6; why.push('블로킹 득점'); }
      if (last && last.c === 'serve' && last.ok) { v += 5; why.push('서브 에이스'); }
      const t1 = D.teamIds[0], t2 = D.teamIds[1];
      const s1 = r.after[t1] || 0, s2 = r.after[t2] || 0;
      const b1 = r.before[t1] || 0, b2 = r.before[t2] || 0;
      const mx = Math.max(s1, s2), df = Math.abs(s1 - s2);
      if (mx >= 20 && df <= 2) { v += 4; why.push('접전 구간'); }
      if (b1 === b2 || (b1 - b2) * (s1 - s2) < 0) { v += 1.5; if (mx >= 10) why.push('동점·역전'); }
      if (idx === all.length - 1) { v += 9; why.unshift('세트 마무리'); }
      if (r.scorer === win) v += 0.5;
      if (!why.length) why.push('결정적 득점');
      return { r, idx, v, why };
    });
    const picked = [];
    [...sc].sort((a, b) => b.v - a.v).forEach((c) => {
      if (picked.length < 5 && picked.every((p) => Math.abs(p.idx - c.idx) >= 3)) picked.push(c);
    });
    [...sc].sort((a, b) => b.v - a.v).forEach((c) => { if (picked.length < 5 && !picked.includes(c)) picked.push(c); });
    picked.sort((a, b) => a.idx - b.idx);
    picked.forEach((c) => (c.r.hlWhy = c.why.slice(0, 2).join(' · ')));
    return (HL[n] = picked.map((c) => c.r));
  };

  const repList = () => {
    const all = D.ralliesBySet[D.setNo] || [];
    if (S.rf === 'hl') return highlightsOf(D.setNo);
    if (S.rf === 'long') return all.filter((r) => r.events.length >= 9);
    const t1 = D.teamIds[0], t2 = D.teamIds[1];
    if (S.rf === t1 || S.rf === t2) return all.filter((r) => r.scorer === S.rf);
    return all;
  };

  function startRally(i) {
    const list = repList(); const r = list[i]; if (!r) return;
    resetAllTokens();
    const plan = planRally(r);
    // 이 랠리에 참여하는 교체 선수들을 미리 코트 토큰에 반영!
    plan.infos.forEach((info) => {
      if (info.isSub && info.key && info.player) {
        updateTokenPlayer(info.key, info.player, true);
      }
    });
    const base = baseFormation();
    S.rp = { i, r, n: r.events.length, ...plan, base, target: { ...base }, k: 0, t: 0, dur: 1, from: null, to: null, h: 0 };
    S.pos = { ...base };
    S.live = { ...r.before };
    S.finished = false;
    clearTrails();
    renderScoreboard();
    renderRallyList(true);
    startStep(0);
  }

  function startStep(k) {
    const rp = S.rp; const r = rp.r; const ev = r.events[k]; const info = rp.infos[k]; const fl = rp.flights[k];
    rp.k = k; rp.t = 0; rp.from = fl.from; rp.to = fl.to; rp.dur = fl.dur; rp.h = fl.h;
    rp.target = { ...rp.base };
    if (info.key && ['serve', 'attack', 'block', 'set', 'receive', 'dig'].includes(ev.c)) {
      rp.target[info.key] = { x: rp.pts[k].x, y: rp.pts[k].y };
    }
    S.ball = { show: true, x: fl.from.x, y: fl.from.y, h: 0 };
    S.focusKey = info.key;

    if (info.key) {
      if (info.isSub && info.player) {
        updateTokenPlayer(info.key, info.player, true);
      } else if (!info.isSub) {
        const starter = playerOf(ev.t, info.slot);
        if (starter) updateTokenPlayer(info.key, starter, false);
      }
    }

    showCall(`${info.isSub ? '🔄[교체] ' : ''}${ev.num} ${ev.n} · ${ev.a}`, evTone(ev), rp.pts[k]);
    if (S.autoFocus && ev.pid) selectPlayer(ev.pid, { silent: true });
    const hl = S.rf === 'hl';
    const total = (D.ralliesBySet[D.setNo] || []).length;
    const tags = [k === 0 ? `#${short(ev.t)}서브` : tagOf(ev), `#${setInfo(D.setNo).set_no}세트`];
    if (info.isSub) tags.unshift('#교체선수');
    setCaster(hl ? `⭐ 하이라이트 ${rp.i + 1}/${repList().length} · ${r.hlWhy} · ${k + 1}/${rp.n}터치` : `랠리 ${r.rally_no}/${total} · ${k + 1}/${rp.n}터치`,
      tags,
      touchText(r, k), new Set([ev.n]), false);
    renderTimeline();
  }

  function startResult() {
    const rp = S.rp; const r = rp.r;
    rp.k = rp.n; rp.t = 0; rp.dur = S.rf === 'hl' ? 2600 : 1400; rp.target = { ...rp.base };
    S.ball = { show: true, x: rp.landing.x, y: rp.landing.y, h: 0 };
    S.focusKey = null;
    S.live = { ...r.after };
    renderScoreboard();
    const t1 = D.teamIds[0], t2 = D.teamIds[1];
    showCall(`${short(r.scorer)} 득점!  ${r.after[t1]} : ${r.after[t2]}`, 'score', rp.landing);
    const sum = resultSummary(r);
    setCaster(S.rf === 'hl' ? `⭐ 하이라이트 ${rp.i + 1}/${repList().length} 종료 · ${r.hlWhy}` : `랠리 ${r.rally_no} 종료`, [`#${short(r.scorer)}득점`, `#${r.events.length}터치`],
      `득점! ${short(r.scorer)} — ${sum}. 스코어 ${short(t1)} ${r.after[t1]} : ${r.after[t2]} ${short(t2)}.`, new Set(), false);
    const li = document.createElement('li');
    li.innerHTML = `<b>#${r.rally_no}</b>${esc(short(r.scorer))} ${r.after[t1]}:${r.after[t2]} — ${esc(sum)} (${r.events.length}터치)`;
    $('castLog').prepend(li);
    renderTimeline();
  }

  function advanceReplay(dt) {
    const rp = S.rp; const dts = dt * S.speed * (S.rf === 'hl' ? 0.55 : 1); // 하이라이트는 슬로우 연출
    const a = 1 - Math.exp(-dts / 130);
    for (const k in rp.target) {
      const c = S.pos[k] || rp.target[k], t = rp.target[k];
      S.pos[k] = { x: c.x + (t.x - c.x) * a, y: c.y + (t.y - c.y) * a, bench: t.bench };
    }
    rp.t += dts;
    if (rp.k < rp.n) {
      const p = clamp01(rp.t / rp.dur);
      S.ball = { show: true, x: lerp(rp.from.x, rp.to.x, p), y: lerp(rp.from.y, rp.to.y, p), h: 4 * rp.h * p * (1 - p) };
      if (p >= 1) { if (rp.k + 1 < rp.n) startStep(rp.k + 1); else startResult(); }
    } else if (rp.t >= rp.dur) {
      const list = repList();
      if (rp.i + 1 < list.length) startRally(rp.i + 1);
      else finishReplay();
    }
    const step = rp.k + (rp.k < rp.n ? clamp01(rp.t / rp.dur) : 1);
    $('progressBar').style.width = `${(step / (rp.n + 1)) * 100}%`;
  }

  function finishReplay() {
    S.playing = false; S.finished = true; S.focusKey = null;
    resetAllTokens();
    const s = setInfo(D.setNo);
    const t1 = D.teamIds[0], t2 = D.teamIds[1];
    setCaster('리플레이 종료', [`#${D.setNo}세트`], `${D.setNo}세트 리플레이가 끝났습니다. 최종 스코어 ${short(t1)} ${getSetScore(s, t1)} : ${getSetScore(s, t2)} ${short(t2)} — ${short(s.winner)} 승.`, new Set(), false);
    renderTimeline(); updateControls(); renderRallyList();
  }

  function renderRallyList(scroll) {
    const list = repList();
    const t1 = D.teamIds[0], t2 = D.teamIds[1];
    const filters = [['hl', '⭐ 하이라이트 5'], ['all', '전체'], ['long', '긴 랠리(9터치+)'], [t1, `${short(t1)} 득점`], [t2, `${short(t2)} 득점`]];
    $('rallyFilters').innerHTML = filters.map(([k, l]) => `<button class="rf ${S.rf === k ? 'active' : ''}" data-k="${k}">${esc(l)}</button>`).join('');
    $('rallyFilters').querySelectorAll('.rf').forEach((b) => b.addEventListener('click', () => {
      S.rf = b.dataset.k; stopAll(); idle(); renderRallyList();
    }));
    $('rallyList').innerHTML = list.length ? list.map((r, i) => {
      const last = r.events[r.point_idx - 1];
      const cur = S.rp && S.rp.r === r;
      return `<button class="ry ${cur ? 'current' : ''}" data-i="${i}" style="--rc:${color(r.scorer)}">
        <span class="no">#${r.rally_no}</span>
        <div><div class="t1">${esc(short(r.scorer))} 득점 <span class="sc">${short(t1)[0]} ${r.after[t1]} : ${r.after[t2]} ${short(t2)[0]}</span></div>
        <div class="t2">${S.rf === 'hl' ? `<b>${esc(r.hlWhy)}</b> · ` : ''}${esc(last.n)} ${esc(last.a)} · <span class="len">${r.events.length}</span>터치</div></div></button>`;
    }).join('') : '<div class="rally-empty">조건에 맞는 랠리가 없습니다.</div>';
    $('rallyList').querySelectorAll('.ry').forEach((b) => b.addEventListener('click', () => {
      $('castLog').innerHTML = '';
      startRally(+b.dataset.i); S.playing = true; updateControls();
    }));
    if (scroll) $('rallyList').querySelector('.current')?.scrollIntoView({ block: 'nearest' });
  }

  function stepRally(delta) {
    if (S.mode !== 'replay') return;
    const list = repList(); if (!list.length) return;
    const i = clamp((S.rp ? S.rp.i : -1) + delta, 0, list.length - 1);
    const was = S.playing;
    startRally(i); S.playing = was; updateControls();
  }

  // ───────────────────────── 루프 ─────────────────────────
  function tick(now) {
    const dt = Math.min(64, now - (tick.last || now)); tick.last = now;
    if (S.tween) {
      S.tween.t += dt;
      const p = ease(clamp01(S.tween.t / S.tween.dur));
      for (const k in S.tween.to) {
        const a = S.tween.from[k] || S.tween.to[k], b = S.tween.to[k];
        S.pos[k] = { x: lerp(a.x, b.x, p), y: lerp(a.y, b.y, p), bench: b.bench };
      }
      if (p >= 1) S.tween = null;
      renderCourt();
    } else if (S.playing && S.mode === 'replay' && S.rp) {
      advanceReplay(dt);
      renderCourt();
    } else if (S.playing && S.mode === 'scenario' && S.run) {
      S.t += dt * S.speed;
      const f = clamp01(S.t / S.run.dur);
      applyRun(S.run, f);
      $('progressBar').style.width = `${((S.phase + f) / scen().phases.length) * 100}%`;
      if (f >= 1) {
        if (S.phase < scen().phases.length - 1) startPhase(S.phase + 1);
        else { S.playing = false; S.finished = true; renderTimeline(); updateControls(); }
      }
      renderCourt();
    }
    requestAnimationFrame(tick);
  }

  function tweenTo(target, dur = 650) { S.tween = { from: { ...S.pos }, to: target, t: 0, dur }; }
  function stopTween() { if (S.tween) { S.pos = { ...S.pos, ...S.tween.to }; S.tween = null; } }

  // ───────────────────────── 해설 ─────────────────────────
  function hasBatchim(word) {
    const c = String(word).trim().slice(-1).charCodeAt(0) - 0xac00;
    if (c >= 0 && c <= 11171) return c % 28 !== 0;
    return /[0-9]$/.test(word) ? /[0136789]$/.test(word) : false;
  }
  function playerField(p, f) {
    const mt = (a, b) => `${p[a]}/${p[b]}`;
    switch (f) {
      case 'name': return p.name;
      case 'attPct': return p.att_pct ?? '-';
      case 'attPctS': return p.att_pct != null ? `${p.att_pct}%` : '기록 없음';
      case 'share': return p.att_share ?? '-';
      case 'shareS': return p.att_share != null ? `${p.att_share}%` : '기록 없음';
      case 'dig': return mt('dig_made', 'dig_tried');
      case 'rcv': return mt('rcv_made', 'rcv_tried');
      case 'blk': return mt('blk_made', 'blk_tried');
      case 'set': return mt('set_made', 'set_tried');
      case 'pts': return p.points ?? 0;
      case 'err': return p.errors ?? 0;
      default: return '?';
    }
  }
  function teamField(team, f) {
    const s = D.summary[team];
    switch (f) {
      case 'short': return D.teams[team].short_name;
      case 'blk': return `${s.blk_made}/${s.blk_tried}`;
      case 'rcv': return s.rcv_pct;
      case 'att': return s.att_pct;
      case 'dig': return s.dig_pct;
      default: return '?';
    }
  }
  function fillTemplate(tpl, R, T) {
    const names = new Set();
    const text = tpl.replace(/\{(atk|def)\.(\w+)\.(\w+)(?:\|([^}]+))?\}/g, (_, side, role, field, part) => {
      const team = T[side];
      let v;
      if (role === 'team') v = teamField(team, field);
      else { const p = playerOf(team, R[side][role]); v = playerField(p, field); if (field === 'name') names.add(p.name); }
      if (part && part.length === 2) v = `${v}${hasBatchim(v) ? part[0] : part[1]}`;
      return v;
    });
    return { text, names };
  }
  function highlight(text, names) {
    let h = esc(text);
    [...names].sort((a, b) => b.length - a.length).forEach((n) => { h = h.split(esc(n)).join(`<strong>${esc(n)}</strong>`); });
    return h;
  }

  function setCaster(title, tags, text, names = new Set(), log = true) {
    const box = $('casterText');
    if (log && S.typing && S.typing.full) {
      const li = document.createElement('li');
      li.innerHTML = `<b>${esc(S.typing.title)}</b>${esc(S.typing.full)}`;
      $('castLog').prepend(li);
    }
    clearInterval(typeTimer);
    $('casterPhase').textContent = title;
    $('casterTags').innerHTML = tags.map((t) => `<span class="tag">${esc(t)}</span>`).join('');
    let i = 0;
    const html = highlight(text, names);
    S.typing = { title, full: text };
    const id = setInterval(() => step(), 26 / S.speed);
    typeTimer = id;
    function step() {
      if (typeTimer !== id) return clearInterval(id);
      i += 2;
      if (i >= text.length) { box.innerHTML = html; clearInterval(id); return; }
      box.innerHTML = `${esc(text.slice(0, i))}<span class="cursor"></span>`;
    }
    step();
  }

  function narrate(run) {
    const { text, names } = fillTemplate(run.ph.text, run.R, run.T);
    setCaster(`${run.i + 1}. ${run.ph.name}`, run.ph.tags || [], text, names);
  }

  function introCaster() {
    $('castLog').innerHTML = '';
    S.typing = null;
    const ctx = D.setNo ? `[${D.setNo}세트 기록 기준] ` : '';
    if (S.mode === 'replay') {
      const n = (D.ralliesBySet[D.setNo] || []).length;
      const s = setInfo(D.setNo);
      setCaster(`${D.setNo}세트 리플레이`, ['#실제기록', `#득점랠리${n}개`],
        `${D.setNo}세트의 주요 득점 장면 5개(⭐ 하이라이트)를 자동 선정했습니다. ▶ 재생을 누르면 하이라이트 릴로 이어서 재생되고, '전체' 필터에서는 득점 랠리 ${n}개를 모두 재현합니다 (정관장 ${s.kgc_score} : ${s.hdec_score} 현대건설). 선수·공의 위치는 기록된 터치 순서를 바탕으로 한 근사 연출입니다.`,
        new Set(), false);
      return;
    }
    const sc = scen();
    setCaster('대기', ['#' + D.teams[sc.attack_team].short_name + '공격'],
      `${ctx}「${sc.title}」 — ${sc.subtitle}. ▶ 재생을 누르면 세터 토스 타이밍에 맞춘 공격수 동선이 시뮬레이션됩니다.`, new Set(), false);
  }

  // ───────────────────────── UI 렌더 ─────────────────────────
  function applyTheme() {
    const root = document.documentElement;
    root.dataset.theme = S.theme;
    const h = D.teams[S.home];
    root.style.setProperty('--primary', h.primary_color);
    root.style.setProperty('--accent', h.accent_color);
    root.style.setProperty('--home', color(S.home));
    root.style.setProperty('--away', color(away()));
    $('homeLabel').textContent = `HOME: ${h.short_name}`;
    $('lgHome').textContent = `${D.teams[S.home].short_name} (HOME)`;
    $('lgAway').textContent = `${D.teams[away()].short_name} (AWAY)`;
  }

  function renderScoreboard() {
    const score = (id) => {
      if (S.live) return S.live[id];
      if (D.setNo > 0) {
        const s = setInfo(D.setNo);
        return getSetScore(s, id);
      }
      return RAW.sets.filter((s) => s.winner === id).length;
    };
    const midTop = S.live ? `SET ${D.setNo} · LIVE` : D.setNo > 0 ? `SET ${D.setNo} 최종` : '세트 스코어';
    const team = (id, tag) => {
      const v = score(id);
      const pop = S.lastScore[id] != null && S.lastScore[id] !== v ? ' pop' : '';
      S.lastScore[id] = v;
      return `
      <div class="sb-team">
        <span class="sb-swatch" style="background:${color(id)}"></span>
        <div><span class="sb-tag">${tag}${S.mode === 'scenario' ? ` · R${(S.rotCount[id] % 6) + 1}` : ''}</span><span class="sb-name">${esc(short(id))}</span></div>
        <span class="sb-score${pop}" style="color:${color(id)}">${v}</span>
      </div>`;
    };
    $('scoreboard').innerHTML = `${team(S.home, 'HOME')}<div class="sb-mid"><span class="sb-set">${midTop}</span><span class="sb-vs">VS</span></div>${team(away(), 'AWAY')}`;
  }

  function renderSetBar() {
    const t1 = D.teamIds[0], t2 = D.teamIds[1];
    const wins = (id) => RAW.sets.filter((s) => s.winner === id).length;
    const abbr = (t) => `<span style="color:${color(t)};font-weight:800">${esc(short(t).slice(0, 1))}</span>`;
    const btn = (n, name, a, b, wc) => `
      <button class="setbtn ${D.setNo === n ? 'active' : ''}" data-n="${n}" role="tab" aria-selected="${D.setNo === n}" style="--wc:${wc}">
        <span class="sb-n">${name}</span>
        <span class="sb-sc">${abbr(t1)}<b>${a}</b> : <b>${b}</b>${abbr(t2)}</span></button>`;
    $('setBtns').innerHTML =
      btn(0, '전체', wins(t1), wins(t2), color(wins(t1) >= wins(t2) ? t1 : t2)) +
      RAW.sets.map((s) => btn(s.set_no, `${s.set_no}세트`, getSetScore(s, t1), getSetScore(s, t2), color(s.winner))).join('');
    $('setBtns').querySelectorAll('.setbtn').forEach((b) => b.addEventListener('click', () => setView(+b.dataset.n)));
  }

  function renderHeadline() {
    const a = analyze(D.setNo);
    $('setHeadline').innerHTML = `<span class="hl-main">${esc(a.headline)}</span>${a.chips.map((c) => `<span class="hl-chip">${esc(c)}</span>`).join('')}`;
    let insHtml = `<div class="section-label">Data Insights · ${esc(D.view.label)}</div><ul>${a.bullets.map((x) => `<li>${x}</li>`).join('')}</ul>`;
    if (RAW.best_players) {
      insHtml += `<div class="best-player-box" style="margin-top:10px;padding:8px 10px;background:rgba(255,255,255,0.05);border-radius:8px;border:1px solid rgba(255,255,255,0.1);">
        <div style="font-weight:700;font-size:11px;color:var(--accent);margin-bottom:4px;">🏆 팬 투표 BEST 플레이어</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11px;">
          ${D.teamIds.map(t => RAW.best_players[t] ? `<div><b style="color:${color(t)}">${esc(short(t))}</b><ol style="margin:2px 0 0 14px;padding:0;line-height:1.4;">
            ${RAW.best_players[t].map(p => `<li><b>${esc(p.name)}</b> (${p.pct}%)</li>`).join('')}
          </ol></div>` : '').join('')}
        </div>
      </div>`;
    }
    if (RAW.key_players) {
      const kp = RAW.key_players;
      const t1 = D.teamIds[0], t2 = D.teamIds[1];
      insHtml += `<div class="key-player-box" style="margin-top:8px;padding:8px 10px;background:rgba(255,255,255,0.03);border-radius:8px;border:1px solid rgba(255,255,255,0.08);font-size:11px;">
        <div style="font-weight:700;font-size:11px;color:#38bdf8;margin-bottom:4px;">⚡ 키플레이어 매치업</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:3px;line-height:1.4;">
          <div>득점: <b style="color:${color(t1)}">${kp.points[t1].name} ${kp.points[t1].val}</b> vs <b style="color:${color(t2)}">${kp.points[t2].name} ${kp.points[t2].val}</b></div>
          <div>공격: <b style="color:${color(t1)}">${kp.attacks[t1].name} ${kp.attacks[t1].val}</b> vs <b style="color:${color(t2)}">${kp.attacks[t2].name} ${kp.attacks[t2].val}</b></div>
          <div>블록: <b style="color:${color(t1)}">${kp.blocks[t1].name} ${kp.blocks[t1].val}</b> vs <b style="color:${color(t2)}">${kp.blocks[t2].name} ${kp.blocks[t2].val}</b></div>
          <div>디그: <b style="color:${color(t1)}">${kp.digs[t1].name} ${kp.digs[t1].val}</b> vs <b style="color:${color(t2)}">${kp.digs[t2].name} ${kp.digs[t2].val}</b></div>
        </div>
      </div>`;
    }
    $('insights').innerHTML = insHtml;
  }

  function renderMatchStats() {
    const h = D.summary[S.home], a = D.summary[away()];
    const rows = [
      ['공격 성공률', h.att_pct, a.att_pct, '%'],
      ['블로킹 득점', h.blk_made, a.blk_made, ''],
      ['서브 득점', h.srv_made, a.srv_made, ''],
      ['디그 성공률', h.dig_pct, a.dig_pct, '%'],
      ['리시브 정확', h.rcv_pct, a.rcv_pct, '%'],
      ['범실', h.errors, a.errors, ''],
    ];
    const ch = color(S.home), ca = color(away());
    $('matchStats').innerHTML = `
      <div class="section-label">Match Stats · ${esc(D.view.label)} · ${esc(D.source || '')}</div>
      <div class="ms-head"><span style="color:${ch}">${esc(D.teams[S.home].short_name)}</span><span style="color:${ca}">${esc(D.teams[away()].short_name)}</span></div>
      ${rows.map(([lab, x, y, u]) => {
      const tot = (Number(x) || 0) + (Number(y) || 0) || 1;
      return `<div class="ms-row">
          <span class="v l">${x ?? '-'}${u}</span>
          <div class="ms-bar l"><i style="width:${((x || 0) / tot) * 100}%;background:${ch}"></i></div>
          <span class="lab">${lab}</span>
          <div class="ms-bar"><i style="width:${((y || 0) / tot) * 100}%;background:${ca}"></i></div>
          <span class="v r">${y ?? '-'}${u}</span></div>`;
    }).join('')}`;
  }

  function renderTabs() {
    $('teamTabs').innerHTML = [S.home, away()].map((id) => `
      <button class="tab ${id === S.panelTeam ? 'active' : ''}" data-team="${id}" style="--tc:${color(id)}">
        <span class="dot" style="background:${color(id)}"></span>${esc(D.teams[id].short_name)}
        <span class="muted" style="font-size:11px">${id === S.home ? 'HOME' : 'AWAY'}</span></button>`).join('');
    $('teamTabs').querySelectorAll('.tab').forEach((b) => b.addEventListener('click', () => {
      S.panelTeam = b.dataset.team; renderTabs(); renderList(); updateControls();
    }));
  }

  function courtStatus(team, slot) {
    const z = zoneOfSlot(team, slot);
    if (z == null) return '교체 대기';
    return [2, 3, 4].includes(z) ? `전위 ${z}번` : `후위 ${z}번`;
  }

  function highlightText(text, q) {
    if (!q) return esc(text);
    const s = String(text);
    const idx = s.toLowerCase().indexOf(q.toLowerCase());
    if (idx === -1) return esc(s);
    return `${esc(s.slice(0, idx))}<mark class="hl">${esc(s.slice(idx, idx + q.length))}</mark>${esc(s.slice(idx + q.length))}`;
  }

  function renderList() {
    const q = (S.searchQuery || '').trim().toLowerCase();

    // 검색어가 활성화된 경우: 양팀 전체 선수 대상 실시간 빠른 검색
    if (q) {
      const allPlayers = Object.values(D.players);
      const matched = allPlayers.filter((p) => {
        const n = (p.name || '').toLowerCase();
        const num = p.number != null ? String(p.number) : '';
        const pos = (p.position || '').toLowerCase();
        const posKo = (POS_KO[p.position] || '').toLowerCase();
        const teamKo = (D.teams[p.team_id]?.name || '').toLowerCase();
        const teamShort = (D.teams[p.team_id]?.short_name || '').toLowerCase();
        return (
          n.includes(q) ||
          num === q.replace('#', '') ||
          pos.includes(q) ||
          posKo.includes(q) ||
          teamKo.includes(q) ||
          teamShort.includes(q)
        );
      }).sort((a, b) => {
        const ea = a.name.toLowerCase() === q ? 1 : 0;
        const eb = b.name.toLowerCase() === q ? 1 : 0;
        return eb - ea || (b.points || 0) - (a.points || 0) || (b.sets_played || 0) - (a.sets_played || 0);
      });

      const countEl = $('searchCount');
      if (countEl) countEl.textContent = `${matched.length}명 검색`;

      if (!matched.length) {
        $('playerList').innerHTML = `<div class="search-empty-box">🔍 "${esc(S.searchQuery)}" 검색 결과가 없습니다.<br><small style="color:var(--muted);display:block;margin-top:4px;">선수명, 등번호(#88, #17), 포지션(OH, MB, OP, S, L)을 입력해 보세요.</small></div>`;
        return;
      }

      $('playerList').innerHTML = matched.map((p) => {
        const team = p.team_id;
        const lu = D.lineups[team] || {};
        const slot = Object.keys(lu).find((s) => lu[s] === p.id);
        const statPreview = p.points != null ? `${p.points}점` : (p.att_pct != null ? `${p.att_pct}%` : '-');
        return `<button class="pl-item ${p.id === S.selected ? 'selected' : ''}" data-id="${p.id}" style="--tc:${color(team)}">
          <span class="pl-team-tag" style="background:${color(team)}">${short(team)}</span>
          <span class="pl-pos">${p.position}</span>
          <span class="pl-name">${highlightText(p.name, q)}${p.number != null ? `<small>#${p.number}</small>` : ''}</span>
          <span class="pl-badge">${slot ? `★ ${courtStatus(team, slot)}` : ''}</span>
          <span class="pl-num">${statPreview}</span></button>`;
      }).join('');
      $('playerList').querySelectorAll('.pl-item').forEach((b) => b.addEventListener('click', () => selectPlayer(+b.dataset.id)));
      return;
    }

    // 일반 목록: 선택된 팀 탭 선수 목록
    const countEl = $('searchCount');
    if (countEl) countEl.textContent = '';

    const team = S.panelTeam;
    const lu = D.lineups[team];
    const slotOf = {}; for (const s in lu) slotOf[lu[s]] = s;
    const list = [...D.byTeam[team]].sort((a, b) => {
      const sa = slotOf[a.id] ? SLOTS.indexOf(slotOf[a.id]) : 99, sb = slotOf[b.id] ? SLOTS.indexOf(slotOf[b.id]) : 99;
      return sa - sb || (b.points || 0) - (a.points || 0) || (b.sets_played || 0) - (a.sets_played || 0);
    });
    $('playerList').innerHTML = list.map((p) => {
      const slot = slotOf[p.id];
      return `<button class="pl-item ${p.id === S.selected ? 'selected' : ''} ${p.sets_played ? '' : 'off'}" data-id="${p.id}" style="--tc:${color(team)}">
        <span class="pl-pos">${p.position}</span>
        <span class="pl-name">${esc(p.name)}${p.number != null ? `<small>#${p.number}</small>` : ''}</span>
        <span class="pl-badge">${slot ? `★ ${courtStatus(team, slot)}` : ''}</span>
        <span class="pl-num">${p.points != null ? p.points + '점' : '-'}</span></button>`;
    }).join('');
    $('playerList').querySelectorAll('.pl-item').forEach((b) => b.addEventListener('click', () => selectPlayer(+b.dataset.id)));
  }

  function radarSVG(p, c) {
    const M = D.radarMax;
    const axes = [
      ['공격', (p.att_pct || 0) / M.att], ['점유', (p.att_share || 0) / M.share],
      ['블로킹', (p.blk_per_set || 0) / M.blk], ['디그', (p.dig_per_set || 0) / M.dig],
      ['리시브', (p.rcv_tried >= 3 ? p.rcv_pct : 0) / M.rcv], ['세트', p.sets_played ? p.set_made / p.sets_played / M.set : 0],
    ];
    const R = 40, n = axes.length;
    const pt = (i, r) => { const a = -Math.PI / 2 + (i * 2 * Math.PI) / n; return [Math.cos(a) * r, Math.sin(a) * r]; };
    const grid = [0.25, 0.5, 0.75, 1].map((k) => `<polygon points="${axes.map((_, i) => pt(i, R * k).join(',')).join(' ')}" fill="none" stroke="var(--line)" stroke-width="1"/>`).join('');
    const spokes = axes.map((_, i) => `<line x1="0" y1="0" x2="${pt(i, R)[0]}" y2="${pt(i, R)[1]}" stroke="var(--line)"/>`).join('');
    const shape = axes.map(([, v], i) => pt(i, R * Math.max(0.03, Math.min(1, v || 0))).join(',')).join(' ');
    const labels = axes.map(([l], i) => { const [x, y] = pt(i, R + 10); return `<text x="${x}" y="${y + 2.5}">${l}</text>`; }).join('');
    return `<svg class="radar" viewBox="-60 -60 120 120" width="120" height="120">${grid}${spokes}
      <polygon points="${shape}" fill="${c}" fill-opacity=".35" stroke="${c}" stroke-width="1.6"/>${labels}</svg>`;
  }

  function renderCard() {
    const p = D.players[S.selected];
    if (!p) { $('playerCard').innerHTML = '<div class="pc-empty">코트 위 선수나 리스트에서<br>선수를 선택하세요</div>'; return; }
    const c = color(p.team_id);
    const lu = D.lineups[p.team_id]; const slot = Object.keys(lu).find((s) => lu[s] === p.id);
    const inSet = D.setNo > 0;
    const stat = (label, v, raw, show = true) => !show ? '' : `
      <div class="stat"><div class="stat-top"><span>${label} <span class="raw">${raw || ''}</span></span><b>${v == null ? '-' : v + '%'}</b></div>
      <div class="stat-bar"><i data-w="${Math.min(100, v || 0)}" style="background:${c}"></i></div></div>`;
    const chips = inSet
      ? [[p.points ?? '-', '득점'], [p.errors ?? '-', '범실'], [p.att_share != null ? p.att_share + '%' : '-', '공격 점유율']]
      : [[p.sets_played ?? '-', '출전 세트'], [p.points ?? '-', '득점'], [p.errors ?? '-', '범실']];
    const body = inSet && !p.sets_played
      ? '<div class="pc-empty" style="padding:18px 6px">이번 세트 출전 기록이 없습니다.</div>'
      : `<div class="pc-body"><div>
          ${stat('공격 성공률', p.att_pct, `${p.att_made}/${p.att_tried}`, !inSet || p.att_tried > 0)}
          ${stat('공격 점유율', p.att_share, '', p.att_share != null)}
          ${stat('블로킹', p.blk_pct, `${p.blk_made}/${p.blk_tried}`, p.blk_tried > 0)}
          ${stat('디그', p.dig_pct, `${p.dig_made}/${p.dig_tried}`, p.dig_tried > 0)}
          ${stat('리시브 정확', p.rcv_pct, `${p.rcv_made}/${p.rcv_tried}`, p.rcv_tried > 0)}
          ${stat('세트', p.set_pct, `${p.set_made}/${p.set_tried}`, p.set_tried >= 5)}
          ${stat('서브', p.srv_pct, `${p.srv_made}/${p.srv_tried}`, p.srv_tried > 0)}
        </div>${radarSVG(p, c)}</div>`;
    $('playerCard').innerHTML = `
      <div class="pc-head">
        <div class="pc-avatar" style="background:${c}">${p.number != null ? p.number : p.position}</div>
        <div><div class="pc-name">${esc(p.name)}</div>
        <div class="pc-sub">${esc(D.teams[p.team_id].short_name)} · ${POS_KO[p.position]} · ${esc(D.view.label)}${slot ? ` · <span style="color:var(--accent)">${courtStatus(p.team_id, slot)}</span>` : ''}</div></div>
      </div>
      <div class="pc-chips">${chips.map(([v, l]) => `<div class="pc-chip"><b>${v}</b><span>${l}</span></div>`).join('')}</div>
      ${body}
      <div class="pc-comment"><span class="ttl">ANALYSIS</span>${esc(p.comment || '')}</div>`;
    requestAnimationFrame(() => $('playerCard').querySelectorAll('.stat-bar i').forEach((i) => (i.style.width = i.dataset.w + '%')));
  }

  function selectPlayer(id, opts = {}) {
    S.selected = id;
    const p = D.players[id];
    if (p && S.panelTeam !== p.team_id) { S.panelTeam = p.team_id; renderTabs(); updateControls(); }
    renderList(); renderCard(); renderCourt();
    if (!opts.silent) $('playerList').querySelector('.selected')?.scrollIntoView({ block: 'nearest' });
  }

  function renderScenarios() {
    $('scenarioList').innerHTML = D.scenarios.map((s, i) => `
      <button class="sc-btn ${i === S.scenario ? 'active' : ''}" data-i="${i}">
        <span class="t"><span class="n">${i + 1}.</span>${esc(s.title)}</span>
        <span class="s">${esc(s.subtitle)}</span></button>`).join('');
    $('scenarioList').querySelectorAll('.sc-btn').forEach((b) => b.addEventListener('click', () => chooseScenario(+b.dataset.i)));
  }

  function renderModeUI() {
    document.querySelectorAll('.mode-tab').forEach((b) => b.classList.toggle('active', b.dataset.mode === S.mode));
    $('scenarioList').hidden = S.mode !== 'scenario';
    $('replayPane').hidden = S.mode !== 'replay';
    if (S.mode === 'replay') renderRallyList();
  }

  function renderTimeline() {
    if (S.mode === 'replay') {
      const rp = S.rp;
      if (!rp) {
        $('timeline').innerHTML = '';
        $('courtMeta').textContent = `${D.view.label} 리플레이 · 득점 랠리 ${(D.ralliesBySet[D.setNo] || []).length}개`;
        if (!S.finished) $('progressBar').style.width = '0%';
        return;
      }
      $('timeline').innerHTML = rp.r.events.map((ev, i) => {
        const cls = i === rp.k ? 'current' : i < rp.k || rp.k >= rp.n ? 'done' : '';
        const tone = evTone(ev);
        const isSub = rp.infos && rp.infos[i] && rp.infos[i].isSub;
        return `<button type="button" class="ph ev ${cls} ${tone === 'neutral' ? '' : tone} ${isSub ? 'is-sub' : ''}" data-step="${i}"><span class="i">${i + 1}</span>${isSub ? '<span class="sub-pill">교체</span>' : ''}${esc(CAT_KO[ev.c])} ${esc(ev.n)}</button>`;
      }).join('');
      $('timeline').querySelectorAll('.ph.ev').forEach((b) => b.addEventListener('click', () => {
        const step = +b.dataset.step;
        if (S.rp && step >= 0 && step < S.rp.n) {
          startStep(step);
          renderCourt();
        }
      }));
      $('courtMeta').textContent = `${D.view.label} 리플레이 · 랠리 #${rp.r.rally_no} · ${short(rp.r.scorer)} 득점 · ${rp.n}터치`;
      return;
    }
    const sc = scen();
    $('timeline').innerHTML = sc.phases.map((ph, i) => {
      const cls = i === S.phase && !S.finished ? 'current' : (i < S.phase || (S.finished && i <= S.phase)) ? 'done' : '';
      return `<button class="ph ${cls}" data-i="${i}"><span class="i">${i + 1}</span>${esc(ph.name)}</button>`;
    }).join('');
    $('timeline').querySelectorAll('.ph').forEach((b) => b.addEventListener('click', () => jumpTo(+b.dataset.i)));
    $('courtMeta').textContent = `${D.setNo ? D.view.label + ' 기준 · ' : ''}${sc.title} · 공격 ${D.teams[sc.attack_team].short_name}`;
    if (S.phase < 0) $('progressBar').style.width = '0%';
    if (S.finished) $('progressBar').style.width = '100%';
  }

  function updateControls() {
    $('btnPlay').disabled = S.playing;
    $('btnPause').disabled = !S.playing;
    $('btnRotate').disabled = S.playing || S.mode === 'replay';
    const started = S.mode === 'replay' ? !!S.rp : S.phase >= 0;
    $('btnPlay').querySelector('span').textContent = S.finished ? '다시 재생' : (started && !S.playing ? '이어서 재생' : '재생');
    $('btnRotate').querySelector('span').textContent = S.mode === 'replay' ? '로테이션 (리플레이 중 비활성)' : `로테이션 (${D.teams[S.panelTeam].short_name})`;
    const chip = $('statusChip');
    chip.textContent = S.playing ? '● 재생 중' : S.finished ? '■ 완료' : started ? '❚❚ 일시정지' : '대기';
    chip.classList.toggle('playing', S.playing);
  }

  // ───────────────────────── 컨트롤 동작 ─────────────────────────
  function stopAll() { S.playing = false; clearInterval(typeTimer); }

  function idle(keepCaster) {
    S.playing = false; S.finished = false; S.phase = -1; S.run = null; S.rp = null; S.live = null; S.focusKey = null;
    S.ball.show = false; clearTrails(); clearCall();
    resetAllTokens();
    tweenTo(baseFormation());
    renderScoreboard(); renderTimeline(); updateControls(); renderCourt();
    if (S.mode === 'replay') renderRallyList();
    if (!keepCaster) introCaster();
  }

  function play() {
    if (S.playing) return;
    if (S.mode === 'replay') {
      if (!S.rp || S.finished) {
        stopTween(); $('castLog').innerHTML = '';
        if (!repList().length) return;
        startRally(0);
      }
      S.playing = true; updateControls(); return;
    }
    if (S.phase < 0 || S.finished) {
      stopTween();
      S.pos = baseFormation(); S.ball.show = false; S.finished = false;
      $('castLog').innerHTML = ''; S.typing = null;
      startPhase(0);
    }
    S.playing = true; updateControls(); renderTimeline();
  }
  function pause() { S.playing = false; updateControls(); }

  function rotate() {
    if (S.playing || S.mode === 'replay') return;
    const team = S.panelTeam;
    const r = S.rot[team];
    S.rot[team] = [...r.slice(1), r[0]]; // 시계 방향: 2→1, 3→2, … 1→6
    S.rotCount[team]++;
    idle(true);
    const R = roles(team);
    const nm = (z) => playerOf(team, R['Z' + z]).name;
    setCaster(`↻ ${D.teams[team].short_name} 로테이션 R${(S.rotCount[team] % 6) + 1}`, ['#로테이션'],
      `전위 4·3·2번: ${nm(4)}·${nm(3)}·${nm(2)} / 후위 5·6·1번: ${nm(5)}·${nm(6)}·${nm(1)}. 후위 미들 ${playerOf(team, R.MBB).name} 대신 리베로가 들어갑니다. 서브는 ${nm(1)}.`,
      new Set(), false);
    renderScoreboard(); renderList(); renderCard();
  }

  function reset() {
    D.teamIds.forEach((t) => { S.rot[t] = [...BASE_ROT]; S.rotCount[t] = 0; });
    $('castLog').innerHTML = '';
    idle();
    renderScoreboard(); renderList(); renderCard();
  }

  function chooseScenario(i) {
    S.scenario = i; renderScenarios(); idle();
  }

  // 세트(0=전체) 전환: 선수 기록·라인업·해설 수치가 해당 세트 기준으로 바뀐다
  function setView(n) {
    if (!V[n]) return;
    stopAll(); stopTween();
    useView(n);
    if (n === 0 && S.mode === 'replay') S.mode = 'scenario';
    D.teamIds.forEach((t) => { S.rot[t] = [...BASE_ROT]; S.rotCount[t] = 0; });
    S.rp = null; S.live = null; S.lastScore = {};
    buildTokens();
    S.pos = baseFormation();
    renderSetBar(); renderHeadline(); renderMatchStats(); renderList(); renderCard(); renderModeUI();
    idle();
  }

  function setMode(m) {
    if (m === S.mode) return;
    S.mode = m;
    if (m === 'replay' && D.setNo === 0) { setView(1); return; }
    stopAll(); S.rp = null; S.live = null;
    renderModeUI(); idle();
  }

  function swapHome() {
    stopAll(); stopTween();
    S.home = away();
    S.pos = mirror(S.pos);
    applyTheme(); drawFloor(); renderScoreboard(); renderMatchStats(); renderTabs(); renderList(); renderCard();
    idle(true);
    setCaster('🏠 홈팀 전환', ['#테마'], `${D.teams[S.home].short_name} 홈 경기로 전환합니다. 화면 테마가 ${D.teams[S.home].short_name} 컬러로 바뀌고, 홈팀이 왼쪽 진영에 섭니다.`, new Set(), false);
  }
  function mirror(pos) {
    const out = {};
    for (const k in pos) out[k] = { x: 180 - pos[k].x, y: 90 - pos[k].y, bench: pos[k].bench };
    return out;
  }

  function switchMatch(dateVal) {
    if (!window.MATCHES) return false;
    const key = window.MATCHES[dateVal] ? dateVal :
      window.MATCHES[dateVal.replace('2024-', '2026-')] ? dateVal.replace('2024-', '2026-') :
        window.MATCHES[dateVal.replace('2026-', '2024-')] ? dateVal.replace('2026-', '2024-') :
          (dateVal.includes('11-04') && window.MATCHES['2024-11-04']) ? '2024-11-04' :
            (dateVal.includes('11-04') && window.MATCHES['2026-11-04']) ? '2026-11-04' :
              (dateVal.includes('11-03') && window.MATCHES['2024-11-03']) ? '2024-11-03' :
                (dateVal.includes('11-03') && window.MATCHES['2026-11-03']) ? '2026-11-03' :
                  (dateVal.includes('11-07') && window.MATCHES['2024-11-07']) ? '2024-11-07' :
                    (dateVal.includes('11-07') && window.MATCHES['2026-11-07']) ? '2026-11-07' : null;
    if (!key || !window.MATCHES[key]) return false;
    stopAll(); stopTween();
    const raw = window.MATCHES[key];
    S.matchDate = key;
    for (const k in HL) delete HL[k]; // 이전 경기 하이라이트 캐시 제거
    indexData(raw);
    S.home = D.teamIds.find((t) => D.teams[t].is_home) || D.teamIds[0];
    S.panelTeam = S.home;
    D.teamIds.forEach((t) => { S.rot[t] = [...BASE_ROT]; S.rotCount[t] = 0; });
    S.scenario = 0;
    S.phase = -1;
    S.selected = null;
    S.focusKey = null;
    S.live = null;
    S.rp = null;
    S.mode = 'scenario';

    const titleEl = $('mainTitle') || document.querySelector('h1');
    if (titleEl) {
      titleEl.textContent = `[${D.teams[S.home].short_name} vs ${D.teams[away()].short_name}] V-리그 전술 분석 & 리뷰 판`;
    }

    applyTheme();
    drawFloor();
    buildTokens();
    S.pos = baseFormation();
    renderSetBar();
    renderHeadline();
    renderScoreboard();
    renderMatchStats();
    renderTabs();
    renderList();
    selectPlayer(D.lineups[S.home].OH1, { silent: true });
    renderScenarios();
    renderModeUI();
    renderTimeline();
    updateControls();
    updateQuickChips(key);
    renderCourt();
    idle();
    return true;
  }

  function updateQuickChips(dateVal) {
    const chipsEl = $('quickChips');
    if (!chipsEl) return;
    if (dateVal.includes('11-03')) {
      chipsEl.innerHTML = `
        <button type="button" class="q-chip active" data-q="">전체</button>
        <button type="button" class="q-chip" data-q="빅토리아">빅토리아</button>
        <button type="button" class="q-chip" data-q="최정민">최정민</button>
        <button type="button" class="q-chip" data-q="이주아">이주아</button>
        <button type="button" class="q-chip" data-q="미와">미와</button>
        <button type="button" class="q-chip" data-q="이소영">이소영</button>
        <button type="button" class="q-chip" data-q="김하경">김하경</button>
        <button type="button" class="q-chip" data-q="조던">조던</button>
        <button type="button" class="q-chip" data-q="김다인">김다인</button>
        <button type="button" class="q-chip" data-q="배유나">배유나</button>
        <button type="button" class="q-chip" data-q="세터">세터</button>
        <button type="button" class="q-chip" data-q="리베로">리베로</button>
      `;
    } else if (dateVal.includes('11-04')) {
      chipsEl.innerHTML = `
        <button type="button" class="q-chip active" data-q="">전체</button>
        <button type="button" class="q-chip" data-q="킨델란">킨델란</button>
        <button type="button" class="q-chip" data-q="자스티스">자스티스</button>
        <button type="button" class="q-chip" data-q="표승주">표승주</button>
        <button type="button" class="q-chip" data-q="종휘">종휘</button>
        <button type="button" class="q-chip" data-q="박혜민">박혜민</button>
        <button type="button" class="q-chip" data-q="김수지">김수지</button>
        <button type="button" class="q-chip" data-q="정호영">정호영</button>
        <button type="button" class="q-chip" data-q="세터">세터</button>
        <button type="button" class="q-chip" data-q="리베로">리베로</button>
      `;
    } else {
      chipsEl.innerHTML = `
        <button type="button" class="q-chip active" data-q="">전체</button>
        <button type="button" class="q-chip" data-q="조던">조던</button>
        <button type="button" class="q-chip" data-q="메가">메가</button>
        <button type="button" class="q-chip" data-q="종휘">종휘</button>
        <button type="button" class="q-chip" data-q="박은진">박은진</button>
        <button type="button" class="q-chip" data-q="신은지">신은지</button>
        <button type="button" class="q-chip" data-q="이지수">이지수</button>
        <button type="button" class="q-chip" data-q="세터">세터</button>
        <button type="button" class="q-chip" data-q="리베로">리베로</button>
      `;
    }
    chipsEl.querySelectorAll('.q-chip').forEach((btn) => {
      btn.addEventListener('click', () => {
        const q = btn.dataset.q;
        const input = $('playerSearchInput');
        if (input) input.value = q;
        S.searchQuery = q;
        const clearBtn = $('playerSearchClear');
        if (clearBtn) clearBtn.style.display = q ? 'block' : 'none';
        chipsEl.querySelectorAll('.q-chip').forEach((b) => b.classList.toggle('active', b === btn));
        renderList();
        if (q) {
          const allPlayers = Object.values(D.players);
          const found = allPlayers.find((p) => (p.name || '').includes(q));
          if (found) selectPlayer(found.id);
        }
      });
    });
  }

  function bindMatchDate() {
    const form = $('matchDateForm');
    const input = $('matchDateInput');
    const select = $('matchSelect');
    if (!form || !input) return;

    function normalizeDate(raw) {
      if (!raw) return '2024-11-04';
      const s = String(raw).trim().toLowerCase();
      if (s.includes('기업') || s.includes('ibk') || s.includes('빅토리아') || s.includes('최정민') || s.includes('이소영') ||
        s.includes('11-03') || s.includes('1103') || s.includes('11/03') || s.includes('11/3') ||
        s.includes('11.03') || s.includes('11.3') || s === '03' || s === '3' ||
        s.endsWith('-03') || s.endsWith('.03') || s.endsWith('/03')) {
        return '2024-11-03';
      }
      if (s.includes('흥국') || s.includes('자스티스') || s.includes('킨델란') ||
        s.includes('11-04') || s.includes('1104') || s.includes('11/04') || s.includes('11/4') ||
        s.includes('11.04') || s.includes('11.4') || s === '04' || s === '4' ||
        s.endsWith('-04') || s.endsWith('.04') || s.endsWith('/04')) {
        return '2024-11-04';
      }
      if (s.includes('현대') || s.includes('메가') ||
        s.includes('11-07') || s.includes('1107') || s.includes('11/07') || s.includes('11/7') ||
        s.includes('11.07') || s.includes('11.7') || s === '07' || s === '7' ||
        s.endsWith('-07') || s.endsWith('.07') || s.endsWith('/07')) {
        return '2024-11-07';
      }
      return s;
    }

    const applyDate = (rawVal) => {
      const dateVal = normalizeDate(rawVal);
      S.matchDate = dateVal;

      // input이 type="date"여도 안전하도록 10자리 YYYY-MM-DD 유지
      if (input) {
        input.value = dateVal.length === 10 ? dateVal : ('2024-' + dateVal.slice(-5));
      }
      if (select) {
        const opt = Array.from(select.options).find(o => o.value === dateVal || o.value.slice(-5) === dateVal.slice(-5));
        if (opt) select.value = opt.value;
      }

      const display = $('matchDateDisplay');
      const DAYS = ['일', '월', '화', '수', '목', '금', '토'];
      const d = new Date(dateVal + 'T00:00:00');
      const dayName = isNaN(d.getTime()) ? '월' : DAYS[d.getDay()];

      if (dateVal.includes('11-03')) {
        switchMatch(dateVal);
        if (display) {
          display.innerHTML = `
            <span class="match-badge active-match" style="background:rgba(0,75,155,0.25);border-color:#004B9B;">
              <i class="dot-live" style="background:#004B9B;"></i> <b id="matchDateText">2024년 11월 3일 (${dayName})</b> 16:00
            </span>
            <span class="match-venue" id="matchVenueText">화성종합실내체육관 · 정규리그 (IBK기업은행 3:0 완승)</span>
          `;
        }
        setCaster('📅 경기 날짜 선택', ['#2024-11-03', '#IBK기업은행', '#현대건설'],
          '11월 3일 [IBK기업은행 vs 현대건설] 전술 분석 데이터가 선택되었습니다. 빅토리아 21득점(공격 18) 폭격과 최정민 17득점(블로킹 3), 이소영 BEST 플레이어 1위 선정 및 3:0 셧아웃 완승을 분석할 수 있습니다.',
          new Set(), false);
      } else if (dateVal.includes('11-04')) {
        switchMatch(dateVal);
        if (display) {
          display.innerHTML = `
            <span class="match-badge active-match" style="background:rgba(230,0,126,0.2);border-color:#E6007E;">
              <i class="dot-live" style="background:#E6007E;"></i> <b id="matchDateText">2024년 11월 4일 (${dayName})</b> 19:00
            </span>
            <span class="match-venue" id="matchVenueText">인천 삼산월드체육관 · 정규리그 (흥국생명 3:0 완승)</span>
          `;
        }
        setCaster('📅 경기 날짜 선택', ['#2024-11-04', '#흥국생명', '#정관장'],
          '11월 4일 [흥국생명 vs 정관장] 전술 분석 데이터가 선택되었습니다. 킨델란 22득점(블로킹 4) 대폭발과 자스티스 BEST 플레이어 1위, 종휘 24득점 분전을 분석할 수 있습니다.',
          new Set(), false);
      } else if (dateVal.includes('11-07')) {
        switchMatch(dateVal);
        if (display) {
          display.innerHTML = `
            <span class="match-badge active-match">
              <i class="dot-live"></i> <b id="matchDateText">2024년 11월 7일 (${dayName})</b> 16:00
            </span>
            <span class="match-venue" id="matchVenueText">대전 충무체육관 · 정규리그 (4세트 풀경기)</span>
          `;
        }
        setCaster('📅 경기 날짜 선택', ['#2024-11-07', '#정관장', '#현대건설'],
          '11월 7일 [정관장 vs 현대건설] 정규리그 전술 분석 데이터가 선택되었습니다. 4세트 풀경기 기록과 세트별 리플레이를 분석할 수 있습니다.',
          new Set(), false);
      } else {
        const formatted = `${dateVal} (${dayName}요일)`;
        if (display) {
          display.innerHTML = `
            <span class="match-badge">
              <b>${formatted}</b>
            </span>
            <span class="match-venue" style="color:var(--accent);">
              등록 경기 없음 · 
              <button type="button" class="btn btn-date-submit" style="padding:2px 7px;font-size:11px;" id="btnResetDate">
                11.04(화) 흥국생명전
              </button>
            </span>
          `;
          $('btnResetDate')?.addEventListener('click', () => {
            applyDate('2024-11-04');
          });
        }
        setCaster('📅 경기 안내', [`#${dateVal}`, `#${dayName}요일`],
          `선택하신 ${formatted}에는 등록된 경기 데이터가 없습니다. 상단의 11.03(기업은행전), 11.04(흥국생명전), 또는 11.07(현대건설전)을 선택해 주세요.`,
          new Set(), false);
      }
    };

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      applyDate(input.value);
    });
    input.addEventListener('change', () => {
      applyDate(input.value);
    });
    if (select) {
      select.addEventListener('change', () => {
        input.value = select.value;
        applyDate(select.value);
      });
    }

    const urlParams = new URLSearchParams(window.location.search);
    const initialDate = urlParams.get('date') || urlParams.get('matchDate') || input.value || '2024-11-04';
    applyDate(initialDate);
  }

  function bindPlayerSearch() {
    const input = $('playerSearchInput');
    const clearBtn = $('playerSearchClear');
    const chips = $('quickChips');
    if (!input) return;

    const performSearch = (q) => {
      S.searchQuery = q.trim();
      input.value = q;
      if (clearBtn) clearBtn.style.display = S.searchQuery ? 'block' : 'none';

      chips?.querySelectorAll('.q-chip').forEach((btn) => {
        const bq = btn.dataset.q;
        btn.classList.toggle('active', (bq && S.searchQuery.toLowerCase().includes(bq.toLowerCase())) || (!bq && !S.searchQuery));
      });

      renderList();
    };

    input.addEventListener('input', (e) => {
      performSearch(e.target.value);
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const firstItem = $('playerList').querySelector('.pl-item');
        if (firstItem) {
          selectPlayer(+firstItem.dataset.id);
          $('playerCard')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      } else if (e.key === 'Escape') {
        performSearch('');
        input.blur();
      }
    });

    clearBtn?.addEventListener('click', () => {
      performSearch('');
      input.focus();
    });

    chips?.querySelectorAll('.q-chip').forEach((btn) => {
      btn.addEventListener('click', () => {
        const q = btn.dataset.q;
        performSearch(q);
        if (q) {
          const allPlayers = Object.values(D.players);
          const found = allPlayers.find((p) => (p.name || '').includes(q));
          if (found) {
            selectPlayer(found.id);
          }
        }
      });
    });
  }

  function bind() {
    $('btnPlay').onclick = play;
    $('btnPause').onclick = pause;
    $('btnRotate').onclick = rotate;
    $('btnReset').onclick = reset;
    $('btnHome').onclick = swapHome;
    $('btnTheme').onclick = () => { S.theme = S.theme === 'dark' ? 'light' : 'dark'; applyTheme(); };
    $('speed').onchange = (e) => (S.speed = +e.target.value);
    $('autoFocus').onchange = (e) => (S.autoFocus = e.target.checked);
    document.querySelectorAll('.mode-tab').forEach((b) => b.addEventListener('click', () => setMode(b.dataset.mode)));
    bindMatchDate();
    bindPlayerSearch();
    document.addEventListener('keydown', (e) => {
      if (['SELECT', 'TEXTAREA', 'INPUT'].includes(e.target.tagName)) return;
      if (!$('reviewOverlay').hidden) return;
      if (e.code === 'Space') { e.preventDefault(); S.playing ? pause() : play(); }
      else if (e.key === 'r' || e.key === 'R') rotate();
      else if (e.key === 'Escape') reset();
      else if (/^[0-4]$/.test(e.key)) setView(+e.key);
      else if (e.key === 'ArrowRight') stepRally(1);
      else if (e.key === 'ArrowLeft') stepRally(-1);
    });
  }

  // ───────────────────────── 시작 ─────────────────────────
  window.VT = {
    ready,
    get D() { return D; }, get V() { return V; }, get RAW() { return RAW; },
    esc, color: (t) => color(t), short: (t) => short(t), other: (t) => other(t),
    analyze, compare, fmtD, METRICS, setView,
  };

  async function init() {
    const urlParams = new URLSearchParams(window.location.search);
    const dateParam = urlParams.get('date') || urlParams.get('matchDate');
    if (dateParam) {
      S.matchDate = dateParam;
    } else if (!S.matchDate || S.matchDate === '2026-11-07') {
      S.matchDate = '2024-11-04';
    }
    let raw;
    try {
      raw = await loadData();
    } catch (e) {
      $('casterText').textContent = '데이터를 불러오지 못했습니다. python server.py 로 실행하거나 python db/seed.py 로 data.js 를 생성하세요.';
      return;
    }
    indexData(raw);
    S.home = D.teamIds.find((t) => D.teams[t].is_home) || D.teamIds[0];
    S.panelTeam = S.home;
    D.teamIds.forEach((t) => { S.rot[t] = [...BASE_ROT]; S.rotCount[t] = 0; });
    applyTheme(); drawFloor(); buildTokens();
    S.pos = baseFormation();
    renderSetBar(); renderHeadline(); renderScoreboard(); renderMatchStats(); renderTabs(); renderList();
    selectPlayer(D.lineups[S.home].OH1, { silent: true });
    renderScenarios(); renderModeUI(); renderTimeline(); updateControls(); introCaster(); bind();
    renderCourt();
    requestAnimationFrame(tick);
    resolveReady(window.VT);
  }
  init();
})();
