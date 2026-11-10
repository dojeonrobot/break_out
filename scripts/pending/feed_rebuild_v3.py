# -*- coding: utf-8 -*-
"""도로그램 예시 게시물 전면 교체 (2026-11-10).
- 「사라진 섬」 소재 전부 제거. 실제 놀이공원 소식(방문객 기록, 신메뉴, 굿즈, 동물, 행사, 안전 점검, 분실물, 반려견)만.
- 모든 진짜/가짜는 chapter05/archive-data.js 의 문서와 짝. answer.doc = 대조할 문서 제목, answer.part = 거짓으로 쓴 곳.
- 실행: python scripts/pending/feed_rebuild_v3.py  → server/ch5_seed.json 을 새로 쓴다. 사진은 server/ch5_make_seed_images_free.py 로.
"""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
SEED = ROOT / 'server' / 'ch5_seed.json'
ARC = ROOT / 'chapter05' / 'archive-data.js'

# 자료실 문서 제목 (id → title) 을 archive-data.js 에서 읽어 오타를 막는다
src = ARC.read_text(encoding='utf-8')
DOC = dict(re.findall(r"id: '([\w-]+)', type: '\w+', title: '([^']+)'", src))
assert len(DOC) >= 28, len(DOC)

# ---------- 계정 ----------
DOROILBO = lambda reporter: {"name": "도로일보", "handle": "@doroilbo", "kind": "press", "verified": True, "joined": "2009.07", "followers": "8.7만", "posts": "41,230", "bio": "도로랜드와 항구 도시 소식을 가장 빠르게.", "color": "#0f766e", "reporter": reporter}
SEOHAE = lambda reporter: {"name": "서해바다신문", "handle": "@seohaenews", "kind": "press", "verified": True, "joined": "2011.03", "followers": "4.2만", "posts": "18,204", "bio": "서해안 항구 도시의 지역 신문. 바다·항구·섬 소식을 전합니다.", "color": "#1d4ed8", "reporter": reporter}
OFFICIAL = {"name": "도로랜드 운영실", "handle": "@doroland", "kind": "official", "verified": True, "joined": "2015.04", "followers": "15.3만", "posts": "3,812", "bio": "바다 위 놀이공원 도로랜드의 유일한 공식 계정 🎡 매일 10:00~19:00", "color": "#0e4a84"}
COASTER = {"name": "롤코타는남자", "handle": "@coaster_guy", "kind": "creator", "verified": True, "joined": "2017.02", "followers": "112만", "posts": "1,384", "bio": "전국 롤러코스터 다 타 봄. 도로랜드와 관계없는 개인 채널", "color": "#dc2626"}
def press_fake(name, handle, joined, followers, posts, bio, color, reporter=''):
    return {"name": name, "handle": handle, "kind": "press", "verified": False, "joined": joined, "followers": followers, "posts": posts, "bio": bio, "color": color, "reporter": reporter}
def person(name, handle, joined, followers, posts, bio, color, kind='person'):
    return {"name": name, "handle": handle, "kind": kind, "verified": False, "joined": joined, "followers": followers, "posts": posts, "bio": bio, "color": color}

def cm(*rows): return [{"name": n, "text": t, "likes": l, "time": tm} for n, t, l, tm in rows]

def news(id, author, title, subhead, body, quote, stats, images, truth, doc, explain, part='', clue='', tactic='', place='도로랜드', postedAt='어제', photoTakenAt='어제', views='4.1만', commentCount=120, comments=None, tags=''):
    return {"id": id, "format": "news", "author": author, "title": title, "subhead": subhead, "body": body,
            "quote": ({"text": quote[0], "who": quote[1]} if quote else None), "stats": [{"label": l, "value": v} for l, v in stats], "tags": tags, "place": place,
            "postedAt": postedAt, "editedAt": "", "photoTakenAt": photoTakenAt, "views": views, "commentCount": commentCount, "comments": comments or [],
            "images": images, "secret": secret(truth, doc, part, clue, tactic), "answer": answer(truth, doc, part, explain)}
def shorts(id, author, title, scenes, images, truth, doc, explain, part='', clue='', tactic='', tags='', place='도로랜드', postedAt='어제', photoTakenAt='어제', likes='1.2만', views='18만', commentCount=240, music=None, comments=None):
    return {"id": id, "format": "shorts", "author": author, "title": title, "body": "\n\n".join(t for _, t in scenes), "scenes": [{"img": i, "text": t} for i, t in scenes],
            "tags": tags, "place": place, "postedAt": postedAt, "photoTakenAt": photoTakenAt, "likes": likes, "views": views, "commentCount": commentCount,
            "music": music or (author["name"] + " · 원본 오디오"), "comments": comments or [], "images": images, "secret": secret(truth, doc, part, clue, tactic), "answer": answer(truth, doc, part, explain)}
def story(id, author, slides, images, truth, doc, explain, part='', clue='', tactic='', place='도로랜드', postedAt='3시간 전', photoTakenAt='3시간 전', views='84'):
    return {"id": id, "format": "story", "author": author, "title": "", "body": "\n\n".join(s["text"] for s in slides), "slides": slides, "tags": "", "place": place,
            "postedAt": postedAt, "photoTakenAt": photoTakenAt, "likes": "", "views": views, "images": images, "secret": secret(truth, doc, part, clue, tactic), "answer": answer(truth, doc, part, explain)}
def sl(img, text, time='3시간 전', sticker=None):
    s = {"img": img, "text": text, "time": time}
    if sticker: s["sticker"] = sticker
    return s
PART_KIND = {'제목': 'title', '부제': 'subhead', '본문': 'body', '숫자 상자': 'stats', '인용': 'quote', '계정': 'account', '시간·날짜': 'time'}
PART_CRIT = {'account': 'who', 'time': 'when'}
def secret(truth, doc, part, clue, tactic):
    if truth == 'real':
        return {"truth": "real", "tactic": "", "clue": DOC[doc], "clueCriterion": "cross", "clueKind": "", "fact": DOC[doc]}
    k = PART_KIND[part]
    return {"truth": "fake", "tactic": tactic, "clue": clue, "clueCriterion": PART_CRIT.get(k, 'cross'), "clueKind": k, "fact": DOC[doc]}
def answer(truth, doc, part, explain):
    a = {"truth": truth, "explain": explain, "doc": DOC[doc]}
    if part: a["part"] = part
    return a

