# J. 실전형 하이브리드: [A] MA25 단기매매로 가짜바닥 방어 → 한 거래가 k배 되면 [B] 상승장 모드(이동평균 매도 해제, 3/10/30배 1/4 익절, 나머지 느린 청산)
from sigs import *
pd.set_option('display.width',260)
def hybrid(p, nav, start, end, k=2.0, tp=(3,10,30), rest=('ma',140,2), tr=None, lag=1, tc=0.002, mode_b=True, fix200=True):
    p=p[:end]; nav=nav[:end]
    up=(p>p.rolling(25).mean()); ma140=p.rolling(140).mean()
    idx=p[start:end].index; sig_hist=[]
    cash=1.0; units=0.0; state='A0'; cnt_up=0; cnt_dn=0; entry_nav=None; base=None; peak=None; taken=0; orig_units=0
    pend=[]  # (실행일, 행동) 체결 지연
    eq=[]
    for i,t in enumerate(idx):
        v=nav[t]
        # 지연된 주문 체결
        for act in [a for (d,a) in pend if d==i]:
            if act=='buy' and units==0:
                units=cash*(1-tc)/v; cash=0; entry_nav=v; orig_units=units; taken=0; state='A1'
            elif act=='sell' and units>0:
                cash+=units*v*(1-tc); units=0; state='A0'
        pend=[(d,a) for (d,a) in pend if d!=i]
        u=bool(up[t]); cnt_up=cnt_up+1 if u else 0
        if state=='A0' and cnt_up>=2 and not pend: pend.append((i+lag,'buy'))
        elif state=='A1':
            if mode_b and v/entry_nav>=k: state='B'; base=entry_nav; peak=v; seen_above=False
            elif not u and not pend: pend.append((i+lag,'sell'))
        elif state=='B':
            peak=max(peak,v); m=v/base
            for j,lvl in enumerate(tp):
                if taken==j and m>=lvl and units>0:
                    q=min(units,orig_units*0.25); cash+=q*v*(1-tc); units-=q; taken+=1
            below=p[t]<ma140[t]; cnt_dn=cnt_dn+1 if below else 0
            if not below: seen_above=True
            if rest is not None and fix200 and not seen_above:
                hit=(not u)                                   # 아직 200일선 위에 선 적 없으면 MA25 이탈로 판단
            else:
                hit=(rest is not None and cnt_dn>=rest[2])
            hit=hit or (tr is not None and v<=peak*(1-tr))
            if hit and not pend: pend.append((i+lag,'sell'))
        eq.append(cash+units*v)
    e=pd.Series(eq,idx); return e.iloc[-1], e.max(), (e/e.cummax()-1).min()
if __name__=='__main__':
    CYC=[('SOL','sol','2020-09-01','2022-11-21'),('SOL','sol','2022-08-23','2026-11-13'),
         ('2015','ltc','2014-10-16','2018-12-15'),('2015','xrp','2014-11-15','2018-12-15'),('2015','dash','2014-10-16','2018-12-15'),('2015','doge','2014-10-16','2018-12-15'),
         ]+[('2018',a,'2018-09-16','2022-11-21') for a in ['eth','xrp','ltc','ada','bnb','link','xlm','doge','etc']]+\
         [('2022',a,'2022-08-23','2026-11-13') for a in ['eth','ada','avax','dot','link','bnb','doge','xrp']]
    VAR={'계속 보유(시작일 매수)':None,'MA25 단기매매만':dict(mode_b=False),
         '하이브리드 k=2, 3/10/30익절, 나머지 200일선':dict(k=2.0),
     '(수정 전) k=3, 200일선 즉시판단':dict(k=3.0,fix200=False),
         '하이브리드 k=3, 3/10/30익절, 나머지 200일선':dict(k=3.0),
         '하이브리드 k=2, 3/10/30익절, 나머지 고점-50%':dict(k=2.0,rest=None,tr=0.50),
         '하이브리드 k=2, 5/15/50익절, 나머지 고점-50%':dict(k=2.0,tp=(5,15,50),rest=None,tr=0.50),
         '하이브리드 k=2, 익절없음, 고점-50%':dict(k=2.0,tp=(),rest=None,tr=0.50),
         '하이브리드 k=2, 익절없음, 고점-60%':dict(k=2.0,tp=(),rest=None,tr=0.60)}
    rows=[]
    for cy,a,st,en in CYC:
        for lev in [2,1]:
            p=P(a); nav=lev2(p,COST) if lev==2 else p/p.iloc[0]
            st_=pd.Timestamp(st); en_=pd.Timestamp(en)
            if p.index[0]>st_-pd.Timedelta(days=150): continue
            for vn,kw in VAR.items():
                if kw is None:
                    s=nav[st_:en_]; r=(s.iloc[-1]/s.iloc[0],s.max()/s.iloc[0],(s/s.cummax()-1).min())
                else:
                    rr=[hybrid(p,nav,st_,en_,lag=l,**kw) for l in [1,2]]
                    r=tuple(np.exp(np.mean(np.log([x[j] if j<2 else 1+x[j] for x in rr]))) for j in range(3)); r=(r[0],r[1],r[2]-1)
                rows.append(dict(cy=cy,asset=a,start=st,lev=lev,var=vn,end_mult=r[0],peak_mult=r[1],mdd=r[2]))
    R=pd.DataFrame(rows); R.to_csv('output/hybrid_fixed.csv',index=False)
    for lev in [2,1]:
        x=R[R.lev==lev]
        sol=x[x.asset=='sol'].pivot_table(index='var',columns='start',values='end_mult')
        alt=x[x.asset!='sol'].groupby(['var','cy']).end_mult.median().unstack('cy')
        t=sol.join(alt); t.columns=[('SOL 2020~22' if c=='2020-09-01' else 'SOL 2022~26' if c=='2022-08-23' else f'알트 {c} 사이클') for c in t.columns]
        t['SOL MDD(22~26)']=x[(x.asset=='sol')&(x.start=='2022-08-23')].set_index('var').mdd
        print(f"\n== {lev}배 — 사이클 끝(다음 바닥 또는 현재) 최종 배수. 바닥 90일 전부터 시작, 사후정보 없음, 지연1·2 평균")
        print(t.loc[list(VAR)].round(2).to_string())
