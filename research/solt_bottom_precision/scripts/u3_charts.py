# U3. 사이클 바닥 차트 모양 그림 4종
#  u1 큰 그림(주봉) · u2 바닥 모양(일봉) · u3 바닥 기준 겹쳐보기 · u4 2026 현재
import sys; sys.path.insert(0,'scripts')
from u_chart_shape import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib import font_manager as fm
from matplotlib.ticker import FuncFormatter, NullFormatter, FixedLocator
for f in fm.findSystemFonts():
    if 'NanumGothic.ttf' in f or 'NanumGothicBold.ttf' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family':'NanumGothic','axes.unicode_minus':False,'text.parse_math':False,
    'axes.edgecolor':'#cfcfcf','axes.linewidth':0.6,'axes.labelcolor':'#666666','xtick.color':'#666666','ytick.color':'#666666',
    'axes.titlesize':10.5,'axes.titlecolor':'#191919','font.size':9,'figure.facecolor':'white','axes.facecolor':'white'})
UP,DN='#ec4647','#257de0'            # 한국식: 상승 빨강, 하락 파랑
TXT,TX2,GRID='#191919','#666666','#ececec'
NECK='#f47230'                        # 넥라인
SUP='#8a8a8a'                         # 직전 저점(지지선)
SER=['#257de0','#f47230','#00b894','#f2a600','#ee7fac','#008a17','#6a4ce2','#ec4647']
T=pd.read_csv('output/u_chart_shape.csv',parse_dates=['직전저점일','약세반등고점일','붕괴일','급반등고점일','재시험일','넥라인일','돌파일'])
T=T.set_index('사례')
SHAPE={'BTC 2011':'이중바닥(W) — 한 달 간격, 둘째 저점 +1.4%','BTC 2015':'투매 꼬리(스파이크) → 9개월 박스권',
       'BTC 2018':'충격 뒤 이중 저점 → 역헤드앤숄더형 박스','BTC 2020 (급락)':'V자 — 투매 당일 장대 아래꼬리',
       'BTC 2022':'이중바닥(0.7% 차이) → 7주 좁은 박스','BTC 2026 (진행)':'투매 망치형 → 재시험 +3.9% (진행 중)',
       'ETH 2018':'이중바닥(0.3% 차이) → V반등','ETH 2022':'투매 스파이크 → 재시험 +13%','SOL 2022':'계단식 하락 끝 투매 → V자'}
SYM={n:s for n,s,_,_ in CASES}; T0={n:pd.Timestamp(t) for n,_,t,_ in CASES}
def money(v,_=None):
    if v>=1000: return "$"+f"{v/1000:.1f}".rstrip('0').rstrip('.')+"k"
    if v>=100: return f"${v:.0f}"
    if v>=10: return f"${v:.0f}"
    return f"${v:.1f}" if v>=1 else f"${v:.2f}"
def logticks(ax,lo,hi):
    sets=[(1,2,5),(1,1.5,2,3,5,7),(1,1.2,1.5,2,2.5,3,4,5,6,7,8),(1,1.1,1.2,1.3,1.4,1.5,1.6,1.8,2,2.2,2.5,2.8,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5)]
    for S in sets:
        tk=[m*10**e for e in range(-2,7) for m in S if lo<=m*10**e<=hi]
        if len(tk)>=4: break
    while len(tk)>8: tk=tk[::2]
    ax.set_yscale('log'); ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FuncFormatter(money))
    ax.yaxis.set_minor_formatter(NullFormatter()); ax.yaxis.set_minor_locator(FixedLocator([]))
    k=hi/lo; ax.set_ylim(lo/k**0.16,hi*k**0.12)
def candles(ax,df,width):
    x=mdates.date2num(df.index.to_pydatetime()); up=(df.c>=df.o).values; col=np.where(up,UP,DN)
    ax.vlines(x,df.l,df.h,color=col,lw=0.7,zorder=2)
    lo=np.minimum(df.o,df.c).values; hi=np.maximum(df.o,df.c).values; hi=np.maximum(hi,lo*1.002)
    ax.bar(x,hi-lo,bottom=lo,width=width,color=col,linewidth=0,zorder=3)
def style(ax):
    ax.grid(axis='y',color=GRID,lw=0.6); ax.set_axisbelow(True)
    for s in ['top','right']: ax.spines[s].set_visible(False)
