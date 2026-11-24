# K2. 원인 세분화 + "BTC 저점이 지켜졌을 때" 조건부
import sys; sys.path.insert(0,'scripts')
from common import *
import k_btc_vs_solt as K0
pd.set_option('display.width',260)
K=pd.read_csv('output/k_btc_vs_solt.csv',parse_dates=['btc_low']); b1=m1('BTC'); s1=m1('SOL'); H=K0.H; cl=K0.cl
rows=[]
for _,r in K.iterrows():
    tb=r.btc_low; end=min(tb+pd.Timedelta(days=90),H.index[-1])
    held=b1.l[tb+pd.Timedelta(minutes=1):end].min()>b1.l[tb] if end>tb+pd.Timedelta(days=3) else np.nan
    tx=K0.open_time(tb); Sb=s1.l[tb]; Vx=K0.nav_at(tx, Sb if tx==tb else s1.c.asof(tx))
    Wo=H[tb:end]; Wo=Wo[Wo.open]; tmin=Wo.nav_l.idxmin(); vmin=Wo.nav_l.min()
    j=cl.index.searchsorted(tmin,side='right')-1; day_drop=Wo.l[tmin]/cl.S.iloc[j]-1     # 그 재조정 구간 SOL 하락폭
    if vmin>=Vx*0.98: cause='더 낮아지지 않음'
    elif Wo.l[tmin]<Sb*0.995: cause='SOL 신저가'
    elif day_drop<=-0.30: cause='하루 급락 2배 증폭'
    else: cause='감가(SOL은 더 높음)'
    # 감가만의 크기: SOL이 처음으로 BTC저점 당시 SOL 가격(±2%)으로 돌아온 시점(10일 이후)의 SOLT / 매수가
    fut=H[tb+pd.Timedelta(days=10):end]; back=fut[(fut.c>=Sb*0.98)&(fut.c<=Sb*1.02)]
    same_price=(back.nav_c.iloc[0]/Vx-1) if len(back) else np.nan; same_days=((back.index[0]-tb).days if len(back) else np.nan)
    rows.append(dict(btc_low=tb,phase=r.phase,type=r.type,held90=held,cause=cause,solt_dd=vmin/Vx-1,same_price_solt=same_price,same_days=same_days,horizon=r.horizon))
R=pd.DataFrame(rows); R.to_csv('output/k2_refine.csv',index=False)
def summ(x,lab):
    print(f"\n[{lab}] n={len(x)}")
    print("  원인:",x.cause.value_counts(normalize=True).round(2).to_dict())
    print(f"  SOLT 추가하락(매수가 대비) 중앙 {x.solt_dd.median():+.1%}, 하위25% {x.solt_dd.quantile(.25):+.1%}")
    sp=x.same_price_solt.dropna()
    if len(sp): print(f"  SOL이 같은 가격(±2%)으로 돌아왔을 때 SOLT: 중앙 {sp.median():+.1%} (n={len(sp)}, 경과일 중앙 {x.same_days.median():.0f}일)")
x=R[R.horizon>=60]
summ(x,'전체 (90일 관찰 가능)'); summ(x[x.held90==True],'BTC 저점이 90일 지켜진 경우'); summ(x[x.held90==False],'BTC 저점이 90일 안에 깨진 경우')
summ(x[(x.held90==True)&(x.phase=='약세장')],'약세장 + BTC 저점 지켜짐')
print("\n약세장 + 지켜진 BTC 저점 목록:"); print(x[(x.held90==True)&(x.phase=='약세장')][['btc_low','type','cause','solt_dd','same_price_solt','same_days']].round(3).to_string(index=False))
print("\n지켜진 BTC 저점 전체 목록:"); print(x[x.held90==True][['btc_low','phase','type','cause','solt_dd','same_price_solt','same_days']].round(3).to_string(index=False))
