from base import *
# 실제 SOXL 시가가 있는 2010-06 이후만 (합성 구간 시가는 지수 시가라 불신)
R=real.values
vol20=(np.log(CL).diff().rolling(20).std()*np.sqrt(252)).values
B=bear.values
gap=oL.values*100; oc=(c/o-1)*100      # 시가 갭(전일 종가 대비), 시가→종가
print("=== A3. 지금 국면에서 갭 상승 시가 신규 롱 금지 (원래: 10/20 이후 갭+3%↑ 10건 승률 40% 중앙 -1.9% 상위3뺀 -6.2% 최악 -16.0%; 2011~2026.10 하락장·고변동 156건 52% +0.6%)")
def pick(m): return [i for i in range(1,N) if m[i] and R[i]]
d=pd.Series(cal,index=cal)
recent=(d>=pd.Timestamp("2026-10-20")).values
for g in (2,3,5,8):
    idx=pick(recent&(gap>=g)); print(st([oc[i] for i in idx],f"10/20 이후 갭 +{g}%↑ 시가→종가"))
idx=pick(recent&(gap>=3)); print("   목록:",[(str(cal[i].date()),round(gap[i],1),round(oc[i],1)) for i in idx])
for start in ("2026-10-01","2026-11-01"):
    m=(d>=pd.Timestamp(start)).values; idx=pick(m&(gap>=3)); print(st([oc[i] for i in idx],f"{start} 이후 갭 +3%↑"))
print("-- 비교 국면 (갭 +3%↑, 시가→종가)")
hv=B&(vol20>=1.0)
for nm,m in (("하락장 & 20일 변동성 100%↑ (2011~2026.10)",hv&(d<pd.Timestamp("2026-10-20")).values&(d>=pd.Timestamp("2011-01-01")).values),
             ("하락장 & 변동성 100%↑ & VIX≥30",hv&(vx.values>=30)&(d<pd.Timestamp("2026-10-20")).values),
             ("상승장 전체",(~B)&(d>=pd.Timestamp("2010-06-01")).values),("전체 2010~",(d>=pd.Timestamp("2010-06-01")).values)):
    idx=pick(m&(gap>=3)); print(st([oc[i] for i in idx],nm,48))
print("-- 같은 자리 대조: 갭 상승일에 시가 매수 대신 종가 매수 → 다음 날 종가 (하락장&변동성100%↑)")
idx=pick(hv&(gap>=3)); print(st([(c[i+1]/c[i]-1)*100 for i in idx if i+1<N],"갭+3%↑ 날 종가 매수 1일",48))
print(st([(c[i+1]/o[i]-1)*100 for i in idx if i+1<N],"갭+3%↑ 날 시가 매수 → 다음 날 종가",48))
# 갭다운 대조
idx=pick(hv&(gap<=-3)); print(st([oc[i] for i in idx],"참고: 갭 -3%↓ 시가→종가",48))