BOUNDS={}
def note(ax,x,y,text,dy=-28,dx=0,ha=None):
    x=pd.Timestamp(x); bd=BOUNDS.get(id(ax))
    if bd is not None:
        f=(x-bd[0])/(bd[1]-bd[0])
        if f>0.80 and dx>=0: dx=-max(abs(dx),6)
        elif f<0.12 and dx<=0: dx=max(abs(dx),6)
    if ha is None: ha='right' if dx<0 else ('left' if dx>0 else 'center')
    ax.annotate(text,xy=(mdates.date2num(x),y),xytext=(dx,dy),textcoords='offset points',ha=ha,va='top' if dy<0 else 'bottom',
                fontsize=7.6,color=TXT,arrowprops=dict(arrowstyle='-',color=TX2,lw=0.6,shrinkA=0,shrinkB=1),zorder=6,
                bbox=dict(boxstyle='round,pad=0.15',fc='white',ec='none',alpha=0.85))
def datefmt(ax,span_days):
    if span_days>300: ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,4,7,10])); ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))
    elif span_days>120: ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))
    elif span_days>30: ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0,interval=2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    else: ax.xaxis.set_major_locator(mdates.DayLocator(interval=2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.tick_params(axis='x',labelsize=7.5)
D=pd.Timedelta
def dsrc(n):
    df=daily(SYM[n])
    if n=='BTC 2011':
        df=df.copy(); df['h']=np.minimum(df.h,df[['o','c']].max(axis=1)*1.5)   # 비트스탬프 2011 얇은 거래의 튀는 고가 제거
    return df

# ───────── u1: 큰 그림 (주봉) ─────────
big=['BTC 2011','BTC 2015','BTC 2018','BTC 2020 (급락)','BTC 2022','BTC 2026 (진행)']
fig,axes=plt.subplots(2,3,figsize=(15,8.6)); axes=axes.ravel()
for ax,n in zip(axes,big):
    r=T.loc[n]; df=dsrc(n); t0=T0[n]
    a=max(df.index[0],r.직전저점일-D(days=150)); b=min(df.index[-1],t0+D(days=200)); BOUNDS[id(ax)]=(a,b)
    wk=weekly(df[a:b]); candles(ax,wk,5.0); style(ax)
    logticks(ax,wk.l.min(),wk.h.max())
    ax.hlines(r.직전저점,mdates.date2num(r.직전저점일),mdates.date2num(min(b,t0+D(days=60))),color=SUP,lw=0.9,zorder=4)
    note(ax,r.직전저점일,r.직전저점,f"① 첫 저점 {money(r.직전저점)}",dy=-22)
    note(ax,r.약세반등고점일,df.h[r.약세반등고점일],f"② 약세장 반등 +{r.약세반등*100:.0f}%",dy=12)
    note(ax,t0,r.최종바닥,f"③ 최종 바닥 {money(r.최종바닥)}\n(첫 저점 {r.직전저점대비*100:+.0f}%)",dy=-10,dx=14)
    if pd.notna(r.돌파일):
        note(ax,r.돌파일,df.c[r.돌파일],f"④ 넥라인 돌파\n(바닥 +{r.돌파시상승*100:.0f}%)",dy=-34,dx=44 if n=='BTC 2022' else 12)
    ax.set_title(f"{n}: {SHAPE[n]}",loc='left')
    datefmt(ax,(b-a).days); ax.set_xlim(mdates.date2num(a-D(days=7)),mdates.date2num(b+D(days=10)))
fig.suptitle('BTC 사이클 바닥의 큰 그림 (주봉, 로그): ① 첫 저점 → ② 약세장 반등 → 회색선(첫 저점) 붕괴 → ③ 최종 바닥 → ④ 넥라인 돌파   ·   빨강=상승 주, 파랑=하락 주',
             fontsize=11,color=TXT,x=0.01,ha='left')
plt.tight_layout(rect=(0,0,1,0.965)); plt.savefig('charts/u1_big_picture_weekly.png',dpi=110); plt.close()

# ───────── u2: 바닥 모양 (일봉) ─────────
U2=pd.read_csv('output/u2_after_pivots.csv',parse_dates=['충격저점']).set_index('사례')
fig,axes=plt.subplots(3,3,figsize=(15,12)); axes=axes.ravel()
for ax,n in zip(axes,[c[0] for c in CASES]):
    r=T.loc[n]; df=dsrc(n); t0=T0[n]
    a=t0-D(days=40); b=min(df.index[-1],t0+D(days=80)); x=df[a:b]; BOUNDS[id(ax)]=(a,b)
    candles(ax,x,0.7); style(ax); logticks(ax,x.l.min(),x.h.max())
    u=U2.loc[n]
    if pd.notna(u.충격저점) and u.충격저점>=a and abs(u.충격대비)<0.15:
        note(ax,u.충격저점,u.충격저점가,f"충격 저점 {money(u.충격저점가)}",dy=-12,dx=-14)
    note(ax,t0,r.최종바닥,f"최종 바닥 {money(r.최종바닥)}",dy=-24,dx=10)
    if n=='BTC 2020 (급락)': note(ax,pd.Timestamp('2020-03-16'),4442.0,"3일 뒤 재시험 +17%",dy=-10,dx=16)
    if n=='BTC 2022': note(ax,pd.Timestamp('2022-11-09'),15588.0,"11/9 FTX 저점 $15.6k",dy=-12,dx=-14)
    if pd.notna(r.급반등고점일):
        note(ax,r.급반등고점일,df.h[r.급반등고점일],f"첫 반등 +{r.급반등*100:.0f}%",dy=10)
    if pd.notna(r.재시험일) and r.재시험일<=b:
        note(ax,r.재시험일,r.재시험저점,f"재시험 +{r.재시험_바닥대비*100:.1f}%",dy=-14,dx=10)
    if pd.notna(r.넥라인):
        e=r.돌파일 if pd.notna(r.돌파일) and r.돌파일<=b else b
        ax.hlines(r.넥라인,mdates.date2num(r.넥라인일),mdates.date2num(e),color=NECK,lw=1.0,zorder=4)
        if pd.notna(r.돌파일) and r.돌파일<=b:
            note(ax,r.돌파일,df.c[r.돌파일],f"넥라인 돌파 +{r.돌파시상승*100:.0f}%",dy=16,dx=12)
    ax.axvline(mdates.date2num(t0),color=GRID,lw=6,zorder=0)
    ax.set_title(f"{n}: {SHAPE[n]}",loc='left',fontsize=9.8)
    datefmt(ax,(b-a).days); ax.set_xlim(mdates.date2num(a-D(days=1)),mdates.date2num(b+D(days=2)))
fig.suptitle('사이클 바닥 앞뒤 120일 (일봉, 로그): 회색 띠 = 최종 바닥일, 주황선 = 넥라인(첫 반등 고점)   ·   빨강=상승일, 파랑=하락일',fontsize=11,color=TXT,x=0.01,ha='left')
plt.tight_layout(rect=(0,0,1,0.97)); plt.savefig('charts/u2_bottom_shapes_daily.png',dpi=110); plt.close()

# ───────── u3: 최종 바닥 기준 겹쳐보기 ─────────
fig,axes=plt.subplots(1,2,figsize=(15,6.2))
groups=[('BTC: 최종 바닥 = 1 로 맞춘 일봉 종가',['BTC 2015','BTC 2018','BTC 2020 (급락)','BTC 2022'],'BTC 2026 (진행)'),
        ('ETH·SOL: 최종 바닥 = 1',['ETH 2018','ETH 2022','SOL 2022'],None)]
for ax,(tt,names,now) in zip(axes,groups):
    allv=[]
    for i,n in enumerate(names+([now] if now else [])):
        df=daily(SYM[n]); t0=T0[n]; L0=T.loc[n].최종바닥
        s=df.c[t0-D(days=90):t0+D(days=150)]/L0; xx=(s.index-t0).days
        isnow=(n==now); col=TXT if isnow else SER[i]
        ax.plot(xx,s.values,color=col,lw=2.4 if isnow else 1.5,zorder=5 if isnow else 3,label=n)
        ax.text(xx[-1]+2,s.values[-1]*(1.03 if n=='ETH 2018' else 0.97 if n=='SOL 2022' else 1),n.replace(' (급락)','').replace(' (진행)',' 지금'),color=TXT,fontsize=8,va='center')
        allv+=list(s.values)
    if now is None:   # SOL 2026 (11/21 저점 기준) 함께
        df=daily('SOL'); t0=pd.Timestamp('2026-11-21'); L0=df.l[t0]; s=df.c[t0-D(days=90):]/L0; xx=(s.index-t0).days
        ax.plot(xx,s.values,color=TXT,lw=2.4,zorder=5,label='SOL 2026 (11/21 저점 기준)'); ax.text(xx[-1]+2,s.values[-1],'SOL 지금',fontsize=8,va='center'); allv+=list(s.values)
    ax.axvline(0,color=TX2,lw=0.6); ax.axhline(1,color=TX2,lw=0.6)
    lo,hi=min(allv),max(allv); ax.set_yscale('log')
    tk=[v for v in [0.8,1,1.25,1.5,2,3,4,6] if lo*0.95<=v<=hi*1.05]+[v for v in [1.5,2,2.5,3] if False]
    ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"×{v:g}")); ax.yaxis.set_minor_formatter(NullFormatter()); ax.yaxis.set_minor_locator(FixedLocator([]))
    style(ax); ax.set_xlabel('최종 바닥 기준 일수',labelpad=2); ax.set_title(tt,loc='left'); ax.set_xlim(-92,175)
    ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.13),ncol=5,fontsize=8,frameon=False)
