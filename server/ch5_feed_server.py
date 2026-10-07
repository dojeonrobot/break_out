#!/usr/bin/env python3
"""챕터 5 「도로그램」 실시간 피드 서버 (표준 라이브러리만 사용, 추가 설치 없음).

학생 화면(chapter05/feed.html)과 운영자 화면(chapter05/feed-admin.html)이 쓰는 API를 제공한다.
- 게시글/판별 저장: server/data/ch5_feed.json (gitignore)
- 업로드·AI 이미지: server/data/uploads/
- 실시간 반영: SSE(/api/ch5/stream). 무언가 바뀌면 version을 올려 알리고, 화면은 /api/ch5/state를 다시 받는다.
- AI 이미지: Gemini 이미지 모델(나노바나나 2)을 서버에서 호출. 키는 환경변수 GEMINI_API_KEY.

실행:
    python server/ch5_feed_server.py            # http://localhost:8095/chapter05/feed.html
환경변수:
    CH5_PORT=8095  CH5_HOST=127.0.0.1  CH5_ADMIN_KEY=0101
    GEMINI_API_KEY=...  GEMINI_IMAGE_MODEL=gemini-3.1-flash-image  GEMINI_TEXT_MODEL=gemini-2.5-flash
    CH5_AI_QUOTA=8 (조당 AI 이미지 횟수)  CH5_STATIC=1 (저장소 파일도 서빙, 로컬 확인용)
"""
import base64
import json
import os
import queue
import re
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data')
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')
DB_PATH = os.path.join(DATA_DIR, 'ch5_feed.json')
SEED_PATH = os.path.join(HERE, 'ch5_seed.json')

PORT = int(os.environ.get('CH5_PORT', '8095'))
HOST = os.environ.get('CH5_HOST', '127.0.0.1')
ADMIN_KEY = os.environ.get('CH5_ADMIN_KEY', '0101')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY', '')
IMAGE_MODEL = os.environ.get('GEMINI_IMAGE_MODEL', 'gemini-3.1-flash-image')
TEXT_MODEL = os.environ.get('GEMINI_TEXT_MODEL', 'gemini-2.5-flash')
AI_QUOTA = int(os.environ.get('CH5_AI_QUOTA', '8'))
SERVE_STATIC = os.environ.get('CH5_STATIC', '1') == '1'

TEAM_COUNT = 10
MAX_POSTS_PER_TEAM = int(os.environ.get('CH5_MAX_POSTS', '2'))   # 조마다 올릴 수 있는 가짜 게시물 수
MAX_UPLOAD = 6 * 1024 * 1024
PHASES = ['read', 'make', 'judge', 'reveal']
FORMATS = {'news', 'sns', 'story', 'witness', 'notice'}
VERDICTS = {'real', 'fake', 'unsure'}
THUMB_TPLS = {'auto', 'frame', 'full', 'cam', 'pola', 'collage', 'black', 'text'}
CRITERIA = {'who', 'when', 'witness', 'cross'}
# 아이들이 입력하는 AI 프롬프트에서 막을 말 (모델 자체 안전 필터와 별도로 한 번 더 거른다)
BLOCKED_WORDS = ['피가', '피투성', '시체', '죽이', '살인', '총으로', '칼로', '야한', '벗은', '나체', '대통령', '연예인',
                 '아이돌', '유튜버', '실제 사람', '자살', '마약', '담배', '술 마시']
AI_STYLE = ('어린이 교육 캠프용 이미지다. 실존 인물, 유명인, 실제 브랜드 로고, 폭력적이거나 선정적인 표현은 넣지 않는다. '
            '도로랜드는 바다 위 섬에 있는 놀이공원이다(관람차, 회전목마, 롤러코스터, 사파리, 하모니아 공연장). ')

lock = threading.RLock()
listeners = []
listeners_lock = threading.Lock()


def now_ms():
    return int(time.time() * 1000)


SEED_IMG_DIR = os.path.join(HERE, 'seed_images')


