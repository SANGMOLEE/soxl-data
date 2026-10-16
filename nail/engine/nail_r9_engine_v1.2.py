# -*- coding: utf-8 -*-
"""
NAIL 사이클 저점 매수 R9 — 계산·신호 엔진 v1.2 (2026-09-23)

R9 = R8 v1.1 점수·기준선(표시 58/48/38) 그대로 + 분할 방식 변경:
  비중 10%/30%/60%(깊을수록 많이), 가격 간격 10%, 직전 체결 후 최소 5거래일.
  목적: 사이클 최저점 대비 평균 매수 위치를 낮추고 초기 과다 투입을 줄임(보고서 NAIL_R9_최저점매수_최적화보고서).

v1.0 대비 수정 (독립검토보고서 2026-09-23 지적 반영)
  E1  A블록을 ITB·SPY 전체 이력에서 먼저 계산한 뒤 NAIL 거래일로 정렬한다. 준비 부족은 0점이 아니라 결측(NOT_READY).
  E2  주봉 RSI·200주 평균은 '완결된 주'만 쓴다. 완결 판정은 뉴욕증권거래소 예정 달력(XNYS)으로 하며,
      그 주의 마지막 예정 거래일 자료가 들어와야 완결이다. 효력일은 그 마지막 거래일(보통 금요일, 성금요일 주는 목요일).
  E3  VIX 60일 최고는 VIX 원천 행이 아니라 주식 거래일(XNYS) 60일 창으로 계산한다(휴장일 행 제거).
  입력  OHLC 유한·양수·고저 관계 검사. 체결 시가가 무효면 체결하지 않고 차수도 늘리지 않는다.
  달력  점수가 결측인 날도 달력에서 지우지 않는다(신호만 무효). 체결은 항상 다음 실제 거래일.
  최신성 원천별 마지막 관측일과 지연을 출력하고, 최신일 점수가 없으면 DATA_INCOMPLETE로 표시한다.
  실제체결 평가일 이후 체결 제외, 가격 검증, order_id(없으면 같은 날짜)로 부분체결을 한 차수로 묶는다.
  표시  주인님이 정한 방향대로 표시점수 = 100 − 조건점수 (0에 가까울수록 저점 조건 충족).
        조건점수 42/52/62 이상 = 표시점수 58/48/38 이하. 두 값을 모두 출력한다.

조건점수(내부) = N(NAIL 가격 손상 50) + A(ITB 업종 손상 30) + S(시장·신용 스트레스 20)
  N : NAIL 종가 / 직전 최대 252거래일(당일 포함, 최소 60거래일) 최고 종가 − 1: ≤−50/−60/−70/−80/−90% → 10/20/30/40/50
  A : A1 ITB 종가/756거래일 최고 종가−1 ≤−40/−30/−20% → 10/7/4
      A2 (ITB 총수익/SPY 총수익)의 504거래일 범위 위치 ≤10/20/30 → 8/5/3
      A3 ITB 완결 주봉 RSI14(Wilder) ≤30/35/40 → 6/4/2
      A4 ITB 종가/완결 주봉 200주 평균−1 ≤−10/0% → 6/3
  S : S1 HY OAS 10년(달력) 백분위(현재 제외, 최소 1,000관측, 관측 후 2거래일부터) ≥90/75/60/45 → 10/8/5/2
      S2 VIX 60거래일 최고 종가 ≥45/33/25 → 10/5/2
매수 규칙 R9 (신호일 종가 확인 → 다음 거래일 시가, 매수 마찰 0.075%, 하루 최대 1개 차수)
  1차 10%: 조건점수 ≥42 (표시 ≤58)
  2차 30%: 조건점수 ≥52 (표시 ≤48) AND NAIL 종가 ≤ 직전 체결가×0.90 AND 직전 체결 후 5거래일 이상
  3차 60%: 조건점수 ≥62 (표시 ≤38) AND NAIL 종가 ≤ 직전 체결가×0.90 AND 직전 체결 후 5거래일 이상
  재무장: NAIL 252일 낙폭 > −30% 이면 차수 초기화(보유 매도가 아님)

입력
  (1) 원자료: --nail --itb --spy (열: date,open,high,low,close[,adj_close]) --vix --hy (열: date,value; URL 가능)
      ITB·SPY는 adj_close(분배 반영)가 있으면 A2에 쓴다. A1·A4는 가격 종가(close).
  (2) R7.3 차트 혼합: --r73-chart 파일 --vix --hy  (NAIL OHLC·R7.3 일별 A를 쓰고 N·S는 새로 계산)
  (3) 실제 보유: --my-fills (열: date,price[,shares][,order_id])
  달력: exchange_calendars(XNYS). 없으면 --calendar-from spy.csv 의 날짜를 달력으로 쓴다.
주의: 기준값은 2016~2026 인샘플에서 정했다. 투자 권유가 아니다.
"""
import argparse, json, re, sys, os
import numpy as np, pandas as pd

