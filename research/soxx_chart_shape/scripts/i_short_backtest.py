# I. 숏(SOXS)을 과거 스프링 16번에 대입 — 스프링 날 종가(지금 = 11/25 종가)에 결정
#  SOXS: 2010-06 전 SOX×(−3) 합성, 이후 실제 SOXS (재검증 base.py). 장중 체결가 ≈ 전일 SOXS × (1 − 3×(SOX 체결가/전일 SOX − 1))
import sys, os; sys.path.insert(0,'scripts'); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','scripts','reverify_20261124'))
from common import *
import base as B
CS=B.CS
def sx(t): return float(CS.asof(t))
def sxs_at(k,lv):                     # k일 SOX가 lv에 닿았을 때 SOXS 값
    return sx(IDX[k-1])*(1-3*(lv/C[k-1]-1))
O=d.open.values
def opn_ok(k): return IDX[k]>=pd.Timestamp('2005-01-01')
S=pd.read_csv(f'{OUT}/b3_springs.csv',parse_dates=['날짜']); S=S[S.결과!='진행중'].reset_index(drop=True)
VOL4=pd.to_datetime(['2011-08-09','2018-10-30','2020-03-17','2025-04-09'])
def neck(b):
    a=b-60+int(np.argmin(Lo[b-60:b])); return H[a+1:b].max() if b-a>1 else H[a:b].max()
def trade(b,entry_up=None,maxd=20,tgt_k=0.0,use_stop=True):
    """entry_up=None: 스프링 날 종가에 SOXS 진입. entry_up=x: 10일 안 SOX가 종가×(1+x)에 닿으면 그때 진입(미체결=0).
       목표: SOX 장중이 스프링 저점×(1−tgt_k)에 닿으면 청산. 손절: SOX 종가 > 넥라인. 기한: 진입 뒤 maxd거래일 종가."""
    Lb=Lo[b]; nk=neck(b); tgt=Lb*(1-tgt_k)
    if entry_up is None: e=b; px_in=sx(IDX[b])
    else:
        lv=C[b]*(1+entry_up); e=next((k for k in range(b+1,min(N,b+11)) if H[k]>=lv),None)
        if e is None: return 0.0,'미진입'
        px_in=sxs_at(e,max(lv,O[e]) if opn_ok(e) and O[e]>lv else lv) if True else None
        if opn_ok(e) and O[e]>lv: px_in=sxs_at(e,O[e])
        if Lo[e]<=tgt: return sxs_at(e,tgt)/px_in-1,'목표(당일)'
    for k in range(e+1,min(N,e+maxd+1)):
        if Lo[k]<=tgt:
            lvx=O[k] if (opn_ok(k) and O[k]<tgt) else tgt
            return sxs_at(k,lvx)/px_in-1,'목표'
        if use_stop and C[k]>nk: return sx(IDX[k])/px_in-1,'손절'
    k=min(N-1,e+maxd); return sx(IDX[k])/px_in-1,'기한'
def hold(b,h): return sx(IDX[b+h])/sx(IDX[b])-1 if b+h<N else np.nan
STRATS=[('1 지금 종가 SOXS, 3일 보유',lambda b:(hold(b,3),'')),
        ('2 지금 종가 SOXS, 20일 보유',lambda b:(hold(b,20),'')),
        ('3 지금 진입·목표 스프링 저점·손절 넥라인·20일',lambda b:trade(b)),
        ('4 지금 진입·목표 저점·손절 넥라인·3일 (VIX 규칙)',lambda b:trade(b,maxd=3)),
        ('5 +5% 반등 때 진입·목표 저점·손절 넥라인·20일',lambda b:trade(b,entry_up=0.05)),
        ('6 +8% 반등 때 진입·목표 저점·손절 넥라인·20일',lambda b:trade(b,entry_up=0.08)),
        ('7 지금 진입·목표 저점 −6%·손절 넥라인·20일',lambda b:trade(b,tgt_k=0.06))]
def summ(x,nm):
    x=np.array([v for v in x if v==v])*100; n=len(x); xs=np.sort(x); ex=xs[:-3].mean() if n>3 else np.nan
    return f"  {nm:40s} {n:2d}건 | 이익 {(x>0).mean():4.0%} | 중앙 {np.median(x):+6.1f}% | 상위3뺀 {ex:+6.1f}% | 평균 {x.mean():+6.1f}% | 최악 {x.min():+6.1f}% | 최고 {x.max():+6.1f}%"
out=["== 숏(SOXS)을 과거 스프링 16번에 대입 (결정 = 스프링 날 종가, 미진입 = 0%)"]
bidx=[int(b) for b in S.b]
tab={}
for nm,f in STRATS:
    res=[f(b) for b in bidx]; tab[nm]=res
    out.append(summ([r[0] for r in res],nm)+("" if not res[0][1] else " | 결말: "+", ".join(f"{k} {v}" for k,v in pd.Series([r[1] for r in res]).value_counts().items())))
for lab,sel in (('2010년 이후 5건',[b for b in bidx if IDX[b]>=pd.Timestamp('2010-01-01')]),('투매 뒤 스프링 4건 (지금과 같은 순서)',[IDX.get_loc(t) for t in VOL4])):
    out.append(f"\n  [{lab}]")
    for nm,f in STRATS:
        res=[f(b) for b in sel]; out.append(summ([r[0] for r in res],nm))
show=pd.DataFrame({nm[:2].strip():[round(r[0]*100,1) for r in tab[nm]] for nm,_ in STRATS},index=[IDX[b].date() for b in bidx])
out.append("\n  사례별 (%)  열 번호 = 위 방법 번호\n"+show.to_string())
# 지금 가격
s0=62.13; c0=C[-1]
out.append(f"\n== 지금 가격 (SOXS 11/25 종가 {s0}): SOX 8,129(스프링 저점) 닿으면 SOXS ≈ {s0*(1-3*(8129.23/c0-1)):.1f} / SOX 7,641(−6%) ≈ {s0*(1-3*(7641/c0-1)):.1f} / SOX +5%(9,214) 반등 때 진입가 ≈ {s0*(1-3*0.05):.1f} / 넥라인 9,728 종가면 SOXS ≈ {s0*(1-3*(9728.12/c0-1)):.1f}  (하루 만에 닿는다고 본 근사)")
open(f'{OUT}/i_short_backtest.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
