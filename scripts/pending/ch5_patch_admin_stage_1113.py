# 2026-11-13 (사용자: 「관리자 모드에서 1조를 특정 시점으로 되돌려놓는 기능 넣어놔줘」)
#  관리자 표의 조마다 「시점 이동」 고르기 → 서버가 그 조의 기록·섬 미션·본 막을 그 시점으로 맞춘다(/api/void/admin/stage).
#  그 조 태블릿은 다음 상태 확인(15초 안)에 진행 기억을 지우고 새로 열린다(trev 도장).
#  서버 파일도 고치므로 배포 때 server/ch5_void_server.py를 따로 올리고 voidrecord를 다시 시작해야 한다.
import pathlib
R = pathlib.Path(__file__).resolve().parents[2]
# ---------------- server ----------------
SP = R / 'server/ch5_void_server.py'; t = SP.read_bytes().decode('utf-8'); crlf = '\r\n' in t; t = t.replace('\r\n', '\n')
def rs(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:70]); t = t.replace(old, new)
rs("'notice': DB.get('notice'), 'coords': DB.get('coords', {}), 'now': now_ms()}", "'notice': DB.get('notice'), 'coords': DB.get('coords', {}), 'trev': DB.get('trev', {}), 'now': now_ms()}")
rs("'/api/void/admin/skip': self.admin_skip,", "'/api/void/admin/skip': self.admin_skip, '/api/void/admin/stage': self.admin_stage,")
rs("    # 운영자: 자체 스캔을 복구됨으로 확정(ok=false면 다시 확인 대기로)\n",
   "    # 운영자: 한 조를 흐름의 특정 시점으로 맞춘다 (2026-11-13). zones = 복구된 캠퍼스 기록, done = 끝낸 섬 미션, act = 본 막.\n"
   "    # 그 조의 다른 제출은 지우고, 모자란 기록은 「운영자 건너뜀」으로 채우고, 조의 모든 태블릿 칸을 같은 진행으로 덮어쓴다.\n"
   "    # trev[조] 도장이 바뀌면 그 조 태블릿은 기기에 남은 진행을 지우고 새로 연다.\n"
   "    def admin_stage(self, b):\n"
   "        team = clean_team(b.get('team'))\n"
   "        if not team:\n"
   "            raise ValueError('조 번호가 없습니다.')\n"
   "        zones = [str(z) for z in (b.get('zones') or []) if MISSION_ID.match(str(z))][:5]\n"
   "        done = [str(x) for x in (b.get('done') or []) if QUEST_ID.match(str(x))]\n"
   "        try:\n"
   "            act = max(0, min(3, int(b.get('act') or 0)))\n"
   "        except (TypeError, ValueError):\n"
   "            act = 0\n"
   "        tut = b.get('tut', True) is not False\n"
   "        with lock:\n"
   "            now = now_ms()\n"
   "            DB['subs'] = [s for s in DB['subs'] if s['team'] != team or s['mission'] in zones]\n"
   "            for z in zones:\n"
   "                if not any(s['team'] == team and s['mission'] == z and is_done(s) for s in DB['subs']):\n"
   "                    sid = uuid.uuid4().hex[:12]\n"
   "                    DB['subs'].append({'id': sid, 'scanId': 'skip' + sid, 'kind': 'skip', 'url': '', 'mission': z, 'team': team,\n"
   "                                       'note': '', 'caption': '운영자 건너뜀', 'author': '', 'status': 'ok', 'createdAt': now,\n"
   "                                       'splat': {'skip': True, 'caption': '운영자 건너뜀', 'points': 0}})\n"
   "            tq = DB.setdefault('quests', {}).get(str(team), {})\n"
   "            if any(k.startswith('q') or k in ('act', 'tut') for k in tq):\n"
   "                tq = {'a': dict(tq, dev='legacy')}\n"
   "            for l, cur in list(tq.items()):\n"
   "                if not isinstance(cur, dict):\n"
   "                    continue\n"
   "                new = {'dev': cur.get('dev'), 'seen': cur.get('seen') or now}\n"
   "                for x in done:\n"
   "                    new[x] = now\n"
   "                if act:\n"
   "                    new['act'] = act\n"
   "                if tut:\n"
   "                    new['tut'] = cur.get('tut') or now\n"
   "                if done:\n"
   "                    new['story'] = 3\n"
   "                    new['records'] = {k: now for k in ('q1', 'q2') if k in done}\n"
   "                if 'q1' in done:\n"
   "                    new['power'] = now\n"
   "                tq[l] = new\n"
   "            if tq:\n"
   "                DB['quests'][str(team)] = tq\n"
   "            if 'q4' not in done and str(team) in DB.get('vikings', {}):\n"
   "                DB['vikings'].pop(str(team), None)\n"
   "                vik_remove(team)\n"
   "            DB.setdefault('trev', {})[str(team)] = now\n"
   "            save()\n"
   "            self.send_json(state())\n\n"
   "    # 운영자: 자체 스캔을 복구됨으로 확정(ok=false면 다시 확인 대기로)\n")
