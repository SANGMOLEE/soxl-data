# -*- coding: utf-8 -*-
# 반등 크기 검사 (사전 고정: 2026-10-23_rally_check_preregistration.md §3)
import numpy as np, pandas as pd, runpy
G = runpy.run_path('nail/research/bottom_study.py', run_name='lib')
NAIL, ITB, A, C = G['NAIL'], G['ITB'], G['A'], G['C']
OUT = 'nail/research/output'
c = NAIL.close; ic = ITB.close.reindex(c.index).ffill()
ma50 = c.rolling(50).mean(); ima50 = ic.rolling(50).mean()

# 이번 사이클 기준 저점 L: 마지막 252거래일 최저 종가
w = c.iloc[-252:]; Ld = w.idxmin(); L = w.min(); iL = c.index.get_loc(Ld); k = len(c) - 1 - iL
Rk = c.iloc[-1] / L - 1; Mk = c.iloc[iL:].max() / L - 1
print(f'기준 저점 {Ld.date()} {L:.2f} | 마지막 {c.index[-1].date()} {c.iloc[-1]:.2f} | k={k}거래일 | R_k {Rk:+.1%} | M_k {Mk:+.1%} (최고 {c.iloc[iL:].idxmax().date()} {c.iloc[iL:].max():.2f})')
print(f'현재 NAIL>50일선 {c.iloc[-1] > ma50.iloc[-1]} ({c.iloc[-1]:.2f} vs {ma50.iloc[-1]:.2f}) | ITB>50일선 {ic.iloc[-1] > ima50.iloc[-1]} ({ic.iloc[-1]:.2f} vs {ima50.iloc[-1]:.2f})')

fl = pd.read_csv(f'{OUT}/fresh_low_rebound_8.csv'); fl = fl[~fl.status.str.startswith('진행')]
sets = {'A 진짜 바닥': list(A.date), 'C 실패 저점': list(C.date), 'D 1년 신저가 저점(+8% 반등 동반)': list(fl.low_date)}
rows = []
for nm, ds in sets.items():
    for d in ds:
        i = c.index.get_loc(pd.Timestamp(d)); lo = c.iloc[i]
        if i + k >= len(c): continue
        fut = c.iloc[i + 1:i + 127]; held = bool((fut >= lo).all()) if len(fut) >= 126 else None
        brk = int(np.argmax(fut.values < lo)) + 1 if (fut < lo).any() else None
        pre = c.iloc[i + 1:i + brk] if brk else fut
        rows.append(dict(set=nm, low_date=d, low=round(lo, 2), ret_k=c.iloc[i + k] / lo - 1, max_k=c.iloc[i:i + k + 1].max() / lo - 1,
                         nail_gt_ma50=bool(c.iloc[i + k] > ma50.iloc[i + k]), itb_gt_ma50=bool(ic.iloc[i + k] > ima50.iloc[i + k]),
                         held_126=held, break_day=brk, max_rally_before_break=(pre.max() / lo - 1) if len(pre) else np.nan))
X = pd.DataFrame(rows); X.to_csv(f'{OUT}/rally_check.csv', index=False, float_format='%.4f')
pd.set_option('display.width', 220)
print(X.assign(ret_k=lambda d: (d.ret_k * 100).round(1), max_k=lambda d: (d.max_k * 100).round(1),
               max_rally_before_break=lambda d: (d.max_rally_before_break * 100).round(1)).to_string(index=False))
print('\n=== 같은 k에서의 비교 ===')
for nm in sets:
    s = X[X.set == nm]
    print(f'{nm}: n={len(s)} | ret_k 중앙 {s.ret_k.median():+.1%} | ret_k ≥ 현재({Rk:+.1%}) {int((s.ret_k >= Rk).sum())} | max_k ≥ 현재({Mk:+.1%}) {int((s.max_k >= Mk).sum())}'
          f' | NAIL>50일선 {int(s.nail_gt_ma50.sum())} | ITB>50일선 {int(s.itb_gt_ma50.sum())}')
D = X[X.set.str.startswith('D')]
for lab, m in [('ret_k ≥ 현재', D.ret_k >= Rk), ('max_k ≥ 현재', D.max_k >= Mk), ('NAIL>50일선', D.nail_gt_ma50), ('ITB>50일선', D.itb_gt_ma50)]:
    s = D[m]; print(f'D 중 {lab}: {len(s)}건 → 저점 유지 {int((s.held_126 == True).sum())}건', list(zip(s.low_date, s.held_126)))
f = X[X.set.str.startswith('C')]
print(f'\n실패 저점이 깨지기 전 최고 반등: 중앙 {f.max_rally_before_break.median():+.1%}, 범위 {f.max_rally_before_break.min():+.1%} ~ {f.max_rally_before_break.max():+.1%}')
