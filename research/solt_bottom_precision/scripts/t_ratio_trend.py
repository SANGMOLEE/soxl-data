# T. 사이클 바닥 MVRV 비율이 어떤 추세로 높아졌는지: 여러 추세 모형 비교 + 고점 MVRV 비교
import sys; sys.path.insert(0,'scripts')
from common import *
E='data/ext/'
old=pd.read_csv(E+'BTC_ONCHAIN.csv',parse_dates=['date']).set_index('date')
cmb=pd.read_csv(E+'CM_BTC_REALIZED.csv',parse_dates=['date']).set_index('date')
rp=pd.concat([old.realized_price[old.index<cmb.index[0]],cmb.realized_price]).sort_index()
px=pd.concat([old.price[old.index<cmb.index[0]],cmb.price]).sort_index()
mv=(px/rp).dropna()
# 바닥 비율 (s_ratio_apply.py 결과, 장중 기준)
B=pd.DataFrame({'cy':['2011','2015','2018','2022'],'date':pd.to_datetime(['2011-11-18','2015-01-14','2018-12-15','2022-11-21']),
                'ratio':[0.404,0.489,0.684,0.763]})
B['할인율']=1-B.ratio
B['직전대비증가']=B.ratio.diff()
B['할인율축소배수']=B.할인율/B.할인율.shift()
print("== 바닥 비율과 사이클 간 변화 (장중 기준)"); print(B.assign(date=B.date.dt.date).round(3).to_string(index=False))
nxt_date=pd.Timestamp('2026-11-21')
yr=lambda d:d.dt.year+d.dt.dayofyear/365 if hasattr(d,'dt') else d.year+d.dayofyear/365
X=yr(B.date).values; y=B.ratio.values; xn=yr(nxt_date)
res=[]
f=np.polyfit(range(4),y,1); res.append(('① 사이클 순번 직선 (보고서 사용)',np.polyval(f,4),f"사이클당 +{f[0]:.3f}"))
f=np.polyfit(X,y,1); res.append(('② 연도 직선',np.polyval(f,xn),f"연 +{f[0]:.4f} (4년 +{4*f[0]:.3f})"))
f=np.polyfit(range(4),np.log(1-y),1); res.append(('③ 할인율이 일정 배수로 축소 (사이클 순번)',1-np.exp(np.polyval(f,4)),f"사이클당 할인율 ×{np.exp(f[0]):.2f}"))
f=np.polyfit(X,np.log(1-y),1); res.append(('④ 할인율이 일정 배수로 축소 (연도)',1-np.exp(np.polyval(f,xn)),f"연 ×{np.exp(f[0]):.3f}"))
res.append(('⑤ 직전 증가폭(2018→2022 +0.079) 반복',y[-1]+(y[-1]-y[-2]),"사이클당 +0.079"))
res.append(('⑥ 평균 증가폭(3번 평균 +0.120) 반복',y[-1]+(y[-1]-y[0])/3,"사이클당 +0.120"))
res.append(('⑦ 직전 할인율 축소 배수(×0.75) 반복',1-(1-y[-1])*((1-y[-1])/(1-y[-2])),"할인율 ×0.75"))
# 2020 포함 판
B2=pd.concat([B,pd.DataFrame({'cy':['2020'],'date':[pd.Timestamp('2020-03-13')],'ratio':[0.674]})]).sort_values('date')
f=np.polyfit(yr(B2.date).values,B2.ratio.values,1); res.append(('⑧ 연도 직선, 2020 포함',np.polyval(f,xn),f"연 +{f[0]:.4f}"))
R=pd.DataFrame(res,columns=['모형','다음 바닥 비율','증가 속도'])
r_now=53099
R['BTC']=(R['다음 바닥 비율']*r_now).round(0)
print("\n== 추세 모형별 다음(2026 사이클) 바닥 비율과 BTC"); print(R.round(3).to_string(index=False))
# 고점 MVRV: 사이클 고점 근처 최대
tops=[('2011','2011-03-01','2011-08-31'),('2013','2013-10-01','2014-01-31'),('2017','2017-11-01','2018-01-31'),('2021','2021-02-01','2021-12-31'),('2024-25','2024-01-01','2025-12-31')]
print("\n== 사이클 고점의 MVRV 최대값 (일봉)")
for n,a,b in tops:
    s=mv[a:b]; print(f"  {n}: {s.max():.2f} ({s.idxmax().date()})")
# 고점 대비 낙폭
print("\n== 사이클 고점 → 바닥 낙폭 (일봉 종가 기준 대략)")
for n,(a,b),(c,d) in [('2011',('2011-01-01','2011-08-31'),('2011-09-01','2011-12-31')),('2015',('2013-10-01','2014-01-31'),('2014-02-01','2015-06-30')),('2018',('2017-11-01','2018-01-31'),('2018-02-01','2019-03-31')),('2022',('2021-02-01','2021-12-31'),('2022-01-01','2023-03-31'))]:
    print(f"  {n}: {px[c:d].min()/px[a:b].max()-1:.0%}")
# 모형별 ETH·SOL·SOLT (s_ratio_apply.py와 같은 연동 가정)
now={a:m1(a).c.iloc[-1] for a in ['BTC','ETH','SOL']}
P0,S0=24.82,70.62; fair_now=P0*(1+2*(now['SOL']/S0-1))
sv=np.log(m1('SOL').c.resample('D').last()).diff().dropna()[-60:].std()*np.sqrt(365)
def solt(S,T=21,c=0.10): return fair_now*(S/now['SOL'])**2*np.exp(-(sv**2+c)*T/365)
print(f"\n== 모형별 연동 가격 (현재 BTC ${now['BTC']:,.0f}, SOL ${now['SOL']:.2f}, SOLT 이론가 ${fair_now:.2f})")
for r in R.itertuples():
    L=np.log(r.BTC/now['BTC']); sol=now['SOL']*np.exp(1.45*L)
    print(f"  {r.모형}: 비율 {r._2:.2f} → BTC ${r.BTC:,.0f} ({r.BTC/now['BTC']-1:+.0%}), ETH ${now['ETH']*np.exp(1.25*L):,.0f}, SOL ${sol:.1f}, SOLT ${solt(sol):.1f}")
# 직선 모형을 계속 이으면 언제 1.0을 넘나
print("\n== 직선 모형 ①을 계속 이으면: 다음다음 바닥", f"{np.polyval(np.polyfit(range(4),y,1),5):.2f}", "→ 실현가격 위에서 바닥 (구조적으로 무리)")
print("== 할인율 축소 모형 ③을 이으면: 다음다음 바닥", f"{1-np.exp(np.polyval(np.polyfit(range(4),np.log(1-y),1),5)):.2f}", "→ 1.0에 가까워지되 넘지 않음")
