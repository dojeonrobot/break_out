"""RUN button only: joystick edge no longer sprints; RUN state survives pad hide/show, resets on stopWalk (user, 2026-11-25)."""
import sys
p = 'C:/Users/dlgus/break_out/chapter05/index.html'
s = open(p, encoding='utf-8', newline='').read()
subs = [
    ("const speed = (k.ShiftLeft || k.ShiftRight || walkPad.run || walkPad.lock ? 11 : 5.5)",
     "const speed = (k.ShiftLeft || k.ShiftRight || walkPad.lock ? 11 : 5.5)"),
    ("walkPad.run = d > R*(chase && !chase.over ? 0.82 : 1.15); pad.classList.toggle('run', walkPad.run); ",
     "/* no sprint from pushing the stick to the edge: only the RUN button runs (user, 2026-11-25) */ "),
    ("new MutationObserver(()=>{ rb.hidden = jb.hidden = wp.hidden; if(wp.hidden){ walkPad.lock = false; rb.setAttribute('aria-pressed', 'false'); } })",
     "new MutationObserver(()=>{ rb.hidden = jb.hidden = wp.hidden; rb.setAttribute('aria-pressed', walkPad.lock ? 'true' : 'false'); })"),
    ("walk = null; for(const k in WALK_KEYS) delete WALK_KEYS[k]; walkPad.dx = walkPad.dz = 0; walkPad.run = false;",
     "walk = null; for(const k in WALK_KEYS) delete WALK_KEYS[k]; walkPad.dx = walkPad.dz = 0; walkPad.run = false; walkPad.lock = false; $('walkRun').setAttribute('aria-pressed', 'false');"),
]
for a, b in subs:
    n = s.count(a)
    if n != 1:
        sys.exit(f'match {n}: {a[:60]}')
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
