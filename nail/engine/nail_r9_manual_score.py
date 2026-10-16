# NAIL R9 수기 점수 계산기 (soxl-data에 NAIL·ITB가 없을 때 쓰는 방법)
# 실행: python3 -I nail_r9_manual_score.py <soxl-data 폴더: VIXCLS.csv, BAMLH0A0HYM2.csv, SPY.csv>
# 새 거래일이 생기면 ITB, NAIL_CHG, WEEKS(금요일 종가) 세 곳에 값을 추가한다.
import sys, numpy as np, pandas as pd

D = sys.argv[1] if len(sys.argv) > 1 else '.'

# ---------- 1. 기준값 (R7.3 2026-09-21 원값에서 역산) ----------
HI252 = 77.60                       # NAIL 252거래일 최고 종가 (2026-02-13). 2027-02 중순까지 창에 남음
HI756 = 88.20 / (1 - 0.318076)      # ITB 756거래일 최고 종가 ≈ 129.34 (R7.3 A1 원값 −31.8076%)
SMA_0918 = 88.20 / (1 - 0.079867)   # ITB 200주 평균, 9/18로 끝난 주 ≈ 95.856 (R7.3 A4 원값 −7.9867%)
RSI_0911, RSI_0918 = 40.51, 38.4209 # R7.3 ITB 주봉 RSI14 (Wilder)

# ---------- 2. 일별 종가 ----------
# ITB: StockAnalysis 일봉 종가(가격 기준)
ITB = {'2026-09-18':87.41,'2026-09-21':88.20,'2026-09-22':91.03,'2026-09-23':88.79,'2026-09-24':88.31,
       '2026-09-25':89.43,'2026-09-28':88.75,'2026-09-29':88.38,'2026-09-30':87.02,'2026-10-01':87.37,
       '2026-10-02':86.64,'2026-10-05':85.58,'2026-10-06':86.95,'2026-10-07':84.70,'2026-10-08':85.87,
       '2026-10-09':84.76,'2026-10-12':83.99,'2026-10-13':84.64,'2026-10-14':83.39,'2026-10-15':86.75}
# NAIL: 9/21 종가 29.61에서 stockscan 일별 등락률(%)로 이어 계산
NAIL_CHG = {'2026-09-22':8.92,'2026-09-23':-7.04,'2026-09-24':-1.63,'2026-09-25':3.70,'2026-09-28':-2.32,
            '2026-09-29':-1.47,'2026-09-30':-4.49,'2026-10-01':1.21,'2026-10-02':-2.39,'2026-10-05':-4.11,
            '2026-10-06':5.07,'2026-10-07':-7.68,'2026-10-08':4.03,'2026-10-09':-4.06,'2026-10-12':-2.91,
            '2026-10-13':2.24,'2026-10-14':-4.18,'2026-10-15':11.87}
NAIL = {'2026-09-21': 29.61}; p = 29.61
for d, c in NAIL_CHG.items():
    p *= 1 + c / 100; NAIL[d] = p

# ---------- 3. ITB 완결 주봉(금요일 종가) ----------
WEEKS = [('2026-09-25',89.43), ('2026-10-02',86.64), ('2026-10-09',84.76)]   # 10/16 주 완결 후 추가
# 200주 창에서 빠지는 2022년 주봉(일봉 미확보). 2022-11·12 월말 종가 60.88·60.61 → 57~64 범위로 상·하한
DROP_LO, DROP_HI = 57.0, 64.0

# ---------- 4. 주봉 RSI: R7.3 두 값과 9/18 주 변화로 Wilder 상태를 역산 ----------
def wilder_state(c_prev, c_now, r1, r2):
    a, b = r1 / (100 - r1), r2 / (100 - r2); ch = c_now - c_prev
    assert ch < 0, '9/18 주는 하락 주여야 이 역산식이 성립'
    ad1 = (-ch) * b / (13 * (a - b)); au1 = a * ad1
    return 13 * au1 / 14, (13 * ad1 - ch) / 14          # 9/18 주 기준 평균 상승폭, 평균 하락폭

def rsi_path(c_prev_0911, label):
    au, ad = wilder_state(c_prev_0911, 87.41, RSI_0911, RSI_0918); prev = 87.41; out = {}
    for d, c in WEEKS:
        g = c - prev; au = (13 * au + max(g, 0)) / 14; ad = (13 * ad + max(-g, 0)) / 14
        out[d] = (100 - 100 / (1 + au / ad), au, ad); prev = c
    return out, au, ad, prev

def next_week_bounds(au, ad, prev):
    # 다음 주 종가 x에서 RSI가 정확히 40, 35, 30이 되는 x
    res = {}
    for t in (40, 35, 30):
        r = t / (100 - t)
        up = r * 13 * ad - 13 * au          # 상승 주: (13au+g)/(13ad) = r
        dn = 13 * au / r - 13 * ad          # 하락 주: 13au/(13ad+l) = r
        res[t] = prev + up if up >= 0 else prev - dn
    return res

# ---------- 5. HY·VIX·SPY ----------
def load(name):
    s = pd.read_csv(f'{D}/{name}', usecols=[0, 1]); s.columns = ['date', 'v']
    s['date'] = pd.to_datetime(s.date); return s.set_index('date').v.apply(pd.to_numeric, errors='coerce').dropna()
