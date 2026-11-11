import asyncio, json, os
from ch5_flow_helper import H, API, STATIC
ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 1
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flow'); LOG = []; STAGE = ['start']
os.makedirs(OUT, exist_ok=True)
WATCH = r"""()=>{const seen={};const vis=e=>e&&e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden'&&+getComputedStyle(e).opacity>.05;
 const txt=e=>(e.innerText||'').replace(/\s+/g,' ').trim();
 const ids=['teamPick','voidVn','vn','questHud','qReward','recDone','callDlg','callPill','questPill','toast','simDone','cinemaEnd','miniBox','restoreDlg','walkHint'];
 setInterval(()=>{const cur={};ids.forEach(id=>{const e=document.getElementById(id);if(vis(e))cur[id]=txt(e)});
  document.querySelectorAll('[data-on]').forEach(e=>{if(e.id&&!ids.includes(e.id)&&vis(e))cur[e.id]=txt(e).slice(0,700)});
  for(const k in cur){if(seen[k]!==cur[k]){seen[k]=cur[k];if(cur[k])window.__flowLog(k,cur[k])}}for(const k in seen){if(!(k in cur))delete seen[k]}},120)}"""
VIS = "(id)=>{const e=document.getElementById(id);return !!e&&e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden'&&+getComputedStyle(e).opacity>.05}"
PANEL = r"""(()=>{const out=[];document.querySelectorAll('body > *').forEach(e=>{if(e.tagName==='CANVAS'||e.tagName==='SCRIPT'||!e.getClientRects().length)return;const t=(e.innerText||'').replace(/\s+/g,' ').trim();if(t&&e.getBoundingClientRect().width>20)out.push((e.id||e.className||e.tagName)+': '+t.slice(0,420))});return out.join('\n      ')})()"""


class F(H):
    async def load(s, q=''):
        pg = s.pg
        await pg.goto(STATIC + '/chapter05/index.html', wait_until='domcontentloaded', timeout=120000)
        for i in range(200):
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.tutEnd"): break
            await asyncio.sleep(.5)


