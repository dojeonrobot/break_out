#!/usr/bin/env python3
"""챕터 5 「보이드의 기록」 스캔 링크 제출 서버 (표준 라이브러리만 사용, 추가 설치 없음).

chapter05/index.html(보이드의 기록)과 chapter05/feed.html(도로그램 사이드바 현황)이 쓰는 API.
조별로 어느 구역에 어떤 Scaniverse 링크를 냈는지 저장하고, 운영자(비밀번호)가 전체 목록 확인·삭제·초기화를 한다.
도로그램 서버(ch5_feed_server.py)와는 완전히 별개다.
- 제출 기록: data/ch5_void.json (gitignore)
- 짝 목록: ch5_void_pairs.json (erica-twin build.py가 dist/void-pairs.json으로 만든 것. 캠퍼스 지점 ↔ 섬 구역, 이미 3D에 들어간 스캔 id)
- 초기화: 제출 기록을 지우고, 페이지에 이미 3D로 들어가 있는 스캔은 "숨김" 목록에 넣어 구역을 다시 "복구 필요"로 되돌린다.
  (3D 데이터 자체는 페이지에 박혀 있으므로 지우지 않고 숨기기만 한다. "되살리기"로 되돌릴 수 있다.)
- 썸네일: /api/void/thumb/<scanId> 가 Scaniverse 미리보기 사진을 받아 data/thumbs/ 에 캐시해 준다(핫링크 차단·CSP 회피).
- 자체 카메라 스캔(v2, 2026-10-13~27)은 2026-10-30에 제거됨: 구역 복구는 Scaniverse 링크 1건. 옛 사진 세트는 data/scans_trash/ 에 남아 있을 수 있다.
- 운영자 공지(2026-10-30): POST /api/void/admin/notice {text} → DB notice {id,text,t}(빈 text면 내림), state()의 notice로 모든 태블릿에 내려간다.

실행:
    python server/ch5_void_server.py           # http://localhost:8096/chapter05/index.html
환경변수:
    VOID_PORT=8096  VOID_HOST=127.0.0.1  CH5_ADMIN_KEY=0101  VOID_STATIC=1 (저장소 파일도 서빙, 로컬 확인용)
- 링크 자동 변환(v3, 2026-10-13): Scaniverse 링크가 제출되면 백그라운드 스레드가 스캔 페이지의 __NEXT_DATA__에서 가우시안 SPZ 주소·카메라 정보를 읽어
  내려받고 spz2splat.py(numpy)로 .splat(32B/점)로 바꾼 뒤 gzip+base64 텍스트 data/splats/<id>.splat.txt 로 둔다(페이지의 loadSplat이 그대로 읽음).
  제출 기록에 splat:{center,radius,yaw,pitch,points,...}가 붙고 auto면 status ok(복구됨), 아니면 pend(운영자 확정). 실패하면 error 문구.
- 조별 위치(v3): POST /api/void/pos {team,lat,lng,acc} → 메모리(POS)에 최근 위치, state()의 pos로 내려감(3분 지나면 빠짐).
"""
import base64
import gzip
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data')
THUMB_DIR = os.path.join(DATA_DIR, 'thumbs')
SPLAT_DIR = os.path.join(DATA_DIR, 'splats')
try:
    from spz2splat import convert as spz_convert
except Exception:          # numpy 없는 환경: 링크는 받되 변환은 못 한다
    spz_convert = None
POS = {}                   # team -> {'lat','lng','acc','t'}
POS_TTL_MS = 3 * 60 * 1000
DB_PATH = os.path.join(DATA_DIR, 'ch5_void.json')
PAIRS_PATH = os.path.join(HERE, 'ch5_void_pairs.json')

PORT = int(os.environ.get('VOID_PORT', '8096'))
HOST = os.environ.get('VOID_HOST', '127.0.0.1')
ADMIN_KEY = os.environ.get('CH5_ADMIN_KEY', '0101')
SERVE_STATIC = os.environ.get('VOID_STATIC', '1') == '1'

MAX_TEAM = 12
SCAN_ID = re.compile(r'^[a-z0-9]{6,40}$')
MISSION_ID = re.compile(r'^[a-z0-9_-]{1,40}$')
QUEST_ID = re.compile(r'^q[1-9]$')          # 섬 미션 id (페이지 QUESTS)
UA = 'Mozilla/5.0 (DOROLAND void record)'