fig.suptitle('바닥 앞뒤 모양 겹쳐보기 (종가 기준, 로그): 바닥 전 90일의 하락 모양과 바닥 후 150일의 반등·재시험 모양',fontsize=11,color=TXT,x=0.01,ha='left')
plt.tight_layout(rect=(0,0.02,1,0.95)); plt.savefig('charts/u3_overlay_from_bottom.png',dpi=110); plt.close()

# ───────── u4: 2026 현재 ─────────
fig=plt.figure(figsize=(15,16)); gs=fig.add_gridspec(4,1,height_ratios=[1.15,1,0.9,0.9])
ax=fig.add_subplot(gs[0]); df=daily('BTC')['2025-12-01':]; BOUNDS[id(ax)]=(df.index[0],df.index[-1]); candles(ax,df,0.7); style(ax); logticks(ax,df.l.min(),df.h.max())
for t,v,lab,dy,dx in [('2026-02-06',60000,'2/6 $60.0k',-16,0),('2026-06-05',59131,'6/5 $59.1k',-16,-10),('2026-07-01',57800,'7/1 $57.8k (첫 저점)',-16,30),
                      ('2026-09-21',87396,'9/21 $87.4k (약세장 반등 +51%)',10,0),('2026-11-21',55130,'11/21 $55.1k (최종 바닥 후보)',-16,-40)]:
    note(ax,pd.Timestamp(t),v,lab,dy=dy,dx=dx)
