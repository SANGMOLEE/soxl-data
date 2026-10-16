# -*- coding: utf-8 -*-
"""
NAIL 연구용 원자료 수집기 (GitHub Actions에서 실행 — 작업 컨테이너에서는 시세 사이트가 막혀 있음)

- 주가: Yahoo(yfinance), 전 기간을 매번 새로 받는다(조정종가가 새 분배금마다 과거까지 다시 계산되므로
  append-only로 쌓으면 총수익 비율 A2가 틀어진다). 결과: nail/data/prices/{이름}.csv
- 거시: FRED fredgraph.csv, 전 기간. 결과: nail/data/macro/{ID}.csv
  HY OAS(BAMLH0A0HYM2)는 FRED가 최근 3년만 보내므로 soxl-data의 보존 이력(data/macro)과 합친다.
- 분배금: nail/data/dividends/{이름}.csv
- 상태: nail/data/fetch_status.json (시리즈별 행수·마지막 날짜·실패)
- 처음 한 번만: soxl-data 공용 수집기용 시드 파일(data/prices/NAIL.csv, ITB.csv, data/macro/DGS10.csv 등)을
  파일이 없을 때만 만든다. 이미 있으면 건드리지 않는다(공용 수집기의 '기존 행 불변' 원칙).
"""
import os, sys, json, time
from datetime import datetime, timezone, timedelta
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'nail', 'data')
KST = timezone(timedelta(hours=9)); NOW = datetime.now(KST)

# 이름: Yahoo 심볼
PRICES = {
    'NAIL': 'NAIL', 'ITB': 'ITB', 'SPY': 'SPY', 'XHB': 'XHB',
    'LEN': 'LEN', 'DHI': 'DHI', 'PHM': 'PHM', 'NVR': 'NVR', 'TOL': 'TOL',
    'HYG': 'HYG', 'TLT': 'TLT', 'IWM': 'IWM', 'KRE': 'KRE',
    'GSPC': '^GSPC', 'VIX': '^VIX', 'TNX': '^TNX', 'IRX': '^IRX', 'MOVE': '^MOVE',
}
FRED = [
    # 신용·변동성
    'VIXCLS', 'BAMLH0A0HYM2', 'BAA10Y', 'NFCI', 'STLFSI4',
    # 금리
    'DGS10', 'DGS2', 'DGS30', 'DFF', 'FEDFUNDS', 'DFEDTARU', 'T10Y2Y', 'T10Y3M', 'DFII10', 'T5YIE',
    'MORTGAGE30US', 'MORTGAGE15US', 'OBMMIJUMBO30YF',
    # 물가·경기
    'CPIAUCSL', 'CPILFESL', 'UNRATE', 'ICSA', 'PAYEMS', 'INDPRO', 'UMCSENT', 'USREC', 'DCOILWTICO',
    # 주택
    'HOUST', 'HOUST1F', 'PERMIT', 'PERMIT1', 'HSN1F', 'MSACSR', 'EXHOSLUSM495S', 'CSUSHPINSA', 'MSPUS',
    'NHSUSSPT', 'COMPUTSA', 'UNDCONTSA',
]
SEED_PRICES = ('NAIL', 'ITB')                     # soxl-data 공용 수집기 시드(없을 때만)
SEED_FRED = ('DGS10', 'DGS2', 'MORTGAGE30US')
status = dict(run_at_kst=NOW.strftime('%Y-%m-%d %H:%M:%S'), prices={}, macro={}, failed=[], notes=[])


def fetch_yahoo(sym):
    import yfinance as yf
    last = None
    for k in range(3):
        try:
            t = yf.Ticker(sym)
            raw = t.history(period='max', interval='1d', auto_adjust=False, actions=True)
            if raw is None or raw.empty: raise ValueError('빈 응답')
            idx = pd.to_datetime(raw.index)
            idx = idx.tz_localize(None) if idx.tz is not None else idx
            d = pd.DataFrame({'date': idx.normalize(), 'open': raw['Open'].values, 'high': raw['High'].values,
                              'low': raw['Low'].values, 'close': raw['Close'].values,
                              'adj_close': (raw['Adj Close'] if 'Adj Close' in raw else raw['Close']).values,
                              'volume': raw['Volume'].values if 'Volume' in raw else 0})
            d = d.dropna(subset=['close']).drop_duplicates('date', keep='last').sort_values('date')
            # 장중 실행이면 오늘 행은 미확정 값이므로 버린다(미국 동부 16:30 이전)
            et = datetime.now(timezone.utc).astimezone(__import__('zoneinfo').ZoneInfo('America/New_York'))
            if len(d) and d.date.iloc[-1].date() == et.date() and (et.hour, et.minute) < (16, 30):
                status['notes'].append(f'{sym}: 장중 미확정 행 {et.date()} 제외'); d = d.iloc[:-1]
            div = raw['Dividends'] if 'Dividends' in raw else pd.Series(dtype=float)
            div = div[div > 0]
            dv = pd.DataFrame({'date': pd.to_datetime(div.index).tz_localize(None).normalize() if len(div) else [],
                               'dividend': div.values})
            spl = raw['Stock Splits'] if 'Stock Splits' in raw else pd.Series(dtype=float)
            spl = spl[spl > 0]
            return d.reset_index(drop=True), dv, [(str(pd.Timestamp(i).date()), float(v)) for i, v in spl.items()]
        except Exception as e:
            last = e; time.sleep(3 + 3 * k)
    raise last


