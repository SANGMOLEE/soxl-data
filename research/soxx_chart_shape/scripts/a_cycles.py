# A. 큰 그림: SOX 사이클마다 ① 첫 주요 저점 → ② 약세장 반등 → ③ 첫 저점 붕괴 → 최종 바닥 → ④ 넥라인 돌파
import sys; sys.path.insert(0,'scripts')
from common import *
def zigzag(c,th):
    piv=[(0,'?')]; hi=lo=0; trend=0
    for i in range(1,len(c)):
        if trend>=0:
            if c[i]>c[hi]: hi=i
            if c[i]<=c[hi]*(1-th): piv.append((hi,'H')); lo=i; trend=-1
        if trend<0:
            if c[i]<c[lo]: lo=i
            if c[i]>=c[lo]*(1+th): piv.append((lo,'L')); hi=i; trend=1
    return piv[1:]
# 1) 사이클 고점·바닥 (종가 25% 지그재그)
pv=zigzag(C,0.25)
cyc=[(pv[k][0],pv[k+1][0]) for k in range(len(pv)-1) if pv[k][1]=='H' and pv[k+1][1]=='L']
out=["== SOX 종가 25% 지그재그로 잡은 사이클 (고점 → 바닥)"]
for a,b in cyc: out.append(f"  {IDX[a].date()} {C[a]:9.1f} → {IDX[b].date()} {C[b]:9.1f}  {C[b]/C[a]-1:+.1%}  {(IDX[b]-IDX[a]).days/30.44:.1f}개월")
# 2010년 이후는 보고서 표의 날짜로 고정, 그 전은 지그재그 결과 사용
use=[(IDX[a],IDX[b]) for a,b in cyc if IDX[b]<pd.Timestamp('2010-01-01')]+[(pd.Timestamp(a),pd.Timestamp(b)) for a,b in CYC10]
rows=[]
for pk,bt in use:
    a=IDX.get_loc(pk); b=IDX.get_loc(bt)
    seg=C[a:b+1]
    # 고점~바닥 안의 흔들림: 종가 10% 지그재그
    z=zigzag(seg,0.10); lows=[(a+i) for i,t in z if t=='L']+[b]
    lows=sorted(set(lows))
    # ① 첫 주요 저점: 고점 대비 -20% 이하인 첫 흔들림 저점
    first=next((i for i in lows if C[i]/C[a]-1<=-0.20),b)
    # ② 첫 저점 뒤 약세장 반등 (첫 저점 ~ 최종 바닥 사이 최고 종가)
    if first<b:
        k=first+int(np.argmax(C[first:b+1])); rally=C[k]/C[first]-1
        brk=next((i for i in range(k,b+1) if C[i]<C[first]),None)
    else: k=None; rally=np.nan; brk=None
    # ④ 넥라인: 최종 바닥 뒤 첫 반등 고점(종가 8% 지그재그의 첫 H)
    post=C[b:min(N,b+400)]; z2=zigzag(post,0.08)
    nk=next((b+i for i,t in z2 if t=='H'),None)
    nb=next((i for i in range(nk+1,N) if C[i]>C[nk]),None) if nk is not None else None
    # 바닥 모양: 바닥 ±40일 안에 바닥 대비 +3% 이내 다른 저점(사이에 +8% 이상 반등) → 이중바닥
    w=[]; 
    for j in range(max(a,b-40),min(N,b+41)):
        if abs(j-b)<5: continue
        if Lo[j]<=Lo[b]*1.03 and Lo[j]<=Lo[max(0,j-3):j+4].min()+1e-9:
            mid=H[min(j,b):max(j,b)+1].max()
            if mid>=Lo[b]*1.08: w.append(j)
    shape="이중바닥(W)" if w else "단일 바닥(V)"
    r5=C[b]/C[max(0,b-5)]-1
    rows.append(dict(고점=pk.date(),바닥=bt.date(),낙폭=C[b]/C[a]-1,개월=(bt-pk).days/30.44,
        첫저점=IDX[first].date(),첫저점낙폭=C[first]/C[a]-1,첫저점뒤반등=rally,
        붕괴일=IDX[brk].date() if brk is not None else None,
        붕괴후바닥까지일=(bt-IDX[brk]).days if brk is not None else None,
        첫저점대비=C[b]/C[first]-1 if first<b else 0.0,
        모양=shape,짝저점=",".join(str(IDX[j].date()) for j in w[:3]),
        바닥전5일=r5,바닥RSI=d.rsi.iloc[b],바닥VIX=d.vix.iloc[b],
        넥라인=IDX[nk].date() if nk else None,넥라인돌파일=IDX[nb].date() if nb else None,
        돌파때바닥대비=C[nb]/C[b]-1 if nb else np.nan,돌파까지일=(IDX[nb]-bt).days if nb else None,
        _200주선비=C[b]/d.ma200w.iloc[b] if d.ma200w.iloc[b]==d.ma200w.iloc[b] else np.nan,
        금리=regime(bt),시대="2010~" if bt.year>=2010 else "~2009"))
