#!/usr/bin/env python3
"""
모의 장부 — 일봉 규칙(D, E, 반등 뒤 숏) 신호를 매일 다시 계산해 기록한다.

사람(세션)이 기억해서 적는 방식은 11/5·11/16 신호를 놓쳤다(2026-11-25 확인).
그래서 공식 일봉이 들어올 때마다 전부 다시 계산한다. 결과는 결정적이라 매번 같은 값이 나온다.

출력: ledger/paper_trades.csv, ledger/paper_trades.md
근사: D 진입 = 종가(실제는 05:30 KST 가격), E 진입 = 시가(실제는 00:30 KST). 비용 전 수익률.
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = pd.Timestamp("2026-10-30")   # D·E 채택(10/31 KST) 뒤 첫 미국 세션

def load(name, sub="prices"):
    df = pd.read_csv(os.path.join(ROOT, "data", sub, f"{name}.csv"), parse_dates=["date"])
    return df.set_index("date").sort_index()

L = load("SOXL"); S = load("SOXS").reindex(L.index)
V = load("VIXCLS", "macro")["value"]
d = L.index
c, o, h, lo = (L[k].to_numpy(float) for k in ("close", "open", "high", "low"))
sc, so, sh, sl = (S[k].to_numpy(float) for k in ("close", "open", "high", "low"))
r = c / np.r_[np.nan, c[:-1]] - 1
with np.errstate(divide="ignore", invalid="ignore"):
    pos = (c - lo) / (h - lo)
ma200 = pd.Series(c, index=d).rolling(200).mean().to_numpy()
vix = V.reindex(d).to_numpy(float)           # 결측(FRED 지연)은 NaN 그대로 → '미확인'
N = len(d)
st = int(np.searchsorted(d, START))
rows = []

def ds(i): return d[i].strftime("%Y-%m-%d")

def b_exit(i):
    """(b) +15% 절반, +25% 나머지, 10거래일 시한. 지정가는 시가가 위면 시가 체결."""
    e = c[i]; legs = []; done = True
    for tgt in (1.15, 1.25):
        fill = None
        for k in range(i + 1, min(i + 11, N)):
            if o[k] >= e * tgt: fill = o[k] / e - 1; break
            if h[k] >= e * tgt: fill = tgt - 1; break
        if fill is None:
            last = min(i + 10, N - 1); fill = c[last] / e - 1
            if i + 10 >= N: done = False
        legs.append(fill)
    return sum(legs) / 2, done

# ── D: 당일 −8%↓ & 종가 위치 하위 20% & 전일 하락 → 종가 매수, 다음 날 종가 매도(D2)
Didx = [i for i in range(st, N) if r[i] <= -0.08 and pos[i] <= 0.2 and r[i - 1] < 0]
for i in Didx:
    row = dict(rule="D", signal=ds(i), entry_date=ds(i), entry=round(c[i], 2), ticker="SOXL",
               vix=None if np.isnan(vix[i]) else round(vix[i], 2))
    if i + 1 < N:
        d2 = c[i + 1] / c[i] - 1
        b, bdone = b_exit(i)
        hi_vix = (not np.isnan(vix[i])) and vix[i] >= 30 and c[i] < ma200[i]
        if hi_vix:   # D+ 후보: 첫날 +10%↑면 정리, 아니면 (b)
            alt = d2 if d2 >= 0.10 else b; alt_name = "D+ (VIX30↑)"; alt_done = True if d2 >= 0.10 else bdone
        else:        # 그 밖 국면 제안: 절반 D2 + 절반 (b)
            alt = (d2 + b) / 2; alt_name = "절반D2+절반(b)"; alt_done = bdone
        row.update(exit_date=ds(i + 1), exit=round(c[i + 1], 2), ret_pct=round(d2 * 100, 2), status="청산",
                   alt_name=alt_name, alt_pct=round(alt * 100, 2), alt_status="청산" if alt_done else "진행중")
    else:
        row.update(status="보유중")
    rows.append(row)

# ── E: 전일 −12%↓ & 시가 −3%↓ 갭락 → 시가(실제 00:30) 매수, 당일 종가 매도
for i in range(st, N):
    if r[i - 1] <= -0.12:
        gap = o[i] / c[i - 1] - 1
        if gap <= -0.03:
            rows.append(dict(rule="E", signal=ds(i), entry_date=ds(i), entry=round(o[i], 2), ticker="SOXL",
                             exit_date=ds(i), exit=round(c[i], 2), ret_pct=round((c[i] / o[i] - 1) * 100, 2),
                             status="청산", note=f"갭 {gap*100:+.1f}%, 전일 {r[i-1]*100:+.1f}%"
                             + (" (전일 −15%↓ 주의 구간)" if r[i - 1] <= -0.15 else "")))
        else:
            rows.append(dict(rule="E", signal=ds(i), status="미발동", note=f"갭 {gap*100:+.1f}% (−3% 이하 아님)"))

# ── 반등 뒤 숏: D 뒤 2~7일째 첫 종가 ≥ 신호일×1.10 → SOXS 종가 매수, +10% / −15% / 5거래일
#    필터: SOXL < 200일선 & VIX < 30.  금지: 반등 첫날 종가 +10%↑ (10/31 세션 4-2, 11/25 재확인)
for i in Didx:
    base = dict(rule="반등뒤숏", signal=ds(i), ticker="SOXS")
    day1 = c[i + 1] / c[i] - 1 if i + 1 < N else np.nan
    if not np.isnan(day1) and day1 >= 0.10:
        rows.append({**base, "status": "금지", "note": f"반등 첫날 {day1*100:+.1f}% (첫날 +10%↑ 숏 금지)"}); continue
    trig = None
    for k in range(2, 8):
        j = i + k
        if j >= N: break
        if c[j] >= c[i] * 1.10: trig = j; break
    if trig is None:
        live = i + 7 >= N
        rows.append({**base, "status": "대기" if live else "미발동",
                     "note": f"기준 종가 {c[i]*1.10:.2f}" + (f", {ds(i)} 뒤 7거래일째까지 감시" if live else "")}); continue
    j = trig
    if np.isnan(vix[j]):
        rows.append({**base, "status": "보류", "note": f"{ds(j)} 조건 충족, VIX 미확인"}); continue
    if not (c[j] < ma200[j] and vix[j] < 30):
        rows.append({**base, "status": "필터 불통과", "note": f"{ds(j)} VIX {vix[j]:.1f}"}); continue
    e = sc[j]; res = None
    for k in range(j + 1, min(j + 6, N)):
        if so[k] <= e * 0.85: res = (so[k] / e - 1, "갭손절", k); break
        if sl[k] <= e * 0.85: res = (-0.15, "손절", k); break
        if so[k] >= e * 1.10: res = (so[k] / e - 1, "갭익절", k); break
        if sh[k] >= e * 1.10: res = (0.10, "익절", k); break
    if res is None:
        k = min(j + 5, N - 1); res = (sc[k] / e - 1, "시한" if j + 5 < N else "보유중", k)
    rows.append({**base, "entry_date": ds(j), "entry": round(e, 2), "exit_date": ds(res[2]),
                 "exit": round(e * (1 + res[0]), 2), "ret_pct": round(res[0] * 100, 2), "status": res[1]})

df = pd.DataFrame(rows)
cols = ["rule", "signal", "ticker", "entry_date", "entry", "exit_date", "exit", "ret_pct", "status",
        "alt_name", "alt_pct", "alt_status", "vix", "note"]
df = df.reindex(columns=cols)
df.to_csv(os.path.join(ROOT, "ledger", "paper_trades.csv"), index=False, encoding="utf-8")

# ── 사람용 요약
def summ(x):
    x = [v for v in x if pd.notna(v)]
    if not x: return "0건"
    x = sorted(x)
    top3 = np.mean(x[:-3]) if len(x) > 3 else float("nan")
    return (f"{len(x)}건 · 이익 {np.mean([v > 0 for v in x])*100:.0f}% · 중앙 {np.median(x):+.1f}% · "
            f"상위3뺀 {'—' if np.isnan(top3) else f'{top3:+.1f}%'} · 평균 {np.mean(x):+.1f}% · 최악 {min(x):+.1f}%")

done = df[df.status.isin(["청산", "익절", "손절", "갭익절", "갭손절", "시한"])]
md = ["# 모의 장부 (자동 생성 — scripts/paper.py)", "",
      f"갱신: SOXL 마지막 일봉 {ds(N-1)} · 대상: {START.date()} 이후 미국 세션", "",
      "근사: D는 종가 진입(실제 05:30 KST), E는 시가 진입(실제 00:30 KST). **비용 전** 수익률.", "",
      "## 요약", "",
      f"- D (다음 날 종가 정리, 현행): {summ(done[done.rule=='D'].ret_pct)}",
      f"- D 대안 청산(국면별 제안안, 진행중 포함 평가): {summ(df[df.rule=='D'].alt_pct)}",
      f"- E: {summ(done[done.rule=='E'].ret_pct)}",
      f"- 반등 뒤 숏: {summ(done[done.rule=='반등뒤숏'].ret_pct)}", "",
      "## 전체 기록", "", "| 규칙 | 신호일 | 진입 | 청산 | 수익률 | 상태 | 대안 청산 | 비고 |", "|---|---|---|---|---|---|---|---|"]
for _, x in df.iterrows():
    ent = f"{x.entry_date} {x.entry}" if pd.notna(x.entry) else ""
    ex = f"{x.exit_date} {x.exit}" if pd.notna(x.exit) else ""
    ret = f"{x.ret_pct:+.1f}%" if pd.notna(x.ret_pct) else ""
    alt = f"{x.alt_name} {x.alt_pct:+.1f}% ({x.alt_status})" if pd.notna(x.alt_pct) else ""
    md.append(f"| {x.rule} | {x.signal} | {ent} | {ex} | {ret} | {x.status} | {alt} | {'' if pd.isna(x.note) else x.note} |")
open(os.path.join(ROOT, "ledger", "paper_trades.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md))
