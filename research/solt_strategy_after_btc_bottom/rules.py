from engine import *
import sys, itertools
cost=float(sys.argv[1]) if len(sys.argv)>1 else 0.20; lag=int(sys.argv[2]) if len(sys.argv)>2 else 1
RULES=['HOLD']+[f'MA_{n}' for n in [10,15,20,30,50,100]]+['XMA_5_20','XMA_10_30','XMA_10_50','XMA_20_50','XMA_20_100']+\
      [f'BMA_{n}' for n in [20,50]]+['MAB_20_50','MAB_10_20','MAB_15_50']+['DON_20_10','DON_20_20','DON_10_10','DON_40_20']+\
      [f'MAT_{n}_{x}' for n in [10,20] for x in [20,30]]
rows=[]
for D,assets in BOTTOMS.items():
    for a in assets+['btc']:
        for R in RULES:
            e=episode(a,D,R,cost=cost,lag=lag)
            if e: rows.append(e)
    # 오라클: D에 매수해 끝까지 / D에 매수해 D+180 매도
for D,assets in BOTTOMS.items():
    for a in assets+['btc']:
        p=sess(raw(a).dropna()); st=pd.Timestamp(D)
        for nm,en in [('ORACLE_D_to_end',st+pd.Timedelta(days=540)),('ORACLE_D_to_D180',st+pd.Timedelta(days=180))]:
            eq,ex,tr,mdd=run(p,pd.Series(1,p.index),cost=cost,lag=0,start=st,end=en)
            rows.append(dict(asset=a,D=D,rule=nm,mult=eq.iloc[-1],exposure=np.nan,trades=1,mdd=mdd))
r=pd.DataFrame(rows); r.to_csv(f'output/rules_c{int(cost*100)}_lag{lag}.csv',index=False)
alts=r[r.asset!='btc']
cyc=alts.groupby(['rule','D']).agg(mult=('mult','median'),mdd=('mdd','median'),exp=('exposure','median'),tr=('trades','median')).reset_index()
gm=lambda x: np.exp(np.log(x).mean())
summ=cyc.groupby('rule').agg(사이클중앙=('mult','median'),사이클기하평균=('mult',gm),최악사이클=('mult','min'),MDD중앙=('mdd','median'),노출=('exp','median'),거래=('tr','median'))
wide=cyc.pivot(index='rule',columns='D',values='mult')
out=summ.join(wide).sort_values('사이클기하평균',ascending=False)
# 개별 에피소드 기준 승률(시작시점 보유 대비)
hold=alts[alts.rule=='HOLD'].set_index(['asset','D']).mult
alts2=alts.join(hold.rename('hold'),on=['asset','D']); out=out.join(alts2.groupby('rule').apply(lambda x:(x.mult>x.hold).mean()).rename('HOLD대비승률'))
sol_=r[(r.asset=='sol')].set_index('rule').mult.rename('SOL_2022'); btc_=r[r.asset=='btc'].groupby('rule').mult.apply(gm).rename('BTC2x_기하')
out=out.join(sol_).join(btc_)
pd.set_option('display.width',260)
print(f"[비용 {cost:.0%}, 체결지연 {lag}일] 구간 D-90 ~ D+540, 알트 2배 합성 (사이클별 알트 중앙값 기준)")
print(out.round(2).to_string())
