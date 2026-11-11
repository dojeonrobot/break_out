# 챕터 3 점검: 허브의 기억의 틈 버튼, gap.html, 시그널 브레이크 안의 미션 뽑기
# 사용: python scripts/pending/ch3_check_merge.py <출력 폴더>   (break_out 폴더에서 python -m http.server 8811 을 먼저 띄운다)
import sys, os
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
BASE = "http://127.0.0.1:8811"
GPU = ["--use-gl=angle", "--use-angle=d3d11", "--ignore-gpu-blocklist"]
RENDERER = """() => { const g = document.createElement('canvas').getContext('webgl'); if (!g) return 'no-webgl';
  const e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'no-extension'; }"""
OVERFLOW = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"

with sync_playwright() as p:
    b = p.chromium.launch(args=GPU)
    errors = []

    def new(w, h):
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        return pg

    pg = new(1366, 768)
    pg.goto(BASE + "/index.html", timeout=120000)
    print("renderer:", pg.evaluate(RENDERER))
    pg.wait_for_timeout(1500)
    card = pg.locator("text=기억의 틈").first
    card.scroll_into_view_if_needed()
    pg.screenshot(path=f"{OUT}/hub.png")
    card.click()
    pg.wait_for_timeout(300)
    print("hub modal name:", pg.inner_text("#modalChapterName"))
    pg.close()

    for name, (w, h) in {"gap_1366": (1366, 768), "gap_tab_land": (1280, 800), "gap_tab_port": (800, 1280),
                         "gap_phone": (390, 844), "gap_phone_land": (780, 360)}.items():
        pg = new(w, h)
        pg.goto(BASE + "/chapter03/gap.html")
        pg.wait_for_timeout(500)
        print(name, "overflowX:", pg.evaluate(OVERFLOW), "scrollH-clientH:",
              pg.evaluate("() => document.documentElement.scrollHeight - innerHeight"))
        pg.screenshot(path=f"{OUT}/{name}.png")
        if name == "gap_1366":
            pg.click(".gap-item .qr-zoom >> nth=1")
            pg.wait_for_timeout(300)
            pg.screenshot(path=f"{OUT}/gap_zoom.png")
            pg.keyboard.press("Escape")
            print("zoom closed:", not pg.evaluate("() => document.getElementById('zoomOverlay').classList.contains('show')"))
        pg.close()

    for name, (w, h) in {"sb_1366": (1366, 768), "sb_tab_port": (800, 1280), "sb_phone": (390, 844)}.items():
        pg = new(w, h)
        pg.goto(BASE + "/chapter03/index.html")
        pg.wait_for_timeout(1200)
        if pg.locator("#missionStartBtn").is_visible():
            pg.click("#missionStartBtn")
            pg.wait_for_timeout(700)
        if pg.locator("#qrConfirmBtn").is_visible():
            pg.click("#qrConfirmBtn")
            pg.wait_for_timeout(500)
        print(name, "overflowX:", pg.evaluate(OVERFLOW))
        pg.screenshot(path=f"{OUT}/{name}.png")
        pg.click("#missionBtn")
        fr = pg.frame_locator("#missionLayer iframe")
        fr.locator("#embed-close").wait_for(state="visible", timeout=20000)
        fr.locator(".card").first.wait_for(state="visible", timeout=20000)
        pg.wait_for_timeout(1800)
        print(name, "home hidden:", not fr.locator("#home-link").is_visible(), "cards:", fr.locator(".card").count())
        pg.screenshot(path=f"{OUT}/{name}_mission.png")
        if name == "sb_1366":
            fr.locator(".card").first.click()
            pg.wait_for_timeout(2200)
            pg.screenshot(path=f"{OUT}/{name}_mission_result.png")
            fr.locator("#result-close-btn").click()
            pg.wait_for_timeout(400)
        fr.locator("#embed-close").click()
        pg.wait_for_timeout(300)
        print(name, "layer closed:", not pg.evaluate("() => document.getElementById('missionLayer').classList.contains('show')"),
              "focus:", pg.evaluate("() => document.activeElement.id"))
        pg.close()

    # 따로 열었을 때는 예전처럼 메인 링크가 보여야 한다
    pg = new(1366, 768)
    pg.goto(BASE + "/chapter03/mission.html")
    pg.wait_for_timeout(1500)
    print("standalone home visible:", pg.locator("#home-link").is_visible(), "close visible:", pg.locator("#embed-close").is_visible())
    pg.close()
    b.close()
    print("errors:", errors)
