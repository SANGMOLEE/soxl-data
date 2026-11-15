# G. 매도(청산) 완화 변형: 상승기 포착률 vs 하락장 방어
from sigs import *
pd.set_option('display.width',240)
def gsig(p, n_in=25, c_in=2, n_out=25, c_out=1, b_out=0.0, regime=None):
    ma_in=p.rolling(n_in).mean().values; ma_out=p.rolling(n_out).mean().values; v=p.values
    ma200=p.rolling(200).mean().values
    s=np.zeros(len(v),int); st=False; ci=co=0
    for i in range(len(v)):
        if np.isnan(ma_in[i]) or np.isnan(ma_out[i]): continue
        mo=ma_out[i]; bo=b_out
        if regime and not np.isnan(ma200[i]) and v[i]>ma200[i]:      # 상승 국면(200일선 위)에서만 느슨한 청산
            mo=p.iloc[max(0,i-regime['n']+1):i+1].mean(); bo=regime.get('b',0.0)
        elif regime: mo=ma_in[i]; bo=0.0
        if not st:
            ci=ci+1 if v[i]>ma_in[i] else 0
            if ci>=c_in: st=True; ci=0; co=0
        else:
            co=co+1 if v[i]<mo*(1-bo) else 0
            if co>=c_out: st=False; co=0
        s[i]=int(st)
    return pd.Series(s,p.index)
V={'V0 현행: MA25 이탈 즉시':dict(),
   'V1 MA25 2일 연속 이탈':dict(c_out=2),
   'V2 MA25 -5% 이탈':dict(b_out=0.05),
   'V3 MA25 -10% 이탈':dict(b_out=0.10),
   'V4 MA50 이탈':dict(n_out=50),
   'V5 200일선 위면 MA50, 아래면 MA25':dict(regime=dict(n=50)),
   'V6 200일선 위면 MA25-10%, 아래면 MA25':dict(regime=dict(n=25,b=0.10))}
# 상승기 목록 (bull.py 와 동일 정의)
L=pd.read_csv('output/bull_legs.csv'); legs=[tuple(map(pd.Timestamp,x.split('→'))) for x in L['상승기']]
p=P('sol'); nav=lev2(p,COST)
rows=[]
for vn,kw in V.items():
    sig=gsig(p,**kw); out={'변형':vn}
    caps=[]
    for a,b in legs:
        lm=np.mean([np.log(run(p,sig,cost=COST,lag=l,start=a,end=b)[0].iloc[-1]) for l in [1,2]])
        caps.append(lm/np.log(nav[b]/nav[a]))
        if a.year==2025: out['2025상승기(4.15배)']=np.exp(lm)
    out['상승기 포착률(중앙)']=np.median(caps)
    # 상승기 밖 손실: 상승기 사이 구간들 누적
    out['SOL 2020~26 전체']=np.exp(np.mean([np.log(run(p,sig,cost=COST,lag=l,start='2020-11-01',end='2026-11-13')[0].iloc[-1]) for l in [1,2,3]]))
    a_=solt.reindex(p.index).dropna(); vals=[]
    for l in [1,2,3]:
        pos=sig.shift(l).reindex(a_.index).fillna(0); held=pos.shift(1).fillna(0); held.iloc[0]=0
        vals.append(np.log(((1+held*a_.pct_change().fillna(0))*(1-0.002*held.diff().abs().fillna(0))).prod()))
    out['실제SOLT 25~26']=np.exp(np.mean(vals))
    # 4개 사이클 알트 (D-90~D+540), 지연1~3 평균
    cyc=[]
    for D,assets in BOTTOMS.items():
        st=pd.Timestamp(D)-pd.Timedelta(days=90); en=pd.Timestamp(D)+pd.Timedelta(days=540); ms=[]
        for a in assets:
            q=P(a)
            if q.index[0]>st-pd.Timedelta(days=250): continue
            sg=gsig(q,**kw); ms.append(np.mean([np.log(run(q,sg,cost=COST,lag=l,start=st,end=en)[0].iloc[-1]) for l in [1,2,3]]))
        cyc.append(np.median(ms))
    out['4사이클 중앙']=np.exp(np.median(cyc)); out['4사이클 최악']=np.exp(min(cyc))
    pos=sig.shift(1).fillna(0)['2020-11':]; out['거래수(SOL)']=int(pos.diff().abs().sum()); out['보유비중']=pos.mean()
    rows.append(out)
o=pd.DataFrame(rows).set_index('변형')
print("[가상 SOLT 비용 20%; 상승기 지표는 지연1·2 평균, 나머지 지연1~3 평균]")
print(o.round(2).to_string()); o.round(3).to_csv('output/exits.csv')
# 2025 상승기 실제 SOLT 거래기록: V0 vs 최선 변형
for vn in ['V0 현행: MA25 이탈 즉시','V3 MA25 -10% 이탈','V6 200일선 위면 MA25-10%, 아래면 MA25']:
    sig=gsig(p,**V[vn]); a_=solt_raw.reindex(p.index).dropna(); pos=sig.shift(1).reindex(a_.index).fillna(0); chg=pos.diff().fillna(0)
    print(f"\n-- {vn}: 실제 SOLT 거래 (2025-03~2026-11, 지연1)"); ent=None; tot=1
    for d,v in chg.items():
        if v==1: ent=(d,a_[d])
        if v==-1 and ent: m=a_[d]/ent[1]; tot*=m; print(f"   {ent[0].date()} {ent[1]:7.2f} → {d.date()} {a_[d]:7.2f}  {m-1:+.1%}"); ent=None
    if ent: print(f"   {ent[0].date()} {ent[1]:7.2f} → 보유중")
    print(f"   누적 {tot:.2f}배")
