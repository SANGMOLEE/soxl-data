# I. 사이클 전체(바닥 전 ~ 고점 ~ 다음 하락장)에서 '수백 배'를 얼마나 먹나: 매수 시점 × 단순 매도법 × 1배/2배
from sigs import *
pd.set_option('display.width',260)
CYC={'2015':('2015-01-14','2018-12-15',['ltc','xrp','dash','doge']),
     '2018':('2018-12-15','2022-11-21',['eth','xrp','ltc','ada','bnb','link','xlm','doge','etc','trx']),
     '2022':('2022-11-21','2026-11-13',['sol','eth','ada','avax','dot','link','bnb','doge','xrp'])}
def path(a, lev):
    p=P(a); return p, (lev2(p,COST) if lev==2 else p/p.iloc[0])
def first_on(sig, after):
    x=sig[after:]; x=x[x==1]; return x.index[0] if len(x) else None
def at(idx, t):
    i=idx.searchsorted(t); return idx[min(i,len(idx)-1)]
def sim(p, nav, entry, exit_rule, end):
    """entry: 진입일(종가 매수). exit_rule: 'hold' | 'top' | ('ma',n,c) 한 번 매도 | ('ma_re',n,c) 이탈 매도·재돌파 재매수 | ('stage',n,c)"""
    if entry is None: return np.nan, np.nan
    e=at(nav.index,entry); seg=nav[e:end]; ps=p[e:end]
    if exit_rule=='hold': return seg.iloc[-1]/seg.iloc[0], (seg.max()/seg.iloc[0])
    if exit_rule=='top':  return seg.max()/seg.iloc[0], seg.max()/seg.iloc[0]
    kind,n,c=exit_rule; ma=p.rolling(n).mean()[e:end]
    below=(ps<ma).astype(int); run_=below.groupby((below!=below.shift()).cumsum()).cumsum()
    if kind=='ma':      # 한 번 매도: 매수 후 +100% 이상 된 뒤 MA 아래 c일 연속이면 매도
        gained=(seg/seg.iloc[0]).cummax()>=2.0
        hit=run_[(run_>=c)&gained]
        if hit.empty: return seg.iloc[-1]/seg.iloc[0], seg.max()/seg.iloc[0]
        t=hit.index[0]; return seg[t]/seg.iloc[0]*(0.998), seg.max()/seg.iloc[0]
    if kind=='ma_re':   # 느린 추세 따라가기: MA 아래 c일 → 매도, MA 위 c일 → 재매수
        above=(ps>ma).astype(int); ra=above.groupby((above!=above.shift()).cumsum()).cumsum()
        pos=pd.Series(np.nan,ps.index); pos.iloc[0]=1; pos[run_>=c]=0; pos[ra>=c]=1; pos=pos.ffill()
        held=pos.shift(1).fillna(1); g=seg.pct_change().fillna(0); eq=(1+held*g)*(1-0.002*held.diff().abs().fillna(0))
        eq=eq.cumprod(); return eq.iloc[-1], eq.max()
    if kind=='stage':   # 3배·10배·30배에 1/4씩 익절, 나머지는 'ma' 규칙
        m=seg/seg.iloc[0]; out=0; left=1.0
        for k in [3,10,30]:
            hit=m[m>=k]
            if len(hit): out+=0.25*k*0.998; left-=0.25
        r,_=sim(p,nav,entry,('ma',n,c),end); return out+left*r, m.max()
ENTRIES=lambda D,p: {'BTC바닥 60일 전':D-pd.Timedelta(days=60),'30일 전':D-pd.Timedelta(days=30),'BTC바닥일':D,'30일 후':D+pd.Timedelta(days=30),
    '60일 후':D+pd.Timedelta(days=60),'90일 후':D+pd.Timedelta(days=90),'180일 후':D+pd.Timedelta(days=180),
    '자기 바닥일(사후)':p[D-pd.Timedelta(days=60):D+pd.Timedelta(days=200)].idxmin(),
    '첫 MA25 신호':first_on(band_sig(p,25,0.0,2),D),'첫 200일선 회복':first_on(band_sig(p,140,0.0,2),D)}
EXITS={'끝까지 보유':'hold','고점 매도(사후)':'top','+100% 뒤 200일선 2일 이탈 1회 매도':('ma',140,2),
       '200일선 추세(이탈 매도·회복 재매수)':('ma_re',140,2),'3/10/30배 1/4씩 익절+나머지 200일선':('stage',140,2)}
rows=[]
for cy,(D,E,assets) in CYC.items():
    D=pd.Timestamp(D); E=pd.Timestamp(E)
    for a in assets+['btc']:
        for lev in [1,2]:
            p,nav=path(a,lev)
            if p.index[0]>D-pd.Timedelta(days=300): continue
            for en,et in ENTRIES(D,p).items():
                for xn,xr in EXITS.items():
                    r,mx=sim(p,nav,et,xr,E)
                    rows.append(dict(cycle=cy,asset=a,lev=lev,entry=en,exit=xn,mult=r,peak=mx))
R=pd.DataFrame(rows).dropna(subset=['mult']); R.to_csv('output/cycle_all.csv',index=False)
gm=lambda x: np.exp(np.log(x.clip(lower=1e-6)).mean())
def table(df,title):
    per=df.groupby(['cycle','entry','exit']).mult.median().reset_index()
    t=per.groupby(['entry','exit']).mult.median().unstack('exit')[list(EXITS)].reindex(list(ENTRIES(pd.Timestamp('2022-11-21'),P('sol')).keys()))
    print(f"\n== {title}"); print(t.round(2).to_string())
table(R[(R.lev==2)&(R.asset!='btc')],"알트 2배(SOLT형): 매수시점(행)×매도법(열), 3개 사이클의 '사이클별 알트 중앙값'의 중앙값")
table(R[(R.lev==1)&(R.asset!='btc')],"알트 1배(현물): 같은 표")
s2=R[(R.asset=='sol')].pivot_table(index=['lev','entry'],columns='exit',values='mult')[list(EXITS)]
print("\n== SOL 2022 사이클 (2022-11-21 → 2026-11-13), 1배·2배"); print(s2.round(2).to_string())
print("\n고점까지 평가액 최대(보유 시) — SOL 2배:", R[(R.asset=='sol')&(R.lev==2)&(R.exit=='끝까지 보유')].set_index('entry').peak.round(1).to_dict())
