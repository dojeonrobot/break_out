let ADM_FILTER = 'all';                       // 제출 기록 필터: all | need | <조 번호> (2026-11-10)
const ADM_OPEN = new Set(['notice']);         // 오른쪽 접이식 칸 중 펼친 것. 15초마다 다시 그려도 유지
function adminHTML(){
  const isDone = s => inMap.has(s.scanId) || subDone(s);
  const stOf = s => isDone(s) ? ['ok', '복구됨'] : s.splat ? ['wait', '확인 대기'] : s.error ? ['err', '변환 실패'] : ['run', '변환 중'];
  const subRow = s=>{ const m = missionById(s.mission), done = isDone(s), [k, txt] = stOf(s), memo = [s.caption, s.note].filter(Boolean).join(' · ');
    return `<tr class="${k}"><td><b>${s.team || '-'}조</b></td><td><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(m ? m.name : s.mission)}</a></td><td class="memo" title="${esc(memo)}">${esc(memo)}</td><td class="t">${timeText(s.createdAt)}</td><td><span class="sst ${k}">${txt}</span>${s.error && !done ? `<small>${esc(s.error)}</small>` : ''}</td><td class="act">${done ? `<button type="button" class="mini" data-approve="${esc(s.id)}" data-ok="0">되돌리기</button>` : s.splat ? `<button type="button" class="mini on" data-approve="${esc(s.id)}">복구 확정</button>` : ''}${s.error || (!s.splat && Date.now()-s.createdAt > 240000) ? `<button type="button" class="mini" data-reconv="${esc(s.id)}">다시 변환</button>` : ''}<button type="button" class="mini" data-adel="${esc(s.id)}">삭제</button></td></tr>`; };
  const n = SUBS.length, wait = SUBS.filter(s=> s.splat && !isDone(s)).length, errs = SUBS.filter(s=> s.error && !isDone(s)).length;
  let rows = []; try{ rows = flowRows(PAIRS()); }catch(e){}
  const teams = [...new Set([...SUBS.map(s=> s.team || 0), ...Object.keys(SQUESTS).map(Number)])].filter(Boolean).sort((a,b)=> a-b);
  const full = teams.filter(t=> teamZones(t, rows).every(z=> z.st === 'ok')).length;
  const QS_ = typeof QUESTS === 'object' ? QUESTS : [], qShort = id => { const q = QS_.find(x=> x.id === id); return q ? q.short : id; }, qNo = id => QS_.findIndex(x=> x.id === id) + 1;
  // 조별 진행: 조마다 한 줄. 태블릿은 조 칸 안의 알약(막 · 빼기), 섬 미션은 태블릿별 토글 (2026-11-10: 태블릿마다 한 줄이던 표가 6조면 12줄이라 줄임)
  const head = rows.map(r=> r.quest ? `<th><em>섬 · 미션 ${qNo(r.quest.quest)}</em>${esc(qShort(r.quest.quest))}</th>` : `<th><em>캠퍼스</em>${esc(r.campus.name)}</th>`).join('');
  const teamRow = t=>{ const zs = teamZones(t, rows), ok = zs.filter(z=> z.st === 'ok').length, ls = teamDevs(t), sq = SQUESTS[t] || {};
    const tabs = ls.length ? ls.map(l=>{ const d = sq[l] || {}; return `<span class="tab"><b title="${esc(l)}">${esc(l)}</b>${d.tut ? (d.act ? `<em>${d.act}막</em>` : '') : '<em>튜토리얼 전</em>'}<button type="button" data-aq="${t}:${l}:*:0" title="이 태블릿을 조에서 뺍니다" aria-label="${t}조 태블릿 ${esc(l)} 빼기">×</button></span>`; }).join('') : '<small class="none">태블릿 없음</small>';
    const cells = zs.map(z=> z.p.quest ? `<td class="qcell">${ls.length ? ls.map(l=>{ const on = devQuests(t, l).includes(z.p.quest.quest); return `<button type="button" class="qc ${on ? 'on' : ''}" data-aq="${t}:${l}:${z.p.quest.quest}:${on ? 0 : 1}" title="${on ? `${esc(l)} 완료를 되돌립니다` : `${esc(l)}를 완료로 처리합니다`}">${esc(l)}${on ? ' ✓' : ''}</button>`; }).join('') : '<span class="none">-</span>'}</td>` : `<td><span class="st ${z.st}">${z.st === 'ok' ? '복구됨' : z.st === 'pend' ? '처리 중' : '미제출'}</span></td>`).join('');
    return `<tr class="${ok === rows.length ? 'full' : ''}"><td class="tc"><b>${t}조</b><div class="tabs">${tabs}</div></td>${cells}<td><div class="rate"><i style="width:${ok*20}%"></i><span>${ok*20}%</span></div></td><td class="act"><button type="button" class="mini" data-aq="${t}:*:*:0" ${ls.length ? '' : 'hidden'}>조 초기화</button></td></tr>`; };
  const table = rows.length ? `<div class="tw"><table class="qt big v2"><thead><tr><th>조</th>${head}<th>복구율</th><th></th></tr></thead><tbody>${teams.length ? teams.map(teamRow).join('') : `<tr><td colspan="${rows.length + 3}" class="empty">아직 조를 고른 태블릿이 없습니다</td></tr>`}</tbody></table></div>` : '';
  // 제출 기록: 조별 묶음 대신 한 표(최근 것 위), 조·처리 필요 필터
  const need = s=> !isDone(s) && (s.splat || s.error);
  const list = SUBS.filter(s=> ADM_FILTER === 'all' ? true : ADM_FILTER === 'need' ? need(s) : (s.team || 0) === +ADM_FILTER).slice().sort((a,b)=> b.createdAt - a.createdAt);
  const chip = (k, label, cnt)=> `<button type="button" class="chip ${String(ADM_FILTER) === String(k) ? 'on' : ''}" data-afilt="${k}">${label}<i>${cnt}</i></button>`;
  const chips = n ? chip('all', '전체', n) + chip('need', '처리 필요', wait + errs) + teams.map(t=> chip(t, `${t}조`, SUBS.filter(s=> (s.team || 0) === t).length)).join('') : '';
  // 오른쪽: 접이식 네 칸. 공지만 기본으로 펼침
  const det = (k, title, sub, body)=> `<details class="card" data-ad="${k}" ${ADM_OPEN.has(k) ? 'open' : ''}><summary><h3>${title}</h3>${sub ? `<span>${sub}</span>` : ''}</summary><div class="db">${body}</div></details>`;
  const changed = MISSIONS.filter(m=> COORD_DEF[m.id] && COORDS[m.id]).length;
  return `<div class="adm dash v2">
    <div class="tb">
      <label class="autol">화면 기준 <select data-aview><option value="0" ${VIEW_ADMIN ? '' : 'selected'}>모든 조</option>${Array.from({length:12}, (_,i)=> `<option value="${i+1}" ${VIEW_ADMIN === i+1 ? 'selected' : ''}>${i+1}조 화면</option>`).join('')}</select></label>
      <label class="autol"><input type="checkbox" id="autoChk" data-aact="auto" ${AUTO ? 'checked' : ''}> 제출되면 자동으로 복구 처리 <small>끄면 제출마다 「복구 확정」을 누릅니다</small></label>
      <span class="sum">${teams.length ? `${teams.length}조 참여` : '참여 조 없음'}${full ? ` · 복구 완료 ${full}조` : ''}</span>
    </div>
    <div class="cols">
      <div class="main">
        <section class="card"><div class="ch"><h3>조별 진행</h3><span class="sum">캠퍼스는 제출 상태, 섬 미션은 태블릿별로 완료 표시</span></div>${table}</section>
        <section class="card"><div class="ch"><h3>제출 기록</h3><span class="sum">${n ? `${n}건${wait ? ` · 확인 대기 ${wait}` : ''}${errs ? ` · 변환 실패 ${errs}` : ''}` : ''}</span>${n ? '<button type="button" class="mini" data-aact="copy">표로 복사</button>' : ''}</div>
          ${chips ? `<div class="chips">${chips}</div>` : ''}
          ${list.length ? `<div class="tw"><table class="sbt"><thead><tr><th>조</th><th>기록</th><th>메모</th><th>제출 시각</th><th>상태</th><th></th></tr></thead><tbody>${list.map(subRow).join('')}</tbody></table></div>` : `<p class="empty">${n ? '이 조건에 맞는 제출이 없습니다' : '아직 제출이 없습니다'}</p>`}</section>
      </div>
      <aside class="side">
        ${det('notice', '전체 공지', NOTICE ? '공지 중' : '', `<p class="hint">모든 태블릿에 보이드 말풍선으로 뜹니다. 15초 안에 도착합니다.</p>
          ${NOTICE ? `<p class="nnow">지금 공지: <b>${esc(NOTICE.text)}</b> <button type="button" class="mini" data-aact="noticeClear">내리기</button></p>` : ''}
          <div class="arow col">${NOTICE_PRESETS.map(t=> `<button type="button" class="mini" data-npre="${esc(t)}">${esc(t)}</button>`).join('')}</div>
          <div class="nrow"><input id="noticeIn" type="text" maxlength="120" placeholder="직접 쓰기" autocomplete="off" aria-label="공지 내용"><button type="button" class="mini on" data-aact="noticeSend">보내기</button></div>`)}
        ${det('coords', '기록 좌표', changed ? `${changed}곳 바꿈` : '기본값', `<p class="hint">조 태블릿의 좌표 카드와 지도 링크가 바뀝니다. 3D 화면의 구역 위치는 그대로입니다.</p>
          ${MISSIONS.filter(m=> COORD_DEF[m.id]).map(m=>{ const d = COORD_DEF[m.id], ch = !!COORDS[m.id]; return `<div class="crow">
            <div class="cn"><b>${esc(m.name)}</b>${ch ? `<button type="button" class="mini" data-cdef="${esc(m.id)}">기본값으로</button>` : ''}</div>
            <div class="cin"><label><small>위도</small><input type="text" inputmode="decimal" autocomplete="off" data-keep="clat-${esc(m.id)}" value="${m.lat.toFixed(6)}" aria-label="${esc(m.name)} 위도"></label>
              <label><small>경도</small><input type="text" inputmode="decimal" autocomplete="off" data-keep="clng-${esc(m.id)}" value="${m.lng.toFixed(6)}" aria-label="${esc(m.name)} 경도"></label>
              <button type="button" class="mini on" data-csave="${esc(m.id)}">저장</button></div>
            ${ch ? `<small class="cdef">기본값 ${d.lat.toFixed(6)}, ${d.lng.toFixed(6)}</small>` : ''}</div>`; }).join('')}`)}
        ${det('demo', '복구 미리보기', DEMO.size ? `${DEMO.size}곳 켬` : '', `<p class="hint">이 기기 화면에서만 복구된 모습을 미리 봅니다. 「모든 조」 화면에서만 보입니다.</p>
          ${MISSIONS.map(m=>{ const tw = missionById(m.twin), id = m.twin || m.id; return `<label class="autol"><input type="checkbox" data-demo="${esc(id)}" ${DEMO.has(id) ? 'checked' : ''}> ${esc(tw ? tw.name : m.name)} <small>↔ ${esc(m.name)}</small></label>`; }).join('')}
          ${(typeof MI !== 'undefined' ? MI.filter(m=> m.quest) : []).map(m=> `<label class="autol"><input type="checkbox" data-demo="${esc(m.id)}" ${DEMO.has(m.id) ? 'checked' : ''}> ${esc(m.name)} <small>섬 미션</small></label>`).join('')}
          <div class="arow"><button type="button" class="mini" data-aact="demoAll">전부 켜기</button><button type="button" class="mini" data-aact="demoNone">전부 끄기</button></div>`)}
        ${det('tools', '도구', HIDDEN.size ? `숨긴 스캔 ${HIDDEN.size}` : '', `<div class="arow col">
          <button type="button" class="mini" data-aact="copy">제출 목록 표로 복사</button>
          <button type="button" class="mini" data-aact="unhide" ${HIDDEN.size ? '' : 'hidden'}>숨긴 스캔 ${HIDDEN.size}건 되살리기</button>
          <button type="button" class="mini danger" data-aact="reset">전체 초기화</button></div>`)}
      </aside>
    </div>
  </div>`;
}
document.addEventListener('toggle', e=>{ const d = e.target; if(!d || d.tagName !== 'DETAILS' || !d.dataset.ad) return; if(d.open) ADM_OPEN.add(d.dataset.ad); else ADM_OPEN.delete(d.dataset.ad); }, true);
