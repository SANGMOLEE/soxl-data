# U. 역대 사이클 바닥의 차트 모양: 큰 그림(첫 저점→약세장 반등→지지선 붕괴→최종 바닥) + 바닥 뒤(급반등→재시험→넥라인 돌파)
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',250); pd.set_option('display.max_columns',40)
BS=pd.read_csv(os.path.join(ROOT,'../solt_strategy_after_btc_bottom/data/BTC_BITSTAMP_1D.csv'),parse_dates=['date']).set_index('date').rename(columns={'open':'o','high':'h','low':'l','close':'c','volume':'v'})
def daily(sym):
    return BS if sym=='BTC_BS' else bars(sym,'1D').tz_localize(None)[['o','h','l','c','v']]
def rsi(c,n=14):
    d=c.diff(); up=d.clip(lower=0).ewm(alpha=1/n,adjust=False).mean(); dn=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean(); return 100-100/(1+up/dn)
def weekly(df): return df.resample('W-MON',label='left',closed='left').agg({'o':'first','h':'max','l':'min','c':'last','v':'sum'}).dropna()
# 사례: (이름, 자료, 최종 바닥일, 비고)
CASES=[('BTC 2011','BTC_BS','2011-10-20','비트스탬프(마운트곡스 11-18 $2.01)'),('BTC 2015','BTC_BS','2015-01-14',''),
       ('BTC 2018','BTC','2018-12-15',''),('BTC 2020 (급락)','BTC','2020-03-13','사이클 중간 급락'),('BTC 2022','BTC','2022-11-21',''),
       ('BTC 2026 (진행)','BTC','2026-11-21','11/26까지'),
       ('ETH 2018','ETH','2018-12-15',''),('ETH 2022','ETH','2022-06-18',''),('SOL 2022','SOL','2022-12-29','')]
END=None
def analyze(name,sym,t0s):
    df=daily(sym); t0=pd.Timestamp(t0s); D=pd.Timedelta
    last=df.index[-1]
    L0=df.l[t0]
    # 1) 직전 주요 저점 F: 최종 바닥 45~300일 전 최저 (자료 시작 이후)
    w=df[max(df.index[0],t0-D(days=300)):t0-D(days=45)]
    if name=='BTC 2011': w=df[:t0-D(days=30)]
    F=w.l.idxmin(); LF=w.l.min()
    R=df.h[F:t0].idxmax(); HR=df.h[F:t0].max()
    brk=df[(df.index>F+D(days=1))&(df.index<=t0)&(df.l<LF)].index[0]
    # 2) 바닥 뒤
    a=df[t0:t0+D(days=21)]; AR=a.h.idxmax(); HAR=a.h.max()
    rt=df[AR:t0+D(days=120)]; RT=rt.l.idxmin() if len(rt)>1 else None; LRT=rt.l.min() if RT is not None else np.nan
    if RT is not None and RT<=AR+D(days=0): RT=None
    nk_end=RT if RT is not None else AR
    NK=df.h[t0:nk_end].max(); NKd=df.h[t0:nk_end].idxmax()
    after=df[(df.index>nk_end)&(df.c>NK)] if RT is not None else df.iloc[0:0]
    BO=after.index[0] if len(after) else None
    rec=df[(df.index>t0)&(df.c>LF)]; REC=rec.index[0] if len(rec) else None
    # 3) 바닥 캔들
    c=df.loc[t0]; rng=c.h-c.l; wick=(min(c.o,c.c)-c.l)/rng if rng>0 else np.nan
    vm=df.v[t0]/df.v[t0-D(days=30):t0-D(days=1)].median()
    vmax=(df.v[t0-D(days=5):t0]/df.v[t0-D(days=35):t0-D(days=6)].median()).max()
    wk=weekly(df); wt=wk.index[wk.index<=t0][-1]; wc=wk.loc[wt]; wr=wc.h-wc.l; wwick=(min(wc.o,wc.c)-wc.l)/wr
    # 4) RSI 다이버전스 (일·주)
    r=rsi(df.c); rw=rsi(wk.c)
    rF=r[F-D(days=2):F+D(days=2)].min(); r0=r[t0-D(days=2):t0+D(days=2)].min()
    wF=rw[rw.index<=F].iloc[-1]; w0=rw[rw.index<=t0].iloc[-1]
    if name=='BTC 2011': rF=r0=wF=w0=np.nan   # 비트스탬프 자료 시작(2011-08) 직후라 RSI 계산 불가
    # 바닥권(바닥×1.25 이하) 체류: 최종 바닥 앞뒤
    zone=df[t0-D(days=200):t0+D(days=300)]; inz=zone[zone.l<=L0*1.25]
    out=dict(사례=name,직전저점일=F.date(),직전저점=LF,약세반등고점일=R.date(),약세반등=HR/LF-1,
             반등고점후하락=L0/HR-1,반등고점후일수=(t0-R).days,바닥전90일=(L0/df.c[:t0-D(days=90)].iloc[-1]-1) if len(df.c[:t0-D(days=90)]) else np.nan,
             붕괴일=brk.date(),붕괴후바닥까지일=(t0-brk).days,최종바닥=L0,직전저점대비=L0/LF-1,직전저점후일수=(t0-F).days,
             급반등고점일=AR.date(),급반등=HAR/L0-1,급반등일수=(AR-t0).days,
             재시험일=RT.date() if RT is not None else None,재시험저점=LRT if RT is not None else np.nan,재시험_바닥대비=(LRT/L0-1) if RT is not None else np.nan,
             넥라인=NK,넥라인일=NKd.date(),돌파일=BO.date() if BO is not None else None,돌파일수=(BO-t0).days if BO is not None else None,
             돌파시상승=(df.c[BO]/L0-1) if BO is not None else np.nan,
             돌파후90일최고=(df.h[BO:BO+D(days=90)].max()/df.c[BO]-1) if BO is not None else np.nan,
             돌파후90일최저=(df.l[BO:BO+D(days=90)].min()/df.c[BO]-1) if BO is not None else np.nan,
             직전저점회복일수=(REC-t0).days if REC is not None else None,
             일봉아래꼬리=wick,종가위치=(c.c-c.l)/rng if rng>0 else np.nan,바닥일거래량배수=vm,직전5일최대거래량배수=vmax,주봉아래꼬리=wwick,
             일RSI_직전저점=rF,일RSI_바닥=r0,주RSI_직전저점=wF,주RSI_바닥=w0,
             바닥권첫진입=(inz.index[0]-t0).days,바닥권마지막=(inz.index[-1]-t0).days,자료끝=last.date())
    return out