TH = (42, 52, 62); STEP = 0.10; RESET_DD = -0.30; FRICTION = 0.00075
WEIGHTS = (0.10, 0.30, 0.60); MIN_GAP = 5   # 직전 체결일로부터 신호일까지 최소 거래일 수
N_CUTS = (-0.50, -0.60, -0.70, -0.80, -0.90); N_PTS = (10, 20, 30, 40, 50)
VERSION = '1.2 (R9)'

# ---------------------------------------------------------------- 달력
def get_sessions(start, end, fallback_dates=None):
    try:
        import exchange_calendars as xc
        cal = xc.get_calendar('XNYS', start=pd.Timestamp(start).normalize().strftime('%Y-%m-%d'))
        s = cal.sessions_in_range(pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize())
        return pd.DatetimeIndex(s.tz_localize(None) if s.tz is not None else s), 'XNYS'
    except Exception as e:
        if fallback_dates is None:
            sys.exit('거래일 달력을 만들 수 없음: exchange_calendars 설치 또는 --calendar-from 필요 (%s)' % e)
        idx = pd.DatetimeIndex(sorted(set(pd.to_datetime(fallback_dates))))
        return idx[(idx >= pd.Timestamp(start)) & (idx <= pd.Timestamp(end))], 'fallback'

# ---------------------------------------------------------------- 입력
def _norm_cols(df):
    df.columns = [str(c).strip().lower().replace('\ufeff', '') for c in df.columns]
    return df

def read_price(path, name, problems):
    df = _norm_cols(pd.read_csv(path))
    df['date'] = pd.to_datetime(df['date'])
    for c in ['open', 'high', 'low', 'close', 'adj_close']:
        if c in df: df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.sort_values('date').drop_duplicates('date', keep='last').set_index('date')
    bad = ~np.isfinite(df['close']) | (df['close'] <= 0)
    for c in ['open', 'high', 'low']:
        if c in df: bad |= df[c].notna() & (~np.isfinite(df[c]) | (df[c] <= 0))
    if {'open', 'high', 'low'} <= set(df.columns):
        hi_bad = df['high'].notna() & (df['high'] + 1e-9 < df[['open', 'close']].max(axis=1))
        lo_bad = df['low'].notna() & (df['low'] - 1e-9 > df[['open', 'close']].min(axis=1))
        bad |= hi_bad | lo_bad
    if bad.any():
        problems.append(f'{name}: 무효 OHLC {int(bad.sum())}행 제외 ({", ".join(d.date().isoformat() for d in df.index[bad][:5])}…)')
        df = df[~bad]
    return df

def read_series(path, name, problems):
    s = _norm_cols(pd.read_csv(path))
    dcol = 'date' if 'date' in s else s.columns[0]; vcol = 'value' if 'value' in s else s.columns[1]
    s[dcol] = pd.to_datetime(s[dcol]); s[vcol] = pd.to_numeric(s[vcol], errors='coerce')
    s = s.sort_values(dcol).drop_duplicates(dcol, keep='last').set_index(dcol)[vcol]
    bad = s.notna() & (~np.isfinite(s) | (s <= 0))
    if bad.any(): problems.append(f'{name}: 무효 값 {int(bad.sum())}행 제외'); s = s[~bad]
    return s.dropna()

def read_r73_chart(path):
    html = open(path, encoding='utf-8').read()
    m = re.search(r'const DATA=(\{.*?\});\n', html, re.S)
    if not m: sys.exit('차트 HTML에서 DATA를 찾지 못함')
    d = json.loads(m.group(1))
    df = pd.DataFrame(d['rows'], columns=['date', 'close', 'S73', 'open', 'high', 'low', 'P', 'T', 'A', 'B', 'R', 'D'])
    df['date'] = pd.to_datetime(df['date'])
    return df.set_index('date')

# ---------------------------------------------------------------- 공통 도구
def bands_le(x, cuts, pts):
    x = np.asarray(x, float); out = np.zeros(len(x))
    for c, p in zip(cuts, pts): out = np.where((x <= c) & (p > out), p, out)
    return np.where(np.isnan(x), np.nan, out)

