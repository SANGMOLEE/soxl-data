# 낙폭 기준 A/B 시험: 1년(252일) 고점 vs 사이클 고점(사상 최고 종가). 나머지 규칙은 R8 v1.1 그대로(기준 58/48/38, 15% 간격, 1/3씩, 1년 낙폭 −30% 회복 시 재무장)
# 사전에 정한 판정 순서(결과 보기 전 고정):
#   ① 저점 탐지(점수): 사이클 저점일 ±5거래일 안에 표시점수 ≤58인 날이 있는가
#   ② 저점 근처 실제 매수: 저점 전 126~후 21거래일 안에, 저점 종가 +30% 이내 가격의 체결이 있는가
#   ③ 저점 +10% 이내 체결 수  ④ 평균단가 할증 중앙값(낮을수록)  ⑤ 최악 예산 손실(얕을수록)
import pandas as pd, numpy as np
base = pd.read_pickle('bundle/nail.pkl')
v11 = pd.read_csv('r8/v11_chart/r8_daily.csv', parse_dates=['date']).set_index('date')
df = base[['open','high','low','close','A']].copy(); df['S'] = v11['S'].reindex(df.index)
df.loc[pd.Timestamp('2026-09-22'), ['open','high','low','close','A','S']] = [np.nan, np.nan, np.nan, 32.25, 17, 0]
df = df.sort_index(); df['S'] = df['S'].fillna(0)
C = df.close.values; O = df.open.values; L = df.low.values; idx = df.index; n = len(df); pos = {d: i for i, d in enumerate(idx)}
def bands(x):
    x = np.asarray(x, float); out = np.zeros(len(x))
    for c, p in zip((-0.5,-0.6,-0.7,-0.8,-0.9), (10,20,30,40,50)): out = np.where((x <= c) & (p > out), p, out)
    return out
cl = df.close; a252 = cl.rolling(252, min_periods=60).max().values; aath = cl.cummax().values
dd252 = C / a252 - 1
TR = {'2016-02-11':'깊음','2016-11-02':'얕음','2018-12-24':'깊음','2020-03-23':'깊음','2022-10-20':'깊음','2023-10-25':'얕음','2025-04-08':'깊음'}
ST = pos[idx[idx >= pd.Timestamp('2016-01-01')][0]]
def sim(cond):
    used = 0; last = None; camp = 0; F = []; resets = {}
    for i in range(ST, n - 1):
        if used > 0 and dd252[i] > -0.30: resets[camp] = i; used = 0; last = None; camp += 1
        if used < 3 and cond[i] >= (42, 52, 62)[used] and (used == 0 or C[i] <= last * 0.85) and np.isfinite(O[i+1]):
            px = O[i+1] * 1.00075; F.append((camp, i+1, px, used + 1)); last = px; used += 1
    return F, resets, used
res = {}
for name, anc in [('1년 고점', a252), ('사이클 고점(사상최고)', aath)]:
    cond = bands(C / anc - 1) + df.A.values + df.S.values; disp = 100 - cond
    F, resets, used = sim(cond)
    camps = {}
    for cid, fi, px, tr in F: camps.setdefault(cid, []).append((fi, px, tr))
    rows = []; linked = set()
    for e, kind in TR.items():
        ie = pos[pd.Timestamp(e)]; low = C[ie]
        det_score = bool((disp[max(0, ie-5):ie+6] <= 58).any()); min_disp = int(disp[max(0, ie-5):ie+6].min())
        near = [(idx[fi].date().isoformat(), px/low-1) for cid, fi, px, tr in F if ie-126 <= fi <= ie+21]
        n30 = sum(1 for _, p in near if p <= 0.30); n10 = sum(1 for _, p in near if p <= 0.10)
        best = None
        for cid, fl in camps.items():
            i0 = fl[0][0]; alive = (cid not in resets) or (resets[cid] > ie)
            if ie-252 <= i0 <= ie+21 and alive and (best is None or i0 > camps[best][0][0]): best = cid
        avg = mae = None
        if best is not None:
            linked.add(best); fl = [x for x in camps[best] if x[0] <= ie+21]; w = 1/3
            avg = (w*len(fl)) / sum(w/p for _, p, _ in fl) / low - 1
            i0 = camps[best][0][0]; i1 = min(n-1, ie+126); vals = []
            for j in range(i0, i1+1):
                sh = sum(w/p for fi, p, _ in camps[best] if fi <= j); cash = 1 - w*sum(1 for fi, _, _ in camps[best] if fi <= j)
                if np.isfinite(L[j]): vals.append(cash + sh*L[j])
            mae = min(vals) - 1
        rows.append(dict(저점=e, 유형=kind, 저점점수최저=min_disp, 점수탐지=det_score, 근처체결=' / '.join(f"{d}({p:+.0%})" for d, p in near) or '없음',
                         근접30=n30, 근접10=n10, 평균단가=None if avg is None else f"{avg:+.0%}", 예산최악=None if mae is None else f"{mae:+.0%}"))
    R = pd.DataFrame(rows)
    unl = [(cid, idx[fl[0][0]].date().isoformat(), [(idx[fi].date().isoformat(), round(px, 2)) for fi, px, _ in fl]) for cid, fl in camps.items() if cid not in linked]
    res[name] = dict(R=R, F=F, unlinked=unl, cond=cond, disp=disp)
    avgs = [float(x.strip('%'))/100 for x in R.평균단가.dropna()]
    maes = [float(x.strip('%'))/100 for x in R.예산최악.dropna()]
    print(f'\n========== {name} ==========')
    pd.set_option('display.width', 300); pd.set_option('display.max_colwidth', 90)
    print(R.to_string(index=False))
    print(f"① 점수 탐지 {int(R.점수탐지.sum())}/7 | ② 근처(+30%) 매수 탐지 {int((R.근접30>0).sum())}/7 | ③ +10% 이내 체결 {int(R.근접10.sum())}건 | ④ 평균단가 중앙 {np.median(avgs):+.0%} | ⑤ 최악 예산 {min(maes):+.0%}")
    print('저점과 연결되지 않은 캠페인(조기·오신호·진행 중):', unl)
    for thr in (0.10, 0.20, 0.30, 0.50):
        cnt = 0
        for e in TR:
            ie = pos[pd.Timestamp(e)]
            cnt += any(ie-126 <= fi <= ie+21 and px/C[ie]-1 <= thr for _, fi, px, _ in F)
        print(f'   민감도: 저점 +{int(thr*100)}% 이내 매수 탐지 {cnt}/7')
    i18 = pos[pd.Timestamp('2026-09-18')]
    print(f"현재: 9/18 저점 점수 {disp[i18]:.0f}, 9/22 점수 {disp[-1]:.0f}, 최근 체결 {[(idx[fi].date().isoformat(), round(px,2), tr) for _, fi, px, tr in F if idx[fi] >= pd.Timestamp('2025-09-01')]}")
import pickle; pickle.dump({k: dict(F=v['F'], unlinked=v['unlinked']) for k, v in res.items()}, open('anchor_test.pkl', 'wb'))
