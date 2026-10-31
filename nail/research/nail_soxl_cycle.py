# -*- coding: utf-8 -*-
# NAIL과 나스닥·SOXL의 상관관계와 사이클 겹침 (사전 고정: 2026-10-31_nail_soxl_cycle_preregistration.md)
# 실행: python3 nail/research/nail_soxl_cycle.py   출력: 화면 + nail/research/output/cycle_*.csv
import numpy as np, pandas as pd
R = 'nail/data/prices'; OUT = 'nail/research/output'
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
def px(n): return pd.read_csv(f'{R}/{n}.csv', parse_dates=['date']).set_index('date')
D = {n: px(n) for n in ['NAIL', 'SOXL', 'ITB', 'SOXX', 'SOX', 'QQQ', 'NDX', 'SPY', 'TNX']}
A = pd.DataFrame({n: D[n].adj_close for n in D if n != 'TNX'}); C = pd.DataFrame({n: D[n].close for n in D if n != 'TNX'})
Y = D['TNX'].close                                      # 10년물(%)
T0 = D['NAIL'].index[0]
lr = np.log(A).diff()
def corr(a, b, freq, start=T0):
    x = A[[a, b]].loc[start:].dropna()
    if freq == 'D': r = np.log(x).diff()
    else: r = np.log(x.resample(freq).last()).diff()
    return r.corr().iloc[0, 1], len(r.dropna())

print('=' * 100, '\n[2-1·2-2] 수익률 상관 (전 기간 겹침)')
rows = []
for a, b, st in [('NAIL', 'SOXL', T0), ('NAIL', 'QQQ', T0), ('NAIL', 'SPY', T0), ('SOXL', 'QQQ', T0), ('NAIL', 'ITB', T0),
                 ('ITB', 'SOXX', pd.Timestamp('2006-05-05')), ('ITB', 'QQQ', pd.Timestamp('2006-05-05')), ('ITB', 'SPY', pd.Timestamp('2006-05-05'))]:
    rows.append(dict(쌍=f'{a}–{b}', 시작=st.date(), 일간=round(corr(a, b, 'D', st)[0], 2), 주간=round(corr(a, b, 'W-FRI', st)[0], 2), 월간=round(corr(a, b, 'ME', st)[0], 2)))
K = pd.DataFrame(rows); print(K.to_string(index=False)); K.to_csv(f'{OUT}/cycle_corr.csv', index=False)

print('\n[2-3] 52주 이동 상관(주간 수익률) — 연도별 평균, 최근 13주')
W = np.log(A.resample('W-FRI').last()).diff().loc[T0:]
roll = pd.DataFrame({f'{a}–{b}': W[a].rolling(52).corr(W[b]) for a, b in [('NAIL', 'SOXL'), ('NAIL', 'QQQ'), ('SOXL', 'QQQ')]})
print(roll.groupby(roll.index.year).mean().round(2).T.to_string())
print('최근 13주 상관:', {f'{a}–{b}': round(W[a].iloc[-13:].corr(W[b].iloc[-13:]), 2) for a, b in [('NAIL', 'SOXL'), ('NAIL', 'QQQ'), ('SOXL', 'QQQ'), ('NAIL', 'SPY')]})
print('52주 상관 최저·최고(NAIL–SOXL):', round(roll['NAIL–SOXL'].min(), 2), roll['NAIL–SOXL'].idxmin().date(), '/', round(roll['NAIL–SOXL'].max(), 2), roll['NAIL–SOXL'].idxmax().date(), '| 현재', round(roll['NAIL–SOXL'].iloc[-1], 2))
roll.to_csv(f'{OUT}/cycle_rolling_corr.csv', float_format='%.4f')

