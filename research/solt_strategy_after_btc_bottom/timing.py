# (1) 수익이 BTC 바닥 기준 언제 났나: 거래를 진입 시점(D 기준) 구간별로 묶어 로그수익 합산
# (2) 차트용 변형: 달력일 MA(SOL 일봉) / SOLT 자체 MA
# (3) SOL 개별 저점 사례
from sigs import *
def trades(p, sig, lag, st, en, cost=COST):
    pos=sig.shift(lag).fillna(0)[st:en]; pp=p[st:en]; r=pp.pct_change().fillna(0); dt=pp.index.to_series().diff().dt.days.fillna(0)
    held=pos.shift(1).fillna(0); held.iloc[0]=0
    g=(1+2*r).clip(lower=0)*np.exp(-cost*dt/365)
    out=[]; cur=None
    for t in pp.index:
        if held[t]==1 and cur is None: cur=dict(entry=prev_t, lg=0.0)   # 진입 = 전일 종가 매수
        if held[t]==1: cur['lg']+=np.log(g[t])
        if held[t]==0 and cur is not None: cur['exit']=prev_t; out.append(cur); cur=None
        prev_t=t
    if cur is not None: cur['exit']=pp.index[-1]; out.append(cur)
    for o in out: o['lg']+=2*np.log(1-0.002)
    return out
BUCK=[(-90,0,'D-90~D'),(0,60,'D~D+60'),(60,180,'D+60~D+180'),(180,365,'D+180~D+365'),(365,541,'D+365~D+540')]
def attrib(n,b,c,label):
    rows=[]
    for D,assets in BOTTOMS.items():
        st=pd.Timestamp(D)-pd.Timedelta(days=90); en=pd.Timestamp(D)+pd.Timedelta(days=540)
        for a in assets:
            p=P(a)
            if p.index[0]>st-pd.Timedelta(days=150): continue
            sig=band_sig(p,n,b,c)
            for lag in [1,2,3]:
                for tr in trades(p,sig,lag,st,en):
                    off=(tr['entry']-pd.Timestamp(D)).days
                    bk=[nm for lo,hi,nm in BUCK if lo<=off<hi]
                    rows.append(dict(D=D,asset=a,lag=lag,bucket=bk[0] if bk else 'x',lg=tr['lg'],days=(tr['exit']-tr['entry']).days))
    t=pd.DataFrame(rows)
    per=t.groupby(['D','asset','lag','bucket']).lg.sum().unstack('bucket').fillna(0)
    per=per.groupby(['D','asset']).mean()                 # 지연 평균
    cyc=per.groupby('D').median()                         # 사이클별 알트 중앙
    cols=[nm for _,_,nm in BUCK]
    print(f"\n== {label}: 구간별 로그수익 기여 (사이클별 알트 중앙값, 지연1~3 평균) → 배수로 표시")
    print(np.exp(cyc[cols]).round(2).to_string()); print("4사이클 중앙:", np.exp(cyc[cols].median()).round(2).to_dict())
    w=t[t.lg>0]; big=t[t.lg>np.log(1.5)]
    print("1.5배 이상 거래의 진입 시점 분포:", (big.bucket.value_counts(normalize=True).reindex(cols).fillna(0)).round(2).to_dict(), " 보유일 중앙", big.days.median())
attrib(25,0.0,2,'MA25(거래일)·2일확인')
attrib(20,0.0,1,'MA20(거래일)')
# (2) 달력일 MA: SOL 일봉(7일) 기준 신호 → 다음 미국 거래일 체결
def cal_sig_to_sess(a,n,c):
    s=raw(a).dropna(); sig=band_sig(s,n,0.0,c)        # 달력일 신호
    p=sess(s); return p, sig.reindex(p.index,method='ffill')
print("\n== 차트용 변형 (지연1~3 평균, 4사이클 알트)")
for lab,fn in [('달력 MA28·2일',lambda a:cal_sig_to_sess(a,28,2)),('달력 MA35·2일',lambda a:cal_sig_to_sess(a,35,2)),('달력 MA42·2일',lambda a:cal_sig_to_sess(a,42,2)),
               ('2배NAV 자체 MA25·2일',None)]:
    res=[]
    for D,assets in BOTTOMS.items():
        st=pd.Timestamp(D)-pd.Timedelta(days=90); en=pd.Timestamp(D)+pd.Timedelta(days=540)
        for a in assets:
            if fn: p,sig=fn(a)
            else:
                p=P(a); nav=lev2(p[pd.Timestamp(D)-pd.Timedelta(days=400):],COST); sig=band_sig(nav,25,0.0,2).reindex(p.index).fillna(0).astype(int)
            if p.index[0]>st-pd.Timedelta(days=150): continue
            lm=np.mean([np.log(run(p,sig,cost=COST,lag=l,start=st,end=en)[0].iloc[-1]) for l in [1,2,3]])
            res.append(dict(D=D,asset=a,lm=lm))
    cy=pd.DataFrame(res).groupby('D').lm.median()
    print(f"{lab:18s} 사이클중앙 {np.exp(cy.median()):.2f}  최악 {np.exp(cy.min()):.2f}  사이클별 {np.exp(cy).round(2).to_dict()}")
# (3) SOL 개별 BTC 저점 사례: D-30 ~ D+180, MA25·2일 vs D 매수보유
print("\n== SOL 사례별 (D-30~D+180): MA25·2일 규칙 vs D매수보유 (합성 SOLT, 지연1~3 평균)")
p=P('sol'); sig=band_sig(p,25,0.0,2)
for D in ['2021-07-20','2022-06-18','2022-11-21','2024-09-06','2025-04-08','2026-02-05','2026-06-30']:
    st=pd.Timestamp(D)-pd.Timedelta(days=30); en=min(pd.Timestamp(D)+pd.Timedelta(days=180),p.index[-1])
    lm=np.exp(np.mean([np.log(run(p,sig,cost=COST,lag=l,start=st,end=en)[0].iloc[-1]) for l in [1,2,3]]))
    bh=run(p,pd.Series(1,p.index),cost=COST,lag=0,start=pd.Timestamp(D),end=en)[0].iloc[-1]
    print(f"{D}  규칙 {lm:5.2f}배   D매수보유 {bh:5.2f}배   (종료 {en.date()})")
