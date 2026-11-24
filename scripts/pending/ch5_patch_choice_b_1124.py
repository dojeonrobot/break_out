# 2026-11-24 사용자가 고른 선택지 시안 B: 아래쪽 밝은 카드 세 장(인물 얼굴·이름·번호) + 그 위 코덱스 질문 줄 + 위 가운데 「코덱스의 믿음」(눈 모양 네 칸).
#  시안 그림 bak/sian_1124/선택지_시안AB.png (아래 장).  벽화가 위쪽에 보이도록 아래만 어둡게.
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
def rep(a, b):
    global s
    if s.count(a) != 1: sys.exit(f'anchor x{s.count(a)}: {a[:80]}')
    s = s.replace(a, b)

CSS = ("#choiceDlg{position:fixed;inset:0;z-index:37;display:none;-webkit-user-select:none;user-select:none;font-family:var(--sans)}\n"
"#choiceDlg[data-on]{display:block}\n"
"#choiceDlg::before{content:'';position:absolute;inset:auto 0 0 0;height:min(440px,62vh);background:linear-gradient(to top,rgba(12,9,6,.92),rgba(12,9,6,.55) 60%,transparent);pointer-events:none}\n"
"#choiceDlg .in{position:absolute;left:50%;bottom:calc(24px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);width:min(1180px,calc(100vw - 32px));display:grid;gap:14px}\n"
"#choiceDlg .q{display:flex;align-items:center;gap:16px;width:min(1000px,100%);margin:0 auto}\n"
"#choiceDlg .q .face{flex:none;width:72px;height:72px;border-radius:50%;overflow:hidden;background:#e9dcc2;border:3px solid #f2e7cf}\n"
"#choiceDlg .q .face img{width:100%;height:100%;object-fit:cover;object-position:50% 6%}\n"
"#choiceDlg .q p{flex:1;margin:0;padding:12px 22px;border-radius:16px;background:rgba(20,15,10,.84);color:#fff4df;font:600 21px/1.5 var(--sans);word-break:keep-all}\n"
"#choiceDlg .q p small{display:block;font:800 14px var(--sans);color:#ffcf8a;margin-bottom:2px}\n"
"#choiceDlg .trust{position:fixed;left:50%;top:22px;transform:translateX(-50%);display:flex;align-items:center;gap:10px;padding:10px 16px;border-radius:14px;background:rgba(20,15,10,.84);color:#fff4df;font:700 15px var(--sans);white-space:nowrap}\n"
"#choiceDlg .trust span{display:flex;gap:8px}\n"
"#choiceDlg .trust i{position:relative;width:30px;height:20px;border-radius:50%;border:2px solid #ffcf8a;box-sizing:border-box}\n"
"#choiceDlg .trust i.ok{background:#ffcf8a}\n"
"#choiceDlg .trust i.ok::after{content:'';position:absolute;left:50%;top:50%;width:8px;height:8px;margin:-4px;border-radius:50%;background:#3a2410}\n"
"#choiceDlg .opts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:stretch}\n"
"#choiceDlg .opts button{display:grid;align-content:start;gap:10px;padding:16px 20px 20px;text-align:left;border:0;border-radius:20px;background:#f6edda;color:#2a1d12;box-shadow:0 18px 40px -18px rgba(0,0,0,.8);cursor:pointer;font:600 20px/1.5 var(--sans);word-break:keep-all;transition:transform .18s cubic-bezier(.16,1,.3,1),box-shadow .18s}\n"
"#choiceDlg .opts .who{display:flex;align-items:center;gap:10px;font:800 16px var(--sans)}\n"
"#choiceDlg .opts .who img{width:46px;height:46px;border-radius:50%;object-fit:cover;object-position:50% 6%;background:#e3d3b4}\n"
"#choiceDlg .opts .who b{margin-left:auto;width:34px;height:34px;border-radius:10px;background:#2a1d12;color:#f6edda;font:800 17px var(--mono);display:grid;place-items:center}\n"
"#choiceDlg .opts button:hover,#choiceDlg .opts button:focus-visible{transform:translateY(-6px);outline:4px solid #ffcf8a;outline-offset:0}\n"
"#choiceDlg .opts button:active{transform:translateY(-2px) scale(.99)}\n"
"@media (prefers-reduced-motion:reduce){#choiceDlg .opts button{transition:none}#choiceDlg .opts button:hover,#choiceDlg .opts button:focus-visible{transform:none}}\n"
"@media (max-width:760px){#choiceDlg .opts{grid-template-columns:minmax(0,1fr);gap:8px}#choiceDlg .opts button{padding:10px 14px;font-size:16px;gap:4px}#choiceDlg .opts .who img{width:32px;height:32px}#choiceDlg .q .face{display:none}#choiceDlg .q p{font-size:16px;padding:10px 14px}#choiceDlg .trust{top:12px;font-size:13px}}\n"
"@media (max-height:560px){#choiceDlg .in{bottom:10px;gap:8px}#choiceDlg .q .face{display:none}#choiceDlg .q p{font-size:15px;padding:8px 14px}#choiceDlg .opts button{padding:8px 12px;font-size:14px;gap:4px;border-radius:14px}#choiceDlg .opts .who{font-size:13px}#choiceDlg .opts .who img{width:26px;height:26px}#choiceDlg .opts .who b{width:24px;height:24px;font-size:13px;border-radius:7px}#choiceDlg .trust{top:8px;padding:6px 12px;font-size:12px}#choiceDlg .trust i{width:22px;height:15px}}\n")

i = s.find('#choiceDlg{'); e = s.find('#choiceDlg .opts button b{display:none}}')
if i < 0 or e < 0 or e < i: sys.exit('css chunk not found')
e += len('#choiceDlg .opts button b{display:none}}')
s = s[:i] + CSS + s[e:]

rep("d.innerHTML = '<div class=\"in\"><div class=\"q\"><img src=\"img/chars/codex.png?v=20261028c\" alt=\"\"><div><small>코덱스</small><p id=\"chQ\"></p></div><div class=\"trust\">코덱스의 믿음<span id=\"chTrust\"></span></div></div><div class=\"opts\" id=\"chOpts\"></div></div>';",
    "d.innerHTML = '<div class=\"trust\">코덱스의 믿음<span id=\"chTrust\"></span></div><div class=\"in\"><div class=\"q\"><span class=\"face\"><img src=\"img/chars/codex.png?v=20261028c\" alt=\"\"></span><p><small>코덱스</small><span id=\"chQ\"></span></p></div><div class=\"opts\" id=\"chOpts\"></div></div>';")
rep("`<button type=\"button\" data-k=\"${k}\"><b>${k + 1}</b><span><em>${esc(o.who)}</em>${esc(o.text)}</span></button>`",
    "`<button type=\"button\" data-k=\"${k}\"><span class=\"who\"><img src=\"img/chars/${VN_IMG[o.who] || 'zero'}.png?v=20261028c\" alt=\"\">${esc(o.who)}<b>${k + 1}</b></span><span>${esc(o.text)}</span></button>`")
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
