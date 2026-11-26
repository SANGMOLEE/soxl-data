# U2. 최종 바닥 직전·직후의 스윙 구조 (1시간봉 지그재그) — 충격 저점, 급반등(H1), 재시험(L1), 넥라인 돌파
import sys; sys.path.insert(0,'scripts')
from common import *
from u_chart_shape import daily, rsi, CASES
pd.set_option('display.width',250); pd.set_option('display.max_columns',40)
BSH=pd.read_csv('data/ext/BTC_BITSTAMP_1H.csv.gz',parse_dates=['date']).set_index('date').rename(columns={'open':'o','high':'h','low':'l','close':'c','volume':'v'})
def h4(sym):
    if sym=='BTC_BS': return BSH[['o','h','l','c','v']]
    return bars(sym,'1h').tz_localize(None)[['o','h','l','c','v']]
def zigzag(df,th):
    """확정된 피벗 [(종류, 시각, 가격)]. 반전 판정은 '이전 봉까지의 극값' 기준(같은 봉 안 고·저 순서 모호성 회피)"""
    piv=[]; it=df.itertuples(); f=next(it); lo,lot,hi,hit=f.l,f.Index,f.h,f.Index; mode=None
    for r in it:
        t=r.Index
        if mode in (None,'up') and r.l<=hi*(1-th) and (mode=='up' or hit>lot):
            piv.append(('H',hit,hi)); mode='dn'; lo,lot=r.l,t; continue
        if mode in (None,'dn') and r.h>=lo*(1+th) and (mode=='dn' or lot>=hit):
            piv.append(('L',lot,lo)); mode='up'; hi,hit=r.h,t; continue
        if r.h>hi and mode!='dn': hi,hit=r.h,t
        if r.l<lo and mode!='up': lo,lot=r.l,t
        if mode is None:
            if r.h>hi: hi,hit=r.h,t
            if r.l<lo: lo,lot=r.l,t
    return piv
TH={'BTC_BS':0.08,'BTC':0.08,'ETH':0.12,'SOL':0.15}
rows=[]
for name,sym,t0s,_ in CASES:
    t0=pd.Timestamp(t0s); D=pd.Timedelta; x=h4(sym); dd=daily(sym)
    lo_t=x[t0:t0+D(days=1)].l.idxmin(); L0=x.l[lo_t]
    # 바닥 이후: 바닥 봉에서 시작하는 지그재그
    aft=zigzag(x[lo_t:t0+D(days=200)],TH[sym])
    aft=[p for p in aft if p[1]>lo_t]
    if aft and aft[0][0]=='L': aft=aft[1:]
    H1=aft[0] if len(aft)>0 else None; L1=aft[1] if len(aft)>1 else None; H2=aft[2] if len(aft)>2 else None; L2=aft[3] if len(aft)>3 else None
    # 120일 안 가장 깊은 재시험 (H1 이후)
    deep=x[H1[1]:t0+D(days=120)].l if H1 else pd.Series(dtype=float)
    dpt=deep.idxmin() if len(deep)>1 else None
    # 넥라인 = H1, 돌파 = L1 이후 일봉 종가 > H1
    bo=None; fail=None
    if H1 and L1:
        c=dd.c[(dd.index>L1[1].normalize())&(dd.c>H1[2])]
        if len(c):
            bo=c.index[0]
            nxt=dd.c[bo:bo+D(days=60)]; fail=bool((nxt<L1[2]).any())
    # 바닥 이전: 충격 저점 = 바닥 전 45일 안의 마지막 확정 저점(지그재그) 중 최저가 아닌 직전 것
    bef=zigzag(x[t0-D(days=60):lo_t],TH[sym]); bl=[p for p in bef if p[0]=='L' and p[1]<lo_t-D(days=2)]
    SH=min(bl[-3:],key=lambda p:p[2]) if bl else None
    r=rsi(dd.c)
    def rv(t): return r[t.normalize()-D(days=1):t.normalize()+D(days=1)].min()
    rows.append(dict(사례=name,바닥시각=lo_t,바닥=L0,
        충격저점=SH[1].date() if SH else None,충격저점가=SH[2] if SH else np.nan,충격대비=(L0/SH[2]-1) if SH else np.nan,
        RSI_충격=rv(SH[1]) if SH else np.nan,RSI_바닥=rv(lo_t),
        H1시각=H1[1] if H1 else None,H1상승=(H1[2]/L0-1) if H1 else np.nan,H1일수=(H1[1]-lo_t).total_seconds()/86400 if H1 else np.nan,
        L1시각=L1[1] if L1 else None,L1_바닥대비=(L1[2]/L0-1) if L1 else np.nan,L1일수=(L1[1]-lo_t).total_seconds()/86400 if L1 else np.nan,
        H2상승=(H2[2]/L0-1) if H2 else np.nan,L2_바닥대비=(L2[2]/L0-1) if L2 else np.nan,L2일수=(L2[1]-lo_t).days if L2 else np.nan,
        최심재시험=dpt.date() if dpt is not None else None,최심_바닥대비=(deep.min()/L0-1) if dpt is not None else np.nan,
        넥라인=H1[2] if H1 else np.nan,돌파일=bo.date() if bo is not None else None,돌파일수=(bo-t0).days if bo is not None else np.nan,
        돌파시_바닥대비=(dd.c[bo]/L0-1) if bo is not None else np.nan,돌파후60일내_L1이탈=fail))
T=pd.DataFrame(rows); T.to_csv('output/u2_after_pivots.csv',index=False)
S=T.copy()
for k in ['충격대비','H1상승','L1_바닥대비','H2상승','L2_바닥대비','최심_바닥대비','돌파시_바닥대비']: S[k]=(S[k]*100).round(1)
for k in ['RSI_충격','RSI_바닥','H1일수','L1일수']: S[k]=S[k].round(1)
with open('output/u2_after_pivots.txt','w') as f:
    for cols,tt in [(['사례','바닥시각','바닥','충격저점','충격저점가','충격대비','RSI_충격','RSI_바닥'],'바닥 직전: 충격 저점(바닥 전 60일 안 스윙 저점)과 일봉 RSI'),
                    (['사례','H1시각','H1상승','H1일수','L1시각','L1_바닥대비','L1일수','H2상승','L2_바닥대비','L2일수','최심재시험','최심_바닥대비'],'바닥 직후 스윙 (1시간봉 지그재그 BTC 8%·ETH 12%·SOL 15%, %)'),
                    (['사례','넥라인','돌파일','돌파일수','돌파시_바닥대비','돌파후60일내_L1이탈'],'넥라인(H1) 돌파 — 일봉 종가 기준')]:
        s=f"== {tt}\n{S[cols].to_string(index=False)}\n\n"; print(s); f.write(s)
