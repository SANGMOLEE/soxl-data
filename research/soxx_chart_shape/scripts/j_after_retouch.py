# J. 스프링 저점(지금 SOX 8,129 ≈ SOXL 25)을 다시 찍은 뒤: 반등이냐 추가 하락이냐 (과거 13번)
import sys; sys.path.insert(0,'scripts')
from common import *
from math import log
S=pd.read_csv(f'{OUT}/b3_springs.csv',parse_dates=['날짜']); S=S[S.결과!='진행중']
rows=[]
for r in S.itertuples():
    b=int(r.b); L=Lo[b]
    k=next((j for j in range(b+1,min(N,b+21)) if Lo[j]<L),None)
    if k is None: continue
    def first(up,dn,start=k,T=60):
        for j in range(start,min(N,start+T)):
            if Lo[j]<=L*(1-dn): return '추가 하락'
            if C[j]>=L*(1+up): return '반등'
        return '없음'
    rows.append(dict(스프링=r.날짜.date(),재터치일=IDX[k].date(),
        최저20=Lo[k:k+20].min()/L-1, 최저60=Lo[k:k+60].min()/L-1,
        최고20=H[k+1:k+21].max()/L-1, 종가5=C[min(N-1,k+5)]/L-1, 종가20=C[min(N-1,k+20)]/L-1,
        먼저_반등10_vs_하락6=first(0.10,0.06), 먼저_반등10_vs_하락12=first(0.10,0.12), 먼저_반등20_vs_하락12=first(0.20,0.12)))
R=pd.DataFrame(rows); n=len(R)
out=[f"== 스프링 저점을 다시 찍은 {n}번: 찍은 가격(= 지금 SOX 8,129, SOXL 약 25) 기준"]
S_=R.copy()
for c in ('최저20','최저60','최고20','종가5','종가20'): S_[c]=(S_[c]*100).round(1)
out.append(S_.to_string(index=False))
def st(x,nm):
    x=np.sort(np.asarray(x)*100); return f"  {nm:26s} 중앙 {np.median(x):+6.1f}% | 상위3뺀 {x[:-3].mean():+6.1f}% | 평균 {x.mean():+6.1f}% | 최악 {x.min():+6.1f}% | 최고 {x.max():+6.1f}%"
out.append("")
for c,nm in (('최저20','20일 안 더 내려간 최저'),('최저60','60일 안 더 내려간 최저'),('최고20','20일 안 반등 최고'),('종가5','5일 뒤 종가'),('종가20','20일 뒤 종가')): out.append(st(R[c],nm))
for t in (0.03,0.06,0.12,0.20): out.append(f"  20일 안 찍은 가격보다 {t:.0%} 이상 더 내려감: {(R.최저20<=-t).sum()}/{n} | 60일 안: {(R.최저60<=-t).sum()}/{n}")
for t in (0.05,0.10,0.20): out.append(f"  20일 안 찍은 가격보다 {t:.0%} 이상 반등: {(R.최고20>=t).sum()}/{n}")
for c,lab,base in (('먼저_반등10_vs_하락6','+10% 반등 vs −6% 추가 하락, 먼저 온 것',log(1.10)/(log(1.10)+log(1/0.94))),('먼저_반등10_vs_하락12','+10% 반등 vs −12% 추가 하락',log(1.10)/(log(1.10)+log(1/0.88))),('먼저_반등20_vs_하락12','+20% 반등 vs −12% 추가 하락',log(1.20)/(log(1.20)+log(1/0.88)))):
    v=R[c].value_counts(); out.append(f"  {lab}: "+", ".join(f"{a} {b}" for a,b in v.items())+f" | 변동성만이면 추가 하락 먼저 {base:.0%}")
out.append("\n  SOXL 환산(같은 날 기준 근사): SOX −3% ≈ SOXL 23, −6% ≈ 20.5, −12% ≈ 16.5, −20% ≈ 12.5 / +5% ≈ 29, +10% ≈ 33, +20% ≈ 43")
open(f'{OUT}/j_after_retouch.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