def bands_ge(x, cuts, pts):
    x = np.asarray(x, float); out = np.zeros(len(x))
    for c, p in zip(cuts, pts): out = np.where((x >= c) & (p > out), p, out)
    return np.where(np.isnan(x), np.nan, out)

def wilder_rsi(x, n=14):
    d = x.diff().values; up = np.clip(d, 0, None); dn = np.clip(-d, 0, None)
    out = np.full(len(x), np.nan)
    if len(x) <= n: return pd.Series(out, index=x.index)
    au = np.nanmean(up[1:n + 1]); ad = np.nanmean(dn[1:n + 1])
    out[n] = 100 - 100 / (1 + au / ad) if ad > 0 else 100.0
    for i in range(n + 1, len(x)):
        au = (13 * au + up[i]) / 14; ad = (13 * ad + dn[i]) / 14
        out[i] = 100 - 100 / (1 + au / ad) if ad > 0 else 100.0
    return pd.Series(out, index=x.index)

def completed_weeks(close, sessions, calendar_has_future=True):
    """완결 주봉: 그 주(W-FRI)의 마지막 예정 거래일 자료가 있는 주만. 반환: 효력일 인덱스의 주간 종가.
    예정 달력이 평가일 이후를 모르면(대체 달력) 마지막 자료일이 금요일일 때만 그 주를 완결로 본다."""
    per_s = pd.Series(sessions, index=sessions).groupby(sessions.to_period('W-FRI')).max()
    if not calendar_has_future and len(close):
        lastp = close.index[-1].to_period('W-FRI')
        if close.index[-1].weekday() != 4: per_s = per_s.drop(lastp, errors='ignore')
    per_d = close.groupby(close.index.to_period('W-FRI'))
    rows = []
    for p, g in per_d:
        last_sched = per_s.get(p)
        if last_sched is None or pd.isna(last_sched): continue
        if g.index[-1] == last_sched:            # 마지막 예정 거래일 자료 존재 → 완결
            rows.append((last_sched, g.iloc[-1]))
    return pd.Series([v for _, v in rows], index=pd.DatetimeIndex([d for d, _ in rows]))

# ---------------------------------------------------------------- 블록
def block_N(nail_close):
    dd = nail_close / nail_close.rolling(252, min_periods=60).max() - 1
    return pd.Series(bands_le(dd.values, N_CUTS, N_PTS), index=nail_close.index), dd

def hy_pct_10y(hy):
    v = hy.values; d = hy.index; out = np.full(len(v), np.nan)
    for i in range(len(v)):
        j0 = d.searchsorted(d[i] - pd.DateOffset(years=10), side='left')
        past = v[j0:i]
        if len(past) >= 1000: out[i] = 100.0 * np.mean(past <= v[i])
    return pd.Series(out, index=d)

def block_S(vix, hy, tdays, sessions):
    # S1: HY 관측 d는 d 이후 두 번째 거래일부터 사용 → 날짜 t에는 '세션(t−2) 이하'의 마지막 관측
    hp = hy_pct_10y(hy).dropna()
    pos = sessions.get_indexer(tdays)
    lagdates = [sessions[p - 2] if p >= 2 else pd.NaT for p in pos]
    hyp = pd.Series([hp[hp.index <= x].iloc[-1] if (pd.notna(x) and (hp.index <= x).any()) else np.nan for x in lagdates], index=tdays)
    # S2: VIX를 거래일 달력에 맞춘 뒤 60거래일 최고 (결측 거래일은 직전값 최대 2일 이월)
    vs = sessions[(sessions >= vix.index[0]) & (sessions <= tdays[-1])]
    v_td = vix.reindex(vs)
    n_missing = int(v_td.isna().sum())
    v60 = v_td.ffill(limit=2).rolling(60, min_periods=60).max().reindex(tdays)
    s1 = bands_ge(hyp.values, (90, 75, 60, 45), (10, 8, 5, 2))
    s2 = bands_ge(v60.values, (45, 33, 25), (10, 5, 2))
    S = pd.Series(s1 + s2, index=tdays)
    return S, hyp, v60, n_missing

