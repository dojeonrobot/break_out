# 2026-11-09 운영자 탭 정리 (사용자): 예제 숨기기/보이기 구역·「조 게시물 전부 삭제」 삭제, 게시물은 하나씩 삭제만, 맨 아래 「전부 초기화」(확인 창, 문구 입력 없음).
import io, sys
PP = r'C:\Users\dlgus\break_out\chapter05\feed.html'
h = io.open(PP, encoding='utf-8', newline='').read(); crlf = '\r\n' in h; h = h.replace('\r\n', '\n')
if 'adSeedPosts' not in h:
    sys.exit('이미 적용됨')
B = [h]
def r(old, new, cnt=1):
    n = B[0].count(old)
    if n != cnt: sys.exit(f'{n}≠{cnt}: {old[:100]}')
    B[0] = B[0].replace(old, new)

r("""        <div class="ad-card"><h2><i data-lucide="users" class="icon"></i>조가 올린 게시물 <span id="adTeamCount" class="ad-b team">0</span><span class="small muted" style="font-weight:400">문제 있는 글은 숨기기 또는 삭제(사진까지 지움)</span>
            <button class="btn btn-ghost" id="adDelAllBtn" type="button" style="margin-left:auto;color:var(--fake)"><i data-lucide="trash-2" class="icon"></i>조 게시물 전부 삭제</button></h2>
          <div class="ad-posts" id="adPosts"></div></div>
        <details class="ad-card" style="padding:0">
          <summary style="padding:16px;cursor:pointer;font-weight:700;display:flex;gap:8px;align-items:center;list-style:none"><i data-lucide="database" class="icon"></i>예제 자료 <span id="adSeedCount" class="ad-b seed">0</span><span class="small muted" style="font-weight:400">기본 세트. 지울 수는 없고 숨기기만 됩니다.</span></summary>
          <div class="ad-posts" id="adSeedPosts" style="padding:0 16px 16px"></div></details>
        <div class="ad-card"><h2><i data-lucide="rotate-ccw" class="icon"></i>새 기수 시작</h2>
          <p class="small muted">조 게시물, 판별, AI 사용 횟수를 모두 지우고 예제 자료만 남깁니다. 되돌릴 수 없습니다.</p>
          <div class="opt-row"><input class="input" id="adResetTxt" placeholder="RESET 이라고 입력" style="max-width:220px" aria-label="초기화 확인 문구"><button class="btn btn-ghost" id="adResetBtn" type="button" style="color:var(--fake)">전부 초기화</button></div>
          <p class="err" id="adResetErr"></p></div>""",
"""        <div class="ad-card"><h2><i data-lucide="users" class="icon"></i>조가 올린 게시물 <span id="adTeamCount" class="ad-b team">0</span></h2>
          <div class="ad-posts" id="adPosts"></div></div>
        <div class="ad-card" style="display:flex;align-items:center;gap:14px;flex-wrap:wrap"><div style="flex:1;min-width:200px"><h2 style="margin:0"><i data-lucide="rotate-ccw" class="icon"></i>전부 초기화</h2><p class="small muted" style="margin:4px 0 0">조 게시물·판별·점수를 모두 지우고 1라운드 예시 보기로 돌아갑니다.</p></div>
          <button class="btn btn-ghost" id="adResetBtn" type="button" style="color:var(--fake);min-height:44px"><i data-lucide="trash-2" class="icon"></i>전부 초기화</button></div>""")
r("""  $('#adTeamCount').textContent = teamN; $('#adSeedCount').textContent = posts.length - teamN; $('#adDelAllBtn').disabled = !teamN;""",
  """  $('#adTeamCount').textContent = teamN;""")
r("""      <div style="display:grid;gap:6px"><button class="btn btn-ghost" data-adtoggle="${p.id}" data-hidden="${p.status === 'hidden'}">${p.status === 'hidden' ? '보이기' : '숨기기'}</button>${p.seed ? '' : `<button class="btn btn-ghost" data-addel="${p.id}" style="color:var(--fake)">삭제</button>`}</div></div>`; };""",
  """      <div><button class="btn btn-ghost" data-addel="${p.id}" style="color:var(--fake)">삭제</button></div></div>`; };""")
r("""  $('#adSeedPosts').innerHTML = posts.filter(p => p.seed).map(row).join('');\n""", "")
r("""    if (e.target.closest('#adDelAllBtn') && confirm('조가 올린 게시물을 전부 지울까요? 예제 자료와 진행 단계는 그대로 둡니다. 되돌릴 수 없습니다.')) {""",
  """    if (false) {""")
r("""$('#adResetBtn').onclick = async () => {
  try { await adApi('/admin/reset', { confirm: $('#adResetTxt').value.trim() }); $('#adResetTxt').value = ''; $('#adResetErr').textContent = ''; toast('초기화했습니다.'); } catch (e) { $('#adResetErr').textContent = e.message; }""",
  """$('#adResetBtn').onclick = async () => {
  if (!confirm('조 게시물, 판별, 점수를 모두 지우고 1라운드 예시 보기로 돌아갑니다. 되돌릴 수 없습니다. 초기화할까요?')) return;
  try { await adApi('/admin/reset', { confirm: 'RESET' }); toast('초기화했습니다.'); await refresh(); } catch (e) { toast(e.message); }""")
h = B[0]
io.open(PP, 'w', encoding='utf-8', newline='').write(h.replace('\n', '\r\n') if crlf else h); print('ok')
