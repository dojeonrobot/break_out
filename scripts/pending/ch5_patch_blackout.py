# 2026-11-11 정전 연출(사용자: 전기가 안 들어왔는데 롤러코스터가 움직임): 예비 배전선을 잇기 전에는 구역 시계로 돌던 롤러코스터·관람차·회전목마·하모니아도 멈추고,
# 홀로그램 고목과 등대 불빛은 꺼지고, 범죄수사과 본부 톱니도 멈춘다. 전원이 들어오면 다른 기구와 같이 천천히 출발한다. 사파리(동물)는 전기와 무관해 그대로.
# 사용: python ch5_patch_blackout.py [사본경로]
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s
def swap(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)
swap("""  for(const id in RIDE){ const R = RIDE[id]; R.tau += R.s*dtF; }
  parkWakeTick(dtF);PARK_ON=parkPowerOn();if(PARK_ON)PARK_T+=dtF*(PARK_WAKE?PARK_WAKE.sp:1);else PARK_T=0;
""", """  parkWakeTick(dtF);PARK_ON=parkPowerOn();if(PARK_ON)PARK_T+=dtF*(PARK_WAKE?PARK_WAKE.sp:1);else PARK_T=0;
  for(const id in RIDE){ const R = RIDE[id]; R.tau += R.s*dtF*(id === 'dl-safari' ? 1 : PARK_ON ? (PARK_WAKE ? PARK_WAKE.sp : 1) : 0); }   /* no power, no ride: the zone clocks wait for the backup line too (2026-11-11) */
""")
swap("  islAnim.push(t=>{ holo.rotation.y = t*0.06;", "  poweredAnim(t=>{ holo.visible = PARK_ON || RIDE_PROBE; holo.rotation.y = t*0.06;")
swap("  islAnim.push(t=>{ beam.rotation.y = t*0.6; });", "  poweredAnim(t=>{ beam.visible = PARK_ON || RIDE_PROBE; beam.rotation.y = t*0.6; });")
swap("  islAnim.push(t=>{ gear.rotation.z = t*0.4;", "  poweredAnim(t=>{ gear.rotation.z = t*0.4;")
# the coaster train and the Splash River logs stepped a fixed 1/60 s per call whatever time they were handed, so they ran without power (and at frame-rate speed): step by the clock they are given
swap("  let u0 = 0;
  islAnim.push(t=>{
    const dt = 1/60; const sp", "  let u0 = 0, u0t = null;
  islAnim.push(t=>{
    const dt = Math.max(0, Math.min(0.1, t - (u0t ?? t))); u0t = t; const sp")
swap("  poweredAnim(t=>{
    let sMax = 0; const dt = 1/60;", "  let riverLogT = null;
  poweredAnim(t=>{
    let sMax = 0; const dt = Math.max(0, Math.min(0.1, t - (riverLogT ?? t))); riverLogT = t;")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
