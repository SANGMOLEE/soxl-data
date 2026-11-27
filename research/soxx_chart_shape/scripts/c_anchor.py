# C. 비트코인의 '실현가격'에 해당하는 기준선: SOX 200주(≈1000거래일) 이동평균
#  약세장 주요 저점(52주 고점 대비 −25%↓, 앞 60일·뒤 30일 중 최저, 뒤 60일 안 +15%↑ 반등) 중
#  200주선 위 몇 배에서 찍은 저점이 사이클 바닥이었나
import sys; sys.path.insert(0,'scripts')
from common import *
CYC_BOTTOM=['1998-10-08','2002-10-09','2004-09-08','2006-07-21','2008-11-20','2011-10-04','2016-02-11','2018-12-24','2020-03-18','2022-10-13','2025-04-07']
cb=pd.to_datetime(CYC_BOTTOM)
R=d.ma200w.values; DD=d.dd.values
lows=[]
for i in range(260,N-30):
    if R[i]!=R[i]: continue
    if Lo[i]>Lo[i-60:i+31].min() or DD[i]>-0.25: continue
    if H[i:i+61].max()<Lo[i]*1.15: continue
    t=IDX[i]; cyc=bool((abs((cb-t).days)<=7).any())
    lows.append((t,Lo[i],Lo[i]/R[i],DD[i],cyc))
Lw=pd.DataFrame(lows,columns=['t','low','ratio','dd','cyc'])
out=["== 약세장 주요 저점과 200주선 비율 (★ = 사이클 바닥)"]
out.append("  "+", ".join(f"{r.t.date()}({r.ratio:.2f}{'★' if r.cyc else ''})" for r in Lw.itertuples()))
for lo_,hi_ in ((0,1.0),(1.0,1.15),(1.15,1.3),(1.3,9)):
    x=Lw[(Lw.ratio>=lo_)&(Lw.ratio<hi_)]
    out.append(f"  200주선 {lo_:.2f}~{hi_:.2f}배: 저점 {len(x)}건 중 사이클 바닥 {int(x.cyc.sum())}건")
x=Lw[Lw.t>='2010-01-01']
out.append(f"  2010년 이후만: 1.15배 이상 {int((x.ratio>=1.15).sum())}건 중 사이클 바닥 {int(x[x.ratio>=1.15].cyc.sum())}건 / 1.15배 미만 {int((x.ratio<1.15).sum())}건 중 {int(x[x.ratio<1.15].cyc.sum())}건")
out.append(f"  사이클 바닥 비율: "+", ".join(f"{t.date()} {Lo[IDX.get_loc(t)]/R[IDX.get_loc(t)]:.2f}" for t in cb if R[IDX.get_loc(t)]==R[IDX.get_loc(t)]))
# 이번: 11/20, 11/25
for t in ('2026-11-20','2026-11-25'):
    k=IDX.get_loc(pd.Timestamp(t)); out.append(f"  이번 {t}: 장중 저가 {Lo[k]:.0f} / 200주선 {R[k]:.0f} = {Lo[k]/R[k]:.2f}배")
# 200주선 앞으로: SOX가 지금 가격에 머문다고 가정, 1000일 전 값이 빠지는 속도
cc=d.close.values
def ma_future(days,price):
    hist=list(cc[-1000:]); 
    for _ in range(days): hist=hist[1:]+[price]
    return np.mean(hist)
out.append("\n== 200주선이 앞으로 어디쯤일까 (SOX가 그 사이 평균적으로 머무는 가격 가정)")
for days,lab in ((40,'2027-01 하순'),(60,'2027-02 하순'),(85,'2027-03 하순'),(105,'2027-04 하순'),(150,'2027-06 하순')):
    a=[ma_future(days,p) for p in (7500,8500,9500)]
    out.append(f"  {lab} ({days}거래일 뒤): 200주선 {a[0]:.0f}/{a[1]:.0f}/{a[2]:.0f} (SOX 7,500/8,500/9,500 가정) → 1.12배 {a[1]*1.12:.0f}, 1.00배 {a[1]:.0f} (8,500 가정)")
open(f'{OUT}/c_anchor.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
