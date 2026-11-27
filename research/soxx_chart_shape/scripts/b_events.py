# B. "지금과 같은 모양"이 과거 SOX 약세장에서 나왔을 때 그 뒤 결과 세기 (1994~2026, SOX 일봉)
#  B1 (비트코인 세션과 같은 틀, 장중 기준): 52주 고점 대비 −25% 이하에서 60일 신저가 L → 5일 안 +B 반등(고점 H=넥라인)
#      → 그 뒤 10일 안 L~L×(1+R) 재시험(L 미이탈) → 이후 'H 위 종가'가 먼저냐 'L 아래 장중'이 먼저냐
#  B2 (지금 단계): B1에서 L이 깨진 날(b)의 모양별로 그 뒤 결과. 11/25처럼 깨고 다시 L 위로 마감(스프링)한 경우를 따로 봄
#  B3 (넓은 스프링): 약세장에서 직전 저점(60일)을 장중에 깨고 그 저점 위로 마감, 두 저점 사이 +8% 이상 반등
#  B4 (종가 기준 B1): 종가로만 본 같은 모양. 지금은 종가 기준으로는 아직 안 깨짐
import sys; sys.path.insert(0,'scripts')
from common import *
DD=d.dd.values; DDC=d.ddc.values; POS=d.pos.values
def resolve(start,L,Hn,FW=120,low_arr=Lo,brk_close=False):
    """start부터 FW일: 첫 이탈(low<L, 또는 종가<L)과 첫 돌파(종가>Hn)"""
    e=min(N,start+FW); fb=fu=None
    for k in range(start,e):
        if fb is None and ((C[k]<L) if brk_close else (low_arr[k]<L)): fb=k
        if fu is None and C[k]>Hn: fu=k
        if fb is not None and fu is not None: break
    return fb,fu
def events_intraday(B=0.10,R=0.04,DTH=-0.25,LB=60,BW=5,RW=10,FW=120):
    ev=[]; blocked=-1
    for i in range(260,N):
        if i<blocked: continue
        L=Lo[i]
        if L>Lo[i-LB:i].min() or DD[i]>DTH: continue
        w_end=min(N,i+BW+1); j=i+int(np.argmax(H[i:w_end])); Hn=H[j]
        if Hn<L*(1+B): continue
        if Lo[i:j+1].min()<L: continue                      # 반등 전에 더 낮은 저점이 있으면 그날이 L
        rt=None
        for k in range(j+1,min(N,j+RW+1)):
            if Lo[k]<L: break
            if Lo[k]<=L*(1+R): rt=k; break
        if rt is None:
            if j+1>=N or (N-1-j<RW and Lo[j+1:].min()>=L): pass
            continue
        fb,fu=resolve(rt+1,L,Hn,FW)
        win=(fu is not None) and (fb is None or fu<fb)
        e=dict(i=i,j=j,rt=rt,fb=fb,fu=fu,L=L,Hn=Hn,win=win,저점일=IDX[i].date(),고점대비=DD[i],첫반등=Hn/L-1,재시험=Lo[rt]/L-1,
               재시험일=IDX[rt].date(),결과=("진행중" if fb is None and fu is None else ("넥라인 먼저" if win else "저점 먼저 깨짐")),
               이탈일수=(fb-rt) if fb is not None else None,금리=regime(IDX[i]),시대="2010~" if IDX[i].year>=2010 else "~2009")
        if fb is not None:
            e.update(깬날=IDX[fb].date(),깬깊이=Lo[fb]/L-1,깬날종가=C[fb]/L-1,깬날위치=POS[fb],
                     이탈후20일최저=Lo[fb:fb+20].min()/L-1,이탈후60일최저=Lo[fb:fb+60].min()/L-1,_120일최저=Lo[rt:rt+120].min()/L-1)
        ev.append(e)
        res=[x for x in (fb,fu) if x is not None]
        blocked=min(res) if res else N
    return pd.DataFrame(ev)
