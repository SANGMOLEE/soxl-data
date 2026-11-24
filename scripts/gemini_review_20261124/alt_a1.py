import sys; sys.path.insert(0,"/home/claude/rv")
from base import *
s=SOXL[SOXL.index>="2010-06-01"].copy()
C=s.close.values;O=s.open.values;H=s.high.values;L=s.low.values;D=s.index;n=len(s)
r=np.r_[np.nan,C[1:]/C[:-1]-1]*100
lv=np.log(C); vol20=pd.Series(np.r_[np.nan,np.diff(lv)]).rolling(20).std().values*np.sqrt(252)
B=bear.reindex(D).values
def longlim(ev,x,tp=None,sl=None,cost=0.2):
    out=[]
    for i in ev:
        j=i+1; E=C[i]*(1-x)
        if L[j]>E: continue
        e=min(O[j],E)
        if sl is not None and L[j]<=e*(1-sl): out.append(-sl*100-cost); continue   # 비관: 손절 먼저
        if tp is not None and C[j]>=e*(1+tp): out.append(tp*100-cost); continue     # 비관: 종가가 익절가 위일 때만 익절 인정
        out.append((C[j]/e-1)*100-cost)
    return out
def shortlim(ev,x,tp=None,sl=None,cost=0.3):
    out=[]
    for i in ev:
        j=i+1; E=C[i]*(1+x)
        if H[j]<E: continue
        e=max(O[j],E)
        if sl is not None and H[j]>=e*(1+sl): out.append(-sl*100-cost); continue
        if tp is not None and C[j]<=e*(1-tp): out.append(tp*100-cost); continue
        out.append((e/C[j]-1)*100-cost)
    return out
def openfade(ev,g):
    return [ (O[i+1]/C[i+1]-1)*100-0.3 for i in ev if O[i+1]>=C[i]*(1+g)]
def report(ev,title):
    print(f"\n[{title}] {len(ev)}일")
    for x in (0.04,0.06,0.08,0.10):
        print(st(longlim(ev,x),f"롱: 전일종가 -{int(x*100)}% 지정가 → 종가 매도",44))
    print(st(longlim(ev,0.06,tp=0.05),"롱: -6% 지정가, +5% 익절(비관)·종가",44))
    print(st(longlim(ev,0.06,sl=0.06),"롱: -6% 지정가, -6% 손절(비관)·종가",44))
    for x in (0.04,0.076,0.10):
        print(st(shortlim(ev,x),f"숏: 전일종가 +{x*100:.1f}% 도달 시 SOXS → 종가",44))
    for g in (0.0,0.03):
        print(st(openfade(ev,g),f"숏: 시가 +{int(g*100)}%↑ 갭이면 시가 SOXS → 종가",44))
E15=[i for i in range(1,n-1) if r[i]>=15]
report(E15,"실제 SOXL +15%↑ 다음 날 (지금과 같은 자리)")
report([i for i in E15 if B[i]],"   그중 하락장")
HV=[i for i in range(30,n-1) if vol20[i]>=1.2 and B[i]]
report(HV,"대조: 하락장 & 20일 변동성 120%↑ 모든 날 (더 넓은 표본)")
