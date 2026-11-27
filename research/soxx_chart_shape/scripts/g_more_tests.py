# G. 추가 시험 (11/27): ① 재이탈을 종가 기준으로 ② 거래량을 넣은 모양 ③ 주봉 모양
#  모든 시험은 "모양으로 고른 날" vs "모양 없는 비교 기준(같은 변동성의 무작위 걸음, 또는 같은 국면의 모든 날)"을 나란히 봄
import sys; sys.path.insert(0,'scripts')
from common import *
from math import erf, sqrt, log, comb
Phi=lambda x:0.5*(1+erf(x/sqrt(2)))
rng=np.random.default_rng(7)
def wilson(k,n,z=1.96):
    if n==0: return (np.nan,np.nan)
    p=k/n; c=(p+z*z/(2*n))/(1+z*z/n); h=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n); return c-h,c+h
def binom_p(k,n,p0):
    """양쪽 p값: 관측 k가 기준 p0에서 나올 확률 이하인 경우의 합"""
    pk=comb(n,k)*p0**k*(1-p0)**(n-k)
    return min(1.0,sum(comb(n,i)*p0**i*(1-p0)**(n-i) for i in range(n+1) if comb(n,i)*p0**i*(1-p0)**(n-i)<=pk*(1+1e-9)))
def mc_close_below(dist,sig,T=20,n=20000):
    """종가 기준: T일 안 종가가 dist(로그) 아래로 한 번이라도 마감할 확률 (추세 0, 정규)"""
    x=np.cumsum(rng.normal(0,sig,(n,T)),axis=1); return (x.min(axis=1)<-dist).mean()
def p_touch(dist,sig,T): return min(1.0,2*Phi(-dist/(sig*sqrt(T))))
lr=np.log(d.close).diff().values
def s20(i): return np.nanstd(lr[i-19:i+1],ddof=1)
out=[]
# ---------------- ① 종가 기준 재이탈
S=pd.read_csv(f'{OUT}/b3_springs.csv',parse_dates=['날짜']); S=S[S.결과!='진행중']
out.append("== ① 스프링 16건: 재이탈을 종가 기준으로 (20거래일 안)")
rows=[]
for r in S.itertuples():
    b=int(r.b); a=b-60+int(np.argmin(Lo[b-60:b])); sg=s20(b)
    cl_prev=C[a:b].min()                                      # 직전 저점 구간의 최저 종가 (지금의 11/20 종가 8,408.59에 해당)
    f=C[b+1:b+21]
    rows.append(dict(날짜=r.날짜.date(),
        장중재이탈=float(Lo[b+1:b+21].min()<Lo[b]),RW장중=p_touch(log(C[b]/Lo[b]),sg,20),
        종가_스프링저점아래=float(f.min()<Lo[b]),RW종가_스프링저점=mc_close_below(log(C[b]/Lo[b]),sg),
        종가_직전최저종가아래=float(f.min()<cl_prev),RW종가_직전최저종가=mc_close_below(log(C[b]/cl_prev),sg) if C[b]>cl_prev else 1.0))
R=pd.DataFrame(rows); n=len(R)
for k,e,lab in (('장중재이탈','RW장중','장중 저가 < 스프링 저점 (보고서 기준)'),('종가_스프링저점아래','RW종가_스프링저점','종가 < 스프링 저점'),('종가_직전최저종가아래','RW종가_직전최저종가','종가 < 직전 최저 종가 (지금의 8,408.59)')):
    o=int(R[k].sum()); ex=R[e].sum(); lo,hi=wilson(o,n)
    out.append(f"  {lab:38s}: 실제 {o}/{n} ({o/n:.0%}, 95% {lo:.0%}~{hi:.0%}) | 변동성만 예상 {ex:.1f}건 ({ex/n:.0%})")
