# 2026-11-11 섬 위치 이름표 기본값 꺼짐(사용자). 캠퍼스 「건물 이름」은 그대로 켜짐. 켜고 끈 상태는 월드별로 따로 기억한다(새로고침하면 기본값).
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s
def swap(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)
swap("tgl('lLbl', v=>{ showLabels=v; });", "const LBL_ON = {erica:true, island:false};   // island place labels start hidden (user, 2026-11-11); each world keeps its own switch\ntgl('lLbl', v=>{ showLabels=v; LBL_ON[W.id]=v; labelsDirty=true; });")
swap("  $('lLbl').textContent = w.lblBtn;\n", "  $('lLbl').textContent = w.lblBtn; showLabels = LBL_ON[id] !== false; $('lLbl').setAttribute('aria-pressed', showLabels);\n")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