if __name__=='__main__':
    T=pd.DataFrame([analyze(n,s,t) for n,s,t,_ in CASES])
    T.to_csv('output/u_chart_shape.csv',index=False)
    pct=['반등고점후하락','바닥전90일','약세반등','직전저점대비','급반등','재시험_바닥대비','돌파시상승','돌파후90일최고','돌파후90일최저']
    S=T.copy()
    for k in pct: S[k]=(S[k]*100).round(1)
    for k in ['일봉아래꼬리','종가위치','주봉아래꼬리']: S[k]=S[k].round(2)
    for k in ['바닥일거래량배수','직전5일최대거래량배수','일RSI_직전저점','일RSI_바닥','주RSI_직전저점','주RSI_바닥']: S[k]=S[k].round(1)
    with open('output/u_chart_shape.txt','w') as f:
        for cols,tt in [(['사례','직전저점일','직전저점','약세반등고점일','약세반등','반등고점후하락','반등고점후일수','바닥전90일','붕괴일','붕괴후바닥까지일','최종바닥','직전저점대비','직전저점후일수'],'A. 큰 그림: 직전 주요 저점 → 약세장 반등 → 지지선 붕괴 → 최종 바닥 (%)'),
                        (['사례','급반등고점일','급반등','급반등일수','재시험일','재시험저점','재시험_바닥대비','넥라인일','넥라인','돌파일','돌파일수','돌파시상승','돌파후90일최고','돌파후90일최저','직전저점회복일수'],'B. 바닥 뒤: 급반등 → 재시험 → 넥라인 돌파 (%)'),
                        (['사례','일봉아래꼬리','종가위치','바닥일거래량배수','직전5일최대거래량배수','주봉아래꼬리','일RSI_직전저점','일RSI_바닥','주RSI_직전저점','주RSI_바닥','바닥권첫진입','바닥권마지막','자료끝'],'C. 바닥 캔들·거래량·RSI, 바닥권(바닥×1.25 이하) 체류 (최종 바닥 기준 일수)')]:
            s=f"== {tt}\n{S[cols].to_string(index=False)}\n\n"; print(s); f.write(s)
