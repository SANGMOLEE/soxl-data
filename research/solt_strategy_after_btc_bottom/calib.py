# 합성 SOLT 비용모형 보정: 실제 SOLT(2025-03-20~) 대비
from lib import *
p=sess(sol); a=solt.reindex(p.index).dropna(); p=p.reindex(a.index)
fa=funding_ann('SOLUSDT').rolling(30,min_periods=5).mean()
rf=0.042
models={'flat 5%':0.05,'flat 10%':0.10,'flat 15%':0.15,'flat 20%':0.20,
        'fee+2*funding-rf':(0.0185+2*fa.clip(lower=0)-rf).clip(lower=0.0185),
        'fee+1*funding':(0.0185+fa.clip(lower=0)).clip(lower=0.0185)}
an=a/a.iloc[0]
print("실제 SOLT 총수익 %.3f"%(an.iloc[-1]))
for k,c in models.items():
    m=lev2(p,c); e=np.log(an/m)
    yr=e.groupby(e.index.year).agg(lambda x: x.iloc[-1]-x.iloc[0])
    print(f"{k:20s} 합성 {m.iloc[-1]:.3f}  최종 로그오차 {e.iloc[-1]:+.3f}  RMSE {np.sqrt((e**2).mean()):.3f}  연도별 드리프트 {dict(yr.round(3))}")
print("SOL 펀딩 연율 30일평균, 분기별:"); print(fa.resample('QE').mean()['2020-12':].round(3).to_string())
# 일간 수익 대응: 주간 기준 기울기
w=pd.DataFrame({'a':a,'p':p}).resample('W-FRI').last().pct_change().dropna()
print("주간 SOLT/SOL 기울기 %.2f, 상관 %.3f"%(np.polyfit(w.p,w.a,1)[0], w.a.corr(w.p)))
