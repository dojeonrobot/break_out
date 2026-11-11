# 챕터 3 기억의 틈(gap.html) 점검: 배경, QR 크게 보기 움직임
# 사용: python scripts/pending/ch3_check_gap.py <출력 폴더>   (break_out 폴더에서 python -m http.server 8811 을 먼저 띄운다)
import sys, os
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:8811/chapter03/gap.html"
GPU = ["--use-gl=angle", "--use-angle=d3d11", "--ignore-gpu-blocklist"]
RENDERER = """() => { const g = document.createElement('canvas').getContext('webgl'); if (!g) return 'no-webgl';
  const e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'no-extension'; }"""

with sync_playwright() as p:
    b = p.chromium.launch(args=GPU)
    errors = []
    first = True
    for name, (w, h) in {"g_1366": (1366, 768), "g_1920": (1920, 1080), "g_tab_land": (1280, 800), "g_tab_port": (800, 1280),
                         "g_phone": (390, 844), "g_phone_land": (780, 360)}.items():
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.goto(URL)
        if first:
            print("renderer:", pg.evaluate(RENDERER)); first = False
        pg.wait_for_timeout(900)
        print(name, "overflowX:", pg.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth"),
              "overflowY:", pg.evaluate("() => document.documentElement.scrollHeight - innerHeight"))
        pg.screenshot(path=f"{OUT}/{name}.png")
        pg.click(".gap-qr >> nth=1", force=True)   # 떠다니는 움직임 때문에 안정 대기를 건너뛴다
        if name == "g_1366":
            pg.wait_for_timeout(110)
            pg.screenshot(path=f"{OUT}/{name}_zoom_mid.png")   # 커지는 도중
        pg.wait_for_timeout(500)
        r = pg.evaluate("() => { const r = document.getElementById('zoomPlate').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height), innerWidth, innerHeight]; }")
        print(name, "zoom plate:", r, "inside:", r[0] >= 0 and r[1] >= 0 and r[0] + r[2] <= r[4] and r[1] + r[3] <= r[5])
        pg.screenshot(path=f"{OUT}/{name}_zoom.png")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(500)
        print(name, "closed:", not pg.evaluate("() => document.getElementById('zoomOverlay').classList.contains('show')"),
              "focus back:", pg.evaluate("() => document.activeElement.className"))
        pg.close()
    b.close()
    print("errors:", errors)