def block_A_raw(itb, spy, tdays, sessions, calendar_has_future=True):
    """E1: ITB 전체 이력에서 계산 → NAIL 거래일로 정렬. 준비 부족은 NaN."""
    ic = itb['close']
    a1v = ic / ic.rolling(756, min_periods=756).max() - 1
    itr = itb['adj_close'] if 'adj_close' in itb else ic
    str_ = spy['adj_close'] if 'adj_close' in spy else spy['close']
    common = itr.index.intersection(str_.index)
    q = (itr.reindex(common) / str_.reindex(common))
    lo = q.rolling(504, min_periods=504).min(); hi = q.rolling(504, min_periods=504).max()
    a2v = 100 * (q - lo) / (hi - lo)
    wk = completed_weeks(ic, sessions, calendar_has_future)  # E2
    rsi_w = wilder_rsi(wk); sma200w = wk.rolling(200, min_periods=200).mean()
    def asof(s):
        s = s.dropna(); idx = s.index.searchsorted(tdays, side='right') - 1
        return pd.Series([s.iloc[j] if j >= 0 else np.nan for j in idx], index=tdays)
    a1v_t = asof(a1v); a2v_t = asof(a2v); rsi_t = asof(rsi_w); sma_t = asof(sma200w)
    ic_t = asof(ic)
    # ITB 자료가 그날 없으면(지연) 결측 처리
    has_itb = pd.Series(tdays.isin(ic.index), index=tdays)
    a4v_t = ic_t / sma_t - 1
    A1 = bands_le(a1v_t.values, (-0.40, -0.30, -0.20), (10, 7, 4))
    A2 = bands_le(a2v_t.values, (10, 20, 30), (8, 5, 3))
    A3 = bands_le(rsi_t.values, (30, 35, 40), (6, 4, 2))
    A4 = bands_le(a4v_t.values, (-0.10, 0.0), (6, 3))
    A = pd.Series(A1 + A2 + A3 + A4, index=tdays).where(has_itb)
    parts = pd.DataFrame({'A1_dd756': a1v_t, 'A2_rs504': a2v_t, 'A3_rsiW': rsi_t, 'A4_ma200w': a4v_t,
                          'A1': A1, 'A2': A2, 'A3': A3, 'A4': A4}, index=tdays)
    return A, parts

# ---------------------------------------------------------------- 신호 엔진
def run_campaigns(df):
    """모든 거래일을 유지한다. 점수 결측일은 신호 없음. 체결은 다음 거래일 시가(유효할 때만)."""
    used = 0; last_px = None; last_i = -10**9; camp = 0; fills = []; events = []; pending = None
    O = df.open.values; C = df.close.values; K = df.cond.values; DD = df.dd252.values; D = df.index
    for i in range(len(df)):
        if pending is not None:                                     # 전일 신호 → 오늘 시가
            if np.isfinite(O[i]) and O[i] > 0:
                px = O[i] * (1 + FRICTION)
                fills.append(dict(campaign=camp, tranche=used + 1, weight=WEIGHTS[used], signal=pending['signal'], fill=D[i].date().isoformat(),
                                  fill_px=round(px, 4), cond_at_signal=pending['cond'], display_at_signal=100 - pending['cond']))
                last_px = px; last_i = i; used += 1
            else:
                events.append(f'{D[i].date()} 체결 실패: 시가 무효 → 차수 미증가')
            pending = None
        if used > 0 and np.isfinite(DD[i]) and DD[i] > RESET_DD:
            events.append(f'{D[i].date()} 재무장(252일 낙폭 {DD[i]:+.1%})'); used = 0; last_px = None; camp += 1
        if used < 3 and np.isfinite(K[i]) and K[i] >= TH[used] and (used == 0 or (C[i] <= last_px * (1 - STEP) and i - last_i >= MIN_GAP)):
            if i + 1 < len(df):
                pending = dict(signal=D[i].date().isoformat(), cond=float(K[i]))
            else:
                fills.append(dict(campaign=camp, tranche=used + 1, weight=WEIGHTS[used], signal=D[i].date().isoformat(), fill='다음 거래일 시가(예정)',
                                  fill_px=np.nan, cond_at_signal=float(K[i]), display_at_signal=100 - float(K[i])))
    return fills, events, used, last_px, camp

