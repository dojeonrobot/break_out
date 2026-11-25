"""사용자 1차 수정(docs/보이드의기록_동굴대사.md 1~3절, 2026-11-25)을 페이지 STORY에 반영: q3shake·q3cave·caveIn·mural1.
맞춤법만 고침(거예요, 모든 게, 생긴 거지, 하다 보니, 되새겨 주지, 동굴 속으로, 대상으로밖에)."""
import json, re, sys
p = 'C:/Users/dlgus/break_out/chapter05/index.html'
s = open(p, encoding='utf-8', newline='').read()
N = lambda t: {"who": "", "nar": True, "text": t}
W = lambda w, t: {"who": w, "text": t}
NEW = {
  "q3shake": [
    None,   # keep narration line as is
    W("제로", "네이티! 왜 그래?"),
    W("코덱스", "일루아가 더는 버티지 못하는군."),
    W("코덱스", "이대로 흔들리면 섬이 일루아를 붙잡지 못한다. 땅이 꺼지고, 이 섬은 바다 아래로 가라앉을 거다."),
    W("리코", "아니요! 저희가 그렇게 두지는 않을 거예요!"),
    W("리코", "저희가 수집한 스캔 기록으로 일루아를 환원하는 시뮬레이션을 돌려 봤어요."),
    W("제로", "저희의 시뮬레이션 결과로 일루아의 원래 자리를 모두 파악했어요! 조금씩 환원하면 섬이 이전처럼 돌아올 거예요!"),
  ],
  "q3cave": [
    W("코덱스", "시뮬레이션이라…… 연구라면 지긋지긋하다."),
    W("코덱스", "그때도 연구로 인해 모든 게 망가졌지. 너희의 선대들에게 연구를 맡기고 나서 섬은 급격히 나빠졌다."),
    W("코덱스", "그들은 일루아를 제멋대로 끌어다 썼다. 섬이 버티지 못할 때까지. 연구를 하다 보니 욕심이 생긴 거지."),
    W("코덱스", "그래서 너희를 믿을 수 없다."),
    W("코덱스", "따라와라. 너희 선대들의 과오를 다시 되새겨 주지. 이 동굴에는 그때 일이 벽화로 그대로 새겨져 있더군."),
    N("코덱스가 동굴 안으로 들어간다. 제로와 리코는 그 뒤를 따라 동굴 속으로 들어간다."),
  ],
  "caveIn": [
    N("끝없이 이어진 동굴 벽을 따라 벽화로 보이는 그림이 길게 이어져 있다. 군데군데 닳아서 무엇을 그렸는지 알 수 없다."),
    W("코덱스", "나의 선대는 이 동굴 벽에 우리의 일상을 기록했지."),
    W("제로", "보이드, 벽을 비춰 줄 수 있어?"),
    W("보이드", "응. 그런데 이 그림, 내 기록이랑 닮은 장면이 있어. 노아와 루나가 나한테 남긴 기록이야."),
    W("코덱스", "…… 비춰 봐라."),
  ],
  "mural1": [
    W("제로", "이건…… 큐브에서 봤던 그 장면이야. 토네이도에 휩쓸려서 우리 선대들이 섬에 왔던 날."),
    W("리코", "쓰러진 노아, 루나, 렌을 원류민들이 데려가고 있어."),
    W("코덱스", "그래. 그들은 우리를 도와준다는 명목하에 섬을 망가뜨렸다. 렌의 후손들은 망가진 섬을 연구할 대상으로밖에 여기지 않았고, 우리는 모두 이 터전을 잃었다."),
  ],
}
dec = json.JSONDecoder(); done = set()
for m in list(re.finditer(r'Object\.assign\(STORY, ', s))[::-1]:
    try:
        obj, end = dec.raw_decode(s, m.end())
    except ValueError:
        continue
    old_txt = s[m.end():end]
    if json.dumps(obj, ensure_ascii=False) != old_txt:
        continue   # not a plain json.dumps block; leave it
    hit = False
    for k, lines in NEW.items():
        if k in obj:
            cur = obj[k]
            if lines[0] is None:   # keep first original line
                if not cur or cur[0].get('who'):
                    sys.exit(f'{k}: first line is not narration')
                lines = [cur[0]] + lines[1:]
            # keep extra fields (img etc.) from matching speaker lines
            obj[k] = lines; done.add(k); hit = True
    if hit:
        s = s[:m.end()] + json.dumps(obj, ensure_ascii=False) + s[end:]
missing = set(NEW) - done
if missing:
    sys.exit(f'not found: {missing}')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok', sorted(done))