async def main():
    async with F(team=T, w=1180, h=820, touch=True, init="localStorage.setItem('void-sound','0');") as h:
        pg = h.pg; rq = h.ctx.request; ev = h.ev

        def log(k, t): LOG.append((STAGE[0], k, t))
        await pg.expose_function('__flowLog', log)
        await pg.reload(wait_until='domcontentloaded')
        for i in range(200):
            if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.tutEnd"): break
            await asyncio.sleep(.5)
        await ev(WATCH)
        print('GL', await ev("(()=>{const g=__dbg.renderer.getContext(),e=g.getExtension('WEBGL_debug_renderer_info');return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"), flush=True)

        async def vis(i): return await ev(VIS, i)

        async def state():
            return await ev("({world:document.body.className,live:__dbg.quest().live?.id,done:__dbg.quest().done,walk:!!__dbg.walkState(),mini:__dbg.mini?.(),tut:__dbg.tutState().step,vn:!!__dbg.quest().vn(),t:__dbg.target()})")

        async def note(tag):
            LOG.append((STAGE[0], tag + ' STATE', json.dumps(await state(), ensure_ascii=False)))
            LOG.append((STAGE[0], tag + ' SCREEN', await ev(PANEL)))

        async def step():
            if await ev("!!document.getElementById('recDone').dataset.on"):
                await asyncio.sleep(1.1); await ev("document.getElementById('recDone').click()"); return 'rec'
            if await ev("!!__dbg.quest().vn()"):
                await asyncio.sleep(.25); await ev("__dbg.quest().next()"); return 'vn'
            if await vis('voidNext'):
                await asyncio.sleep(.25); await ev("document.getElementById('voidNext').click()"); return 'void'
            return None

        async def pump(cond, limit=120, stepping=True):
            t = 0
            while t < limit:
                try:
                    if await ev(cond): return True
                except Exception: pass
                if stepping: await step()
                await asyncio.sleep(.3); t += .3
            raise AssertionError('timeout ' + cond + ' state=' + json.dumps(await state(), ensure_ascii=False))

        async def settle(q=2.0):
            idle = 0
            while idle < q:
                if await step(): idle = 0
                else: idle += .3
                await asyncio.sleep(.3)

        async def shot(n):
            try: await pg.screenshot(path=os.path.join(OUT, n + '.png'), timeout=60000)
            except Exception: print('shot fail', n)

        async def stage(name, fn):
            STAGE[0] = name; print('==', name, flush=True)
            try:
                await fn(); return True
            except Exception as e:
                LOG.append((name, '!!ERROR', str(e)[:700])); print('ERR', name, str(e)[:600], flush=True); await shot('err'); return False

        async def skip(m):
            await rq.post(API + '/api/void/admin/skip', data=json.dumps({'team': T, 'mission': m}), headers=ADM)

        async def arrive(cond, tries=6):
            for _ in range(tries):
                await settle(1.2); await ev('__dbg.walkTo(...__dbg.target())')
                for _ in range(30):
                    if await ev(cond): return
                    await asyncio.sleep(.3)
            raise AssertionError('arrive ' + cond + ' ' + json.dumps(await state(), ensure_ascii=False))

        async def s_team():
            await pump("!!document.getElementById('teamPick').dataset.on", 60, False); await asyncio.sleep(.5); await shot('01_teampick')
            await ev("()=>{const b=[...document.querySelectorAll('#tpGrid button')].find(b=>b.textContent.trim().startsWith('1조'));b.click()}"); await asyncio.sleep(1.5)

        async def s_tut():
            n = 0
            await pump("__dbg.tutState().step>=0", 30, False); await shot('02_tut_first')
            while await ev("__dbg.tutState().step<99&&__dbg.tutState().step>=0") and n < 80:
                await asyncio.sleep(.5); await ev("document.getElementById('voidNext').click()"); n += 1
                if n in (5, 12, 18): await shot('03_tut_%d' % n)
            await asyncio.sleep(2); await settle(1.5); await shot('04_campus_after_tut'); await note('튜토리얼 끝')

        async def s_rec1():
            await skip('z1'); await pump("!!__dbg.walkState()&&!!__dbg.quest().live", 150); await settle(); await shot('05_m1_start'); await note('미션1 시작')

        async def s_m1():
            await arrive("!!__dbg.quest().vn()"); await shot('06_m1_xylo'); await settle()
            await note('자일로 뒤')
            await ev('__dbg.walkTo(...__dbg.yardDoor())'); await pump("!!document.querySelector('#yardDlg[data-on]')", 40); await asyncio.sleep(1); await settle(1); await shot('07_m1_yard')
            await ev('()=>{const y=__dbg.yard();y.tiles=y.sol.map(r=>r.map(c=>new Set(c)));__dbg.yardPaint()}'); await asyncio.sleep(.8)
            await pump("(()=>{const b=document.getElementById('ydContinue'); return b && b.offsetParent && !b.disabled})()", 60, False); await shot('08_m1_yard_done'); await ev("document.getElementById('ydContinue').click()")
            await asyncio.sleep(3); await shot('09_m1_wake'); await pump("!!document.querySelector('#qReward[data-on]')", 300); await asyncio.sleep(1.2); await shot('10_m1_reward'); await ev("document.getElementById('qrMap').click()")

        async def s_m2():
            await asyncio.sleep(2); await settle(); await shot('11_m2_start'); await note('미션2 시작')
            if not await ev("!!__dbg.walkState()") and await vis('questPill'):
                await ev("document.getElementById('questPill').click()"); await asyncio.sleep(2); await settle()
            await arrive("!!__dbg.quest().vn()"); await shot('12_m2_maze_gate'); await settle(); await note('미로 입구 뒤')
            await ev('__dbg.walkTo(...__dbg.target())'); await pump("!!__dbg.quest().vn()", 40, False); await shot('13_m2_naty')
            await pump("!!document.querySelector('#qReward[data-on]')", 120); await asyncio.sleep(1.2); await shot('14_m2_reward'); await ev("document.getElementById('qrMap').click()")
            await asyncio.sleep(3); await settle(); await shot('15_campus_rec2'); await note('미션2 끝')

        async def s_rec2():
            await skip('z2'); await pump("__rem().noise", 240); await asyncio.sleep(1); await shot('16_act2_noise'); await note('2막 시뮬레이터')

        async def s_m3():
            await pump("__rem().mini?.phase==='hunt'", 180); await settle(); await shot('17_m3_hunt_start'); await note('잔재 수색 시작')
            if not await ev("!!__dbg.walkState()"):
                LOG.append((STAGE[0], 'NOTE', '수색 단계인데 탐험 상태가 아님: questPill=' + str(await vis('questPill'))))
                if await vis('questPill'):
                    await ev("document.getElementById('questPill').click()"); await asyncio.sleep(2); await settle()
                else:
                    await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2); await settle()
            for i in range(3):
                sp = (await ev('__rem()'))['spots'][i]; await ev(f"__dbg.walkTo({sp['x']},{sp['z']})"); await asyncio.sleep(1)
                if i == 0: await shot('19_m3_dig')
                await ev("()=>{document.getElementById('miniGo').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerId:1}))}"); await pump("['dig','game'].includes(__rem().mini?.phase)", 60, False)
                await ev("()=>{document.getElementById('miniGo').dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:1}))}")
                await pump("!!document.querySelector('#remDlg[data-on]')", 60); await asyncio.sleep(.5)
                if i == 0: await shot('20_m3_remdlg')
                await ev("document.getElementById('rmGo').click()"); await asyncio.sleep(.3)
                for k in range(3):
                    await ev("()=>{__remAim();document.getElementById('rmGo').click()}"); await asyncio.sleep(.35)
                await pump("!document.querySelector('#remDlg[data-on]')", 30, False); await asyncio.sleep(.5); await settle(1)
            await pump("__rem().mini?.phase==='walk'", 40); await note('잔재 3개 뒤')
            await ev('__dbg.walkTo(...__dbg.labDoor())'); await pump("!!document.querySelector('#qReward[data-on]')", 120); await asyncio.sleep(1.2); await shot('21_m3_reward'); await ev("document.getElementById('qrMap').click()")
            await asyncio.sleep(3); await settle(); await shot('22_campus_rec3'); await note('미션3 끝')

        async def s_rec3():
            await skip('z3'); await pump("!!__dbg.walkState()&&__dbg.quest().live?.id==='q3'", 180); await settle(); await shot('23_m4_start'); await note('미션4 시작')

        async def s_m4():
            await ev('__dbg.walkTo(...__dbg.target())'); await pump("!!document.querySelector('#caveDlg[data-on]')", 60); await asyncio.sleep(1); await settle(1); await shot('24_cave')
            for g in ['forest', 'valley', 'shore', 'cave', 'water', 'plaza']:
                await pg.locator(f'#cvTiles [data-g="{g}"]').click(); await pg.locator(f'#cvMap [data-s="{g}"]').click(); await asyncio.sleep(.5); await settle(.6)
            await asyncio.sleep(.8); await settle(1); await shot('25_cave_decoded'); await pg.locator('#cvNext').click(); await asyncio.sleep(.6); await settle(1)

            async def trial(o, a):
                await pg.locator('#cvReset').click()
                for k in o: await pg.locator(f'[data-set="ord"] [data-v="{k}"]').click()
                await pg.locator(f'[data-set="amt"] [data-v="{a}"]').click(); await pg.locator('#cvGo').click(); await asyncio.sleep(3.6); await settle(1)
            await trial(['shore', 'forest', 'valley'], 'big'); await trial(['forest', 'valley', 'shore'], 'big'); await trial(['forest', 'valley', 'shore'], 'small'); await shot('26_cave_won')
            await pg.locator('#cvNext').click(); await pump("(()=>{const e=document.getElementById('simDone');return !!e&&e.getClientRects().length>0})()", 80); await asyncio.sleep(1); await shot('27_simdone')
            await ev("document.getElementById('simDoneX').click()"); await pump("(()=>{const e=document.getElementById('cinema');return !!e&&e.getClientRects().length>0})()", 60); await asyncio.sleep(2)
            await ev("document.getElementById('cinemaSkip').click()"); await asyncio.sleep(1.5); await shot('28_end')
            await ev("document.getElementById('cinemaX')&&document.getElementById('cinemaX').click()"); await asyncio.sleep(3); await settle(); await shot('29_after_end'); await note('엔딩 뒤')

        for name, fn in [('0 조 선택', s_team), ('1 튜토리얼', s_tut), ('2 캠퍼스 기록1 → 1막', s_rec1), ('3 미션1', s_m1), ('4 미션2', s_m2), ('5 캠퍼스 기록2 → 2막', s_rec2), ('6 미션3', s_m3), ('7 캠퍼스 기록3 → 3막', s_rec3), ('8 미션4·엔딩', s_m4)]:
            if not await stage(name, fn): break
        print('ERRS', h.errs, h.bad)
        with open(os.path.join(OUT, 'transcript.txt'), 'w', encoding='utf-8') as f:
            last = None
            for st, k, t in LOG:
                if st != last: f.write('\n===== ' + st + ' =====\n'); last = st
                f.write(f'[{k}] {t}\n')
        print('lines', len(LOG))
asyncio.run(main())
