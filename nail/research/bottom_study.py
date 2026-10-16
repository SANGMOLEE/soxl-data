# -*- coding: utf-8 -*-
"""
NAIL 과거 최저점 환경·공통점 연구 + "최저점 통과 여부" 기준률 (사전 고정: 2026-10-16_bottom_study_preregistration.md)
실행: python3 nail/research/bottom_study.py   (nail/data 원자료, nail/output/engine/r8_daily.csv 필요)
출력: nail/research/output/*.csv, 화면 요약
"""
import os, importlib.util
import numpy as np, pandas as pd

R = 'nail/data'; OUT = 'nail/research/output'; os.makedirs(OUT, exist_ok=True)
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 60); pd.set_option('display.max_colwidth', 40)

def px(n):
    d = pd.read_csv(f'{R}/prices/{n}.csv', parse_dates=['date']).set_index('date'); return d
def mac(n):
    d = pd.read_csv(f'{R}/macro/{n}.csv', parse_dates=['date']).set_index('date').value; return d.dropna()

NAIL, ITB, SPY = px('NAIL'), px('ITB'), px('SPY')
M = {k: mac(k) for k in ['VIXCLS', 'BAMLH0A0HYM2', 'DGS10', 'DGS2', 'MORTGAGE30US', 'DFF', 'CPIAUCSL', 'UNRATE', 'USREC',
                         'NFCI', 'HOUST', 'PERMIT', 'HSN1F', 'MSACSR', 'T10Y2Y', 'DCOILWTICO']}
TD = SPY.index                                  # 거래일 달력(SPY)
pos = {d: i for i, d in enumerate(TD)}

# 엔진 함수 재사용(ITB A블록을 2006년부터 계산)
spec = importlib.util.spec_from_file_location('eng', 'nail/engine/nail_r9_engine_v1.2.py'); eng = importlib.util.module_from_spec(spec); spec.loader.exec_module(eng)
sessions, _ = eng.get_sessions(TD[0], TD[-1] + pd.Timedelta(days=14))
tdA = TD[TD >= ITB.index[0]]
_, APARTS = eng.block_A_raw(ITB, SPY, tdA, sessions)

def asof(s, t):
    s = s[s.index <= t]; return (s.iloc[-1], s.index[-1]) if len(s) else (np.nan, None)

def hy_pct(t):
    hy = M['BAMLH0A0HYM2']; v, d0 = asof(hy, t)
    if d0 is None: return np.nan
    p = hy[(hy.index >= d0 - pd.DateOffset(years=10)) & (hy.index < d0)]
    return 100 * np.mean(p.values <= v) if len(p) >= 1000 else np.nan

def on_td(s):   # 일별 시계열을 거래일로 맞춤(이월)
    return s.reindex(TD.union(s.index)).ffill().reindex(TD)

VIX = on_td(M['VIXCLS']); HY = on_td(M['BAMLH0A0HYM2']); Y10 = on_td(M['DGS10']); Y2 = on_td(M['DGS2'])
MTG = on_td(M['MORTGAGE30US']); FF = on_td(M['DFF']); NFCI = on_td(M['NFCI'])
SPYc = SPY.close; ITBc = ITB.close.reindex(TD)

# 합성 3배(표본 D): ITB 총수익 일간 수익률 ×3 − (2×DFF + 0.95%)/252
itr = ITB.adj_close.pct_change()
cost = (2 * FF.reindex(itr.index).ffill() / 100 + 0.0095) / 252
syn_r = 3 * itr - cost
SYN = (1 + syn_r.fillna(0)).cumprod() * 100
# NAIL 상장 뒤 구간에서 합성과 실제의 추적 정도
ov = NAIL.index[NAIL.index >= '2015-09-01']
nr = NAIL.adj_close.pct_change().reindex(ov); sr = syn_r.reindex(ov)
TRACK = dict(corr=round(nr.corr(sr), 4), ann_gap=round(((1 + nr).prod() ** (252 / len(ov)) - (1 + sr).prod() ** (252 / len(ov))) * 100, 2))
# 이어 붙인 'NAIL 확장' 가격(2015-08-19 이전 합성, 이후 실제 종가)
k0 = NAIL.index[0]
EXT = pd.concat([SYN[SYN.index < k0] / SYN.loc[k0] * NAIL.close.loc[k0], NAIL.close]).sort_index()

