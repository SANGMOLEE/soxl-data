from exits import *
r=rL.values*100; P=pos.values; V=vx.values; Bm=bear.values; R=real.values; H=hike.values; DD=dd252.values
COST=0.2
isD=np.zeros(N,bool)
for i in range(2,N):
    if r[i]<=-8 and P[i]<0.2 and r[i-1]<0: isD[i]=True
Didx=[i for i in range(2,N-1) if isD[i]]
d2=lambda i:(c[i+1]/c[i]-1)*100-COST
print("=== B1. D 규칙 일봉 근사 (원래: 일봉 2010~ 89건 승률 66% 평균 +3.1% / 30분봉 2022~26 39건 67% 중앙 +2.3% 평균 +2.9% 최악 -12.7%)")
print(st([d2(i) for i in Didx if R[i]],"2010~ 실제 SOXL (비용 0.2% 차감)"))
print(st([(c[i+1]/c[i]-1)*100 for i in Didx if R[i]],"2010~ 비용 차감 전"))
for e in ("~2009","2010~18","2019~26"): print(st([d2(i) for i in Didx if era(i)==e],"  "+e))
print(st([d2(i) for i in Didx if cal[i]>=pd.Timestamp("2022-01-01")],"  2022~ (30분봉 검증 구간)"))
print("-- 반복 신호 (직전 5거래일 안에 D)")
rep=[i for i in Didx if isD[max(0,i-5):i].any()]; first=[i for i in Didx if not isD[max(0,i-5):i].any()]
print(st([d2(i) for i in first if R[i]],"2010~ 첫 신호")); print(st([d2(i) for i in rep if R[i]],"2010~ 반복 신호"))
print(st([d2(i) for i in first],"전체 첫 신호")); print(st([d2(i) for i in rep],"전체 반복 신호"))
print("-- 주변값 (2010~, 비용 차감)")
for th in (-6,-7,-8,-9,-10,-12):
    for pz in (0.15,0.2,0.33):
        idx=[i for i in range(2,N-1) if R[i] and r[i]<=th and P[i]<pz and r[i-1]<0]
        x=[d2(i) for i in idx]; xs=np.sort(x)
        print(f"   당일≤{th}% 위치<{pz}: {len(x)}건 이익 {(np.array(x)>0).mean()*100:.0f}% 중앙 {np.median(x):+.1f}% 상위3뺀 {xs[:-3].mean():+.1f}% 평균 {np.mean(x):+.1f}%")
idx=[i for i in range(2,N-1) if R[i] and r[i]<=-8 and P[i]<0.2 and r[i-1]>=0]; print(st([d2(i) for i in idx],"대조: 전일 상승(③ 없음)"))
idx=[i for i in range(2,N-1) if R[i] and r[i]<=-8 and P[i]>=0.2 and r[i-1]<0]; print(st([d2(i) for i in idx],"대조: 저가권 아님(② 없음)"))
print("-- 국면별 (2010~)")
for nm,m in (("하락장",Bm),("상승장",~Bm),("VIX≥30",V>=30),("VIX<25",V<25),("인상기",H),("하락장&VIX≥30&SOX-25%↓",Bm&(V>=30)&(DD<=-0.25))):
    print(st([d2(i) for i in Didx if R[i] and m[i]],nm))
print("-- 보유 기간 (2010~, 비용 차감)")
for k in (1,2,3,5,10): print(st([(c[i+k]/c[i]-1)*100-COST for i in Didx if R[i] and i+k<N],f"{k}일째 종가"))
mix=[]
for i in Didx:
    if not R[i] or i+3>=N: continue
    a=d2(i); b,_=limit(i,0.08,3); mix.append((a+b-COST)/2)
print(st(mix,"혼합: 절반 D2 + 절반 +8% 3일"))
pb=[]
for i in Didx:
    if not R[i] or i+11>=N: continue
    x,_=limit(i,0.15,10); y,_=limit(i,0.25,10); pb.append((x+y)/2-COST)
print(st(pb,"(b) +15% 절반·+25% 나머지·10일"))
print("-- 첫날 종가가 +10%↑일 때 하루 더 들고 가면")
ex=[(c[i+2]/c[i+1]-1)*100 for i in Didx if i+2<N and c[i+1]/c[i]-1>=0.10]; print(st(ex,"하루 더 (첫날 종가 기준)"))
print("-- 채택(10/31) 이후 실전 표본외 신호")
for i in Didx:
    if cal[i]>=pd.Timestamp("2026-10-31"):
        nx=f"{(c[i+1]/c[i]-1)*100:+.1f}%" if i+1<N else "결과 대기(다음 날 종가 미반영)"
        print(f"   {cal[i].date()} 당일 {r[i]:+.1f}% 위치 {P[i]:.2f} 전일 {r[i-1]:+.1f}% 반복 {'예' if isD[max(0,i-5):i].any() else '아니오'} → 다음 날 {nx}")
for i in [N-1]:
    if isD[i]: print(f"   {cal[i].date()} D 신호 (다음 날 결과 미반영) 반복 {'예' if isD[max(0,i-5):i].any() else '아니오'}")
