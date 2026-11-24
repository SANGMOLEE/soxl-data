# L. 계획 대안 비교: BTC 저점에서 SOLT 원안 vs 분할/현물 혼합/전환
import sys; sys.path.insert(0,'scripts')
from common import *
import k_btc_vs_solt as K0
pd.set_option('display.width',260)
cl=K0.cl; s1=m1('SOL'); nav_at=K0.nav_at; open_time=K0.open_time
K2=pd.read_csv('output/k2_refine.csv',parse_dates=['btc_low'])
ma=cl.S.rolling(25).mean(); above=(cl.S>ma).astype(int); run2=above.groupby((above!=above.shift()).cumsum()).cumsum()
def confirm_after(t, maxd=90):
    x=run2[(run2.index>t)&(run2.index<=t+pd.Timedelta(days=maxd))]; x=x[x>=2]
    return x.index[0] if len(x) else None
def value_path(legs, t0, H=365):
    """legs: [(weight, kind('solt'|'sol'), t_buy, t_switch or None)]  → 일별(미국 종가) 포트폴리오 가치"""
    idx=cl.index[(cl.index>t0)&(cl.index<=t0+pd.Timedelta(days=H))]
    vals=[]
    for T in idx:
        v=0
        for w,kind,tb,tsw in legs:
            if tb is None or T<tb: v+=w; continue                    # 미투입 = 현금
            Sb=s1.c.asof(tb)
            if kind=='solt': v+=w*cl.nav[T]/nav_at(tb,Sb)
            elif kind=='sol': v+=w*cl.S[T]/Sb
            elif kind=='sol2solt':                                  # 현물로 보유하다 전환
                if tsw is None or T<tsw: v+=w*cl.S[T]/Sb
                else: v+=w*(s1.c.asof(tsw)/Sb)*cl.nav[T]/nav_at(tsw,s1.c.asof(tsw))
        vals.append(v)
    return pd.Series(vals,index=idx)
rows=[]
for _,r in K2.iterrows():
    tb=r.btc_low; tx=open_time(tb)
    if tb<pd.Timestamp('2020-10-01',tz='UTC') or tx>cl.index[-1]-pd.Timedelta(days=60): continue
    tc=confirm_after(tx)
    P={'P0 원안: SOLT 100% (BTC저점)':[(1,'solt',tx,None)],
       'P1 SOLT 50% + 추세확인 시 SOLT 50%':[(.5,'solt',tx,None),(.5,'solt',tc,None)],
       'P2 SOL현물 → 추세확인 시 SOLT 전환':[(1,'sol2solt',tx,tc)],
       'P3 SOLT 3분할 (0·14·28일)':[(1/3,'solt',tx,None),(1/3,'solt',open_time(tx+pd.Timedelta(days=14)),None),(1/3,'solt',open_time(tx+pd.Timedelta(days=28)),None)],
       'P4 SOLT 50% + SOL현물 50%':[(.5,'solt',tx,None),(.5,'sol',tx,None)],
       '참고: SOL현물 100%':[(1,'sol',tx,None)]}
    for nm,legs in P.items():
        vp=value_path(legs,tx)
        if len(vp)<40: continue
        hit=lambda k: (vp>=k).any()
        def first(k):
            w=vp[vp>=k]; return (w.index[0]-tx).days if len(w) else np.nan
        mae=vp.cummin().min()-1
        rows.append(dict(event=tb,held=r.held90,phase=r.phase,plan=nm,v90=vp.iloc[min(len(vp)-1,62)],v365=vp.iloc[-1],full=len(vp)>=240,
                         hit15=hit(1.5),hit2=hit(2.0),d15=first(1.5),d2=first(2.0),mae=mae,
                         mae_before15=(vp[:vp[vp>=1.5].index[0]].min()-1) if hit(1.5) else mae))
R=pd.DataFrame(rows); R.to_csv('output/l_plans.csv',index=False)
gm=lambda v: float(np.exp(np.log(np.clip(v,1e-4,None)).mean()))
def tab(x,title):
    t=x.groupby('plan').apply(lambda g: pd.Series({'n':len(g),'1.5배 도달':g.hit15.mean(),'2배 도달':g.hit2.mean(),'1.5배까지 일(중앙)':g.d15.median(),
        '1.5배 전 최대손실(중앙)':g.mae_before15.median(),'최대손실 하위25%':g.mae.quantile(.25),'90일 가치(기하)':gm(g.v90),'1년 가치(기하)':gm(g.v365)}))
    print(f"\n== {title}"); print(t.round(2).to_string())
tab(R[R.held==True],'BTC 저점이 지켜진 경우 (진짜 바닥에 가까움)')
tab(R[R.held==False],'BTC 저점이 깨진 경우 (가짜 바닥)')
tab(R[R.phase=='약세장'],'약세장 저점 전체')
tab(R,'전체')
