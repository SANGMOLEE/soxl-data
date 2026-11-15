# A2. 핵심 바닥 상세: 1분 단위 BTC·SOL 저점, 바닥 국면(-30일~+60일)의 SOL 최저, SOLT 실제 가격
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',260)
b1=m1('BTC'); s1=m1('SOL')
KEY=[('2021-07-20','중간 조정 저점'),('2022-01-24','약세장 1차'),('2022-06-18','약세장 투매(가짜 바닥)'),('2022-11-09','FTX 투매'),
     ('2022-11-21','BTC 사이클 최저'),('2022-12-30','BTC 마지막 눌림 / SOL 최저'),('2024-08-05','엔캐리 투매'),('2025-04-07','관세 투매'),
     ('2025-11-21','약세장 1차'),('2026-02-06','2026 투매'),('2026-06-05','2026-06 SOL 최저 부근'),('2026-07-01','2026 BTC 최저(현재까지)'),('2026-11-14','최근 급락')]
rows=[]
for d,lab in KEY:
    d=pd.Timestamp(d,tz='UTC'); w=b1.l[d-pd.Timedelta(days=2):d+pd.Timedelta(days=2)]; tb=w.idxmin(); lb=w.min()
    ws=s1.l[tb-pd.Timedelta(hours=6):tb+pd.Timedelta(hours=6)]; ts6=ws.idxmin()
    wper=s1.l[tb-pd.Timedelta(days=30):tb+pd.Timedelta(days=60)]; tsp=wper.idxmin(); lsp=wper.min()
    s_at=s1.l[tb]
    rows.append(dict(바닥=lab,BTC저점_UTC=tb.strftime('%Y-%m-%d %H:%M'),ET=tb.tz_convert('America/New_York').strftime('%a %H:%M'),SOLT시간대=session_of(tb),BTC=round(lb),
        SOL_같은분=round(s_at,2),SOL_6h내최저=round(ws.min(),2),시차_분=int((ts6-tb).total_seconds()/60),
        국면최저SOL=round(lsp,2),국면최저일=tsp.strftime('%Y-%m-%d %H:%M'),국면최저까지_일=round((tsp-tb).total_seconds()/86400,1),
        국면최저_대비_BTC저점순간=s_at/lsp-1, 그때BTC_대비=b1.c.asof(tsp)/lb-1))
K=pd.DataFrame(rows); print(K.round(3).to_string(index=False)); K.to_csv('output/a2_key_bottoms.csv',index=False)