b=N-1; sgs=[0.03,np.nanstd(lr[-60:],ddof=1),0.05,s20(b)]
out.append("  지금 (변동성만, 추세 0): "+" / ".join(f"σ{sg:.1%}: 장중 8,129 {p_touch(log(C[b]/8129.23),sg,20):.0%}·종가 8,129 {mc_close_below(log(C[b]/8129.23),sg):.0%}·종가 8,408.59 {mc_close_below(log(C[b]/8408.59),sg):.0%}" for sg in sgs))
# ---------------- ② 거래량 (2010년 이후, SOXX 거래량, 11/5 분할 전 ×3)
vx=pd.read_csv(os.path.join(ROOT,'data','prices','SOXX.csv'),parse_dates=['date']).set_index('date').volume
vx=vx[~vx.index.duplicated()]; vx.loc[vx.index<'2026-11-05']*=3
vr=(vx/vx.rolling(50).median().shift(1)).reindex(IDX).values
vl=pd.read_csv(os.path.join(ROOT,'data','prices','SOXL.csv'),parse_dates=['date']).set_index('date').volume
vl=vl[~vl.index.duplicated()]; vlr=(vl/vl.rolling(50).median().shift(1)).reindex(IDX).values
DD=d.dd.values; POS=d.pos.values
start=IDX.get_loc(IDX[IDX>='2010-06-01'][0])
out.append(f"\n== ② 거래량 (2010-06 이후). 지금 SOXX 거래량 배수(50일 중앙 대비): 11/20 {vr[IDX.get_loc(pd.Timestamp('2026-11-20'))]:.1f}배, 11/25 {vr[-1]:.1f}배 | SOXL 11/20 {vlr[IDX.get_loc(pd.Timestamp('2026-11-20'))]:.1f}배, 11/25 {vlr[-1]:.1f}배")
def outcome_rows(idx):
    rr=[]
    for i in idx:
        sg=s20(i); rr.append(dict(i=i,날짜=IDX[i].date(),거래량배수=vr[i],위치=POS[i],고점대비=DD[i],
            재이탈20=float(Lo[i+1:i+21].min()<Lo[i]) if i+20<N else np.nan,RW재이탈20=p_touch(log(C[i]/Lo[i]),sg,20),
            r5=C[i+5]/C[i]-1 if i+5<N else np.nan,r20=C[i+20]/C[i]-1 if i+20<N else np.nan,r60=C[i+60]/C[i]-1 if i+60<N else np.nan))
    return pd.DataFrame(rr)
def thin(idx,gap=10):
    kept=[]; 
    for i in idx:
        if not kept or i-kept[-1]>gap: kept.append(i)
    return kept
bear_all=[i for i in range(start,N-1) if DD[i]<=-0.20]
base={h:np.mean([C[i+h]<C[i] for i in bear_all if i+h<N]) for h in (5,20,60)}
def report(nm,idx):
    X=outcome_rows(idx); P=X[X.재이탈20.notna()]
    if len(P)==0: out.append(f"  {nm}: 0건"); return X
    o=int(P.재이탈20.sum()); n=len(P)
    line=f"  {nm}: {len(X)}건 | 20일 안 장중 재이탈 실제 {o}/{n} ({o/n:.0%}) vs 변동성만 {P.RW재이탈20.sum():.1f}건"
    for h in (5,20,60):
        y=X[f'r{h}'].dropna(); k=int((y<0).sum()); m=len(y)
        if m: line+=f" | {h}일 뒤 하락 {k}/{m} ({k/m:.0%}, 비교 {base[h]:.0%}, p={binom_p(k,m,base[h]):.2f}), 중앙 {np.median(y)*100:+.1f}%"
    out.append(line); return X
out.append(f"  비교 기준(2010년 이후 SOX 52주 고점 대비 −20%↓ 모든 날 {len(bear_all)}일): 5일 뒤 하락 {base[5]:.0%}, 20일 {base[20]:.0%}, 60일 {base[60]:.0%}")
hammer=lambda i: Lo[i]<=Lo[i-20:i].min() and POS[i]>=0.8 and DD[i]<=-0.20
X1=report("망치(20일 신저가·마감 위치 0.8↑), 거래량 2배↑",thin([i for i in bear_all if i>start+60 and hammer(i) and vr[i]>=2]))
X2=report("망치, 거래량 1.5배 미만 (거래량 효과 비교용)",thin([i for i in bear_all if i>start+60 and hammer(i) and vr[i]<1.5]))
X3=report("망치, SOXL 거래량 2배↑",thin([i for i in bear_all if i>start+60 and hammer(i) and vlr[i]>=2]))
# 지금과 같은 순서: 5일 안에 투매일(하락 −5%↓·마감 위치 0.2↓·거래량 2배↑)이 있고, 그 뒤 스프링(그 투매일 저점 장중 이탈 & 그 위 종가)
seq=[]
for i in bear_all:
    if i<start+60: continue
    for j in range(i-5,i):
        if C[j]/C[j-1]-1<=-0.05 and POS[j]<=0.2 and vr[j]>=2 and Lo[i]<Lo[j] and C[i]>=Lo[j] and POS[i]>=0.7:
            seq.append(i); break
