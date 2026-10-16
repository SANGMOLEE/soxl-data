# -*- coding: utf-8 -*-
# 보조 분석(사전 고정 §6을 실시간 판정 형태로 다듬은 것). bottom_study.py 결과를 재사용.
import numpy as np, pandas as pd, runpy
G = runpy.run_path('nail/research/bottom_study.py', run_name='lib')
NAIL, SPY, TD, VIX, HY, Y10, MTG, A, C, hy_pct, pos = (G[k] for k in ['NAIL','SPY','TD','VIX','HY','Y10','MTG','A','C','hy_pct','pos'])
OUT = 'nail/research/output'; c = NAIL.close
def rt(t):
    """실시간(그날까지 자료만) 지표"""
    i = pos[t]; s = SPY.close
    return dict(date=t.date().isoformat(),
        SPY_vs63low=s.loc[t] / s.iloc[max(0, i-62):i+1].min() - 1,
        SPY_dd252=s.loc[t] / s.iloc[max(0, i-251):i+1].max() - 1,
        VIX_vs63max=VIX.loc[t] / VIX.iloc[max(0, i-62):i+1].max(),
        VIX_max21_is_max63=VIX.iloc[max(0, i-20):i+1].max() >= VIX.iloc[max(0, i-62):i+1].max(),
        HY_pct=hy_pct(t), HY_chg63=(HY.loc[t]-HY.iloc[max(0,i-63)])*100,
        HY_max21_is_max63=HY.iloc[max(0, i-20):i+1].max() >= HY.iloc[max(0, i-62):i+1].max(),
        Y10_from252max_bp=(Y10.loc[t]-Y10.iloc[max(0,i-251):i+1].max())*100,
        Y10_peak_days_ago=i - int(np.argmax(Y10.iloc[max(0,i-251):i+1].values)) - max(0,i-251),
        MTG_from52wmax=MTG.loc[t]-MTG.iloc[max(0,i-251):i+1].max())
RA = pd.DataFrame([rt(pd.Timestamp(d)) for d in A.date]); RA.insert(0,'set','A 진짜 저점')
RC = pd.DataFrame([rt(pd.Timestamp(d)) for d in C.date]); RC.insert(0,'set','C 실패 저점')
RN = pd.DataFrame([rt(pd.Timestamp(d)) for d in ['2026-10-14', str(c.index[-1].date())]]); RN.insert(0,'set','현재')
RT = pd.concat([RA, RC, RN]); RT.to_csv(f'{OUT}/realtime_checks.csv', index=False, float_format='%.4f')
pd.set_option('display.width', 250); print(RT.round(3).to_string(index=False))
chk = {'HY 10년 백분위 ≥45': lambda r: r.HY_pct >= 45, 'SPY가 63일 최저 +5% 이내': lambda r: r.SPY_vs63low <= 0.05,
       'VIX 최근 21일 안에 63일 최고': lambda r: bool(r.VIX_max21_is_max63), 'HY 최근 21일 안에 63일 최고': lambda r: bool(r.HY_max21_is_max63),
       'HY 63일 +50bp 이상': lambda r: r.HY_chg63 >= 50, '10년물 252일 최고 대비 −25bp 이하': lambda r: r.Y10_from252max_bp <= -25,
       'SPY 252일 낙폭 ≤−10%': lambda r: r.SPY_dd252 <= -0.10}
rows = []
for k, f in chk.items():
    a = [f(r) for _, r in RA.iterrows()]; cc = [f(r) for _, r in RC.iterrows()]; n = [f(r) for _, r in RN.iterrows()]
    rows.append(dict(조건=k, A=f'{sum(a)}/7', A_사례=''.join('O' if x else 'x' for x in a), C=f'{sum(cc)}/{len(cc)}', 현재_1014=n[0], 마지막=n[1]))
K = pd.DataFrame(rows); K.to_csv(f'{OUT}/realtime_commonality.csv', index=False); print(K.to_string(index=False))

# 새 252일 최저 종가에서 10거래일 안의 +8%/+10% 급반등 → 그 저점이 126거래일 동안 지켜졌나
def fresh_low_rebound(th):
    r1 = c.pct_change(); dd = c / c.rolling(252, min_periods=60).max() - 1; lo252 = c.rolling(252, min_periods=60).min()
    rows = []; used = set()
    for i in range(1, len(c)):
        if r1.iloc[i] < th: continue
        j0 = max(0, i-10); w = c.iloc[j0:i]; jl = j0 + int(np.argmin(w.values)); L = c.iloc[jl]
        if L > lo252.iloc[jl] + 1e-9 or dd.iloc[jl] > -0.50 or jl in used: continue
        used.add(jl); fut = c.iloc[i+1:i+127]
        rows.append(dict(rebound=c.index[i].date().isoformat(), ret=round(r1.iloc[i]*100,1), low_date=c.index[jl].date().isoformat(), low=round(L,2),
                         dd252_at_low=round(dd.iloc[jl]*100,1), status=('지켜짐' if (fut >= L).all() else '깨짐') if len(fut) >= 126 else f'진행중({len(fut)}일)',
                         min_after=round((fut.min()/L-1)*100,1) if len(fut) else None, days_to_break=(int(np.argmax(fut.values < L))+1) if len(fut) and (fut < L).any() else None))
    return pd.DataFrame(rows)