def zigzag(s, th):
    """종가 지그재그. th 이상 반대 방향 움직임이 나오면 직전 극점 확정. 반환 [(날짜, 값, 'L'/'H')]"""
    v = s.values; ix = s.index; piv = []; mode = 0; hi_i = lo_i = 0
    for i in range(1, len(v)):
        if v[i] > v[hi_i]: hi_i = i
        if v[i] < v[lo_i]: lo_i = i
        if mode >= 0 and v[i] <= v[hi_i] * (1 - th) and (mode == 1 or hi_i < i):
            if mode == 0 and lo_i < hi_i: piv.append((ix[lo_i], v[lo_i], 'L'))
            piv.append((ix[hi_i], v[hi_i], 'H')); mode = -1; lo_i = i
        elif mode <= 0 and v[i] >= v[lo_i] * (1 + th) and (mode == -1 or lo_i < i):
            if mode == 0 and hi_i < lo_i: piv.append((ix[hi_i], v[hi_i], 'H'))
            piv.append((ix[lo_i], v[lo_i], 'L')); mode = 1; hi_i = i
    return piv

def win(series, t, a, b):
    i = pos[t]; return series.iloc[max(0, i + a): min(len(series), i + b + 1)]

def peak_lag(series, t, a, b, mode='max'):
    w = win(series.reindex(TD), t, a, b).dropna()
    if not len(w): return np.nan
    d = w.idxmax() if mode == 'max' else w.idxmin()
    return pos[d] - pos[t]

def env(t, price=None, label=''):
    """저점일 t의 환경 변수(사전 고정 §4)"""
    t = TD[TD.searchsorted(t)] if t not in pos else t
    i = pos[t]; r = dict(date=t.date().isoformat(), label=label)
    P = (price if price is not None else NAIL.close)
    if t in P.index:
        h252 = P.loc[:t].tail(252); r['NAIL_dd252'] = P.loc[t] / h252.max() - 1
        r['NAIL_ddATH'] = P.loc[t] / P.loc[:t].max() - 1
        r['days_from_252hi'] = len(P.loc[h252.idxmax():t]) - 1
    if t in APARTS.index:
        a = APARTS.loc[t]; r.update(ITB_dd756=a.A1_dd756, ITB_rs504=a.A2_rs504, ITB_rsiW=a.A3_rsiW, ITB_ma200w=a.A4_ma200w)
    r['ITB_low_lag'] = peak_lag(ITBc, t, -63, 63, 'min')
    r['SPY_dd252'] = SPYc.loc[t] / SPYc.loc[:t].tail(252).max() - 1
    r['SPY_low_lag'] = peak_lag(SPYc, t, -63, 63, 'min')
    r['HY'] = HY.loc[t]; r['HY_pct10y'] = hy_pct(t); r['HY_chg63_bp'] = (HY.loc[t] - HY.iloc[max(0, i - 63)]) * 100
    r['HY_peak_lag'] = peak_lag(HY, t, -63, 63)
    r['VIX'] = VIX.loc[t]; r['VIX60max'] = VIX.iloc[max(0, i - 59): i + 1].max(); r['VIX_peak_lag'] = peak_lag(VIX, t, -63, 63)
    r['Y10'] = Y10.loc[t]; r['Y10_vs252max_bp'] = (Y10.loc[t] - Y10.iloc[max(0, i - 251): i + 1].max()) * 100
    r['Y10_chg63_bp'] = (Y10.loc[t] - Y10.iloc[max(0, i - 63)]) * 100; r['Y10_peak_lag'] = peak_lag(Y10, t, -126, 63)
    r['Y2'] = Y2.loc[t]; r['Y2_peak_lag'] = peak_lag(Y2, t, -126, 63)
    r['MTG'] = MTG.loc[t]; r['MTG_vs52wmax'] = MTG.loc[t] - MTG.iloc[max(0, i - 251): i + 1].max(); r['MTG_peak_lag'] = peak_lag(MTG, t, -126, 63)
    r['FF'] = FF.loc[t]; r['FF_chg_prev126'] = FF.loc[t] - FF.iloc[max(0, i - 126)]
    r['FF_chg_next126'] = (FF.iloc[min(len(FF) - 1, i + 126)] - FF.loc[t]) if i + 126 < len(FF) else np.nan
    r['T10Y2Y'] = (Y10.loc[t] - Y2.loc[t])
    m = (t - pd.DateOffset(days=45)).to_period('M').to_timestamp()        # 발표 지연 감안: 45일 전 달
    cpi = M['CPIAUCSL']
    if m in cpi.index:
        yo = cpi.loc[m] / cpi.loc[m - pd.DateOffset(years=1)] - 1; yo3 = cpi.loc[m - pd.DateOffset(months=3)] / cpi.loc[m - pd.DateOffset(months=15)] - 1
        r['CPI_yoy'] = yo; r['CPI_yoy_chg3m_pp'] = (yo - yo3) * 100
    ur = M['UNRATE']
    if m in ur.index: r['UNRATE_chg12m'] = ur.loc[m] - ur.loc[m - pd.DateOffset(years=1)]
    r['USREC'] = M['USREC'].get(t.to_period('M').to_timestamp(), np.nan)
    r['NFCI'] = NFCI.loc[t]
    for k in ('HOUST', 'PERMIT', 'HSN1F'):
        s = M[k]
        if m in s.index: r[f'{k}_yoy'] = s.loc[m] / s.loc[m - pd.DateOffset(years=1)] - 1
    if m in M['MSACSR'].index: r['MSACSR'] = M['MSACSR'].loc[m]
    shock = (r['VIX60max'] >= 33) or (r['HY_pct10y'] >= 75 if r['HY_pct10y'] == r['HY_pct10y'] else False)
    rate = (r['Y10_peak_lag'] == r['Y10_peak_lag']) and (-63 <= r['Y10_peak_lag'] <= 21)
    r['type'] = '충격+금리' if shock and rate else '충격' if shock else '금리' if rate else '기타'
    return r

