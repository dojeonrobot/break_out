# 2026-11-09 도로그램 3라운드 점검. 서버: CH5_PORT=8095 CH5_ADMIN_KEY=0101 (data는 스크래치 사본 폴더), 페이지는 그 서버가 정적으로 서빙.
import asyncio, json, sys
from playwright.async_api import async_playwright
BASE = 'http://127.0.0.1:8095'; OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
fails = []
def check(c, m): print(('OK   ' if c else 'FAIL ') + m); (None if c else fails.append(m))
H = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; J = {'content-type': 'application/json'}

def post(team, fmt, truth='fake'):
    body = '첫 문단입니다. 도로랜드 소식.\n\n둘째 문단입니다. 자세한 내용.'
    return {'team': team, 'format': fmt, 'author': {'name': f'{team}조 계정', 'handle': f'@t{team}', 'kind': 'person'},
            'title': f'{team}조 {fmt}', 'body': body, 'secret': {'truth': truth, 'clue': '단서', 'tactic': '숫자 부풀리기', 'clueCriterion': 'who'}}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1366, 'height': 768})
        rq = ctx.request
        async def phase(ph, rd): r = await rq.post(BASE + '/api/ch5/admin/phase', data=json.dumps({'phase': ph, 'round': rd}), headers=H); assert r.ok, await r.text()
        await rq.post(BASE + '/api/ch5/admin/reset', data=json.dumps({'confirm': 'RESET'}), headers=H)
        await phase('read', 'news')
        st = await (await rq.get(BASE + '/api/ch5/state?team=1')).json()
        check(not any(x.get('seed') for x in st['posts']), f'no example posts sent to a team ({len(st["posts"])} posts)')
        check(st.get('round') == 'news', 'starts on round news')

        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(BASE + '/chapter05/feed.html', wait_until='load'); await asyncio.sleep(2)
        await asyncio.sleep(1)
        check(await pg.locator('#teamModal').is_visible(), 'team picker shows first')
        await pg.screenshot(path=OUT + '/r0_team.png')
        await pg.locator('#teamGrid [data-team="1"]').click(); await asyncio.sleep(1)
        body = await pg.evaluate('document.body.innerText')
        check('지금 단계' not in body and '자료 살펴보기' not in body and '예제' not in body, 'no phase/example text on the first screen')
        tiles = await pg.evaluate("[...document.querySelectorAll('[data-round]')].map(b=>[b.dataset.round,b.disabled])")
        check(tiles == [['news', False], ['shorts', True], ['story', True]], f'tiles: news open, others locked ({tiles})')
        await pg.screenshot(path=OUT + '/r1_home.png')
        # reload keeps asking for the team
        await pg.reload(wait_until='load'); await asyncio.sleep(2); await asyncio.sleep(1)
        check(await pg.locator('#teamModal').is_visible(), 'team picker shows again after reload')
        await pg.locator('#teamGrid [data-team="1"]').click(); await asyncio.sleep(0.5)

        # round 1 make
        await phase('make', 'news'); await asyncio.sleep(1.5)
        r = await rq.post(BASE + '/api/ch5/posts', data=json.dumps(post(1, 'shorts')), headers=J)
        check(r.status == 400, 'shorts refused in the news round')
        for t in (1, 2, 3):
            r = await rq.post(BASE + '/api/ch5/posts', data=json.dumps(post(t, 'news', 'fake' if t != 3 else 'real')), headers=J); check(r.ok, f'team {t} news saved ({r.status} {(await r.text())[:80]})')
        await pg.locator('[data-round="news"]').click(); await asyncio.sleep(0.6)
        head = await pg.locator('#roundHead').inner_text()
        check('우리 조 뉴스 만들기' in head, f'make button in round view ({head!r})')
        n = await pg.locator('#feed .news-item, #feed [data-open]').count()
        await pg.screenshot(path=OUT + '/r2_make.png')
        await pg.locator('#roundHead [data-goto="make"]').click(); await asyncio.sleep(0.6)
        fm = await pg.evaluate("[...document.querySelectorAll('#optFormat [data-format]')].map(b=>[b.dataset.format,b.disabled])")
        check(fm and all(dis == (k != 'news') for k, dis in fm), f'make tab: only news selectable ({fm})')
        await pg.screenshot(path=OUT + '/r3_maketab.png')

        # judge
        await phase('judge', 'news'); await asyncio.sleep(1.5)
        st = await (await rq.get(BASE + '/api/ch5/state?team=1')).json()
        others = [x for x in st['posts'] if not x.get('mine')]
        check(len(others) == 2 and all('secret' not in x for x in others), f'team 1 sees 2 other news, no secrets ({len(others)})')
        for x in others:
            r = await rq.post(BASE + '/api/ch5/judge', data=json.dumps({'team': 1, 'postId': x['id'], 'verdict': 'fake', 'criterion': 'who'}), headers=J); check(r.ok, 'judge ok')
        check('scores' not in st, 'no scores before reveal')
        await pg.locator('[data-tab="feed"]').first.click(); await asyncio.sleep(0.3)
        await pg.locator('[data-round="news"]').click(); await asyncio.sleep(0.8)
        await pg.screenshot(path=OUT + '/r4_judge.png')

        # reveal → round 2
        await phase('reveal', 'news'); await asyncio.sleep(1.5)
        st = await (await rq.get(BASE + '/api/ch5/state?team=1')).json()
        me = next(r for r in st['scores'] if r['team'] == 1)
        check(me['correct'] == 1 and me['judgable'] == 2, f'team 1 score after round 1 ({me})')
        await pg.screenshot(path=OUT + '/r5_reveal.png')
        await phase('make', 'shorts'); await asyncio.sleep(1.5)
        tiles = await pg.evaluate("[...document.querySelectorAll('[data-round]')].map(b=>[b.dataset.round,b.disabled,b.classList.contains('now')])")
        check(tiles == [['news', False, False], ['shorts', False, True], ['story', True, False]], f'round 2: news reviewable, shorts now, story locked ({tiles})')
        st = await (await rq.get(BASE + '/api/ch5/state?team=1')).json()
        check(all('secret' in x for x in st['posts'] if x['format'] == 'news'), 'round 1 answers stay open in round 2')
        check('scores' in st, 'scores stay visible')
        r = await rq.post(BASE + '/api/ch5/judge', data=json.dumps({'team': 1, 'postId': others[0]['id'], 'verdict': 'real', 'criterion': 'who'}), headers=J)
        check(r.status == 400, 'old round can no longer be judged')
        await pg.screenshot(path=OUT + '/r6_round2.png')

        # admin buttons
        await pg.evaluate("sessionStorage.setItem('dorogram-admin','0101')")
        await pg.locator('[data-tab="admin"]').first.click(); await asyncio.sleep(1.5)
        if await pg.locator('#adPw').is_visible():
            await pg.fill('#adPw', '0101'); await pg.click('#adLoginBtn'); await asyncio.sleep(1.5)
        nb = await pg.locator('[data-adphase]').count()
        check(nb == 10, f'admin shows 10 step buttons ({nb})')
        await pg.locator('[data-adphase="judge:shorts"]').click(); await asyncio.sleep(1.5)
        st = await (await rq.get(BASE + '/api/ch5/state')).json()
        check(st['phase'] == 'judge' and st['round'] == 'shorts', f'admin button sets round+phase ({st["phase"]},{st["round"]})')
        await pg.screenshot(path=OUT + '/r7_admin.png', full_page=True)
        check(not errs, f'no page errors {errs[:2]}')
        await b.close()
    print('FAILS', len(fails)); sys.exit(1 if fails else 0)
asyncio.run(main())
