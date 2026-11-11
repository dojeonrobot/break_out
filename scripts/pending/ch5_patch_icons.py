# 2026-11-11 관리자 버튼 = 설정(톱니) 아이콘, 소리 끔 = 스피커 옆 X(사선 한 줄은 뜻이 안 읽힘) (사용자)
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s
def swap(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)
GEAR = 'M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z'
swap('<button id="adminBtn" type="button">관리자</button>', f'<button id="adminBtn" type="button" aria-label="관리자" title="관리자"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="{GEAR}" fill="currentColor"/></svg></button>')
swap('<path d="M16 7l6 10" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" class="x"/>', '<path d="M16.5 9.5l5 5M21.5 9.5l-5 5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" class="x"/>')
swap('</style></head><body>', '''#adminBtn{width:44px;padding:0;justify-content:center;color:var(--fg)}
#sndBtn{right:68px}
body.admkey.teamdev #adminBtn{width:auto;padding:0 12px;gap:2px}
</style></head><body>''')
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