# ---------------- 표본
A_DATES = ['2016-02-11', '2016-11-02', '2018-12-24', '2020-03-23', '2022-10-20', '2023-10-25', '2025-04-08']
A = pd.DataFrame([env(pd.Timestamp(d), label='A') for d in A_DATES])

zz = zigzag(ITB.close, 0.30)
B_list = [(d, v) for d, v, k in zz if k == 'L']
B = pd.DataFrame([env(d, price=EXT, label='B') for d, v in B_list])
B['ITB_low'] = [v for _, v in B_list]
B['ITB_dd_from_prev_hi'] = [v / max([x for dd, x, k in zz if k == 'H' and dd < d] or [np.nan]) - 1 for d, v in B_list]

# 표본 C: NAIL 252일 낙폭 −50% 이하에서 25% 지그재그 저점 중, 126거래일 안에 깨진 것
nz = zigzag(NAIL.close, 0.25); C_rows = []
for d, v, k in nz:
    if k != 'L': continue
    dd = v / NAIL.close.loc[:d].tail(252).max() - 1
    fut = NAIL.close.loc[d:].iloc[1:127]
    if dd <= -0.50 and len(fut) and (fut < v).any():
        r = env(d, label='C'); r['broken_after_td'] = int(np.argmax(fut.values < v)) + 1
        r['next_low_vs'] = fut.min() / v - 1; C_rows.append(r)
C = pd.DataFrame(C_rows)

# 현재(10/14 사이클 최저 종가, 마지막 종가)
NOW = pd.DataFrame([env(pd.Timestamp('2026-10-14'), label='현재 저점'), env(NAIL.index[-1], label='마지막 종가')])

for nm, df in [('A', A), ('B', B), ('C', C), ('NOW', NOW)]:
    df.to_csv(f'{OUT}/env_{nm}.csv', index=False, float_format='%.4f')

