# N. 이번 사례 차트: 11/21 토요일 저점 + 6월→11월 감가
import sys; sys.path.insert(0,'scripts')
from common import *
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'NanumGothic.ttf' in f: fm.fontManager.addfont(f)
plt.rcParams['font.family']='NanumGothic'; plt.rcParams['axes.unicode_minus']=False; plt.rcParams['text.usetex']=False; plt.rcParams['text.parse_math']=False
s1=m1('SOL'); b1=m1('BTC'); S=solt24(); cl=pd.read_parquet('data/synth_solt_daily.parquet')
fig,ax=plt.subplots(2,1,figsize=(12,9))
a,b_=pd.Timestamp('2026-11-19',tz='UTC'),pd.Timestamp('2026-11-25',tz='UTC'); t0=pd.Timestamp('2026-11-21 06:17',tz='UTC')
bb=b1.c[a:b_].resample('15min').last(); ss=s1.c[a:b_].resample('15min').last()
ax0=ax[0]; ax0.plot(bb.index,(bb/b1.l[t0]-1)*100,color='#f7931a',lw=1,label='BTC (11/21 저점 대비 %)'); ax0.plot(ss.index,(ss/s1.l[t0]-1)*100,color='#7b3fe4',lw=1,label='SOL (11/21 저점 대비 %)')
tt=pd.date_range(a,b_,freq='15min'); j=cl.index.searchsorted(tt,side='right')-1
fair=cl.nav.values[j]*(1+2*(s1.c.reindex(tt,method='ffill').values/cl.S.values[j]-1)); scale=22.80/ (cl.nav[cl.index<=pd.Timestamp('2026-11-20 21:00',tz='UTC')].iloc[-1])
ax1=ax0.twinx(); ax1.plot(tt,fair*scale,color='#999999',lw=1,label='SOLT 이론가($, 우축)')
x=S[a:b_]
for src,colr in [('yahoo','#1f77b4'),('boats','#d62728')]:
    y=x[x.src==src]; ax1.vlines(y.index+pd.Timedelta(minutes=30),y.l,y.h,color=colr,lw=2.5,label='실제 SOLT '+('프리/정규/애프터' if src=='yahoo' else '블루오션 야간'))
for xx in pd.date_range(a,b_,freq='1h'):
    if session_of(xx)=='weekend_closed': ax0.axvspan(xx,xx+pd.Timedelta(hours=1),color='#cccccc',alpha=0.35,lw=0)
ax0.axvline(t0,color='k',ls='--',lw=0.8); ax0.set_ylabel('저점 대비 %'); ax1.set_ylabel('SOLT $')
ax0.set_title('2026-11-21 06:17 UTC(토) BTC $55,130 · SOL $64.87 같은 분 저점 — 회색=SOLT 거래 불가(주말)',fontsize=10)
h0,l0=ax0.get_legend_handles_labels(); h1,l1=ax1.get_legend_handles_labels(); ax0.legend(h0+h1,l0+l1,fontsize=7.5,loc='upper left'); ax0.grid(alpha=0.3)
ax0.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H시'))
# 6월→11월: SOL vs SOLT 일봉
a2=pd.Timestamp('2026-05-20',tz='UTC'); sd=s1.c[a2:].resample('D').last(); sl=s1.l[a2:].resample('D').min()
sol_d=S[a2:].c.resample('D').last().dropna(); solt_l=S[a2:].l.resample('D').min().dropna()
axa=ax[1]; axa.plot(sd.index,sd,color='#7b3fe4',lw=1.2,label='SOL 종가 (좌)'); axb=axa.twinx(); axb.plot(sol_d.index,sol_d,color='#1f77b4',lw=1.2,label='SOLT 종가 (우)')
for t,lab in [('2026-06-06','SOL 6/6 저점 $60.13'),('2026-11-21','SOL 11/21 저점 $64.87 (6월보다 +8%)')]:
    axa.axvline(pd.Timestamp(t,tz='UTC'),color='#7b3fe4',ls=':',lw=0.8); axa.text(pd.Timestamp(t,tz='UTC'),sd.max()*0.98,lab,fontsize=8,color='#7b3fe4')
axb.axhline(23.28,color='#1f77b4',ls='--',lw=0.8); axb.text(sd.index[5],23.6,'SOLT 6월 장중 최저 $23.28',fontsize=8,color='#1f77b4')
axb.axhline(22.58,color='#d62728',ls='--',lw=0.8); axb.text(sd.index[60],21.9,'SOLT 11/20 장중 최저 $22.58 (6월보다 낮음)',fontsize=8,color='#d62728')
axa.set_title('감가: SOL은 6월보다 높은 저점, SOLT는 6월보다 낮은 저점 (2배 일일 재조정)',fontsize=10)
h0,l0=axa.get_legend_handles_labels(); h1,l1=axb.get_legend_handles_labels(); axa.legend(h0+h1,l0+l1,fontsize=8,loc='upper right'); axa.grid(alpha=0.3)
axa.set_ylim(55,128); axb.set_ylim(20,84)
plt.tight_layout(); plt.savefig('charts/n_btc_vs_solt_bottom_2026-11.png',dpi=110); print('saved')
