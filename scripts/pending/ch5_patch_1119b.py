# 2026-11-19 저녁: 위에서 본 시뮬레이터 시점의 눈부심·거리, 문양 회상 배치(코덱스는 오른쪽, 문양은 가운데: 왼쪽은 말하는 인물 자리), 관리자 기기에서 소리 버튼이 「관리자 모드」 알약과 겹치던 것.
# 한 번만 적용: python scripts/pending/ch5_patch_1119b.py
import pathlib
p = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8')
R = [("bloomPass.strength += ((simFlyOn ? 0.08 : 0.6) - bloomPass.strength)*0.1;", "bloomPass.strength += ((simFlyOn ? 0.08 : SIM_TOP ? 0.1 : 0.6) - bloomPass.strength)*0.1;"),
     ("/Math.min(1, camera.aspect)*1.12; return {pos:", "/Math.min(1, camera.aspect)*1.34; return {pos:"),
     ("#recall .cx{position:absolute;left:8vw;bottom:0;", "#recall .cx{position:absolute;right:5vw;bottom:0;"),
     ("transform:translateX(-3vw);transition:opacity 1.3s", "transform:translateX(3vw);transition:opacity 1.3s"),
     ("#recall .pt{position:absolute;right:10vw;top:46%;width:min(44vh,36vw);", "#recall .pt{position:absolute;left:50%;margin-left:calc(min(44vh,36vw) / -2);top:40%;width:min(44vh,36vw);"),
     ("@media (max-width:760px){#recall .cx{left:2vw;height:52vh}#recall .pt{right:6vw;top:30%;width:44vw}}", "@media (max-width:760px){#recall .cx{right:0;height:50vh}#recall .pt{left:28%;margin-left:-22vw;top:26%;width:44vw}}"),
     ("body.walk #sndBtn{top:calc(64px + env(safe-area-inset-top,0px))!important;bottom:auto!important;right:64px!important}", "body.walk #sndBtn{top:calc(64px + env(safe-area-inset-top,0px))!important;bottom:auto!important;right:64px!important}body.admkey #sndBtn{right:136px!important}body.walk.admkey #sndBtn{right:132px!important}")]
for a, b in R:
    assert s.count(a) == 1, (s.count(a), a[:50]); s = s.replace(a, b)
p.write_bytes(s.encode('utf-8')); print('ok', len(R))
