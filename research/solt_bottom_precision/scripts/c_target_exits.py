# C. "저점 정밀 매수 + 고정 배수 매도" 검증: 모든 BTC 저점 이벤트(가짜 바닥 포함)에서 가상 SOLT 목표 도달 확률
import sys; sys.path.insert(0,'scripts')
from common import *
pd.set_option('display.width',260)
cl=pd.read_parquet('data/synth_solt_daily.parquet'); s1=m1('SOL'); b1=m1('BTC')
A=pd.read_csv('output/a_sync_th15.csv',parse_dates=['btc_low_utc','sol_low72_utc'])
extra=pd.DataFrame({'btc_low_utc':pd.to_datetime(['2022-11-21 21:52','2022-12-30 14:49'],utc=True)})
ev=pd.concat([A[['btc_low_utc','type']],extra]).drop_duplicates('btc_low_utc').sort_values('btc_low_utc').reset_index(drop=True)
ev['type']=ev['type'].fillna('조용한형')
bdaily=b1.c.resample('D').last(); ath=b1.h.cummax()
def nav_entry(t, S):
    """t 시점에 SOL 가격 S로 SOLT를 산다면 가상 NAV"""
    prev=cl[cl.index<=t]; 
    if prev.empty: return np.nan, None
    i=len(prev)-1; return prev.nav.iloc[-1]*(1+2*(S/prev.S.iloc[-1]-1)), i
def open_time(t):
    """주말이면 일요일 20:00 ET 개장 시각으로 이동"""
    if session_of(t)!='weekend_closed': return t
    et=t.tz_convert('America/New_York'); days=(6-et.weekday())%7
    o=(et+pd.Timedelta(days=days)).normalize()+pd.Timedelta(hours=20)
    if o<et: o+=pd.Timedelta(days=7)
    return o.tz_convert('UTC')
def outcome(t, S, K=(1.3,1.5,2,3,5), H=365):
    n0,i=nav_entry(t,S)
    if not np.isfinite(n0) or n0<=0.05*cl.nav.iloc[i]: return None      # 장중 -47.5% 이상이면 2배 상품은 사실상 청산 → 매수 불가
    # 진입 구간 나머지: 진입 후 같은 재조정 구간 안의 SOL 고/저
    end0=cl.index[i+1] if i+1<len(cl) else None
    if end0 is None: return None
    seg=s1[t:end0]; P0=cl.nav.iloc[i]; S0=cl.S.iloc[i]
    hi0=P0*(1+2*(seg.h.max()/S0-1)); lo0=max(P0*(1+2*(seg.l.min()/S0-1)),1e-9)
    fut=cl.iloc[i+1:]; fut=fut[fut.index<=t+pd.Timedelta(days=H)]
    hi=np.r_[hi0,fut.nav_hi.values]/n0; lo=np.r_[lo0,fut.nav_lo.values]/n0; dts=np.r_[(end0-t).total_seconds()/86400,[(x-t).total_seconds()/86400 for x in fut.index]]
    r=dict(entry_nav=n0)
    for k in K:
        idx=np.where(hi>=k)[0]
        if len(idx):
            j=idx[0]; r[f'hit{k}']=True; r[f'days{k}']=dts[j]; r[f'mae{k}']=lo[:j+1].min()-1
        else: r[f'hit{k}']=False; r[f'days{k}']=np.nan; r[f'mae{k}']=lo.min()-1
    r['max365']=hi.max(); r['min365']=lo.min()-1; r['end365']=(fut.nav.iloc[-1]/n0) if len(fut) else np.nan
    return r
if __name__=='__main__':
  rows=[]
  for _,e in ev.iterrows():
      tb=e.btc_low_utc
      if tb<pd.Timestamp('2020-08-20',tz='UTC') or tb>pd.Timestamp('2026-10-15',tz='UTC'): continue
      S_at=s1.l[tb]; ws=s1.l[tb-pd.Timedelta(hours=6):tb+pd.Timedelta(hours=6)]; ts=ws.idxmin(); Ssol=ws.min()
      dd=b1.l[tb]/ath[tb]-1
      held=b1.l[tb+pd.Timedelta(minutes=1):tb+pd.Timedelta(days=90)].min()>b1.l[tb]
      entries={'A BTC저점 그 분 (완벽)':(tb,S_at),'B SOL 6h내 최저 (완벽)':(ts,Ssol)}
      to=open_time(tb); entries['C 체결가능 (주말이면 일요일 밤)']=(to,s1.c.asof(to) if to!=tb else S_at)
      # 확인 매수: 저점 후 48시간 안에 SOL 1시간 종가가 저점 대비 +5% / +10%
      h1=s1.c[ts:ts+pd.Timedelta(hours=48)].resample('1h').last()
      for x in [0.05,0.10]:
          ok=h1[h1>=Ssol*(1+x)]
          if len(ok): tt=open_time(ok.index[0]+pd.Timedelta(hours=1)); entries[f'D 확인매수 SOL+{int(x*100)}%']=(tt,s1.c.asof(tt))
      for nm,(t,S) in entries.items():
          o=outcome(t,S)
          if o: rows.append(dict(event=tb,entry=nm,type=e.type,btc_dd_ath=dd,held90=held,entry_vs_sol_low=S/Ssol-1,**o))
  R=pd.DataFrame(rows); R.to_csv('output/c_target_exits.csv',index=False)
  K=(1.3,1.5,2,3,5)
  def table(x,title):
      t=x.groupby('entry').apply(lambda g: pd.Series({'n':len(g),'진입가_SOL저점대비':g.entry_vs_sol_low.median(),
          **{f'{k}배 도달(1년)':g[f'hit{k}'].mean() for k in K},**{f'{k}배 중앙일':g[f'days{k}'].median() for k in (1.5,2,3)},
          '2배 전 최대낙폭(중앙)':g['mae2'].median(),'1년 최저(중앙)':g.min365.median(),'1년 최대(중앙)':g.max365.median()}))
      print(f"\n== {title}"); print(t.round(2).to_string())
  table(R,'전체 BTC 저점 이벤트 (2020-08~2026-10, 가짜 바닥 포함)')
  table(R[R.btc_dd_ath<=-0.40],'약세장 바닥권 이벤트만 (BTC 고점 대비 -40% 이하)')
  table(R[R.held90],'(사후) 90일 동안 깨지지 않은 저점만')
  table(R[~R.held90],'(사후) 90일 안에 깨진 저점만')
  print("\n== 약세장 바닥권 이벤트 목록 (A 진입)")
  x=R[(R.btc_dd_ath<=-0.40)&(R.entry=='A BTC저점 그 분 (완벽)')]
  print(x[['event','type','btc_dd_ath','held90','hit1.5','hit2','hit3','days2','mae2','max365','min365']].round(2).to_string(index=False))
