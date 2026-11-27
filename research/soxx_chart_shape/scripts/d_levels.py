# D. SOX 시나리오 가격 → SOXX·SOXL 환산 (기준: 11/25 종가)
#  SOXX ≈ SOX 비율 × 기울기(최근 60일 회귀), SOXL ≈ 종가 × (SOX비)^3 × e^(−3σ²t)
import sys; sys.path.insert(0,'scripts')
from common import *
j=pd.DataFrame({'x':np.log(SOX.close).diff(),'y':np.log(SOXX.close).diff(),'l':np.log(SOXL.close).diff()}).dropna()[-60:]
bx=np.polyfit(j.x,j.y,1)[0]; bl=np.polyfit(j.x,j.l,1)[0]
S0,X0,L0=SOX.close.iloc[-1],SOXX.close.iloc[-1],SOXL.close.iloc[-1]
def soxx(S): return X0*(S/S0)**bx
def soxl(S,t,sig): return L0*(S/S0)**3*np.exp(-3*sig**2*t)
out=[f"기준 {SOX.index[-1].date()}: SOX {S0:.1f} · SOXX {X0:.2f} · SOXL {L0:.2f} | 최근 60일 기울기 SOXX/SOX {bx:.2f}, SOXL/SOX {bl:.2f}"]
lv=[("넥라인 (11/23 SOX 고가)",9728.1,10),("11/20 장중 저가",8342.2,5),("11/25 장중 저가 (스프링 저점)",8129.2,5),
    ("스프링 저점 -2% (2016형)",8129.2*0.98,10),("스프링 저점 -6% (2010년 이후 중앙 부근)",8129.2*0.94,15),("스프링 저점 -12% (전체 중앙, 2022-09형)",8129.2*0.88,20),
    ("스프링 저점 -25% (2008·2002형 깊은 경우)",8129.2*0.75,30),
    ("200주선×1.12 (2027-02 하순)",7026,60),("200주선×1.12 (2027-04 하순)",7300,105),("200주선×1.00 (2027-04 하순)",6518,105)]
out.append(f"{'자리':40s} {'SOX':>7s} {'SOXX':>7s} {'SOXL(바로)':>10s} {'SOXL(σ3%)':>10s} {'SOXL(σ4%)':>10s}  (t=거래일)")
for nm,S,t in lv:
    out.append(f"{nm:40s} {S:7.0f} {soxx(S):7.1f} {L0*(S/S0)**3:10.1f} {soxl(S,t,0.03):10.1f} {soxl(S,t,0.04):10.1f}  t={t}")
open(f'{OUT}/d_levels.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