print('\n[2-4] 나스닥 급락일·조정 구간의 NAIL')
r = lr.loc[T0:].copy(); dy = (Y.diff() * 100).reindex(r.index)
dn = r[r.QQQ <= np.log(0.98)]
print(f'QQQ −2% 이하 {len(dn)}일: NAIL 평균 {np.expm1(dn.NAIL.mean()):+.2%} (하락 비율 {(dn.NAIL < 0).mean():.0%}), SOXL 평균 {np.expm1(dn.SOXL.mean()):+.2%} (하락 {(dn.SOXL < 0).mean():.0%}), 그날 10년물 평균 {dy.reindex(dn.index).mean():+.1f}bp')
for lab, m in [('그날 10년물 하락(−5bp 이하)', dy.reindex(dn.index) <= -5), ('그날 10년물 상승·보합(−5bp 초과)', dy.reindex(dn.index) > -5)]:
    s = dn[m.values]; print(f'   {lab}: {len(s)}일, NAIL 평균 {np.expm1(s.NAIL.mean()):+.2%} 하락비율 {(s.NAIL < 0).mean():.0%} | SOXL {np.expm1(s.SOXL.mean()):+.2%}')
# QQQ 조정 구간(종가 지그재그 10%)
def zigzag(s, th):
    v = s.values; ix = s.index; piv = []; mode = 0; hi = lo = 0
    for i in range(1, len(v)):
        if v[i] > v[hi]: hi = i
        if v[i] < v[lo]: lo = i
        if mode >= 0 and v[i] <= v[hi] * (1 - th) and (mode == 1 or hi < i):
            if mode == 0 and lo < hi: piv.append((ix[lo], v[lo], 'L'))
            piv.append((ix[hi], v[hi], 'H')); mode = -1; lo = i
        elif mode <= 0 and v[i] >= v[lo] * (1 + th) and (mode == -1 or lo < i):
            if mode == 0 and hi < lo: piv.append((ix[hi], v[hi], 'H'))
            piv.append((ix[lo], v[lo], 'L')); mode = 1; hi = i
    return piv
qz = zigzag(C.QQQ.loc[T0:].dropna(), 0.10); ep = []
for (d1, v1, k1), (d2, v2, k2) in zip(qz, qz[1:]):
    if k1 == 'H' and k2 == 'L':
        g = lambda n: C[n].loc[d2] / C[n].loc[d1] - 1
        ep.append(dict(QQQ고점=d1.date(), QQQ저점=d2.date(), QQQ=f'{g("QQQ"):+.0%}', SOXL=f'{g("SOXL"):+.0%}', NAIL=f'{g("NAIL"):+.0%}', ITB=f'{g("ITB"):+.0%}',
                       **{'10년물bp': round((Y.asof(d2) - Y.asof(d1)) * 100)}))
# 진행 중 구간(마지막 고점 이후 아직 저점 미확정)
last = qz[-1]
if last[2] == 'H':
    d1 = last[0]; d2 = C.QQQ.loc[d1:].idxmin(); g = lambda n: C[n].loc[d2] / C[n].loc[d1] - 1
    ep.append(dict(QQQ고점=d1.date(), QQQ저점=f'{d2.date()}(진행 중)', QQQ=f'{g("QQQ"):+.0%}', SOXL=f'{g("SOXL"):+.0%}', NAIL=f'{g("NAIL"):+.0%}', ITB=f'{g("ITB"):+.0%}',
                   **{'10년물bp': round((Y.asof(d2) - Y.asof(d1)) * 100)}))
E = pd.DataFrame(ep); print('QQQ 10% 이상 조정 구간:'); print(E.to_string(index=False)); E.to_csv(f'{OUT}/cycle_qqq_corrections.csv', index=False)
# 진행 중 구간이 없으면 최근 63거래일 QQQ 최고점 이후를 별도로 표시
q63 = C.QQQ.iloc[-63:]; d1 = q63.idxmax(); d2 = C.QQQ.loc[d1:].idxmin()
g = lambda n: C[n].loc[d2] / C[n].loc[d1] - 1
print(f'최근: QQQ 63일 고점 {d1.date()} → 이후 최저 {d2.date()}: QQQ {g("QQQ"):+.1%}, SOXL {g("SOXL"):+.1%}, NAIL {g("NAIL"):+.1%}, ITB {g("ITB"):+.1%}, 10년물 {(Y.asof(d2)-Y.asof(d1))*100:+.0f}bp')

