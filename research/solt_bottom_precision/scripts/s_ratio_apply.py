# S. 역대 사이클 바닥의 실현가격 대비 비율(MVRV) → 현재 실현가격에 적용 (BTC), ETH·SOL·SOLT 연동
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',250)
E='data/ext/'
old=pd.read_csv(E+'BTC_ONCHAIN.csv',parse_dates=['date']).set_index('date')            # 2011~ (CoinMetrics)
cmb=pd.read_csv(E+'CM_BTC_REALIZED.csv',parse_dates=['date']).set_index('date')        # 2013~ 최신
rp=pd.concat([old.realized_price[old.index<cmb.index[0]],cmb.realized_price]).sort_index()
px=pd.concat([old.price[old.index<cmb.index[0]],cmb.price]).sort_index()
cme=pd.read_csv(E+'CM_ETH_REALIZED.csv',parse_dates=['date']).set_index('date')
b1=m1('BTC')
BOT=[('2011','2011-11-18',2.01,'마운트곡스 장중 약 $2.01'),('2015','2015-01-14',152.40,'비트스탬프'),('2018','2018-12-15',None,''),('2020','2020-03-13',None,''),('2022','2022-11-21',None,'')]
rows=[]
for cy,d,lo,note in BOT:
    d=pd.Timestamp(d)
    if lo is None: lo=b1.l[d.tz_localize('UTC'):d.tz_localize('UTC')+pd.Timedelta(days=1)].min()
    r=rp.asof(d); cmin=px[d-pd.Timedelta(days=45):d+pd.Timedelta(days=45)]; tclose=cmin.idxmin()
    rows.append(dict(사이클=cy,바닥일=d.date(),장중저점=lo,그날실현가격=r,장중기준비율=lo/r,종가최저일=tclose.date(),종가기준비율=cmin.min()/rp.asof(tclose)))
T=pd.DataFrame(rows); print("== 역대 BTC 사이클 바닥: 실현가격 대비 비율 (MVRV)"); print(T.round(3).to_string(index=False))
# 추세 외삽: 장중 기준 비율의 사이클별 증가
x=T[T.사이클!='2020']; fit=np.polyfit(range(len(x)),x.장중기준비율,1); nxt=np.polyval(fit,len(x))
fit2=np.polyfit(range(len(x)),x.종가기준비율,1); nxt2=np.polyval(fit2,len(x))
print(f"\n사이클별 추세(2020 제외) 외삽: 장중 기준 {nxt:.2f}, 종가 기준 {nxt2:.2f}")
# 현재 실현가격과 최근 변화 속도
r_now=rp.iloc[-1]; chg90=rp.iloc[-1]/rp.asof(rp.index[-1]-pd.Timedelta(days=90))-1; chg30=rp.iloc[-1]/rp.asof(rp.index[-1]-pd.Timedelta(days=30))-1
m_rate=(1+chg90)**(1/3)-1
print(f"현재 BTC 실현가격 ${r_now:,.0f} ({rp.index[-1].date()}), 최근 30일 {chg30:+.1%}, 90일 {chg90:+.1%} → 월 {m_rate:+.1%}")
now={a:m1(a).c.iloc[-1] for a in ['BTC','ETH','SOL']}
P0,S0=24.82,70.62; fair_now=P0*(1+2*(now['SOL']/S0-1))
sv=np.log(m1('SOL').c.resample('D').last()).diff().dropna()[-60:].std()*np.sqrt(365)
def solt(S,T=21,c=0.10): return fair_now*(S/now['SOL'])**2*np.exp(-(sv**2+c)*T/365)
print(f"현재 BTC ${now['BTC']:,.0f}, ETH ${now['ETH']:,.0f}, SOL ${now['SOL']:.2f}, SOLT 이론가 ${fair_now:.2f}")
cases=[(f"{r.사이클} 장중 ({r.장중기준비율:.2f})",r.장중기준비율) for r in T.itertuples()]+[(f"{r.사이클} 종가 ({r.종가기준비율:.2f})",r.종가기준비율) for r in T.itertuples()]+[(f"추세 외삽 장중 ({nxt:.2f})",nxt),(f"추세 외삽 종가 ({nxt2:.2f})",nxt2)]
out=[]
for nm,ratio in cases:
    for lab,rr in [('지금 실현가격',r_now),('2개월 뒤 실현가격',r_now*(1+m_rate)**2)]:
        B=rr*ratio; L=np.log(B/now['BTC'])
        eth=now['ETH']*np.exp(1.25*L); sol=[now['SOL']*np.exp(k*L) for k in (1.0,1.45,1.8)]
        out.append(dict(기준=nm,실현가격=lab,BTC=round(B),BTC하락=f"{B/now['BTC']-1:+.0%}",ETH=round(eth),SOL=f"{sol[1]:.1f} ({sol[2]:.1f}~{sol[0]:.1f})",
                        SOLT_3주=f"{solt(sol[1]):.1f} ({solt(sol[2]):.1f}~{solt(sol[0]):.1f})",SOLT_2개월=f"{solt(sol[1],60):.1f}"))
O=pd.DataFrame(out); O.to_csv('output/s_ratio_apply.csv',index=False)
print("\n== 비율을 현재 사이클에 적용"); print(O[O.실현가격=='지금 실현가격'].drop(columns='실현가격').to_string(index=False))
print("\n(2개월 뒤 실현가격 기준)"); print(O[O.실현가격=='2개월 뒤 실현가격'].drop(columns='실현가격')[['기준','BTC','BTC하락','SOL','SOLT_3주']].to_string(index=False))
# ETH 자체 비율
print("\n== ETH 자체: 역대 ETH 바닥 비율 × 현재 ETH 실현가격 ${:,.0f}".format(cme.realized_price.iloc[-1]))
for d,lo in [('2018-12-15',81.79),('2020-03-13',86.00),('2022-06-18',881.56)]:
    r=lo/cme.realized_price.asof(pd.Timestamp(d)); print(f"  {d}: 비율 {r:.2f} → ETH ${cme.realized_price.iloc[-1]*r:,.0f} (현재 대비 {cme.realized_price.iloc[-1]*r/now['ETH']-1:+.0%})")
# 현재 사이클 지금까지의 비율
for d,lo in [('2026-06-30',None),('2026-11-21',55130.0)]:
    d=pd.Timestamp(d); lo=lo or b1.l[d.tz_localize('UTC'):d.tz_localize('UTC')+pd.Timedelta(days=1)].min()
    print(f"현재 사이클 {d.date()} 장중 저점 ${lo:,.0f} → 그날 실현가격 대비 {lo/rp.asof(d):.2f}")
