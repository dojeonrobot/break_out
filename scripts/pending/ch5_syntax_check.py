# 페이지의 모듈 스크립트를 떼어 node --check 로 문법만 본다(패치 뒤 바로 돌린다).  python ch5_syntax_check.py
import io, re, subprocess, tempfile, os, sys
s = io.open("C:/Users/dlgus/break_out/chapter05/index.html", encoding="utf-8").read()
ok = True
for i, m in enumerate(re.finditer(r"<script([^>]*)>([\s\S]*?)</script>", s)):
    if "src=" in m.group(1) or not m.group(2).strip() or "importmap" in m.group(1) or "json" in m.group(1): continue
    ext = ".mjs" if "module" in m.group(1) else ".js"
    f = os.path.join(tempfile.gettempdir(), f"ch5_chk_{i}{ext}"); io.open(f, "w", encoding="utf-8").write(m.group(2))
    r = subprocess.run(["node", "--check", f], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode: ok = False; print("SYNTAX ERROR in script", i, "\n", r.stderr[:1500])
    os.remove(f)
print("syntax ok" if ok else "FAILED"); sys.exit(0 if ok else 1)