ax.hlines(57800,mdates.date2num(pd.Timestamp('2026-07-01')),mdates.date2num(df.index[-1]),color=SUP,lw=0.9)
ax.hlines(60000,mdates.date2num(pd.Timestamp('2026-02-06')),mdates.date2num(pd.Timestamp('2026-07-01')),color=SUP,lw=0.9)
ax.set_title('BTC 2026 일봉 (로그): 2~7월 $57.8~60k 바닥선 → 9월 반등 +51% → 11/20 바닥선 붕괴 → 11/21 $55.1k',loc='left')
datefmt(ax,400); ax.set_xlim(mdates.date2num(df.index[0]-D(days=2)),mdates.date2num(df.index[-1]+D(days=4)))
for k,(sym,lab) in enumerate([('BTC','BTC'),('SOL','SOL')]):
    ax=fig.add_subplot(gs[k+1]); h=bars(sym,'1h').tz_localize(None)['2026-11-12':]; BOUNDS[id(ax)]=(h.index[0],h.index[-1]); candles(ax,h,0.03); style(ax); logticks(ax,h.l.min(),h.h.max())
    if sym=='BTC':
        pts=[('2026-11-15 00:00',62006,'11/15 충격 저점 $62.0k',-16,0),('2026-11-21 06:00',55130,'11/21 바닥 $55.1k',-14,-40),
             ('2026-11-23 14:00',64603,'11/23 첫 반등 $64.6k (+17%)',10,0),('2026-11-25 14:00',57300,'11/25 재시험 $57.3k (+3.9%)',-14,30)]
        neck=64603
    else:
        lo=h.loc['2026-11-21'].l.idxmin(); hi=h.loc['2026-11-23'].h.idxmax(); rt=h.loc['2026-11-25'].l.idxmin()
        pts=[(lo,h.l[lo],f"11/21 바닥 ${h.l[lo]:.2f}",-14,-40),(hi,h.h[hi],f"11/23 첫 반등 ${h.h[hi]:.2f} (+{h.h[hi]/h.l[lo]*100-100:.0f}%)",10,0),
             (rt,h.l[rt],f"11/25 재시험 ${h.l[rt]:.2f} (+{h.l[rt]/h.l[lo]*100-100:.1f}%)",-14,30)]
        neck=h.h[hi]
    for t,v,labx,dy,dx in pts: note(ax,pd.Timestamp(t),v,labx,dy=dy,dx=dx)
    ax.hlines(neck,mdates.date2num(pd.Timestamp('2026-11-23 14:00')),mdates.date2num(h.index[-1]),color=NECK,lw=1.0)
    ax.text(mdates.date2num(h.index[-1]),neck,f" 넥라인 {money(neck) if sym=='BTC' else '$%.2f'%neck}",color=TXT,fontsize=8,va='bottom',ha='right')
    ax.set_title(f"{lab} 1시간봉 (UTC, 로그): 11/12 ~ {h.index[-1]:%m/%d %H}시",loc='left')
    datefmt(ax,15); ax.set_xlim(mdates.date2num(h.index[0]),mdates.date2num(h.index[-1]+D(hours=6)))
