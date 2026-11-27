# F. 자기 점검: 보고서의 "재이탈 70~81%"가 차트 모양 덕인가, 변동성만으로도 나오는 숫자인가
#  같은 16건마다 '그날까지의 변동성'만 가진 무작위 걸음(추세 0)이 예상하는 확률을 계산해 실제와 비교
import sys; sys.path.insert(0,'scripts')
from common import *
from math import erf, sqrt, log
Phi=lambda x:0.5*(1+erf(x/sqrt(2)))
def p_touch(dist,sig,T): return min(1.0,2*Phi(-dist/(sig*sqrt(T))))       # 추세 0, T일 안 dist(로그) 아래 닿을 확률
def p_down_first(up,dn): return up/(up+dn)                                  # 추세 0, 아래 장벽이 먼저일 확률
def wilson(k,n,z=1.96):
    p=k/n; c=(p+z*z/(2*n))/(1+z*z/n); h=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n); return c-h,c+h
lr=np.log(d.close).diff()
S=pd.read_csv(f'{OUT}/b3_springs.csv',parse_dates=['날짜'])
rows=[]
for r in S.itertuples():
    b=int(r.b); s20=lr.iloc[b-19:b+1].std(); s60=lr.iloc[b-59:b+1].std()
    dn=log(C[b]/Lo[b]); a=b-60+int(np.argmin(Lo[b-60:b])); Hn=H[a+1:b].max(); up=log(Hn/C[b])
    done=r.결과!='진행중'
    hit20=float(Lo[b+1:b+21].min()<Lo[b]) if done else np.nan
    rows.append(dict(날짜=r.날짜.date(),s20=s20,s60=s60,아래거리=dn,위거리=up,
        RW20일재이탈_s20=p_touch(dn,s20,20),RW20일재이탈_s60=p_touch(dn,s60,20),RW아래먼저=p_down_first(up,dn),
        실제20일재이탈=hit20,실제아래먼저=float(r.결과!="넥라인 먼저") if done else np.nan,
        r5=C[b+5]/C[b]-1 if b+5<N else np.nan,r20=C[b+20]/C[b]-1 if b+20<N else np.nan,r60=C[b+60]/C[b]-1 if b+60<N else np.nan))
R=pd.DataFrame(rows); P=R[R.실제20일재이탈.notna()]
out=["== 16건: 실제 vs 변동성만 있는 무작위 걸음(추세 0)의 예상"]
show=R.copy()
for k in ['s20','s60','아래거리','위거리','RW20일재이탈_s20','RW20일재이탈_s60','RW아래먼저','r5','r20','r60']: show[k]=(show[k]*100).round(1)
out.append(show.to_string(index=False))
n=len(P); k1=int(P.실제20일재이탈.sum()); k2=int(P.실제아래먼저.sum())
out.append(f"\n  20일 안 재이탈: 실제 {k1}/{n} ({k1/n:.0%}, 95% 범위 {wilson(k1,n)[0]:.0%}~{wilson(k1,n)[1]:.0%}) | 무작위 예상 합 {P.RW20일재이탈_s20.sum():.1f}건 (20일 변동성) / {P.RW20일재이탈_s60.sum():.1f}건 (60일 변동성)")
out.append(f"  넥라인보다 아래가 먼저: 실제 {k2}/{n} ({k2/n:.0%}, 95% 범위 {wilson(k2,n)[0]:.0%}~{wilson(k2,n)[1]:.0%}) | 무작위 예상 합 {P.RW아래먼저.sum():.1f}건 ({P.RW아래먼저.mean():.0%})")
for nm,m in (('마감 위치 0.8↑',S.loc[P.index,'위치']>=0.8),('2010년 이후',pd.to_datetime(P.날짜)>='2010-01-01')):
    x=P[m.values]; out.append(f"  {nm} {len(x)}건: 재이탈 실제 {int(x.실제20일재이탈.sum())} vs 예상 {x.RW20일재이탈_s20.sum():.1f}/{x.RW20일재이탈_s60.sum():.1f} | 아래 먼저 실제 {int(x.실제아래먼저.sum())} vs 예상 {x.RW아래먼저.sum():.1f}")
# 지금
b=N-1; s20=lr.iloc[-20:].std(); s60=lr.iloc[-60:].std(); dn=log(C[b]/Lo[b]); up=log(9728.12/C[b])
out.append(f"\n== 지금 (11/25): 20일 변동성 {s20:.2%}, 60일 {s60:.2%}, 스프링 저점까지 {dn:.2%}, 넥라인까지 {up:.2%}")
for sg in (0.03,0.04,s60,0.05,s20):
    out.append(f"  변동성 {sg:.1%}: 20일 안 8,129 아래 닿을 확률 {p_touch(dn,sg,20):.0%}, 10일 {p_touch(dn,sg,10):.0%}, 5일 {p_touch(dn,sg,5):.0%}")
out.append(f"  넥라인보다 8,129가 먼저일 확률 (추세 0): {p_down_first(up,dn):.0%}")
# 방향: 종가 대 종가 수익률
out.append("\n== 방향 (종가 → N일 뒤 종가): 스프링 16건 vs 약세장 모든 날")
bear=[i for i in range(260,N-60) if d.dd.iloc[i]<=-0.25]
for h in (5,20,60):
    sp=R[f'r{h}'].dropna().values*100; al=np.array([(C[i+h]/C[i]-1)*100 for i in bear])
    hv=[i for i in bear if lr.iloc[i-19:i+1].std()>=0.03]; hvv=np.array([(C[i+h]/C[i]-1)*100 for i in hv])
    out.append(f"  {h:2d}일 | 스프링 {len(sp)}건: 하락 {np.mean(sp<0):.0%}, 중앙 {np.median(sp):+.1f}%, 최악 {sp.min():+.1f}% | 약세장 전체 {len(al)}일: 하락 {np.mean(al<0):.0%}, 중앙 {np.median(al):+.1f}% | 약세장·20일 변동성 3%↑ {len(hvv)}일: 하락 {np.mean(hvv<0):.0%}, 중앙 {np.median(hvv):+.1f}%")
open(f'{OUT}/f_selfaudit.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
# B1(W 재시험)도 같은 점검: 재시험 날 종가에서 L까지, 넥라인까지 거리로 무작위 걸음의 '아래 먼저' 확률
E=pd.read_csv(f'{OUT}/b1_events.csv'); E=E[(E.결과!='진행중')&(E.저점일<'2026-01-01')]
ex=[]; ob=[]
for r in E.itertuples():
    rt=int(r.rt); dn=log(C[rt]/r.L); up=log(r.Hn/C[rt]); ex.append(p_down_first(up,dn)); ob.append(r.결과=='저점 먼저 깨짐')
o=int(sum(ob)); n=len(ob)
line=f"\n== B1 W 재시험 과거 {n}건: 저점 먼저 실제 {o} ({o/n:.0%}, 95% 범위 {wilson(o,n)[0]:.0%}~{wilson(o,n)[1]:.0%}) vs 무작위 예상 {sum(ex):.1f}건 ({np.mean(ex):.0%})"
open(f'{OUT}/f_selfaudit.txt','a').write(line+'\n'); print(line)