# ---------------- 공통점 후보(사전 고정 §4 변수의 자연 경계)
CONDS = {
    'c01 NAIL 252일 낙폭 ≤ −50%': lambda r: r.NAIL_dd252 <= -0.50,
    'c02 ITB 주봉 RSI ≤ 40': lambda r: r.ITB_rsiW <= 40,
    'c03 ITB 200주선 아래': lambda r: r.ITB_ma200w <= 0,
    'c04 ITB/SPY 504일 위치 ≤ 20': lambda r: r.ITB_rs504 <= 20,
    'c05 ITB 저점이 ±10거래일 안': lambda r: abs(r.ITB_low_lag) <= 10,
    'c06 SPY 저점이 ±21거래일 안': lambda r: abs(r.SPY_low_lag) <= 21,
    'c07 SPY 252일 낙폭 ≤ −10%': lambda r: r.SPY_dd252 <= -0.10,
    'c08 HY 63일 +50bp 이상 상승': lambda r: r.HY_chg63_bp >= 50,
    'c09 HY 10년 백분위 ≥ 45': lambda r: r.HY_pct10y >= 45,
    'c10 HY 고점이 ±21거래일 안': lambda r: abs(r.HY_peak_lag) <= 21,
    'c11 VIX 60일 최고 ≥ 25': lambda r: r.VIX60max >= 25,
    'c12 VIX 고점이 ±21거래일 안': lambda r: abs(r.VIX_peak_lag) <= 21,
    'c13 10년물 고점이 −63~+21거래일': lambda r: -63 <= r.Y10_peak_lag <= 21,
    'c14 10년물 252일 최고 대비 −25bp 이상 하락': lambda r: r.Y10_vs252max_bp <= -25,
    'c15 모기지 고점이 −63~+21거래일': lambda r: -63 <= r.MTG_peak_lag <= 21,
    'c16 기준금리 이후 6개월 인하': lambda r: r.FF_chg_next126 <= -0.25,
    'c17 기준금리 직전 6개월 인상': lambda r: r.FF_chg_prev126 >= 0.25,
    'c18 CPI 상승률 둔화(3개월 전보다 낮음)': lambda r: r.CPI_yoy_chg3m_pp < 0,
    'c19 금리 하락 또는 스트레스 급등(c14 또는 c11)': lambda r: (r.Y10_vs252max_bp <= -25) or (r.VIX60max >= 25),
}
def tally(df, f):
    out = []
    for _, r in df.iterrows():
        try: v = bool(f(r))
        except Exception: v = None
        if v is not None and isinstance(v, (bool, np.bool_)):
            if any(pd.isna(x) for x in [r.get(k) for k in r.index if k.endswith('lag')] if False): pass
        out.append(v)
    return out
rows = []
for k, f in CONDS.items():
    a = tally(A, f); b = tally(B, f); c = tally(C, f); n = tally(NOW, f)
    rows.append(dict(조건=k, A=f'{sum(x is True for x in a)}/{len(a)}', A_사례=''.join('O' if x else 'x' for x in a),
                     B=f'{sum(x is True for x in b)}/{len(b)}', C실패저점=f'{sum(x is True for x in c)}/{len(c)}',
                     현재저점_1014=n[0], 마지막종가=n[1]))
T = pd.DataFrame(rows); T.to_csv(f'{OUT}/commonality.csv', index=False)

# ---------------- 급반등 기준률(§6-2)
def rebound_base(th, cluster=10):
    c = NAIL.close; r1 = c.pct_change(); dd = c / c.rolling(252, min_periods=60).max() - 1
    ev = c.index[(r1 >= th) & (dd.shift(1) <= -0.50)]
    rows = []; lastk = None
    for e in ev:
        i = c.index.get_loc(e)
        if lastk is not None and i - lastk <= cluster: continue
        lastk = i
        L = c.iloc[max(0, i - 10): i + 1].min(); Ld = c.iloc[max(0, i - 10): i + 1].idxmin()
        fut = c.iloc[i + 1: i + 127]
        done = len(fut) >= 126
        held = bool((fut >= L).all()) if len(fut) else None
        rows.append(dict(date=e.date().isoformat(), ret=round(r1.loc[e] * 100, 1), dd252=round(dd.shift(1).loc[e] * 100, 1),
                         prior_low=round(L, 2), prior_low_date=Ld.date().isoformat(), held_126=held if done else f'진행중({len(fut)}일)',
                         next_min_vs_low=round((fut.min() / L - 1) * 100, 1) if len(fut) else None,
                         ret_126=round((fut.iloc[-1] / c.loc[e] - 1) * 100, 1) if done else None))
    return pd.DataFrame(rows)
