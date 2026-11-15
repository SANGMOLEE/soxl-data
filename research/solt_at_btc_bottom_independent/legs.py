# SOL vs BTC: 약세장 베타, BTC 하락 구간(zigzag 25%)·저점 직전 마지막 -Y% 구간의 로그이동 배수 k
from load import *
pd.set_option('display.width',220)
b=btc['2020-04-10':]; s_=sol
piv=[('L','2020-04-15'),('H','2021-01-08'),('L','2021-01-27'),('H','2021-04-13'),('L','2021-07-20'),('H','2021-11-08'),('L','2022-01-22'),('H','2022-03-29'),('L','2022-06-18'),('H','2022-08-13'),('L','2022-11-21'),('H','2024-03-13'),('L','2024-09-06'),('H','2025-01-21'),('L','2025-04-08'),('H','2025-10-06'),('L','2026-02-05'),('H','2026-05-10'),('L','2026-06-30'),('H','2026-09-21')]
piv=[(k,pd.Timestamp(t)) for k,t in piv]
r=pd.DataFrame({'b':btc,'s':sol}).dropna(); w=np.log(r.resample('W-SUN').last()).diff().dropna()
print("== 주간 로그수익 회귀 (SOL on BTC)")
for lab,sl in [('2023~',slice('2023',None)),('2025-01~',slice('2025-01',None)),('BTC고점 2025-10-06~',slice('2025-10-06',None)),('2026~',slice('2026',None))]:
    x=w[sl]; be,a=np.polyfit(x.b,x.s,1); res=x.s-(a+be*x.b); dn=x[x.b<0]
    print(f"{lab:20s} beta {be:.2f} (하락주 {np.polyfit(dn.b,dn.s,1)[0]:.2f}) alpha/yr {a*52:+.2f} 잔차변동성/yr {res.std()*np.sqrt(52):.2f} corr {x.b.corr(x.s):.2f}")
print("\n== BTC 하락 구간별 k = ln(SOL)/ln(BTC)")
rows=[]
for i in range(1,len(piv)):
    k,t=piv[i]; kp,tp=piv[i-1]
    if k=='L': rows.append(dict(고점=tp.date(),저점=t.date(),일수=(t-tp).days,BTC=b[t]/b[tp]-1,SOL=s_[t]/s_[tp]-1,k=np.log(s_[t]/s_[tp])/np.log(b[t]/b[tp])))
tp=pd.Timestamp('2026-09-21'); t=b.index[-1]
rows.append(dict(고점=tp.date(),저점=str(t.date())+'(진행중)',일수=(t-tp).days,BTC=b[t]/b[tp]-1,SOL=s_[t]/s_[tp]-1,k=np.log(s_[t]/s_[tp])/np.log(b[t]/b[tp])))
print(pd.DataFrame(rows).round(3).to_string(index=False))
print("\n== 저점 직전 마지막 -Y% 구간의 k")
rows=[]
for t in [t for k,t in piv if k=='L'][1:]:
    ph=[tt for k,tt in piv if k=='H' and tt<t][-1]; L=b[t]
    for Y in [0.10,0.15,0.20,0.25]:
        seg=b[ph:t]; above=seg[seg>=L/(1-Y)]
        if above.empty: continue
        st=above.index[-1]; win=s_[t-pd.Timedelta(days=10):t+pd.Timedelta(days=10)]
        rows.append(dict(btc_low=t.date(),Y=Y,days=(t-st).days,k=np.log(s_[t]/s_[st])/np.log(L/b[st]),sol_low_near=win.idxmin().date(),sol_low_vs_btc_low=win.min()/s_[t]-1))
o=pd.DataFrame(rows); print(o.round(3).to_string(index=False))
print("\n전체:\n",o.groupby('Y').k.agg(['median','mean','min','max','count']).round(2))
print("2024년 이후:\n",o[o.btc_low>=pd.Timestamp('2024-01-01').date()].groupby('Y').k.agg(['median','mean','min','max','count']).round(2))