def load_seed_posts():
    """운영실 자료(정답이 정해진 게시물). 판별 화면에서 조 게시물과 구별되지 않도록 id는 무작위로 새로 붙인다."""
    with open(SEED_PATH, encoding='utf-8') as f:
        seeds = json.load(f)
    out = []
    for i, s in enumerate(seeds):
        p = {k: v for k, v in s.items() if k not in ('id', 'image', 'imagePrompt')}
        p.update(id='p' + uuid.uuid4().hex[:10], seedKey=s.get('id'), team=0, status='approved', seed=True,
                 createdAt=now_ms() - (len(seeds) - i) * 1000, imageId=None)
        img = s.get('image')
        if img and os.path.exists(os.path.join(SEED_IMG_DIR, img)):
            with open(os.path.join(SEED_IMG_DIR, img), 'rb') as f:
                p['imageId'] = store_image(f.read())
        out.append(p)
    return out


def fresh_db():
    return {'version': 1, 'phase': 'read', 'posts': load_seed_posts(), 'judgments': {},
            'aiUsed': {}, 'updatedAt': now_ms()}


def read_db():
    if not os.path.exists(DB_PATH):
        return fresh_db()
    with open(DB_PATH, encoding='utf-8') as f:
        return json.load(f)


os.makedirs(UPLOAD_DIR, exist_ok=True)
DB = None   # main()에서 불러온다 (운영실 자료 사진을 넣는 store_image가 아래에 정의돼 있어서)


def save_and_broadcast():
    """DB를 저장하고 열려 있는 모든 화면에 바뀌었다고 알린다. lock 안에서 호출할 것."""
    DB['version'] += 1
    DB['updatedAt'] = now_ms()
    tmp = DB_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(DB, f, ensure_ascii=False)
    os.replace(tmp, DB_PATH)
    msg = json.dumps({'v': DB['version'], 'phase': DB['phase']})
    with listeners_lock:
        for q in list(listeners):
            q.put(msg)


def remove_posts(posts):
    """게시물과 그 판별 기록, 다른 글이 안 쓰는 업로드 사진 파일을 지운다. lock 안에서 호출할 것."""
    ids = {p['id'] for p in posts}
    DB['posts'] = [p for p in DB['posts'] if p['id'] not in ids]
    DB['judgments'] = {k: v for k, v in DB['judgments'].items() if k.rsplit(':', 1)[0] not in ids}
    still = {p.get('imageId') for p in DB['posts']} | {p.get('thumbImageId') for p in DB['posts']}
    for p in posts:
        for img in (p.get('imageId'), p.get('thumbImageId')):
            if img and img not in still and re.fullmatch(r'[a-f0-9]{32}\.(jpg|png|webp)', img):
                try:
                    os.remove(os.path.join(UPLOAD_DIR, img))
                except OSError:
                    pass
                DB.get('aiImages', {}).pop(img, None)


def find_post(pid):
    return next((p for p in DB['posts'] if p['id'] == pid), None)


def judgment_key(pid, team):
    return f'{pid}:{team}'


def compute_scores():
    """공개 단계 점수: 맞힌 판별 1점(근거 기준을 고른 경우만), 우리 조 가짜를 진짜라고 한 조마다 1점."""
    scores = {t: {'team': t, 'correct': 0, 'fooled': 0, 'judged': 0} for t in range(1, TEAM_COUNT + 1)}
    for p in DB['posts']:
        if p['status'] != 'approved':
            continue
        truth = p['answer']['truth'] if p.get('seed') else p['secret'].get('truth', 'fake')
        for t in range(1, TEAM_COUNT + 1):
            j = DB['judgments'].get(judgment_key(p['id'], t))
            if not j or t == p['team']:
                continue
            scores[t]['judged'] += 1
            if j['verdict'] == truth and j.get('criterion') in CRITERIA:
                scores[t]['correct'] += 1
            if truth == 'fake' and j['verdict'] == 'real' and p['team'] in scores:
                scores[p['team']]['fooled'] += 1
    rows = list(scores.values())
    for r in rows:
        r['total'] = r['correct'] + r['fooled']
    rows.sort(key=lambda r: (-r['total'], r['team']))
    return rows


def verdict_counts(pid):
    c = {'real': 0, 'fake': 0, 'unsure': 0}
    for k, j in DB['judgments'].items():
        if k.startswith(pid + ':'):
            c[j['verdict']] += 1
    return c


PUBLIC_FIELDS = ('id', 'format', 'author', 'title', 'body', 'tags', 'place', 'postedAt', 'photoTakenAt', 'imageId', 'likes', 'views', 'thumbTpl', 'thumbTitle', 'thumbImageId', 'status')


