# E. 그림 4장 (밝은 배경, 같은 3색: 파랑=과거/넥라인 먼저, 주황=이번/하락 지속, 청록=깨진 뒤 바닥)
import sys; sys.path.insert(0,'scripts')
from common import *
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
plt.rcParams.update({'font.family':'WenQuanYi Zen Hei','axes.unicode_minus':False,'font.size':10,
  'axes.edgecolor':'#bbbbbb','axes.labelcolor':'#191919','xtick.color':'#666666','ytick.color':'#666666',
  'axes.grid':True,'grid.color':'#e6e6e6','grid.linewidth':0.6,'axes.spines.top':False,'axes.spines.right':False,
  'text.color':'#191919','figure.dpi':100,'savefig.dpi':200,'lines.linewidth':2})
BLUE,ORANGE,AQUA,TXT,SUB,GRAY='#257de0','#f47230','#00b894','#191919','#666666','#9c9c9c'
A=pd.read_csv(f'{OUT}/a_cycles.csv'); A=A[A.시대=='2010~']
pk=IDX.get_loc(pd.Timestamp(NOW_PEAK)); now=C[pk:]/C[pk]*100-100
# ---------- u1 큰 그림: 고점 기준 겹쳐 보기
fig,axs=plt.subplots(2,3,figsize=(15,8),sharey=True)
for ax,r in zip(axs.flat,A.itertuples()):
    a=IDX.get_loc(pd.Timestamp(r.고점)); b=IDX.get_loc(pd.Timestamp(r.바닥)); e=min(N,b+60)
    y=C[a:e]/C[a]*100-100; x=np.arange(len(y))
    ax.plot(x,y,color=BLUE,label=f'{r.고점[:7]} 사이클')
    ax.plot(np.arange(len(now)),now,color=ORANGE,label='이번 (2026-06-22 고점)')
    f=IDX.get_loc(pd.Timestamp(r.첫저점))
    ax.scatter([f-a],[C[f]/C[a]*100-100],s=40,color=BLUE,edgecolor='white',linewidth=1.5,zorder=5)
    ax.scatter([b-a],[r.낙폭*100],s=60,marker='v',color=BLUE,edgecolor='white',linewidth=1.5,zorder=5)
    ax.text(0.02,0.11,f'● ① 첫 저점 {r.첫저점낙폭*100:.0f}% → 반등 +{r.첫저점뒤반등*100:.0f}%' if r.첫저점뒤반등==r.첫저점뒤반등 else '● ① 첫 저점 = 최종 바닥',transform=ax.transAxes,ha='left',va='bottom',fontsize=8.5,color=TXT)
    ax.text(0.02,0.03,f'▼ 최종 바닥 {r.낙폭*100:.0f}% ({r.모양})',transform=ax.transAxes,ha='left',va='bottom',fontsize=8.5,color=TXT)
    ax.set_title(f'{r.고점[:7]} 고점 → {r.바닥[:7]} 바닥 ({r.개월:.1f}개월)',fontsize=10.5,loc='left')
    ax.axhline(0,color='#cccccc',lw=0.8)
    ax.set_xlim(0,max(len(y),len(now))+5)
