# K. 11/27 종가 반영: 스프링 다음 날 강하게 오른(팔로스루) 경우의 과거 결과 vs 변동성만의 예상
#  11/27 봉(야후, 반일장)은 저장소에 아직 없어 메모리에서만 붙임: O 9036.29 H 9213.64 L 8789.31 C 9186.71
import sys; sys.path.insert(0,'scripts')
from common import *
from math import erf, sqrt, log, comb
Phi=lambda x:0.5*(1+erf(x/sqrt(2)))
x=d[['open','high','low','close']].copy(); x.loc[pd.Timestamp('2026-11-27')]=[9036.29,9213.64,8789.31,9186.71]
h=x.high.values; l=x.low.values; c=x.close.values; n=len(x); ix=x.index
dd=l/pd.Series(h).rolling(252,min_periods=120).max().values-1
pos=np.clip((c-l)/np.where(h>l,h-l,np.nan),0,1); lr=np.log(c/np.roll(c,1)); lr[0]=np.nan
def s20(i): return np.nanstd(lr[i-19:i+1],ddof=1)
def binom_p(k,m,p0):
    pk=comb(m,k)*p0**k*(1-p0)**(m-k); return min(1.0,sum(comb(m,i)*p0**i*(1-p0)**(m-i) for i in range(m+1) if comb(m,i)*p0**i*(1-p0)**(m-i)<=pk*(1+1e-9)))
def events(LB=60,B=0.08,FT=0.03,FTPOS=0.7,DTH=-0.25):
    ev=[]; last=-99
    for b in range(260,n-1):
        if dd[b]>DTH or b-last<10: continue
        a=b-LB+int(np.argmin(l[b-LB:b])); m=l[a]
        if l[b]>=m or b-a<3 or c[b]<m: continue
        nk=h[a+1:b].max()
        if nk<m*(1+B): continue
        f=b+1
        if c[f]/c[b]-1<FT or l[f]<=l[b] or pos[f]<FTPOS or c[f]>nk: continue
        # f일 종가부터: 넥라인 종가 돌파 vs 스프링 저점 장중 이탈, 먼저 온 것 (60일)
        res='진행중'
        for k in range(f+1,min(n,f+61)):
            if l[k]<l[b]: res='저점 먼저'; break
            if c[k]>nk: res='넥라인 먼저'; break
        up=log(nk/c[f]); dn=log(c[f]/l[b]); sg=s20(f)
        ev.append(dict(f=f,스프링=ix[b].date(),다음날=ix[f].date(),다음날상승=c[f]/c[b]-1,넥라인까지=nk/c[f]-1,저점까지=l[b]/c[f]-1,결과=res,
            RW넥라인먼저=dn/(up+dn),RW20일재터치=min(1,2*Phi(-dn/(sg*sqrt(20)))),
            재터치20=float(l[f+1:f+21].min()<l[b]) if f+20<n else np.nan,
            r20=c[f+20]/c[f]-1 if f+20<n else np.nan,r60=c[f+60]/c[f]-1 if f+60<n else np.nan))
        last=b
    return pd.DataFrame(ev)
bear=[i for i in range(260,n-61) if dd[i]<=-0.25]
base20=np.mean([c[i+20]<c[i] for i in bear]); base60=np.mean([c[i+60]<c[i] for i in bear])
out=[f"== 11/27 반영: SOX 종가 9,186.71 (+4.7%, 마감 위치 {pos[-1]:.2f}) | 넥라인 9,728.12까지 {9728.12/9186.71-1:+.1%}, 스프링 저점 8,129.23까지 {8129.23/9186.71-1:+.1%}"]
sg=np.nanstd(lr[-20:],ddof=1); sg60=np.nanstd(lr[-60:],ddof=1); up=log(9728.12/9186.71); dn=log(9186.71/8129.23)
out.append(f"  변동성만(추세 0): 넥라인 먼저 {dn/(up+dn):.0%} | 20일 안 8,129 재터치 "+" / ".join(f"σ{s:.1%} {min(1,2*Phi(-dn/(s*sqrt(20)))):.0%}" for s in (0.04,sg60,0.05,sg)))
out.append(f"  비교 기준(약세장 모든 날): 20일 뒤 더 낮음 {base20:.0%}, 60일 뒤 {base60:.0%}")
E=events(); P=E[E.결과!='진행중']
show=E.drop(columns=['f']).copy()
for k in ('다음날상승','넥라인까지','저점까지','RW넥라인먼저','RW20일재터치','r20','r60'): show[k]=(show[k].astype(float)*100).round(1)
out.append("\n== 기본: 스프링(60일 저점 장중 이탈·그 위 마감·사이 반등 8%↑) 다음 날 +3%↑·스프링 저점 위·마감 위치 0.7↑\n"+show.to_string(index=False))
def line(E,nm):
    P=E[E.결과!='진행중']; m=len(P); k=int((P.결과=='넥라인 먼저').sum())
    s=f"  {nm}: {len(E)}건 | 넥라인 먼저 {k}/{m} vs 변동성만 {P.RW넥라인먼저.sum():.1f}"
    Q=E[E.재터치20.notna()]; s+=f" | 20일 안 재터치 {int(Q.재터치20.sum())}/{len(Q)} vs 변동성만 {Q.RW20일재터치.sum():.1f}"
    for hh,bs in ((20,base20),(60,base60)):
        y=E[f'r{hh}'].dropna(); kk=int((y<0).sum()); mm=len(y)
        if mm: s+=f" | {hh}일 뒤 더 낮음 {kk}/{mm} (비교 {bs:.0%}, p={binom_p(kk,mm,bs):.2f}), 중앙 {np.median(y)*100:+.1f}%"
    return s
out.append("\n"+line(E,"기본"))
out.append("  민감도:")
for LB in (20,60):
    for B in (0.05,0.08):
        for FT in (0.02,0.03,0.04):
            out.append(line(events(LB,B,FT),f"직전 저점 {LB}일·사이 반등 {B:.0%}·다음 날 +{FT:.0%}"))
open(f'{OUT}/k_followthrough.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