ax=fig.add_subplot(gs[3]); so=solt24()['2026-11-12':].tz_convert(None)[['o','h','l','c']]; BOUNDS[id(ax)]=(so.index[0],so.index[-1])
candles(ax,so,0.03); style(ax); logticks(ax,so.l.min(),so.h.max())
for t,lab,dy,dx in [(so['2026-11-20':'2026-11-21'].l.idxmin(),'11/20(금) 저점 ${:.2f}',-14,-30),(so['2026-11-23':'2026-11-23 23:59'].h.idxmax(),'11/23 첫 반등 ${:.2f}',10,0),
                    (so['2026-11-25':].l.idxmin(),'11/25 정규장 저점 ${:.2f}',-14,30)]:
    v=so.h[t] if '반등' in lab else so.l[t]; note(ax,t,v,lab.format(v),dy=dy,dx=dx)
for w0,w1 in [('2026-11-14 01:00','2026-11-16 01:00'),('2026-11-21 01:00','2026-11-23 01:00'),('2026-11-26 01:00','2026-11-27 01:00')]:
    ax.axvspan(mdates.date2num(pd.Timestamp(w0)),mdates.date2num(pd.Timestamp(w1)),color='#f4f4f4',zorder=0)
ax.text(mdates.date2num(pd.Timestamp('2026-11-26 13:00')),so.h.max(),'추수감사절\n휴장',ha='center',va='top',fontsize=7.6,color=TX2)
ax.text(mdates.date2num(pd.Timestamp('2026-11-22 01:00')),so.h.max(),'주말 휴장 (회색)\nBTC·SOL 바닥 11/21(토) 06:17 UTC',ha='center',va='top',fontsize=7.6,color=TX2)
ax.set_title('SOLT 1시간봉 (UTC, 로그, 야후 프리·정규·애프터 + 블루오션 야간): 주말 바닥은 못 사고, 평일 재시험(11/25)이 실제 최저가',loc='left')
datefmt(ax,15); ax.set_xlim(mdates.date2num(pd.Timestamp('2026-11-12')),mdates.date2num(bars('BTC','1h').tz_localize(None).index[-1]+D(hours=6)))
fig.suptitle('2026 지금의 모양: 큰 그림은 역대 "첫 저점 → 반등 → 붕괴 → 최종 바닥" 순서와 같고, 바닥 뒤에는 첫 반등과 더 높은 재시험까지 나온 상태',fontsize=11,color=TXT,x=0.01,ha='left')
plt.tight_layout(rect=(0,0,1,0.975)); plt.savefig('charts/u4_now_2026.png',dpi=110); plt.close()
print('saved u1~u4')
