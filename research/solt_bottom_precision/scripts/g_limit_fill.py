# G. 지정가 사다리 체결 검증: SOL이 직전 정규장 종가 대비 -x%에 닿은 시간에, 그 SOL 가격에 해당하는 SOLT 이론가 지정가가 실제 체결됐나
import sys; sys.path.insert(0,'scripts')
from common import *
s1=m1('SOL'); S=solt24()
hm=S.et.dt.strftime('%H:%M'); S['end']=S.index+pd.to_timedelta(np.where((S.src=='yahoo')&hm.isin(['09:00','15:30']),30,60),unit='m')
reg=S[(S.src=='yahoo')&(hm=='15:30')]
ref=pd.DataFrame({'P0':reg.c.values,'S0':[s1.c.asof(t+pd.Timedelta(minutes=29)) for t in reg.index]},index=reg.index+pd.Timedelta(minutes=30))
rows=[]
for t,bar in S.iterrows():
    r=ref[ref.index<=t]
    if r.empty: continue
    P0,S0=r.iloc[-1]; w=s1[t:bar.end-pd.Timedelta(minutes=1)]
    if w.empty: continue
    sol_lo=w.l.min()
    for x in [0.06,0.10,0.15,0.20]:
        lvl=S0*(1-x)
        if sol_lo<=lvl:
            lim=P0*(1-2*x)                                 # 그 SOL 가격의 SOLT 이론가에 지정가
            # 그 SOL 레벨에 머문 분(minute) 수
            mins=int((w.l<=lvl).sum())
            rows.append(dict(t=t,sess=session_of(t),x=x,filled=bar.l<=lim,fill_gap=bar.l/lim-1,mins_below=mins))
R=pd.DataFrame(rows)
# 같은 날 같은 x는 첫 터치만
R['day']=R.t.dt.tz_convert('America/New_York').dt.date; R=R.sort_values('t').drop_duplicates(['day','x'])
print("== SOL이 직전 정규장 종가 대비 -x%를 처음 터치한 시간봉에서, SOLT 이론가 지정가가 같은 봉 안에 체결됐나 (2025-03~2026-11)")
print(R.groupby(['x','sess']).agg(n=('filled','size'),체결률=('filled','mean'),SOLT저가_지정가대비_중앙=('fill_gap','median')).round(3).to_string())
print("\n머문 시간(분)별 체결률:"); R['stay']=pd.cut(R.mins_below,[0,5,15,60,1e9],labels=['≤5분','6~15분','16~60분','60분+'])
print(R.groupby('stay').filled.agg(['size','mean']).round(2).to_string())
R.to_csv('output/g_limit_fill.csv',index=False)
