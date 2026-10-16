# -*- coding: utf-8 -*-
"""
NAIL R9 일일 판정 (엔진 v1.2 원자료 모드) + 전진 기록 누적

실행: python nail/scripts/run_daily.py
입력: nail/data/prices/{NAIL,ITB,SPY}.csv, nail/data/macro/{VIXCLS,BAMLH0A0HYM2}.csv (fetch_nail_data.py 결과)
출력: nail/output/engine/(r8_daily.csv, r8_fills.csv, r8_status.json)  — 엔진 원 출력
      nail/output/score_log.csv  — 평가일별 1행, 같은 날짜가 이미 있으면 덮지 않고 건너뜀(전진 기록 보존)
      nail/output/LATEST.md      — 최신 판정 요약
"""
import os, sys, json, subprocess
from datetime import datetime, timezone, timedelta
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
N = os.path.join(ROOT, 'nail'); D = os.path.join(N, 'data'); O = os.path.join(N, 'output'); E = os.path.join(O, 'engine')
KST = timezone(timedelta(hours=9))


def _md(df):
    cols = list(df.columns)
    out = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    out += ['| ' + ' | '.join(str(v) for v in r) + ' |' for r in df.itertuples(index=False)]
    return '\n'.join(out)


def main():
    os.makedirs(E, exist_ok=True)
    cmd = [sys.executable, os.path.join(N, 'engine', 'nail_r9_engine_v1.2.py'),
           '--nail', f'{D}/prices/NAIL.csv', '--itb', f'{D}/prices/ITB.csv', '--spy', f'{D}/prices/SPY.csv',
           '--vix', f'{D}/macro/VIXCLS.csv', '--hy', f'{D}/macro/BAMLH0A0HYM2.csv', '--out', E]
    try:
        import exchange_calendars  # noqa: F401
    except Exception:
        cmd += ['--calendar-from', f'{D}/prices/SPY.csv']
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout); print(r.stderr, file=sys.stderr)
    if r.returncode != 0: sys.exit(r.returncode)
    st = json.load(open(os.path.join(E, 'r8_status.json'), encoding='utf-8'))
    daily = pd.read_csv(os.path.join(E, 'r8_daily.csv'), index_col=0, parse_dates=True)
    last = daily.iloc[-1]; d = daily.index[-1]
    row = dict(date=str(d.date()), recorded_at_kst=datetime.now(KST).strftime('%Y-%m-%d %H:%M'),
               nail_close=round(float(last.close), 4), display=st['display_score'], cond=st['condition_score'],
               N=last.N, A1=last.get('A1'), A2=last.get('A2'), A3=last.get('A3'), A4=last.get('A4'), S=last.S,
               dd252=round(float(last.dd252), 4), A1_dd756=round(float(last.get('A1_dd756')), 4),
               A2_rs504=round(float(last.get('A2_rs504')), 2), A3_rsiW=round(float(last.get('A3_rsiW')), 2),
               A4_ma200w=round(float(last.get('A4_ma200w')), 4), hy_pct10y=round(float(last.hy_pct10y), 1),
               vix60max=float(last.vix60max), verdict=st['verdict'], problems=' | '.join(st['problems']))
    log = os.path.join(O, 'score_log.csv')
    if os.path.exists(log):
        L = pd.read_csv(log)
        if row['date'] in set(L.date.astype(str)):
            print('score_log: 같은 날짜가 이미 기록됨 — 보존(덮지 않음)')
        else:
            pd.concat([L, pd.DataFrame([row])]).to_csv(log, index=False)
    else:
        pd.DataFrame([row]).to_csv(log, index=False)
    fills = pd.read_csv(os.path.join(E, 'r8_fills.csv'))
    md = [f'# NAIL R9 최신 판정 — {row["date"]} 미국 종가', '',
          f'- 기록 시각(KST): {row["recorded_at_kst"]} · 엔진 {st["engine_version"]} · 원자료 모드(ITB·SPY·NAIL 전 기간)',
          f'- **표시점수 {row["display"]:.0f}** (조건 {row["cond"]:.0f} = N {row["N"]:.0f} + A {last.A:.0f} + S {row["S"]:.0f})',
          f'- 판정: {st["verdict"]}', '',
          '| 블록 | 원값 | 점수 |', '|---|---|---:|',
          f'| N | NAIL {row["nail_close"]:.2f} / 252일 최고 {st["ref_high_252"]:.2f} = {row["dd252"]:+.1%} | {row["N"]:.0f} |',
          f'| A1 | ITB 756일 낙폭 {row["A1_dd756"]:+.1%} | {row["A1"]:.0f} |',
          f'| A2 | ITB/SPY 총수익 504일 위치 {row["A2_rs504"]:.1f} | {row["A2"]:.0f} |',
          f'| A3 | ITB 완결 주봉 RSI14 {row["A3_rsiW"]:.2f} | {row["A3"]:.0f} |',
          f'| A4 | ITB / 200주 평균 {row["A4_ma200w"]:+.1%} | {row["A4"]:.0f} |',
          f'| S | HY 10년 백분위 {row["hy_pct10y"]:.1f} · VIX 60거래일 최고 {row["vix60max"]:.2f} | {row["S"]:.0f} |', '',
          'N 점수 경계(NAIL 종가): ' + ' · '.join(f'{k} ≤ {v}' for k, v in st['nail_price_for_N_bands'].items()), '',
          f'원천 마지막 관측: {st["data"]["last_obs"]}', '',
          '경고: ' + ('; '.join(st['problems']) if st['problems'] else '없음'), '',
          '## 모형 가상 체결 (R9)', '', _md(fills),
          '', '*인샘플 규칙의 기계적 판정이며 투자 권유가 아니다.*']
    open(os.path.join(O, 'LATEST.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('\n'.join(md[:6]))


if __name__ == '__main__':
    main()
