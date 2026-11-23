from exits import *
r=rL.values*100; P=pos.values; V=vx.values
crash=[i for i in range(2,N-11) if r[i]<=-15 and r[i-1]<0]
low=[i for i in crash if P[i]<0.2]; notlow=[i for i in crash if P[i]>=0.2]
print("=== A4. 급락일 손절 예외 (원래: 저가권 95건 다음 날 종가 상승 61% 중앙 +4.1% 최악 -25.7% / +5% 지정가 81% +5.0% / 저가권 아님 15건 33% -4.9%)")
print(st([close_k(i,1) for i in low],"저가권 마감: 다음 날 종가"))
print(st([limit(i,0.05,1)[0] for i in low],"저가권 마감: 다음 날 +5% 지정가"))
print(st([close_k(i,1) for i in notlow],"저가권 아님: 다음 날 종가"))
for e in ("~2009","2010~18","2019~26"):
    s=[i for i in low if era(i)==e]; print(st([limit(i,0.05,1)[0] for i in s],f"   {e} 저가권 +5% 지정가"))
lowv=[i for i in low if V[i]>=25]
print(f"\n-- 매도 방식 비교: 저가권 마감 & VIX≥25 ({len(lowv)}건; 원래 63건, 잠금안 70% 중앙 +10.0% 평균 +4.6% 최악 -17.6%)")
res={}
for i in lowv:
    for k,v in policies(i).items(): res.setdefault(k,[]).append(v)
for k,v in res.items(): print(st(v,k,46))
cur=[i for i in lowv if bear.values[i] and dd252.values[i]<=-0.25]
print(f"\n-- 같은 비교, 지금 국면(하락장 & SOX -25%↓ & VIX≥25) {len(cur)}건")
res={}
for i in cur:
    for k,v in policies(i).items(): res.setdefault(k,[]).append(v)
for k,v in res.items(): print(st(v,k,46))
big=[i for i in low if r[i]<=-25]
print(f"\n-- 당일 -25%↓ 저가권 {len(big)}건 (11/20 같은 극단)")
res={}
for i in big:
    for k,v in policies(i).items(): res.setdefault(k,[]).append(v)
for k,v in res.items(): print(st(v,k,46))
print("   날짜:",[str(cal[i].date()) for i in big])
# 갭 상승 +8%↑로 시작한 경우 (원래 11건, 잠금안 100% 이익)
gu=[i for i in low if oL.values[i+1]>=0.08]
print(f"\n-- 다음 날 갭 +8%↑로 열린 경우 {len(gu)}건: {[str(cal[i].date()) for i in gu]}")
res={}
for i in gu:
    for k,v in policies(i).items(): res.setdefault(k,[]).append(v)
for k,v in res.items(): print(st(v,k,46))
