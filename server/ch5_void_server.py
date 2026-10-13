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
- 자체 스캔(v2): 페이지 안의 카메라로 상하좌우를 돌며 찍은 사진 세트(최대 72장, 방향 dirs 포함)를 data/scans/<id>/ 에 받는다.
  start(JSON) → frame/<n>(JPEG 본문) → finish(JSON) 순서. finish 때 제출 기록에 kind:"orbit"으로 들어가며
  운영자 설정 auto(기본 켬)가 켜져 있으면 바로 status:"ok"(복구됨), 꺼져 있으면 "pend"(운영자가 "복구 확정"을 눌러야 함).
  삭제·초기화된 세트는 지우지 않고 data/scans_trash/ 로 옮긴다.

실행:
    python server/ch5_void_server.py           # http://localhost:8096/chapter05/index.html
환경변수:
    VOID_PORT=8096  VOID_HOST=127.0.0.1  CH5_ADMIN_KEY=0101  VOID_STATIC=1 (저장소 파일도 서빙, 로컬 확인용)
"""
import json
import os
import re
import shutil
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data')
THUMB_DIR = os.path.join(DATA_DIR, 'thumbs')
SCAN_DIR = os.path.join(DATA_DIR, 'scans')
TRASH_DIR = os.path.join(DATA_DIR, 'scans_trash')
DB_PATH = os.path.join(DATA_DIR, 'ch5_void.json')
PAIRS_PATH = os.path.join(HERE, 'ch5_void_pairs.json')

PORT = int(os.environ.get('VOID_PORT', '8096'))
HOST = os.environ.get('VOID_HOST', '127.0.0.1')
ADMIN_KEY = os.environ.get('CH5_ADMIN_KEY', '0101')
SERVE_STATIC = os.environ.get('VOID_STATIC', '1') == '1'

MAX_TEAM = 12
MAX_FRAMES = 72                       # 상하 5단 × 좌우 9/16/18/16/9 = 68칸, 여유를 둔다
MAX_FRAME_BYTES = 3 * 1024 * 1024
UPLOAD_TTL_MS = 2 * 60 * 60 * 1000    # 올리다 만 세트는 2시간 뒤 정리
SCAN_ID = re.compile(r'^[a-z0-9]{6,40}$')
ORBIT_ID = re.compile(r'^o[a-f0-9]{15}$')
MISSION_ID = re.compile(r'^[a-z0-9_-]{1,40}$')
UA = 'Mozilla/5.0 (DOROLAND void record)'

lock = threading.Lock()
DB = None
PAIRS = []


def now_ms():
    return int(time.time() * 1000)


def fresh_db():
    return {'version': 0, 'subs': [], 'hidden': [], 'auto': True}


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
    """자체 스캔은 운영자 확정(또는 자동)으로 ok가 되면 복구된 것으로 본다."""
    return s.get('kind') == 'orbit' and s.get('status') == 'ok'


def pair_status():
    """짝마다 복구 상태: ok(3D에 들어간 스캔이 보이거나 자체 스캔이 확정됨) / pend(제출됨) / void."""
    hidden = set(DB['hidden'])
    out = []
    for p in PAIRS:
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


def state():
    return {'version': DB['version'], 'subs': DB['subs'], 'hidden': DB['hidden'], 'auto': bool(DB.get('auto', True)),
            'pairs': pair_status()}


# ---------- 자체 카메라 스캔(사진 세트) ----------
def scan_path(sid, *parts):
    return os.path.join(SCAN_DIR, sid, *parts)


def read_meta(sid):
    try:
        with open(scan_path(sid, 'meta.json'), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write_meta(sid, meta):
    os.makedirs(scan_path(sid), exist_ok=True)
    tmp = scan_path(sid, 'meta.json.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    os.replace(tmp, scan_path(sid, 'meta.json'))


def trash_scan(sid):
    """사진 세트는 지우지 않고 scans_trash/<시각>_<id>/ 로 옮긴다(실수 복구용)."""
    if not ORBIT_ID.match(sid) or not os.path.isdir(scan_path(sid)):
        return
    os.makedirs(TRASH_DIR, exist_ok=True)
    try:
        shutil.move(scan_path(sid), os.path.join(TRASH_DIR, f'{now_ms()}_{sid}'))
    except OSError:
        pass


def sweep_uploads():
    """올리다 만(finish 안 된) 세트 중 오래된 것을 정리한다."""
    if not os.path.isdir(SCAN_DIR):
        return
    for sid in os.listdir(SCAN_DIR):
        meta = read_meta(sid) if ORBIT_ID.match(sid) else None
        if meta and meta.get('status') == 'uploading' and now_ms() - meta.get('createdAt', 0) > UPLOAD_TTL_MS:
            trash_scan(sid)


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
    server_version = 'VoidRecordServer/2.0'

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

    def read_jpeg(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n <= 0 or n > MAX_FRAME_BYTES:
            raise ValueError('사진 한 장이 너무 큽니다.')
        raw = self.rfile.read(n)
        if not raw.startswith(b'\xff\xd8'):
            raise ValueError('JPEG 사진이 아닙니다.')
        return raw

    def is_admin(self):
        return self.headers.get('X-Admin-Key') == ADMIN_KEY

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/void/state':
            with lock:
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
        # 자체 스캔 사진 세트: /api/void/scan/<id>/<n>.jpg, thumb.jpg, meta.json
        m = re.fullmatch(r'/api/void/scan/(o[a-f0-9]{15})/(\d{1,2}\.jpg|thumb\.jpg|meta\.json)', path)
        if m:
            fp = scan_path(m.group(1), m.group(2))
            if not os.path.isfile(fp):
                return self.fail('없는 사진입니다.', 404)
            ctype = 'application/json; charset=utf-8' if fp.endswith('.json') else 'image/jpeg'
            return self.send_bytes(open(fp, 'rb').read(), ctype, cache=fp.endswith('.jpg'))
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
        # 사진 본문(JPEG)을 그대로 받는 경로: /api/void/scan/<id>/frame/<n>, /api/void/scan/<id>/thumb
        m = re.fullmatch(r'/api/void/scan/(o[a-f0-9]{15})/(?:frame/(\d{1,2})|(thumb))', path)
        if m:
            try:
                return self.scan_frame(m.group(1), m.group(2))
            except ValueError as e:
                return self.fail(str(e))
        try:
            body = self.read_json()
        except (ValueError, json.JSONDecodeError):
            return self.fail('요청 형식이 올바르지 않습니다.')
        routes = {
            '/api/void/submit': self.submit, '/api/void/unsubmit': self.unsubmit,
            '/api/void/scan/start': self.scan_start, '/api/void/scan/finish': self.scan_finish,
            '/api/void/admin/delete': self.admin_delete, '/api/void/admin/reset': self.admin_reset,
            '/api/void/admin/unhide': self.admin_unhide, '/api/void/admin/approve': self.admin_approve,
            '/api/void/admin/auto': self.admin_auto,
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
            DB['subs'].append({
                'id': uuid.uuid4().hex[:12], 'scanId': scan_id, 'url': f'https://scaniverse.com/scan/{scan_id}',
                'mission': mission, 'team': team, 'note': clean_text(b.get('note'), 60),
                'caption': caption, 'author': author, 'createdAt': now_ms(),
            })
            save()
            self.send_json(state())
        threading.Thread(target=fetch_thumb, args=(scan_id,), daemon=True).start()

    # 학생: 자체 스캔 1단계 — 어느 구역에 몇 장을 올릴지 알리고 id를 받는다
    def scan_start(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('우리 조를 먼저 고르세요.')
        mission = str(b.get('mission') or '')
        if not MISSION_ID.match(mission):
            raise ValueError('구역 정보가 없습니다.')
        try:
            count = int(b.get('count'))
        except (TypeError, ValueError):
            count = 0
        if not 1 <= count <= MAX_FRAMES:
            raise ValueError('사진 수가 올바르지 않습니다.')
        heads = b.get('headings') or []
        heads = [max(0, min(359, int(h))) for h in heads[:MAX_FRAMES] if isinstance(h, (int, float))]
        # 사진마다 찍은 방향 [yaw(0~359), pitch(-90~90)] — 점구름 돔을 펼칠 때 쓴다
        dirs = []
        for dv in (b.get('dirs') or [])[:MAX_FRAMES]:
            try:
                dirs.append([max(0, min(359, int(dv[0]))), max(-90, min(90, int(dv[1])))])
            except (TypeError, ValueError, IndexError):
                dirs.append([0, 0])
        pos = {}
        for k in ('lat', 'lng'):
            try:
                pos[k] = round(float(b.get(k)), 6)
            except (TypeError, ValueError):
                pos[k] = None
        sweep_uploads()
        sid = 'o' + uuid.uuid4().hex[:15]
        write_meta(sid, {
            'id': sid, 'team': team, 'mission': mission, 'note': clean_text(b.get('note'), 60), 'count': count,
            'mode': 'space' if b.get('mode') == 'space' else 'object', 'sensor': bool(b.get('sensor', True)), 'headings': heads, 'dirs': dirs, 'lat': pos['lat'], 'lng': pos['lng'],
            'ua': clean_text(self.headers.get('User-Agent'), 160), 'createdAt': now_ms(), 'status': 'uploading',
        })
        self.send_json({'id': sid})

    # 학생: 자체 스캔 2단계 — 사진 한 장씩(JPEG 본문). n은 0부터 count-1, 'thumb'는 미리보기
    def scan_frame(self, sid, n):
        meta = read_meta(sid)
        if not meta or meta.get('status') != 'uploading':
            raise ValueError('올리는 중인 기록이 아닙니다. 처음부터 다시 올려 주세요.')
        name = 'thumb.jpg' if n is None else f'{int(n)}.jpg'
        if n is not None and not 0 <= int(n) < meta['count']:
            raise ValueError('사진 번호가 맞지 않습니다.')
        raw = self.read_jpeg()
        tmp = scan_path(sid, name + '.tmp')
        with open(tmp, 'wb') as f:
            f.write(raw)
        os.replace(tmp, scan_path(sid, name))
        self.send_json({'ok': True, 'name': name})

    # 학생: 자체 스캔 3단계 — 모두 올라왔는지 확인하고 제출 기록에 넣는다
    def scan_finish(self, b):
        sid = str(b.get('id') or '')
        team = clean_team(b.get('team'))
        if not ORBIT_ID.match(sid):
            raise ValueError('기록 정보가 없습니다.')
        meta = read_meta(sid)
        if not meta or meta.get('status') != 'uploading':
            raise ValueError('올리는 중인 기록이 아닙니다.')
        if meta['team'] != team:
            raise ValueError('이 기록을 올리던 조가 아닙니다.')
        missing = [i for i in range(meta['count']) if not os.path.isfile(scan_path(sid, f'{i}.jpg'))]
        if missing:
            self.send_json({'missing': missing})
            return
        if not os.path.isfile(scan_path(sid, 'thumb.jpg')):
            shutil.copyfile(scan_path(sid, '0.jpg'), scan_path(sid, 'thumb.jpg'))
        note = clean_text(b.get('note'), 60) or meta.get('note', '')
        meta.update(status='done', note=note, finishedAt=now_ms())
        write_meta(sid, meta)
        with lock:
            if not any(s['scanId'] == sid for s in DB['subs']):
                DB['subs'].append({
                    'id': uuid.uuid4().hex[:12], 'scanId': sid, 'kind': 'orbit', 'url': '',
                    'mission': meta['mission'], 'team': team, 'note': note, 'caption': note, 'author': f'{team}조',
                    'frames': meta['count'], 'mode': meta['mode'], 'status': 'ok' if DB.get('auto', True) else 'pend',
                    'createdAt': now_ms(),
                })
                save()
            self.send_json(dict(state(), scanId=sid))

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
        for s in gone:
            if s.get('kind') == 'orbit':
                trash_scan(s['scanId'])

    def admin_delete(self, b):
        sid = str(b.get('id') or '')
        with lock:
            gone = [s for s in DB['subs'] if s['id'] == sid]
            DB['subs'] = [s for s in DB['subs'] if s['id'] != sid]
            save()
            self.send_json(state())
        for s in gone:
            if s.get('kind') == 'orbit':
                trash_scan(s['scanId'])

    # 운영자: 자체 스캔을 복구됨으로 확정(ok=false면 다시 확인 대기로)
    def admin_approve(self, b):
        sid = str(b.get('id') or '')
        ok = b.get('ok', True) is not False
        with lock:
            hit = [s for s in DB['subs'] if s['id'] == sid and s.get('kind') == 'orbit']
            if not hit:
                raise ValueError('그 기록이 없습니다.')
            for s in hit:
                s['status'] = 'ok' if ok else 'pend'
            save()
            self.send_json(state())

    # 운영자: 올리면 바로 복구됨으로 할지(auto)
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
            gone = [s for s in DB['subs'] if s.get('kind') == 'orbit']
            DB['subs'] = []
            DB['hidden'] = sorted(set(DB['hidden']) | set(hide))
            save()
            self.send_json(state())
        for s in gone:
            trash_scan(s['scanId'])

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
    sweep_uploads()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    srv.daemon_threads = True
    print(f'보이드의 기록 서버: http://{HOST}:{PORT}/chapter05/index.html  (운영자 비밀번호는 CH5_ADMIN_KEY, 짝 {len(PAIRS)}개)')
    srv.serve_forever()


if __name__ == '__main__':
    main()