def after_break(E):
    """B2: 깨진 날 b 이후. 넥라인(H) 종가 돌파가 먼저냐, 깬 날 저점(Lb) 이탈이 먼저냐"""
    rows=[]
    for r in E[E.fb.notna()].itertuples():
        b=int(r.fb); Lb=Lo[b]
        fb2,fu2=resolve(b+1,Lb,r.Hn,120)
        win=(fu2 is not None) and (fb2 is None or fu2<fb2)
        lo60=Lo[b+1:b+61].min() if b+1<N else np.nan
        rows.append(dict(저점일=r.저점일,깬날=IDX[b].date(),깬깊이=Lb/r.L-1,깬날종가=C[b]/r.L-1,위치=POS[b],스프링=C[b]>=r.L,
            결과=("진행중" if fb2 is None and fu2 is None else ("넥라인 먼저" if win else "깬 날 저점도 깨짐")),
            재이탈일수=(fb2-b) if fb2 is not None else None,
            _60일최저_L대비=lo60/r.L-1 if lo60==lo60 else np.nan,_60일최저_Lb대비=lo60/Lb-1 if lo60==lo60 else np.nan,
            _120일최고=H[b+1:b+121].max()/Lb-1 if b+1<N else np.nan,금리=r.금리,시대=r.시대))
    return pd.DataFrame(rows)
def springs(B=0.08,LB=60,DTH=-0.25,need_close_above=True,minpos=0.0,FW=120):
    rows=[]; blocked=-1
    for b in range(260,N):
        if b<=blocked: continue
        if DD[b]>DTH: continue
        a=b-LB+int(np.argmin(Lo[b-LB:b])); m=Lo[a]
        if Lo[b]>=m: continue
        if b-a<3: continue
        Hn=H[a+1:b].max() if b-a>1 else np.nan
        if not Hn==Hn or Hn<m*(1+B): continue
        if need_close_above and C[b]<m: continue
        if POS[b]<minpos: continue
        fb,fu=resolve(b+1,Lo[b],Hn,FW)
        win=(fu is not None) and (fb is None or fu<fb)
        lo20=Lo[b+1:b+21].min() if b+1<N else np.nan; lo60=Lo[b+1:b+61].min() if b+1<N else np.nan
        rows.append(dict(b=b,날짜=IDX[b].date(),직전저점일=IDX[a].date(),사이반등=Hn/m-1,깬깊이=Lo[b]/m-1,종가_직전저점대비=C[b]/m-1,위치=POS[b],
            고점대비=DD[b],결과=("진행중" if fb is None and fu is None else ("넥라인 먼저" if win else "그날 저점도 깨짐")),
            재이탈일수=(fb-b) if fb is not None else None,돌파일수=(fu-b) if fu is not None else None,
            _20일최저=lo20/Lo[b]-1 if lo20==lo20 else np.nan,_60일최저=lo60/Lo[b]-1 if lo60==lo60 else np.nan,
            _60일최고=H[b+1:b+61].max()/C[b]-1 if b+1<N else np.nan,금리=regime(IDX[b]),시대="2010~" if IDX[b].year>=2010 else "~2009",VIX=d.vix.iloc[b]))
        res=[x for x in (fb,fu) if x is not None]; blocked=min(res) if res else N
    return pd.DataFrame(rows)