RB8 = rebound_base(0.08); RB10 = rebound_base(0.10)
RB8.to_csv(f'{OUT}/rebound_8pct.csv', index=False); RB10.to_csv(f'{OUT}/rebound_10pct.csv', index=False)

# ---------------- 추가 하락 기준률(§6-3): 252일 낙폭 −65% 이하인 날
def downside_base(P, lab, th=-0.65):
    dd = P / P.rolling(252, min_periods=60).max() - 1
    days = P.index[dd <= th]; rows = []
    for d in days:
        i = P.index.get_loc(d); fut = P.iloc[i + 1: i + 127]
        if len(fut) < 126: continue
        rows.append(dict(date=d, dd=dd.loc[d], further=fut.min() / P.loc[d] - 1, r126=fut.iloc[-1] / P.loc[d] - 1))
    X = pd.DataFrame(rows)
    if X.empty: return X, None
    X['episode'] = (X.date.diff().dt.days.fillna(999) > 60).cumsum()
    q = lambda s: ' / '.join(f'{v*100:+.0f}%' for v in s.quantile([0.1, 0.25, 0.5, 0.75, 0.9]))
    ep = X.groupby('episode').agg(start=('date', 'min'), end=('date', 'max'), days=('date', 'size'), worst_further=('further', 'min'),
                                  med_r126=('r126', 'median'))
    summ = dict(표본=lab, 일수=len(X), 에피소드=len(ep), 추가하락_분위=q(X.further), r126_분위=q(X.r126),
                추가하락_30이상_비율=f'{(X.further <= -0.30).mean():.0%}', r126_양수_비율=f'{(X.r126 > 0).mean():.0%}')
    return ep, summ
EP_N, S_N = downside_base(NAIL.close, 'NAIL 실제 2015~')
EP_S, S_S = downside_base(EXT[EXT.index < k0], '합성 3배 2006~2015')
EP_N.to_csv(f'{OUT}/downside_episodes_nail.csv'); EP_S.to_csv(f'{OUT}/downside_episodes_synthetic.csv')

if __name__ == '__main__':
    print('합성 3배 추적(2015-09~):', TRACK)
    show = ['date', 'type', 'NAIL_dd252', 'NAIL_ddATH', 'days_from_252hi', 'ITB_dd756', 'ITB_rsiW', 'ITB_ma200w', 'ITB_rs504', 'ITB_low_lag', 'SPY_dd252', 'SPY_low_lag',
            'HY', 'HY_pct10y', 'HY_chg63_bp', 'HY_peak_lag', 'VIX', 'VIX60max', 'VIX_peak_lag']
    show2 = ['date', 'Y10', 'Y10_vs252max_bp', 'Y10_chg63_bp', 'Y10_peak_lag', 'Y2_peak_lag', 'MTG', 'MTG_vs52wmax', 'MTG_peak_lag', 'FF', 'FF_chg_prev126', 'FF_chg_next126',
             'T10Y2Y', 'CPI_yoy', 'CPI_yoy_chg3m_pp', 'UNRATE_chg12m', 'USREC', 'NFCI', 'HOUST_yoy', 'PERMIT_yoy', 'HSN1F_yoy', 'MSACSR']
    for nm, df in [('A 연구 표준 7개', A), ('B ITB 지그재그 30%', B), ('C 실패 저점', C), ('현재', NOW)]:
        print(f'\n===== {nm} ({len(df)}) =====')
        print(df[[c for c in show if c in df]].round(3).to_string(index=False))
        print(df[[c for c in show2 if c in df]].round(3).to_string(index=False))
        if nm.startswith('C'): print(df[['date', 'broken_after_td', 'next_low_vs']].round(3).to_string(index=False))
    print('\n===== 공통점 =====\n', T.to_string(index=False))
    print('\n===== 급반등 +8% (낙폭 −50% 이하, 10거래일 묶음) =====\n', RB8.to_string(index=False))
    print('\n===== 급반등 +10% =====\n', RB10.to_string(index=False))
    print('\n===== 추가 하락 기준률 (252일 낙폭 ≤ −65%) =====')
    print(S_N); print(EP_N.round(3).to_string()); print(S_S); print(EP_S.round(3).to_string())
