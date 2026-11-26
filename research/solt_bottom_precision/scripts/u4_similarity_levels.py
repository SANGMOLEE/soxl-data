# U4. 2026 바닥 전 90일 경로와 역대 사이클의 모양 유사도 + 2026 시나리오별 BTC·SOL·SOLT 가격
import sys; sys.path.insert(0,'scripts')
from u_chart_shape import *
D=pd.Timedelta
T=pd.read_csv('output/u_chart_shape.csv').set_index('사례')
def path(n):
    sym={c[0]:c[1] for c in CASES}[n]; t0=pd.Timestamp({c[0]:c[2] for c in CASES}[n]); df=daily(sym)
    s=np.log(df.c[t0-D(days=90):t0]/T.loc[n,'최종바닥']); s.index=(s.index-t0).days; return s.reindex(range(-90,1)).interpolate()
now=path('BTC 2026 (진행)')
out=["== 바닥 전 90일 모양 유사도 (log(종가/최종바닥), 2026 대비)"]
for n in ['BTC 2015','BTC 2018','BTC 2020 (급락)','BTC 2022','ETH 2018','ETH 2022','SOL 2022']:
    p=path(n); m=p.notna()&now.notna()
    out.append(f"  {n}: 상관 {np.corrcoef(p[m],now[m])[0,1]:.2f}, 평균 차이(RMSE) {np.sqrt(((p[m]-now[m])**2).mean())*100:.0f}%p")
# 시나리오 가격
b_now=m1('BTC').c.iloc[-1]; s_now=m1('SOL').c.iloc[-1]
P0,S0=24.82,70.62; fair=P0*(1+2*(s_now/S0-1))
sv=np.log(m1('SOL').c.resample('D').last()).diff().dropna()[-60:].std()*np.sqrt(365)
def sol(b,k=1.45): return s_now*np.exp(k*np.log(b/b_now))
def solt_inst(S): return P0*(1+2*(S/S0-1))                      # 11/25 종가 기준 하루 안 이동
def solt_path(S,T=21,c=0.10): return fair*(S/s_now)**2*np.exp(-(sv**2+c)*T/365)
out.append(f"\n== 2026 시나리오 가격 (현재 BTC ${b_now:,.0f}, SOL ${s_now:.2f}, SOLT 이론가 ${fair:.2f}, SOL 60일 변동성 {sv:.0%})")
L0=55130
rows=[('W 확인: BTC 넥라인 종가 돌파',64603,78.48,'inst'),('재시험 저점 (11/25)',57300,65.84,'inst'),('바닥 (11/21)',L0,64.87,'inst'),
      ('충격 저점형: 12일 뒤 −0.7% (2022)',L0*(1-0.007),None,'path'),('충격 저점형: 20일 뒤 −13.6% (2018)',L0*(1-0.136),None,'path')]
for lab,b,s,mode in rows:
    S=s if s is not None else sol(b); lo,hi=(sol(b,1.8),sol(b,1.0)) if s is None else (S,S)
    so=solt_inst(S) if mode=='inst' else solt_path(S)
    rng='' if s is not None else f" (SOL {lo:.1f}~{hi:.1f}, SOLT {solt_path(lo):.1f}~{solt_path(hi):.1f})"
    out.append(f"  {lab}: BTC ${b:,.0f} ({b/b_now-1:+.1%}) → SOL ${S:.2f} → SOLT ≈ ${so:.2f}{rng}")
open('output/u4_similarity_levels.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