def events_close(B=0.10,R=0.06,DTH=-0.25,LB=60,BW=5,RW=10,FW=120):
    ev=[]; blocked=-1
    for i in range(260,N):
        if i<blocked: continue
        L=C[i]
        if L>C[i-LB:i].min() or DDC[i]>DTH: continue
        w_end=min(N,i+BW+1); j=i+int(np.argmax(C[i:w_end])); Hn=C[j]
        if Hn<L*(1+B) or C[i:j+1].min()<L: continue
        rt=None
        for k in range(j+1,min(N,j+RW+1)):
            if C[k]<L: break
            if C[k]<=L*(1+R): rt=k; break
        if rt is None: continue
        fb,fu=resolve(rt+1,L,Hn,FW,brk_close=True)
        win=(fu is not None) and (fb is None or fu<fb)
        ev.append(dict(i=i,저점일=IDX[i].date(),고점대비=DDC[i],첫반등=Hn/L-1,재시험일=IDX[rt].date(),재시험=C[rt]/L-1,
            결과=("진행중" if fb is None and fu is None else ("넥라인 먼저" if win else "저점 먼저 깨짐")),
            이탈일수=(fb-rt) if fb is not None else None,돌파일수=(fu-rt) if fu is not None else None,
            이탈후20일최저=(C[fb:fb+20].min()/L-1) if fb is not None else np.nan,_120일최저=C[rt:rt+120].min()/L-1,
            금리=regime(IDX[i]),시대="2010~" if IDX[i].year>=2010 else "~2009"))
        res=[x for x in (fb,fu) if x is not None]; blocked=min(res) if res else N
    return pd.DataFrame(ev)
pd.set_option('display.width',320); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',300)
def pct(df,cols):
    S=df.copy()
    for k in cols:
        if k in S: S[k]=(S[k].astype(float)*100).round(1)
    for k in ('위치','VIX'):
        if k in S: S[k]=S[k].astype(float).round(2)
    return S
def tally(df,lab="결과",win="넥라인 먼저"):
    x=df[df[lab]!="진행중"]; n=len(x); w=(x[lab]==win).sum()
    return f"{w}/{n} ({(w/n if n else np.nan):.0%})"
out=[]
# ---------- B1
E=events_intraday()
out.append("== B1. 비트코인 세션과 같은 틀 (장중 기준): 약세장 60일 신저가 L → 5일 안 +10% 반등 → 10일 안 +4% 안 재시험")
out.append(pct(E.drop(columns=['i','j','rt','fb','fu','L','Hn','win']),['고점대비','첫반등','재시험','깬깊이','깬날종가','이탈후20일최저','이탈후60일최저','_120일최저']).to_string(index=False))
P=E[E.결과!="진행중"]
out.append(f"\n  넥라인 먼저 = {tally(E)}  | 2010~ {tally(P[P.시대=='2010~'])} | ~2009 {tally(P[P.시대=='~2009'])} | 인상기 {tally(P[P.금리=='인상기'])} | 인하기 {tally(P[P.금리=='인하기'])} | 그 외 {tally(P[P.금리=='그 외'])}")
lost=P[P.결과=="저점 먼저 깨짐"]
out.append(f"  깨진 경우 {len(lost)}건: 재시험 뒤 이탈까지 중앙 {lost.이탈일수.median():.0f}거래일 (3일 안 {(lost.이탈일수<=3).sum()}건, 10일 안 {(lost.이탈일수<=10).sum()}건)")
out.append(st(lost.이탈후20일최저*100,"이탈 뒤 20일 최저 (L 대비)"))
out.append(st(lost.이탈후60일최저*100,"이탈 뒤 60일 최저 (L 대비)"))
out.append("\n  민감도 (넥라인 먼저 / 결론 난 전체):")
for b_ in (0.08,0.10,0.12,0.15):
    line=[]
    for r_ in (0.03,0.04,0.06):
        X=events_intraday(b_,r_); X=X[X.결과!="진행중"]; X=X[X.저점일<pd.Timestamp('2026-01-01').date()]
        line.append(f"재시험 ≤+{r_:.0%}: {int((X.결과=='넥라인 먼저').sum())}/{len(X)}")
    out.append(f"    첫 반등 ≥{b_:.0%} | "+" | ".join(line))