lock = threading.Lock()
DB = None
PAIRS = []


def now_ms():
    return int(time.time() * 1000)


def fresh_db():
    return {'version': 0, 'subs': [], 'hidden': [], 'auto': True, 'reset': 0, 'quests': {}, 'notice': None}


def read_db():
    try:
        with open(DB_PATH, encoding='utf-8') as f:
            db = json.load(f)
        for k, v in fresh_db().items():
            db.setdefault(k, v)
        return db
    except (OSError, ValueError):
        return fresh_db()


def read_pairs():
    try:
        with open(PAIRS_PATH, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def save():
    DB['version'] += 1
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DB_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(DB, f, ensure_ascii=False, indent=1)
    os.replace(tmp, DB_PATH)


def clean_team(v):
    try:
        n = int(v)
    except (TypeError, ValueError):
        return None
    return n if 1 <= n <= MAX_TEAM else None


def clean_text(v, limit):
    return re.sub(r'\s+', ' ', str(v or '')).strip()[:limit]


def is_done(s):
    """변환된 Scaniverse 스캔이 status ok면 복구된 것으로 본다."""
    return s.get('status') == 'ok' and bool(s.get('splat'))


def team_done(d, q):
    """조가 미션 q를 끝냈나(현황판·큰 화면용): 조의 태블릿 중 하나라도 끝냈으면. 태블릿끼리는 독립이다 (2026-10-30)."""
    if not d:
        return False
    if any(k.startswith('q') for k in d):      # 글자 없이 저장된 옛 형식
        return q in d
    return any(isinstance(v, dict) and q in v for v in d.values())


def pair_status():
    """짝마다 복구 상태: ok(3D에 들어간 스캔이 보이거나 자체 스캔이 확정됨) / pend(제출됨) / void."""
    hidden = set(DB['hidden'])
    out = []
    quests = DB.get('quests', {})
    for p in PAIRS:
        if p.get('kind') == 'quest':   # 섬 미션으로 복구되는 구역: 그 미션을 끝낸 조가 하나라도 있으면 ok
            teams = sorted(int(t) for t, d in quests.items() if team_done(d, p['quest']))
            out.append({'id': p['id'], 'kind': 'quest', 'quest': p['quest'], 'island': p['island'], 'status': 'ok' if teams else 'void',
                        'teams': teams, 'scans': [], 'subs': []})
            continue
        ids = {p['campus']['id'], p['island']['id']}
        shown = [s for s in p.get('scans', []) if s not in hidden]
        mine = [s for s in DB['subs'] if s['mission'] in ids]
        oks = [s['scanId'] for s in mine if is_done(s)]
        subs = [s for s in mine if s['scanId'] not in shown and not is_done(s)]
        st = 'ok' if (shown or oks) else 'pend' if subs else 'void'
        out.append({'id': p['id'], 'campus': p['campus'], 'island': p['island'], 'status': st,
                    'teams': sorted({s['team'] for s in subs}), 'scans': shown + oks,
                    'subs': [{'scanId': s['scanId'], 'team': s['team'], 'note': s.get('note', ''), 'caption': s.get('caption', ''),
                              'kind': s.get('kind', 'link'), 'createdAt': s['createdAt']} for s in subs]})
    return out


def live_pos():
    now = now_ms()
    return {str(t): v for t, v in POS.items() if now - v['t'] < POS_TTL_MS}


def state():
    return {'version': DB['version'], 'subs': DB['subs'], 'hidden': DB['hidden'], 'auto': bool(DB.get('auto', True)), 'reset': int(DB.get('reset', 0)),
            'quests': DB.get('quests', {}), 'pairs': pair_status(), 'pos': live_pos(), 'notice': DB.get('notice'), 'now': now_ms()}


# ---------- Scaniverse 링크 → 스플랫 자동 변환 ----------
def scan_page(scan_id):
    """Scaniverse 공유 페이지의 __NEXT_DATA__: 미디어 주소와 카메라 시작 시점."""
    req = urllib.request.Request(f'https://scaniverse.com/scan/{scan_id}', headers={'User-Agent': UA})
    html = urllib.request.urlopen(req, timeout=20).read(3_000_000).decode('utf-8', 'ignore')
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise ValueError('스캔 페이지를 읽지 못했습니다')
    nd = json.loads(m.group(1))['props']['pageProps']
    return nd['scan'], nd.get('user') or {}


def set_sub(sub_id, **fields):
    with lock:
        for sb in DB['subs']:
            if sb['id'] == sub_id:
                sb.update(fields)
                save()
                return True
    return False


def convert_scan(sub_id, scan_id):
    """백그라운드: SPZ를 받아 .splat로 바꾸고 gzip+base64 텍스트로 저장한 뒤 제출 기록에 splat 정보를 붙인다."""
    try:
        if spz_convert is None:
            raise ValueError('서버에 변환 모듈(numpy)이 없습니다')
        sc, user = scan_page(scan_id)
        if sc.get('modelType') != 'gaussians':
            raise ValueError('가우시안 스플랫 스캔이 아닙니다 (Scaniverse에서 Splat으로 처리한 스캔만 됩니다)')
        os.makedirs(SPLAT_DIR, exist_ok=True)
        spz = os.path.join(SPLAT_DIR, scan_id + '.spz')
        splat = os.path.join(SPLAT_DIR, scan_id + '.splat')
        raw = urllib.request.urlopen(urllib.request.Request(sc['media']['gaussians'], headers={'User-Agent': UA}), timeout=180).read()
        with open(spz, 'wb') as f:
            f.write(raw)
        info = spz_convert(spz, splat)
        with open(splat, 'rb') as f:
            txt = base64.b64encode(gzip.compress(f.read(), mtime=0)).decode('ascii')
        with open(os.path.join(SPLAT_DIR, scan_id + '.splat.txt'), 'w') as f:
            f.write(txt)
        for fp in (spz, splat):
            try:
                os.remove(fp)
            except OSError:
                pass
        md, loc = sc.get('metadata') or {}, sc.get('location') or {}
        meta = {'center': md.get('center'), 'radius': (md.get('radius') or {}).get('start'), 'yaw': (md.get('yaw') or {}).get('start'),
                'pitch': (md.get('pitch') or {}).get('start'), 'points': int(info.get('points', 0)), 'captured': md.get('capturedAt') or sc.get('createdAt'),
                'lat': loc.get('lat'), 'lng': loc.get('lng'), 'caption': clean_text(sc.get('caption'), 60), 'author': clean_text(user.get('username'), 40)}
        with lock:
            auto = bool(DB.get('auto', True))
        set_sub(sub_id, splat=meta, error='', status='ok' if auto else 'pend')
    except Exception as e:
        set_sub(sub_id, error=clean_text(str(e), 140)[:140], status='pend')








def scan_meta(scan_id):
    """Scaniverse 공유 페이지의 og:title(스캔 제목)·설명(@작성자)을 읽는다. 실패해도 제출은 된다."""
    try:
        req = urllib.request.Request(f'https://scaniverse.com/scan/{scan_id}', headers={'User-Agent': UA})
        html = urllib.request.urlopen(req, timeout=6).read(200000).decode('utf-8', 'ignore')
        title = re.search(r'property="og:title"\s+content="([^"]*)"', html)
        desc = re.search(r'property="og:description"\s+content="([^"]*)"', html)
        author = re.search(r'@([\w.]+)', desc.group(1)) if desc else None
        return clean_text(title.group(1) if title else '', 60), (author.group(1) if author else '')
    except Exception:
        return '', ''


def fetch_thumb(scan_id):
    os.makedirs(THUMB_DIR, exist_ok=True)
    fp = os.path.join(THUMB_DIR, scan_id + '.jpg')
    if os.path.isfile(fp):
        return fp
    try:
        req = urllib.request.Request(f'https://scaniverse.com/api/media/{scan_id}/preview.jpg', headers={'User-Agent': UA})
        raw = urllib.request.urlopen(req, timeout=8).read(5 * 1024 * 1024)
        if not raw.startswith(b'\xff\xd8'):
            return None
        with open(fp + '.tmp', 'wb') as f:
            f.write(raw)
        os.replace(fp + '.tmp', fp)
        return fp
    except Exception:
        return None


class Handler(BaseHTTPRequestHandler):
    server_version = 'VoidRecordServer/3.0'

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
        if n > 64 * 1024:
            raise ValueError('요청이 너무 큽니다.')
        return json.loads(self.rfile.read(n) or b'{}')


    def is_admin(self):
        return self.headers.get('X-Admin-Key') == ADMIN_KEY

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/void/state':
            qs = parse_qs(urlparse(self.path).query)
            dev = re.sub(r'[^a-z0-9]', '', (qs.get('dev') or [''])[0])[:16]; team = clean_team((qs.get('team') or [''])[0])
            with lock:
                if dev and team:      # the tablet is alive: note it (stale tablets drop out of the team's "everyone finished" rule)
                    tq = DB.setdefault('quests', {}).get(str(team), {})
                    for l, v in tq.items():
                        if isinstance(v, dict) and v.get('dev') == dev:
                            v['seen'] = now_ms()
                return self.send_json(state())
        if path == '/api/void/admin/state':
            if not self.is_admin():
                return self.fail('운영자 비밀번호가 맞지 않습니다.', 403)
            with lock:
                return self.send_json(dict(state(), admin=True))
        m = re.fullmatch(r'/api/void/thumb/([a-z0-9]{6,40})', path)
        if m:
            fp = fetch_thumb(m.group(1))
            if not fp:
                return self.fail('미리보기를 가져오지 못했습니다.', 404)
            return self.send_bytes(open(fp, 'rb').read(), 'image/jpeg', cache=True)
        m = re.fullmatch(r'/api/void/splat/([a-z0-9]{6,40})\.txt', path)
        if m:
            fp = os.path.join(SPLAT_DIR, m.group(1) + '.splat.txt')
            if not os.path.isfile(fp):
                return self.fail('아직 변환되지 않은 스캔입니다.', 404)
            return self.send_bytes(open(fp, 'rb').read(), 'text/plain; charset=us-ascii', cache=True)
        if SERVE_STATIC and not path.startswith('/api/'):
            return self.send_static(path)
        self.fail('없는 주소입니다.', 404)

    def send_bytes(self, data, ctype, cache=False):
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Cache-Control', 'public, max-age=86400' if cache else 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_static(self, path):
        rel = unquote(path).lstrip('/') or 'index.html'
        fp = os.path.normpath(os.path.join(ROOT, rel))
        if os.path.isdir(fp):
            fp = os.path.join(fp, 'index.html')
        if not fp.startswith(ROOT) or not os.path.isfile(fp):
            return self.fail('없는 파일입니다.', 404)
        ext = os.path.splitext(fp)[1].lower()
        ctype = {'.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.css': 'text/css',
                 '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.txt': 'text/plain'}.get(ext, 'application/octet-stream')
        with open(fp, 'rb') as f:
            self.send_bytes(f.read(), ctype)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self.read_json()
        except (ValueError, json.JSONDecodeError):
            return self.fail('요청 형식이 올바르지 않습니다.')
        routes = {
            '/api/void/submit': self.submit, '/api/void/unsubmit': self.unsubmit,
            '/api/void/pos': self.pos, '/api/void/admin/notice': self.admin_notice,
            '/api/void/admin/convert': self.admin_convert,
            '/api/void/admin/delete': self.admin_delete, '/api/void/admin/reset': self.admin_reset,
            '/api/void/admin/unhide': self.admin_unhide, '/api/void/admin/approve': self.admin_approve,
            '/api/void/admin/auto': self.admin_auto,
            '/api/void/quest': self.quest, '/api/void/admin/quest': self.admin_quest, '/api/void/team_reset': self.team_reset,
        }
        fn = routes.get(path)
        if not fn:
            return self.fail('없는 주소입니다.', 404)
        if path.startswith('/api/void/admin/') and not self.is_admin():
            return self.fail('운영자 비밀번호가 맞지 않습니다.', 403)
        try:
            fn(body)
        except ValueError as e:
            self.fail(str(e))

    # 학생: 구역 카드에서 링크 제출
    def submit(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('우리 조를 먼저 고르세요.')
        scan_id = str(b.get('scanId') or '').lower()
        if not SCAN_ID.match(scan_id):
            raise ValueError('Scaniverse 스캔 링크가 아닙니다.')
        mission = str(b.get('mission') or '')
        if not MISSION_ID.match(mission):
            raise ValueError('구역 정보가 없습니다.')
        with lock:
            dup = next((s for s in DB['subs'] if s['scanId'] == scan_id), None)
        if dup:
            raise ValueError(f'이미 제출된 링크입니다 ({dup["team"]}조).')
        caption, author = scan_meta(scan_id)      # 네트워크는 잠금 밖에서
        with lock:
            if any(s['scanId'] == scan_id for s in DB['subs']):
                raise ValueError('이미 제출된 링크입니다.')
            sub_id = uuid.uuid4().hex[:12]
            DB['subs'].append({
                'id': sub_id, 'scanId': scan_id, 'kind': 'link', 'url': f'https://scaniverse.com/scan/{scan_id}',
                'mission': mission, 'team': team, 'note': clean_text(b.get('note'), 60),
                'caption': caption, 'author': author, 'status': 'pend', 'createdAt': now_ms(),
            })
            save()
            self.send_json(state())
        threading.Thread(target=fetch_thumb, args=(scan_id,), daemon=True).start()
        threading.Thread(target=convert_scan, args=(sub_id, scan_id), daemon=True).start()

    # 학생: 우리 조 처음부터 — 이 조의 제출과 미션·막·튜토리얼 진행을 모두 지운다 (2026-10-27).
    # 2026-10-30: 같이 다니는 선생님의 비밀번호(X-Admin-Key)가 있어야 한다 — 아이가 혼자 눌러 조 전체를 날리지 않게.
    def team_reset(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('우리 조를 먼저 고르세요.')
        if b.get('confirm') != 'AGAIN':
            raise ValueError('확인 문구가 필요합니다.')
        if not self.is_admin():
            raise ValueError('선생님 비밀번호가 맞지 않습니다.')
        with lock:
            DB['subs'] = [s for s in DB['subs'] if s['team'] != team]
            DB.setdefault('quests', {}).pop(str(team), None)
            save()
            self.send_json(state())

    # 학생: 우리 조의 섬 미션 진행(끝낸 미션 id 목록 전체를 보냄) — 태블릿을 바꿔도 이어지게 서버에 둔다 (2026-10-27)
    def quest(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('우리 조를 먼저 고르세요.')
        self.set_quests(team, b)

    # 운영자: 어느 조든 미션 완료 처리·되돌리기·초기화({team, done:[...]} 또는 {team, clear:true})
    def admin_quest(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('조 번호가 없습니다.')
        self.set_quests(team, b)

    def set_quests(self, team, b):
        # quests[team] = {'a': {'dev': 태블릿 id, 'q1': ts, ..., 'act': 본 막, 'tut': 튜토리얼 끝낸 시각}, 'b': {...}} — 조 안의 태블릿마다 한 칸 (2026-10-27)
        dev = re.sub(r'[^a-z0-9]', '', str(b.get('dev') or ''))[:16]
        letter = str(b.get('letter') or '')
        with lock:
            q = DB.setdefault('quests', {})
            tq = q.get(str(team), {})
            if any(k.startswith('q') or k in ('act', 'tut') for k in tq):      # 글자 없이 저장된 옛 형식
                tq = {'a': dict(tq, dev='legacy')}
            if b.get('clear'):
                if letter:
                    tq.pop(letter, None)
                else:
                    tq = {}
            else:
                if not letter and dev:
                    letter = next((l for l, v in tq.items() if v.get('dev') == dev), None) or next(l for l in 'abcdefghij' if l not in tq)
                if not letter:
                    raise ValueError('태블릿 정보가 없습니다.')
                cur = dict(tq.get(letter, {}))
                if not cur and tq:   # new tablet in a team with progress: start from the team's furthest point
                    for v in tq.values():
                        if not isinstance(v, dict):
                            continue
                        for k, val in v.items():
                            if QUEST_ID.match(k) or k == 'tut':
                                cur[k] = cur.get(k) or val
                            elif k == 'act':
                                cur['act'] = max(int(cur.get('act') or 0), int(val or 0))
                if dev:
                    cur['dev'] = dev
                cur['seen'] = now_ms()
                if isinstance(b.get('done'), list):
                    done = [str(x) for x in b['done'] if QUEST_ID.match(str(x))]
                    keep = {k: v for k, v in cur.items() if not QUEST_ID.match(k)}
                    cur = dict(keep, **{x: cur.get(x) or now_ms() for x in done})
                if b.get('act') is not None:
                    try:
                        cur['act'] = max(int(cur.get('act') or 0), min(3, int(b['act'])))
                    except (TypeError, ValueError):
                        pass
                if b.get('tut'):
                    cur['tut'] = cur.get('tut') or now_ms()
                tq[letter] = cur
            if tq:
                q[str(team)] = tq
            else:
                q.pop(str(team), None)
            save()
            self.send_json(state())

    # 학생: 조별 현재 위치 (캠퍼스 트윈에 점으로 표시)
    def pos(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('조를 먼저 고르세요.')
        try:
            lat, lng = float(b.get('lat')), float(b.get('lng'))
        except (TypeError, ValueError):
            raise ValueError('위치 값이 없습니다.')
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError('위치 값이 이상합니다.')
        try:
            acc = max(0.0, min(9999.0, float(b.get('acc') or 0)))
        except (TypeError, ValueError):
            acc = 0.0
        POS[team] = {'lat': round(lat, 6), 'lng': round(lng, 6), 'acc': round(acc, 1), 't': now_ms()}
        self.send_json({'ok': True, 'pos': live_pos(), 'now': now_ms()})

    # 운영자: 링크 변환 다시 시도
    def admin_convert(self, b):
        sid = str(b.get('id') or '')
        with lock:
            hit = next((s for s in DB['subs'] if s['id'] == sid and s.get('kind', 'link') == 'link'), None)
        if not hit:
            raise ValueError('그 제출이 없습니다.')
        threading.Thread(target=convert_scan, args=(sid, hit['scanId']), daemon=True).start()
        self.send_json({'ok': True})

    # 학생: 우리 조가 낸 제출 취소
    def unsubmit(self, b):
        team = clean_team(b.get('team'))
        sid = str(b.get('id') or '')
        with lock:
            gone = [s for s in DB['subs'] if s['id'] == sid and s['team'] == team]
            if not gone:
                raise ValueError('우리 조가 낸 제출만 취소할 수 있습니다.')
            DB['subs'] = [s for s in DB['subs'] if s not in gone]
            save()
            self.send_json(state())

    def admin_delete(self, b):
        sid = str(b.get('id') or '')
        with lock:
            DB['subs'] = [s for s in DB['subs'] if s['id'] != sid]
            save()
            self.send_json(state())

    # 운영자: 자체 스캔을 복구됨으로 확정(ok=false면 다시 확인 대기로)
    def admin_approve(self, b):
        sid = str(b.get('id') or '')
        ok = b.get('ok', True) is not False
        with lock:
            hit = [s for s in DB['subs'] if s['id'] == sid and s.get('splat')]
            if not hit:
                raise ValueError('그 기록이 없습니다.')
            for s in hit:
                s['status'] = 'ok' if ok else 'pend'
            save()
            self.send_json(state())

    # 운영자: 전체 공지 한 줄 — 모든 태블릿이 다음 state 폴링 때 받아 보이드가 말한다. 빈 text면 내린다 (2026-10-30)
    def admin_notice(self, b):
        text = clean_text(b.get('text'), 120)
        with lock:
            DB['notice'] = {'id': now_ms(), 'text': text, 't': now_ms()} if text else None
            save()
            self.send_json(state())

    # 운영자: 링크가 변환되면 바로 복구됨으로 할지(auto)
    def admin_auto(self, b):
        with lock:
            DB['auto'] = bool(b.get('auto'))
            save()
            self.send_json(state())

    # 운영자: 제출 기록 전부 삭제 + 페이지에 이미 들어간 스캔을 숨겨 모든 구역을 "복구 필요"로
    def admin_reset(self, b):
        if b.get('confirm') != 'RESET':
            raise ValueError('확인 문구가 필요합니다.')
        hide = [str(x).lower() for x in (b.get('hide') or []) if SCAN_ID.match(str(x).lower())]
        with lock:
            DB['subs'] = []
            DB['hidden'] = sorted(set(DB['hidden']) | set(hide))
            DB['quests'] = {}
            DB['notice'] = None
            DB['reset'] = now_ms()   # every tablet forgets its team when it sees a newer reset
            save()
            self.send_json(state())

    # 운영자: 숨긴 스캔을 다시 보이게
    def admin_unhide(self, b):
        with lock:
            DB['hidden'] = []
            save()
            self.send_json(state())


def main():
    global DB, PAIRS
    DB = read_db()
    PAIRS = read_pairs()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    srv.daemon_threads = True
    print(f'보이드의 기록 서버: http://{HOST}:{PORT}/chapter05/index.html  (운영자 비밀번호는 CH5_ADMIN_KEY, 짝 {len(PAIRS)}개)')
    srv.serve_forever()


if __name__ == '__main__':
    main()