axs[0,0].set_ylabel('고점 대비 (%)'); axs[1,0].set_ylabel('고점 대비 (%)')
for ax in axs[1]: ax.set_xlabel('고점 뒤 거래일')
h_,l_=axs[0,0].get_legend_handles_labels(); fig.legend(h_,['과거 사이클 (각 칸 제목)','이번 (2026-06-22 고점)'],loc='upper right',ncol=2,frameon=False,fontsize=10)
for ax in axs.flat: ax.set_ylim(-50,8)
fig.suptitle('SOX 큰 그림: 2010년 이후 사이클 6번(파랑)과 이번 사이클(주황)을 고점 기준으로 겹침',fontsize=13,x=0.01,ha='left')
fig.text(0.01,0.005,'이번 사이클: ① 7/29 첫 저점 -28.6% → ② 10/6까지 +26.5% 반등 → ③ 11/2 첫 저점 붕괴 → 11/20 종가 -42.5%, 11/25 장중 -44.5%',fontsize=9.5,color=SUB)
fig.tight_layout(rect=(0,0.03,1,0.95)); fig.savefig(f'{CH}/u1_big_picture.png'); plt.close(fig)
# ---------- u2 바닥 모양: 바닥 ±40일, 바닥 장중 저가 = 0%
fig,axs=plt.subplots(2,4,figsize=(16,7.5),sharey=True)
BD={'2011-10-03':'2011-10-04','2022-10-14':'2022-10-13','2025-04-08':'2025-04-07'}
cases=[(BD.get(r.바닥,r.바닥),f'{BD.get(r.바닥,r.바닥)} ({r.모양})') for r in A.itertuples()]
for ax,(bt,title) in zip(axs.flat,cases+[('2026-11-25','지금: 2026-11-25 장중 저점')]):
    b=IDX.get_loc(pd.Timestamp(bt)); base=Lo[b]; s=max(0,b-40); e=min(N,b+41)
    x=np.arange(s,e)-b
    ax.vlines(x,Lo[s:e]/base*100-100,H[s:e]/base*100-100,color=GRAY,lw=1.2)
    col=ORANGE if bt.startswith('2026') else BLUE
    ax.plot(x,C[s:e]/base*100-100,color=col,lw=1.8)
    ax.axhline(0,color='#cccccc',lw=0.8); ax.axvline(0,color='#dddddd',lw=0.8)
    ax.set_title(title,fontsize=10.5,loc='left'); ax.set_xlim(-41,41); ax.set_ylim(-5,62)
axs.flat[-1].axis('off')
axs.flat[-1].text(0.02,0.95,'읽는 법\n· 회색 막대 = 하루 고가~저가\n· 선 = 종가\n· 0% = 그 바닥날 장중 저가\n· 가로축 = 바닥 앞뒤 거래일\n\n2010년 이후 바닥 6번:\n이중바닥(W) 3번, 단일 바닥(V) 3번.\nW 3번의 마지막 저점은 모두\n앞 저점을 장중에 살짝 깨고 끝남\n(2011 -1.0%, 2016 -1.9%, 2018 -4.5%)\n지금 11/25도 11/20 저점을 -2.6% 깸',
    transform=axs.flat[-1].transAxes,va='top',fontsize=10,color=TXT,linespacing=1.6)
for ax in axs[:,0]: ax.set_ylabel('바닥 장중 저가 대비 (%)')
fig.suptitle('SOX 바닥 모양: 2010년 이후 사이클 바닥 6번과 지금',fontsize=13,x=0.01,ha='left')
fig.tight_layout(rect=(0,0,1,0.95)); fig.savefig(f'{CH}/u2_bottom_shapes.png'); plt.close(fig)
# ---------- u3 지금: SOXX·SOXL 일봉 (6월~)
def candles(ax,df,col_up=BLUE,col_dn=ORANGE):
    x=np.arange(len(df))
    up=df.close>=df.open
    ax.vlines(x,df.low,df.high,color=np.where(up,col_up,col_dn),lw=0.9)
    ax.bar(x,(df.close-df.open).abs().clip(lower=df.close*0.002),bottom=np.minimum(df.open,df.close),width=0.7,color=np.where(up,col_up,col_dn),linewidth=0)
    return x
fig,axs=plt.subplots(2,1,figsize=(14,10),gridspec_kw={'height_ratios':[1.25,1]})
for ax,df,lv,nm in ((axs[0],SOXX['2026-06-01':],[(142.27,'넥라인 142.27 (11/23 고가) — 종가로 넘으면 W 성공'),(122.20,'11/20 저점 122.20'),(118.18,'11/25 저점 118.18 — 다시 깨지면 한 번 더 하락'),(102.0,'역대 바닥 기준선(200주선×1.12) 부근 ≈ 102~106')],'SOXX (11/5 3:1 분할 반영)'),
                    (axs[1],SOXL['2026-06-01':],[(44.85,'넥라인 44.85'),(29.82,'11/20 저점 29.82'),(24.61,'11/25 저점 24.61')],'SOXL')):
    x=candles(ax,df)
    for v,t in lv:
        ax.axhline(v,color=SUB if '기준선' not in t else AQUA,lw=0.9,ls='--')
        ax.text(1,v,t,fontsize=9,color=TXT,va='top' if ('11/25' in t) else 'bottom')
    ax.set_xticks(x[::10]); ax.set_xticklabels([d_.strftime('%m/%d') for d_ in df.index[::10]])
    ax.set_title(f'{nm} 일봉 (2026-06-01 ~ 11-25)',fontsize=11.5,loc='left'); ax.set_xlim(-1,len(df)+1)
