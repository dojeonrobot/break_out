# 2026-11-12 (사용자)
#  1) 「융합교육관」이라는 말을 없앤다: 보이드는 「특정 건물에서 반응하고 있어」라고만 하고, 「지금 네가 있는 건물」은 그대로. 카드 이름·설명에서도 건물 이름을 뺀다(지도의 건물 이름표는 그대로).
#  2) 시뮬레이터에서 카메라가 흐름을 따라가는 동안에는 흐름 위를 달리는 파동을 끈다(눈이 부심). 따라가기가 끝나면 다시 켠다.
import pathlib, json
R = pathlib.Path(__file__).resolve().parents[2]
p = R / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)
rep('{"id":"z1","name":"융합교육관","place":true,', '{"id":"z1","name":"캠퍼스 기록 1",')
rep('"brief":"융합교육관 건물 어딘가에 있는 물건을 한 바퀴 돌며 스캔해 기록을 채우세요."', '"brief":"지금 있는 건물 어딘가에 있는 물건을 한 바퀴 돌며 스캔해 기록을 채우세요."')
rep("return `그 자리를 트윈해 보니 융합교육관 쪽이었어. 좌표는 ${z && z.lat != null ? coordText(z) : '카드에 있는 좌표'}야. 지금 네가 있는 건물이지.`;",
    "return `그 자리를 트윈해 보니 특정 건물에서 반응하고 있어. 좌표는 ${z && z.lat != null ? coordText(z) : '카드에 있는 좌표'}야. 지금 네가 있는 건물이지.`;")
rep("setTimeout(()=> qPop('융합교육관'), 900);", "setTimeout(()=> qPop('지금 있는 건물'), 900);")
rep("const VEIN_U = {uTime:{value:0}};", "const VEIN_U = {uTime:{value:0}, uPulse:{value:1}};   /* uPulse: the running pulses, off while the camera chases the flow (user, 2026-11-12) */")
i = s.index("const veinShader = "); j = s.index("const VEIN = veinShader(", i); blk = s[i:j]
for a, b in [("uniforms:{uTime:VEIN_U.uTime, uColor:", "uniforms:{uTime:VEIN_U.uTime, uPulse:VEIN_U.uPulse, uColor:"), ("uniform float uTime, uAlpha;", "uniform float uTime, uAlpha, uPulse;"), ("pulse*0.45 + pulse2*0.25)", "(pulse*0.45 + pulse2*0.25)*uPulse)"), ("+ pulse*0.22)*uAlpha", "+ pulse*0.22*uPulse)*uAlpha")]:
    assert blk.count(a) == 1, a; blk = blk.replace(a, b)
s = s[:i] + blk + s[j:]
rep("function simFlyTick(t){\n", "function simFlyTick(t){\n  VEIN_U.uPulse.value += ((simFlyOn ? 0 : 1) - VEIN_U.uPulse.value)*0.1;\n")
p.write_bytes(s.encode('utf-8'))
p = R / 'docs/chapter05_script.md'; t = p.read_bytes().decode('utf-8')
a = '13. (캠퍼스로 전환, 융합교육관에 빛기둥) 첫 번째 좌표는 37.295655, 126.838475야. 지금 네가 있는 융합교육관이야.'; assert t.count(a) == 1
t = t.replace(a, '13. (섬, 하모니아로 카메라) 가장 먼저 복구할 곳은 하모니아 근처야.\n13-2. (캠퍼스로 전환, 지금 있는 건물에 빛기둥) 그 자리를 트윈해 보니 특정 건물에서 반응하고 있어. 좌표는 37.295655, 126.838475야. 지금 네가 있는 건물이지. (2026-11-12 사용자: 건물 이름은 말하지 않는다)')
p.write_bytes(t.encode('utf-8'))
m = pathlib.Path('C:/Users/dlgus/erica-twin/missions.json'); d = json.loads(m.read_text(encoding='utf-8'))
for x in d:
    if x['id'] == 'z1': x['name'] = '캠퍼스 기록 1'; x.pop('place', None); x['brief'] = '지금 있는 건물 어딘가에 있는 물건을 한 바퀴 돌며 스캔해 기록을 채우세요.'
m.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n'); print('ok')