X4=report("투매일(−5%↓·저가 마감·거래량 2배↑) 뒤 5일 안 스프링",thin(seq))
for nm,X in (("망치+거래량 2배↑",X1),("투매 뒤 스프링",X4)):
    if len(X) and len(X)<=20:
        S_=X.copy()
        for k in ('고점대비','r5','r20','r60'): S_[k]=(S_[k]*100).round(1)
        out.append(f"   [{nm} 사례]\n"+S_[['날짜','거래량배수','위치','고점대비','재이탈20','r5','r20','r60']].round(2).to_string(index=False))
# ---------------- ③ 주봉 (1994~, 금요일 기준. 이번 주는 11/23~25 3일만의 미완성 주봉)
w=d[['high','low','close']].resample('W-FRI').agg({'high':'max','low':'min','close':'last'}).dropna()
w['h52']=w.high.rolling(52,min_periods=26).max(); w['dd']=w.low/w.h52-1; w['rsi']=rsi(w.close)
wh,wl,wc,wd,wr=w.high.values,w.low.values,w.close.values,w.dd.values,w.rsi.values; WN=len(w); wlr=np.log(w.close).diff().values
cur=WN-1
out.append(f"\n== ③ 주봉 (이번 주 = 11/23~25 미완성). 이번 주 고 {wh[cur]:.0f} 저 {wl[cur]:.0f} 종 {wc[cur]:.0f} | 지난주 저 {wl[cur-1]:.0f} 종 {wc[cur-1]:.0f} | 주봉 RSI {wr[cur]:.1f}")
wbear=[k for k in range(60,WN-1) if wd[k]<=-0.25]
wbase={h:np.mean([wc[k+h]<wc[k] for k in wbear if k+h<WN]) for h in (4,12)}
def wreport(nm,idx):
    rr=[]
    for k in idx:
        sg=np.nanstd(wlr[k-25:k+1],ddof=1)
        rr.append(dict(주=w.index[k].date(),재이탈4주=float(wl[k+1:k+5].min()<wl[k]) if k+4<WN else np.nan,RW4주=p_touch(log(wc[k]/wl[k]),sg,4),
                       재이탈12주=float(wl[k+1:k+13].min()<wl[k]) if k+12<WN else np.nan,RW12주=p_touch(log(wc[k]/wl[k]),sg,12),
                       r4=wc[k+4]/wc[k]-1 if k+4<WN else np.nan,r12=wc[k+12]/wc[k]-1 if k+12<WN else np.nan))
    X=pd.DataFrame(rr); line=f"  {nm}: {len(X)}건"
    if len(X)==0: out.append(line); return X
    for lab,a_,e_ in (('4주 안 재이탈','재이탈4주','RW4주'),('12주 안 재이탈','재이탈12주','RW12주')):
        P=X[X[a_].notna()]; line+=f" | {lab} 실제 {int(P[a_].sum())}/{len(P)} vs 변동성만 {P[e_].sum():.1f}"
    for h in (4,12):
        y=X[f'r{h}'].dropna(); k=int((y<0).sum()); m=len(y)
        line+=f" | {h}주 뒤 하락 {k}/{m} ({k/m:.0%}, 비교 {wbase[h]:.0%}, p={binom_p(k,m,wbase[h]):.2f}), 중앙 {np.median(y)*100:+.1f}%"
    out.append(line); return X
out.append(f"  비교 기준(52주 고점 대비 −25%↓ 모든 주 {len(wbear)}주): 4주 뒤 하락 {wbase[4]:.0%}, 12주 뒤 {wbase[12]:.0%}")
W1=wreport("주봉 스프링(지난주 저가를 깨고 지난주 종가 위 마감, 8주 신저가)",[k for k in wbear if wl[k]<wl[k-1] and wl[k]<=wl[k-8:k].min() and wc[k]>wc[k-1]])
def div(k):
    if wl[k]>wl[k-26:k].min(): return False
    prev=[j for j in range(k-26,k-3) if wl[j]<=wl[max(0,j-26):j].min()]
    return bool(prev) and wr[k]>wr[prev[-1]]+3
W2=wreport("주봉 RSI 상승 다이버전스(26주 신저가인데 RSI는 직전 신저가 때보다 3↑)",[k for k in wbear if div(k)])
out.append(f"  이번 주: 스프링 조건 {'충족' if (wl[cur]<wl[cur-1] and wc[cur]>wc[cur-1]) else '불충족'}, RSI 다이버전스 {'충족' if div(cur) else '불충족'} (미완성 주봉)")
open(f'{OUT}/g_more_tests.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