for th in (0.08, 0.10):
    F = fresh_low_rebound(th); F.to_csv(f'{OUT}/fresh_low_rebound_{int(th*100)}.csv', index=False)
    done = F[~F.status.str.startswith('진행')]
    print(f'\n=== 새 1년 최저 종가 후 10거래일 안 +{int(th*100)}% 급반등: 완료 {len(done)}건 중 지켜짐 {int((done.status=="지켜짐").sum())} ===')
    print(F.to_string(index=False))

# 252일 낙폭 −65% 첫 도달 에피소드 → 이후 252거래일 최저까지
dd = c / c.rolling(252, min_periods=60).max() - 1
first = []; last_i = -999
for i in range(len(c)):
    if dd.iloc[i] <= -0.65:
        if i - last_i > 63: first.append(i)
        last_i = i
rows = []
for i in first:
    fut = c.iloc[i+1:i+253]
    rows.append(dict(first_day=c.index[i].date().isoformat(), close=round(c.iloc[i],2), dd=round(dd.iloc[i]*100,1),
                     min_252=round((fut.min()/c.iloc[i]-1)*100,1) if len(fut) else None, min_date=fut.idxmin().date().isoformat() if len(fut) else None,
                     days_to_min=int(np.argmin(fut.values))+1 if len(fut) else None, fwd_days=len(fut)))
E = pd.DataFrame(rows); E.to_csv(f'{OUT}/first_cross_65.csv', index=False); print('\n=== 252일 낙폭 −65% 첫 도달(63거래일 공백으로 구분) ===\n', E.to_string(index=False))

# 저점 이후 경로(진짜 저점 7개): 1·5·10·21·63거래일 수익률, 저점 후 첫 +8% 일까지 일수
rows = []
for d in A.date:
    i = c.index.get_loc(pd.Timestamp(d)); L = c.iloc[i]
    f = lambda k: round((c.iloc[i+k]/L-1)*100,1)
    r1 = c.pct_change().iloc[i+1:i+22]
    rows.append(dict(bottom=d, d1=f(1), d5=f(5), d10=f(10), d21=f(21), d63=f(63), first_8pct_day=(int(np.argmax(r1.values>=0.08))+1) if (r1>=0.08).any() else None,
                     max_dd_after_21=round((c.iloc[i+1:i+22].min()/L-1)*100,1)))
P = pd.DataFrame(rows); P.to_csv(f'{OUT}/post_bottom_path.csv', index=False); print('\n=== 진짜 저점 이후 경로(%) ===\n', P.to_string(index=False))
print('\n최근 금리:', Y10.loc['2026-08-01':].dropna().resample('W-FRI').last().round(2).to_dict())
print('10년물 252일 최고:', Y10.loc['2025-10-15':].max(), Y10.loc['2025-10-15':].idxmax().date())
print('모기지:', G['M']['MORTGAGE30US'].loc['2026-06-01':].to_dict())

# 급반등 사건을 저점일 HY 백분위로 나눔(실시간 판별력 점검)
for th in (0.08, 0.10):
    F = pd.read_csv(f'{OUT}/fresh_low_rebound_{int(th*100)}.csv'); F = F[~F.status.str.startswith('진행')].copy()
    F['HY_pct_at_low'] = [hy_pct(pd.Timestamp(d)) for d in F.low_date]
    F['VIX21max_is_63max'] = [bool(rt(pd.Timestamp(d))['VIX_max21_is_max63']) for d in F.low_date]
    for lab, m in [('HY≥45', F.HY_pct_at_low >= 45), ('HY<45', F.HY_pct_at_low < 45)]:
        s = F[m]; print(f'+{int(th*100)}% {lab}: {len(s)}건 중 지켜짐 {int((s.status=="지켜짐").sum())}', list(zip(s.low_date, s.HY_pct_at_low.round(0), s.status)))
    F.to_csv(f'{OUT}/fresh_low_rebound_{int(th*100)}_hy.csv', index=False)
