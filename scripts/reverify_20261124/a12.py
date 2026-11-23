from base import *
# 바닥권 = 하락장(SOXL<200일선) & SOX 52주 고점 대비 -25% 이하
bottom=(bear&(dd252<=-0.25)).values
V=vx.values
def fwdS(i,k):  # SOXS 종가 매수 k일 보유
    return (cs[i+k]/cs[i]-1)*100
def fwdL(i,k): return (c[i+k]/c[i]-1)*100
def run(mask,f,k,nm,first=False):
    idx=[i for i in range(260,N-k) if mask[i]]
    if first:   # 비겹침: 직전 k일 안에 신호가 없던 날만
        out=[];last=-999
        for i in idx:
            if i-last>k: out.append(i); last=i
        idx=out
    return idx,[f(i,k) for i in idx]
print("=== A1. 바닥권 & VIX≥25 → SOXS 10일 보유 (원래: 승률 36%, 2010~ 25%, 중앙 -10.7%, 2010~ -14.0%, 평균 -6.3%, 최악 -80%)")
for first in (False,True):
    idx,x=run(bottom&(V>=25),fwdS,10,"",first)
    print(st(x,("비겹침 " if first else "모든 날 ")+"전체"))
    for e in ("~2009","2010~18","2019~26"):
        print(st([v for i,v in zip(idx,x) if era(i)==e],"   "+e))
print("\n-- 보유 기간별 (모든 날 / 비겹침)")
for k in (1,3,5,10,20):
    for first in (False,True):
        idx,x=run(bottom&(V>=25),fwdS,k,"",first); print(st(x,f"SOXS {k}일 "+("비겹침" if first else "모든 날")))
print("\n-- VIX 기준별 (SOXS 10일, 모든 날)")
for a,b in ((0,20),(20,25),(25,30),(30,35),(35,99)):
    idx,x=run(bottom&(V>=a)&(V<b),fwdS,10,""); print(st(x,f"VIX {a}~{b}"))
print("\n-- 대조: 바닥권이 아닐 때 SOXS 10일 (모든 날)")
idx,x=run(~bottom&(V>=25),fwdS,10,""); print(st(x,"바닥권 아님 & VIX≥25"))
idx,x=run(~bottom&(V<25),fwdS,10,""); print(st(x,"바닥권 아님 & VIX<25"))
print("\n-- 금리 국면 (SOXS 10일, 바닥권&VIX≥25)")
for nm,m in (("인상기",hike.values),("인하기",cutw.values),("그 외",~(hike.values|cutw.values))):
    idx,x=run(bottom&(V>=25)&m,fwdS,10,""); print(st(x,nm))
print("\n=== A2. 같은 자리 SOXL 롱 10일 (원래: 51%, 중앙 +0.4%, 평균 +3.3%, 최악 -68%)")
for first in (False,True):
    idx,x=run(bottom&(V>=25),fwdL,10,"",first); print(st(x,("비겹침" if first else "모든 날")))
    for e in ("~2009","2010~18","2019~26"): print(st([v for i,v in zip(idx,x) if era(i)==e],"   "+e))
idx,x=run(bottom&(V<25),fwdL,10,""); print(st(x,"대조: 바닥권 & VIX<25 롱 (원래 48%, -1.9%)"))
# 첫날 계열: VIX가 25를 처음 넘는 날 (직전 20일 동안 25 미만) / VIX가 정점(20일 최고) 대비 15% 꺾인 첫날
vser=pd.Series(V,index=cal)
spike=(vser>=25)&(vser.shift(1)<25)
peak=vser.rolling(20).max(); turn=(vser<=peak*0.85)&(vser.shift(1)>peak.shift(1)*0.85)&(peak>=25)
for nm,m in (("VIX 25 돌파 첫날 (원래 44건 52% 중앙 +4.4% 상위3뺀 +0.5%)",spike.values),("VIX 정점 대비 15% 꺾인 첫날 (원래 42건 48% 중앙 -2.1%)",turn.values)):
    idx,x=run(bottom&m,fwdL,10,"",True); print(st(x,nm,60))
    idx,x=run(bottom&m,fwdS,10,"",True); print(st(x,"   같은 날 SOXS",60))
