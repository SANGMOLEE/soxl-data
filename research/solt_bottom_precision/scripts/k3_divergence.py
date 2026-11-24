# K3. BTC가 신저가를 낼 때 SOL은 이전 저점 위에서 버티는 '상대강도 다이버전스' → 이후 SOL/SOLT가 또 빠졌나
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',250)
K=pd.read_csv('output/k2_refine.csv',parse_dates=['btc_low']); K0=pd.read_csv('output/k_btc_vs_solt.csv',parse_dates=['btc_low'])
b1=m1('BTC'); s1=m1('SOL')
rows=[]
for _,r in K0.iterrows():
    tb=r.btc_low
    bprev=b1.l[tb-pd.Timedelta(days=120):tb-pd.Timedelta(days=5)].min(); sprev=s1.l[tb-pd.Timedelta(days=120):tb-pd.Timedelta(days=5)].min()
    Sb=s1.l[tb]; Bb=b1.l[tb]
    btc_new=Bb<bprev; sol_vs_prev=Sb/sprev-1
    end=min(tb+pd.Timedelta(days=90),s1.index[-1])
    sol_ll=s1.l[tb+pd.Timedelta(hours=6):end].min()/Sb-1
    rows.append(dict(btc_low=tb,phase=r.phase,btc_new_low=btc_new,btc_vs_prev=Bb/bprev-1,sol_vs_prev=sol_vs_prev,
                     divergence=btc_new and sol_vs_prev>0.03,sol_later=sol_ll,solt_dd=r.solt_later_dd,horizon=r.horizon))
D=pd.DataFrame(rows)
x=D[D.btc_new_low]
print("== BTC가 120일 신저가를 낸 저점들: SOL은 자기 이전 저점 대비 어디였나 → 이후 90일")
print(x.assign(btc_low=x.btc_low.dt.strftime('%Y-%m-%d %H:%M'))[['btc_low','phase','btc_vs_prev','sol_vs_prev','divergence','sol_later','solt_dd','horizon']].round(3).to_string(index=False))
for flag,lab in [(True,'다이버전스 (BTC 신저가, SOL은 이전 저점보다 3%↑)'),(False,'동반 신저가 (SOL도 이전 저점 근처/아래)')]:
    g=x[(x.divergence==flag)&(x.horizon>=60)]
    print(f"\n[{lab}] n={len(g)}: 이후 90일 SOL 추가 신저가 비율 {(g.sol_later<-0.02).mean():.0%}, SOL 추가하락 중앙 {g.sol_later.median():+.1%}, SOLT 추가하락 중앙 {g.solt_dd.median():+.1%}")
D.to_csv('output/k3_divergence.csv',index=False)
