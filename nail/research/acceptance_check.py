# 원자료 인수 검사 (사전 고정 문서 §1): 엔진 v1.2 원자료 모드 결과 vs 인계 문서 기록값
import pandas as pd, numpy as np
E = 'nail/output/engine'
d = pd.read_csv(f'{E}/r8_daily.csv', index_col=0, parse_dates=True)
f = pd.read_csv(f'{E}/r8_fills.csv'); ref = pd.read_csv('nail/data/r9_v12_fills.csv')
print('=== 1. R9 가상 체결 13건 ===')
m = ref.merge(f, on=['campaign', 'tranche'], how='outer', suffixes=('_ref', '_raw'))
m['px_diff%'] = (m.fill_px_raw / m.fill_px_ref - 1) * 100
print(m[['campaign', 'tranche', 'signal_ref', 'signal_raw', 'fill_ref', 'fill_raw', 'fill_px_ref', 'fill_px_raw', 'px_diff%', 'display_at_signal_ref', 'display_at_signal_raw']].to_string(index=False))
ok = (m.signal_ref == m.signal_raw).all() and (m.fill_ref == m.fill_raw).all() and (m['px_diff%'].abs() < 0.5).all()
print('판정:', '일치' if ok else '불일치 있음')
print('\n=== 2. 저점일 표시점수 구성 ===')
C5 = {'2016-02-11': (20, 16, 10), '2016-11-02': (0, 10, 0), '2018-12-24': (40, 22, 7), '2020-03-23': (50, 30, 20),
      '2022-10-20': (40, 17, 10), '2023-10-25': (10, 6, 5), '2025-04-08': (30, 16, 15)}
for k, (n, a, s) in C5.items():
    r = d.loc[k]
    print(f'{k} 기록 N{n} A{a} S{s} 표시{100-n-a-s:3d} | 원자료 N{r.N:.0f} A{r.A:.0f}(A1 {r.A1:.0f} A2 {r.A2:.0f} A3 {r.A3:.0f} A4 {r.A4:.0f}) S{r.S:.0f} 표시{r.score_display:.0f}',
          '' if (r.N, r.A, r.S) == (n, a, s) else '  ← 차이')
print('\n=== 3. R7.3 9/21 원값 ===')
r = d.loc['2026-09-21']
print(f'A1 756일 낙폭 기록 -31.8076% | 원자료 {r.A1_dd756*100:.4f}%')
print(f'A4 200주 이격 기록 -7.9867% | 원자료 {r.A4_ma200w*100:.4f}%')
print(f"주봉 RSI 9/11 주 기록 40.51 | 원자료 {d.loc['2026-09-14','A3_rsiW']:.2f} (9/14 시점 값=9/11 주) ; 9/18 주 기록 38.42 | 원자료 {d.loc['2026-09-21','A3_rsiW']:.2f}")
itb = pd.read_csv('nail/data/prices/ITB.csv', parse_dates=['date']).set_index('date')
hi = itb.close.rolling(756).max()
print(f"ITB 756일 최고(9/21 창) {hi.loc['2026-09-21']:.2f} 날짜 {itb.close.loc[:'2026-09-21'].tail(756).idxmax().date()} | 수기 추정 129.34")
print('\n=== 4. 수기 일별 표(9/22~10/15) 대조 ===')
MAN = {'09-22':73,'09-23':60,'09-24':60,'09-25':62,'09-28':62,'09-29':62,'09-30':62,'10-01':62,'10-02':60,'10-05':57,'10-06':60,'10-07':57,'10-08':57,'10-09':57,'10-12':57,'10-13':57,'10-14':57,'10-15':60}
cols = ['close', 'N', 'A1', 'A2', 'A3', 'A4', 'S', 'score_display', 'A1_dd756', 'A2_rs504', 'A3_rsiW', 'A4_ma200w', 'hy_pct10y', 'vix60max']
t = d.loc['2026-09-22':, cols].copy(); t['수기'] = [MAN.get(x.strftime('%m-%d')) for x in t.index]
t['차이'] = t.score_display - t['수기']
pd.set_option('display.width', 250); print(t.round(4).to_string())
