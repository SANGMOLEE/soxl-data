# F. 차트: 핵심 바닥별 BTC·SOL 5분봉 정렬 + SOLT 실제 vs 이론
import sys; sys.path.insert(0,'scripts')
from common import *
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib import font_manager as fm
for f in fm.findSystemFonts(): 
    if 'NanumGothic.ttf' in f: fm.fontManager.addfont(f)
plt.rcParams['font.family']='NanumGothic'; plt.rcParams['axes.unicode_minus']=False
b1=m1('BTC'); s1=m1('SOL')
KEYS=[('2022-11-21 21:52','BTC 사이클 최저 (조용한 바닥)',3),('2022-12-30 14:49','SOL 최저(12/29) · BTC 마지막 눌림',3),
      ('2024-08-05 06:24','2024-08 엔캐리 투매',2),('2025-04-07 07:04','2025-04 관세 투매',2),('2026-02-06 00:19','2026-02 투매',2),
      ('2026-07-01 01:13','2026-07 BTC 최저 (SOL은 6/6)',30),('2026-11-15 01:45','2026-11 최근 급락 (토요일 밤)',2)]
fig,axes=plt.subplots(len(KEYS),1,figsize=(12,3.0*len(KEYS)))
for ax,(t,lab,span) in zip(axes,KEYS):
    t=pd.Timestamp(t,tz='UTC'); a,b_=t-pd.Timedelta(days=span),t+pd.Timedelta(days=span)
    rule='5min' if span<=3 else '1h'
    bb=b1.c[a:b_].resample(rule).last(); ss=s1.c[a:b_].resample(rule).last()
    ax.plot(bb.index,(bb/b1.l[t]-1)*100,color='#f7931a',lw=1.1,label='BTC')
    ax.plot(ss.index,(ss/s1.l[t]-1)*100,color='#7b3fe4',lw=1.1,label='SOL')
    ax.axvline(t,color='k',ls='--',lw=0.8)
    # SOLT 거래 불가(주말) 음영
    rng=pd.date_range(a.floor('h'),b_,freq='1h')
    closed=[x for x in rng if session_of(x)=='weekend_closed']
    for x in closed: ax.axvspan(x,x+pd.Timedelta(hours=1),color='#cccccc',alpha=0.35,lw=0)
    ws=s1.l[t-pd.Timedelta(days=span):t+pd.Timedelta(days=span)]; tsl=ws.idxmin()
    ax.scatter([tsl],[(ws.min()/s1.l[t]-1)*100],color='#7b3fe4',zorder=5,s=25)
    ax.set_title(f"{lab} — BTC 저점 {t.strftime('%Y-%m-%d %H:%M')} UTC (점선), 보라 점 = 구간 내 SOL 최저, 회색 = SOLT 거래 불가(주말)",fontsize=9.5)
    ax.set_ylabel('저점 대비 %'); ax.grid(alpha=0.3); ax.legend(loc='upper left',fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H시' if span<=3 else '%m-%d'))
plt.tight_layout(); plt.savefig('charts/f1_btc_sol_bottoms.png',dpi=110); plt.close()
# SOLT 실제(야후+BOATS) vs 이론 (SOL 1분봉 + 직전 정규장 종가)
S=solt24()
reg=S[(S.src=='yahoo')&(S.et.dt.strftime('%H:%M')=='15:30')]
ref=pd.DataFrame({'P0':reg.c.values,'S0':[s1.c.asof(t+pd.Timedelta(minutes=29)) for t in reg.index]},index=reg.index+pd.Timedelta(minutes=30))
def fair(t):
    r=ref[ref.index<=t]; P0,S0=r.iloc[-1]; return P0*(1+2*(s1.c.asof(t)/S0-1))
fig,axes=plt.subplots(3,1,figsize=(12,10))
for ax,(a,b_,lab) in zip(axes,[('2025-04-05','2025-04-10','2025-04 관세 투매'),('2026-02-04','2026-02-08','2026-02 투매 (시간외 급락)'),('2026-11-11','2026-11-16','2026-11 최근')]):
    a=pd.Timestamp(a,tz='UTC'); b_=pd.Timestamp(b_,tz='UTC')
    x=S[a:b_]; tt=pd.date_range(a,min(b_,s1.index[-1]),freq='15min'); fv=[fair(t) for t in tt]
    ax.plot(tt,fv,color='#999999',lw=1,label='이론 SOLT (SOL 실시간 × 2배)')
    for src,colr in [('yahoo','#1f77b4'),('boats','#d62728')]:
        y=x[x.src==src]; ax.vlines(y.index+pd.Timedelta(minutes=30),y.l,y.h,color=colr,lw=2.2,label='실제 SOLT '+('프리/정규/애프터' if src=='yahoo' else '블루오션 야간'))
    for xx in pd.date_range(a,b_,freq='1h'):
        if session_of(xx)=='weekend_closed': ax.axvspan(xx,xx+pd.Timedelta(hours=1),color='#cccccc',alpha=0.35,lw=0)
    ax.set_title(lab+' — 회색 음영 = 주말(거래 불가)',fontsize=10); ax.grid(alpha=0.3); ax.legend(fontsize=8,loc='upper right')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H시'))
plt.tight_layout(); plt.savefig('charts/f2_solt_actual_vs_fair.png',dpi=110); plt.close()
print('charts saved')
