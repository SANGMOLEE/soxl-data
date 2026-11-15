# 역검증: 실제 BTC 저점가를 알았다면, 공식(k, 변동성손실, 비용)으로 SOLT를 얼마나 맞혔나
from load import *
def pred(solt0, b0, bT, days, k=1.4, sig_sol=0.65, c=0.08, alpha=-0.15):
    return solt0*np.exp(2*k*np.log(bT/b0) + 2*alpha*days/365 - (sig_sol**2 + c)*days/365)
lows=['2025-04-08','2025-11-21','2026-02-05','2026-06-30']
rows=[]
for L in lows:
    L=pd.Timestamp(L)
    if L not in solt.index:  # use next US session
        L=solt.index[solt.index>=L][0]
    for lb in [10,20,30,45,60]:
        cand=solt.index[solt.index<=L-pd.Timedelta(days=lb)]
        if len(cand)==0: continue
        st=cand[-1]
        days=(L-st).days
        # realized SOL vol over window for the 'oracle' variant
        for k in [1.0,1.4,1.8]:
            p=pred(solt_raw[st], btc[st], btc[L], days, k=k)
            rows.append(dict(low=L.date(),lookback=lb,k=k,btc_move=btc[L]/btc[st]-1,solt_start=solt_raw[st],solt_actual=solt_raw[L],solt_pred=p,err=np.log(p/solt_raw[L])))
o=pd.DataFrame(rows)
pd.set_option('display.width',200)
print(o[o.k==1.4].round(3).to_string())
print("\nlog error by k (mean, abs-mean, sd):")
print(o.groupby('k').err.agg(['mean',lambda x:x.abs().mean(),'std']).round(3))
# implied k at each low (what k would have fit exactly, given drag)
o2=o[o.k==1.4].copy()
o2['k_implied']=(np.log(o2.solt_actual/o2.solt_start)+ (0.65**2+0.08)*o2.lookback/365 +0.3*o2.lookback/365)/(2*np.log(1+o2.btc_move))
print(o2.groupby('low').k_implied.median().round(2))