P = []
# ======================= 기사 22개 (진짜 12 · 가짜 10) =======================
P += [
news('n-million', DOROILBO('서하늘'), '도로랜드 올해 방문객 100만 명 돌파… 100만 번째는 "관람차 타러 온 네 식구"', '9일 오후 2시 10분 배로 입장… 지난해보다 3주 빨라, 운영실 "연말 130만 명 예상"',
  '도로랜드의 올해 누적 방문객이 9일 100만 명을 넘었다. 운영실은 9일 오후 2시 10분 항구에서 들어온 배의 승객 가운데 부모와 초등학생 둘로 이루어진 네 식구가 100만 번째 방문객이 됐다고 밝혔다.\n\n운영실은 이 가족에게 연간회원권 4장과 기린 인형 4개를 선물했다. 기념 사진은 회전목마 앞 광장에서 찍었다. 아버지는 "관람차 한 번 타러 왔다가 1년 치 입장권을 받았다"고 말했다.\n\n지난해에는 10월 30일에 100만 명을 넘었으니 올해가 3주 빠르다. 운영실은 "가을 주말마다 하루 8천 명 넘게 찾고 있어 연말에는 130만 명을 넘길 것 같다"고 했다.',
  ('관람차 한 번 타러 왔다가 1년 치 입장권을 받았어요.', '100만 번째 방문객 가족'), [('올해 누적', '100만 명'), ('지난해 돌파일', '10월 30일'), ('선물', '연간회원권 4장')],
  {"main": "family of four holding ferris wheel shaped balloons in front of a white seaside ferris wheel, bright afternoon, seen from behind"},
  'real', 'press-million', '진짜 기사입니다. 100만 번째 방문객(10월 9일 오후 2시 10분, 네 식구, 연간회원권 4장·기린 인형)과 지난해 돌파일 10월 30일이 보도자료와 맞고, 도로일보는 등록 언론사입니다.',
  postedAt='3일 전', photoTakenAt='3일 전', views='9.2만', commentCount=640, comments=cm(('연간권있는사람', '기린 인형까지 주는 거 부럽다', 410, '3일 전'), ('도로일보독자', '지난해보다 3주 빠르다니 진짜 많이 왔네', 150, '2일 전'))),
news('n-million-fake', DOROILBO('한바다'), '도로랜드, 이번 달에만 100만 명 방문… 개장 이래 최고 기록', '10월 1일부터 9일까지 9일 만에 100만 명, 하루 평균 11만 명… 운영실 "배 증편 검토"',
  '도로랜드가 10월 들어 9일 만에 방문객 100만 명을 모았다. 하루 평균 11만 명이 섬을 찾은 셈이다. 운영실은 9일 오후 2시 10분 입장한 네 식구가 이달 100만 번째 방문객이라고 밝혔다.\n\n운영실은 이 가족에게 연간회원권 4장과 기린 인형 4개를 선물했다. 지난해 10월 한 달 방문객이 12만 명이었던 것과 비교하면 여덟 배가 넘는 숫자다.\n\n운영실 관계자는 "배 두 척으로는 감당이 어려워 증편을 검토하고 있다"고 말했다.',
  ('배 두 척으로는 감당이 어려워 증편을 검토하고 있습니다.', '운영실 관계자'), [('이달 방문객', '100만 명'), ('하루 평균', '11만 명')],
  {"main": "very long queue of visitors at a harbor ferry terminal in the morning, seaside amusement park ferris wheel far in the background"},
  'fake', 'stat-monthly', '가짜입니다. 100만 명은 「이달」이 아니라 「올해 누적」입니다. 월별 방문객 통계에 10월 1~9일은 8만 3천 명이고, 하루 평균 11만 명은 배 두 척이 하루에 나를 수 있는 인원(520명 × 20회)으로도 불가능합니다. 등록 언론사(도로일보)가 낸 오보입니다.',
  part='제목', clue='올해 누적 100만 명을 「이번 달에만 100만 명」으로 바꿔 씀. 10월 1~9일 방문객은 8만 3천 명.', tactic='숫자 부풀리기', postedAt='3일 전', photoTakenAt='3일 전', views='12.4만', commentCount=980, comments=cm(('계산해봄', '9일에 100만이면 하루 11만인데 배가 520명씩 20번이면 1만 명… 뭔가 이상한데', 1200, '3일 전'), ('도로일보독자', '다른 기사엔 올해 누적이라고 써 있는데요?', 640, '2일 전'))),
news('n-drone', SEOHAE('정해솔'), '관람차 위에 뜬 드론 500대… 도로랜드 15주년 라이트쇼 첫 시연에 항구 2,100명', '8일 저녁 8시, 15분 동안 관람차·배·기린 그려… 추락·사고 없어, 본 공연은 내년 5월 5일',
  '도로랜드가 개장 15주년 기념 드론 라이트쇼를 8일 저녁 8시 처음 시연했다. 드론 500대가 관람차 위 바다 상공에서 15분 동안 관람차, 배, 기린 모양을 차례로 그렸고 항구 광장에는 2,100명이 모였다.\n\n쇼는 항구에서 바다 건너로 보는 방식이라 입장권이나 좌석이 없다. 운영실은 "드론 추락이나 사고는 한 건도 없었다"고 밝혔다.\n\n본 공연은 내년 5월 5일 저녁 8시 같은 자리에서 한다. 섬에서 나오는 막배는 그날도 오후 7시 30분이라 섬 안에서는 볼 수 없다.',
  ('드론 추락이나 사고는 한 건도 없었습니다.', '도로랜드 운영실'), [('드론', '500대'), ('관람 인원', '2,100명'), ('본 공연', '내년 5월 5일')],
  {"main": "hundreds of drone lights forming a giant ferris wheel shape in the night sky above the sea, crowd silhouettes at a harbor plaza"},
  'real', 'press-drone', '진짜 기사입니다. 드론 500대, 15분, 항구 2,100명, 사고 없음, 본 공연 내년 5월 5일이 모두 드론 라이트쇼 보도자료와 맞습니다.',
  postedAt='4일 전', photoTakenAt='4일 전', views='7.8만', commentCount=520, place='항구 광장'),
news('n-dronecrash', press_fake('항구뉴스24', '@harbor_news24', '2026.09', '1,820', '37', '항구와 섬 소식을 24시간 전합니다', '#be123c'), '[속보] 도로랜드 드론쇼 중 드론 120대 바다에 추락… 관람객 긴급 대피', '배터리 결함 추정, 운영실은 침묵… "15주년 본 공연 취소 검토"',
  '8일 저녁 도로랜드 드론 라이트쇼 시연 도중 드론 120대가 한꺼번에 바다로 떨어졌다. 항구 광장에 모인 관람객 2,100명은 긴급 대피했고 일부는 넘어져 다친 것으로 알려졌다.\n\n추락 원인은 배터리 결함으로 추정된다. 한 관계자는 "500대 가운데 4분의 1이 떨어졌다"고 전했다.\n\n운영실은 아직 공식 입장을 내지 않았다. 내년 5월 5일 본 공연도 취소를 검토 중인 것으로 알려졌다.',
  ('500대 가운데 4분의 1이 떨어졌습니다.', '한 관계자'), [('추락 드론', '120대'), ('관람 인원', '2,100명')],
  {"main": "dark sea surface at night with small scattered lights floating on the water near a harbor, blurry, dramatic"},
  'fake', 'press-drone', '가짜입니다. 드론 라이트쇼 보도자료에 「추락 0대, 부상 0명」이 있습니다. 드론 500대·관람객 2,100명 같은 맞는 숫자를 섞었고, 항구뉴스24는 등록 계정부에 없는 매체이며 이름 없는 「관계자」만 나옵니다.',
  part='본문', clue='보도자료에는 추락 0대·사고 없음인데 드론 120대 추락으로 씀.', tactic='감정 자극', postedAt='4일 전', photoTakenAt='4일 전', views='21만', commentCount=1400, place='항구 광장', comments=cm(('현장에있던사람', '저 어제 항구에 있었는데 떨어진 거 하나도 없었어요', 2100, '3일 전'), ('ㅇㅇ', '사진이 왜 이렇게 흐려요', 300, '3일 전'))),
news('n-giraffe', SEOHAE('정해솔'), '도로랜드 사파리에 아기 기린 탄생… 이름 공모 사흘 만에 4,800건', '4일 새벽 태어나 키 1.8m·62kg… 공모는 @doroland 댓글로 이달 31일까지, 당첨 1명에 연간회원권',
  '도로랜드 사파리에서 4일 토요일 새벽 3시 40분 아기 기린이 태어났다. 태어날 때 키는 1.8m, 몸무게는 62kg이었다. 어미 「하늘」과 새끼 모두 건강하다고 사파리 사육팀은 밝혔다.\n\n운영실이 공식 계정 @doroland 게시물 댓글로 이름 공모를 시작하자 사흘 만에 4,800건이 들어왔다. 공모는 31일까지이고 당첨자 1명에게 연간회원권 1장을 준다. 이름은 11월 초에 발표한다.\n\n아기 기린은 지프 투어 코스에서 볼 수 있다. 사육팀은 "창문 밖으로 손을 내밀거나 먹이를 주면 안 된다"고 당부했다. 도로랜드 기린은 이번 탄생으로 5마리가 됐다.',
  ('어미도 새끼도 건강합니다. 창문 밖으로 손을 내밀지만 말아 주세요.', '사파리 사육팀'), [('키', '1.8m'), ('이름 공모', '4,800건'), ('기린', '5마리')],
  {"main": "baby giraffe standing next to its mother in a safari park, morning light, seen from a jeep window"},
  'real', 'press-giraffe', '진짜 기사입니다. 출생일(10월 4일 새벽), 키 1.8m·62kg, 공모 4,800건(6~8일), 당첨 1명, 기린 5마리가 아기 기린 보도자료와 맞습니다.',
  postedAt='4일 전', photoTakenAt='4일 전', views='6.3만', commentCount=730, place='사파리', comments=cm(('기린팬', "이름 '도로미' 냈어요 뽑아 주세요", 820, '4일 전'), ('동물원덕후', '제 쇼츠에서 본 기린이 엄마였군요🦒', 410, '3일 전'))),
news('n-giraffe-name', press_fake('바다경제', '@sea_economy', '2026.08', '3,410', '58', '서해안 경제 뉴스', '#7c3aed'), '도로랜드 아기 기린 이름 「도도」로 확정… 공모 1만 건 넘자 조기 마감', '운영실 "너무 많이 들어와 8일에 마감"… 당첨자 10명에게 연간회원권',
  '도로랜드 사파리 아기 기린의 이름이 「도도」로 정해졌다. 운영실은 이름 공모에 1만 2천 건이 들어오자 예정보다 일찍 8일에 공모를 마감하고 가장 많이 나온 이름을 골랐다고 밝혔다.\n\n「도도」를 낸 사람 가운데 10명을 뽑아 연간회원권을 준다. 당첨자는 이번 주 안에 발표된다.\n\n아기 기린은 4일 새벽 태어났으며 키 1.8m, 몸무게 62kg이다.',
  None, [('공모 접수', '1만 2천 건'), ('당첨', '10명')],
  {"main": "a baby giraffe close up with a small wooden name sign hanging on a fence, blurred, no readable text"},
  'fake', 'press-giraffe', '가짜입니다. 아기 기린 보도자료에 공모는 10월 31일까지, 접수는 사흘 4,800건, 당첨 1명, 이름 발표는 11월 초라고 되어 있습니다. 바다경제는 등록 계정부에 없는 매체입니다.',
  part='제목', clue='공모가 31일까지 진행 중인데 「도도로 확정·조기 마감」으로 씀. 접수 4,800건을 1만 2천 건, 당첨 1명을 10명으로.', tactic='숫자 부풀리기', postedAt='2일 전', photoTakenAt='4일 전', views='3.9만', commentCount=260, place='사파리'),
news('n-popup', DOROILBO('서하늘'), '항구에 15주년 굿즈 팝업… 새벽 5시 20분부터 줄, 키링은 11시 5분에 매진', '엽서 세트 하루 1,200개 매진 행진, 키링은 1인 2개 제한… 31일까지 매일 10시~20시',
  '도로랜드 운영실이 항구 광장에 연 15주년 굿즈 팝업스토어가 사흘째 매진을 이어가고 있다. 관람차 엽서 세트(3,000원)는 하루 1,200세트가 매일 다 팔렸고, 관람차 키링(8,000원)은 하루 400개가 첫날 낮 12시 10분, 둘째 날 오전 11시 40분, 셋째 날 오전 11시 5분에 동났다.\n\n첫날은 새벽 5시 20분부터 줄이 섰고 문을 연 오전 10시에는 줄 길이가 약 200m였다. 키링은 1인 2개까지만 살 수 있다.\n\n팝업스토어는 31일까지 매일 오전 10시부터 오후 8시까지 열며 입장권이 없어도 살 수 있다.',
  ('키링 사려고 새벽 5시에 왔어요. 2개 제한이라 친구 것까지는 못 샀어요.', '방문객 (고등학생)'), [('엽서 세트', '하루 1,200'), ('키링', '하루 400'), ('첫날 줄', '약 200m')],
  {"main": "long morning queue of young people in front of a white pop-up store tent at a harbor plaza, ferris wheel across the sea"},
  'real', 'press-popup', '진짜 기사입니다. 엽서 하루 1,200세트, 키링 하루 400개와 매진 시각(12:10·11:40·11:05), 1인 2개 제한, 첫날 새벽 5시 20분·줄 200m가 팝업스토어 보도자료 표와 맞습니다.',
  postedAt='2일 전', photoTakenAt='2일 전', views='5.5만', commentCount=410, place='항구 광장'),
news('n-popup-fake', press_fake('도로일보', '@doroilbo_news', '2026.09', '640', '12', '도로랜드 소식 속보 채널', '#0f766e', '한바다'), '[단독] 팝업 키링 하루 3,000개씩 팔려… 사흘 매출 7,200만 원', '엽서는 하루 1,200세트… 운영실 "키링 생산 라인 두 배로"',
  '항구 광장 15주년 굿즈 팝업스토어의 관람차 키링이 하루 3,000개씩 팔리고 있다. 8,000원짜리 키링이 사흘 동안 9,000개 팔려 매출만 7,200만 원이다.\n\n엽서 세트는 하루 1,200세트가 매진됐다. 운영실 관계자는 "키링 생산 라인을 두 배로 늘렸다"고 밝혔다.\n\n팝업스토어는 31일까지 매일 오전 10시부터 오후 8시까지 연다.',
  ('키링 생산 라인을 두 배로 늘렸습니다.', '운영실 관계자'), [('키링 하루 판매', '3,000개'), ('사흘 매출', '7,200만 원')],
  {"main": "display table full of small ferris wheel keyrings in a pop-up store, close up, soft light"},
  'fake', 'press-popup', '가짜입니다. 팝업스토어 보도자료 표에 키링은 하루 400개 한정이고 1인 2개 제한입니다. 엽서 1,200세트 같은 맞는 숫자를 섞었고, 계정 @doroilbo_news는 등록 계정부의 사칭 신고 계정입니다(진짜 도로일보는 @doroilbo).',
  part='숫자 상자', clue='키링 하루 400개 한정을 3,000개로 부풀림. 계정도 도로일보 사칭.', tactic='사칭', postedAt='어제', photoTakenAt='2일 전', views='8.1만', commentCount=330, place='항구 광장', comments=cm(('굿즈수집러', '400개 한정이라 11시면 끝나는데 3,000개가 어디서 나와요', 540, '어제'),)),
news('n-ferry-guide', person('섬여행 노트', '@island_note', '2021.05', '2,140', '318', '주말마다 섬 하나씩. 배 시간표 정리 전문', '#0369a1'), '도로랜드 가는 배 시간표 총정리: 매시 정각 출발, 25분, 막배는 7시 30분', '처음 가는 사람이 가장 많이 묻는 것… 주말은 30분 간격, 배 요금은 입장권에 포함',
  '도로랜드에 처음 가는 사람이 가장 많이 묻는 게 배 시간이다. 항구에서 섬으로 가는 배는 오전 9시부터 오후 6시까지 매시 정각에 출발하고 주말에는 30분 간격으로 늘어난다.\n\n섬에서 항구로 돌아오는 배는 오전 10시 30분부터 매시 30분에 있고 막배는 오후 7시 30분이다. 도로1호와 도로2호 두 척이 번갈아 다니며 한 번에 520명이 타고 25분 걸린다.\n\n배 요금은 따로 없다. 입장권에 포함되어 있다. 항구 주차장은 1,200면이고 하루 5,000원이다.',
  None, [('항구 → 섬', '매시 정각'), ('막배', '오후 7시 30분'), ('소요', '25분')],
  {"main": "white passenger ferry leaving a harbor pier on a calm sunny morning, island with ferris wheel in the distance"},
  'real', 'hours-ferry', '진짜입니다. 배 시간(매시 정각·30분, 주말 30분 간격), 막배 7시 30분, 520명·25분이 운영 시간과 배 시간표 문서와 맞습니다. 인증 배지 없는 개인 블로그 계정이지만 내용이 자료실과 맞으면 진짜입니다.',
  postedAt='5일 전', photoTakenAt='5일 전', views='2.7만', commentCount=96, place='항구'),
news('n-nightopen', press_fake('꿀팁생활', '@honeytip_life', '2026.07', '9,870', '210', '생활 꿀팁·할인 정보', '#ea580c'), '도로랜드 11월부터 야간 개장… 막배 밤 9시로 연장', '폐장 오후 9시로 두 시간 늘려, 관람차 야간 조명도 미리 점등… "가을 밤바다 보러 오세요"',
  '도로랜드가 11월 1일부터 야간 개장을 시작한다. 폐장 시간이 오후 7시에서 9시로 두 시간 늘고 섬에서 나오는 막배도 밤 9시 30분으로 바뀐다.\n\n관람차에 설치 중인 조명 1만 2천 개도 11월부터 미리 켠다. 운영실은 "가을 밤바다를 관람차에서 보라"고 홍보할 계획이다.\n\n야간 입장권은 어른 3만 원으로 따로 판다.',
  None, [('폐장', '오후 9시'), ('막배', '밤 9시 30분')],
  {"main": "seaside ferris wheel lit at dusk with warm lights, calm sea, long exposure"},
  'fake', 'hours-ferry', '가짜입니다. 운영 시간 문서에 「야간 개장은 하지 않는다, 막배 오후 7시 30분」이 있고, 관람차 조명 보도자료에 점등식은 내년 5월 5일이라고 되어 있습니다. 운영실 공지에도 야간 개장 없음이 정리되어 있습니다. 꿀팁생활은 등록 계정부에 없는 매체입니다.',
  part='시간·날짜', clue='야간 개장 없음·막배 7시 30분을 「폐장 9시·막배 9시 30분」으로 바꿈.', tactic='없는 혜택', postedAt='어제', photoTakenAt='3일 전', views='6.6만', commentCount=410),
news('n-pets', SEOHAE('정해솔'), '도로랜드, 반려견 동반 입장 시범 운영… 10kg 이하·유모차 태우면 하루 50마리', '11월 30일까지 두 달… 사파리·공연장·놀이기구는 제외, 동반 요금 없음',
  '도로랜드가 1일부터 11월 30일까지 반려견 동반 입장을 시범 운영한다. 10kg 이하 반려견을 반려견 유모차나 가방에 태운 경우에만 되고, 하루 50마리까지 항구 매표소에서 접수한다. 동반 요금은 없다.\n\n사파리 지프 투어와 하모니아 공연장에는 들어갈 수 없고 놀이기구에도 함께 탈 수 없다. 운영실은 "동물들이 놀라지 않도록 사파리는 제외했다"고 설명했다.\n\n첫 주에는 하루 평균 31마리가 들어왔고 가장 많이 온 견종은 말티즈였다.',
  ('동물들이 놀라지 않도록 사파리는 제외했습니다.', '도로랜드 운영실'), [('조건', '10kg 이하'), ('하루 접수', '50마리')],
  {"main": "small white dog sitting in a pet stroller in front of a carousel at an amusement park, sunny day"},
  'real', 'press-pets', '진짜 기사입니다. 기간, 10kg 이하·유모차, 하루 50마리, 요금 없음, 사파리·공연장·놀이기구 제외가 반려견 동반 보도자료와 맞습니다.',
  postedAt='6일 전', photoTakenAt='6일 전', views='4.4만', commentCount=380, place='중앙 광장'),
news('n-pets-safari', SEOHAE('정해솔'), '도로랜드 사파리 지프에도 반려견 동반 허용… "기린과 강아지가 눈 맞춰"', '반려견 시범 운영 범위 넓혀… 10kg 이하 가방에 태우면 지프 투어 가능',
  '도로랜드가 반려견 동반 시범 운영 범위를 사파리 지프 투어까지 넓혔다. 10kg 이하 반려견을 가방에 태우면 40분 지프 투어에 함께 탈 수 있다.\n\n운영실은 "첫 주 반응이 좋아 범위를 넓혔다"고 밝혔다. 하루 접수는 50마리 그대로이고 동반 요금은 없다.\n\n하모니아 공연장과 놀이기구 탑승은 여전히 안 된다.',
  ('첫 주 반응이 좋아 범위를 넓혔습니다.', '도로랜드 운영실'), [('지프 투어', '동반 가능'), ('하루 접수', '50마리')],
  {"main": "safari jeep driving past zebras, a small dog carrier bag visible on the seat, afternoon light"},
  'fake', 'press-pets', '가짜입니다. 반려견 동반 보도자료에 사파리 지프 투어는 「출입 불가」로 되어 있고 범위를 넓혔다는 문서는 없습니다. 인증 배지가 있는 등록 언론사가 낸 오보라서 계정만 보면 못 찾고, 문서와 대조해야 찾습니다. 정정 보도가 따로 나왔습니다.',
  part='본문', clue='사파리 지프 투어 출입 불가인데 「허용」으로 씀.', tactic='가짜 전문가', postedAt='3일 전', photoTakenAt='6일 전', views='5.1만', commentCount=290, place='사파리'),
news('n-pets-correction', SEOHAE('정해솔'), '[정정] 「사파리 지프에도 반려견 동반 허용」 기사는 사실과 다릅니다', '반려견은 사파리·공연장·놀이기구에 들어갈 수 없음… 운영실 확인 없이 보도한 점 사과',
  '본지는 3일 전 기사에서 도로랜드가 반려견 동반 범위를 사파리 지프 투어까지 넓혔다고 보도했습니다. 확인 결과 반려견은 사파리 지프 투어, 하모니아 공연장, 놀이기구에 들어갈 수 없으며 운영실에 범위를 넓힐 계획도 없었습니다.\n\n해당 기사는 운영실 확인을 거치지 않고 제보 내용을 그대로 실은 것입니다. 독자 여러분께 사과드립니다.\n\n반려견 동반 시범 운영은 11월 30일까지이며 10kg 이하, 유모차나 가방, 하루 50마리 조건은 그대로입니다.',
  None, [('출입 불가', '사파리·공연장·놀이기구'), ('조건', '10kg 이하')],
  {"main": "newspaper correction notice concept, safari park entrance gate with a no-pets pictogram sign, no readable text"},
  'real', 'press-pets', '진짜 기사입니다. 정정 내용(사파리·공연장·놀이기구 출입 불가, 10kg 이하·하루 50마리)이 반려견 동반 보도자료와 맞습니다. 등록 언론사는 틀린 기사를 내면 정정 보도를 냅니다.',
  postedAt='어제', photoTakenAt='어제', views='2.2만', commentCount=140),
news('n-lostfound', DOROILBO('한바다'), '도로랜드 분실물 센터 상반기 3,412건… 선글라스 412개, 틀니 3점, 거북이 1마리', '주인 찾은 비율 61%… 거북이는 바이킹 앞 벤치에서 발견돼 당일 저녁 집으로',
  '도로랜드 분실물 센터에 올해 상반기 들어온 물건은 3,412건이고 그중 61%인 2,081건이 주인에게 돌아갔다. 가장 많이 잃어버리는 물건은 선글라스(412건)였고 모자(388건), 우산(240건)이 뒤를 이었다.\n\n눈에 띄는 분실물도 있었다. 틀니 3점 가운데 2점은 주인을 찾았고, 반려 거북이 1마리는 바이킹 앞 벤치에서 발견돼 당일 저녁 주인에게 돌아갔다. 아동 신발 한 짝은 64건이었다.\n\n분실물 센터는 중앙 광장 안내소 안에 있고 3개월 동안 보관한다.',
  ('거북이는 벤치 밑에서 아주 천천히 걷고 있었어요. 주인분이 울면서 데려가셨어요.', '고객지원팀 분실물 담당'), [('상반기 분실물', '3,412건'), ('주인 찾음', '61%'), ('선글라스', '412건')],
  {"main": "lost and found counter shelf with many sunglasses and caps neatly arranged, a small turtle terrarium on the side, bright indoor light"},
  'real', 'press-lostfound', '진짜 기사입니다. 3,412건, 61%, 선글라스 412·모자 388·우산 240, 틀니 3점(2점 반환), 거북이 1마리가 분실물 보도자료 표와 맞습니다. 황당해 보여도 자료실에 있으면 진짜입니다.',
  postedAt='4일 전', photoTakenAt='4일 전', views='11.3만', commentCount=1500, place='중앙 광장 안내소', comments=cm(('ㅋㅋㅋ', '틀니를 어떻게 잃어버리지', 3100, '4일 전'), ('거북이주인', '저희 거북이예요… 바이킹 타는 동안 가방에서 나갔어요 감사합니다', 5400, '3일 전'))),
news('n-crocodile', press_fake('세상에이런일이', '@wow_news_kr', '2026.06', '2.4만', '512', '세상의 신기한 소식을 전합니다', '#b45309'), '도로랜드 분실물 센터에 새끼 악어 신고… 주인 안 나타나 사파리로', '선글라스·모자 다음으로 많은 분실물은 "반려동물"… 올해만 거북이 1마리, 악어 1마리',
  '도로랜드 분실물 센터에 지난달 새끼 악어가 들어왔다. 길이 40cm의 새끼 악어는 바이킹 앞 벤치에서 발견됐고 주인이 나타나지 않아 사파리에서 키우기로 했다.\n\n센터 관계자는 "올해 상반기에만 반려동물이 두 마리 들어왔다"고 말했다. 거북이는 당일 주인을 찾았다.\n\n분실물 센터는 중앙 광장 안내소 안에 있다.',
  ('올해 상반기에만 반려동물이 두 마리 들어왔습니다.', '센터 관계자'), [('새끼 악어', '40cm'), ('반려동물 분실', '2마리')],
  {"main": "small baby crocodile on a wooden bench in a park, blurry background, sensational framing"},
  'fake', 'press-lostfound', '가짜입니다. 분실물 보도자료 상위 10 표에 반려 거북이 1마리는 있지만 악어는 없고, 사파리 동물 현황 문서에 악어는 「0, 없음」입니다. 거북이·바이킹 앞 벤치 같은 진짜 세부를 섞었습니다.',
  part='제목', clue='분실물 표에 없는 「새끼 악어」를 넣음. 거북이 1마리는 진짜.', tactic='감정 자극', postedAt='2일 전', photoTakenAt='2일 전', views='15.2만', commentCount=900, place='중앙 광장 안내소'),
news('n-wheel-stop', DOROILBO('서하늘'), '도로랜드 관람차 11분 정지… 탑승객 48명 전원 안전하게 하차', '7일 오후 2시 14분 캐빈 문 센서 오류, 부상자 없어… 재탑승권 지급 후 오후 4시 정상 운행',
  '도로랜드 관람차가 7일 오후 2시 14분 멈췄다가 11분 만에 다시 움직였다. 운영실은 캐빈 문 센서 한 개가 오류를 일으켜 안전장치가 작동했다고 밝혔다.\n\n정지 당시 캐빈에 타고 있던 48명은 2시 25분 재가동 뒤 모두 안전하게 내렸고 다친 사람은 없다. 운영실은 48명에게 재탑승권을 줬다.\n\n센서를 교체한 뒤 당일 오후 4시부터 정상 운행했다. 관람차는 높이 88m, 캐빈 36개로 한 바퀴 도는 데 14분이 걸린다.',
  ('센서가 먼저 멈추도록 되어 있어서 멈춘 겁니다. 안전장치가 제대로 일한 거예요.', '시설안전팀장'), [('정지 시간', '11분'), ('탑승객', '48명'), ('부상', '0명')],
  {"main": "white ferris wheel against a cloudy sky with a maintenance worker in a safety vest at the base platform, seen from a distance"},
  'real', 'record-wheel-stop', '진짜 기사입니다. 7일 오후 2시 14분, 11분, 센서 오류, 48명·부상 0, 재탑승권, 오후 4시 재개가 관람차 정지 운영 기록과 맞습니다.',
  postedAt='4일 전', photoTakenAt='4일 전', views='6.9만', commentCount=450),
news('n-wheel-stop-fake', DOROILBO('한바다'), '도로랜드 관람차 공중에 2시간 멈춰… 승객 120명 사다리차로 구조', '7일 오후 전기 계통 고장, 어린이 3명 탈진… 운영실 "원인 조사 중"',
  '도로랜드 관람차가 7일 오후 2시 14분 멈춰 2시간 동안 움직이지 않았다. 캐빈 36개에 나눠 타고 있던 승객 120명은 소방 사다리차로 한 명씩 내려왔고 어린이 3명이 탈진 증세를 보였다.\n\n운영실은 전기 계통 고장으로 보고 원인을 조사 중이라고 밝혔다. 관람차는 이번 주말까지 운행하지 않는다.\n\n관람차는 높이 88m로 한 바퀴 도는 데 14분이 걸린다.',
  None, [('정지 시간', '2시간'), ('구조 승객', '120명')],
  {"main": "fire truck ladder extended toward a ferris wheel cabin, overcast sky, dramatic angle"},
  'fake', 'record-wheel-stop', '가짜입니다. 관람차 정지 운영 기록에 정지 11분, 탑승객 48명, 부상 0명, 당일 오후 4시 운행 재개라고 되어 있습니다. 높이 88m·14분 같은 맞는 숫자를 섞은 등록 언론사의 오보입니다.',
  part='숫자 상자', clue='11분·48명을 2시간·120명으로 부풀림. 사다리차 구조·탈진은 기록에 없음.', tactic='숫자 부풀리기', postedAt='4일 전', photoTakenAt='4일 전', views='18.6만', commentCount=2100, comments=cm(('그날탄사람', '저 그 캐빈에 있었는데 11분 멈추고 바로 내렸어요 사다리차 같은 거 없었음', 4300, '3일 전'),)),
news('n-halloween', SEOHAE('정해솔'), '도로랜드 할로윈 축제 17일부터… 코스튬 입고 오면 입장권 20% 할인', '퍼레이드는 할로윈 버전, 중앙 광장에 호박 포토존… 야간 개장은 없어 오후 7시 폐장 그대로',
  '도로랜드가 17일부터 31일까지 할로윈 축제를 연다. 머리부터 발끝까지 코스튬을 입고 매표소에 오면 입장권을 20% 깎아 준다. 어른 54,000원이 43,200원이 되는 셈이다.\n\n매일 오후 3시 퍼레이드는 할로윈 버전으로 바뀌고 중앙 광장에는 호박 포토존이 생긴다.\n\n운영 시간은 평소와 같이 오전 10시부터 오후 7시까지다. 운영실은 "야간 개장 문의가 많은데 올해는 하지 않는다"고 밝혔다.',
  ('야간 개장 문의가 많은데 올해는 하지 않습니다.', '도로랜드 운영실'), [('기간', '17 ~ 31일'), ('코스튬 할인', '20%')],
  {"main": "amusement park plaza decorated with many orange pumpkins and autumn garlands, carousel behind, daytime"},
  'real', 'event-halloween', '진짜 기사입니다. 기간 17~31일, 코스튬 20% 할인, 3시 퍼레이드 할로윈 버전, 호박 포토존, 야간 개장 없음이 할로윈 축제 안내와 맞습니다.',
  postedAt='5일 전', photoTakenAt='5일 전', views='5.0만', commentCount=360, place='중앙 광장'),
news('n-halloween-night', {"name": "도로랜드 공식", "handle": "@doroland_official_kr", "kind": "official", "verified": False, "joined": "2026.10", "followers": "1,120", "posts": "4", "bio": "도로랜드 공식 안내 계정", "color": "#0e4a84"}, '[안내] 할로윈 기간 야간 개장… 밤 10시까지 운영, 어린이 무료 입장', '17일부터 31일까지 폐장 밤 10시로 연장, 12세 이하 무료… 막배 밤 10시 30분',
  '도로랜드 운영실에서 안내드립니다. 할로윈 축제 기간인 17일부터 31일까지 야간 개장을 합니다. 폐장 시간은 밤 10시로 늘어나고 섬에서 나오는 막배는 밤 10시 30분입니다.\n\n같은 기간 12세 이하 어린이는 무료로 입장합니다. 코스튬을 입은 어른은 20% 할인입니다.\n\n자세한 내용은 이 계정의 다음 게시물을 확인해 주세요.',
  None, [('폐장', '밤 10시'), ('어린이', '무료')],
  {"main": "amusement park entrance gate at night with orange and purple lights, pumpkins, no people, no text"},
  'fake', 'account-registry', '가짜입니다. 등록 계정부에 공식 계정은 @doroland 하나뿐이고 @doroland_official_kr은 사칭 신고 계정입니다. 할로윈 안내 문서에도 야간 개장 없음, 어린이 무료 없음(코스튬 20% 할인만)이라고 되어 있습니다.',
  part='계정', clue='공식 계정 @doroland 대신 사칭 계정 @doroland_official_kr로 씀. 야간 개장·어린이 무료도 안내 문서와 어긋남.', tactic='사칭', postedAt='2일 전', photoTakenAt='2일 전', views='9.7만', commentCount=620, comments=cm(('의심많은사람', '공식 계정은 @doroland 아닌가요? 이건 팔로워가 천 명인데', 880, '2일 전'),)),
news('n-coaster-why', person('놀이기구 리뷰어', '@ride_review', '2019.11', '5,230', '402', '전국 놀이기구 제원 정리. 숫자로 말합니다', '#4f46e5'), '도로랜드 롤러코스터 정점에서 바다가 보이는 이유… 최고 높이 42m, 시속 92km', '길이 1,180m, 2분 10초… 섬 가장자리에 세워 꼭대기에서 수평선까지 트여',
  '도로랜드 롤러코스터 「블루웨이브」는 최고 높이 42m, 최고 속도 시속 92km, 길이 1,180m다. 숫자만 보면 국내 다른 코스터와 비슷하지만 정점에서 바다가 보인다는 점이 다르다.\n\n이유는 위치다. 코스터가 섬 가장자리에 세워져 있어 꼭대기에 올라가면 가리는 건물 없이 수평선까지 트인다. 한 번 타는 데 2분 10초가 걸리고 키 130cm부터 탈 수 있다.\n\n지난해 방문객 설문에서 가장 좋았던 시설 1위(38%)로 뽑혔다.',
  None, [('최고 높이', '42m'), ('최고 속도', '92km/h'), ('길이', '1,180m')],
  {"main": "blue roller coaster track rising over a sea cliff edge, ocean horizon behind, bright day, wide angle"},
  'real', 'facility-spec', '진짜입니다. 42m, 92km, 1,180m, 2분 10초, 키 130cm가 시설 제원표와 맞고, 설문 1위 38%는 방문객 설문 문서와 맞습니다. 배지 없는 개인 계정이지만 내용이 자료실과 맞습니다.',
  postedAt='6일 전', photoTakenAt='6일 전', views='3.3만', commentCount=180, place='롤러코스터'),
news('n-coaster-65', DOROILBO('한바다'), '[단독] 도로랜드 롤러코스터 2층 코스 증설… 최고 높이 65m로 국내 최고', '내년 15주년 맞춰 공사, 시속 110km… 운영실 "내부 결정 끝났다"',
  '도로랜드가 롤러코스터 「블루웨이브」에 2층 코스를 증설해 최고 높이를 42m에서 65m로 올리는 것으로 확인됐다. 최고 속도도 시속 92km에서 110km로 빨라진다.\n\n도로랜드 사정에 밝은 관계자는 "내부 결정은 끝났고 발표만 남았다"고 전했다. 공사는 내년 15주년에 맞춰 마무리된다.\n\n현재 블루웨이브는 길이 1,180m로 한 번 타는 데 2분 10초가 걸린다.',
  ('내부 결정은 끝났고 발표만 남았습니다.', '도로랜드 사정에 밝은 관계자'), [('증설 후 높이', '65m'), ('증설 후 속도', '110km/h')],
  {"main": "construction cranes next to a tall roller coaster structure by the sea, blueprint style mood, daytime"},
  'fake', 'notice-correction', '가짜입니다. 운영실 공지에 「관람차·롤러코스터 증축 계획 없음(높이 88m·42m 그대로)」가 있고, 시설 제원표에도 증설 계획이 없다고 되어 있습니다. 이름 없는 「관계자」 말뿐인 등록 언론사의 오보입니다.',
  part='인용', clue='증축 계획 없음인데 「관계자: 내부 결정 끝났다」로 씀. 65m·110km는 자료실 어디에도 없음.', tactic='가짜 전문가', postedAt='2일 전', photoTakenAt='6일 전', views='7.3만', commentCount=540, place='롤러코스터'),
news('n-lights', DOROILBO('서하늘'), '15주년 앞둔 도로랜드, 관람차에 조명 1만 2천 개… 13일부터 밤에만 공사', '11월 30일까지 오후 7시 30분~오전 6시 작업, 낮 운행은 그대로… 점등식은 내년 5월 5일',
  '도로랜드가 내년 5월 5일 개장 15주년을 앞두고 관람차 야간 조명 쇼를 준비한다. 높이 88m, 캐빈 36개 관람차 바퀴 전체에 조명 1만 2천 개를 단다.\n\n공사는 13일부터 11월 30일까지 영업이 끝난 오후 7시 30분부터 다음 날 오전 6시까지만 한다. 낮 운행은 평소대로이며 관람차 높이와 캐빈 수는 바뀌지 않는다.\n\n점등식은 내년 5월 5일 저녁 항구에서 드론쇼 본 공연과 함께 한다.',
  ('낮에 타시는 분들은 아무 차이를 못 느끼실 겁니다.', '시설안전팀'), [('조명', '1만 2천 개'), ('공사', '13일 ~ 11월 30일'), ('점등식', '내년 5월 5일')],
  {"main": "workers on a lift installing light strips on a giant ferris wheel spoke at dusk, seaside, no faces"},
  'real', 'press-lights', '진짜 기사입니다. 조명 1만 2천 개, 공사 기간과 야간 시간, 낮 운행 정상, 점등식 내년 5월 5일이 관람차 조명 보도자료와 맞습니다.',
  postedAt='2일 전', photoTakenAt='2일 전', views='4.6만', commentCount=270),
]
# ======================= 쇼츠 14개 (진짜 8 · 가짜 6) =======================
P += [
shorts('s-coaster', COASTER, '도로랜드 롤러코스터 맨 앞자리 POV, 내려올 때 바다가 통째로 보임',
  [('main', '도로랜드 롤러코스터 맨 앞자리 POV! 최고 높이 42m까지 1분쯤 올라감'), ('main', '정점에서 바다가 통째로 보이는 순간… 여기서 숨 참으세요'), ('b', '최고 속도 시속 92km, 한 번에 2분 10초. 오늘만 3번 탐 ㅋㅋ 맨 앞자리 강추')],
  {"main": "first person view from the front seat of a roller coaster at the top of the lift hill, ocean horizon ahead, vertical", "b": "roller coaster train speeding down a blue track by the sea, motion blur, vertical"},
  'real', 'facility-spec', '진짜입니다. 42m, 시속 92km, 2분 10초가 시설 제원표와 맞습니다. 2017년부터 활동한 등록 크리에이터(구독자 112만)입니다.',
  tags='#도로랜드 #롤러코스터 #POV', place='롤러코스터', likes='4.8만', views='61만', commentCount=1300, comments=cm(('놀이기구정복', '42m인데 체감 100m', 900, '어제'),)),
shorts('s-pass', person('놀이공원꿀팁왕', '@park_hack_king', '2025.12', '860', '19', '줄 안 서는 법만 연구함', '#f59e0b', 'creator'), '도로랜드 줄 안 서고 타는 법 (직원 친구가 알려줌)',
  [('main', '도로랜드 줄 안 서고 바로 타는 법, 직원 친구한테 들음'), ('main', "바이킹 직원한테 '운영실 패스'라고 말하면 프리패스 줌"), ('b', '하루 50명만이래요. 아침 배 타고 가서 바로 말하세요')],
  {"main": "long queue line barriers at a viking ship ride entrance, amusement park, vertical", "b": "hand holding a blank plastic pass card near a ride gate, vertical, no text"},
  'fake', 'ticket-price', '가짜입니다. 입장권 요금표 문서에 「우선탑승권이나 프리패스는 운영하지 않는다」가 있고 운영실 공지에도 프리패스 없음이 정리되어 있습니다. 구독자 860명인 채널의 「직원 친구한테 들음」 꿀팁입니다.',
  part='본문', clue='프리패스 없음인데 「운영실 패스 하루 50명」이 있다고 씀.', tactic='없는 혜택', tags='#도로랜드 #꿀팁 #프리패스', place='바이킹', likes='3,100', views='9.8만', commentCount=410, comments=cm(('직원임', '그런 거 없어요 제발 와서 말하지 마세요', 2200, '어제'),)),
shorts('s-churros', person('먹방하는지우', '@jiwoo_eats', '2020.02', '28.7만', '1,040', '전국 놀이공원 먹거리 다 먹어 봄 🍟', '#ca8a04', 'creator'), '도로랜드 10월 신메뉴 관람차 츄러스 6,500원, 솔직 후기',
  [('main', '회전목마 앞 광장 노란 트럭, 10월 신메뉴 관람차 모양 츄러스 6,500원'), ('main', '바퀴살까지 시나몬… 한 입 베어 물면 캐빈이 떨어짐 ㅋㅋ'), ('b', '맛은 시나몬 한 가지. 초코는 없어요. 사진용으로 100점, 줄 10분')],
  {"main": "churro shaped like a ferris wheel held in front of a yellow food truck in an amusement park, vertical close up", "b": "close-up of a cinnamon churro with a bite taken out, carousel blurred behind, vertical"},
  'real', 'press-churros', '진짜입니다. 6,500원, 회전목마 앞 광장 노란 트럭, 시나몬 한 가지(초코 없음)가 관람차 츄러스 보도자료와 맞습니다.',
  tags='#도로랜드 #신메뉴 #츄러스 #먹방', place='회전목마 앞 광장', likes='2.2만', views='34만', commentCount=880, comments=cm(('츄러스요정', '드디어 지우님이 오셨다!! 시나몬 맞죠', 900, '어제'),)),
shorts('s-churros-choco', person('맛집헌터', '@tasty_hunter', '2026.09', '420', '8', '신상 먹거리 1등으로 먹기', '#92400e', 'creator'), '도로랜드 관람차 츄러스 초코맛 신상 떴다!! 1인 1개 한정이라 오픈런 필수',
  [('main', '관람차 츄러스 초코맛 오늘 첫 출시!! 7,500원'), ('main', '시나몬보다 초코가 훨씬 맛있음… 바퀴살이 초코로 코팅됨'), ('b', '1인 1개 한정이라 10시 배 타고 바로 달려야 함')],
  {"main": "chocolate coated churro shaped like a ferris wheel on a paper tray, yellow truck behind, vertical", "b": "people queueing at a yellow churro food truck in a plaza, vertical"},
  'fake', 'press-churros', '가짜입니다. 관람차 츄러스 보도자료에 「맛은 시나몬 한 가지, 초코 맛은 없음, 6,500원, 구매 수량 제한 없음」이라고 되어 있습니다. 가입 한 달 된 채널에 조회수만 큽니다.',
  part='제목', clue='시나몬 한 가지뿐인데 「초코맛 신상 7,500원·1인 1개」로 씀.', tactic='없는 혜택', tags='#도로랜드 #신상 #츄러스', place='회전목마 앞 광장', likes='5,600', views='22만', commentCount=330, comments=cm(('먹방하는지우', '어제 갔는데 초코 없었어요 트럭에 시나몬만 써 있음', 1800, '어제'),)),
shorts('s-safari', person('동물원덕후', '@zoo_lover_min', '2018.06', '9.4만', '612', '전국 동물원·사파리 38군데 다녀옴', '#15803d', 'creator'), '도로랜드 사파리에서 기린이 지프 창문까지 왔어요🦒 (38종 중 최애)',
  [('main', '사파리 지프 투어 시작! 동물 38종 산다는데 기린부터'), ('main', '기린이 차 바로 앞까지 왔어요🦒 가이드님이 "창문 닫지 마세요, 혀 길어요" ㅋㅋ'), ('b', '투어 40분 동안 얼룩말, 타조, 미어캣까지. 지난주 태어난 아기 기린도 멀리서 봄')],
  {"main": "giraffe head leaning close to a safari jeep window, seen from inside the jeep, vertical", "b": "zebras and ostriches in an open safari field seen from a jeep, vertical"},
  'real', 'record-safari', '진짜입니다. 동물 38종, 40분 투어, 기린·얼룩말·타조·미어캣, 아기 기린이 사파리 동물 현황과 시설 제원표와 맞습니다.',
  tags='#도로랜드 #사파리 #기린', place='사파리', likes='1.9만', views='27만', commentCount=640),
shorts('s-lion', person('세상의모든비밀', '@secret_world_tv', '2026.04', '2,904', '41', '그들이 숨기는 진실', '#111827', 'creator'), '[충격] 도로랜드 사파리에 사자 풀어놨다… 지프 투어 중 관람객 대피',
  [('main', '도로랜드 사파리에 사자가 있다는 거 아셨나요?'), ('main', '어제 지프 투어 중 사자 두 마리가 울타리를 넘어 관람객이 대피했습니다'), ('b', '운영실은 이 사실을 숨기고 있습니다. 영상이 지워지기 전에 공유하세요')],
  {"main": "blurry photo of a large lion walking in tall grass near a safari fence, dramatic low light, vertical", "b": "empty safari jeep parked on a dirt road, dark mood, vertical"},
  'fake', 'record-safari', '가짜입니다. 사파리 동물 현황 문서에 「초식동물 사파리, 사자·호랑이 0(없음)」이라고 되어 있고 안전 점검 기록에도 대피 같은 일은 없습니다. AI 합성 삭제 집계에 「사파리 사자 탈출」 합성물이 삭제됐다는 기록도 있습니다.',
  part='본문', clue='사자가 없는 사파리에 「사자 두 마리 탈출·대피」를 씀.', tactic='감정 자극', tags='#도로랜드 #사자 #충격', place='사파리', likes='8,900', views='126만', commentCount=2400, comments=cm(('사파리가이드', '저희 사파리에 사자 없어요 초식동물만 있습니다', 5200, '어제'), ('AI감별사', '사자 앞발 발가락 세어 보세요 여섯 개', 3100, '어제'))),
shorts('s-run', person('달리는직장인', '@run_after_work', '2019.03', '4.1만', '388', '퇴근하고 달립니다. 주말엔 어디든', '#0ea5e9', 'creator'), '바다 위 놀이공원을 달린다? 도로랜드 섬 둘레길 5.2km 러닝 크루 체험',
  [('main', '토요일 아침 9시, 도로랜드 섬 둘레길 러닝 크루 합류. 8시 30분 배로 들어옴'), ('main', '한 바퀴 5.2km, 왼쪽은 바다 오른쪽은 롤러코스터'), ('b', '사파리 울타리 옆 구간에서 기린이 같이 뜀 (진짜). 32분 완주, 참가비 무료, 회차당 100명')],
  {"main": "runners on a seaside path with a roller coaster on one side and the ocean on the other, early morning, vertical, seen from behind", "b": "giraffe behind a wooden fence next to a running path, morning light, vertical"},
  'real', 'press-run', '진짜입니다. 매주 토요일 9시, 8시 30분 배, 5.2km, 사파리 울타리 옆 구간, 무료, 회차당 100명이 러닝 크루 보도자료와 맞습니다.',
  tags='#러닝 #도로랜드 #둘레길', place='섬 둘레길', likes='6,400', views='8.9만', commentCount=210),
shorts('s-drone', person('밤하늘기록', '@night_sky_log', '2020.09', '1.8만', '276', '밤하늘, 불꽃, 드론쇼 기록', '#4338ca', 'creator'), '도로랜드 드론쇼 직캠, 관람차가 하늘에 하나 더 떴다',
  [('main', '8일 저녁 8시, 항구 광장에서 기다린 지 40분'), ('main', '드론 500대가 한 번에 떠오름… 소리가 벌 떼 같음'), ('b', '관람차가 하늘에 하나 더!! 15분 끝. 다들 박수. 본 공연은 내년 5월 5일이래요')],
  {"main": "drone light show forming a glowing ferris wheel in the night sky above a real ferris wheel across the sea, vertical", "b": "crowd at a harbor plaza looking up at drone lights at night, vertical, seen from behind"},
  'real', 'press-drone', '진짜입니다. 8일 저녁 8시, 항구 광장, 드론 500대, 15분, 관람차 모양, 본 공연 내년 5월 5일이 드론 라이트쇼 보도자료와 맞습니다.',
  tags='#드론쇼 #도로랜드 #직캠', place='항구 광장', likes='1.1만', views='19만', commentCount=380, postedAt='4일 전', photoTakenAt='4일 전'),
shorts('s-drone-vip', person('티켓정보통', '@ticket_info_kr', '2026.08', '1,340', '26', '공연·행사 티켓 오픈 알림', '#db2777', 'creator'), '도로랜드 드론쇼 본 공연 VIP석 예매 오픈!! 10만 원, 선착순 300석',
  [('main', '내년 5월 5일 드론쇼 본 공연 VIP석 예매가 오늘 열렸습니다'), ('main', '항구 광장 맨 앞 300석, 1인 10만 원. 일반석은 3만 원'), ('b', '아래 링크에서 이름·전화번호 넣고 예매하세요. 선착순!')],
  {"main": "rows of empty white VIP chairs set up on a harbor plaza facing the sea at dusk, vertical", "b": "smartphone screen glow in a dark crowd, vertical, no text"},
  'fake', 'press-drone', '가짜입니다. 드론 라이트쇼 보도자료에 본 공연은 「무료, 좌석 없음, VIP석 없음」이라고 되어 있습니다. 행사 일정 문서에도 항구에서 그냥 보는 행사입니다. 이름·전화번호를 모으는 글입니다.',
  part='본문', clue='좌석·VIP석 없는 무료 행사인데 「VIP석 10만 원 예매」로 씀.', tactic='없는 혜택', tags='#드론쇼 #예매 #도로랜드', place='항구 광장', likes='2,700', views='14만', commentCount=520),
shorts('s-vlog', person('하루하루기록', '@haru_daily_', '2021.01', '3,620', '540', '평범한 하루를 60초에', '#64748b', 'creator'), '도로랜드 하루 60초 브이로그 | 10시 배부터 7시 반 막배까지',
  [('main', '10시 정각 배 타고 출발! 25분이면 섬 도착'), ('b', '사파리 지프 투어 먼저. 기린이 차 바로 앞까지 옴'), ('c', '회전목마 앞 노란 트럭 관람차 츄러스 6,500원, 줄 5분'), ('d', '3시 퍼레이드 보고 관람차 노을 보고, 7시 반 막배로 집. 완벽한 하루')],
  {"main": "view from a ferry deck approaching an island amusement park with a ferris wheel, morning, vertical", "b": "giraffe near a safari jeep, vertical", "c": "ferris wheel shaped churro held up in front of a carousel, vertical", "d": "sunset seen from inside a ferris wheel cabin over the sea, vertical"},
  'real', 'hours-ferry', '진짜입니다. 10시 배, 25분, 츄러스 6,500원, 3시 퍼레이드, 막배 7시 30분이 운영 시간·배 시간표, 츄러스 보도자료, 행사 일정과 맞습니다.',
  tags='#브이로그 #도로랜드', place='도로랜드', likes='2,300', views='4.1만', commentCount=96),
shorts('s-free', person('도로랜드꿀팁TV', '@doroland_tips', '2026.09', '140', '6', '도로랜드 꿀팁만 모음', '#f97316', 'creator'), '내일 도로랜드 전 기구 무료!! 운영실 직원한테 들음 (선착순 500명)',
  [('main', '내일 도로랜드 모든 놀이기구 무료입니다!!'), ('main', '15주년 기념으로 운영실이 결정했대요. 운영실 직원 지인이 알려 줬어요'), ('b', '오전 10시 배 선착순 500명만!! 입장권 5만 4천 원 아끼세요 🔥')],
  {"main": "amusement park entrance gate with a crowd rushing in, bright morning, vertical, seen from behind", "b": "ferry ticket counter window with a small sign, no readable text, vertical"},
  'fake', 'notice-correction', '가짜입니다. 운영실 공지에 「전 기구 무료 개방·선착순 무료 입장은 계획 없음」이 있고, 공식 계정과 전광판 외의 무료 안내는 운영실과 관계없다고 되어 있습니다. 가입 한 달, 팔로워 140명인 채널입니다.',
  part='본문', clue='무료 개방 계획 없음인데 「내일 전 기구 무료, 선착순 500명」으로 씀.', tactic='없는 혜택', tags='#도로랜드 #무료 #꿀팁', place='항구', likes='1.9만', views='48만', commentCount=1700),
shorts('s-popup-vlog', person('굿즈수집러', '@goods_hunter_', '2022.11', '7,800', '233', '한정판이면 일단 줄 섬', '#be185d', 'creator'), '도로랜드 팝업 오픈런 브이로그 | 새벽 5시 20분 도착, 키링 2개 성공',
  [('main', '새벽 5시 20분 항구 광장 도착. 벌써 앞에 40명'), ('main', '10시 오픈 때 줄이 200m… 키링은 1인 2개 제한'), ('b', '11시 5분 키링 매진 방송 나옴. 엽서 세트 3,000원도 겟. 기린 인형 19,000원은 참음')],
  {"main": "dawn at a harbor plaza, a short queue of people with blankets in front of a closed white pop-up store tent, vertical", "b": "two small ferris wheel keyrings and a postcard set held in hands, vertical"},
  'real', 'press-popup', '진짜입니다. 새벽 5시 20분, 줄 200m, 키링 1인 2개, 셋째 날 매진 11시 5분, 엽서 3,000원, 기린 인형 19,000원이 팝업스토어 보도자료 표와 맞습니다.',
  tags='#오픈런 #팝업 #도로랜드', place='항구 광장', likes='4,200', views='6.2만', commentCount=150, postedAt='2일 전', photoTakenAt='3일 전'),
shorts('s-challenge', {"name": "도로랜드챌린지", "handle": "@doroland_challenge", "kind": "official", "verified": False, "joined": "2026.10", "followers": "2,340", "posts": "3", "bio": "도로랜드 공식 챌린지 계정", "color": "#0e4a84"}, '#기린이름챌린지 참여하면 연간회원권 추첨!! (이번 주 100명)',
  [('main', '아기 기린 이름 지어서 #기린이름챌린지 올리면 끝!'), ('main', '매주 100명에게 연간회원권(189,000원) 추첨 🎁'), ('b', '아래 링크에 이름·학교·전화번호 등록해야 추첨 대상!')],
  {"main": "baby giraffe sticker style graphic on a phone screen with confetti, vertical, no readable text", "b": "gift box with a ribbon on a table, vertical"},
  'fake', 'press-giraffe', '가짜입니다. 아기 기린 보도자료에 이름 공모는 「@doroland 게시물 댓글로만, 개인정보 안 받음, 당첨 1명」이라고 되어 있습니다. 등록 계정부에 @doroland_challenge는 사칭 신고 계정입니다. 연간회원권 189,000원은 맞는 숫자를 섞은 것입니다.',
  part='계정', clue='공식 계정 @doroland 대신 사칭 계정으로 쓰고, 당첨 1명을 매주 100명 추첨으로 바꿈. 이름·학교·전화번호를 모음.', tactic='사칭', tags='#기린이름챌린지 #도로랜드', place='도로랜드', likes='3,300', views='11만', commentCount=640),
shorts('s-parade', person('회전목마러버', '@merrygo_round', '2020.05', '1,270', '194', '회전목마 있는 곳이면 어디든', '#e11d48', 'creator'), '할로윈 퍼레이드 리허설 목격! 호박 머리 쓴 댄서들이 3시 퍼레이드 연습 중',
  [('main', '오늘 2시 40분 중앙 광장, 호박 머리 쓴 댄서들이 줄 서 있음'), ('main', '직원분께 물어보니 17일부터 하는 할로윈 퍼레이드 리허설이래요. 매일 3시'), ('b', '중앙 광장에 호박 포토존도 만드는 중. 코스튬 입고 오면 입장권 20% 할인이라는데 뭐 입지')],
  {"main": "dancers in orange pumpkin costumes rehearsing in an amusement park plaza, seen from behind, vertical", "b": "workers arranging large pumpkins for a photo zone in a plaza, vertical, no faces"},
  'real', 'event-halloween', '진짜입니다. 17일부터, 매일 3시 퍼레이드 할로윈 버전, 중앙 광장 호박 포토존, 코스튬 20% 할인이 할로윈 축제 안내와 맞습니다.',
  tags='#할로윈 #도로랜드 #퍼레이드', place='중앙 광장', likes='1,500', views='2.8만', commentCount=88),
]
# ======================= 스토리 14개 (진짜 8 · 가짜 6) =======================
P += [
story('t-ferry', person('여행하는 다은', '@daeun_trip', '2020.03', '412', '388', '주말마다 어디든. 섬 여행 좋아함', '#0369a1'),
  [sl('main', '도로랜드 가는 10시 배 안! 관람차 벌써 보인다', '2시간 전', {"type": "place", "text": "도로1호"}), sl('main', '25분 만에 도착 🚢 주말이라 30분마다 배가 있대요', '2시간 전')],
  {"main": "view from a ferry window of an island with a white ferris wheel, sunny sea, vertical"},
  'real', 'hours-ferry', '진짜입니다. 10시 배, 25분, 주말 30분 간격이 운영 시간과 배 시간표와 맞습니다. 팔로워 412명 계정의 평범한 스토리입니다.', postedAt='2시간 전', photoTakenAt='2시간 전', views='73'),
story('t-churros', person('츄러스요정', '@churros_fairy', '2022.02', '96', '141', '츄러스 있는 곳이면 어디든', '#ca8a04'),
  [sl('main', '회전목마 옆 노란 트럭 관람차 츄러스 6,500원 🥨 시나몬 듬뿍!!', '3시간 전', {"type": "place", "text": "회전목마 앞 광장"}), sl('main', '줄 5분밖에 안 섰어요. 다음에 또 올 듯', '3시간 전', {"type": "poll", "q": "또 먹을래요?", "a": "당연", "b": "배불러요", "pa": 71})],
  {"main": "close-up of a ferris wheel shaped cinnamon churro held in front of a yellow food truck, carousel in background, vertical"},
  'real', 'press-churros', '진짜입니다. 노란 트럭, 6,500원, 시나몬이 관람차 츄러스 보도자료와 맞습니다. 팔로워 96명에 조회 64회인 작은 계정의 후기입니다.', views='64'),
story('t-sunset', person('바다랑나랑', '@sea_and_me', '2019.08', '233', '902', '바다 사진만 올림', '#0e7490'),
  [sl('main', '관람차 올라가는 중… 한 바퀴 14분이래', '어제 오후 6:12', {"type": "place", "text": "도로랜드 관람차"}), sl('main', '꼭대기에서 본 노을🌅 마지막 탑승 6시 40분이라 딱 맞춰 탐', '어제 오후 6:20')],
  {"main": "sunset over the sea seen from inside a ferris wheel cabin, warm orange light, vertical"},
  'real', 'facility-spec', '진짜입니다. 한 바퀴 14분, 마지막 탑승 오후 6시 40분이 시설 제원표와 맞습니다.', postedAt='어제', photoTakenAt='어제 오후 6:20', views='118'),
story('t-fireworks', person('꿀팁전도사', '@honey_tip_kr', '2026.09', '58', '11', '좋은 정보는 나눠야 제맛', '#f97316'),
  [sl('main', '오늘 밤 9시 도로랜드 할로윈 불꽃놀이!!🎆 섬 안에서 봄', '1시간 전', {"type": "place", "text": "도로랜드 중앙 광장"}), sl('main', '막배도 밤 10시까지 늘린대요. 지금 가면 딱', '1시간 전')],
  {"main": "fireworks over a dark sea with a ferris wheel silhouette, vertical, dramatic"},
  'fake', 'event-calendar', '가짜입니다. 행사 일정 문서에 불꽃놀이는 「1년에 한 번, 5월 5일 저녁 8시, 항구에서 관람」이고, 운영 시간 문서에 폐장 오후 7시·막배 7시 30분입니다. 할로윈 안내에도 야간 개장 없음입니다.',
  part='시간·날짜', clue='불꽃놀이는 5월 5일 연 1회인데 「오늘 밤 9시 할로윈 불꽃놀이, 막배 10시」로 씀.', tactic='날짜 조작', postedAt='1시간 전', photoTakenAt='1시간 전', views='5,200'),
story('t-kidsfree', person('소문난아이', '@rumor_kid', '2026.10', '14', '2', '', '#6b7280'),
  [sl('main', '할로윈 기간에 도로랜드 어린이 무료래ㅠㅠ 내일부터!! 친구가 그럼', '40분 전'), sl('main', '어른은 코스튬 입으면 20% 할인이고 애들은 공짜!! 다들 가요', '40분 전')],
  {"main": "children in halloween costumes walking toward an amusement park gate, seen from behind, vertical"},
  'fake', 'event-halloween', '가짜입니다. 할로윈 축제 안내에 「코스튬 입장권 20% 할인, 어린이 무료 입장은 없음」이라고 되어 있습니다. 20% 할인은 맞게 써서 그럴듯합니다.',
  part='본문', clue='어린이 무료 없음인데 「애들은 공짜」로 씀. 코스튬 20% 할인은 진짜.', tactic='없는 혜택', postedAt='40분 전', photoTakenAt='40분 전', views='3,900'),
story('t-official', OFFICIAL,
  [sl('main', '오늘도 정상 운영 중 ☀️ 지금 중앙 광장', '오전 10:05', {"type": "place", "text": "도로랜드 중앙 광장"}), sl('main', '오전 8시 30분 점검 완료 ✓ 모든 기구 운영 중입니다. 오늘 바람이 조금 있어 바이킹은 오후 2시 점검 뒤 다시 안내드려요', '오전 10:06')],
  {"main": "sunny amusement park central plaza with a carousel in the morning, few visitors, vertical"},
  'real', 'record-safety', '진짜입니다. 공식 계정 @doroland(등록 계정부·인증)이고, 개장 전 8시 30분·오후 2시 점검과 강풍 때 바이킹 중단 기준이 안전 점검 기록·휴장 기준 문서와 맞습니다.', postedAt='오전 10:05', photoTakenAt='오전 10:05', views='2.1만'),
story('t-event', {"name": "도로랜드 이벤트", "handle": "@doroland_event", "kind": "official", "verified": False, "joined": "2026.10", "followers": "1,840", "posts": "3", "bio": "도로랜드 공식 이벤트 계정", "color": "#0e4a84"},
  [sl('main', '15주년 기념 🎉 연간회원권(189,000원) 100명 무료!', '2시간 전'), sl('main', '아래 링크에 이름·생년월일·전화번호 남기면 끝. 선착순!', '2시간 전')],
  {"main": "golden ticket shaped card on a confetti background, vertical, no readable text"},
  'fake', 'account-registry', '가짜입니다. 등록 계정부에 공식 계정은 @doroland 하나뿐이고 @doroland_event는 사칭 신고 계정입니다. 운영실 공지에도 연간회원권 추첨 행사는 운영실 행사가 아니라고 되어 있습니다. 가격 189,000원은 맞게 써서 그럴듯하지만 개인정보를 모읍니다.',
  part='계정', clue='공식 계정이 아닌 @doroland_event로 쓰고, 없는 연간회원권 무료 행사를 만듦.', tactic='사칭', postedAt='2시간 전', photoTakenAt='2시간 전', views='1.4만'),
story('t-viking', person('줄서기장인', '@line_king', '2021.06', '301', '77', '줄 서는 게 취미', '#7c3aed'),
  [sl('main', '바이킹 줄 40분째ㅠ 주말은 역시', '어제 오후 3:30', {"type": "place", "text": "도로랜드 바이킹"}), sl('b', '끝자리 탔다!! 75도까지 올라감 진짜 무서움. 한 번에 48명 타는데 끝자리는 4명뿐', '어제 오후 4:12')],
  {"main": "long queue in front of a viking ship ride, sunny afternoon, vertical, seen from behind", "b": "viking ship ride swinging high at a steep angle against blue sky, vertical"},
  'real', 'facility-spec', '진짜입니다. 바이킹 최대 각도 75도, 1회 48명이 시설 제원표와 맞습니다.', postedAt='어제', photoTakenAt='어제 오후 4:12', views='210'),
story('t-lost', person('덜렁이', '@clumsy_dana', '2023.04', '188', '240', '오늘도 뭔가 잃어버림', '#db2777'),
  [sl('main', '하모니아 2시 공연 맨 앞줄에 검은 선글라스 두고 왔어요ㅠㅠ', '1시간 전', {"type": "place", "text": "하모니아 공연장"}), sl('main', '중앙 광장 안내소 분실물 센터에 물어보니 상반기에만 선글라스 412개 들어왔대요… 3개월 보관이라니 찾으러 가야지', '50분 전')],
  {"main": "empty theater front row seats with a pair of black sunglasses left on a seat, vertical"},
  'real', 'press-lostfound', '진짜입니다. 하모니아 2시 공연은 공연 안내와, 분실물 센터 위치(중앙 광장 안내소)·선글라스 412건·3개월 보관은 분실물 보도자료와 맞습니다.', postedAt='1시간 전', photoTakenAt='1시간 전', views='92'),
story('t-drone', person('항구살이', '@harbor_life_', '2018.10', '1,020', '1,311', '항구 동네 20년', '#0f766e'),
  [sl('main', '드론쇼 기다리는 중… 항구 광장에 사람 엄청 많다', '4일 전 저녁 7:40', {"type": "place", "text": "항구 광장"}), sl('b', '떴다!!! 관람차가 두 개 🤯 500대래', '4일 전 저녁 8:03')],
  {"main": "crowd gathering at a harbor plaza at dusk waiting, ferris wheel across the water, vertical, seen from behind", "b": "drone lights forming a ferris wheel shape above the real ferris wheel across the sea at night, vertical"},
  'real', 'press-drone', '진짜입니다. 8일 저녁 8시 항구 광장, 드론 500대, 관람차 모양이 드론 라이트쇼 보도자료와 맞습니다.', postedAt='4일 전', photoTakenAt='4일 전 저녁 8:03', views='640'),
story('t-ticket', person('티켓나눔', '@ticket_share_kr', '2026.10', '33', '5', '못 가게 된 티켓 나눔', '#dc2626'),
  [sl('main', '도로랜드 연간회원권 양도해요!! 189,000원짜리 9만 원에', '30분 전'), sl('main', '이사 가서 못 써요ㅠ 양도 서류 다 됨. DM 주세요 선착순', '30분 전')],
  {"main": "hand holding a blank plastic membership card in front of a ferris wheel, vertical, no readable text"},
  'fake', 'ticket-price', '가짜입니다. 입장권 요금표 문서에 연간회원권은 「본인 사진 등록, 양도 불가」로 되어 있고 운영실 공지에도 양도 이벤트는 운영실과 관계없다고 되어 있습니다. 가격 189,000원은 맞습니다.',
  part='본문', clue='양도 불가인 연간회원권을 「양도 서류 다 됨」으로 씀.', tactic='없는 혜택', postedAt='30분 전', photoTakenAt='30분 전', views='7,600'),
story('t-popup', person('굿즈수집러', '@goods_hunter_', '2022.11', '7,800', '233', '한정판이면 일단 줄 섬', '#be185d'),
  [sl('main', '새벽 5시 20분 항구 팝업 오픈런… 앞에 40명 😇', '3일 전 새벽 5:20', {"type": "place", "text": "항구 광장 팝업스토어"}), sl('b', '키링 2개 성공!! 1인 2개 제한이라 딱. 8,000원씩', '3일 전 오전 10:40')],
  {"main": "dawn queue in front of a white pop-up store tent at a harbor plaza, vertical", "b": "two small ferris wheel keyrings held up in front of the sea, vertical"},
  'real', 'press-popup', '진짜입니다. 새벽 5시 20분, 1인 2개 제한, 키링 8,000원이 팝업스토어 보도자료와 맞습니다.', postedAt='3일 전', photoTakenAt='3일 전 오전 10:40', views='530'),
story('t-live', {"name": "도로랜드 LIVE", "handle": "@doroland_live", "kind": "official", "verified": False, "joined": "2026.10", "followers": "2,210", "posts": "2", "bio": "도로랜드 공식 라이브 채널", "color": "#0e4a84"},
  [sl('main', '오늘 밤 9시 운영실장 긴급 라이브 🔴 입장권 요금 인상 직접 설명합니다', '1시간 전'), sl('main', '알림 설정하고 아래 링크로 사전 질문 남겨 주세요 (이름·전화번호 필수)', '1시간 전')],
  {"main": "dark studio with a red on-air style lamp glowing and an empty chair, vertical, no readable text"},
  'fake', 'notice-correction', '가짜입니다. 운영실 공지에 「라이브 방송은 @doroland에서만, 사전 질문·전화번호 안 받음」과 「내년 요금 동결」이 있고, 등록 계정부에 @doroland_live는 사칭 신고 계정입니다.',
  part='계정', clue='라이브는 @doroland에서만 하는데 사칭 계정 @doroland_live로 쓰고, 요금 동결인데 인상 설명 라이브라고 함.', tactic='사칭', postedAt='1시간 전', photoTakenAt='1시간 전', views='8,100'),
story('t-elephant', COASTER,
  [sl('main', '친구가 그러는데 도로랜드 사파리에 코끼리 투어 새로 생긴대요 🐘 다음 주부터', '2시간 전'), sl('main', '저도 들은 얘기라 확실하진 않은데 일단 공유!! 다음 주 가서 확인해 볼게요', '2시간 전')],
  {"main": "safari jeep on a dirt road at golden hour with no animals visible, vertical"},
  'fake', 'record-safari', '가짜입니다. 사파리 동물 현황 문서에 코끼리는 「0, 없음」이고 초식동물 사파리 38종에 코끼리 투어 계획도 없습니다. 인증 크리에이터(구독자 112만)가 「친구가 그러는데」라며 올린 글이라 배지만 보면 못 찾습니다.',
  part='본문', clue='코끼리가 없는 사파리에 「코끼리 투어 신설」을 씀.', tactic='가짜 전문가', postedAt='2시간 전', photoTakenAt='2시간 전', views='3.4만'),
]

# ---------- 검사 ----------
ids = [p['id'] for p in P]; assert len(ids) == len(set(ids)), 'id 중복'
from collections import Counter
c = Counter((p['format'], p['answer']['truth']) for p in P)
print({k: v for k, v in sorted(c.items())}, 'total', len(P))
for p in P:
    a = p['answer']; assert a['doc'] in DOC.values()
    if a['truth'] == 'fake': assert a.get('part') in PART_KIND, p['id']
    for key in p['images']:
        assert key in {'main', 'b', 'c', 'd'}
    if p['format'] == 'shorts': assert all(s['img'] in p['images'] for s in p['scenes']), p['id']
    if p['format'] == 'story': assert all(s['img'] in p['images'] for s in p['slides']), p['id']
    bad = ['사라', '섬이 안 보', '수평선만']
    txt = json.dumps(p, ensure_ascii=False)
    assert not any(b in txt for b in ['섬이 안 보', '수평선만', '사라진 섬', '사라지는 섬']), p['id']
SEED.write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding='utf-8')
print('wrote', SEED, len(P))
