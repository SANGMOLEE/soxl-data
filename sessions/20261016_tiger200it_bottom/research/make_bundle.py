# -*- coding: utf-8 -*-
r"""세션 코드 묶음 txt 생성 (주인님 보관용). 풀기:
  import re; t=open('tiger_it_code_bundle.txt',encoding='utf-8').read()
  [open(n,'w',encoding='utf-8').write(b) for n,b in re.findall(r'^##### FILE: (\S+) #####\n(.*?)(?=^##### FILE: |\Z)', t, re.S|re.M)]
"""
import os, sys, datetime
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = ["PREREGISTRATION.md", "collect_kr.py", "requirements.txt", "engine/tiger_it_short_bottom.py",
         "research/backtest.py", "research/make_bundle.py"]
wf = os.path.join(os.path.dirname(os.path.dirname(S)), ".github", "workflows", "kr-collect.yml")
out = [f"# TIGER 200 IT 단기저점 스코어 — 코드 묶음 ({datetime.date.today()})",
       "# 풀기: 위 docstring의 두 줄 파이썬을 unpack.py로 저장해 실행", ""]
for f in files + [wf]:
    p = f if os.path.isabs(f) else os.path.join(S, f)
    name = os.path.relpath(p, os.path.dirname(os.path.dirname(S)))
    out.append(f"##### FILE: {name} #####")
    out.append(open(p, encoding="utf-8").read().rstrip("\n"))
    out.append("")
os.makedirs(os.path.join(S, "reports"), exist_ok=True)
dst = os.path.join(S, "reports", f"tiger_it_code_bundle_{datetime.date.today()}.txt")
open(dst, "w", encoding="utf-8").write("\n".join(out))
print(dst)
