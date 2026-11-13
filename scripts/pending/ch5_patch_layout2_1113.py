# 2026-11-13 다시 점검하며 남아 있던 것: 범죄수사과 본부를 지나던 길, 직원 숙소 집을 지나던 자동 곁길, 호수 길 위 가판대, 호수 연결로 위 간식 수레
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90]); s = s.replace(old, new)
rep("[[25,-20],[45,-60],[55,-75]],", "[[25,-20],[48,-28],[53,-56],[55,-75]],")   # round the east side of the investigation HQ, not through it
rep("[[45,-60],[20,-110],[40,-150],[48,-165]],", "[[52,-58],[20,-110],[40,-150],[48,-165]],")
rep("const NO_SPUR = new Set(['관람차']);", "const NO_SPUR = new Set(['관람차', '직원 숙소']);   /* the staff village has its own lanes: an automatic spur ran through a cottage */")
rep("if(side < 0 && (k===3 || k===4)) continue;", "if((side < 0 && (k===3 || k===4)) || (side > 0 && k===3)) continue;   /* east k 3 stood on the lake path */")
rep("cart(0xffe08a, '#e2574c', 230/K, 320/K, 0.8);", "cart(0xffe08a, '#e2574c', 240/K, 328/K, 0.8);")
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))
