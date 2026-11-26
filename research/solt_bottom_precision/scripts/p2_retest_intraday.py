# P2. 시간봉: BTC 저점 뒤 '첫 거래가능 시점 매수' vs '저점 이론가/할인 지정가' — 주말 vs 평일, 지켜진 저점 vs 깨진 저점
import sys; sys.path.insert(0,'scripts')
from common import *
import k_btc_vs_solt as K0
pd.set_option('display.width',260)
H=K0.H; s1=m1('SOL'); K2=pd.read_csv('output/k2_refine.csv',parse_dates=['btc_low'])
rows=[]
for _,r in K2.iterrows():
    tb=r.btc_low; tx=K0.open_time(tb); Sb=s1.l[tb]
    Vb=K0.nav_at(tb,Sb); Vx=K0.nav_at(tx, Sb if tx==tb else s1.c.asof(tx))
    if Vb<=0 or tx>H.index[-1]: continue
    W=H[tx:tx+pd.Timedelta(days=30)]; Wo=W[W.open]
    def fill(level):
        hit=Wo[Wo.nav_l<=level]; return (hit.index[0],level) if len(hit) else (None,None)
    out=dict(event=tb,weekend=session_of(tb)=='weekend_closed',held=r.held90,exec_premium=Vx/Vb-1)
    fut=H[tx:tx+pd.Timedelta(days=365)]
    def up(t,e):
        f=H[t:t+pd.Timedelta(days=365)]; f=f[f.open]
        w=f[f.nav_c>=e*1.5]; return f.nav_c.max()/e, ((w.index[0]-t).days if len(w) else np.nan)
    out['A_up'],out['A_d15']=up(tx,Vx)
    for nm,lvl in [('B 저점 순간 이론가',Vb),('C 체결가능가 -10%',Vx*0.9),('D 체결가능가 -5%',Vx*0.95)]:
        t,e=fill(lvl)
        out[nm+'_fill']=t is not None; out[nm+'_days']=((t-tx).total_seconds()/86400) if t is not None else np.nan
        out[nm+'_gain_vs_A']=(Vx/e-1) if t is not None else np.nan
        if t is not None: out[nm+'_up'],out[nm+'_d15']=up(t,e)
    rows.append(out)
R=pd.DataFrame(rows); R.to_csv('output/p2_retest.csv',index=False)
def summ(x,lab):
    print(f"\n[{lab}] n={len(x)}  (체결가능 시점 가격의 저점 순간 이론가 대비 프리미엄 중앙 {x.exec_premium.median():+.1%})")
    print(f"  A 첫 거래가능 시점 매수: 1.5배 도달 {x.A_d15.notna().mean():.0%} (중앙 {x.A_d15.median():.0f}일), 1년 최대 {x.A_up.median():.2f}배")
    for nm in ['B 저점 순간 이론가','D 체결가능가 -5%','C 체결가능가 -10%']:
        f=x[nm+'_fill']
        print(f"  {nm} 지정가 (30일 유효): 체결 {f.mean():.0%}, 체결 중앙 {x[nm+'_days'].median():.1f}일, A보다 싸게 산 정도 {x[nm+'_gain_vs_A'].median():+.1%}; 체결분의 1.5배 도달 {x.loc[f,nm+'_d15'].notna().mean():.0%}, 1년 최대 {x.loc[f,nm+'_up'].median():.2f}배")
summ(R,'전체'); summ(R[R.weekend],'주말 저점'); summ(R[~R.weekend],'평일 저점')
summ(R[R.held==True],'지켜진 저점(진짜 바닥형)'); summ(R[(R.held==True)&(R.weekend)],'지켜진 + 주말 저점')
