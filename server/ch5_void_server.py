#!/usr/bin/env python3
"""챕터 5 「보이드의 기록」 스캔 링크 제출 서버 (표준 라이브러리만 사용, 추가 설치 없음).

chapter05/index.html(보이드의 기록)이 쓰는 API. 조별로 어느 구역에 어떤 Scaniverse 링크를 냈는지 저장하고,
운영자(비밀번호)가 전체 목록 확인·삭제·초기화를 한다. 도로그램 서버(ch5_feed_server.py)와는 완전히 별개다.
- 제출 기록: data/ch5_void.json (gitignore)
- 초기화: 제출 기록을 지우고, 페이지에 이미 3D로 들어가 있는 스캔은 "숨김" 목록에 넣어 구역을 다시 "복구 필요"로 되돌린다.
  (3D 데이터 자체는 페이지에 박혀 있으므로 지우지 않고 숨기기만 한다. "되살리기"로 되돌릴 수 있다.)

실행:
    python server/ch5_void_server.py           # http://localhost:8096/chapter05/index.html
환경변수:
    VOID_PORT=8096  VOID_HOST=127.0.0.1  CH5_ADMIN_KEY=0101  VOID_STATIC=1 (저장소 파일도 서빙, 로컬 확인용)
"""
import json
import os
import re
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data')
DB_PATH = os.path.join(DATA_DIR, 'ch5_void.json')

PORT = int(os.environ.get('VOID_PORT', '8096'))
HOST = os.environ.get('VOID_HOST', '127.0.0.1')
ADMIN_KEY = os.environ.get('CH5_ADMIN_KEY', '0101')
SERVE_STATIC = os.environ.get('VOID_STATIC', '1') == '1'

MAX_TEAM = 12
SCAN_ID = re.compile(r'^[a-z0-9]{6,40}$')
MISSION_ID = re.compile(r'^[a-z0-9_-]{1,40}$')

lock = threading.Lock()
DB = None


def now_ms():
    return int(time.time() * 1000)


def fresh_db():
    return {'version': 0, 'subs': [], 'hidden': []}


def read_db():
    try:
        with open(DB_PATH, encoding='utf-8') as f:
            db = json.load(f)
        for k, v in fresh_db().items():
            db.setdefault(k, v)
        return db
    except (OSError, ValueError):
        return fresh_db()


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


def state():
    return {'version': DB['version'], 'subs': DB['subs'], 'hidden': DB['hidden']}


class Handler(BaseHTTPRequestHandler):
    server_version = 'VoidRecordServer/1.0'

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
            with lock:
                return self.send_json(state())
        if path == '/api/void/admin/state':
            if not self.is_admin():
                return self.fail('운영자 비밀번호가 맞지 않습니다.', 403)
            with lock:
                return self.send_json(dict(state(), admin=True))
        if SERVE_STATIC and not path.startswith('/api/'):
            return self.send_static(path)
        self.fail('없는 주소입니다.', 404)

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
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self.read_json()
        except (ValueError, json.JSONDecodeError):
            return self.fail('요청 형식이 올바르지 않습니다.')
        routes = {
            '/api/void/submit': self.submit, '/api/void/unsubmit': self.unsubmit,
            '/api/void/admin/delete': self.admin_delete, '/api/void/admin/reset': self.admin_reset,
            '/api/void/admin/unhide': self.admin_unhide,
        }
        fn = routes.get(path)
        if not fn:
            return self.fail('없는 주소입니다.', 404)
        if path.startswith('/api/void/admin/') and not self.is_admin():
            return self.fail('운영자 비밀번호가 맞지 않습니다.', 403)
        try:
            with lock:
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
        dup = next((s for s in DB['subs'] if s['scanId'] == scan_id), None)
        if dup:
            raise ValueError(f'이미 제출된 링크입니다 ({dup["team"]}조).')
        DB['subs'].append({
            'id': uuid.uuid4().hex[:12], 'scanId': scan_id, 'url': f'https://scaniverse.com/scan/{scan_id}',
            'mission': mission, 'team': team, 'note': clean_text(b.get('note'), 60), 'createdAt': now_ms(),
        })
        save()
        self.send_json(state())

    # 학생: 우리 조가 낸 제출 취소
    def unsubmit(self, b):
        team = clean_team(b.get('team'))
        sid = str(b.get('id') or '')
        before = len(DB['subs'])
        DB['subs'] = [s for s in DB['subs'] if not (s['id'] == sid and s['team'] == team)]
        if len(DB['subs']) == before:
            raise ValueError('우리 조가 낸 제출만 취소할 수 있습니다.')
        save()
        self.send_json(state())

    def admin_delete(self, b):
        sid = str(b.get('id') or '')
        DB['subs'] = [s for s in DB['subs'] if s['id'] != sid]
        save()
        self.send_json(state())

    # 운영자: 제출 기록 전부 삭제 + 페이지에 이미 들어간 스캔을 숨겨 모든 구역을 "복구 필요"로
    def admin_reset(self, b):
        if b.get('confirm') != 'RESET':
            raise ValueError('확인 문구가 필요합니다.')
        hide = [str(x).lower() for x in (b.get('hide') or []) if SCAN_ID.match(str(x).lower())]
        DB['subs'] = []
        DB['hidden'] = sorted(set(DB['hidden']) | set(hide))
        save()
        self.send_json(state())

    # 운영자: 숨긴 스캔을 다시 보이게
    def admin_unhide(self, b):
        DB['hidden'] = []
        save()
        self.send_json(state())


def main():
    global DB
    DB = read_db()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    srv.daemon_threads = True
    print(f'보이드의 기록 서버: http://{HOST}:{PORT}/chapter05/index.html  (운영자 비밀번호는 CH5_ADMIN_KEY)')
    srv.serve_forever()


if __name__ == '__main__':
    main()
