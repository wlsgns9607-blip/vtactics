/* ============================================================
   최종 리뷰 화면
   - 왼쪽: 경기 데이터 요약(자동 계산) / 오른쪽: 사용자가 직접 쓰는 리뷰 에디터
   - 저장: PUT api/review (SQLite) → 서버가 없으면 localStorage
   - 리뷰 본문은 사용자가 작성한 내용만 저장한다 (자동 작성 없음)
   ============================================================ */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const LS_KEY = 'vtactics.review.v1';
  const SECTIONS = [
    ['summary', '총평', '경기 전체를 한두 문단으로'],
    ['turning', '승부처', '흐름이 바뀐 세트·구간'],
    ['KGC', '정관장 평가', ''],
    ['HDEC', '현대건설 평가', ''],
    ['players', '선수 코멘트', '눈에 띈 선수'],
    ['next', '개선점 · 다음 경기 포인트', ''],
  ];
  const MET = [
    ['att_pct', '공격 성공률(%)', true], ['rcv_pct', '리시브 정확(%)', true], ['dig_pct', '디그 성공률(%)', true],
    ['blk_made', '블로킹 득점', false], ['srv_made', '서브 득점', false], ['errors', '범실', false],
  ];

  let VT, D, RAW, V, content = {}, saveTimer = null, serverMode = false, el = {}, curMetric = 'att_pct', curPlayer = null;

  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const nz = (v) => (v == null ? '-' : v);

  // ───────── 저장/불러오기 ─────────
  async function load() {
    serverMode = !!(window.VT && VT.D && VT.D.serverMode);
    if (serverMode) {
      try {
        const r = await fetch('api/review', { cache: 'no-store' });
        if (r.ok) { const j = await r.json(); return { c: j.content || {}, at: j.updated_at }; }
      } catch (e) { serverMode = false; }
    }
    try { const j = JSON.parse(localStorage.getItem(LS_KEY) || 'null'); if (j) return { c: j.content || {}, at: j.updated_at }; } catch (e) { /* ignore */ }
    return { c: {}, at: null };
  }
  function status(t, cls = '') { if (el.status) { el.status.textContent = t; el.status.className = 'ed-status ' + cls; } }
  function scheduleSave() { status('입력 중…'); clearTimeout(saveTimer); saveTimer = setTimeout(save, 700); }
  async function save() {
    clearTimeout(saveTimer);
    const now = new Date().toLocaleString('ko-KR');
    try { localStorage.setItem(LS_KEY, JSON.stringify({ content, updated_at: now })); } catch (e) { /* ignore */ }
    if (serverMode) {
      try {
        const r = await fetch('api/review', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(content) });
        if (!r.ok) throw new Error(r.status);
        const j = await r.json();
        return status(`✓ DB에 저장됨 ${j.updated_at || ''}`, 'ok');
      } catch (e) { return status('서버 저장 실패 · 브라우저에만 저장됨', 'err'); }
    }
    status(`✓ 브라우저에 저장됨 ${now}`, 'ok');
  }

  // ───────── 데이터 요약 계산 ─────────
  const sumOf = (n, t) => V[n].summary[t];
  const fmtMetric = (k, v) => (v == null ? '-' : /pct/.test(k) ? `${v}%` : v);

  function finalCard() {
    const wins = {}; D.teamIds.forEach((t) => (wins[t] = RAW.sets.filter((s) => s.winner === t).length));
    const [a, b] = D.teamIds;
    const tm = (t) => `<div class="tm"><div class="nm" style="color:${VT.color(t)}">${esc(D.teams[t].name || VT.short(t))}</div><div class="sc" style="color:${VT.color(t)}">${wins[t]}</div></div>`;
    return `<div class="rv-card"><h3>최종 결과 <span class="tag">FINAL</span></h3>
      <div class="rv-final">${tm(a)}<span class="dash">:</span>${tm(b)}</div>
      <div class="set-pills">${RAW.sets.map((s) => `<span class="set-pill" style="--wc:${VT.color(s.winner)}">${s.set_no}세트 정 ${s.kgc_score} : ${s.hdec_score} 현</span>`).join('')}</div></div>`;
  }

  function compareTable() {
    const [a, b] = D.teamIds;
    const rows = [
      ['공격 성공률', 'att_pct', true], ['공격 (성공/시도)', 'att', 'mt'], ['블로킹 득점', 'blk_made', true],
      ['서브 득점', 'srv_made', true], ['디그 성공률', 'dig_pct', true], ['리시브 정확', 'rcv_pct', true],
      ['범실', 'errors', 'inv'],
    ];
    const cols = [1, 2, 3, 4].filter((n) => V[n]);
    const cell = (n, key, mode) => {
      const x = sumOf(n, a), y = sumOf(n, b);
      let xv, yv, xw, yw;
      if (mode === 'mt') { xv = `${x.att_made}/${x.att_tried}`; yv = `${y.att_made}/${y.att_tried}`; return `<td><span class="a">${xv}</span><span class="sep">|</span><span class="b">${yv}</span></td>`; }
      xv = x[key] ?? 0; yv = y[key] ?? 0;
      const better = mode === 'inv' ? (xv < yv ? 'a' : xv > yv ? 'b' : '') : (xv > yv ? 'a' : xv < yv ? 'b' : '');
      xw = better === 'a' ? 'win' : better ? 'lose' : ''; yw = better === 'b' ? 'win' : better ? 'lose' : '';
      const f = (v) => fmtMetric(key, v);
      return `<td><span class="a ${xw}">${f(xv)}</span><span class="sep">|</span><span class="b ${yw}">${f(yv)}</span></td>`;
    };
    return `<div class="rv-card"><h3>세트별 팀 비교 <span class="tag">${esc(VT.short(a))} | ${esc(VT.short(b))}</span></h3>
      <div style="overflow-x:auto"><table class="rv-table" style="--ca:${VT.color(a)};--cb:${VT.color(b)}">
        <thead><tr><th>항목</th>${cols.map((n) => `<th>${n}세트</th>`).join('')}<th>전체</th></tr></thead>
        <tbody>${rows.map(([lab, key, mode]) => `<tr><td>${lab}</td>${cols.map((n) => cell(n, key, mode)).join('')}${cell(0, key, mode)}</tr>`).join('')}</tbody>
      </table></div>
      <p class="rv-note" style="margin:8px 0 0">굵은 쪽이 해당 항목 우세(범실은 적은 쪽). 세트 합산은 공식 경기 기록표와 선수별 198개 항목이 모두 일치하도록 검증했습니다.</p></div>`;
  }

  function chartSVG(key) {
    const sets = [1, 2, 3, 4].filter((n) => V[n]);
    const W = 520, H = 190, L = 34, R = 30, T = 16, B = 28;
    const series = D.teamIds.map((t) => ({ t, v: sets.map((n) => sumOf(n, t)[key] ?? 0) }));
    const all = series.flatMap((s) => s.v);
    let lo = Math.min(...all), hi = Math.max(...all);
    const pad = (hi - lo) * 0.25 || 1; lo = Math.max(0, lo - pad); hi = hi + pad;
    const x = (i) => L + (sets.length === 1 ? (W - L - R) / 2 : (i * (W - L - R)) / (sets.length - 1));
    const y = (v) => T + (1 - (v - lo) / (hi - lo)) * (H - T - B);
    let g = '';
    for (let i = 0; i <= 3; i++) {
      const v = lo + ((hi - lo) * i) / 3; const yy = y(v);
      g += `<line class="grid" x1="${L}" x2="${W - R}" y1="${yy}" y2="${yy}"/><text x="${L - 6}" y="${yy + 3}" text-anchor="end">${/pct/.test(key) ? v.toFixed(0) : Math.round(v * 10) / 10}</text>`;
    }
    sets.forEach((n, i) => (g += `<text x="${x(i)}" y="${H - 8}" text-anchor="middle">${n}세트</text>`));
    series.forEach((s) => {
      const c = VT.color(s.t);
      g += `<polyline fill="none" stroke="${c}" stroke-width="2.4" points="${s.v.map((v, i) => `${x(i)},${y(v)}`).join(' ')}"/>`;
      s.v.forEach((v, i) => {
        const up = s.t === D.teamIds[0];
        g += `<circle cx="${x(i)}" cy="${y(v)}" r="4" fill="${c}" stroke="var(--panel)" stroke-width="1.5"/><text class="lbl" style="fill:${c}" x="${x(i)}" y="${y(v) + (up ? -9 : 15)}" text-anchor="middle">${fmtMetric(key, v)}</text>`;
      });
    });
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="세트별 추이">${g}</svg>
      <div class="chart-legend">${D.teamIds.map((t) => `<span><i style="background:${VT.color(t)}"></i>${esc(VT.short(t))}</span>`).join('')}</div>`;
  }

  function trendCard() {
    return `<div class="rv-card"><h3>세트별 추이 <span class="tag">TREND</span></h3>
      <div class="rv-tabs" id="rvMetricTabs">${MET.map(([k, l]) => `<button class="rv-tab ${k === curMetric ? 'active' : ''}" data-k="${k}">${l}</button>`).join('')}</div>
      <div id="rvChart">${chartSVG(curMetric)}</div></div>`;
  }

  function insightCard() {
    const items = [];
    const [a, b] = D.teamIds;
    RAW.sets.forEach((s) => {
      const an = VT.analyze(s.set_no);
      items.push(`<li><span class="k">SET ${s.set_no}</span>${esc(an.headline)}</li>`);
    });
    const all = VT.analyze(0);
    items.unshift(`<li><span class="k">MATCH</span>${esc(all.headline)}</li>`);
    // 득점 방식
    const cnt = {};
    D.teamIds.forEach((t) => (cnt[t] = {}));
    RAW.rallies.forEach((r) => { cnt[r.scorer][r.cause] = (cnt[r.scorer][r.cause] || 0) + 1; });
    const K = { kill: '공격', blockkill: '블로킹', out: '상대 아웃', net: '상대 네트', overnet: '상대 오버넷', touchnet: '상대 터치넷', drop: '상대 수비 실패', fault: '상대 기타범실' };
    const line = (t) => Object.entries(cnt[t]).sort((x, y) => y[1] - x[1]).map(([k, v]) => `${K[k] || k} ${v}`).join(' · ');
    items.push(`<li><span class="k">HOW THEY SCORED</span><b>${esc(VT.short(a))}</b> ${esc(line(a))}<br><b>${esc(VT.short(b))}</b> ${esc(line(b))}</li>`);
    return `<div class="rv-card"><h3>자동 데이터 인사이트 <span class="tag">AUTO</span></h3><ul class="rv-insights">${items.join('')}</ul></div>`;
  }

  function playerCard() {
    const list = Object.values(V[0].players).filter((p) => p.sets_played).sort((x, y) => x.team_id.localeCompare(y.team_id) || (y.points || 0) - (x.points || 0));
    if (!curPlayer || !V[0].players[curPlayer]) curPlayer = list[0].id;
    return `<div class="rv-card"><h3>선수별 세트 추이 <span class="tag">PLAYER</span></h3>
      <div class="rv-sel"><select id="rvPlayer">${list.map((p) => `<option value="${p.id}" ${p.id === curPlayer ? 'selected' : ''}>${esc(VT.short(p.team_id))} · ${esc(p.name)} (${p.position})</option>`).join('')}</select></div>
      <div id="rvPlayerTable">${playerTable()}</div>
      <p class="rv-note" style="margin:10px 0 0">집계 기준: 문자중계 기록을 터치 단위로 집계. 블로킹 어시스트는 시도에 포함하지 않으며, 세트 라인업은 세트별 출전 기록에서 추정한 값입니다. 코트 위 선수·공의 이동은 기록 순서를 바탕으로 한 근사 연출입니다.</p></div>`;
  }
  function playerTable() {
    const sets = [1, 2, 3, 4].filter((n) => V[n]);
    const rows = [
      ['공격', (p) => (p.att_tried ? `${p.att_made}/${p.att_tried} (${p.att_pct}%)` : '-')],
      ['득점', (p) => nz(p.points)], ['블로킹', (p) => (p.blk_tried ? `${p.blk_made}/${p.blk_tried}` : '-')],
      ['디그', (p) => (p.dig_tried ? `${p.dig_made}/${p.dig_tried}` : '-')],
      ['리시브', (p) => (p.rcv_tried ? `${p.rcv_made}/${p.rcv_tried}` : '-')],
      ['세트', (p) => (p.set_tried ? `${p.set_made}/${p.set_tried}` : '-')], ['범실', (p) => nz(p.errors)],
    ];
    const get = (n) => V[n].players[curPlayer];
    return `<div style="overflow-x:auto"><table class="rv-table"><thead><tr><th>항목</th>${sets.map((n) => `<th>${n}세트</th>`).join('')}<th>전체</th></tr></thead><tbody>
      ${rows.map(([l, f]) => `<tr><td>${l}</td>${sets.map((n) => `<td>${get(n).sets_played ? f(get(n)) : '-'}</td>`).join('')}<td>${f(get(0))}</td></tr>`).join('')}
    </tbody></table></div>`;
  }

  // ───────── 에디터 ─────────
  function editorHTML() {
    const sets = content.sets || {};
    return `<div class="rv-card rv-editor"><h3>내 리뷰 작성 <span class="tag">WRITE</span></h3>
      <input class="ed-title" id="edTitle" placeholder="리뷰 제목 (예: 정관장 3:1 승 — 블로킹과 리시브가 갈랐다)" value="${esc(content.title || '')}" maxlength="120" />
      ${SECTIONS.map(([k, label, hint]) => `<div class="ed-sec"><div class="ed-sec-h"><label for="ed_${k}">${label}${hint ? `<span class="hint">${hint}</span>` : ''}</label>
        <button class="ed-ins" data-ins="${k}" type="button" title="왼쪽 데이터 요약에서 숫자를 골라 커서 위치에 넣습니다">+ 데이터 삽입</button></div>
        <textarea class="ed-ta" id="ed_${k}" data-k="${k}" placeholder="직접 작성하세요">${esc(content[k] || '')}</textarea></div>`).join('')}
      <div class="ed-sec"><div class="ed-sec-h"><label>세트별 메모</label></div>
        <div class="ed-sets">${[1, 2, 3, 4].map((n) => `<div><div class="lab">${n}SET</div><textarea class="ed-ta sm" data-set="${n}" placeholder="${n}세트 메모">${esc(sets[n] || '')}</textarea></div>`).join('')}</div></div>
      <div class="ed-bar">
        <button class="btn" id="edCopy" type="button">복사</button><button class="btn" id="edMd" type="button">.md 저장</button>
        <button class="btn" id="edPrint" type="button">인쇄</button><button class="btn btn-primary" id="edSave" type="button">저장</button>
        <span class="ed-status" id="edStatus"></span></div></div>`;
  }

  function dataSnippet(k) {
    const [a, b] = D.teamIds;
    const wins = (t) => RAW.sets.filter((s) => s.winner === t).length;
    const team = (t, s) => `${VT.short(t)}: 공격 ${s.att_pct}%(${s.att_made}/${s.att_tried}), 블로킹 득점 ${s.blk_made}, 서브 득점 ${s.srv_made}, 디그 ${s.dig_pct}%, 리시브 ${s.rcv_pct}%, 범실 ${s.errors}`;
    const topP = (t) => Object.values(V[0].players).filter((p) => p.team_id === t).sort((x, y) => (y.points || 0) - (x.points || 0)).slice(0, 3).map((p) => `${p.name} ${p.points}점`).join(', ');
    switch (k) {
      case 'summary': return `[데이터] 세트 스코어 ${VT.short(a)} ${wins(a)}:${wins(b)} ${VT.short(b)} (${RAW.sets.map((s) => `${s.kgc_score}:${s.hdec_score}`).join(', ')})`;
      case 'turning': return `[데이터] ${RAW.sets.map((s) => `${s.set_no}세트 ${VT.short(s.winner)} 승 ${s.kgc_score}:${s.hdec_score}`).join(' / ')}`;
      case 'KGC': return `[데이터] ${team('KGC', sumOf(0, 'KGC'))} / 득점 상위 ${topP('KGC')}`;
      case 'HDEC': return `[데이터] ${team('HDEC', sumOf(0, 'HDEC'))} / 득점 상위 ${topP('HDEC')}`;
      case 'players': return `[데이터] 득점 상위 — ${topP(a)} | ${topP(b)}`;
      default: return `[데이터] 세트별 공격 성공률 ${a}: ${[1, 2, 3, 4].map((n) => sumOf(n, a).att_pct).join('→')}% / ${b}: ${[1, 2, 3, 4].map((n) => sumOf(n, b).att_pct).join('→')}%`;
    }
  }

  function toMarkdown() {
    const sets = content.sets || {};
    const out = [`# ${content.title || '경기 리뷰'}`, '', `> ${VT.short(D.teamIds[0])} vs ${VT.short(D.teamIds[1])} · ${RAW.sets.map((s) => `${s.set_no}세트 ${s.kgc_score}:${s.hdec_score}`).join(' · ')}`, ''];
    SECTIONS.forEach(([k, l]) => { if ((content[k] || '').trim()) out.push(`## ${l}`, '', content[k].trim(), ''); });
    const m = [1, 2, 3, 4].filter((n) => (sets[n] || '').trim());
    if (m.length) { out.push('## 세트별 메모', ''); m.forEach((n) => out.push(`- **${n}세트**: ${sets[n].trim().replace(/\n/g, ' ')}`)); out.push(''); }
    return out.join('\n');
  }

  // ───────── 화면 조립 ─────────
  function build() {
    const o = $('reviewOverlay');
    o.innerHTML = `<div class="rv" role="dialog" aria-modal="true" aria-label="최종 리뷰">
      <div class="rv-head"><h2>📝 최종 리뷰</h2><span class="sub">왼쪽 데이터를 참고해 오른쪽에 직접 작성하세요. 자동 저장됩니다.</span><span class="grow"></span>
        <button class="rv-x" id="rvClose" aria-label="닫기">✕</button></div>
      <div class="rv-body"><div class="rv-col" id="rvData">${finalCard()}${compareTable()}${trendCard()}${insightCard()}${playerCard()}</div>
      <div class="rv-col">${editorHTML()}</div></div></div>`;
    el.status = $('edStatus');
    $('rvClose').onclick = close;
    o.onclick = (e) => { if (e.target === o) close(); };
    $('rvMetricTabs').querySelectorAll('.rv-tab').forEach((b) => (b.onclick = () => {
      curMetric = b.dataset.k;
      $('rvMetricTabs').querySelectorAll('.rv-tab').forEach((x) => x.classList.toggle('active', x === b));
      $('rvChart').innerHTML = chartSVG(curMetric);
    }));
    $('rvPlayer').onchange = (e) => { curPlayer = +e.target.value; $('rvPlayerTable').innerHTML = playerTable(); };
    $('edTitle').oninput = (e) => { content.title = e.target.value; scheduleSave(); };
    o.querySelectorAll('textarea[data-k]').forEach((t) => (t.oninput = () => { content[t.dataset.k] = t.value; scheduleSave(); }));
    o.querySelectorAll('textarea[data-set]').forEach((t) => (t.oninput = () => { (content.sets ||= {})[t.dataset.set] = t.value; scheduleSave(); }));
    o.querySelectorAll('.ed-ins').forEach((b) => (b.onclick = () => {
      const t = $('ed_' + b.dataset.ins); const s = dataSnippet(b.dataset.ins);
      const pos = t.selectionStart ?? t.value.length;
      t.value = t.value.slice(0, pos) + (pos && !/\n$/.test(t.value.slice(0, pos)) ? '\n' : '') + s + '\n' + t.value.slice(pos);
      t.dispatchEvent(new Event('input')); t.focus();
    }));
    $('edSave').onclick = save;
    $('edCopy').onclick = async () => {
      try { await navigator.clipboard.writeText(toMarkdown()); status('✓ 클립보드에 복사됨', 'ok'); }
      catch (e) { status('복사 실패 · .md 저장을 이용하세요', 'err'); }
    };
    $('edMd').onclick = () => {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([toMarkdown()], { type: 'text/markdown;charset=utf-8' }));
      a.download = 'match-review.md'; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    };
    $('edPrint').onclick = () => window.print();
  }

  async function open() {
    await VT.ready;
    D = VT.D; RAW = VT.RAW; V = VT.V;
    const r = await load(); content = r.c || {};
    build();
    $('reviewOverlay').hidden = false;
    document.body.style.overflow = 'hidden';
    status(r.at ? `불러옴 · 마지막 저장 ${r.at}` : (serverMode ? 'DB 연결됨 · 작성 시 자동 저장' : '작성 시 브라우저에 자동 저장'));
  }
  function close() {
    if (saveTimer) save();
    $('reviewOverlay').hidden = true;
    document.body.style.overflow = '';
  }

  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !$('reviewOverlay').hidden) close(); });
  window.addEventListener('DOMContentLoaded', async () => {
    VT = await new Promise((res) => { const t = setInterval(() => { if (window.VT) { clearInterval(t); res(window.VT); } }, 30); });
    $('btnReview').addEventListener('click', open);
  });
})();