def load_my_fills(path, asof, problems):
    mf = _norm_cols(pd.read_csv(path))
    if mf.empty: return mf
    mf['date'] = pd.to_datetime(mf['date']); mf['price'] = pd.to_numeric(mf['price'], errors='coerce')
    bad = ~np.isfinite(mf['price']) | (mf['price'] <= 0)
    if bad.any(): problems.append(f'실제체결: 무효 가격 {int(bad.sum())}행 제외'); mf = mf[~bad]
    fut = mf['date'] > asof
    if fut.any(): problems.append(f'실제체결: 평가일({asof.date()}) 이후 {int(fut.sum())}행 제외'); mf = mf[~fut]
    if 'shares' in mf: mf['shares'] = pd.to_numeric(mf['shares'], errors='coerce')
    mf['_key'] = mf['order_id'].astype(str) if 'order_id' in mf else mf['date'].dt.strftime('%Y-%m-%d')
    key = '_key'
    def agg(g):
        if 'shares' in g and g['shares'].notna().all() and (g['shares'] > 0).all():
            px = float((g['price'] * g['shares']).sum() / g['shares'].sum()); sh = float(g['shares'].sum())
        else:
            px = float(g['price'].mean()); sh = np.nan
        return pd.Series({'date': g['date'].min(), 'price': px, 'shares': sh})
    orders = pd.DataFrame([agg(g) for _, g in mf.groupby(key)]).sort_values('date').reset_index(drop=True)
    return orders