def fetch_fred(sid):
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd=1776-07-04&coed={NOW:%Y-%m-%d}'
    last = None
    for k in range(3):
        try:
            raw = pd.read_csv(url)
            raw.columns = ['date', 'value']
            raw['date'] = pd.to_datetime(raw['date']); raw['value'] = pd.to_numeric(raw['value'], errors='coerce')
            raw = raw.dropna().sort_values('date').reset_index(drop=True)
            if raw.empty: raise ValueError('전량 결측')
            return raw
        except Exception as e:
            last = e; time.sleep(2 + 2 * k)
    raise last


def main():
    for sub in ('prices', 'macro', 'dividends'):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    for name, sym in PRICES.items():
        try:
            d, dv, spl = fetch_yahoo(sym)
            d.to_csv(os.path.join(OUT, 'prices', f'{name}.csv'), index=False, float_format='%.6f')
            if len(dv): dv.to_csv(os.path.join(OUT, 'dividends', f'{name}.csv'), index=False, float_format='%.6f')
            status['prices'][name] = dict(symbol=sym, rows=len(d), first=str(d.date.min().date()), last=str(d.date.max().date()),
                                         last_close=round(float(d.close.iloc[-1]), 4), splits=spl)
            print(f'[OK] {name:5s} {len(d):6d}행 {d.date.min().date()} ~ {d.date.max().date()} 종가 {d.close.iloc[-1]:.2f}')
            if name in SEED_PRICES:
                seed = os.path.join(ROOT, 'data', 'prices', f'{name}.csv')
                if not os.path.exists(seed):
                    s = d.copy(); s['source'] = 'yahoo'
                    s.to_csv(seed, index=False); status['notes'].append(f'시드 생성 {seed}')
        except Exception as e:
            status['failed'].append(f'{name}: {type(e).__name__} {str(e)[:80]}'); print(f'[FAIL] {name}: {e}')
        time.sleep(1)
    for sid in FRED:
        try:
            d = fetch_fred(sid)
            if sid == 'BAMLH0A0HYM2':        # FRED 절단 → soxl-data 보존 이력과 합침
                keep = os.path.join(ROOT, 'data', 'macro', 'BAMLH0A0HYM2.csv')
                if os.path.exists(keep):
                    old = pd.read_csv(keep, usecols=[0, 1]); old.columns = ['date', 'value']
                    old['date'] = pd.to_datetime(old['date']); old['value'] = pd.to_numeric(old['value'], errors='coerce')
                    old = old.dropna()
                    d = pd.concat([old[old.date < d.date.min()], d]).drop_duplicates('date', keep='last').sort_values('date')
                    status['notes'].append(f'HY: 보존 이력 {len(old)}행 + FRED {len(d)}행 병합')
            d.to_csv(os.path.join(OUT, 'macro', f'{sid}.csv'), index=False)
            status['macro'][sid] = dict(rows=len(d), first=str(d.date.min().date()), last=str(d.date.max().date()),
                                        last_value=float(d.value.iloc[-1]))
            print(f'[OK] {sid:14s} {len(d):6d}행 ~ {d.date.max().date()} {d.value.iloc[-1]}')
            if sid in SEED_FRED:
                seed = os.path.join(ROOT, 'data', 'macro', f'{sid}.csv')
                if not os.path.exists(seed):
                    s = d.copy(); s['source'] = 'fred'; s.to_csv(seed, index=False); status['notes'].append(f'시드 생성 {seed}')
        except Exception as e:
            status['failed'].append(f'{sid}: {type(e).__name__} {str(e)[:80]}'); print(f'[FAIL] {sid}: {e}')
        time.sleep(0.6)
    json.dump(status, open(os.path.join(OUT, 'fetch_status.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('실패:', status['failed'])
    core = [k for k in ('NAIL', 'ITB', 'SPY') if k not in status['prices']] + \
           [k for k in ('VIXCLS', 'BAMLH0A0HYM2') if k not in status['macro']]
    if core:
        print('::error::핵심 시리즈 실패', core); sys.exit(1)


if __name__ == '__main__':
    main()
