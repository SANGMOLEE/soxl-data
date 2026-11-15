# F. SOL '본격 상승기'만 따로: 보유 수익, 무작위 진입 승률, 규칙의 포착률
from sigs import *
pd.set_option('display.width',230)
p=P('sol')                                   # 미국 거래일 표본 SOL
nav=lev2(p,COST)                              # 가상 SOLT (비용 연20%)
# 상승기 정의(사후): SOL 종가 zigzag 40% — 저점→고점 구간 중 SOL +100% 이상
def zz(x,th):
    piv=[]; mode=None; hi=lo=x.iloc[0]; hi_i=lo_i=x.index[0]
    for t,v in x.items():
        if v>hi: hi,hi_i=v,t
        if v<lo: lo,lo_i=v,t
        if mode!='down' and v<=hi*(1-th): piv.append(('H',hi_i)); mode='down'; lo,lo_i=v,t
        elif mode!='up' and v>=lo*(1+th): piv.append(('L',lo_i)); mode='up'; hi,hi_i=v,t
    return piv
piv=zz(p['2020-06':],0.40)
legs=[(piv[i][1],piv[i+1][1]) for i in range(len(piv)-1) if piv[i][0]=='L' and piv[i+1][0]=='H']
legs=[(a,b) for a,b in legs if p[b]/p[a]>=2.0]
sigA=band_sig(p,25,0.0,2)
def rule_in(sig,a,b,lag=1):
    eq,_,tr,_=run(p,sig,cost=COST,lag=lag,start=a,end=b); return eq.iloc[-1],tr
rows=[]
for a,b in legs:
    hold=nav[b]/nav[a]; act=(solt[b]/solt[a]) if (a>=solt.index[0]) else np.nan
    r1,tr=rule_in(sigA,a,b,1); r2,_=rule_in(sigA,a,b,2)
    rows.append(dict(상승기=f"{a.date()}→{b.date()}",거래일=len(p[a:b]),SOL=p[b]/p[a],SOLT형_보유=hold,실제SOLT=act,
                     규칙_지연1=r1,규칙_지연2=r2,포착률=np.log(r1)/np.log(hold),거래=tr))
L=pd.DataFrame(rows)
print("== SOL 상승기(사후 정의: 저점→고점, SOL +100% 이상) — 저점 매수·고점 매도 vs MA25 규칙")
print(L.round(2).to_string(index=False))
# 가상 SOLT 정확도: 2025 상승기 실제와 비교
a,b=pd.Timestamp('2025-04-08'),pd.Timestamp('2025-09-18')
print(f"\n2025-04-08→09-18: 실제 SOLT {solt[b]/solt[a]:.2f}배, 가상SOLT(비용20%) {nav[b]/nav[a]:.2f}배, 비용0% {lev2(p,0.0)[b]/lev2(p,0.0)[a]:.2f}배, SOL {p[b]/p[a]:.2f}배")
# 상승기 안에서 아무 날이나 사서 N거래일 보유 (상승기 끝을 넘어가도 그대로 보유 = 현실)
print("\n== 상승기 안 무작위 매수 후 N거래일 보유: 가상 SOLT 수익 분포")
res=[]
for a,b in legs:
    days=p[a:b].index
    for d in days:
        i=nav.index.get_loc(d)
        for N in [20,60,120]:
            if i+N<len(nav): res.append(dict(leg=f"{a.date()}",N=N,r=nav.iloc[i+N]/nav.iloc[i]-1))
R=pd.DataFrame(res)
g=R.groupby('N').r.agg(승률=lambda x:(x>0).mean(),중앙=lambda x:x.median(),평균=lambda x:x.mean(),하위25=lambda x:x.quantile(.25),상위25=lambda x:x.quantile(.75),최악=lambda x:x.min())
print(g.round(2).to_string())
print("\n상승기별 60거래일 보유 승률/중앙:")
print(R[R.N==60].groupby('leg').r.agg(승률=lambda x:(x>0).mean(),중앙='median').round(2).to_string())
# 규칙의 상승기 내 거래 승률
tr=[]
pos=sigA.shift(1).fillna(0); held=pos.shift(1).fillna(0); r=p.pct_change().fillna(0); dt=p.index.to_series().diff().dt.days.fillna(0)
lg=np.log((1+2*r).clip(lower=1e-9)*np.exp(-COST*dt/365)); grp=(held.diff().fillna(0)==1).cumsum()
inleg=pd.Series(False,p.index)
for a,b in legs: inleg[a:b]=True
for k,x in lg[held==1].groupby(grp[held==1]):
    tr.append(dict(start=x.index[0],m=np.exp(x.sum()+2*np.log(0.998)),days=len(x),bull=inleg[x.index[0]]))
T=pd.DataFrame(tr)
for flag,lab in [(True,'상승기 안 진입'),(False,'상승기 밖 진입')]:
    x=T[T.bull==flag]; print(f"\n규칙 거래 — {lab}: {len(x)}회, 승률 {(x.m>1).mean():.0%}, 거래당 중앙 {x.m.median()-1:+.1%}, 평균 {x.m.mean()-1:+.1%}, 누적 {x.m.prod():.2f}배")
L.to_csv('output/bull_legs.csv',index=False); R.to_csv('output/bull_random_entry.csv',index=False)