for dth in (-0.20,-0.30,-0.35):
    X=events_intraday(DTH=dth); X=X[(X.결과!="진행중")&(X.저점일<pd.Timestamp('2026-01-01').date())]
    out.append(f"    약세장 기준 {dth:.0%}: {int((X.결과=='넥라인 먼저').sum())}/{len(X)}")
# ---------- B2
A=after_break(E)
out.append("\n== B2. B1에서 저점이 깨진 날의 모양별 그 뒤 (깬 날 저점 Lb 기준)")
out.append(pct(A,['깬깊이','깬날종가','_60일최저_L대비','_60일최저_Lb대비','_120일최고']).to_string(index=False))
for nm,m in (("스프링(깬 날 L 위 마감)",A.스프링),("L 아래 마감",~A.스프링),("깬 날 위치≥0.8",A.위치>=0.8)):
    x=A[m]; out.append(f"  {nm}: {len(x)}건, 넥라인 먼저 {tally(x)}"+(f", 재이탈까지 중앙 {x.재이탈일수.median():.0f}일" if x.재이탈일수.notna().any() else ""))
    out.append(st(x._60일최저_Lb대비*100,"   60일 최저 (깬 날 저점 대비)"))
# ---------- B3
out.append("\n== B3. 넓은 스프링: 약세장(−25%↓)에서 60일 저점을 장중에 깨고 그 저점 위로 마감, 두 저점 사이 +8%↑ 반등")
S3=springs()
out.append(pct(S3.drop(columns=['b']),['사이반등','깬깊이','종가_직전저점대비','고점대비','_20일최저','_60일최저','_60일최고']).to_string(index=False))
P3=S3[S3.결과!="진행중"]
out.append(f"\n  넥라인 먼저 = {tally(S3)} | 2010~ {tally(P3[P3.시대=='2010~'])} | ~2009 {tally(P3[P3.시대=='~2009'])} | 인상기 {tally(P3[P3.금리=='인상기'])} | 인하기 {tally(P3[P3.금리=='인하기'])} | 그 외 {tally(P3[P3.금리=='그 외'])}")
lost3=P3[P3.결과=="그날 저점도 깨짐"]
out.append(f"  그날 저점도 깨진 {len(lost3)}건: 재이탈까지 중앙 {lost3.재이탈일수.median():.0f}거래일 (5일 안 {(lost3.재이탈일수<=5).sum()}, 10일 안 {(lost3.재이탈일수<=10).sum()}, 20일 안 {(lost3.재이탈일수<=20).sum()})")
out.append(st(P3._20일최저*100,"전체 20일 최저 (그날 저점 대비)"))
out.append(st(P3._60일최저*100,"전체 60일 최저 (그날 저점 대비)"))
out.append(st(lost3._60일최저*100,"깨진 경우 60일 최저"))
out.append(st(P3._60일최고*100,"전체 60일 최고 (그날 종가 대비)"))
won3=P3[P3.결과=="넥라인 먼저"]
if len(won3): out.append(f"  넥라인 먼저 {len(won3)}건: 돌파까지 중앙 {won3.돌파일수.median():.0f}거래일")
out.append("  민감도:")
for b_ in (0.05,0.08,0.12):
    for mp in (0.0,0.8):
        X=springs(B=b_,minpos=mp); X=X[(X.결과!="진행중")&(X.날짜<pd.Timestamp('2026-11-25').date())]
        out.append(f"    두 저점 사이 반등 ≥{b_:.0%}, 마감 위치 ≥{mp}: 넥라인 먼저 {int((X.결과=='넥라인 먼저').sum())}/{len(X)}")
X=springs(need_close_above=False,minpos=0.8); X=X[(X.결과!="진행중")]
out.append(f"    (직전 저점 위 마감 조건 없이, 위치 ≥0.8만): 넥라인 먼저 {int((X.결과=='넥라인 먼저').sum())}/{len(X)}")
for dth in (-0.35,-0.40):
    X=springs(DTH=dth); X=X[(X.결과!="진행중")]
    out.append(f"    약세장 기준 {dth:.0%}: 넥라인 먼저 {int((X.결과=='넥라인 먼저').sum())}/{len(X)}")
