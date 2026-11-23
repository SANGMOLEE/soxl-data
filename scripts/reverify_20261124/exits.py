from base import *
def limit(i,T,W,start=1,lvl=None):
    """i일 종가 기준. start일부터 W일 동안 T(비율) 지정가, 미체결이면 마지막 날 종가. lvl을 주면 그 가격."""
    L=c[i]*(1+T) if lvl is None else lvl
    for j in range(i+start,i+start+W):
        if o[j]>=L: return (o[j]/c[i]-1)*100,j
        if h[j]>=L: return (L/c[i]-1)*100,j
    return (c[i+start+W-1]/c[i]-1)*100,None
def close_k(i,k): return (c[i+k]/c[i]-1)*100
def trail(i,arm,dd,W):
    """고가가 +arm 닿은 다음 날부터, 종가가 그 뒤 최고가 대비 -dd 이하면 그 종가에 매도. W일째 종가 시한."""
    armed=False; pk=None
    for j in range(i+1,i+W+1):
        if armed:
            if c[j]<=pk*(1-dd): return (c[j]/c[i]-1)*100
            pk=max(pk,h[j])
        elif h[j]>=c[i]*(1+arm): armed=True; pk=h[j]
    return (c[i+W]/c[i]-1)*100
def policies(i):
    P={}
    P["A 다음 날 종가 전량"]=close_k(i,1)
    a,_=limit(i,0.05,1); P["B 다음 날 +5% 전량"]=a
    b,_=limit(i,0.15,5); P["C 잠금안: 절반 B + 절반 5일 +15%"]=(a+b)/2
    L2=max(c[i]*1.15,o[i+1]*1.05); b2,_=limit(i,0,5,lvl=L2); P["D 변경3: 절반 B + 절반 max(+15%,시가×1.05) 5일"]=(a+b2)/2
    r30,_=limit(i,0.30,10); P["E 절반 B + 절반 10일 +30%"]=(a+r30)/2
    P["F 절반 5일 +15% + 절반 10일 +30%"]=(b+r30)/2
    r20,_=limit(i,0.20,10); P["G 전량 10일 +20%"]=r20
    P["H 5일째 종가 전량"]=close_k(i,5); P["I 10일째 종가 전량"]=close_k(i,10)
    P["J 추적: +15% 닿은 뒤 고점 -10% 종가, 10일 시한"]=trail(i,0.15,0.10,10)
    P["K 절반 B + 절반 추적(J)"]=(a+P["J 추적: +15% 닿은 뒤 고점 -10% 종가, 10일 시한"])/2
    P["L 절반 B + 절반 추적 +15%/고점-15%"]=(a+trail(i,0.15,0.15,10))/2
    return P
