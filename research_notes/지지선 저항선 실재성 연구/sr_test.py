#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지지선/저항선(S/R) 실재성 실증 검증 — 저장소 일봉 데이터 기반 walk-forward 테스트
=====================================================================================

실행:  python3 sr_test.py            (전체: 기본 설정 + 강건성 + 합성 널 200경로/종목)
       python3 sr_test.py --quick    (합성 널 30경로, 강건성 축소 — 디버깅용)
       python3 sr_test.py --paths 100

출력(같은 폴더):
  tables.md                 자동 생성 마크다운 표 (보고서에 그대로 인용)
  results_summary.csv       설정별/종목별 실제 vs 플라시보 vs 베이스라인 요약
  results_conditional.csv   조건별 분할 결과
  results_synthetic.csv     합성 널 분포 요약
  events_real.csv           기본 설정의 모든 실제 이벤트 (날짜/레벨/결과)
  examples.csv              SOXL/SOX 예시 이벤트

설계 원칙: 모든 레벨은 테스트 이벤트 "이전" 데이터만으로 식별(walk-forward).
"""
import argparse
import os
import sys
import time
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "data", "prices"))
KR_DIR = os.path.join(HERE, "kr_data")
TICKERS_US = ["SPY", "QQQ", "SOX", "SOXX", "SOXL", "NVDA", "MU"]
TICKERS_KR = ["TIGER200IT", "SAMSUNG", "HYNIX", "KOSPI", "KODEX_SEMI"]
TICKERS = TICKERS_US + TICKERS_KR
MARKET = {**{t: "US" for t in TICKERS_US}, **{t: "KR" for t in TICKERS_KR}}
FILES = {**{t: os.path.join(DATA_DIR, f"{t}.csv") for t in TICKERS_US},
         **{t: os.path.join(KR_DIR, f"{t}.csv") for t in TICKERS_KR}}
# 라운드넘버 분석은 '화면에 보였던 가격'이어야 의미가 있으므로, 분할 소급조정이 없는 구간만 사용
# (NVDA/SOXL/SOXX 는 표본 내 분할이 여러 번이라 제외, SAMSUNG 은 2018-05 50:1 액면분할 이후, HYNIX 는 2002-12 병합 이후)
ROUND_FROM = {"SPY": "1900-01-01", "QQQ": "1900-01-01", "SOX": "1900-01-01", "MU": "1900-01-01",
              "TIGER200IT": "1900-01-01", "KOSPI": "1900-01-01", "KODEX_SEMI": "1900-01-01",
              "SAMSUNG": "2018-05-04", "HYNIX": "2003-01-01"}
SEED = 20261020
N_FWD = 20          # 선행 수익률 최대 지평
APPROACH_GAP = 0.02  # 전일 종가가 레벨에서 최소 2% 떨어져 있어야 "접근"
MIN_AGE = 10         # 레벨 최소 나이(거래일)
PLACEBO_EXCL = 0.015  # 플라시보 레벨은 실제 피벗에서 1.5% 이상 떨어져야 함


# ----------------------------------------------------------------------------- 데이터
def load_bars(ticker):
    df = pd.read_csv(FILES[ticker])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    for c in ["open", "high", "low", "close"]:
        df[c] = df[c].astype(float)
    n0 = len(df)
    # 명백한 오염 행 제거: close<=0, high<low, 하루 60% 초과 점프(앞뒤 양쪽 다 점프하는 '스파이크'만)
    bad = (df["close"] <= 0) | (df["high"] < df["low"])
    r = df["close"].pct_change()
    spike = (r.abs() > 0.6) & (df["close"].pct_change(-1).abs() > 0.6)
    bad |= spike.fillna(False)
    big = (r.abs() > 0.6) & ~spike
    if big.any():
        print(f"  [{ticker}] 60% 초과 일간 변동 {int(big.sum())}건 — 지속적 변화로 판단, 유지:",
              df.loc[big, "date"].dt.date.tolist())
    df = df.loc[~bad].reset_index(drop=True)
    # 반올림 오류(high<open 등) 보정
    df["high"] = df[["open", "high", "close"]].max(axis=1)
    df["low"] = df[["open", "low", "close"]].min(axis=1)
    o, h, l, c = (df[k].to_numpy(float) for k in ["open", "high", "low", "close"])
    bars = make_bars(o, h, l, c)
    bars["dates"] = df["date"].to_numpy()
    bars["ticker"] = ticker
    bars["n_dropped"] = n0 - len(df)
    bars["market"] = MARKET[ticker]
    return bars


def make_bars(o, h, l, c):
    n = len(c)
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    tr[0] = h[0] - l[0]
    atr = pd.Series(tr).rolling(14).mean().to_numpy()
    atr_prev = np.r_[np.nan, atr[:-1]]  # t-1 시점까지의 ATR(14)
    lr = np.r_[np.nan, np.diff(np.log(c))]
    vol20 = pd.Series(lr).rolling(20).std().to_numpy() * np.sqrt(252)
    vol20_prev = np.r_[np.nan, vol20[:-1]]
    # 확장 중앙값(walk-forward 레짐 라벨): 최소 250일
    vol_med = pd.Series(vol20_prev).expanding(250).median().to_numpy()
    ma200 = pd.Series(c).rolling(200).mean().to_numpy()
    ma200_prev = np.r_[np.nan, ma200[:-1]]
    return dict(o=o, h=h, l=l, c=c, n=n, pc=pc, atr_prev=atr_prev,
                vol20_prev=vol20_prev, vol_med=vol_med, ma200_prev=ma200_prev)


# ----------------------------------------------------------------------------- 피벗
def find_pivots(h, l, k):
    """k봉 좌우 대비 최고/최저인 봉. 좌측은 >=, 우측은 > (동률 시 첫 봉)."""
    n = len(h)
    idx = np.arange(k, n - k)
    wh = sliding_window_view(h, 2 * k + 1)  # (n-2k, 2k+1), 중앙 = k
    wl = sliding_window_view(l, 2 * k + 1)
    ph = (wh[:, k] >= wh[:, :k].max(1)) & (wh[:, k] > wh[:, k + 1:].max(1))
    pl = (wl[:, k] <= wl[:, :k].min(1)) & (wl[:, k] < wl[:, k + 1:].min(1))
    return idx[ph], idx[pl]


def pivot_table(bars, k_small=5, k_big=10):
    ih5, il5 = find_pivots(bars["h"], bars["l"], k_small)
    ih10, il10 = find_pivots(bars["h"], bars["l"], k_big)
    idx = np.r_[ih5, il5]
    price = np.r_[bars["h"][ih5], bars["l"][il5]]
    is_high = np.r_[np.ones(len(ih5), bool), np.zeros(len(il5), bool)]
    k10 = np.r_[np.isin(ih5, ih10), np.isin(il5, il10)]
    order = np.argsort(idx, kind="stable")
    return dict(idx=idx[order], price=price[order], is_high=is_high[order], k10=k10[order])


# ----------------------------------------------------------------------------- 이벤트 탐지
def detect_events(bars, piv, L, tol, direction):
    """
    direction=+1: 지지 테스트(위에서 접근), -1: 저항 테스트(아래에서 접근)
    반환: dict of arrays (t, v, pid, prior_break) — (t) 당 하나로 중복 제거
    """
    n = bars["n"]
    lo, hi, pc, c = bars["l"], bars["h"], bars["pc"], bars["c"]
    A = max(MIN_AGE, 11)  # k=10 피벗이 완전히 확정된 뒤(i+10 <= t-1)
    ages = np.arange(A, L + 1)
    P = len(piv["idx"])
    if P == 0:
        return dict(t=np.array([], int), v=np.array([]), pid=np.array([], int), prior_break=np.array([], bool))
    T = piv["idx"][:, None] + ages[None, :]            # (P, W)
    valid = (T >= 1) & (T <= n - 1 - N_FWD)
    Tc = np.clip(T, 1, n - 1)
    v = piv["price"][:, None]
    if direction > 0:
        cond = (v <= pc[Tc] * (1 - APPROACH_GAP)) & (lo[Tc] <= v * (1 + tol)) & (lo[Tc - 1] > v * (1 + tol))
    else:
        cond = (v >= pc[Tc] * (1 + APPROACH_GAP)) & (hi[Tc] >= v * (1 - tol)) & (hi[Tc - 1] < v * (1 - tol))
    cond &= valid
    # 피벗 이후 ~ 전일까지 레벨이 이미 뚫린 적이 있는가 (종가 기준)
    # closes at i+1 .. t-1 : 누적 min/max를 (P, W) 격자 위에서 계산
    C = c[np.clip(piv["idx"][:, None] + np.arange(1, L + 1)[None, :], 0, n - 1)]  # 오프셋 1..L
    if direction > 0:
        cum = np.minimum.accumulate(C, axis=1)
        pb_full = cum < v * (1 - tol)
    else:
        cum = np.maximum.accumulate(C, axis=1)
        pb_full = cum > v * (1 + tol)
    # 이벤트 날 t = i + a 이면 전일까지의 누적은 오프셋 a-1 → 열 인덱스 a-2
    pb = pb_full[:, ages - 2]
    pi, wi = np.nonzero(cond)
    t = T[pi, wi]
    vv = piv["price"][pi]
    pbv = pb[pi, wi]
    # 중복 제거: 같은 날 여러 레벨 → 전일 종가에 가장 가까운 것(처음 만나는 레벨)
    if len(t) == 0:
        return dict(t=t, v=vv, pid=pi, prior_break=pbv)
    key = -vv if direction > 0 else vv
    order = np.lexsort((key, t))
    t, vv, pi, pbv = t[order], vv[order], pi[order], pbv[order]
    first = np.r_[True, t[1:] != t[:-1]]
    return dict(t=t[first], v=vv[first], pid=pi[first], prior_break=pbv[first])


def outcomes(bars, t, v, direction, tol, X_pct, N_list=(5, 10)):
    """bounce/break 분류 + 연속 결과. 모두 이벤트 날 종가(day 0)부터 평가."""
    c, hi, lo, atr = bars["c"], bars["h"], bars["l"], bars["atr_prev"]
    E = len(t)
    out = {}
    if E == 0:
        return out
    D = t[:, None] + np.arange(0, N_FWD + 1)[None, :]   # (E, 21)
    C = c[D]
    vcol = v[:, None]
    s = 1.0 if direction > 0 else -1.0
    # 거리(레벨 기준, 반전 방향이 양수)
    dist = s * (C / vcol - 1.0)
    brk = dist < -tol
    for xname, X in (("pct", np.full(E, X_pct)), ("atr", atr[t] / v)):
        bnc = dist >= X[:, None]
        for N in N_list:
            b1 = brk[:, : N + 1]
            n1 = bnc[:, : N + 1]
            fb = np.where(b1.any(1), b1.argmax(1), 99)
            fn = np.where(n1.any(1), n1.argmax(1), 99)
            res = np.where(fn < fb, 1, np.where(fb < fn, -1, 0))  # 1=bounce, -1=break, 0=미해결
            out[f"res_{xname}_N{N}"] = res
            out[f"day_{xname}_N{N}"] = np.minimum(fb, fn)
    # 선행 수익률(반전 방향 기준, 이벤트일 종가 대비)
    for d in (1, 5, 10, 20):
        out[f"ret{d}"] = s * (C[:, d] / C[:, 0] - 1.0)
    # MFE / MAE (10일, 반전 방향 기준)
    H = hi[D[:, 1:11]]
    Lw = lo[D[:, 1:11]]
    if direction > 0:
        out["mfe10"] = H.max(1) / C[:, 0] - 1.0
        out["mae10"] = Lw.min(1) / C[:, 0] - 1.0
    else:
        out["mfe10"] = -(Lw.min(1) / C[:, 0] - 1.0)
        out["mae10"] = -(H.max(1) / C[:, 0] - 1.0)
    out["day0_dist"] = dist[:, 0]
    return out


# ----------------------------------------------------------------------------- 플라시보
def near_any_real(idx_q, price_q, piv, L):
    """후보 (idx, price)가 ±L 인덱스 창 안의 실제 피벗과 1.5% 이내인지 (벡터화, 청크)."""
    out = np.zeros(len(idx_q), bool)
    pi, pp = piv["idx"], piv["price"]
    step = 400
    for s in range(0, len(idx_q), step):
        iq, pq = idx_q[s:s + step, None], price_q[s:s + step, None]
        m = (np.abs(pi[None, :] - iq) <= L) & (np.abs(pp[None, :] / pq - 1.0) < PLACEBO_EXCL)
        out[s:s + step] = m.any(1)
    return out


def placebo_shift(piv, L, rng, lo=0.03, hi=0.08):
    """각 실제 피벗을 ±3~8% 무작위 이동 (실제 피벗 1.5% 이내면 재추출)."""
    P = len(piv["idx"])
    price = piv["price"].copy()
    todo = np.ones(P, bool)
    for _ in range(25):
        if not todo.any():
            break
        m = todo.sum()
        sgn = rng.choice([-1.0, 1.0], m)
        u = rng.uniform(lo, hi, m)
        cand = piv["price"][todo] * (1 + sgn * u)
        bad = near_any_real(piv["idx"][todo], cand, piv, L)
        ids = np.nonzero(todo)[0]
        price[ids[~bad]] = cand[~bad]
        todo[ids[~bad]] = False
    ok = ~todo
    return dict(idx=piv["idx"][ok], price=price[ok], is_high=piv["is_high"][ok], k10=piv["k10"][ok])


def placebo_uniform(bars, piv, L, rng):
    """각 실제 피벗 시점의 직전 L일 가격범위 안에서 균등 추출(실제 피벗 1.5% 이내 제외)."""
    hi, lo = bars["h"], bars["l"]
    P = len(piv["idx"])
    i0 = np.maximum(piv["idx"] - L, 0)
    rmin = np.array([lo[a:b + 1].min() for a, b in zip(i0, piv["idx"])])
    rmax = np.array([hi[a:b + 1].max() for a, b in zip(i0, piv["idx"])])
    price = np.full(P, np.nan)
    todo = np.ones(P, bool)
    for _ in range(25):
        if not todo.any():
            break
        cand = rng.uniform(rmin[todo], rmax[todo])
        bad = near_any_real(piv["idx"][todo], cand, piv, L)
        ids = np.nonzero(todo)[0]
        price[ids[~bad]] = cand[~bad]
        todo[ids[~bad]] = False
    ok = ~todo
    return dict(idx=piv["idx"][ok], price=price[ok], is_high=piv["is_high"][ok], k10=piv["k10"][ok])


def baseline_virtual(bars, piv, L, tol, direction, dist_pool, rng, draws=3):
    """
    평균회귀 베이스라인: 실제 이벤트의 '전일 종가 대비 레벨 거리' 분포에서 d를 뽑아
    가상 레벨 v'=pc*d 를 두고, 같은 접근 규칙을 만족하지만 근처(1.5%)에 활성 피벗이 없는 날만 채택.
    """
    n = bars["n"]
    lo, hi, pc = bars["l"], bars["h"], bars["pc"]
    A = max(MIN_AGE, 11)
    ts = np.arange(max(L, 1), n - N_FWD)
    if len(dist_pool) == 0 or len(ts) == 0:
        return dict(t=np.array([], int), v=np.array([]))
    T = np.repeat(ts, draws)
    d = rng.choice(dist_pool, len(T))
    v = pc[T] * d
    if direction > 0:
        ok = (lo[T] <= v * (1 + tol)) & (lo[T - 1] > v * (1 + tol)) & (v <= pc[T] * (1 - APPROACH_GAP))
    else:
        ok = (hi[T] >= v * (1 - tol)) & (hi[T - 1] < v * (1 - tol)) & (v >= pc[T] * (1 + APPROACH_GAP))
    T, v = T[ok], v[ok]
    # 활성 피벗(나이 A..L) 근처 제외
    pi, pp = piv["idx"], piv["price"]
    keep = np.ones(len(T), bool)
    step = 400
    for s in range(0, len(T), step):
        tq, vq = T[s:s + step, None], v[s:s + step, None]
        age = tq - pi[None, :]
        m = (age >= A) & (age <= L) & (np.abs(pp[None, :] / vq - 1.0) < PLACEBO_EXCL)
        keep[s:s + step] = ~m.any(1)
    T, v = T[keep], v[keep]
    if len(T) == 0:
        return dict(t=T, v=v)
    key = -v if direction > 0 else v
    order = np.lexsort((key, T))
    T, v = T[order], v[order]
    first = np.r_[True, T[1:] != T[:-1]]
    return dict(t=T[first], v=v[first])


# ----------------------------------------------------------------------------- 부가 속성
def count_touches(ev_t, ev_v, piv, L, ctol):
    A = max(MIN_AGE, 11)
    out = np.zeros(len(ev_t), int)
    pi, pp = piv["idx"], piv["price"]
    step = 400
    for s in range(0, len(ev_t), step):
        tq, vq = ev_t[s:s + step, None], ev_v[s:s + step, None]
        age = tq - pi[None, :]
        m = (age >= A) & (age <= L) & (np.abs(pp[None, :] / vq - 1.0) <= ctol)
        out[s:s + step] = m.sum(1)
    return out


def round_unit(p):
    units = np.array([0.05, 0.1, 0.5, 1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000])
    thr = 0.10 * p
    u = np.full(len(p), np.nan)
    for x in units:
        u[x <= thr] = x
    return u


def is_round(v, tol=0.003):
    u = round_unit(v)
    off = np.abs(v / u - np.round(v / u)) * u
    return (off <= tol * v) & ~np.isnan(u)


# ----------------------------------------------------------------------------- 파이프라인
def run_ticker(bars, L, tol, X_pct, rng, kinds=("real", "shift", "uniform", "virtual"),
               with_attrs=True, piv=None):
    """한 종목·한 설정에 대해 모든 레벨 종류의 이벤트+결과 DataFrame 반환."""
    if piv is None:
        piv = pivot_table(bars)
    level_sets = {"real": piv}
    if "shift" in kinds:
        level_sets["shift"] = placebo_shift(piv, L, rng)
    if "uniform" in kinds:
        level_sets["uniform"] = placebo_uniform(bars, piv, L, rng)
    frames = []
    dist_pools = {}
    for kind, pv in level_sets.items():
        for direction in (+1, -1):
            ev = detect_events(bars, pv, L, tol, direction)
            if len(ev["t"]) == 0:
                continue
            oc = outcomes(bars, ev["t"], ev["v"], direction, tol, X_pct)
            df = pd.DataFrame({"t": ev["t"], "level": ev["v"], "dir": direction,
                               "kind": kind, "prior_break": ev["prior_break"]})
            df["pivot_idx"] = pv["idx"][ev["pid"]]
            df["pivot_is_high"] = pv["is_high"][ev["pid"]]
            df["pivot_k10"] = pv["k10"][ev["pid"]]
            for k2, arr in oc.items():
                df[k2] = arr
            if with_attrs:
                df["touches"] = count_touches(ev["t"], ev["v"], piv, L, tol)
                df["is_round"] = is_round(ev["v"])
            frames.append(df)
            if kind == "real":
                dist_pools[direction] = ev["v"] / bars["pc"][ev["t"]]
    if "virtual" in kinds:
        for direction in (+1, -1):
            ev = baseline_virtual(bars, piv, L, tol, direction, dist_pools.get(direction, np.array([])), rng)
            if len(ev["t"]) == 0:
                continue
            oc = outcomes(bars, ev["t"], ev["v"], direction, tol, X_pct)
            df = pd.DataFrame({"t": ev["t"], "level": ev["v"], "dir": direction,
                               "kind": "virtual", "prior_break": False,
                               "pivot_idx": -1, "pivot_is_high": False, "pivot_k10": False})
            for k2, arr in oc.items():
                df[k2] = arr
            if with_attrs:
                df["touches"] = 0
                df["is_round"] = is_round(ev["v"])
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["ticker"] = bars["ticker"]
    df["market"] = bars.get("market", "SYN")
    df["age"] = df["t"] - df["pivot_idx"]
    df.loc[df["kind"] == "virtual", "age"] = -1
    df["dist_prev"] = np.abs(df["level"] / bars["pc"][df["t"].to_numpy()] - 1.0)
    if "dates" in bars:
        df["date"] = bars["dates"][df["t"].to_numpy()]
        df["year"] = pd.DatetimeIndex(df["date"]).year
        v20, vm = bars["vol20_prev"][df["t"].to_numpy()], bars["vol_med"][df["t"].to_numpy()]
        df["vol_regime"] = np.where(np.isnan(vm), "n/a", np.where(v20 > vm, "high", "low"))
        ma = bars["ma200_prev"][df["t"].to_numpy()]
        pcl = bars["pc"][df["t"].to_numpy()]
        df["trend"] = np.where(np.isnan(ma), "n/a", np.where(pcl > ma, "above200", "below200"))
        rf = ROUND_FROM.get(bars["ticker"])
        df["round_ok"] = (df["date"] >= np.datetime64(rf)) if rf else False
    return df


# ----------------------------------------------------------------------------- 합성 널
def bootstrap_bars(bars, block, rng):
    o, h, l, c = bars["o"], bars["h"], bars["l"], bars["c"]
    pc = c[:-1]
    R = np.log(np.c_[o[1:], h[1:], l[1:], c[1:]] / pc[:, None])  # (n-1, 4)
    m = len(R)
    nb = int(np.ceil(m / block))
    starts = rng.integers(0, m - block + 1, nb)
    sel = (starts[:, None] + np.arange(block)[None, :]).ravel()[:m]
    Rb = R[sel]
    cb = np.r_[c[0], c[0] * np.exp(np.cumsum(Rb[:, 3]))]
    prev = cb[:-1]
    ob = np.r_[o[0], prev * np.exp(Rb[:, 0])]
    hb = np.r_[h[0], prev * np.exp(Rb[:, 1])]
    lb = np.r_[l[0], prev * np.exp(Rb[:, 2])]
    nb_ = make_bars(ob, hb, lb, cb)
    nb_["ticker"] = bars["ticker"]
    return nb_


# ----------------------------------------------------------------------------- 통계
def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return cen - half, cen + half


def two_prop(k1, n1, k2, n2):
    if min(n1, n2) == 0:
        return np.nan, np.nan, np.nan, np.nan
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se if se > 0 else np.nan
    pval = 2 * (1 - stats.norm.cdf(abs(z))) if np.isfinite(z) else np.nan
    # Newcombe(Wilson 기반) 차이 CI
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = p1 - p2
    ci = (d - np.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + np.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2))
    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))  # Cohen's h
    return z, pval, ci, h


def rate_row(df, col):
    """resolved 기준 bounce rate와 전체 기준 bounce/break/unresolved 비율."""
    r = df[col].to_numpy()
    n = len(r)
    nb, nk = int((r == 1).sum()), int((r == -1).sum())
    res = nb + nk
    return dict(n=n, bounce=nb, brk=nk, unres=n - res,
                rate=nb / res if res else np.nan,
                rate_all=nb / n if n else np.nan)


def fmt_pct(x, d=1):
    return "–" if (x is None or (isinstance(x, float) and np.isnan(x))) else f"{100 * x:.{d}f}%"


def md_table(rows, cols):
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(lines)


# ----------------------------------------------------------------------------- 메인
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", type=int, default=200, help="합성 널 경로 수/종목")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--tickers", default=",".join(TICKERS))
    ap.add_argument("--paths-secondary", type=int, default=None,
                    help="SOX/SPY/SOXL/TIGER200IT 외 종목의 합성 경로 수(기본: --paths 와 동일)")
    args = ap.parse_args()
    if args.quick:
        args.paths = min(args.paths, 30)
    tickers = args.tickers.split(",")
    rng = np.random.default_rng(SEED)
    t0 = time.time()
    md = []
    md.append(f"# 자동 생성 표 (sr_test.py, seed={SEED}, paths={args.paths})\n")

    print("== 데이터 로드")
    bars = {}
    for tk in tickers:
        bars[tk] = load_bars(tk)
        b = bars[tk]
        print(f"  {tk}[{MARKET[tk]}]: {b['n']}일 {pd.Timestamp(b['dates'][0]).date()}~{pd.Timestamp(b['dates'][-1]).date()}"
              f"  제거행={b['n_dropped']}")
    md.append("## 데이터\n")
    md.append(md_table([dict(t=f"{tk} ({MARKET[tk]})", n=bars[tk]["n"], s=str(pd.Timestamp(bars[tk]["dates"][0]).date()),
                             e=str(pd.Timestamp(bars[tk]["dates"][-1]).date()), d=bars[tk]["n_dropped"],
                             p=len(pivot_table(bars[tk])["idx"]))
                        for tk in tickers], ["t", "n", "s", "e", "d", "p"])
              .replace("| t | n | s | e | d | p |", "| 종목 | 일수 | 시작 | 끝 | 제거행 | 피벗수(k=5) |"))

    # ------------------------------------------------------------------ 설정 격자
    BASE = dict(L=250, tol=0.01, X=0.02)
    configs = [BASE]
    if not args.quick:
        configs += [dict(L=120, tol=0.01, X=0.02), dict(L=500, tol=0.01, X=0.02),
                    dict(L=250, tol=0.005, X=0.02), dict(L=250, tol=0.02, X=0.02)]
    else:
        configs += [dict(L=500, tol=0.01, X=0.02)]

    all_events = {}
    summary_rows = []
    print("== 실제 데이터 파이프라인")
    for cfg in configs:
        key = f"L{cfg['L']}_tol{cfg['tol']}_X{cfg['X']}"
        frames = []
        for tk in tickers:
            df = run_ticker(bars[tk], cfg["L"], cfg["tol"], cfg["X"], rng)
            frames.append(df)
        ev = pd.concat(frames, ignore_index=True)
        all_events[key] = ev
        print(f"  {key}: 이벤트 {len(ev)}건 (real {int((ev.kind == 'real').sum())})  {time.time() - t0:.0f}s")

    base_key = f"L{BASE['L']}_tol{BASE['tol']}_X{BASE['X']}"
    ev0 = all_events[base_key]
    ev0.to_csv(os.path.join(HERE, "events_real.csv"), index=False)

    # ------------------------------------------------------------------ 요약표: 실제 vs 플라시보
    def summarize(ev, label, col, group_cols=("ticker",)):
        rows = []
        groups = [("POOLED", ev)] + [(g, d) for g, d in ev.groupby(list(group_cols))]
        for g, d in groups:
            gname = g if isinstance(g, str) else "/".join(map(str, g))
            real = rate_row(d[d.kind == "real"], col)
            row = dict(config=label, outcome=col, group=gname, n_real=real["n"], real_rate=real["rate"],
                       real_rate_all=real["rate_all"], real_unres=real["unres"] / max(real["n"], 1))
            for kind in ("shift", "uniform", "virtual"):
                pk = rate_row(d[d.kind == kind], col)
                z, p, ci, h = two_prop(real["bounce"], real["bounce"] + real["brk"], pk["bounce"], pk["bounce"] + pk["brk"])
                row.update({f"n_{kind}": pk["n"], f"{kind}_rate": pk["rate"], f"diff_{kind}": real["rate"] - pk["rate"],
                            f"ci_{kind}_lo": ci[0] if isinstance(ci, tuple) else np.nan,
                            f"ci_{kind}_hi": ci[1] if isinstance(ci, tuple) else np.nan,
                            f"z_{kind}": z, f"p_{kind}": p, f"h_{kind}": h})
            # 선행 수익률(반전 방향) 실제 vs uniform 플라시보
            for d_ in (1, 5, 10, 20):
                a = d[d.kind == "real"][f"ret{d_}"].to_numpy()
                b = d[d.kind == "uniform"][f"ret{d_}"].to_numpy()
                row[f"ret{d_}_real"] = a.mean() if len(a) else np.nan
                row[f"ret{d_}_uniform"] = b.mean() if len(b) else np.nan
                if len(a) > 2 and len(b) > 2:
                    row[f"ret{d_}_p"] = stats.ttest_ind(a, b, equal_var=False).pvalue
            a = d[d.kind == "real"]
            row["mfe10_real"] = a["mfe10"].mean() if len(a) else np.nan
            row["mae10_real"] = a["mae10"].mean() if len(a) else np.nan
            b = d[d.kind == "uniform"]
            row["mfe10_uniform"] = b["mfe10"].mean() if len(b) else np.nan
            row["mae10_uniform"] = b["mae10"].mean() if len(b) else np.nan
            rows.append(row)
        return rows

    for key, ev in all_events.items():
        for col in ("res_pct_N5", "res_pct_N10", "res_atr_N5", "res_atr_N10"):
            summary_rows += summarize(ev, key, col)
            summary_rows += summarize(ev, key, col, group_cols=("market",))
            summary_rows += summarize(ev, key, col, group_cols=("dir",))
            summary_rows += summarize(ev, key, col, group_cols=("market", "dir"))
    summ = pd.DataFrame(summary_rows)
    summ.to_csv(os.path.join(HERE, "results_summary.csv"), index=False)

    # 마크다운 헤드라인 표
    def headline_table(col, key=base_key):
        s = summ[(summ.config == key) & (summ.outcome == col)]
        rows = []
        for _, r in s.iterrows():
            g = {"1": "지지(전체)", "-1": "저항(전체)", "US": "POOLED-US", "KR": "POOLED-KR",
                 "US/1": "US 지지", "US/-1": "US 저항", "KR/1": "KR 지지", "KR/-1": "KR 저항"}.get(r.group, r.group)
            rows.append(dict(g=g, n=int(r.n_real), real=fmt_pct(r.real_rate),
                             unres=fmt_pct(r.real_unres),
                             shift=f"{fmt_pct(r.shift_rate)} (n={int(r.n_shift)})",
                             uni=f"{fmt_pct(r.uniform_rate)} (n={int(r.n_uniform)})",
                             virt=f"{fmt_pct(r.virtual_rate)} (n={int(r.n_virtual)})",
                             d_uni=f"{100 * r.diff_uniform:+.1f}pp [{100 * r.ci_uniform_lo:+.1f}, {100 * r.ci_uniform_hi:+.1f}] p={r.p_uniform:.3f}",
                             d_virt=f"{100 * r.diff_virtual:+.1f}pp p={r.p_virtual:.3f}",
                             d_shift=f"{100 * r.diff_shift:+.1f}pp p={r.p_shift:.3f}"))
        return md_table(rows, ["g", "n", "real", "unres", "shift", "uni", "virt", "d_shift", "d_uni", "d_virt"]) \
            .replace("| g | n | real | unres | shift | uni | virt | d_shift | d_uni | d_virt |",
                     "| 그룹 | 실제 n | 실제 bounce율 | 미해결 | 플라시보(이동) | 플라시보(균등) | 베이스라인(가상레벨) | 차이 vs 이동 | 차이 vs 균등 [95% CI] | 차이 vs 가상 |")

    md.append("\n## 1. 헤드라인: 기본 설정 (L=250, tol=1%, X=2%)\n")
    for col, nm in (("res_pct_N10", "N=10, X=2%"), ("res_pct_N5", "N=5, X=2%"),
                    ("res_atr_N10", "N=10, X=1·ATR(14)"), ("res_atr_N5", "N=5, X=1·ATR(14)")):
        md.append(f"\n### {nm}\n")
        md.append(headline_table(col))

    # 선행 수익률 표
    md.append("\n## 2. 선행 수익률(반전 방향, 이벤트일 종가 대비) — 실제 vs 균등 플라시보\n")
    s = summ[(summ.config == base_key) & (summ.outcome == "res_pct_N10")]
    rows = []
    for _, r in s.iterrows():
        g = {"1": "지지(전체)", "-1": "저항(전체)", "US": "POOLED-US", "KR": "POOLED-KR",
             "US/1": "US 지지", "US/-1": "US 저항", "KR/1": "KR 지지", "KR/-1": "KR 저항"}.get(r.group, r.group)
        rows.append(dict(g=g, n=int(r.n_real),
                         r1=f"{100 * r.ret1_real:+.2f} / {100 * r.ret1_uniform:+.2f} (p={r.ret1_p:.2f})",
                         r5=f"{100 * r.ret5_real:+.2f} / {100 * r.ret5_uniform:+.2f} (p={r.ret5_p:.2f})",
                         r10=f"{100 * r.ret10_real:+.2f} / {100 * r.ret10_uniform:+.2f} (p={r.ret10_p:.2f})",
                         r20=f"{100 * r.ret20_real:+.2f} / {100 * r.ret20_uniform:+.2f} (p={r.ret20_p:.2f})",
                         mfe=f"{100 * r.mfe10_real:+.2f} / {100 * r.mfe10_uniform:+.2f}",
                         mae=f"{100 * r.mae10_real:+.2f} / {100 * r.mae10_uniform:+.2f}"))
    md.append(md_table(rows, ["g", "n", "r1", "r5", "r10", "r20", "mfe", "mae"]).replace(
        "| g | n | r1 | r5 | r10 | r20 | mfe | mae |",
        "| 그룹 | n | 1일 실제/플라시보 (%) | 5일 | 10일 | 20일 | MFE10 실제/플라시보 | MAE10 실제/플라시보 |"))

    # 연도별 차이(겹침 보정용 조잡한 검정)
    md.append("\n## 3. 연도별 (실제 − 균등 플라시보) bounce율 차이, 시장별 풀링, N=10 X=2%\n")
    for mk in ("US", "KR"):
        yr_rows = []
        for yr, d in ev0[ev0.market == mk].groupby("year"):
            a, b = rate_row(d[d.kind == "real"], "res_pct_N10"), rate_row(d[d.kind == "uniform"], "res_pct_N10")
            if a["bounce"] + a["brk"] >= 20 and b["bounce"] + b["brk"] >= 20:
                yr_rows.append(dict(year=int(yr), n_real=a["n"], real=a["rate"], uni=b["rate"], diff=a["rate"] - b["rate"]))
        yrdf = pd.DataFrame(yr_rows)
        tt = stats.ttest_1samp(yrdf["diff"], 0.0)
        pos = int((yrdf["diff"] > 0).sum())
        md.append(f"\n### {mk}: 연도 수 {len(yrdf)}, 차이>0인 연도 {pos}개, 평균 차이 {100 * yrdf['diff'].mean():+.2f}pp, "
                  f"t={tt.statistic:.2f}, p={tt.pvalue:.3f}, 부호검정 p={stats.binomtest(pos, len(yrdf)).pvalue:.3f}\n")
        md.append(md_table([dict(y=r.year, n=r.n_real, a=fmt_pct(r.real), b=fmt_pct(r.uni), d=f"{100 * r.diff:+.1f}pp")
                            for r in yrdf.itertuples()], ["y", "n", "a", "b", "d"]).replace(
            "| y | n | a | b | d |", "| 연도 | 실제 n | 실제 | 플라시보 | 차이 |"))

    # ------------------------------------------------------------------ 강건성 표
    md.append("\n## 4. 강건성: 설정별 풀링 결과 (실제 vs 균등 플라시보 vs 가상레벨)\n")
    rows = []
    for key in all_events:
        for col in ("res_pct_N5", "res_pct_N10", "res_atr_N10"):
          for grp in ("US", "KR"):
            r = summ[(summ.config == key) & (summ.outcome == col) & (summ.group == grp)].iloc[0]
            rows.append(dict(cfg=f"{key} [{grp}]", oc=col, n=int(r.n_real), real=fmt_pct(r.real_rate), shift=fmt_pct(r.shift_rate),
                             uni=fmt_pct(r.uniform_rate), virt=fmt_pct(r.virtual_rate),
                             du=f"{100 * r.diff_uniform:+.1f}pp (p={r.p_uniform:.3f})",
                             dv=f"{100 * r.diff_virtual:+.1f}pp (p={r.p_virtual:.3f})",
                             ds=f"{100 * r.diff_shift:+.1f}pp (p={r.p_shift:.3f})"))
    md.append(md_table(rows, ["cfg", "oc", "n", "real", "shift", "uni", "virt", "ds", "du", "dv"]).replace(
        "| cfg | oc | n | real | shift | uni | virt | ds | du | dv |",
        "| 설정 | 결과정의 | 실제 n | 실제 | 이동 | 균등 | 가상 | 차이 vs 이동 | 차이 vs 균등 | 차이 vs 가상 |"))

    # ------------------------------------------------------------------ 조건별 분할
    print("== 조건별 분할")
    cond_rows = []
    n_cells = 0

    def cond_block(ev, label, cond_col, col="res_pct_N10", kinds_cmp=("uniform",), only_real=False, order=None):
        nonlocal n_cells
        rows = []
        vals = order or sorted(ev[cond_col].dropna().unique(), key=str)
        for val in vals:
            d = ev[ev[cond_col] == val]
            real = rate_row(d[d.kind == "real"], col)
            row = dict(split=label, value=str(val), n_real=real["n"], real_rate=real["rate"],
                       ci_lo=wilson(real["bounce"], real["bounce"] + real["brk"])[0],
                       ci_hi=wilson(real["bounce"], real["bounce"] + real["brk"])[1])
            if not only_real:
                for kind in kinds_cmp:
                    pk = rate_row(d[d.kind == kind], col)
                    z, p, ci, h = two_prop(real["bounce"], real["bounce"] + real["brk"], pk["bounce"], pk["bounce"] + pk["brk"])
                    row.update({f"n_{kind}": pk["n"], f"{kind}_rate": pk["rate"], f"diff_{kind}": real["rate"] - pk["rate"],
                                f"p_{kind}": p, f"h_{kind}": h})
                    n_cells += 1
            rows.append(row)
        return rows

    evb = ev0.copy()
    evb["touch_bin"] = pd.cut(evb["touches"], [0, 1, 2, 99], labels=["1", "2", "3+"]).astype(str)
    evb["age_bin"] = pd.cut(evb["age"], [0, 60, 250, 9999], labels=["10-60", "61-250", ">250"]).astype(str)
    evb["dir_name"] = np.where(evb["dir"] > 0, "support", "resistance")
    evb["role"] = np.where(evb["kind"] == "virtual", "n/a",
                           np.where((evb["dir"] > 0) == (~evb["pivot_is_high"]), "same-role", "role-reversal"))
    evb["k_name"] = np.where(evb["pivot_k10"], "k10", "k5-only")
    evb["pb_name"] = np.where(evb["prior_break"], "broken-before", "intact")
    evb["round_name"] = np.where(evb["is_round"], "round", "not-round")

    cond_rows += cond_block(evb, "(i) 터치 수(실제만)", "touch_bin", only_real=True, order=["1", "2", "3+"])
    cond_rows += cond_block(evb[evb.round_ok & (evb.market == "US")], "(ii) 라운드넘버 US(SPY/QQQ/SOX/MU)", "round_name")
    cond_rows += cond_block(evb[evb.round_ok & (evb.market == "KR")], "(ii) 라운드넘버 KR(TIGER200IT/KOSPI/KODEX_SEMI/삼성 2018-05~/하이닉스 2003~)", "round_name")
    cond_rows += cond_block(evb, "(iii) 레벨 나이(L=250)", "age_bin", order=["10-60", "61-250"])
    ev500 = all_events.get("L500_tol0.01_X0.02")
    if ev500 is not None:
        e5 = ev500.copy()
        e5["age_bin"] = pd.cut(e5["age"], [0, 60, 250, 9999], labels=["10-60", "61-250", ">250"]).astype(str)
        cond_rows += cond_block(e5, "(iii) 레벨 나이(L=500)", "age_bin", order=["10-60", "61-250", ">250"])
    cond_rows += cond_block(evb, "(iv) 변동성 레짐(20일 실현변동성 vs 확장 중앙값)", "vol_regime", order=["low", "high"])
    cond_rows += cond_block(evb, "(v) 추세 레짐(전일 종가 vs 200일 MA)", "trend", order=["above200", "below200"])
    cond_rows += cond_block(evb, "(vi) 종목", "ticker", order=tickers)
    cond_rows += cond_block(evb, "(vi-b) 시장", "market", order=["US", "KR"])
    cond_rows += cond_block(evb, "(vii) 지지 vs 저항", "dir_name", order=["support", "resistance"])
    cond_rows += cond_block(evb, "(viii) 피벗 역할(같은 역할 vs 역할전환)", "role", only_real=True, order=["same-role", "role-reversal"])
    cond_rows += cond_block(evb, "(ix) 피벗 강도(k)", "k_name", only_real=True, order=["k5-only", "k10"])
    cond_rows += cond_block(evb, "(x) 피벗 이후 레벨 돌파 여부", "pb_name", order=["intact", "broken-before"])
    # 터치 수: 추세 카이제곱
    tb = evb[evb.kind == "real"]
    tb = tb[tb.res_pct_N10 != 0]
    ct = pd.crosstab(tb["touch_bin"], tb["res_pct_N10"])
    chi2 = stats.chi2_contingency(ct)
    cond_df = pd.DataFrame(cond_rows)
    cond_df.to_csv(os.path.join(HERE, "results_conditional.csv"), index=False)

    md.append(f"\n## 5. 조건별 분할 (기본 설정, N=10, X=2%). 비교 셀 수 = {n_cells}, Bonferroni 임계 p = {0.05 / max(n_cells, 1):.4f}\n")
    rows = []
    for r in cond_df.itertuples():
        rows.append(dict(s=r.split, v=r.value, n=r.n_real,
                         real=f"{fmt_pct(r.real_rate)} [{fmt_pct(r.ci_lo)}, {fmt_pct(r.ci_hi)}]",
                         uni=fmt_pct(getattr(r, "uniform_rate", np.nan)) if hasattr(r, "uniform_rate") else "–",
                         d=(f"{100 * r.diff_uniform:+.1f}pp (p={r.p_uniform:.3f})"
                            if hasattr(r, "diff_uniform") and not np.isnan(r.diff_uniform) else "–")))
    md.append(md_table(rows, ["s", "v", "n", "real", "uni", "d"]).replace(
        "| s | v | n | real | uni | d |", "| 분할 | 값 | 실제 n | 실제 bounce율 [Wilson 95%] | 균등 플라시보 | 차이 (p) |"))
    md.append(f"\n터치 수 × 결과 카이제곱: chi2={chi2.statistic:.2f}, dof={chi2.dof}, p={chi2.pvalue:.3f}\n")

    # 종목 × 방향 상세
    md.append("\n## 6. 종목 × 방향 (기본 설정, N=10, X=2%)\n")
    rows = []
    for tk in tickers:
        for dn in ("support", "resistance"):
            d = evb[(evb.ticker == tk) & (evb.dir_name == dn)]
            a, b, v = rate_row(d[d.kind == "real"], "res_pct_N10"), rate_row(d[d.kind == "uniform"], "res_pct_N10"), rate_row(d[d.kind == "virtual"], "res_pct_N10")
            z, p, ci, h = two_prop(a["bounce"], a["bounce"] + a["brk"], b["bounce"], b["bounce"] + b["brk"])
            rows.append(dict(t=tk, d=dn, n=a["n"], real=fmt_pct(a["rate"]), uni=fmt_pct(b["rate"]), virt=fmt_pct(v["rate"]),
                             diff=f"{100 * (a['rate'] - b['rate']):+.1f}pp (p={p:.3f})",
                             r10=f"{100 * d[d.kind == 'real']['ret10'].mean():+.2f}% / {100 * d[d.kind == 'uniform']['ret10'].mean():+.2f}%"))
    md.append(md_table(rows, ["t", "d", "n", "real", "uni", "virt", "diff", "r10"]).replace(
        "| t | d | n | real | uni | virt | diff | r10 |", "| 종목 | 방향 | 실제 n | 실제 | 균등 | 가상 | 차이 vs 균등 | 10일 수익률 실제/균등 |"))

    # ------------------------------------------------------------------ 합성 널
    print(f"== 합성 널 (block bootstrap, block=10, paths={args.paths})")
    syn_rows = []
    syn_md = []
    real_pooled = {}
    for col in ("res_pct_N5", "res_pct_N10", "res_atr_N10"):
        real_pooled[col] = rate_row(ev0[ev0.kind == "real"], col)["rate"]
    syn_stats = {tk: {} for tk in tickers}
    pooled_acc = []  # (path, col) -> (bounce, brk) 누적
    for tk in tickers:
        b = bars[tk]
        tk_t0 = time.time()
        recs = []
        n_paths = args.paths if (tk in ("SOX", "SPY", "SOXL", "TIGER200IT") or args.paths_secondary is None) else args.paths_secondary
        for pth in range(n_paths):
            sb = bootstrap_bars(b, 10, rng)
            df = run_ticker(sb, BASE["L"], BASE["tol"], BASE["X"], rng, kinds=("real", "uniform"), with_attrs=False)
            rec = dict(path=pth)
            for col in ("res_pct_N5", "res_pct_N10", "res_atr_N10"):
                a = rate_row(df[df.kind == "real"], col)
                u = rate_row(df[df.kind == "uniform"], col)
                rec[f"{col}_real"] = a["rate"]
                rec[f"{col}_uni"] = u["rate"]
                rec[f"{col}_diff"] = a["rate"] - u["rate"]
                rec[f"{col}_rb"] = a["bounce"]
                rec[f"{col}_rk"] = a["brk"]
                rec[f"{col}_ub"] = u["bounce"]
                rec[f"{col}_uk"] = u["brk"]
            rec["n_real"] = int((df.kind == "real").sum())
            rec["ret10_real"] = df[df.kind == "real"]["ret10"].mean()
            recs.append(rec)
            if (pth + 1) % 50 == 0 or pth == n_paths - 1:
                print(f"  {tk}: {pth + 1}/{n_paths} paths  ({time.time() - tk_t0:.0f}s)")
        sd = pd.DataFrame(recs)
        sd["ticker"] = tk
        pooled_acc.append(sd)
        real_df = ev0[(ev0.ticker == tk) & (ev0.kind == "real")]
        uni_df = ev0[(ev0.ticker == tk) & (ev0.kind == "uniform")]
        for col in ("res_pct_N5", "res_pct_N10", "res_atr_N10"):
            rr = rate_row(real_df, col)["rate"]
            dd = rr - rate_row(uni_df, col)["rate"]
            null = sd[f"{col}_real"].dropna().to_numpy()
            nulld = sd[f"{col}_diff"].dropna().to_numpy()
            syn_rows.append(dict(ticker=tk, outcome=col, real_rate=rr, null_mean=null.mean(), null_sd=null.std(ddof=1),
                                 null_p05=np.percentile(null, 5), null_p95=np.percentile(null, 95),
                                 pct_rank=(null < rr).mean(), p_one_sided_high=(null >= rr).mean(),
                                 p_two_sided=min(1.0, 2 * min((null >= rr).mean(), (null <= rr).mean())),
                                 real_minus_uni=dd, null_diff_mean=nulld.mean(), null_diff_sd=nulld.std(ddof=1),
                                 p_diff_two_sided=min(1.0, 2 * min((nulld >= dd).mean(), (nulld <= dd).mean())),
                                 n_real_events=len(real_df), null_n_events_mean=sd["n_real"].mean(),
                                 real_ret10=real_df["ret10"].mean(), null_ret10_mean=sd["ret10_real"].mean(),
                                 null_ret10_sd=sd["ret10_real"].std(ddof=1)))
    # 풀링: 경로 p 에서 모든 종목 합산
    allsd = pd.concat(pooled_acc, ignore_index=True)
    allsd["market"] = allsd["ticker"].map(MARKET)
    for mk in ("US", "KR"):
      evm = ev0[ev0.market == mk]
      if (evm.kind == "real").sum() == 0 or not (allsd.market == mk).any():
          continue
      for col in ("res_pct_N5", "res_pct_N10", "res_atr_N10"):
        g = allsd[allsd.market == mk].groupby("path")
        null = (g[f"{col}_rb"].sum() / (g[f"{col}_rb"].sum() + g[f"{col}_rk"].sum())).to_numpy()
        nullu = (g[f"{col}_ub"].sum() / (g[f"{col}_ub"].sum() + g[f"{col}_uk"].sum())).to_numpy()
        nulld = null - nullu
        rr = rate_row(evm[evm.kind == "real"], col)["rate"]
        dd = rr - rate_row(evm[evm.kind == "uniform"], col)["rate"]
        syn_rows.append(dict(ticker=f"POOLED-{mk}", outcome=col, real_rate=rr, null_mean=null.mean(), null_sd=null.std(ddof=1),
                             null_p05=np.percentile(null, 5), null_p95=np.percentile(null, 95),
                             pct_rank=(null < rr).mean(), p_one_sided_high=(null >= rr).mean(),
                             p_two_sided=min(1.0, 2 * min((null >= rr).mean(), (null <= rr).mean())),
                             real_minus_uni=dd, null_diff_mean=nulld.mean(), null_diff_sd=nulld.std(ddof=1),
                             p_diff_two_sided=min(1.0, 2 * min((nulld >= dd).mean(), (nulld <= dd).mean())),
                             n_real_events=int((evm.kind == "real").sum()), null_n_events_mean=g["n_real"].sum().mean(),
                             real_ret10=evm[evm.kind == "real"]["ret10"].mean(),
                             null_ret10_mean=np.nan, null_ret10_sd=np.nan))
    syn = pd.DataFrame(syn_rows)
    syn.to_csv(os.path.join(HERE, "results_synthetic.csv"), index=False)
    allsd.to_csv(os.path.join(HERE, "results_synthetic_paths.csv"), index=False)

    md.append(f"\n## 7. 합성 널 (블록 부트스트랩, 블록=10, {args.paths} 경로/종목, 기본 설정)\n")
    for col, nm in (("res_pct_N10", "N=10, X=2%"), ("res_pct_N5", "N=5, X=2%"), ("res_atr_N10", "N=10, X=1·ATR")):
        md.append(f"\n### {nm}\n")
        rows = []
        for r in syn[syn.outcome == col].itertuples():
            rows.append(dict(t=r.ticker, real=fmt_pct(r.real_rate), nm=f"{fmt_pct(r.null_mean)} ± {100 * r.null_sd:.1f}pp",
                             rng_=f"[{fmt_pct(r.null_p05)}, {fmt_pct(r.null_p95)}]", pr=f"{100 * r.pct_rank:.0f}%",
                             p=f"{r.p_two_sided:.3f}", d=f"{100 * r.real_minus_uni:+.1f}pp",
                             nd=f"{100 * r.null_diff_mean:+.1f} ± {100 * r.null_diff_sd:.1f}pp", pd_=f"{r.p_diff_two_sided:.3f}",
                             ne=f"{int(r.n_real_events)} / {r.null_n_events_mean:.0f}"))
        md.append(md_table(rows, ["t", "real", "nm", "rng_", "pr", "p", "d", "nd", "pd_", "ne"]).replace(
            "| t | real | nm | rng_ | pr | p | d | nd | pd_ | ne |",
            "| 종목 | 실제 bounce율 | 널 평균±SD | 널 5–95% | 실제의 백분위 | 양측 p | 실제−플라시보(실데이터) | 널에서의 실제−플라시보 | 양측 p(차이) | 이벤트 수 실제/널평균 |"))

    # ------------------------------------------------------------------ 시장 비교 (KR vs US)
    md.append("\n## 6b. 시장 비교: 한국 vs 미국 (기본 설정). 차이의 차이 = (실제−균등)_KR − (실제−균등)_US\n")
    rows = []
    for col in ("res_pct_N5", "res_pct_N10", "res_atr_N10"):
        for dn in ("all", "support", "resistance"):
            vals = {}
            for mk in ("US", "KR"):
                d = evb[(evb.market == mk)] if dn == "all" else evb[(evb.market == mk) & (evb.dir_name == dn)]
                a, b = rate_row(d[d.kind == "real"], col), rate_row(d[d.kind == "uniform"], col)
                na, nb_ = a["bounce"] + a["brk"], b["bounce"] + b["brk"]
                diff = a["rate"] - b["rate"]
                var = (a["rate"] * (1 - a["rate"]) / max(na, 1)) + (b["rate"] * (1 - b["rate"]) / max(nb_, 1))
                vals[mk] = (a, b, diff, var)
            dd = vals["KR"][2] - vals["US"][2]
            se = np.sqrt(vals["KR"][3] + vals["US"][3])
            z = dd / se if se > 0 else np.nan
            p = 2 * (1 - stats.norm.cdf(abs(z)))
            rows.append(dict(oc=col, d=dn,
                             us=f"{fmt_pct(vals['US'][0]['rate'])} vs {fmt_pct(vals['US'][1]['rate'])} ({100 * vals['US'][2]:+.1f}pp, n={vals['US'][0]['n']})",
                             kr=f"{fmt_pct(vals['KR'][0]['rate'])} vs {fmt_pct(vals['KR'][1]['rate'])} ({100 * vals['KR'][2]:+.1f}pp, n={vals['KR'][0]['n']})",
                             dd=f"{100 * dd:+.1f}pp (z={z:.2f}, p={p:.3f})"))
    md.append(md_table(rows, ["oc", "d", "us", "kr", "dd"]).replace(
        "| oc | d | us | kr | dd |", "| 결과정의 | 방향 | US 실제 vs 균등 (차이) | KR 실제 vs 균등 (차이) | 차이의 차이 KR−US |"))

    # ------------------------------------------------------------------ 예시
    ex_rows = []
    for tk in ("SOXL", "SOX", "TIGER200IT"):
        d = evb[(evb.ticker == tk) & (evb.kind == "real") & (evb.touches >= 2) & (evb.res_pct_N10 != 0)]
        held = d[d.res_pct_N10 == 1].sort_values("touches", ascending=False).head(6)
        broke = d[d.res_pct_N10 == -1].sort_values("touches", ascending=False).head(6)
        for lab, dd in (("held", held), ("broke", broke)):
            for r in dd.itertuples():
                b = bars[tk]
                ex_rows.append(dict(ticker=tk, date=str(pd.Timestamp(r.date).date()), dir="support" if r.dir > 0 else "resistance",
                                    level=round(r.level, 2), pivot_date=str(pd.Timestamp(b["dates"][r.pivot_idx]).date()),
                                    touches=int(r.touches), prev_close=round(b["pc"][r.t], 2),
                                    low=round(b["l"][r.t], 2), high=round(b["h"][r.t], 2), close=round(b["c"][r.t], 2),
                                    outcome=lab, resolved_day=int(r.day_pct_N10), ret10=round(100 * r.ret10, 2)))
    exdf = pd.DataFrame(ex_rows)
    exdf.to_csv(os.path.join(HERE, "examples.csv"), index=False)
    md.append("\n## 8. 예시 이벤트 (SOXL/SOX/TIGER200IT, 터치 2회 이상)\n")
    md.append(md_table(exdf.to_dict("records"), list(exdf.columns)))

    # 미해결/일0 통계
    md.append("\n## 9. 부가 통계 (기본 설정, 실제 이벤트)\n")
    r0 = ev0[ev0.kind == "real"]
    rows = []
    for tk in tickers:
        d = r0[r0.ticker == tk]
        rows.append(dict(t=tk, n=len(d), d0b=fmt_pct(((d.res_pct_N10 == -1) & (d.day_pct_N10 == 0)).mean()),
                         d0n=fmt_pct(((d.res_pct_N10 == 1) & (d.day_pct_N10 == 0)).mean()),
                         unres=fmt_pct((d.res_pct_N10 == 0).mean()), dist=fmt_pct(d.dist_prev.mean(), 2),
                         touches=f"{d.touches.mean():.2f}", rnd=fmt_pct(d.is_round.mean()),
                         sup=int((d.dir > 0).sum()), res=int((d.dir < 0).sum())))
    md.append(md_table(rows, ["t", "n", "sup", "res", "d0b", "d0n", "unres", "dist", "touches", "rnd"]).replace(
        "| t | n | sup | res | d0b | d0n | unres | dist | touches | rnd |",
        "| 종목 | n | 지지 | 저항 | 당일 종가 돌파 | 당일 bounce 확정 | 10일 미해결 | 평균 레벨거리(전일종가) | 평균 터치 | 라운드 비율 |"))

    with open(os.path.join(HERE, "tables.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"== 완료 {time.time() - t0:.0f}s → tables.md, results_*.csv, events_real.csv, examples.csv")


if __name__ == "__main__":
    main()
