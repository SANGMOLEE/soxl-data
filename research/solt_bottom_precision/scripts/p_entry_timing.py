# P. BTC 저점 이후 SOLT형(2배) 최저가는 언제 나오나 + 공격적 저점매수 규칙 비교 (사이클 바닥, 일봉)
import sys, os; sys.path.insert(0,'scripts')
import numpy as np, pandas as pd
exec(open('scripts/o_after_bottom.py',encoding='utf-8').read().split("rows=[]")[0])
pd.set_option('display.width',260)
OFF=[0,3,7,14,21,30,45,60,90,120,150,180,240]
rows=[]; grid=[]; rules=[]
for cy,(D,assets) in CYC.items():
    D=pd.Timestamp(D)
    for a in assets:
        p=px(a)
        if p.index[0]>D-pd.Timedelta(days=60) or p.index[-1]<D+pd.Timedelta(days=400): continue
        q=p[D-pd.Timedelta(days=60):D+pd.Timedelta(days=640)]; n=nav2(q); n=n/n[D]; P0=q[D]
        after=n[D:D+pd.Timedelta(days=365)]; tmin=after.idxmin(); mn=after.min(); dmin=(tmin-D).days
        before=n[D-pd.Timedelta(days=30):D].min()
        zone='바닥 당일(0~3일)' if dmin<=3 else ('바닥 직후 재시험(4~60일)' if dmin<=60 else '횡보기(61~365일)')
        rows.append(dict(cycle=cy,asset=a,min_nav=mn,min_day=dmin,zone=zone,before30_min=before,
                         min_early=n[D+pd.Timedelta(days=4):D+pd.Timedelta(days=60)].min(),min_base=n[D+pd.Timedelta(days=61):D+pd.Timedelta(days=365)].min()))
        for x in OFF:
            t=D+pd.Timedelta(days=x); e=n[:t].iloc[-1]; fut=n[t:t+pd.Timedelta(days=365)]
            def tk(k):
                w=fut[fut>=e*k]; return (w.index[0]-t).days if len(w) else np.nan
            grid.append(dict(cycle=cy,asset=a,off=x,entry=e,dist=e/mn-1,up365=fut.max()/e,t2=tk(2),t3=tk(3),t5=tk(5)))
        # ---- 실시간 규칙 (D 이후 정보만) ----
        def rec(name,t,e,filled=True):
            if not filled: rules.append(dict(cycle=cy,asset=a,rule=name,filled=False)); return
            fut=n[t:t+pd.Timedelta(days=365)]
            def tk(k):
                w=fut[fut>=e*k]; return (w.index[0]-t).days if len(w) else np.nan
            rules.append(dict(cycle=cy,asset=a,rule=name,filled=True,day=(t-D).days,entry=e,dist=e/mn-1,up365=fut.max()/e,t2=tk(2),t3=tk(3)))
        rec('R0 BTC 바닥일 즉시',D,1.0)
        w=n[D+pd.Timedelta(days=1):D+pd.Timedelta(days=120)]
        for m in [0.0,0.10,0.20]:
            hit=w[w<=1-m]
            rec(f'R1 재시험 지정가 (바닥 가격{"" if m==0 else f" -{int(m*100)}%"})',hit.index[0] if len(hit) else None,(1-m) if len(hit) else None,len(hit)>0)
        # 첫 반등 뒤 되밀림: 기초자산 +30% 반등 확인 후, 반등 고점 대비 -Z% 종가에 매수 (180일 안)
        qq=q[D:D+pd.Timedelta(days=180)]
        for Z in [0.20,0.30]:
            up=qq[qq>=P0*1.3]; done=False
            if len(up):
                t1=up.index[0]; hi=-1
                for t,v in qq[t1:].items():
                    hi=max(hi,v)
                    if v<=hi*(1-Z): rec(f'R2 반등(+30%) 뒤 고점 대비 -{int(Z*100)}% 되밀림',t,n[t]); done=True; break
            if not done: rec(f'R2 반등(+30%) 뒤 고점 대비 -{int(Z*100)}% 되밀림',None,None,False)
G=pd.DataFrame(grid); M=pd.DataFrame(rows); Rr=pd.DataFrame(rules)
G.to_csv('output/p_grid.csv',index=False); M.to_csv('output/p_min.csv',index=False); Rr.to_csv('output/p_rules.csv',index=False)
print(f"== ① BTC 사이클 바닥(2011~2022) 이후 1년 안 2배 상품 최저가는 언제였나 — {len(M)}건 (BTC·ETH·SOL·알트)")
print(M.zone.value_counts().to_string())
print(f"   최저가 = 바닥일 대비 중앙 {M.min_nav.median()-1:+.0%} (하위25% {M.min_nav.quantile(.25)-1:+.0%}); 바닥 직후(4~60일) 최저 중앙 {M.min_early.median()-1:+.0%}, 횡보기(61~365일) 최저 중앙 {M.min_base.median()-1:+.0%}")
print(f"   바닥 이전 30일 안에 이미 더 낮았던 경우: {(M.before30_min<1).mean():.0%}")
print(M[M.asset.isin(['btc','eth','sol'])][['cycle','asset','min_day','min_nav','min_early','min_base','zone']].round(2).to_string(index=False))
print("\n== ② 매수일(BTC 바닥 +x일)별: 2배 상품 매수가의 1년 최저 대비 거리, 매수 후 1년 최대 배수, 2·3·5배 도달일 (중앙값)")
t=G.groupby('off').agg(매수가_최저대비=('dist','median'),최대배수_1년=('up365','median'),최대배수_하위25=('up365',lambda x:x.quantile(.25)),
    두배_도달률=('t2',lambda x:x.notna().mean()),두배_일수=('t2','median'),세배_도달률=('t3',lambda x:x.notna().mean()),다섯배_도달률=('t5',lambda x:x.notna().mean()))
print(t.round(2).to_string())
print("\n== ③ 실시간 규칙 (D 이후 정보만)")
t=Rr.groupby('rule').apply(lambda g: pd.Series({'n':len(g),'체결률':g.filled.mean(),'체결 중앙일':g.day.median(),'매수가(바닥=1)':g.entry.median(),
    '1년최저 대비 거리':g.dist.median(),'1년 최대배수':g.up365.median(),'2배 도달률':g.t2.notna().sum()/len(g),'3배 도달률':g.t3.notna().sum()/len(g)}))
print(t.round(2).to_string())