axs[1].set_yscale('log'); axs[1].set_yticks([20,30,40,60,100,150,200,300]); axs[1].set_yticklabels(['20','30','40','60','100','150','200','300'])
fig.suptitle('지금 위치: 11/20 바닥 → 11/23 +14% 반등 → 11/25 장중 11/20 저점을 깨고 그날 고가 근처 마감(스프링)',fontsize=12.5,x=0.01,ha='left')
fig.tight_layout(rect=(0,0,1,0.96)); fig.savefig(f'{CH}/u3_now_soxx_soxl.png'); plt.close(fig)
# ---------- u4 스프링 뒤 경로 (과거 16번, 결말별 색)
S3=pd.read_csv(f'{OUT}/b3_springs.csv',parse_dates=['날짜'])
kinds=[l.split('→ ')[1] for l in open(f'{OUT}/b_events.txt').read().split('== B5')[1].splitlines() if '→' in l]
done=S3[S3.결과!='진행중'].reset_index(drop=True)
groups=[('넥라인 먼저 돌파',BLUE,lambda k:k.startswith('넥라인')),('깨진 뒤 30일 안 주가 최종 바닥 (모두 고점 8개월 뒤)',AQUA,lambda k:'사이클 바닥' in k and not k.startswith('넥라인')),('깨진 뒤 하락 지속 (고점 7개월 안 4번 모두 여기)',ORANGE,lambda k:'하락 지속' in k)]
fig,axs=plt.subplots(1,3,figsize=(16,6.5),sharey=True)
b=N-1; nowy=C[b]/Lo[b]*100-100
for ax,(nm,col,f) in zip(axs,groups):
    sel=[(r,k) for r,k in zip(done.itertuples(),kinds) if f(k)]
    ends=[]
    for r,k in sel:
        bb=int(r.b); e=min(N,bb+41); y=C[bb:e]/Lo[bb]*100-100
        ax.plot(np.arange(len(y)),y,color=col,lw=1.6)
        ends.append([len(y)-1,y[-1],r.날짜.strftime('%Y-%m')])
    ends.sort(key=lambda t:t[1]); 
    for q in range(1,len(ends)):
        if ends[q][1]-ends[q-1][1]<4.5: ends[q][1]=ends[q-1][1]+4.5
    for x_,y_,t in ends: ax.text(x_+0.8,y_,t,fontsize=8.5,color=SUB,va='center')
    ax.scatter([0],[nowy],s=80,color='#191919',zorder=6,edgecolor='white',linewidth=2)
    ax.axhline(0,color='#888888',lw=1)
    ax.set_title(f'{nm} ({len(sel)}번)',fontsize=11.5,loc='left'); ax.set_xlim(-1,50); ax.set_ylim(-35,80)
    ax.set_xlabel('스프링 날 뒤 거래일')
axs[0].set_ylabel('스프링 날 장중 저가 대비 종가 (%)')
axs[0].annotate('● 지금 (11/25 종가 +7.9%)',(0,nowy),xytext=(3,45),fontsize=9.5,color=TXT,arrowprops=dict(arrowstyle='-',color='#888888',lw=0.8))
fig.suptitle('SOX 약세장 스프링(직전 저점을 장중에 깨고 그 위로 마감) 16번의 그 뒤 40거래일 — 0선 아래로 내려가면 스프링 날 저점이 다시 깨진 것',fontsize=12,x=0.01,ha='left')
fig.tight_layout(rect=(0,0,1,0.94)); fig.savefig(f'{CH}/u4_after_spring.png'); plt.close(fig)
print('saved')
