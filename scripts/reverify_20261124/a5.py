from exits import *
from exits import limit as lim
r=rL.values*100; rx=rs.values*100; DD=dd252.values; V=vx.values; R=real.values
def pol(i):
    P={}
    P["A 랠리 당일 종가 전량"]=0.0
    P["B 다음 날 종가 전량"]=close_k(i,1)
    b5,_=lim(i,0.05,1); P["C 다음 날 +5% 지정가 전량"]=b5
    r20,_=lim(i,0.20,10); P["D 전량 10일 +20%"]=r20
    P["E 절반 당일 종가 + 절반 10일 +20% (11/24 제안)"]=r20/2
    P["F 절반 당일 + 절반 다음 날 +5%"]=b5/2
    r30,_=lim(i,0.30,10); P["G 절반 당일 + 절반 10일 +30%"]=r30/2
    r10,_=lim(i,0.10,10); P["H 절반 당일 + 절반 10일 +10%"]=r10/2
    P["I 5일째 종가 전량"]=close_k(i,5); P["J 10일째 종가 전량"]=close_k(i,10)
    return P
def show(idx,title):
    print(f"\n[{title}] {len(idx)}건")
    res={}
    for i in idx:
        for k,v in pol(i).items(): res.setdefault(k,[]).append(v)
    for k,v in res.items(): print(st(v,k,44))
A=[i for i in range(260,N-11) if rx[i]>=8 and DD[i-1]<=-0.25]
show(A,"SOX 하루 +8%↑ & 직전 SOX 52주 고점 대비 -25%↓ (원래 40건)")
for e in ("~2009","2019~26"):
    s=[i for i in A if era(i)==e]
    if s: show(s,"   "+e)
B=[i for i in range(260,N-11) if R[i] and r[i]>=15]; show(B,"실제 SOXL 하루 +15%↑ (원래 41건)")
show([i for i in B if bear.values[i]],"   그중 하락장")
show([i for i in B if not bear.values[i]],"   그중 상승장")
show([i for i in B if V[i]>=30],"   그중 VIX≥30")
C=[i for i in range(260,N-11) if R[i] and r[i]>=20]; show(C,"실제 SOXL 하루 +20%↑ (원래 9건)")
print("   +20% 날짜:",[str(cal[i].date()) for i in C])
# 다음 날 통계
print("\n-- 다음 날 종가가 랠리 당일 종가보다 낮을 확률")
for nm,s in (("SOX +8% 약세장",A),("SOXL +15%",B),("SOXL +20%",C)):
    print(f"  {nm}: {np.mean([c[i+1]<c[i] for i in s])*100:.0f}% ({len(s)}건)")
