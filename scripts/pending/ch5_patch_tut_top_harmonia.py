# 2026-11-12 (사용자)
#  1) 튜토리얼에서 대사 창이 위로 올라갈 때(「내 시점」·「보이드」 버튼 짚기) 보이드 그림이 대사 상자 뒤로 들어가 잘리던 것:
#     그림을 상자 아래쪽이 아니라 위쪽에 맞춰 세워, 글이 길어 상자가 커져도 그림이 가려지지 않게 한다.
#  2) 첫 좌표 앞에 「왜 하모니아부터인지」 한 단계 추가: 가장 먼저 복구할 곳은 하모니아 근처 → 트윈해 보니 융합교육관 쪽.
# 사용: python scripts/pending/ch5_patch_tut_top_harmonia.py   (한 번만)
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60]); s = s.replace(old, new)
rep('#voidVn[data-top="1"] img{height:min(150px,22vh)}',
    '#voidVn[data-top="1"] .in{padding-top:calc(min(150px,22vh) - 30px)}\n#voidVn[data-top="1"] img{top:0;bottom:auto;height:min(150px,22vh)}')
rep("""  {t:()=>{ const z = campusZone(1); return `첫 번째 좌표는 ${z && z.lat != null ? coordText(z) : '카드에 있는 좌표'}야. 지금 네가 있는 융합교육관이야.`; },pose:'say',world:'erica',""",
    """  {t:"가장 먼저 복구할 곳은 하모니아 근처야.",pose:'say',world:'island', do:()=>{ const m = MI.find(x=> x.id === 'dl-harmonia'), b = m && m.b; if(b) flyTo(new THREE.Vector3(b.cx + 95, G + 120, b.cz + 150), new THREE.Vector3(b.cx, G + 20, b.cz), 1400); }},
  {t:()=>{ const z = campusZone(1); return `그 자리를 트윈해 보니 융합교육관 쪽이었어. 좌표는 ${z && z.lat != null ? coordText(z) : '카드에 있는 좌표'}야. 지금 네가 있는 건물이지.`; },pose:'say',world:'erica',""")
rep("if(TUT_SPOT && tutStep < 12){", "if(TUT_SPOT && tutStep < 13){")
rep("if(f && tutStep === 17) tutSpot(f);", "if(f && tutStep === 18) tutSpot(f);")
P.write_bytes(s.encode('utf-8')); print('ok')
