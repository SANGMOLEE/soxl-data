from exits import *
r=rL.values*100; P=pos.values; R=real.values
isD=np.array([i>=2 and r[i]<=-8 and P[i]<0.2 and r[i-1]<0 for i in range(N)])
def pc(i):  # (c) 진입일 저가를 종가로 깨면 다음 날... 종가 매도, +20% 지정가, 10일
    L=c[i]*1.2
    for j in range(i+1,i+11):
        if o[j]>=L: return (o[j]/c[i]-1)*100
        if h[j]>=L: return 20.0
        if c[j]<l[i]: return (c[j]/c[i]-1)*100
    return (c[i+10]/c[i]-1)*100
def pb(i): x,_=limit(i,0.15,10); y,_=limit(i,0.25,10); return (x+y)/2
def pb2(i): x,_=limit(i,0.20,10); y,_=limit(i,0.30,10); return (x+y)/2
print("=== B6. 여러 날 보유 청산 (b) (원래: +15% 절반·+25% 나머지·10일, '모든 구간 승률 최고', 손절형 (c) 승률 39~43%)")
for nm,idx in (("D 신호 진입 2010~",[i for i in range(2,N-11) if isD[i] and R[i]]),("D 신호 진입 ~2009",[i for i in range(2,N-11) if isD[i] and not R[i]]),
               ("하락장 -15%↓ 급락 진입 2010~",[i for i in range(2,N-11) if R[i] and r[i]<=-15 and bear.values[i]])):
    print(f"\n[{nm}] {len(idx)}건")
    print(st([(c[i+5]/c[i]-1)*100 for i in idx],"(a) 5일 보유",36))
    print(st([pb(i) for i in idx],"(b) +15%/+25%/10일",36))
    print(st([pb2(i) for i in idx],"(b') +20%/+30%/10일 (v0.1안)",36))
    print(st([pc(i) for i in idx],"(c) 진입일 저가 종가이탈 손절·+20%·10일",36))
