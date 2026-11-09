# 2026-11-09 도로그램 수업 흐름 점검. 서버: CH5_PORT=8095 CH5_ADMIN_KEY=0101 (스크래치 사본 폴더에서), 페이지는 그 서버가 서빙.
# 학생 1조 노트북 / 진행 화면 / 선생님 화면 세 창으로, 1라운드 예시 보기 → 만들기 → 판별 → 공개 → 2라운드 예시 보기까지.
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
        ctx = await b.new_context(viewport={'width': 1366, 'height': 768}); rq = ctx.request
        errs = []
        async def page(path='/chapter05/feed.html'):
            pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
            await pg.goto(BASE + path, wait_until='load'); await asyncio.sleep(2); return pg
        async def phase(ph, rd): r = await rq.post(BASE + '/api/ch5/admin/phase', data=json.dumps({'phase': ph, 'round': rd}), headers=H); assert r.ok, await r.text()
        async def state(t=1): return await (await rq.get(BASE + f'/api/ch5/state?team={t}')).json()
        await rq.post(BASE + '/api/ch5/admin/reset', data=json.dumps({'confirm': 'RESET'}), headers=H)
        await phase('read', 'news')

        st = await state()
        check(st['posts'] and all(x.get('seed') and x['format'] == 'news' for x in st['posts']), f'예시 보기: 뉴스 예시만 내려감 ({len(st["posts"])})')

        kid = await page()
        check(await kid.locator('#teamModal').is_visible(), '조 선택 창이 먼저 뜸')
        check(await kid.locator('#btnScreen').count() == 0, '진행 화면 버튼 없음')
        await kid.screenshot(path=OUT + '/a0_team.png')
        await kid.locator('#teamGrid [data-team="1"]').click(); await asyncio.sleep(1)
        await kid.screenshot(path=OUT + '/a1_home.png')
        await kid.locator('.round-tile[data-round="news"]').click(); await asyncio.sleep(1)
        check(await kid.locator('#guideBox details[open]').count() == 1, '뉴스 안내 카드가 펼쳐져 있음')
        n = await kid.locator('#feed [data-open]').count(); check(n >= 15, f'예시 뉴스 목록 ({n})')
        await kid.screenshot(path=OUT + '/a2_examples.png', full_page=False)
        # 예시 하나 판별 → 해설 + 들통나는 곳
        sid = next(x['id'] for x in st['posts'] if x['answer'] if False) if False else None
        fake = [x for x in (await (await rq.get(BASE + '/api/ch5/admin/state', headers=H)).json())['posts'] if x.get('seed') and x['format'] == 'news' and x['answer']['truth'] == 'fake'][0]
        r = await rq.post(BASE + '/api/ch5/judge', data=json.dumps({'team': 1, 'postId': fake['id'], 'verdict': 'fake', 'criterion': 'who'}), headers=J); check(r.ok, '예시 판별 저장')
        await kid.evaluate("refresh()"); await asyncio.sleep(1)
        await kid.locator(f'#feed [data-open="{fake["id"]}"]').first.click(); await asyncio.sleep(1)
        txt = await kid.locator('#pmBox').inner_text()
        check('해설' in txt and '들통나는 곳' in txt and '쓴 수법' in txt, f'예시 해설에 들통나는 곳·쓴 수법 ({txt[:0]})')
        await kid.screenshot(path=OUT + '/a3_answer.png')
        await kid.keyboard.press('Escape'); await asyncio.sleep(0.5)

        scr = await page('/chapter05/feed.html?view=screen')
        # 선생님
        tea = await page()
        await tea.locator('#btnTeacher').click(); await asyncio.sleep(0.6)
        await tea.fill('#adPw', '0101'); await tea.click('#adLoginBtn'); await asyncio.sleep(2)
        check(await tea.locator('#opBar').is_visible(), '선생님: 진행 막대')
        tiles = await tea.evaluate("[...document.querySelectorAll('.round-tile[data-round]')].map(b=>b.disabled)")
        check(tiles == [False, False, False], f'선생님: 세 라운드 모두 열림 ({tiles})')
        await tea.locator('.round-tile[data-round="story"]').click(); await asyncio.sleep(1)
        ns = await tea.locator('#feed [data-open]').count(); check(ns >= 10, f'선생님: 스토리 예시도 다 보임 ({ns})')
        await tea.screenshot(path=OUT + '/b0_teacher.png')
        await tea.locator('[data-act="home"]').click(); await asyncio.sleep(0.5)
        nxt = await tea.locator('#opBar [data-step]').last.inner_text()
        check('만들기' in nxt, f'다음 단계 버튼 = 만들기 ({nxt.strip()})')
        await tea.locator('#opBar [data-step="make:news"]').click(); await asyncio.sleep(2.5)

        # 만들기: 아이 노트북은 만들기 화면으로 따라감, 예시는 사라짐
        check(await kid.evaluate("S.tab") == 'make', '만들기 시작 → 1조 노트북이 만들기 화면으로')
        st = await state(); check(not any(x.get('seed') for x in st['posts']), '만들기: 예시가 사라짐')
        fm = await kid.evaluate("[...document.querySelectorAll('#optFormat [data-format]')].filter(b=>!b.disabled).map(b=>b.dataset.format)")
        check(fm == ['news'], f'만들기: 뉴스만 선택 가능 ({fm})')
        nk = await kid.locator('#fClueKind option').count(); check(nk == 7, f'단서 종류 선택지 7개 ({nk})')
        await kid.select_option('#fClueKind', 'cross'); await asyncio.sleep(0.3)
        check(not await kid.evaluate("document.getElementById('factField').hidden"), '자료실 내용 고르기 칸이 열림')
        await kid.screenshot(path=OUT + '/a4_make.png')
        bad = post(9, 'news'); bad['secret']['clueKind'] = 'cross'; bad['secret']['fact'] = ''
        r = await rq.post(BASE + '/api/ch5/posts', data=json.dumps(bad), headers=J); check(r.status == 400, '자료실 사실 없는 가짜는 거부')
        for t in (1, 2, 3):
            r = await rq.post(BASE + '/api/ch5/posts', data=json.dumps(post(t, 'news', 'fake' if t != 3 else 'real')), headers=J); check(r.ok, f'{t}조 뉴스 올림')
        for i in range(2):
            r = await rq.post(BASE + '/api/ch5/posts', data=json.dumps(post(1, 'news')), headers=J); check(r.ok, f'1조 뉴스 {i + 2}번째 올림')
        r = await rq.post(BASE + '/api/ch5/posts', data=json.dumps(post(1, 'news')), headers=J); check(r.status == 400, '1조 4번째는 거부')
        await asyncio.sleep(2)
        # 선생님 검토: 2조 글 돌려보내기 → 2조만 보임, 1조에는 안 보임 → 2조가 고쳐 올리면 다시 올라감
        adm = await (await rq.get(BASE + '/api/ch5/admin/state', headers=H)).json()
        p2 = next(x for x in adm['posts'] if x.get('team') == 2)
        r = await rq.post(BASE + '/api/ch5/admin/moderate', data=json.dumps({'postId': p2['id'], 'action': 'return', 'note': '시간이 자료실에 없어요'}), headers=H); check(r.ok, '돌려보내기')
        s2 = await state(2); mine2 = next(x for x in s2['posts'] if x.get('mine'))
        check(mine2['status'] == 'returned' and '자료실' in mine2.get('note', ''), f'2조에 돌려보냄+메모 보임 ({mine2["status"]}, {mine2.get("note")})')
        s1 = await state(1); check(not any(x.get('team') == 2 for x in s1['posts']) and len([x for x in s1['posts'] if not x.get('mine')]) == 0, '돌려보낸 글은 다른 조에 안 보임(만들기 중)')
        await tea.evaluate("refresh()"); await asyncio.sleep(1)
        bar = await tea.locator('#opBar').inner_text(); check('돌려보냄 1' in bar, f'진행 막대: 돌려보냄 1 ({bar.splitlines()[2] if len(bar.splitlines())>2 else bar})')
        kid2 = await page(); await kid2.locator('#teamGrid [data-team="2"]').click(); await asyncio.sleep(1.5)
        check(await kid2.locator('#returnedNote').count() == 1, '2조 만들기 화면에 돌려보냄 안내')
        await kid2.screenshot(path=OUT + '/a4b_returned.png')
        fix = post(2, 'news'); fix['id'] = p2['id']; fix['secret']['clueKind'] = 'cross'; fix['secret']['fact'] = '지난해 매출 386억 원'
        r = await rq.post(BASE + '/api/ch5/posts', data=json.dumps(fix), headers=J); check(r.ok, f'2조가 고쳐 올림 ({r.status})')
        adm = await (await rq.get(BASE + '/api/ch5/admin/state', headers=H)).json()
        check(next(x for x in adm['posts'] if x['id'] == p2['id'])['status'] == 'approved', '고쳐 올리면 다시 올라감')
        await kid2.close()
        await tea.evaluate("refresh()"); await asyncio.sleep(1)
        bar = await tea.locator('#opBar').inner_text(); check('2개 이상 올린 조 1 / 10' in bar, f'진행 막대: 2개 이상 올린 조 1 ({bar.splitlines()[:3]})')
        await scr.evaluate("refresh()"); await asyncio.sleep(1)
        await scr.screenshot(path=OUT + '/c0_screen_make.png')

        # 판별
        await tea.locator('#opBar [data-step="judge:news"]').click(); await asyncio.sleep(2.5)
        check(await kid.evaluate("S.tab") == 'feed' and await kid.evaluate("S.fmt") == 'news', '판별 시작 → 1조 노트북이 뉴스 판별 화면으로')
        hint = await kid.locator('#roundHint').inner_text(); check('남은 것 2개' in hint, f'판별 안내 ({hint})')
        st = await state()
        for x in [x for x in st['posts'] if not x.get('mine')]:
            await rq.post(BASE + '/api/ch5/judge', data=json.dumps({'team': 1, 'postId': x['id'], 'verdict': 'fake', 'criterion': 'who'}), headers=J)
        await kid.screenshot(path=OUT + '/a5_judge.png')

        # 공개 → 2라운드 예시
        await tea.locator('#opBar [data-step="reveal:news"]').click(); await asyncio.sleep(2.5)
        check(await kid.locator('#twist').is_visible(), '공개 → 1조 노트북에 정답 공개 배너')
        await kid.screenshot(path=OUT + '/a6_reveal.png')
        await tea.locator('#opBar [data-step="read:shorts"]').click(); await asyncio.sleep(2.5)
        check(await kid.evaluate("S.fmt") == 'shorts', '2라운드 예시 → 1조 노트북이 쇼츠 예시로')
        st = await state(); check(st['posts'] and all(x.get('seed') and x['format'] == 'shorts' or not x.get('seed') for x in st['posts']) and any(x.get('seed') for x in st['posts']), '2라운드 예시: 쇼츠 예시가 내려감')
        g = await kid.locator('#guideBox').inner_text(); check('쇼츠에서' in g, '쇼츠 안내 카드')
        await kid.screenshot(path=OUT + '/a7_shorts_examples.png')
        await tea.screenshot(path=OUT + '/b1_teacher_bar.png')
        check(not errs, f'페이지 오류 없음 {errs[:2]}')
        await b.close()
    print('FAILS', len(fails)); sys.exit(1 if fails else 0)
asyncio.run(main())
