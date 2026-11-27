# V. "지금과 같은 모양"이 과거 약세장에서 나왔을 때 그 뒤 결과 세기 (2013~2026, BTC 일봉)
#  모양: 약세장(고점 대비 −40% 이하) 저점 L → 5일 안 +12% 이상 첫 반등 → 그 뒤 10일 안 L~L×1.06 재시험(L 미이탈)
import sys; sys.path.insert(0,'scripts')
from u_chart_shape import *
D=pd.Timedelta
bs=daily('BTC_BS')['2013-01-01':'2017-12-31']; bn=daily('BTC')['2018-01-01':]
d=pd.concat([bs,bn])[['o','h','l','c']]
ath=d.h.cummax()
old=pd.read_csv('data/ext/BTC_ONCHAIN.csv',parse_dates=['date']).set_index('date')
cmb=pd.read_csv('data/ext/CM_BTC_REALIZED.csv',parse_dates=['date']).set_index('date')
rp=pd.concat([old.realized_price[old.index<cmb.index[0]],cmb.realized_price]).sort_index()
CYCLE={pd.Timestamp('2015-01-14'),pd.Timestamp('2018-12-15'),pd.Timestamp('2020-03-13'),pd.Timestamp('2022-11-21')}
idx=d.index
def events(BOUNCE=0.12,RET=0.06,DD=0.60):
  ev=[]; last=None
  for i,t in enumerate(idx):
      if i<60 or i>len(idx)-2: continue
      L=d.l.iloc[i]
      if L>d.l.iloc[i-60:i].min(): continue                      # 직전 60일 신저가
      if L>ath.iloc[i]*DD: continue                           # 고점 대비 −40% 이하
      if last is not None and t-last<D(days=30): continue
      w=d.iloc[i:i+6]
      if w.h.max()<L*(1+BOUNCE): continue                             # 5일 안 +12% 첫 반등
      hb=w.h.idxmax(); H=w.h.max(); j=idx.get_loc(hb)
      r=d.iloc[j+1:j+11]
      if len(r)==0: continue
      brk=r[r.l<L]; ok=r[(r.l>=L)&(r.l<=L*(1+RET))]
      if len(ok)==0: continue
      rt=ok.index[0]
      if len(brk) and brk.index[0]<=rt: continue                 # 재시험 전에 이미 깨졌으면 제외
      k=idx.get_loc(rt); f=d.iloc[k+1:k+121]
      br=f[f.l<L]; up=f[f.c>H]
      first_break=br.index[0] if len(br) else None; first_up=up.index[0] if len(up) else None
      win=(first_up is not None) and (first_break is None or first_up<first_break)
      nxt_low=f.l.min()
      ev.append(dict(저점일=t.date(),저점=L,고점대비=L/ath.iloc[i]-1,MVRV=L/rp.asof(t),첫반등=H/L-1,재시험일=rt.date(),재시험=d.l[rt]/L-1,
                     넥라인먼저돌파=win,이탈일수=(first_break-rt).days if first_break is not None else None,
                     돌파일수=(first_up-rt).days if first_up is not None else None,
                     _120일최저=nxt_low/L-1,이탈후30일최저=(d.l[first_break:first_break+D(days=30)].min()/L-1) if first_break is not None else np.nan,_120일최고=f.h.max()/L-1,사이클바닥=t.normalize() in CYCLE))
      last=t
  return pd.DataFrame(ev)
E=events()
pd.set_option('display.width',250)
S=E.copy()
for k in ['고점대비','첫반등','재시험','_120일최저','_120일최고']: S[k]=(S[k]*100).round(0)
S['MVRV']=S.MVRV.round(2)
out=["== 지금과 같은 모양(약세장 신저가 → 5일 안 +12% 반등 → 10일 안 +6% 안 재시험)이 나온 경우",S.to_string(index=False)]
H_=E[E.저점일<pd.Timestamp('2026-01-01').date()]; n=len(H_); w=H_.넥라인먼저돌파.sum()
out.append(f"\n과거 {n}건 (2026 제외): 넥라인(첫 반등 고점) 종가 돌파가 저점 이탈보다 먼저 = {w}건 ({w/n:.0%}), 저점이 먼저 깨짐 = {n-w}건")
for lab,m in [('실현가격 위(MVRV≥1)',E.MVRV>=1),('실현가격 아래(MVRV<1)',E.MVRV<1)]:
    x=H_[m.loc[H_.index]]; 
    if len(x): out.append(f"  {lab}: {len(x)}건 중 넥라인 먼저 {x.넥라인먼저돌파.sum()}건, 사이클 바닥 {x.사이클바닥.sum()}건")