print('\n[2-5] 일간 수익률 회귀: r = a + b·QQQ + c·Δ10년물(bp)  (c는 10bp당 %)')
X = pd.DataFrame({'Q': r.QQQ, 'dy': dy}).dropna()
def ols(yv, Xm):
    Xm = np.column_stack([np.ones(len(Xm)), Xm]); b, *_ = np.linalg.lstsq(Xm, yv, rcond=None)
    res = yv - Xm @ b; r2 = 1 - res.var() / yv.var(); return b, r2
reg = []
for nm in ['NAIL', 'ITB', 'SOXL', 'SOXX']:
    for lab, st in [('전 기간', T0), ('최근 1년', r.index[-252]), ('최근 3개월', r.index[-63])]:
        idx = X.loc[st:].index.intersection(r[nm].dropna().index); yv = r[nm].reindex(idx).values; xm = X.reindex(idx).values
        b, r2 = ols(yv, xm); b1, r21 = ols(yv, xm[:, :1])
        reg.append(dict(종목=nm, 구간=lab, 나스닥베타=round(b[1], 2), 금리10bp당=f'{b[2]*10*100:+.2f}%', 설명력_둘다=round(r2, 2), 설명력_나스닥만=round(r21, 2)))
G = pd.DataFrame(reg); print(G.to_string(index=False)); G.to_csv(f'{OUT}/cycle_regression.csv', index=False)
# 나스닥과 금리의 같이 움직임
print('QQQ 일간 수익률과 10년물 변화의 상관:', {lab: round(X.Q.loc[st:].corr(X.dy.loc[st:]), 2) for lab, st in [('전 기간', T0), ('최근 1년', r.index[-252]), ('최근 3개월', r.index[-63])]})

print('\n' + '=' * 100, '\n[3] 사이클')
for th in (0.40, 0.50, 0.60):
    nz = [p for p in zigzag(C.NAIL.dropna(), th)]; sz = [p for p in zigzag(C.SOXL.loc[T0:].dropna(), th)]
    print(f'지그재그 {int(th*100)}%: NAIL 저점 {[d.date().isoformat() for d, v, k in nz if k == "L"]}')
    print(f'                SOXL 저점 {[d.date().isoformat() for d, v, k in sz if k == "L"]}')
    print(f'                NAIL 고점 {[d.date().isoformat() for d, v, k in nz if k == "H"]}')
    print(f'                SOXL 고점 {[d.date().isoformat() for d, v, k in sz if k == "H"]}')
nz = zigzag(C.NAIL.dropna(), 0.50); sz = zigzag(C.SOXL.loc['2014-01-01':].dropna(), 0.50)
NL = [d for d, v, k in nz if k == 'L']; NH = [d for d, v, k in nz if k == 'H']; SL = [d for d, v, k in sz if k == 'L']; SH = [d for d, v, k in sz if k == 'H']
idx = C.index
def state(n, t):
    s = C[n].dropna(); i = s.index.get_loc(t); w = s.iloc[max(0, i - 252): i + 253]
    return dict(dd252=s.iloc[i] / s.iloc[max(0, i - 251): i + 1].max() - 1, pos=100 * (s.iloc[i] - w.min()) / (w.max() - w.min()))
def nearest(t, L, s):
    if not L: return None
    ii = C[s].dropna().index; k = min(L, key=lambda d: abs(ii.get_loc(d) - ii.get_loc(t))); return k.date(), ii.get_loc(k) - ii.get_loc(t)
