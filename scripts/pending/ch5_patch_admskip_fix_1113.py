# 2026-11-13 관리자 「건너뛰기」 버튼이 전혀 안 뜨던 버그. ch5_patch_lab_slice_1113이 admSkipWhat에 넣은 on('sliceDlg')가, 게임 창이 아직 만들어지지 않은 동안(게임을 한 번 열기 전) null.dataset으로 터져 버튼이 늘 숨겨졌다.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8')
old = "if(!ADMIN_KEY || SCREEN || LOCAL) return null;\n  const on = id => !!$(id).dataset.on;"
assert s.count(old) == 1
P.write_bytes(s.replace(old, "if(!ADMIN_KEY || SCREEN || LOCAL) return null;\n  const on = id => { const el = $(id); return !!(el && el.dataset.on); };   /* a dialog built on first use may not exist yet */").encode('utf-8')); print('ok')
