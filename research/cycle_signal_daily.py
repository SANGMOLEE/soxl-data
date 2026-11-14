# -*- coding: utf-8 -*-
"""전방 검증용 일일 신호·상태 기록. 엔진 v2 를 전 구간 돌려 오늘의 상태와 다음 발동 수준을 계산해
research/forward_log.csv 에 한 줄 붙인다(같은 날짜가 있으면 덮어쓰지 않는다)."""
import os, sys, csv, datetime as dt, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cycle_engine_v2 as V
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forward_log.csv")
E, log, st = V.run({})
hold = st.get("hold", {}); held = [k for k, v in hold.items() if v > 0]
t = V.BTC.index[-1]; b = V.BTC.iloc[-1]; s = V.SOL.iloc[-1]
ma100 = V.BTC.rolling(100).mean().iloc[-1]; ma200 = V.BTC.rolling(200).mean().iloc[-1]
ratio = V.SOL / V.BTC; rmom = (ratio / ratio.shift(20) - 1).iloc[-1]
below200 = int(((V.BTC < V.BTC.rolling(200).mean()).astype(int)[::-1].cumprod()).sum())  # 현재 연속 하회 일수
row = dict(date=str(t.date()), btc=round(b), sol=round(s, 2), ma100=round(ma100), ma200=round(ma200), rmom20=round(rmom, 4),
           phase=st["phase"], tranche=st["tranche"], holding=",".join(held) or "CASH", evac=st["evac"], wait=st["wait"],
           cycle_peak=round(st["peak"]) if st.get("peak") else "", bottom_ref=round(st["bottom_ref"]) if st.get("bottom_ref") else "",
           equity=round(float(E.iloc[-1]), 4), below200_days=below200,
           lvl_bear200=round(ma200), lvl_evac=round(st["peak"] * 0.9) if st.get("peak") else "", lvl_reset=round(st["bottom_ref"]) if (st.get("bottom_ref") and st["tranche"] < 3) else "off",
           lvl_rot_in=0.0, lvl_rot_out=-0.05, lvl_ladder=round(st["ent_sol"] * 1.5, 2) if st.get("ent_sol") and "SOLT" in held else "", lvl_stop=round(st["ent_sol"] * 0.75, 2) if st.get("ent_sol") and "SOLT" in held else "",
           last_action=f"{log[-1][0]} {log[-1][1]} {log[-1][2]}" if log else "")
new = not os.path.exists(OUT)
if not new and str(t.date()) in open(OUT, encoding="utf-8").read(): print("이미 기록됨:", t.date()); sys.exit(0)
with open(OUT, "a", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(row));
    if new: w.writeheader()
    w.writerow(row)
print("기록:", row)
