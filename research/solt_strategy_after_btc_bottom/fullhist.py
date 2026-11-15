# D. 전체 역사 검증 + 거래 통계 + 현재 SOL 신호 상태
from sigs import *
ASSETS=['btc','sol','eth','xrp','ltc','ada','bnb','link','xlm','dash','xmr','bch','etc','doge','trx','avax','dot']
pd.set_option('display.width',220)
rows=[]; tstats=[]
for a in ASSETS:
    p=P(a); st=p.index[0]+pd.Timedelta(days=60); en=p.index[-1]
    yrs=(en-st).days/365
    sig=band_sig(p,25,0.0,2)
    lm=[np.log(run(p,sig,cost=COST,lag=l,start=st,end=en)[0].iloc[-1]) for l in [1,2,3]]
    eqh,_,_,mh=run(p,pd.Series(1,p.index),cost=COST,lag=0,start=st,end=en)
    eqs,ex,tr,ms=run(p,sig,cost=COST,lag=1,start=st,end=en)
    one=p[st:en]; 
    rows.append(dict(asset=a,시작=st.date(),년=round(yrs,1),규칙_배수=np.exp(np.mean(lm)),규칙_연율=np.exp(np.mean(lm)/yrs)-1,
                     보유2배_배수=eqh.iloc[-1],보유1배_배수=one.iloc[-1]/one.iloc[0],규칙MDD=ms,보유2배MDD=mh,노출=ex))
    # 거래 통계 (지연1)
    pos=sig.shift(1).fillna(0)[st:en]; held=pos.shift(1).fillna(0); r=p[st:en].pct_change().fillna(0); dt=p[st:en].index.to_series().diff().dt.days.fillna(0)
    g=np.log((1+2*r).clip(lower=1e-9)*np.exp(-COST*dt/365)); grp=(held.diff().fillna(0)==1).cumsum()
    for k,x in g[held==1].groupby(grp[held==1]): tstats.append(dict(asset=a,lg=x.sum()+2*np.log(0.998),days=len(x)))
o=pd.DataFrame(rows).set_index('asset'); print("== 전체 역사: SOL MA25(거래일)·2일확인 규칙 vs 2배 계속보유 (합성, 비용 연20%)")
print(o.round(2).to_string())
print("\n규칙이 2배 보유보다 나은 자산 비율: %.0f%%,  규칙 배수>1 비율: %.0f%%"%((o.규칙_배수>o.보유2배_배수).mean()*100,(o.규칙_배수>1).mean()*100))
t=pd.DataFrame(tstats); t['m']=np.exp(t.lg)
def ts(x): return pd.Series({'거래수':len(x),'승률':(x.m>1).mean(),'평균이익':x.m[x.m>1].median()-1,'평균손실':x.m[x.m<=1].median()-1,'최대이익':x.m.max()-1,'최대손실':x.m.min()-1,'보유일중앙':x.days.median(),
                             '상위10%거래 이익비중':x.lg[x.lg>0].nlargest(max(1,len(x)//10)).sum()/x.lg[x.lg>0].sum()})
print("\n== 거래 통계 (거래일 기준 보유일)"); print(pd.concat({'SOL':ts(t[t.asset=='sol']),'알트 전체':ts(t[~t.asset.isin(['btc','sol'])]),'BTC':ts(t[t.asset=='btc'])},axis=1).round(2).to_string())
# 현재 상태
p=P('sol'); ma=p.rolling(25).mean(); sig=band_sig(p,25,0.0,2)
print("\n== SOL 최근 (미국 거래일 종가 = 00:00 UTC 일봉 종가)")
print(pd.DataFrame({'SOL':p,'MA25':ma,'MA대비':p/ma-1,'신호':sig}).tail(12).round(3).to_string())
# 가격 고정 시 MA25 경로 → 2일 연속 MA 위 진입 필요가격
last=p.iloc[-25:].tolist(); print("\nSOL이 x달러에 머문다고 할 때 MA25 (진입은 종가가 MA 위로 2거래일 연속):")
for x in [72.35,75,80,85,90]:
    hist=last.copy(); path=[]
    for d in range(1,31):
        hist=hist[1:]+[x]; path.append(np.mean(hist))
    above=[i+1 for i,m in enumerate(path) if x>m]
    print(f"  SOL ${x:>6}: 5거래일 뒤 MA {path[4]:.1f}, 10거래일 뒤 {path[9]:.1f}, 20거래일 뒤 {path[19]:.1f} → 처음 MA 위: {above[0] if above else '30일 내 없음'}거래일째")
cal=raw('sol').dropna(); print(f"\n달력일 기준 SOL MA35 = {cal.rolling(35).mean().iloc[-1]:.2f} (11/15),  MA25(거래일) = {ma.iloc[-1]:.2f} ({p.index[-1].date()})")
# 실제 SOLT 기간 거래기록 (지연1, 실제 SOLT 가격)
a=solt_raw.reindex(p.index).dropna(); pos=sig.shift(1).reindex(a.index).fillna(0)
chg=pos.diff().fillna(0); print("\n== 실제 SOLT 기간의 규칙 거래 (신호 다음 거래일 종가 체결, 원주가):")
ent=None; log=[]
for d,v in chg.items():
    if v==1: ent=(d,a[d])
    if v==-1 and ent: log.append((ent[0].date(),round(ent[1],2),d.date(),round(a[d],2),round(a[d]/ent[1]-1,3))); ent=None
for x in log: print("  매수",x[0],x[1]," → 매도",x[2],x[3],f" {x[4]:+.1%}")
if ent: print("  보유중:",ent[0].date(),round(ent[1],2))
cum=np.prod([1+x[4] for x in log]); print(f"  누적(거래비용 전) {cum:.2f}배 vs 같은 기간 계속보유 {a.iloc[-1]/a.loc[a.index>=pd.Timestamp('2025-04-25')].iloc[0]:.2f}배 (규칙 첫 진입 시점부터)")
