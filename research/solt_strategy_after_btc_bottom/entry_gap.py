# E. 진짜 바닥 후 첫 진입은 바닥에서 얼마나 늦나 / 실제 SOLT 지연별 결과
from sigs import *
BOTTOMS2={k:v for k,v in BOTTOMS.items()}
rows=[]
for D,assets in BOTTOMS2.items():
    D=pd.Timestamp(D)
    for a in assets+['btc']:
        p=P(a)
        if p.index[0]>D-pd.Timedelta(days=200): continue
        sig=band_sig(p,25,0.0,2); w=p[D-pd.Timedelta(days=10):D+pd.Timedelta(days=60)]
        lowd=w.idxmin(); low=w.min()
        on=sig[D:][sig[D:]==1]
        if on.empty: continue
        e=on.index[0]; ei=p.index.get_loc(e); ex=p.index[min(ei+1,len(p)-1)]   # 신호 다음 거래일 체결
        nav=lev2(p[D-pd.Timedelta(days=30):],COST)
        rows.append(dict(D=D.date(),asset=a,진입까지일=(ex-D).days,기초자산_저점대비=p[ex]/low-1,SOLT형_바닥일대비=nav[ex]/nav[nav.index[nav.index.searchsorted(D)]]-1))
r=pd.DataFrame(rows); pd.set_option('display.width',200)
print("== 진짜 바닥 이후 첫 매수 체결: 바닥일로부터 일수, 기초자산 저점 대비 가격, 2배 상품의 바닥일 대비")
print(r.groupby('D')[['진입까지일','기초자산_저점대비','SOLT형_바닥일대비']].median().round(2).to_string())
print("전체 중앙:", r[['진입까지일','기초자산_저점대비','SOLT형_바닥일대비']].median().round(2).to_dict())
print("SOL 2022:", r[r.asset=='sol'].round(2).to_dict('records'))
# 실제 SOLT, 지연 1/2/3
p=P('sol'); sig=band_sig(p,25,0.0,2); a=solt.reindex(p.index).dropna()
for lag in [1,2,3]:
    pos=sig.shift(lag).reindex(a.index).fillna(0); held=pos.shift(1).fillna(0); held.iloc[0]=0
    g=(1+held*a.pct_change().fillna(0))*(1-0.002*held.diff().abs().fillna(0))
    first=held[held==1].index[0]
    print(f"실제 SOLT 지연{lag}: 규칙 {g.prod():.2f}배 (첫 보유 {first.date()}), 같은 날부터 계속보유 {a.iloc[-1]/a[a.index<first].iloc[-1]:.2f}배, 노출 {held.mean():.0%}")