SP.write_bytes((t.replace('\n', '\r\n') if crlf else t).encode('utf-8'))
# ---------------- page ----------------
P = R / 'chapter05/index.html'; s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80]); s = s.replace(old, new)
rep("function adminHTML(){",
    "/* a team can be put at any point of the flow (user, 2026-11-13). zones = campus records restored, done = island missions finished, act = acts seen */\n"
    "const ADM_STAGES = [\n"
    "  ['튜토리얼 직후 (기록 1 찍기 전)', [], [], 0], ['기록 1 제출 직후 (1막 시작)', ['z1'], [], 0], ['미션 1 시작 전', ['z1'], [], 1], ['미션 2 시작 전', ['z1'], ['q1'], 1],\n"
    "  ['기록 2 찍기 전', ['z1'], ['q1','q2'], 1], ['기록 2 제출 직후 (2막 시작)', ['z1','z2'], ['q1','q2'], 1], ['미션 3 시작 전', ['z1','z2'], ['q1','q2'], 2], ['미션 4 시작 전', ['z1','z2'], ['q1','q2','q4'], 2],\n"
    "  ['기록 3 찍기 전', ['z1','z2'], ['q1','q2','q4','q5'], 2], ['기록 3 제출 직후 (3막 시작)', ['z1','z2','z3'], ['q1','q2','q4','q5'], 2], ['미션 5 시작 전', ['z1','z2','z3'], ['q1','q2','q4','q5'], 3], ['미션 5 끝 (환원 직전)', ['z1','z2','z3'], ['q1','q2','q4','q5','q3'], 3]];\n"
    "async function adminStage(team, k){ const g = ADM_STAGES[k]; if(!team || !g) return;\n"
    "  if(!confirm(`${team}조를 「${g[0]}」 시점으로 옮깁니다.\\n그 조의 제출·섬 미션 진행이 이 시점에 맞게 바뀌고, 조 태블릿은 15초 안에 새로 열립니다.`)) return;\n"
    "  try{ const st = await api('/admin/stage', {team, zones:g[1], done:g[2], act:g[3]}, true); if(team === TEAM) questPending.clear(); STATE_VER = -1; applyState(st); renderAdmin(); toast(`${team}조 → ${g[0]}`); }catch(e){ toast(e.message); } }\n"
    "function adminHTML(){")
rep("<td class=\"act\"><button type=\"button\" class=\"mini\" data-aq=\"${t}:*:*:0\" ${ls.length ? '' : 'hidden'}>조 초기화</button></td></tr>`; };",
    "<td class=\"act\"><select class=\"mini\" data-astage=\"${t}\" aria-label=\"${t}조 시점 이동\" ${ls.length ? '' : 'hidden'}><option value=\"\">시점 이동</option>${ADM_STAGES.map((g, k)=> `<option value=\"${k}\">${esc(g[0])}</option>`).join('')}</select><button type=\"button\" class=\"mini\" data-aq=\"${t}:*:*:0\" ${ls.length ? '' : 'hidden'}>조 초기화</button></td></tr>`; };")
rep("document.addEventListener('change', e=>{ const v = e.target.closest('[data-aview]'); if(!v) return;",
    "document.addEventListener('change', e=>{ const sg = e.target.closest('[data-astage]'); if(sg){ const k = sg.value; sg.value = ''; if(k !== '') adminStage(+sg.dataset.astage, +k); return; } const v = e.target.closest('[data-aview]'); if(!v) return;")
rep("function applyState(st){\n  checkReset(st);",
    "let TREV_SEEN = null;\n"
    "function checkStage(st){ if(!TEAM || SCREEN || LOCAL) return false; const cur = +((st.trev || {})[TEAM] || 0); let stored = 0; try{ stored = +localStorage.getItem('void-trev-' + TEAM) || 0; }catch(e){}\n"
    "  if(cur > stored) try{ localStorage.setItem('void-trev-' + TEAM, String(cur)); }catch(e){}\n"
    "  if(TREV_SEEN === null){ TREV_SEEN = cur; if(cur > stored){ let left = false; try{ left = Object.keys(localStorage).some(k=> /^void-(quest|records|mini)-/.test(k)); }catch(e){} if(left){ hardRestart(false); return true; } } return false; }   /* a page opened after the move already has the server's state: it only drops stale memories */\n"
    "  if(cur > TREV_SEEN){ TREV_SEEN = cur; hardRestart(false); return true; } return false; }\n"
    "function applyState(st){\n  checkReset(st); if(RESTARTING || checkStage(st)) return;")
P.write_bytes(s.encode('utf-8')); print('ok page crlf', s.count('\r\n'), 'server crlf', crlf)
