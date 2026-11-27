# H. 최종: 최초 결론 vs 재분석 결론을 과거 같은 자리(스프링 16번)에 대입
#  (1) 주장 채점  (2) 그대로 따랐으면 SOXL 손익 (2010-06 전은 SOX×3 합성 SOXL, 이후 실제 SOXL; 재검증 base.py 사용)
import sys, os; sys.path.insert(0,'scripts'); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','scripts','reverify_20261124'))
from common import *
import base as B
CLs=B.CL; OPs=B.OL
S=pd.read_csv(f'{OUT}/b3_springs.csv',parse_dates=['날짜']); S=S[S.결과!='진행중'].reset_index(drop=True)
VOL4=pd.to_datetime(['2011-08-09','2018-10-30','2020-03-17','2025-04-09'])     # 투매 뒤 스프링 (g_more_tests)
def soxl_at(t): return float(CLs.asof(t))
def soxl_fill(k,lv):
    """k일에 SOX가 lv에 닿았을 때 SOXL 체결가 ≈ 전일 SOXL × (1 + 3×(lv/전일 SOX − 1)); 시가가 이미 lv 아래면 시가 기준"""
    t=IDX[k]; tp=IDX[k-1]; px=lv
    o=d.open.iloc[k]
    if t>=pd.Timestamp('2005-01-01') and o<lv: px=o
    return soxl_at(tp)*(1+3*(px/C[k-1]-1))
def run(idx_list,H):
    res={}
    for i in idx_list:
        e=min(N-1,i+H)
        if i+H>=N: continue
        buy=soxl_at(IDX[i]); sell=soxl_at(IDX[e])
        r_now=sell/buy-1
        out={}
        out['A 지금 종가 매수']=r_now
        for nm,k_ in (('B 스프링 저점 지정가',0.0),('C 스프링 저점 −6% 지정가',0.06),('D 스프링 저점 −12% 지정가',0.12)):
            lv=Lo[i]*(1-k_); f=next((k for k in range(i+1,min(N,i+21)) if Lo[k]<=lv),None)
            out[nm]=(sell/soxl_fill(f,lv)-1) if f is not None and f<e else 0.0
            out[nm+'_체결']=f is not None and f<e
        out['E 절반 지금 + 절반 −6%']=0.5*out['A 지금 종가 매수']+0.5*out['C 스프링 저점 −6% 지정가']
        res[IDX[i].date()]=out
    return pd.DataFrame(res).T
def summ(df,col):
    x=np.sort(df[col].astype(float).values*100); n=len(x)
    ex=x[:-3].mean() if n>3 else np.nan
    fill=f", 체결 {int(df[col+'_체결'].sum())}/{n}" if col+'_체결' in df else ""
    return f"  {col:22s} {n:2d}건{fill} | 이익 {(x>0).mean():4.0%} | 중앙 {np.median(x):+6.1f}% | 상위3뺀 {ex:+6.1f}% | 평균 {x.mean():+6.1f}% | 최악 {x.min():+6.1f}% | 최고 {x.max():+6.1f}%"
out=[]
# (1) 주장 채점
r20=[C[int(b)+20]/C[int(b)]-1 for b in S.b if int(b)+20<N]; r60=[C[int(b)+60]/C[int(b)]-1 for b in S.b if int(b)+60<N]
lo60=[Lo[int(b)+1:int(b)+61].min()/Lo[int(b)]-1 for b in S.b]
hit=[Lo[int(b)+1:int(b)+21].min()<Lo[int(b)] for b in S.b]
out.append("== (1) 주장 채점: 과거 스프링 16번에서 실제로 어땠나")
out.append(f"  최초 '20일 안 저점 재이탈 약 70%' → 실제 {sum(hit)}/{len(hit)} ({np.mean(hit):.0%})")
out.append(f"  최초 '넥라인보다 저점 먼저 70~80%' → 실제 {int((S.결과!='넥라인 먼저').sum())}/{len(S)} ({(S.결과!='넥라인 먼저').mean():.0%}); 재분석 '약 60%'")
out.append(f"  최초 '몇 주 아래쪽 유력' → 20일 뒤 더 낮음 {sum(np.array(r20)<0)}/{len(r20)} ({np.mean(np.array(r20)<0):.0%}), 60일 뒤 {sum(np.array(r60)<0)}/{len(r60)} ({np.mean(np.array(r60)<0):.0%}); 재분석 '반반'")
out.append(f"  최초 '깨지면 스프링 저점 대비 중앙 −6~−12%' → 60일 안 최저 중앙 {np.median(lo60)*100:+.1f}% (−6% 이하 {sum(np.array(lo60)<=-0.06)}/{len(lo60)}, −12% 이하 {sum(np.array(lo60)<=-0.12)}/{len(lo60)})")
# (2) SOXL 손익
bidx=[int(b) for b in S.b]
for H in (20,60):
    T=run(bidx,H)
    out.append(f"\n== (2) 그대로 따랐으면: SOXL, 스프링 날 종가에 결정, {H}거래일 뒤 종가에 평가 (미체결 = 현금 0%)")
    for col in ('A 지금 종가 매수','B 스프링 저점 지정가','C 스프링 저점 −6% 지정가','D 스프링 저점 −12% 지정가','E 절반 지금 + 절반 −6%'): out.append(summ(T,col))
    T2=T[[pd.Timestamp(x)>=pd.Timestamp('2010-01-01') for x in T.index]]
    out.append(f"  [2010년 이후 {len(T2)}건] "+" / ".join(f"{c[:1]} 중앙 {np.median(T2[c].astype(float))*100:+.1f}%·평균 {T2[c].astype(float).mean()*100:+.1f}%" for c in ('A 지금 종가 매수','B 스프링 저점 지정가','C 스프링 저점 −6% 지정가','E 절반 지금 + 절반 −6%')))
    tv=run([IDX.get_loc(t) for t in VOL4],H)
    out.append(f"  [투매 뒤 스프링 4건 — 지금과 같은 순서] "+" / ".join(f"{c[:1]} 중앙 {np.median(tv[c].astype(float))*100:+.1f}%·최악 {tv[c].astype(float).min()*100:+.1f}%" for c in ('A 지금 종가 매수','B 스프링 저점 지정가','C 스프링 저점 −6% 지정가','E 절반 지금 + 절반 −6%')))
    if H==60:
        show=(T[[c for c in T.columns if not c.endswith('_체결')]].astype(float)*100).round(1)
        out.append("\n  사례별 (60일, %)\n"+show.to_string())
# 지금 가격으로
out.append(f"\n== 지금 가격: SOX 스프링 저점 8,129 → SOXL 약 24.9 / −6%(SOX 7,641) → SOXL 약 19.7~21 / −12%(SOX 7,154) → SOXL 약 16~17 (d_levels.txt)")
open(f'{OUT}/h_final_backtest.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
