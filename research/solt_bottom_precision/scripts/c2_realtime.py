# C2. 실시간(사후정보 없음) 저점 매수 신호 → 고정 배수 매도. 가상 SOLT.
import sys; sys.path.insert(0,'scripts')
from common import *
import c_target_exits as C
pd.set_option('display.width',260)
s1=C.s1; b1=C.b1; cl=C.cl
bh=bars('BTC','1h'); sh=bars('SOL','1h')
BEAR=[('2021-11-10','2023-01-31'),('2025-10-06','2026-11-15')]
def phase(t):
    for a,b in BEAR:
        if pd.Timestamp(a,tz='UTC')<=t<=pd.Timestamp(b,tz='UTC'): return '약세장'
    return '강세장 조정'
# 특징량 (그 시간봉 종가 시점까지의 정보만)
f=pd.DataFrame(index=bh.index)
f['r24']=bh.c/bh.c.shift(24)-1; f['r1']=bh.c/bh.c.shift(1)-1
f['vx']=bh.v/bh.v.rolling(24*7).median().shift(1)
f['dd365']=bh.c/bh.h.rolling(24*365,min_periods=24*60).max()-1
f['sr24']=sh.c.reindex(bh.index)/sh.c.reindex(bh.index).shift(24)-1
f['srsi']=None
d=sh.c.reindex(bh.index).diff(); up=d.clip(lower=0).ewm(alpha=1/14).mean(); dn=(-d.clip(upper=0)).ewm(alpha=1/14).mean(); f['srsi']=100-100/(1+up/dn)
f=f['2020-09-01':'2026-10-15']
def events(mask, gap_h=72):
    t=f.index[mask.fillna(False).values]; out=[]; last=None
    for x in t:
        if last is None or (x-last)>=pd.Timedelta(hours=gap_h): out.append(x); last=x
    return out
TRIG={
 'T1 투매감지: BTC 24h -8%↓ & 거래량 5배↑':(f.r24<=-0.08)&(f.vx>=5),
 'T1b 투매감지 강: BTC 24h -12%↓ & 거래량 8배↑':(f.r24<=-0.12)&(f.vx>=8),
 'T4 SOL 과매도: SOL 24h -15%↓ & RSI14(1h)<20':(f.sr24<=-0.15)&(f.srsi<20),
}
if __name__=='__main__':
  rows=[]
  for nm,mask in TRIG.items():
      for t0 in events(mask):
          tc=t0+pd.Timedelta(hours=1)                      # 그 봉 종가 시각
          # 진입 방식: (i) 감지 즉시, (ii) 감지 후 첫 1h 양봉(SOL) 종가, 24시간 안
          ents={'즉시':tc}
          w=sh['c'][tc:tc+pd.Timedelta(hours=24)]; o=sh['o'][tc:tc+pd.Timedelta(hours=24)]
          g=w[w>o]
          if len(g): ents['첫 양봉 확인']=g.index[0]+pd.Timedelta(hours=1)
          lo72=s1.l[t0-pd.Timedelta(hours=72):t0+pd.Timedelta(hours=72)].min()
          for en,t in ents.items():
              t=C.open_time(t); S=s1.c.asof(t)
              prev=cl[cl.index<=t]
              if prev.empty or (1+2*(S/prev.S.iloc[-1]-1))<0.05: continue
              o_=C.outcome(t,S)
              if o_: rows.append(dict(trig=nm,entry=en,t=t,phase=phase(t),dd365=f.dd365.asof(t0),entry_vs_low72=S/lo72-1,
                                      low_after=s1.l[t:t+pd.Timedelta(days=30)].min()/S-1,**o_))
  R=pd.DataFrame(rows); R.to_csv('output/c2_realtime.csv',index=False)
  K=(1.3,1.5,2,3)
  def tab(x,title):
      t=x.groupby(['trig','entry']).apply(lambda g: pd.Series({'n':len(g),'진입_72h저점대비':g.entry_vs_low72.median(),'이후30일 추가하락':g.low_after.median(),
          **{f'{k}배':g[f'hit{k}'].mean() for k in K},'1.5배 중앙일':g['days1.5'].median(),'2배 중앙일':g['days2'].median(),
          '1.5배 전 낙폭':g['mae1.5'].median(),'2배 전 낙폭':g['mae2'].median(),'2배 전 낙폭 하위25%':g['mae2'].quantile(.25)}))
      print(f"\n== {title}"); print(t.round(2).to_string())
  tab(R,'전체 (2020-09~2026-10)'); tab(R[R.phase=='약세장'],'약세장 구간만 (2021-11~2023-01, 2025-10~)')
  x=R[(R.phase=='약세장')&(R.entry=='즉시')&(R.trig.str.startswith('T1 '))]
  print("\n== 약세장 T1 즉시 진입 사례"); print(x[['t','dd365','entry_vs_low72','low_after','hit1.3','hit1.5','hit2','days1.5','days2','mae1.5','mae2','max365']].round(2).to_string(index=False))