# ---------- B4
E4=events_close()
out.append("\n== B4. 종가 기준 같은 틀: 60일 최저 종가 L → 5일 안 종가 +10%↑ → 10일 안 종가 L~+6% 재시험")
out.append(pct(E4.drop(columns=['i']),['고점대비','첫반등','재시험','이탈후20일최저','_120일최저']).to_string(index=False))
P4=E4[E4.결과!="진행중"]
out.append(f"\n  넥라인 먼저 = {tally(E4)} | 2010~ {tally(P4[P4.시대=='2010~'])} | ~2009 {tally(P4[P4.시대=='~2009'])} | 인상기 {tally(P4[P4.금리=='인상기'])} | 인하기 {tally(P4[P4.금리=='인하기'])}")
l4=P4[P4.결과=="저점 먼저 깨짐"]
out.append(f"  깨진 경우: 이탈까지 중앙 {l4.이탈일수.median():.0f}거래일 (5일 안 {(l4.이탈일수<=5).sum()}, 10일 안 {(l4.이탈일수<=10).sum()})")
out.append(st(l4.이탈후20일최저*100,"이탈 뒤 20일 최저 종가 (L 대비)"))
out.append("  민감도:")
for b_ in (0.08,0.10,0.12):
    line=[]
    for r_ in (0.04,0.06,0.08):
        X=events_close(b_,r_); X=X[X.결과!="진행중"]
        line.append(f"재시험 ≤+{r_:.0%}: {int((X.결과=='넥라인 먼저').sum())}/{len(X)}")
    out.append(f"    첫 반등 ≥{b_:.0%} | "+" | ".join(line))
E.to_csv(f'{OUT}/b1_events.csv',index=False); A.to_csv(f'{OUT}/b2_after_break.csv',index=False)
S3.to_csv(f'{OUT}/b3_springs.csv',index=False); E4.to_csv(f'{OUT}/b4_close.csv',index=False)
open(f'{OUT}/b_events.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
# ---------- B5. 깨진 경우, 그 '한 번 더 깨짐'이 최종 사이클 바닥으로 이어졌나 (사이클 바닥 ±: 재이탈 뒤 30거래일 안)
CB=pd.to_datetime(['1996-07-16','1998-10-08','2002-10-08','2004-09-08','2006-07-21','2008-11-21','2011-10-04','2016-02-11','2018-12-24','2020-03-18','2022-10-13','2025-04-07'])
cbi=[IDX.get_indexer([t],method='nearest')[0] for t in CB]
out2=["\n== B5. 넓은 스프링(B3) 결말을 셋으로 나눔"]
rows=[]
for r in S3[S3.결과!="진행중"].itertuples():
    b=int(r.b)
    if r.결과=="넥라인 먼저":
        cyc_self=any(abs(b-k)<=3 for k in cbi); kind="넥라인 먼저"+(" (그날이 사이클 바닥)" if cyc_self else "")
    else:
        fb=b+int(r.재이탈일수); near=[k for k in cbi if fb<=k<=fb+30]
        kind="한 번 더 깨진 뒤 30일 안 사이클 바닥" if near else "한 번 더 깨진 뒤 하락 지속"
        if near: kind+=f" ({IDX[near[0]].date()}, 그날 저점 대비 {Lo[near[0]]/Lo[b]-1:+.1%})"
    rows.append((r.날짜,r.위치,kind)); out2.append(f"  {r.날짜} 위치 {r.위치:.2f} → {kind}")
k=pd.Series([x[2].split(' (')[0] for x in rows]).value_counts()
out2.append("  집계: "+", ".join(f"{a} {b}건" for a,b in k.items()))
open(f'{OUT}/b_events.txt','a').write('\n'.join(out2)+'\n'); print('\n'.join(out2))