hy, vix = load('BAMLH0A0HYM2.csv'), load('VIXCLS.csv')
spy = pd.read_csv(f'{D}/SPY.csv'); spy.columns = [c.lower() for c in spy.columns]
spy['date'] = pd.to_datetime(spy.date); spy = spy.set_index('date')

def hy_pct(day):
    s = hy[(hy.index >= day - pd.DateOffset(years=10)) & (hy.index < day)]
    return 100 * np.mean(s.values <= hy[day]), len(s)

def pts(v, table, le=True):
    for c, p in table:
        if (v <= c if le else v >= c): return p
    return 0

if __name__ == '__main__':
    print(f'HI756 {HI756:.3f} | SMA200w(9/18 주) {SMA_0918:.3f}')
    paths = {}
    for label, cp in [('가격', 89.54), ('총수익', 88.79)]:      # 9/11 주 종가(가격 89.54, 배당 조정 88.79)
        out, au, ad, prev = rsi_path(cp, label); paths[label] = out
        b = next_week_bounds(au, ad, prev)
        print(f'[RSI {label}] ' + ', '.join(f'{d} {v[0]:.2f}' for d, v in out.items()) +
              f' | 마지막 상태 AU={au:.5f} AD={ad:.5f} 종가={prev}' +
              f' | 다음 주 종가 → RSI40 {b[40]:.2f}, RSI35 {b[35]:.2f}, RSI30 {b[30]:.2f}')
    k = len(WEEKS); s_new = sum(c for _, c in WEEKS)
    sma_lo = SMA_0918 + (s_new - DROP_HI * k) / 200; sma_hi = SMA_0918 + (s_new - DROP_LO * k) / 200
    print(f'200주 평균(마지막 완결 주 {WEEKS[-1][0]}): {sma_lo:.3f}~{sma_hi:.3f} → A4 6점선 ITB ≤ {0.9*sma_lo:.2f}~{0.9*sma_hi:.2f}')
    last = hy.index[-1]; past = hy[(hy.index >= last - pd.DateOffset(years=10)) & (hy.index < last)].values
    print('HY 10년 백분위 경계(%s 기준): 45→%.2f 54.5→%.2f 60→%.2f 75→%.2f 90→%.2f' %
          ((last.date(),) + tuple(np.percentile(past, [45, 54.5, 60, 75, 90]))))
    rows = []; cal = list(ITB.keys())
    for d in cal:
        if d < '2026-09-22': continue
        ts = pd.Timestamp(d); n, i = NAIL[d], ITB[d]
        N = pts(n / HI252 - 1, [(-0.9, 50), (-0.8, 40), (-0.7, 30), (-0.6, 20), (-0.5, 10)])
        A1 = pts(i / HI756 - 1, [(-0.4, 10), (-0.3, 7), (-0.2, 4)])
        A2 = 8                                          # ITB/SPY 504일 최저권(위치 ≤10) — 아래 ITB_SPY 열로 감시
        wk = [w for w, _ in WEEKS if w <= d]
        rsi = paths['가격'][wk[-1]][0] if wk else RSI_0918
        A3 = pts(rsi, [(30, 6), (35, 4), (40, 2)])
        kk = len(wk); s_k = sum(c for _, c in WEEKS[:kk])
        lo = SMA_0918 + (s_k - DROP_HI * kk) / 200; hi_ = SMA_0918 + (s_k - DROP_LO * kk) / 200
        a4_best, a4_worst = i / hi_ - 1, i / lo - 1
        A4 = (6 if a4_worst <= -0.10 else 3) if a4_best <= 0 else 0
        flag = '' if (a4_best <= -0.10) == (a4_worst <= -0.10) else ' (A4 경계 모호)'
        j = cal.index(d); lag = pd.Timestamp(cal[j - 2])       # 관측 후 2거래일부터 사용
        hp, _ = hy_pct(hy.index[hy.index <= lag][-1])
        S1 = pts(hp, [(90, 10), (75, 8), (60, 5), (45, 2)], le=False)
        vwin = vix[vix.index <= ts].tail(60)                   # 주의: soxl-data VIX에는 휴장일 행 가능 → 거래일 달력으로 맞출 것
        S2 = pts(vwin.max(), [(45, 10), (33, 5), (25, 2)], le=False) if len(vwin) else 0
        cond = N + A1 + A2 + A3 + A4 + S1 + S2
        sp = spy.close.get(ts, np.nan)
        rows.append(dict(date=d, NAIL=round(n, 2), ITB=i, N=N, A1=A1, A2=A2, A3=A3, A4=A4, S1=S1, S2=S2,
                         조건=cond, 표시=100 - cond, A4이격=f'{a4_worst:+.2%}~{a4_best:+.2%}{flag}',
                         HY백분위=round(hp, 1), ITB_SPY=round(i / sp, 5) if sp == sp else None))
    pd.set_option('display.width', 250); print(pd.DataFrame(rows).to_string(index=False))
    print('VIX 7/15 이후 최고:', vix['2026-07-15':].max(), vix['2026-07-15':].idxmax().date(),
          '| 9/22 이후 최고:', vix['2026-09-22':].max(), '| VIX 마지막:', vix.index[-1].date(), vix.iloc[-1])
    print('HY 마지막:', hy.index[-1].date(), hy.iloc[-1])