R=pd.DataFrame(rows)
# 이번 사이클
a=IDX.get_loc(pd.Timestamp(NOW_PEAK)); b=N-1
seg=C[a:]; z=zigzag(seg,0.10)
out.append("\n== 이번 사이클 고점 뒤 흔들림 (종가 10% 지그재그)")
for i,t in z: out.append(f"  {t} {IDX[a+i].date()} {C[a+i]:9.1f} ({C[a+i]/C[a]-1:+.1%})")
lowc=a+int(np.argmin(C[a:])); out.append(f"  최저 종가 {IDX[lowc].date()} {C[lowc]:.1f} ({C[lowc]/C[a]-1:+.1%}), 최저 장중 {IDX[a+int(np.argmin(Lo[a:]))].date()} {Lo[a:].min():.1f}, 지금 {IDX[-1].date()} {C[-1]:.1f}")
first=next(a+i for i,t in z if t=='L' and C[a+i]/C[a]-1<=-0.20)
k=first+int(np.argmax(C[first:])); brk=next(i for i in range(k,N) if C[i]<C[first])
out.append(f"  ① 첫 주요 저점 {IDX[first].date()} {C[first]:.1f} ({C[first]/C[a]-1:+.1%}) → ② 반등 고점 {IDX[k].date()} {C[k]:.1f} (+{C[k]/C[first]-1:.1%}) → ③ 첫 저점 종가 붕괴 {IDX[brk].date()} → 지금까지 첫 저점 대비 {C[lowc]/C[first]-1:+.1%}, 붕괴 뒤 {(IDX[-1]-IDX[brk]).days}일")
out.append(f"  200주선 {d.ma200w.iloc[-1]:.0f}, 지금 종가 비율 {C[-1]/d.ma200w.iloc[-1]:.2f}, 11/20 종가 비율 {C[lowc]/d.ma200w.iloc[lowc]:.2f}, 고점 비율 {C[a]/d.ma200w.iloc[a]:.2f}")
pd.set_option('display.width',300); pd.set_option('display.max_columns',40)
S=R.copy()
for k_ in ['낙폭','첫저점낙폭','첫저점뒤반등','첫저점대비','바닥전5일','돌파때바닥대비']: S[k_]=(S[k_]*100).round(1)
for k_ in ['개월','바닥RSI','바닥VIX','_200주선비']: S[k_]=S[k_].round(2)
out.append("\n== 역대 사이클 4단계 표\n"+S.to_string(index=False))
# 고점 과열도(200주선 비율)와 바닥 200주선 비율
pk_ratio=[C[IDX.get_loc(pd.Timestamp(p))]/d.ma200w.loc[pd.Timestamp(p)] for p in R.고점.astype(str)]
out.append("\n== 고점 때 200주선 비율 → 바닥 때 200주선 비율")
for (p,bt_,br),pr in zip(R[['고점','바닥','_200주선비']].values,pk_ratio): out.append(f"  {p}  고점 {pr:.2f} → 바닥 {br:.2f}")
out.append(f"  이번  고점 {C[a]/d.ma200w.iloc[a]:.2f} → 지금 {C[-1]/d.ma200w.iloc[-1]:.2f}")
R.to_csv(f'{OUT}/a_cycles.csv',index=False)
open(f'{OUT}/a_cycles.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