NAIL7 = ['2016-02-11', '2016-11-02', '2018-12-24', '2020-03-23', '2022-10-20', '2023-10-25', '2025-04-08']
rows = []
for d in NAIL7:
    t = pd.Timestamp(d); s = state('SOXL', t); n = state('NAIL', t)
    nl = nearest(t, SL, 'SOXL'); nh = nearest(t, SH, 'SOXL')
    rows.append(dict(NAIL저점=d, NAIL_1년낙폭=f'{n["dd252"]:+.0%}', SOXL_1년낙폭=f'{s["dd252"]:+.0%}', SOXL_가격위치=round(s['pos']), 가까운_SOXL저점=f'{nl[0]} ({nl[1]:+d}일)', 가까운_SOXL고점=f'{nh[0]} ({nh[1]:+d}일)'))
P1 = pd.DataFrame(rows); print('\n[3-2] NAIL 저점 7개에서의 SOXL (가격위치: ±1년 창 0=최저 100=최고, 일=거래일, +는 NAIL 저점 뒤)'); print(P1.to_string(index=False)); P1.to_csv(f'{OUT}/cycle_nail_bottoms_vs_soxl.csv', index=False)
rows = []
for d, v, k in sz:
    if d < T0: continue
    n = state('NAIL', d); s = state('SOXL', d); nl = nearest(d, NL, 'NAIL'); nh = nearest(d, NH, 'NAIL')
    rows.append(dict(SOXL=('고점' if k == 'H' else '저점'), 날짜=d.date(), SOXL_1년낙폭=f'{s["dd252"]:+.0%}', NAIL_1년낙폭=f'{n["dd252"]:+.0%}', NAIL_가격위치=round(n['pos']),
                     가까운_NAIL저점=f'{nl[0]} ({nl[1]:+d}일)' if nl else '', 가까운_NAIL고점=f'{nh[0]} ({nh[1]:+d}일)' if nh else ''))
P2 = pd.DataFrame(rows); print('\n[3-3] SOXL 사이클 고점·저점(지그재그 50%)에서의 NAIL'); print(P2.to_string(index=False)); P2.to_csv(f'{OUT}/cycle_soxl_pivots_vs_nail.csv', index=False)
print('\n[3-4] NAIL 지그재그 50% 저점 ↔ SOXL 저점 짝(±126거래일)')
for d in NL:
    nl = nearest(d, SL, 'SOXL'); print(f'  NAIL {d.date()} ↔ SOXL {nl[0]} ({nl[1]:+d}일)', '짝' if abs(nl[1]) <= 126 else '짝 없음')
print('\n[3-5] 1년 낙폭 상태 겹침(매일, 2016-08 이후 = 두 종목 252일 창 완비)')
dd = pd.DataFrame({n: C[n] / C[n].rolling(252).max() - 1 for n in ['NAIL', 'SOXL']}).loc['2016-08-17':].dropna()
ct = pd.crosstab(dd.NAIL <= -0.5, dd.SOXL <= -0.5, normalize=True).round(3); ct.index = ['NAIL 얕음', 'NAIL 깊음(≤−50%)']; ct.columns = ['SOXL 얕음', 'SOXL 깊음(≤−50%)']
print(ct.to_string()); print('1년 낙폭 상관:', round(dd.NAIL.corr(dd.SOXL), 2))
print('연도별 1년 낙폭 평균:'); print((dd.groupby(dd.index.year).mean() * 100).round(0).T.to_string())
print('\n[3-6] 현재')
for n in ['NAIL', 'SOXL', 'QQQ', 'ITB']:
    s = C[n].dropna(); print(f'  {n}: {s.index[-1].date()} 종가 {s.iloc[-1]:.2f} · 1년 낙폭 {s.iloc[-1]/s.iloc[-252:].max()-1:+.1%} · 사상최고 대비 {s.iloc[-1]/s.max()-1:+.1%} (최고 {s.idxmax().date()}) · 1년 최저 대비 {s.iloc[-1]/s.iloc[-252:].min()-1:+.1%}')