def order_key(pid):
    """판별 화면에서 운영실 자료와 조 게시물이 섞이도록 모두에게 같은 무작위 순서를 준다."""
    return int(uuid.uuid5(uuid.NAMESPACE_URL, pid).hex[:8], 16)


def public_post(p, team, admin=False):
    """보는 사람(조)에 맞게 게시글을 잘라서 보낸다.
    공개 전에는 어느 조가 언제 만들었는지, 운영실 자료인지를 숨긴다. 그래야 "조 게시물은 다 가짜"가 티 나지 않는다."""
    reveal = DB['phase'] == 'reveal'
    own = bool(team) and p['team'] == team
    out = {k: p.get(k) for k in PUBLIC_FIELDS}
    out['order'] = order_key(p['id'])
    if own:
        out['mine'] = True
        out['secret'] = p.get('secret')
        out['aiGenerated'] = p.get('aiGenerated')
    if admin or reveal:
        out.update(seed=bool(p.get('seed')), team=p['team'], secret=p.get('secret'), answer=p.get('answer'),
                   aiGenerated=p.get('aiGenerated'), aiPrompt=p.get('aiPrompt'), counts=verdict_counts(p['id']))
    if admin:
        out.update(createdAt=p.get('createdAt'), seedKey=p.get('seedKey'))
    return out


def visible_to(p, team, admin):
    if admin:
        return True
    if p['status'] != 'approved':
        return False
    if p.get('seed') or (team and p['team'] == team):
        return True
    # 다른 조 게시물은 판별 시간부터 보인다 (만드는 동안 새 글이 뜨면 조 게시물인 게 티 남)
    return DB['phase'] in ('judge', 'reveal')


def state_for(team, admin=False):
    posts = [public_post(p, team, admin) for p in DB['posts'] if visible_to(p, team, admin)]
    mine = {}
    if team:
        for k, j in DB['judgments'].items():
            pid, t = k.rsplit(':', 1)
            if int(t) == team:
                mine[pid] = j
    res = {'version': DB['version'], 'phase': DB['phase'], 'posts': posts, 'myJudgments': mine,
           'aiQuota': AI_QUOTA, 'aiUsed': DB['aiUsed'].get(str(team), 0) if team else 0,
           'aiEnabled': bool(GEMINI_KEY), 'maxPosts': MAX_POSTS_PER_TEAM}
    if admin or DB['phase'] == 'reveal':
        res['scores'] = compute_scores()
    if admin:
        res['judgments'] = DB['judgments']
        res['aiUsedAll'] = DB['aiUsed']
    return res


# ---------- 입력 정리 ----------
def clean_text(v, limit):
    if not isinstance(v, str):
        return ''
    v = v.replace('\r', '').strip()
    return v[:limit]


def clean_team(v):
    try:
        t = int(v)
    except (TypeError, ValueError):
        return None
    return t if 1 <= t <= TEAM_COUNT else None


def clean_image_id(v):
    if isinstance(v, str) and re.fullmatch(r'[a-f0-9]{32}\.(jpg|png|webp)', v) and os.path.exists(os.path.join(UPLOAD_DIR, v)):
        return v
    return None


def sniff_ext(raw):
    if raw[:3] == b'\xff\xd8\xff':
        return 'jpg'
    if raw[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    if raw[:4] == b'RIFF' and raw[8:12] == b'WEBP':
        return 'webp'
    return None


def store_image(raw):
    ext = sniff_ext(raw)
    if not ext:
        raise ValueError('이미지 파일만 올릴 수 있습니다.')
    if len(raw) > MAX_UPLOAD:
        raise ValueError('사진 용량이 너무 큽니다.')
    name = f'{uuid.uuid4().hex}.{ext}'
    with open(os.path.join(UPLOAD_DIR, name), 'wb') as f:
        f.write(raw)
    return name


def decode_data_url(s):
    m = re.match(r'data:image/[a-z+]+;base64,(.*)$', s or '', re.S)
    if not m:
        raise ValueError('사진 형식이 올바르지 않습니다.')
    return base64.b64decode(m.group(1))


# ---------- Gemini ----------
def gemini(model, parts, image=False):
    if not GEMINI_KEY:
        raise RuntimeError('AI 기능이 꺼져 있습니다. 운영자에게 알려 주세요.')
    body = {'contents': [{'role': 'user', 'parts': parts}]}
    if image:
        body['generationConfig'] = {'responseModalities': ['IMAGE']}
    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        data=json.dumps(body).encode(), method='POST',
        headers={'Content-Type': 'application/json', 'x-goog-api-key': GEMINI_KEY})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', 'replace')[:300]
        raise RuntimeError(f'AI 요청이 실패했습니다 ({e.code}). {detail}')


