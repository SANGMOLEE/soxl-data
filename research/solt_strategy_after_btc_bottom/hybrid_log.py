# K. 하이브리드(k=3) SOL 거래 경로 + 비용 민감도
from sigs import *
import hybrid as H
def logrun(p,nav,start,end,k=3.0,lag=1):
    # hybrid()와 같은 로직을 기록용으로 재실행
    p=p[:end]; nav=nav[:end]; up=(p>p.rolling(25).mean()); ma140=p.rolling(140).mean(); idx=p[start:end].index
    cash=1.0; units=0; state='A0'; cu=0; cd=0; pend=[]; log=[]; taken=0
    for i,t in enumerate(idx):
        v=nav[t]
        for (d,a) in [x for x in pend if x[0]==i]:
            if a=='buy' and units==0: units=cash*0.998/v; cash=0; en=v; ou=units; taken=0; state='A1'; log.append((t.date(),'매수',round(p[t],2),round(cash+units*v,2)))
            if a=='sell' and units>0: cash+=units*v*0.998; units=0; log.append((t.date(),'전량매도' if state=='A1' else '상승장모드 잔량매도',round(p[t],2),round(cash,2))); state='A0'
        pend=[x for x in pend if x[0]!=i]
        u=bool(up[t]); cu=cu+1 if u else 0
        if state=='A0' and cu>=2 and not pend: pend.append((i+lag,'buy'))
        elif state=='A1':
            if v/en>=k: state='B'; seen=False; log.append((t.date(),'상승장모드 전환(3배)',round(p[t],2),round(cash+units*v,2)))
            elif not u and not pend: pend.append((i+lag,'sell'))
        elif state=='B':
            m=v/en
            for j,l in enumerate((3,10,30)):
                if taken==j and m>=l and units>0: q=min(units,ou*0.25); cash+=q*v*0.998; units-=q; taken+=1; log.append((t.date(),f'1/4 익절({l}배)',round(p[t],2),round(cash+units*v,2)))
            cd=cd+1 if p[t]<ma140[t] else 0
            if p[t]>=ma140[t]: seen=True
            if ((cd>=2) if seen else (not u)) and not pend: pend.append((i+lag,'sell'))
    return log, cash+units*nav[idx[-1]]
p=P('sol')
for c in [0.20,0.35]:
    nav=lev2(p,c); log,final=logrun(p,nav,pd.Timestamp('2022-08-23'),pd.Timestamp('2026-11-13'))
    big=[x for x in log if '매수' not in x[1] or True]
    print(f"\n== SOL 하이브리드 k=3, 비용 연 {c:.0%}, 지연1: 최종 {final:.2f}배 (MA25 단기매매만: {H.hybrid(p,nav,pd.Timestamp('2022-08-23'),pd.Timestamp('2026-11-13'),mode_b=False)[0]:.2f}배, 계속보유 {nav['2026-11-13']/nav.iloc[nav.index.searchsorted(pd.Timestamp('2022-08-23'))]:.3f}배)")
    if c==0.20:
        for x in log: print("  ",x[0],f"{x[1]:<14s} SOL ${x[2]:<8} 평가액 {x[3]}배")
