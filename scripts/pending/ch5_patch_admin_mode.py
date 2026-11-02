import io, re
p='C:/Users/dlgus/break_out/chapter05/index.html'; s=io.open(p,encoding='utf-8',newline='').read()
def rep(a,b,n=1):
    global s; c=s.count(a); assert c==n,(c,a[:90]); s=s.replace(a,b)

# 1. island missions done on THIS tablet (QDONE), never the team-wide union an admin view returns
rep("const zoneDoneTeam = (m, t)=>{ if(!m) return false; if(!t) return zoneDone(m); if(m.quest) return teamQuests(t).includes(m.quest) || (t === TEAM && typeof QDONE !== 'undefined' && QDONE.has(m.quest));",
    "const zoneDoneTeam = (m, t)=>{ if(!m) return false; if(!t) return zoneDone(m); if(m.quest) return (t === TEAM && typeof QDONE !== 'undefined') ? QDONE.has(m.quest) : teamQuests(t).includes(m.quest);   // this tablet: its own missions only (an admin login turns teamQuests into the union of the team's tablets)")
rep("return LOCAL ? !QDONE.has(q.id) : !teamQuests(TEAM).includes(q.id); };",
    "return (LOCAL || TEAM) ? !QDONE.has(q.id) : !teamQuests(TEAM).includes(q.id); };   // this tablet's missions (2026-11-02: with an admin login another tablet's mission opened these coordinates)")
# 2. the void's "지금 할 일": the team's own next record
rep("const open = MISSION_E.filter(m=> m.lat != null && !zoneDone(m) && !zoneLocked(m))[0], next = MISSION_E.filter(m=> m.lat != null && !zoneDone(m))[0];",
    "const open = MISSION_E.filter(m=> m.lat != null && !zoneMine(m) && !zoneLocked(m))[0], next = MISSION_E.filter(m=> m.lat != null && !zoneMine(m))[0];")
# 3. "already seen" flags for the ending belong to the tablet's team, not to the admin's view
n1 = s.count("`void-simdone-${viewTeam()}`"); n2 = s.count("`void-restore-${viewTeam()}`")
s = s.replace("`void-simdone-${viewTeam()}`", "`void-simdone-${progTeam()}`").replace("`void-restore-${viewTeam()}`", "`void-restore-${progTeam()}`")
print('seen keys', n1, n2)
rep("const zoneMine = m => zoneDoneTeam(m, TEAM);", "const zoneMine = m => zoneDoneTeam(m, TEAM);\nconst progTeam = ()=> TEAM || viewTeam();   // whose progress a flag belongs to")
# 4. notices reach a team tablet even while an admin is logged in on it
rep("if(seen < id && !ADMIN_KEY && !SCREEN){", "if(seen < id && (!ADMIN_KEY || TEAM) && !SCREEN){")
# 5. an admin login on a team tablet ends by itself after 30 minutes (a teacher forgetting to log out must not leave the skip tools to the children)
rep("let ADMIN_KEY = ''; try{ ADMIN_KEY = sessionStorage.getItem('void-admin') || ''; }catch(e){}",
    """let ADMIN_KEY = ''; try{ ADMIN_KEY = sessionStorage.getItem('void-admin') || ''; }catch(e){}
const ADMIN_TTL = 30*60*1000;   // team tablets only (2026-11-02)
try{ const at = +sessionStorage.getItem('void-admin-at') || 0; if(ADMIN_KEY && at && Date.now() - at > ADMIN_TTL && new URLSearchParams(location.search).get('team')){ ADMIN_KEY = ''; sessionStorage.removeItem('void-admin'); sessionStorage.removeItem('void-view'); } }catch(e){}""")
rep("    STATE_VER = -1; applyState(st); openAdmin(); try{ questRefresh(); }catch(e){} }",
    "    try{ sessionStorage.setItem('void-admin-at', String(Date.now())); }catch(e){}\n    STATE_VER = -1; applyState(st); openAdmin(); try{ questRefresh(); }catch(e){} }")
rep("setInterval(()=>{ try{ questPillTick(); }catch(e){}",
    "setInterval(()=>{ try{ questPillTick(); }catch(e){}\n  if(ADMIN_KEY && TEAM){ let at = 0; try{ at = +sessionStorage.getItem('void-admin-at') || 0; }catch(e){} if(at && Date.now() - at > ADMIN_TTL){ try{ adminAct('logout'); toast('관리자 로그인이 30분이 지나 자동으로 풀렸습니다'); }catch(e){} } }")
# admin badge on a team tablet so it is obvious the tablet is in admin mode
rep("#tutSkip[hidden]{display:none}", "#tutSkip[hidden]{display:none}body.admkey.teamdev #adminBtn{background:#ffb347;color:#1a1206;border-color:#ffb347;font-weight:800}body.admkey.teamdev #adminBtn::after{content:' 로그인 중'}")
rep("document.body.classList.toggle('admkey', !!ADMIN_KEY);", "document.body.classList.toggle('admkey', !!ADMIN_KEY); document.body.classList.toggle('teamdev', !!TEAM);")
io.open(p,'w',encoding='utf-8',newline='').write(s); print('admin patch ok')
