# C3. 실시간 정밀 매수 설계: [투매 감지] → [저점 추적] → [반등 확인 매수] → [저점 이탈 손절 / 목표배수 매도 / 기한 청산]
import sys; sys.path.insert(0,'scripts')
from common import *
import c_target_exits as C
from c2_realtime import f, events, phase
pd.set_option('display.width',260)
s1=C.s1; cl=C.cl; sh=bars('SOL','1h')
def nav(t,S):
    prev=cl[cl.index<=t]; return prev.nav.iloc[-1]*(1+2*(S/prev.S.iloc[-1]-1))
OPEN=pd.Series([session_of(t)!='weekend_closed' for t in sh.index],index=sh.index)
def episode(t_arm, x=0.05, hold_h=2, s=0.02, k=1.5, T=60, max_tries=3, wait_h=96):
    """t_arm 이후 SOL 시간봉으로 상태기계 실행. 반환: 거래 목록"""
    trades=[]; L=np.inf; Lt=None; st='wait'; tries=0; end_wait=t_arm+pd.Timedelta(hours=wait_h)
    seg=sh[t_arm:t_arm+pd.Timedelta(days=T+wait_h/24+5)]
    for t,row in seg.iterrows():
        op=OPEN[t]
        if st=='wait':
            if t>end_wait or tries>=max_tries: break
            if row.l<L: L=row.l; Lt=t; continue                       # 새 저점이 나온 봉에서는 매수하지 않음
            trig=L*(1+x)
            if op and Lt is not None and row.h>=trig and (t-Lt)>=pd.Timedelta(hours=hold_h):
                S=max(trig,row.o); n0=nav(t,S)                          # 역지정가 매수: 저점×(1+x) 터치 시 체결 (갭이면 시가)
                if n0<=0: continue
                st='in'; e=dict(entry_t=t,S_in=S,L=L,n0=n0); tries+=1
        elif st=='in':
            stop=e['L']*(1-s)
            # 목표 SOL 가격 (해당 재조정 구간 기준): nav(S)=k*n0
            prev=cl[cl.index<=t]; P0=prev.nav.iloc[-1]; S0=prev.S.iloc[-1]
            S_tgt=S0*(1+(k*e['n0']/P0-1)/2)
            hit_stop=row.l<=stop; hit_tgt=row.h>=S_tgt
            if not op:
                continue
            if hit_stop:      # 보수적으로 손절 먼저. 갭이면 시가 체결
                Sx=min(stop,row.o); e.update(exit_t=t,how='손절',m=nav(t,Sx)/e['n0']*(0.998**2)); trades.append(e); st='wait'
                L=row.l; Lt=t; end_wait=t+pd.Timedelta(hours=wait_h); continue
            if hit_tgt:
                Sx=max(S_tgt,row.o); e.update(exit_t=t,how='목표',m=nav(t,Sx)/e['n0']*(0.998**2)); trades.append(e); break
            if t>=e['entry_t']+pd.Timedelta(days=T):
                e.update(exit_t=t,how='기한',m=nav(t,row.c)/e['n0']*(0.998**2)); trades.append(e); break
    return trades
TRIGS={'BTC 투매(24h-8%,거래량5배)':(f.r24<=-0.08)&(f.vx>=5),'SOL 과매도(24h-15%,RSI<20)':(f.sr24<=-0.15)&(f.srsi<20)}
if __name__=='__main__':
  rows=[]
  for tn,mask in TRIGS.items():
      arms=events(mask,gap_h=96)
      for x in [0.03,0.05,0.08]:
          for hold_h in [1,4]:
              for k in [1.3,1.5,2.0]:
                  for a in arms:
                      tr=episode(a+pd.Timedelta(hours=1),x=x,hold_h=hold_h,k=k)
                      ep=np.prod([z['m'] for z in tr]) if tr else 1.0
                      rows.append(dict(trig=tn,x=x,hold_h=hold_h,k=k,arm=a,phase=phase(a),n_tr=len(tr),ep=ep,
                                       final=tr[-1]['how'] if tr else '미진입',first_vs_low=(tr[0]['S_in']/s1.l[a-pd.Timedelta(hours=72):a+pd.Timedelta(days=30)].min()-1) if tr else np.nan))
  R=pd.DataFrame(rows); R.to_csv('output/c3_confirm.csv',index=False)
  gm=lambda v: float(np.exp(np.log(np.clip(v,1e-6,None)).mean()))
  def summ(x):
      return pd.Series({'에피소드':len(x),'진입률':(x.n_tr>0).mean(),'목표달성':(x.final=='목표').mean(),'손절로끝':(x.final=='손절').mean(),'기한':(x.final=='기한').mean(),
                        '에피소드 기하평균':gm(x.ep),'중앙':x.ep.median(),'최악':x.ep.min(),'평균':x.ep.mean(),'첫진입_30일최저대비':x.first_vs_low.median()})
  for ph in ['전체','약세장']:
      x=R if ph=='전체' else R[R.phase=='약세장']
      t=x.groupby(['trig','x','hold_h','k']).apply(summ)
      print(f"\n== {ph}: 반등확인 매수(x=저점대비 반등폭, hold_h=저점 유지 시간) + 저점-2% 손절 + 목표 k배 (기한 60일, 재시도 3회)")
      print(t.round(2).to_string())