lost=H_[~H_.넥라인먼저돌파]
if len(lost):
    out.append(f"저점이 깨진 경우: 이탈까지 중앙 {lost.이탈일수.median():.0f}일 (7일 안 {(lost.이탈일수<=7).sum()}건, 30일 안 {(lost.이탈일수<=30).sum()}건)")
    out.append(f"  이탈 뒤 30일 안 최저(원래 저점 대비): 중앙 {lost.이탈후30일최저.median()*100:.0f}%, " + ", ".join(f"{r.저점일}:{r.이탈후30일최저*100:.0f}%" for r in lost.itertuples()))
    out.append(f"  120일 안 최저: 중앙 {lost._120일최저.median()*100:.0f}% (범위 {lost._120일최저.min()*100:.0f}~{lost._120일최저.max()*100:.0f}%)")
won=H_[H_.넥라인먼저돌파]
if len(won): out.append(f"넥라인이 먼저인 경우: 돌파까지 중앙 {won.돌파일수.median():.0f}일, 그 뒤에도 120일 안에 저점이 깨진 건 {(won._120일최저<0).sum()}건")
out.append("\n== 민감도: 기준을 바꿔도 같은가 (과거만, 넥라인 먼저 / 전체)")
for b_ in (0.10,0.12,0.15):
    for r_ in (0.04,0.06,0.08):
        X=events(b_,r_); X=X[X.저점일<pd.Timestamp('2026-01-01').date()]
        out.append(f"  첫 반등 ≥{b_:.0%}, 재시험 ≤+{r_:.0%}: {int(X.넥라인먼저돌파.sum())}/{len(X)}")
# 약세장 주요 저점(28건 비교군)의 MVRV
out.append("\n== 비교군: 약세장 주요 저점 중 실현가격 위에서 찍은 저점이 사이클 바닥이었던 적")
lows=[]
for i,t in enumerate(idx):
    if i<60 or i+30>=len(idx): continue
    L=d.l.iloc[i]
    if L<=d.l.iloc[i-60:i+31].min() and L<=ath.iloc[i]*0.55 and d.h.iloc[i:i+61].max()>=L*1.2: lows.append((t,L,L/rp.asof(t)))
Lw=pd.DataFrame(lows,columns=['t','L','mvrv']); Lw['cyc']=Lw.t.dt.normalize().isin(CYCLE)
out.append(f"  고점 대비 −45% 이하·이후 +20% 반등 저점 {len(Lw)}건: MVRV≥1 {int((Lw.mvrv>=1).sum())}건 중 사이클 바닥 {int(Lw[Lw.mvrv>=1].cyc.sum())}건 / MVRV<1 {int((Lw.mvrv<1).sum())}건 중 사이클 바닥 {int(Lw[Lw.mvrv<1].cyc.sum())}건")
out.append("  "+", ".join(f"{r.t.date()}({r.mvrv:.2f}{'★' if r.cyc else ''})" for r in Lw.itertuples()))
open('output/v_w_odds.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
# 생존 조건부: 재시험 뒤 2일 안 안 깨진 경우
X=events(); X=X[X.저점일<pd.Timestamp('2026-01-01').date()]
sv_=X[(X.이탈일수.isna())|(X.이탈일수>2)]
extra=[f"\n== 재시험 뒤 2일 동안 안 깨진 경우만: {len(sv_)}건 중 그 뒤 깨진 것 {int((~sv_.넥라인먼저돌파).sum())}건"]
# 2026 수준 환산 (BTC 저점 55,130 기준) + SOL·SOLT (3주 경로, 11/25 종가 기준)
b_now=m1('BTC').c.iloc[-1]; s_now=m1('SOL').c.iloc[-1]; P0,S0=24.82,70.62; fair=P0*(1+2*(s_now/S0-1))
sv=np.log(m1('SOL').c.resample('D').last()).diff().dropna()[-60:].std()*np.sqrt(365)
def sol(b,k=1.45): return s_now*np.exp(k*np.log(b/b_now))
def solt(S,T=21,c=0.10): return fair*(S/s_now)**2*np.exp(-(sv**2+c)*T/365)
extra.append(f"== 2026 환산 (현재 BTC ${b_now:,.0f}, SOL ${s_now:.2f}, SOLT 이론가 ${fair:.2f})")
for lab,k in [('깨진 뒤 −1% (2022-11, 2023-08형)',-0.01),('중앙 −6%',-0.06),('−12% (2022-06형)',-0.12),('−17% (2022-01형)',-0.17),('−27% (2018-11형)',-0.27),('−40% (2015-01형)',-0.40)]:
    b=55130*(1+k); S=sol(b)
    extra.append(f"  {lab}: BTC ${b:,.0f} → SOL ${S:.1f} ({sol(b,1.8):.1f}~{sol(b,1.0):.1f}) → SOLT ≈ ${solt(S):.1f} ({solt(sol(b,1.8)):.1f}~{solt(sol(b,1.0)):.1f})")
open('output/v_w_odds.txt','a').write('\n'.join(extra)+'\n'); print('\n'.join(extra))