def status(run, used, last_px, sessions_info, problems, mode, holdings):
    last = run.iloc[-1]; d = run.index[-1]
    hi252 = run.close.rolling(252, min_periods=60).max().iloc[-1]
    st = dict(engine_version=VERSION, date=str(d.date()), nail_close=round(float(last.close), 4),
              display_score=(None if not np.isfinite(last.cond) else float(100 - last.cond)),
              condition_score=(None if not np.isfinite(last.cond) else float(last.cond)),
              N=float(last.N) if np.isfinite(last.N) else None, A=float(last.A) if np.isfinite(last.A) else None,
              S=float(last.S) if np.isfinite(last.S) else None, dd252=round(float(last.dd252), 4), ref_high_252=round(float(hi252), 4),
              nail_price_for_N_bands={f'N={p} (낙폭 {int(c*100)}%)': round(hi252 * (1 + c), 2) for c, p in zip(N_CUTS, N_PTS)},
              state_mode=mode, campaign_tranches_used=used, last_fill_px=(None if last_px is None else round(float(last_px), 4)),
              data=sessions_info, problems=problems, holdings=holdings)
    if not np.isfinite(last.cond):
        miss = [k for k in ('N', 'A', 'S') if not np.isfinite(last[k])]
        st['verdict'] = f'DATA_INCOMPLETE — 최신 거래일 {d.date()}의 {",".join(miss)} 결측. 전일 값을 현재로 쓰지 않음'
    elif used == 0:
        ok = last.cond >= TH[0]
        st['verdict'] = (f'표시점수 {100-last.cond:.0f} (조건 {last.cond:.0f}) / 1차 기준 표시 ≤{100-TH[0]} → '
                         + (f'1차 매수 신호(다음 거래일 시가, 예산 {WEIGHTS[0]:.0%})' if ok else f'미충족({TH[0]-last.cond:.0f}점 부족)'))
    elif used < 3:
        need = last_px * (1 - STEP)
        st['verdict'] = (f'{used}차까지 체결(누적 예산 {sum(WEIGHTS[:used]):.0%}). 다음 {used+1}차(예산 {WEIGHTS[used]:.0%}): 표시 ≤{100-TH[used]} (현재 {100-last.cond:.0f}) '
                         f'AND 종가 ≤{need:.2f} (현재 {last.close:.2f}) AND 직전 체결 후 {MIN_GAP}거래일 이상')
    else:
        st['verdict'] = '3/3 체결 완료 — 재무장 전 추가 신호 없음'
    return st

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--r73-chart'); ap.add_argument('--nail'); ap.add_argument('--itb'); ap.add_argument('--spy')
    ap.add_argument('--vix', required=True); ap.add_argument('--hy', required=True)
    ap.add_argument('--calendar-from'); ap.add_argument('--my-fills', dest='my_fills')
    ap.add_argument('--start', default='2016-01-01'); ap.add_argument('--out', default='r8_out')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); problems = []
    vix = read_series(a.vix, 'VIX', problems); hy = read_series(a.hy, 'HY', problems)
    if a.r73_chart:
        ch = read_r73_chart(a.r73_chart); px = ch[['open', 'high', 'low', 'close']].copy(); A_src = ch['A'].astype(float); src = 'R7.3 차트 내장 A'
    else:
        if not (a.nail and a.itb and a.spy): sys.exit('원자료 모드는 --nail --itb --spy 모두 필요')
        px = read_price(a.nail, 'NAIL', problems)[['open', 'high', 'low', 'close']]
        itb = read_price(a.itb, 'ITB', problems); spy = read_price(a.spy, 'SPY', problems); src = 'ITB·SPY 원자료(전체 이력)'
    fb = pd.read_csv(a.calendar_from)['date'] if a.calendar_from else None
    start_cal = min(vix.index[0], hy.index[0], px.index[0]) if a.r73_chart else min(vix.index[0], hy.index[0], itb.index[0], px.index[0])
    # 예정 달력은 평가일 이후 2주까지 받아야 '이번 주가 끝났는가'를 판정할 수 있다(E2)
    sessions, cal_src = get_sessions(start_cal, px.index[-1] + pd.Timedelta(days=14), fb)
    t = px.index
    off = t.difference(sessions)
    if len(off): problems.append(f'NAIL 날짜 중 거래소 달력에 없는 날 {len(off)}일')
    N, dd = block_N(px.close)
    S, hyp, v60, vmiss = block_S(vix, hy, t, sessions)
    if vmiss: problems.append(f'VIX: 거래일 중 관측 없는 날 {vmiss}일(직전값 최대 2일 이월)')
    if a.r73_chart:
        A = A_src.reindex(t); parts = None
    else:
        A, parts = block_A_raw(itb, spy, t, sessions, calendar_has_future=(cal_src == 'XNYS'))
    df = px.copy(); df['dd252'] = dd; df['N'] = N; df['A'] = A; df['S'] = S
    df['hy_pct10y'] = hyp; df['vix60max'] = v60
    df['cond'] = df.N + df.A + df.S; df['score_display'] = 100 - df.cond
    if parts is not None: df = df.join(parts)
    if a.r73_chart:
        b_hat = bands_ge(hyp.values, (90, 75, 60, 45), (10, 8, 5, 2)) + bands_ge(v60.values, (45, 33, 25), (8, 5, 2))
        ok = np.isfinite(b_hat)
        print(f"[대조] 스트레스 블록(VIX≥45=8로 환산) vs R7.3 B 일치율 = {(b_hat[ok] == ch['B'].values[ok]).mean():.4%} ({ok.sum()}일)")
    run = df[df.index >= pd.Timestamp(a.start)]
    fills, events, used, last_px, camp = run_campaigns(run)
    mode = '모형 가상 캠페인'; holdings = None
    if a.my_fills:
        orders = load_my_fills(a.my_fills, run.index[-1], problems)
        rearm = run.index[(run.dd252 > RESET_DD).fillna(False)]
        last_rearm = rearm[-1] if len(rearm) else run.index[0]
        cur = orders[orders.date > last_rearm] if len(orders) else orders
        used = int(min(3, len(cur))); last_px = float(cur.price.iloc[-1]) if len(cur) else None
        mode = f'실제 주문 {used}건(마지막 재무장일 {last_rearm.date()} 이후, 부분체결 묶음)'
        if len(orders) and orders.shares.notna().all():
            holdings = dict(total_shares=float(orders.shares.sum()),
                            avg_cost=round(float((orders.price * orders.shares).sum() / orders.shares.sum()), 4),
                            note='재무장은 차수만 초기화하며 보유를 없애지 않음')
    last_day = run.index[-1]
    info = dict(calendar=cal_src, A_source=src, asof=str(last_day.date()),
                last_obs={'NAIL': str(px.index[-1].date()), 'VIX': str(vix.index[-1].date()), 'HY': str(hy.index[-1].date())})
    if not a.r73_chart: info['last_obs'].update({'ITB': str(itb.index[-1].date()), 'SPY': str(spy.index[-1].date())})
    p = sessions.get_indexer([last_day])[0]
    if vix.index[-1] < last_day: problems.append(f'VIX 최신 관측 {vix.index[-1].date()} < 평가일 {last_day.date()} (이월 사용)')
    need_hy = sessions[p - 2] if p >= 2 else None
    if need_hy is not None and hy.index[-1] < need_hy: problems.append(f'HY 최신 관측 {hy.index[-1].date()} < 필요 관측일 {need_hy.date()}')
    run.to_csv(os.path.join(a.out, 'r8_daily.csv'), float_format='%.6g')
    pd.DataFrame(fills).to_csv(os.path.join(a.out, 'r8_fills.csv'), index=False)
    st = status(run, used, last_px, info, problems, mode, holdings); st['events_tail'] = events[-5:]
    json.dump(st, open(os.path.join(a.out, 'r8_status.json'), 'w'), ensure_ascii=False, indent=2, default=str)
    print(json.dumps({k: st[k] for k in ('date', 'display_score', 'condition_score', 'N', 'A', 'S', 'verdict', 'problems')}, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