def gemini_image(prompt, base_image=None):
    parts = [{'text': AI_STYLE + prompt}]
    if base_image:
        path = os.path.join(UPLOAD_DIR, base_image)
        mime = {'jpg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}[base_image.rsplit('.', 1)[1]]
        with open(path, 'rb') as f:
            parts.append({'inline_data': {'mime_type': mime, 'data': base64.b64encode(f.read()).decode()}})
    res = gemini(IMAGE_MODEL, parts, image=True)
    for c in res.get('candidates', []):
        for part in c.get('content', {}).get('parts', []):
            data = part.get('inlineData') or part.get('inline_data')
            if data and data.get('data'):
                return base64.b64decode(data['data'])
    raise RuntimeError('AI가 이 요청으로는 그림을 만들지 않았습니다. 표현을 바꿔 다시 시도해 주세요.')


def gemini_polish(text, fmt):
    style = {'news': '신문 기사체(~했다, ~로 알려졌다)', 'sns': 'SNS 게시글 말투(짧고 생생하게, 해시태그 1~2개)',
             'witness': '목격담 말투(~했어요, 직접 겪은 듯)', 'notice': '공지문 말투(~합니다, ~바랍니다)'}[fmt]
    prompt = (f'다음 글을 {style}로 다듬어라. 내용(사실 관계, 날짜, 이름)은 바꾸지 말고 문장만 다듬는다. '
              f'초등학생이 읽을 수 있는 쉬운 말로, 5문장 이내. 다듬은 글만 출력한다.\n\n{text}')
    res = gemini(TEXT_MODEL, [{'text': prompt}])
    for c in res.get('candidates', []):
        txt = ''.join(p.get('text', '') for p in c.get('content', {}).get('parts', []))
        if txt.strip():
            return txt.strip()[:1200]
    raise RuntimeError('AI가 글을 다듬지 못했습니다.')


# ---------- HTTP ----------
class Handler(BaseHTTPRequestHandler):
    server_version = 'DorogramServer/1.0'

    def log_message(self, fmt, *args):
        if '/api/ch5/stream' not in (args[0] if args else ''):
            super().log_message(fmt, *args)

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def fail(self, msg, code=400):
        self.send_json({'error': msg}, code)

    def read_json(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n > MAX_UPLOAD * 2:
            raise ValueError('요청이 너무 큽니다.')
        return json.loads(self.rfile.read(n) or b'{}')

    def is_admin(self):
        return self.headers.get('X-Admin-Key') == ADMIN_KEY

    # GET
    def do_GET(self):
        u = urlparse(self.path)
        path, qs = u.path, parse_qs(u.query)
        if path == '/api/ch5/state':
            team = clean_team((qs.get('team') or [None])[0])
            with lock:
                return self.send_json(state_for(team))
        if path == '/api/ch5/admin/state':
            if not self.is_admin():
                return self.fail('운영자 비밀번호가 맞지 않습니다.', 403)
            with lock:
                return self.send_json(state_for(None, admin=True))
        if path == '/api/ch5/stream':
            return self.stream()
        m = re.fullmatch(r'/api/ch5/img/([a-f0-9]{32}\.(jpg|png|webp))', path)
        if m:
            return self.send_file(os.path.join(UPLOAD_DIR, m.group(1)), cache=True)
        if SERVE_STATIC and not path.startswith('/api/'):
            return self.send_static(path)
        self.fail('없는 주소입니다.', 404)

    def stream(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Accel-Buffering', 'no')
        self.end_headers()
        q = queue.Queue()
        with listeners_lock:
            listeners.append(q)
        try:
            self.wfile.write(f'data: {json.dumps({"v": DB["version"], "phase": DB["phase"]})}\n\n'.encode())
            self.wfile.flush()
            while True:
                try:
                    msg = q.get(timeout=20)
                    self.wfile.write(f'data: {msg}\n\n'.encode())
                except queue.Empty:
                    self.wfile.write(b': ping\n\n')
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass
        finally:
            with listeners_lock:
                if q in listeners:
                    listeners.remove(q)

    def send_file(self, fp, cache=False):
        if not os.path.isfile(fp):
            return self.fail('파일이 없습니다.', 404)
        ext = fp.rsplit('.', 1)[-1].lower()
        ctype = {'html': 'text/html; charset=utf-8', 'js': 'text/javascript; charset=utf-8', 'css': 'text/css',
                 'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'webp': 'image/webp',
                 'svg': 'image/svg+xml', 'txt': 'text/plain; charset=utf-8', 'json': 'application/json',
                 'mp3': 'audio/mpeg', 'mp4': 'video/mp4', 'pdf': 'application/pdf'}.get(ext, 'application/octet-stream')
        with open(fp, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'public, max-age=31536000, immutable' if cache else 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def send_static(self, path):
        rel = unquote(path).lstrip('/')
        if rel == '' or rel.endswith('/'):
            rel += 'index.html'
        fp = os.path.normpath(os.path.join(ROOT, rel))
        base = os.path.basename(fp)
        if (not fp.startswith(ROOT) or os.sep + 'server' + os.sep in fp or base.startswith('.')
                or base.rsplit('.', 1)[-1].lower() in ('pem', 'py', 'ps1', 'sh', 'md')):
            return self.fail('없는 주소입니다.', 404)
        if os.path.isdir(fp):
            fp = os.path.join(fp, 'index.html')
        self.send_file(fp)

    # POST
    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self.read_json()
        except (ValueError, json.JSONDecodeError):
            return self.fail('요청 형식이 올바르지 않습니다.')
        routes = {
            '/api/ch5/upload': self.upload, '/api/ch5/posts': self.save_post, '/api/ch5/judge': self.judge,
            '/api/ch5/ai/image': self.ai_image, '/api/ch5/ai/polish': self.ai_polish,
            '/api/ch5/admin/phase': self.admin_phase, '/api/ch5/admin/moderate': self.admin_moderate,
            '/api/ch5/admin/reset': self.admin_reset, '/api/ch5/admin/delete': self.admin_delete,
            '/api/ch5/admin/delete-team-posts': self.admin_delete_team_posts, '/api/ch5/posts/delete': self.delete_own_post,
        }
        fn = routes.get(path)
        if not fn:
            return self.fail('없는 주소입니다.', 404)
        if path.startswith('/api/ch5/admin/') and not self.is_admin():
            return self.fail('운영자 비밀번호가 맞지 않습니다.', 403)
        try:
            fn(body)
        except ValueError as e:
            self.fail(str(e))
        except RuntimeError as e:
            self.fail(str(e), 502)

    def upload(self, b):
        if not clean_team(b.get('team')):
            raise ValueError('조를 먼저 골라 주세요.')
        name = store_image(decode_data_url(b.get('dataUrl')))
        self.send_json({'imageId': name})

    def save_post(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('조를 먼저 골라 주세요.')
        fmt = b.get('format')
        if fmt not in FORMATS:
            raise ValueError('게시글 형식을 골라 주세요.')
        secret = b.get('secret') or {}
        a = b.get('author') or {}
        post = {
            'format': fmt,
            'author': {'name': clean_text(a.get('name'), 30), 'handle': clean_text(a.get('handle'), 30),
                       'joined': clean_text(a.get('joined'), 20), 'followers': clean_text(a.get('followers'), 12),
                       'color': clean_text(a.get('color'), 12), 'reporter': clean_text(a.get('reporter'), 20)},
            'likes': clean_text(b.get('likes'), 10),
            'views': clean_text(b.get('views'), 10),
            'thumbTpl': b.get('thumbTpl') if b.get('thumbTpl') in THUMB_TPLS else 'auto',
            'thumbTitle': clean_text(b.get('thumbTitle'), 60),
            'thumbImageId': clean_image_id(b.get('thumbImageId')),
            'title': clean_text(b.get('title'), 80),
            'body': clean_text(b.get('body'), 1200),
            'tags': clean_text(b.get('tags'), 80),
            'place': clean_text(b.get('place'), 40),
            'postedAt': clean_text(b.get('postedAt'), 20),
            'photoTakenAt': clean_text(b.get('photoTakenAt'), 20),
            'imageId': clean_image_id(b.get('imageId')),
            'secret': {'truth': 'real' if secret.get('truth') == 'real' else 'fake', 'tactic': clean_text(secret.get('tactic'), 30),
                       'clue': clean_text(secret.get('clue'), 200), 'clueCriterion': secret.get('clueCriterion')
                       if secret.get('clueCriterion') in CRITERIA else None},
        }
        if not post['body'] and not post['title']:
            raise ValueError('제목이나 본문을 써 주세요.')
        if not post['secret']['clue']:  # 가짜면 숨긴 단서, 진짜면 근거가 된 사실 카드
            raise ValueError('가짜 게시글에는 들킬 수 있는 단서를 하나 꼭 적어 주세요.')
        with lock:
            if DB['phase'] != 'make':
                raise ValueError('지금은 게시글을 만드는 시간이 아닙니다.')
            pid = b.get('id')
            if pid:
                old = find_post(pid)
                if not old or old['team'] != team:
                    raise ValueError('고칠 수 없는 게시글입니다.')
                ai_meta = {k: old.get(k) for k in ('aiGenerated', 'aiPrompt')}
                if post['imageId'] != old.get('imageId'):
                    ai_meta = self.image_meta(post['imageId'])
                old.update(post, **ai_meta, updatedAt=now_ms())
                saved = old
            else:
                active = [p for p in DB['posts'] if p['team'] == team]
                if len(active) >= MAX_POSTS_PER_TEAM:
                    raise ValueError(f'게시글은 조마다 {MAX_POSTS_PER_TEAM}개까지 올릴 수 있습니다.')
                saved = dict(post, id='p' + uuid.uuid4().hex[:10], team=team, status='approved', note='',
                             createdAt=now_ms(), **self.image_meta(post['imageId']))
                DB['posts'].append(saved)
            save_and_broadcast()
            self.send_json({'post': public_post(saved, team)})

    def image_meta(self, image_id):
        meta = DB.get('aiImages', {}).get(image_id) if image_id else None
        return {'aiGenerated': bool(meta), 'aiPrompt': meta.get('prompt') if meta else None}

    def judge(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('조를 먼저 골라 주세요.')
        verdict, criterion = b.get('verdict'), b.get('criterion')
        if verdict not in VERDICTS:
            raise ValueError('진짜, 가짜, 모르겠음 중에 골라 주세요.')
        if verdict != 'unsure' and criterion not in CRITERIA:
            raise ValueError('어떤 기준으로 판단했는지 골라 주세요.')
        with lock:
            p = find_post(b.get('postId'))
            if not p or p['status'] != 'approved':
                raise ValueError('판별할 수 없는 게시글입니다.')
            if p['team'] == team:
                raise ValueError('우리 조 게시글은 판별하지 않습니다.')
            if DB['phase'] != 'judge':
                raise ValueError('지금은 판별하는 시간이 아닙니다.')
            DB['judgments'][judgment_key(p['id'], team)] = {
                'verdict': verdict, 'criterion': criterion if criterion in CRITERIA else None,
                'reason': clean_text(b.get('reason'), 120), 'at': now_ms()}
            save_and_broadcast()
            self.send_json({'ok': True, 'post': public_post(p, team)})

    def ai_image(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('조를 먼저 골라 주세요.')
        prompt = clean_text(b.get('prompt'), 300)
        if len(prompt) < 4:
            raise ValueError('어떤 그림을 만들지 조금 더 자세히 써 주세요.')
        bad = [w for w in BLOCKED_WORDS if w in prompt]
        if bad:
            raise ValueError(f'"{bad[0]}" 같은 표현은 쓸 수 없습니다. 다른 말로 바꿔 주세요.')
        base = clean_image_id(b.get('baseImageId'))
        with lock:
            if DB['phase'] != 'make':
                raise ValueError('지금은 게시글을 만드는 시간이 아닙니다.')
            used = DB['aiUsed'].get(str(team), 0)
            if used >= AI_QUOTA:
                raise ValueError(f'AI 이미지는 조마다 {AI_QUOTA}번까지 만들 수 있습니다.')
            DB['aiUsed'][str(team)] = used + 1   # 실패해도 한 번 쓴 것으로 센다(연타 방지). 실패 시 아래에서 되돌림.
        try:
            raw = gemini_image(prompt, base)
        except RuntimeError:
            with lock:
                DB['aiUsed'][str(team)] = max(0, DB['aiUsed'].get(str(team), 1) - 1)
            raise
        name = store_image(raw)
        with lock:
            DB.setdefault('aiImages', {})[name] = {'team': team, 'prompt': prompt, 'base': base, 'at': now_ms()}
            save_and_broadcast()
            self.send_json({'imageId': name, 'aiUsed': DB['aiUsed'][str(team)], 'aiQuota': AI_QUOTA})

    def ai_polish(self, b):
        if not clean_team(b.get('team')):
            raise ValueError('조를 먼저 골라 주세요.')
        text = clean_text(b.get('text'), 1200)
        if len(text) < 5:
            raise ValueError('다듬을 글을 먼저 써 주세요.')
        fmt = b.get('format') if b.get('format') in FORMATS else 'news'
        self.send_json({'text': gemini_polish(text, fmt)})

    def admin_phase(self, b):
        if b.get('phase') not in PHASES:
            raise ValueError('없는 단계입니다.')
        with lock:
            DB['phase'] = b['phase']
            save_and_broadcast()
            self.send_json({'phase': DB['phase']})

    def admin_moderate(self, b):
        action = b.get('action')
        if action not in ('hide', 'show'):
            raise ValueError('없는 동작입니다.')
        with lock:
            p = find_post(b.get('postId'))
            if not p:
                raise ValueError('없는 게시글입니다.')
            p['status'] = 'hidden' if action == 'hide' else 'approved'
            p['note'] = clean_text(b.get('note'), 120)
            save_and_broadcast()
            self.send_json({'ok': True})

    def delete_own_post(self, b):
        """아이들: 만들기 단계에서 우리 조 게시물 지우기."""
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('조를 먼저 골라 주세요.')
        with lock:
            if DB['phase'] != 'make':
                raise ValueError('게시물은 만들기 시간에만 지울 수 있습니다.')
            p = find_post(b.get('postId'))
            if not p or p.get('seed') or p['team'] != team:
                raise ValueError('지울 수 없는 게시물입니다.')
            remove_posts([p])
            save_and_broadcast()
            self.send_json({'ok': True})

    def admin_delete(self, b):
        """운영자: 조 게시물 하나 완전히 삭제(사진 파일 포함). 운영실 자료는 숨기기만 가능."""
        with lock:
            p = find_post(b.get('postId'))
            if not p:
                raise ValueError('없는 게시글입니다.')
            if p.get('seed'):
                raise ValueError('운영실 자료는 지울 수 없습니다. 숨기기를 써 주세요.')
            remove_posts([p])
            save_and_broadcast()
            self.send_json({'ok': True})

    def admin_delete_team_posts(self, b):
        """운영자: 조 게시물 전부 삭제(판별 기록도 함께). 운영실 자료·단계·AI 사용 횟수는 그대로."""
        if b.get('confirm') != 'DELETE':
            raise ValueError('확인 문구가 필요합니다.')
        with lock:
            targets = [p for p in DB['posts'] if not p.get('seed')]
            if b.get('team'):
                t = clean_team(b.get('team'))
                targets = [p for p in targets if p['team'] == t]
            remove_posts(targets)
            save_and_broadcast()
            self.send_json({'ok': True, 'deleted': len(targets)})

    def admin_reset(self, b):
        global DB
        if b.get('confirm') != 'RESET':
            raise ValueError('확인 문구가 필요합니다.')
        with lock:
            version = DB['version']
            DB = fresh_db()
            DB['version'] = version
            save_and_broadcast()
            self.send_json({'ok': True})


def main():
    global DB
    DB = read_db()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    srv.daemon_threads = True
    print(f'도로그램 서버: http://{HOST}:{PORT}/chapter05/feed.html  (운영자: /chapter05/feed-admin.html)')
    print(f'AI 이미지: {"켜짐 (" + IMAGE_MODEL + ")" if GEMINI_KEY else "꺼짐 (GEMINI_API_KEY 없음)"}')
    srv.serve_forever()


if __name__ == '__main__':
    main()
