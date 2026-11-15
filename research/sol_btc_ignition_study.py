# -*- coding: utf-8 -*-
"""비트코인 저점 이후 '본격 상승 시작' 시점과, 비트코인 저점·솔라나(알트) 저점 사이 간격 연구.
자료: data/crypto/sol_study/ (scripts/fetch_sol_study.py), data/crypto/extra/BTC_BITSTAMP_1D.csv, data/crypto/BTC_ONCHAIN.csv
실행: python research/sol_btc_ignition_study.py → research/output/sol_btc_ignition_study.txt, research/charts/sol_btc_*.png
"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bottom_anatomy as A
SS = os.path.join(A.DC, "sol_study"); TD = pd.Timedelta; LINES = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); LINES.append(s)

F = A.unified(); c, h, l = F.close, F.high, F.low                       # BTC 2010-07~ (Coin Metrics + Bitstamp)
B1 = pd.read_csv(os.path.join(SS, "BINANCE_1D.csv.gz"), parse_dates=["date"])
def bsym(s):
    d = B1[B1.symbol == s].set_index("date").sort_index(); return d[~d.index.duplicated()]
BTC, SOL, ETH, SOLBTC = bsym("BTCUSDT"), bsym("SOLUSDT"), bsym("ETHUSDT"), bsym("SOLBTC")
CM = pd.read_csv(os.path.join(SS, "CM_PRICES.csv"), parse_dates=["date"]).set_index("date")
def first(mask):
    m = mask[mask.fillna(False)]; return m.index[0] if len(m) else None

# ───────────────────────── 1. 비트코인: 저점에서 본격 상승까지 ─────────────────────────
def btc_ignition():
    ma200 = c.rolling(200).mean(); ma50 = c.rolling(50).mean(); w = c.resample("W-SUN").last()
    ma50w = w.rolling(50).mean().reindex(c.index, method="ffill"); ma20w = w.rolling(20).mean().reindex(c.index, method="ffill"); hi150 = c.shift(1).rolling(150).max()
    bbw = (4 * c.rolling(20).std()) / c.rolling(20).mean(); above = c > ma200; run = above.astype(int).groupby((~above).cumsum()).cumsum()
    LOWS = {"2011": "2011-11-18", "2015": "2015-01-14", "2018": "2018-12-15", "2020": "2020-03-13", "2022": "2022-11-21", "2026-07(후보)": "2026-07-01"}
    P("== 1. 비트코인 사이클 저점에서 '본격 상승'까지 걸린 시간 (종가 기준, 괄호 안은 그날 종가의 저점 대비 수익)")
    rows = []
    for k, v in LOWS.items():
        d0 = l[pd.Timestamp(v) - TD(days=4):pd.Timestamp(v) + TD(days=4)].idxmin(); p0 = l[d0]; seg = c[d0:d0 + TD(days=1100)]
        fmt = lambda d: f"{(d - d0).days}일({d.date()}, {c[d] / p0 - 1:+.0%})" if d is not None else "없음"
        up50 = first(seg >= p0 * 1.5); up100 = first(seg >= p0 * 2)
        in30 = seg[seg <= p0 * 1.30]; in50 = seg[seg <= p0 * 1.50]
        r200 = first((seg > ma200[seg.index]) & (seg.index > d0 + TD(days=5))); s200 = first(run[seg.index] >= 30); s200 = s200 - TD(days=29) if s200 is not None else None
        r50w = first((seg > ma50w[seg.index]) & (seg.index > d0 + TD(days=5))); r20w = first((seg > ma20w[seg.index]) & (seg.index > d0 + TD(days=5)))
        gc = first(((ma50 > ma200) & (ma50.shift(1) <= ma200.shift(1)))[seg.index]); bo = first((seg > hi150[seg.index]) & (seg.index > d0 + TD(days=20)))
        ath = first(seg > F.ath.shift(1)[seg.index]) if "후보" not in k else None
        # 본격 상승 시작점: 그 뒤로 1년 동안 종가가 한 번도 그 아래로 내려가지 않은 '마지막 눌림 저점' (저점 후 30일 이후, 저점 +15% 이상에서)
        ign = None
        for t in seg.index[30:]:
            if t + TD(days=200) > c.index[-1]: break
            fut = c[t + TD(days=1):t + TD(days=365)]
            if c[t] <= c[t - TD(days=10):t + TD(days=10)].min() * 1.0001 and fut.min() > c[t] and fut.max() >= c[t] * 1.8 and (fut.idxmax() - t).days <= 365:
                ign = t; break
        P(f"\n[{k}] 저점 {d0.date()} ${p0:,.0f}")
        P(f"  +50% {fmt(up50)} | +100% {fmt(up100)} | 사상 최고가 경신 {fmt(ath)}")
        P(f"  저점 +30% 이내 종가가 마지막으로 나온 날: " + (f"{(in30.index[-1] - d0).days}일째 ({in30.index[-1].date()})" if len(in30) else "없음(즉시 이탈)") + " | +50% 이내 마지막: " + (f"{(in50.index[-1] - d0).days}일째 ({in50.index[-1].date()})" if len(in50) else "없음"))
        P(f"  200일선 첫 회복 {fmt(r200)} | 30일 이상 유지된 회복 {fmt(s200)} | 20주선 {fmt(r20w)} | 50주선 {fmt(r50w)} | 골든크로스 {fmt(gc)}")
        if bo is not None:
            f = lambda n: c.asof(bo + TD(days=n)) / c[bo] - 1 if bo + TD(days=n) <= c.index[-1] else np.nan
            P(f"  150일 종가 신고가 첫 돌파 {fmt(bo)} | 돌파 전 60일 볼린저 폭 최저 {bbw[bo - TD(days=60):bo - TD(days=1)].min():.2f} | 돌파 뒤 90일 {f(90):+.0%}, 180일 {f(180):+.0%}, 1년 {f(365):+.0%} | 돌파가 대비 이후 1년 최저 {l[bo:bo + TD(days=365)].min() / c[bo] - 1:+.0%}")
            mid = l[d0 + TD(days=30):bo]
            if len(mid): P(f"  저점 30일 뒤~돌파 사이 가장 깊은 눌림: {mid.idxmin().date()} ${mid.min():,.0f} (저점 대비 {mid.min() / p0 - 1:+.0%}, {(mid.idxmin() - d0).days}일째)")
        if ign is not None:
            fut = c[ign:ign + TD(days=365)]; P(f"  ★ 마지막 눌림 저점(이후 1년간 종가 미이탈·+80% 이상 상승): {fmt(ign)} → 1년 내 최고 {fut.max() / c[ign] - 1:+.0%} | 그날 200일선 대비 {c[ign] / ma200[ign] - 1:+.0%}, 직전 30일 볼린저 폭 최저 {bbw[ign - TD(days=30):ign].min():.2f}")
        z = F.z[d0 + TD(days=20):d0 + TD(days=450)]; ups = z[z >= 3.5]
        P("  +3.5σ 이상 양봉(저점 20일 뒤부터): " + (", ".join(f"{d.date()} {F.ret[d]:+.0%} ({(d - d0).days}일, 200일선 {'위' if c[d] > ma200[d] else '아래'})" for d in ups.index[:6]) if len(ups) else "없음"))
        rows.append(dict(k=k, d0=d0, p0=p0, bo=bo, ign=ign, r200=r200, s200=s200, r50w=r50w))
    return rows

# ───────────────────────── 2. 알트 바스켓: 사이클 저점의 시차 ─────────────────────────
def alt_lags():
    P("\n== 2. 주요 알트의 사이클 저점은 비트코인보다 며칠 늦었나/빨랐나 (Coin Metrics 일별 종가, 구간 내 최저 종가일 기준)")
    CYC = {"2015": ("2014-06-01", "2016-06-30"), "2018": ("2018-01-01", "2019-12-31"), "2020-03": ("2020-02-15", "2020-06-30"), "2022": ("2021-11-01", "2023-12-31"), "2026(진행)": ("2025-10-01", str(CM.index[-1].date()))}
    for k, (a, b) in CYC.items():
        w = CM.loc[a:b]; bd = w.btc.idxmin(); P(f"\n[{k}] 비트코인 최저 종가 {bd.date()} ${w.btc.min():,.0f}")
        lags = []; extra = []
        for s in [x for x in CM.columns if x != "btc"]:
            x = w[s].dropna()
            if len(x) < 0.8 * len(w): continue
            ad = x.idxmin(); lag = (ad - bd).days; ex = x.min() / x.asof(bd) - 1 if lag > 0 else 0.0
            r = (x / w.btc.reindex(x.index)).dropna(); rd = r[bd:].idxmin(); rdep = r[bd:].min() / r.asof(bd) - 1
            lags.append(lag); extra.append(ex)
            P(f"   {s.upper():5s} 최저 종가 {ad.date()} (비트코인 대비 {lag:+4d}일) | 비트코인 저점일 이후 추가 하락 {ex:+5.0%} | 비트코인 대비 가격비 최저 {rd.date()} (+{(rd - bd).days}일, {rdep:+.0%})")
        lags = np.array(lags); P(f"   → 알트 {len(lags)}종: 시차 중앙값 {np.median(lags):+.0f}일, 같은 주(±7일) {np.mean(np.abs(lags) <= 7):.0%}, 30일 넘게 늦음 {np.mean(lags > 30):.0%}, 30일 넘게 빠름 {np.mean(lags < -30):.0%} | 늦은 경우 추가 하락 중앙값 {np.median([e for e in extra if e < 0]) if any(e < 0 for e in extra) else 0:+.0%}")

# ───────────────────────── 3. 솔라나 주요 저점과 비트코인 주요 저점 짝짓기 ─────────────────────────
def swing_lows(d, win=30, dd=0.25):
    out = []
    for t in d.index[90:-3]:
        if d.low[t] > d.low[t - TD(days=win):t + TD(days=win)].min(): continue
        if d.low[t] / d.high[t - TD(days=90):t].max() - 1 > -dd: continue
        if out and (t - out[-1]).days < 10: continue
        out.append(t)
    return out
def sol_pairs():
    bl = swing_lows(BTC, 30, 0.20); sl = swing_lows(SOL, 30, 0.30)
    P("\n== 3. 솔라나의 주요 저점과 가장 가까운 비트코인 주요 저점 (Binance 일봉 저가, 2020-08~). 시차 = 솔라나 저점일 − 비트코인 저점일")
    rows = []
    for t in sl:
        nb = min(bl, key=lambda x: abs((x - t).days)); lag = (t - nb).days
        hi = SOL.high[t - TD(days=90):t].max(); bhi = BTC.high[nb - TD(days=90):nb].max()
        rows.append(lag)
        P(f"   SOL {t.date()} ${SOL.low[t]:>7.2f} (90일 고점 대비 {SOL.low[t] / hi - 1:+.0%}) ↔ BTC {nb.date()} ${BTC.low[nb]:>8,.0f} ({BTC.low[nb] / bhi - 1:+.0%}) | 시차 {lag:+4d}일 | SOL/BTC 낙폭 배율 {(SOL.low[t] / hi - 1) / (BTC.low[nb] / bhi - 1):.1f}배")
    rows = np.array(rows); P(f"   → {len(rows)}쌍: 같은 날 {int((rows == 0).sum())}, ±3일 {int((np.abs(rows) <= 3).sum())}, 4~45일 늦음 {int(((rows > 3) & (rows <= 45)).sum())}, 그 이상 늦음 {int((rows > 45).sum())}, 4일 이상 빠름 {int((rows < -3).sum())}")
    return bl, sl

# ───────────────────────── 4. 비트코인 저점 뒤 솔라나의 경로 ─────────────────────────
def sol_after_btc(bl):
    P("\n== 4. 비트코인 주요 저점 뒤 120일 동안 솔라나가 간 길 (Binance 일봉)")
    P("   BTC 저점일 | 그날 SOL 저가 | 이후 120일 SOL 최저(시차, 그날 저가 대비) | SOL/BTC 비율 최저(시차, 깊이) | SOL−BTC 초과수익 2주 / 4주 / 8주 / 12주 (종가)")
    ex = {n: [] for n in (14, 28, 56, 84)}; lagl = []; depl = []; rl = []
    for d in bl:
        if d not in SOL.index or d + TD(days=30) > SOL.index[-1]: continue
        s0 = SOL.low[d]; w = SOL.low[d:d + TD(days=120)]; sd = w.idxmin(); dep = w.min() / s0 - 1
        r = (SOL.close / BTC.close).dropna(); rw = r[d:d + TD(days=120)]; rd = rw.idxmin(); rdep = rw.min() / r[d] - 1
        xs = []
        for n in (14, 28, 56, 84):
            t = d + TD(days=n)
            if t <= SOL.index[-1]:
                v = (SOL.close.asof(t) / SOL.close[d]) - (BTC.close.asof(t) / BTC.close[d]); ex[n].append(v); xs.append(f"{v:+.0%}")
            else: xs.append("  - ")
        lagl.append((sd - d).days); depl.append(dep); rl.append((rd - d).days)
        P(f"   {d.date()} | ${s0:>7.2f} | {sd.date()} (+{(sd - d).days:3d}일, {dep:+4.0%}) | {rd.date()} (+{(rd - d).days:3d}일, {rdep:+4.0%}) | " + " / ".join(xs))
    lagl = np.array(lagl); depl = np.array(depl)
    P(f"   → n={len(lagl)}: SOL 최저가 BTC 저점일과 같은 날 {int((lagl == 0).sum())}, 1~7일 뒤 {int(((lagl > 0) & (lagl <= 7)).sum())}, 8~45일 뒤 {int(((lagl > 7) & (lagl <= 45)).sum())}, 46일 이상 뒤 {int((lagl > 45).sum())} | 추가 하락 중앙값 {np.median(depl):+.0%}, 하위 사분위 {np.quantile(depl, .25):+.0%}")
    P("   → SOL−BTC 초과수익 중앙값: " + ", ".join(f"{n // 7}주 {np.median(v):+.0%} (플러스 {np.mean(np.array(v) > 0):.0%})" for n, v in ex.items()))

# ───────────────────────── 5. 30분봉: 같은 날 누가 먼저 저점을 찍었나 ─────────────────────────
def intraday():
    def ld(s):
        d = pd.read_csv(os.path.join(SS, f"BINANCE_30M_{s}.csv.gz")); d["date"] = pd.to_datetime(d["date"], format="mixed"); return d.set_index("date").sort_index()
    b, s, e = ld("BTCUSDT"), ld("SOLUSDT"), ld("ETHUSDT")
    EV = ["2021-05-19", "2021-06-22", "2021-07-20", "2022-01-24", "2022-05-12", "2022-06-18", "2022-11-09", "2022-11-21", "2023-03-10", "2023-06-15", "2024-08-05", "2025-04-07", "2025-11-21", "2026-02-06", "2026-06-05", "2026-07-01", "2026-11-14"]
    P("\n== 5. 30분봉으로 본 저점 시각 (Binance, UTC). 비트코인 저점 ±36시간 안에서 각 자산의 최저 30분봉")
    P("   BTC 저점 시각 | BTC 72h 낙폭·그 봉 거래량 배수·2h 뒤 반등 | SOL 저점 시각(BTC 대비 시차) 72h 낙폭·2h 뒤 반등 | ETH 시차 | BTC 저점 시각의 SOL 가격 대비 SOL 최저")
    lags = []
    for v in EV:
        t0 = pd.Timestamp(v); wb = b.low[t0 - TD(days=1):t0 + TD(days=2)]
        if not len(wb): continue
        tb = wb.idxmin(); win = lambda x: x.low[tb - TD(hours=36):tb + TD(hours=36)]
        ws = win(s); we = win(e)
        if not len(ws): continue
        ts_, te = ws.idxmin(), we.idxmin()
        dd = lambda x, t: x.low[t] / x.high[t - TD(hours=72):t].max() - 1; rb = lambda x, t: x.close.asof(t + TD(hours=2)) / x.low[t] - 1
        vm = b.volume[tb - TD(days=30):tb - TD(days=2)].median(); lag = (ts_ - tb).total_seconds() / 3600; lags.append(lag)
        P(f"   {tb:%Y-%m-%d %H:%M} | {dd(b, tb):+4.0%} · {b.volume[tb] / vm:4.0f}배 · {rb(b, tb):+5.1%} | {ts_:%m-%d %H:%M} ({lag:+5.1f}h) {dd(s, ts_):+4.0%} · {rb(s, ts_):+5.1%} | {(te - tb).total_seconds() / 3600:+5.1f}h | {s.low[ts_] / s.close.asof(tb) - 1:+5.1%}")
    lags = np.array(lags); P(f"   → n={len(lags)}: SOL 저점이 BTC와 같은 30분봉 {int((lags == 0).sum())}, ±2시간 이내 {int((np.abs(lags) <= 2).sum())}, SOL이 2시간 넘게 늦음 {int((lags > 2).sum())}, 2시간 넘게 빠름 {int((lags < -2).sum())}")
    # 2015 Bitstamp 30분봉
    bs = pd.read_csv(os.path.join(SS, "BITSTAMP_30M_2015.csv"), parse_dates=["date"]).set_index("date").sort_index()
    for a, z in (("2015-01-12", "2015-01-17"), ("2015-08-22", "2015-08-27")):
        w = bs.loc[a:z]; t = w.low.idxmin(); vm = bs.volume[t - TD(days=20):t - TD(days=2)].median()
        P(f"   (Bitstamp 2015) {t:%Y-%m-%d %H:%M} ${w.low.min():,.0f} | 72h 낙폭 {w.low.min() / bs.high[t - TD(hours=72):t].max() - 1:+.0%} · 그 봉 거래량 {bs.volume[t] / vm:.0f}배 · 2h 뒤 {bs.close.asof(t + TD(hours=2)) / w.low.min() - 1:+.1%}")

# ───────────────────────── 6. 솔라나 자체의 저점 서명과 상승 시작 ─────────────────────────
def sol_own(sl):
    S_ = A.feats(SOL[["open", "high", "low", "close", "volume"]]); sc = S_.close; ma200 = sc.rolling(200).mean(); hi150 = sc.shift(1).rolling(150).max()
    r = (SOL.close / BTC.close).dropna(); rm20 = r / r.shift(20) - 1; rma100 = r.rolling(100).mean()
    P("\n== 6. 솔라나 자체: 5σ 음봉, 저점 뒤 회복 순서, SOL/BTC 비율")
    P("   (가) 솔라나의 5σ 음봉(종가 수익 ÷ 직전 60일 변동성 ≤ -5) 전부와 이후")
    for d in S_.index[S_.z <= -5]:
        fut = S_.low[d + TD(days=1):d + TD(days=365)]
        if not len(fut): continue
        more = min(fut.min() / sc[d] - 1, 0); bz = F.z.get(d, np.nan)
        P(f"      {d.date()} ${sc[d]:>7.2f} {S_.ret[d]:+.0%} ({S_.z[d]:.1f}σ, 거래량 {S_.vr[d]:.1f}배) 고점 대비 {S_.dd[d]:+.0%} | 같은 날 BTC {F.ret.get(d, np.nan):+.0%} ({bz:.1f}σ) | 추가 하락 {more:+.0%} ({(fut.idxmin() - d).days if fut.min() < sc[d] else 0}일 뒤)")
    P("   (나) 솔라나 주요 저점 뒤 회복 순서 (저점 대비 일수)")
    for t in sl:
        p0 = SOL.low[t]; seg = sc[t:t + TD(days=700)]
        if len(seg) < 40: continue
        fmt = lambda d: f"{(d - t).days}일({sc[d] / p0 - 1:+.0%})" if d is not None else "없음"
        up50 = first(seg >= p0 * 1.5); up100 = first(seg >= p0 * 2); r200 = first((seg > ma200[seg.index]) & (seg.index > t + TD(days=3))); bo = first((seg > hi150[seg.index]) & (seg.index > t + TD(days=20)))
        rpos = first((rm20[seg.index] > 0) & (seg.index > t + TD(days=3))); broke = seg[seg.index > t + TD(days=1)]; brk = first(SOL.low[broke.index] < p0)
        P(f"      {t.date()} ${p0:.2f}: +50% {fmt(up50)} | +100% {fmt(up100)} | 200일선 {fmt(r200)} | 150일 신고가 {fmt(bo)} | SOL/BTC 20일 모멘텀 플러스 전환 {fmt(rpos)} | 저점 이탈 " + (f"{(brk - t).days}일 뒤" if brk is not None else "없음"))
    P("   (다) SOL/BTC 비율의 주요 저점과 솔라나 달러 저점의 관계")
    rl = []
    for t in r.index[120:-3]:
        if r[t] > r[t - TD(days=45):t + TD(days=45)].min(): continue
        if r[t] / r[t - TD(days=120):t].max() - 1 > -0.25: continue
        if rl and (t - rl[-1]).days < 20: continue
        rl.append(t)
    for t in rl:
        ns = min(sl, key=lambda x: abs((x - t).days)); f = lambda n: r.asof(t + TD(days=n)) / r[t] - 1 if t + TD(days=n) <= r.index[-1] else np.nan
        P(f"      비율 저점 {t.date()} ({r[t] * 1e3:.3f}×10⁻³, 120일 고점 대비 {r[t] / r[t - TD(days=120):t].max() - 1:+.0%}) ↔ SOL 달러 저점 {ns.date()} ({(t - ns).days:+d}일) | 이후 비율 30일 {f(30):+.0%}, 90일 {f(90):+.0%}")
    fu = pd.read_csv(os.path.join(SS, "FUNDING_SOLUSDT.csv"), parse_dates=["date"]).set_index("date").rate.resample("D").sum(); f7 = fu.rolling(7).sum() * 1e4
    P("   (라) 솔라나 주요 저점일의 7일 펀딩 합(bp): " + ", ".join(f"{t.date()} {f7.asof(t):+.0f}" for t in sl if t >= f7.dropna().index[0] and t <= f7.index[-1]) + f" | 최근({f7.index[-1].date()}) {f7.iloc[-1]:+.0f}")
    return S_, r

# ───────────────────────── 7. 현재 ─────────────────────────
def now(S_, r):
    sc = S_.close; x = S_.iloc[-1]; d = S_.index[-1]
    P(f"\n== 7. 현재 ({d.date()} 종가 기준, Binance)")
    P(f"   SOL ${x.close:.2f} | 당일 {x.ret:+.1%} ({x.z:+.1f}σ) | 일간 RSI {x.rsi:.0f} | 사상 최고가 대비 {x.dd:+.0%} | 200일선 대비 {x.close / sc.rolling(200).mean().iloc[-1] - 1:+.0%} | 60일 변동성 {x.sd60:.2%}/일 → 5σ 음봉 기준 {-5 * x.sd60:+.1%}")
    lo26 = SOL.low["2026"]; P(f"   2026년 SOL 저가: 최저 ${lo26.min():.2f} ({lo26.idxmin().date()}), 2월 최저 ${SOL.low['2026-02'].min():.2f} ({SOL.low['2026-02'].idxmin().date()}), 6월 ${SOL.low['2026-06'].min():.2f} ({SOL.low['2026-06'].idxmin().date()}), 7~8월 ${SOL.low['2026-07':'2026-08'].min():.2f} ({SOL.low['2026-07':'2026-08'].idxmin().date()}), 11월 ${SOL.low['2026-11'].min():.2f} ({SOL.low['2026-11'].idxmin().date()}) | 현재가는 2026년 최저 대비 {x.close / lo26.min() - 1:+.0%}")
    P(f"   SOL/BTC 비율 {r.iloc[-1] * 1e3:.3f}×10⁻³ | 2026년 최저 {r['2026'].min() * 1e3:.3f} ({r['2026'].idxmin().date()}), 2022-12-29 {r.asof(pd.Timestamp('2022-12-29')) * 1e3:.3f}, 2023년 최저 {r['2023'].min() * 1e3:.3f} ({r['2023'].idxmin().date()}), 역대 최고 {r.max() * 1e3:.3f} ({r.idxmax().date()}) | 20일 모멘텀 {r.iloc[-1] / r.iloc[-21] - 1:+.1%}")
    b = BTC.close; P(f"   BTC ${b.iloc[-1]:,.0f}: 2026-07-01 저가 대비 {b.iloc[-1] / BTC.low['2026-07-01'] - 1:+.0%} | SOL은 그날 저가(${SOL.low['2026-07-01']:.2f}) 대비 {x.close / SOL.low['2026-07-01'] - 1:+.0%}")

# ───────────────────────── 8. 솔라나 저점일에 비트코인도 저점이었나 / 저점 전후 일봉 ─────────────────────────
def sol_on_btc_days(sl):
    P("\n== 8. 솔라나의 주요 저점일은 비트코인에도 '국지 저점'이었나 (BTC 저가가 ±15일 최저의 1% 이내인 날이 SOL 저점 ±3일 안에 있는가)")
    n = 0
    for t in sl:
        w = BTC.low[t - TD(days=3):t + TD(days=3)]; loc = BTC.low[t - TD(days=15):t + TD(days=15)].min(); ok = w.min() <= loc * 1.01; n += ok
        P(f"   SOL {t.date()} ${SOL.low[t]:.2f} | BTC ±3일 최저 {w.idxmin().date()} ${w.min():,.0f} → {'비트코인도 ±15일 저점' if ok else '비트코인은 저점 아님 (±15일 최저 ' + str(BTC.low[t - TD(days=15):t + TD(days=15)].idxmin().date()) + ')'}")
    P(f"   → {n}/{len(sl)}")
    S_ = A.feats(SOL[["open", "high", "low", "close", "volume"]]); r = (SOL.close / BTC.close)
    for nm, a, b in (("2022-12 (사이클 저점)", "2022-12-14", "2023-01-06"), ("2026-06 (올해 최저)", "2026-05-28", "2026-06-12"), ("2026-11 (지금)", "2026-11-03", str(SOL.index[-1].date()))):
        P(f"   [{nm}] 날짜 | SOL 저가·종가 | 수익(σ) | 거래량 배수 | RSI | 같은 날 BTC 수익 | SOL/BTC 비율(×10⁻³)")
        for d in S_.loc[a:b].index:
            x = S_.loc[d]; P(f"      {d.date()} | {x.low:7.2f} {x.close:7.2f} | {x.ret:+6.1%} ({x.z:+5.1f}σ) | {x.vr:4.1f}배 | {x.rsi:3.0f} | {BTC.close.pct_change().get(d, np.nan):+6.1%} | {r.get(d, np.nan) * 1e3:.3f}")

# ───────────────────────── 9. 비트코인 '점화일' 뒤 알트의 성과 ─────────────────────────
def after_ignition():
    P("\n== 9. 비트코인 점화일(저점 뒤 200일선 위에서 나온 첫 +3.5σ 양봉 또는 200일선 회복일) 뒤 알트의 성과 (Coin Metrics 종가)")
    IG = {"2015-11-02": "2015 본상승 시작", "2019-04-02": "2019 +18% 돌파", "2020-04-29": "2020 200일선 회복", "2023-01-13": "2023 200일선 회복", "2023-10-23": "2023 2차 돌파", "2026-08-19": "2026 200일선 회복(이후 실패)"}
    for v, nm in IG.items():
        d = pd.Timestamp(v); out = []
        for n in (30, 90, 180):
            t = d + TD(days=n)
            if t > CM.index[-1]: out.append(f"{n}일: -"); continue
            br = CM.btc.asof(t) / CM.btc.asof(d) - 1; al = []
            for s_ in [x for x in CM.columns if x != "btc"]:
                if pd.notna(CM[s_].asof(d)) and CM[s_].first_valid_index() < d - TD(days=200): al.append(CM[s_].asof(t) / CM[s_].asof(d) - 1)
            sol = CM.sol.asof(t) / CM.sol.asof(d) - 1 if pd.notna(CM.sol.asof(d)) else np.nan; eth = CM.eth.asof(t) / CM.eth.asof(d) - 1 if pd.notna(CM.eth.asof(d)) else np.nan
            out.append(f"{n}일: BTC {br:+.0%}, 알트 중앙값 {np.median(al):+.0%} (BTC보다 나은 비율 {np.mean(np.array(al) > br):.0%}), ETH {eth:+.0%}, SOL {sol:+.0%}")
        P(f"   {v} {nm} | " + " | ".join(out))

# ───────────────────────── 10. 차트 ─────────────────────────
def chart():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    INK, MUTED, GRID, SURF, C1, C2 = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb", "#2a78d6", "#eb6834"
    plt.rcParams.update({"font.family": ["Inter", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": "#c3c2b7", "xtick.color": MUTED, "ytick.color": MUTED})
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2), facecolor=SURF)
    for ax, (ttl, d0, a, b, marks) in zip(axes, [("2022-23: SOL bottomed 38 days after BTC, at BTC's last pullback low", "2022-11-21", "2022-10-01", "2023-12-31", [("SOL low Dec 29", "2022-12-29"), ("SOL retest Jun 10", "2023-06-10"), ("SOL last pullback Sep 11", "2023-09-11")]),
                                                 ("2026: SOL bottomed 25 days before BTC (so far)", "2026-07-01", "2026-01-01", str(SOL.index[-1].date()), [("SOL low Jun 6", "2026-06-06"), ("SOL higher low Aug 1", "2026-08-01")])]):
        d0 = pd.Timestamp(d0); bb = BTC.close[a:b] / BTC.close[d0] * 100; ss = SOL.close[a:b] / SOL.close[d0] * 100
        ax.set_facecolor(SURF); ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True); ax.set_yscale("log")
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
        ax.plot(bb.index, bb.values, color=C1, lw=2); ax.plot(ss.index, ss.values, color=C2, lw=2); ax.axvline(d0, color=MUTED, lw=0.8, ls=(0, (3, 3)))
        ax.text(d0, ax.get_ylim()[1] if False else max(bb.max(), ss.max()) * 1.02, " BTC low", fontsize=8.5, color="#52514e", va="bottom")
        for lab, md in marks:
            md = pd.Timestamp(md)
            if md in ss.index: ax.plot(md, ss[md], "o", ms=7, color=C2, mec=SURF, mew=1.5); ax.annotate(lab, (md, ss[md]), xytext=(0, -14), textcoords="offset points", ha="center", fontsize=8.5, color=INK)
        ax.text(bb.index[-1], bb.iloc[-1], "  BTC", color=INK, fontsize=9.5, va="center", fontweight="bold"); ax.text(ss.index[-1], ss.iloc[-1], "  SOL", color=INK, fontsize=9.5, va="center", fontweight="bold")
        ax.set_title(ttl, loc="left", fontsize=10.5, color=INK, fontweight="bold"); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}")); ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_ylabel("close, indexed to 100 on the BTC low date (log scale)", fontsize=8, color=MUTED); ax.margins(x=0.08)
        ax.legend(handles=[plt.Line2D([], [], color=C1, lw=2, label="Bitcoin"), plt.Line2D([], [], color=C2, lw=2, label="Solana")], loc="upper left", frameon=False, fontsize=9)
    fig.suptitle("Bitcoin and Solana around the Bitcoin cycle low", x=0.01, ha="left", fontsize=13, color=INK, fontweight="bold")
    p = os.path.join(HERE, "charts", "sol_btc_around_low.png"); fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(p, dpi=150, facecolor=SURF); plt.close(fig); P(f"\n차트 저장: research/charts/sol_btc_around_low.png")

if __name__ == "__main__":
    btc_ignition(); alt_lags(); bl, sl = sol_pairs(); sol_after_btc(bl); intraday(); S_, r = sol_own(sl); sol_on_btc_days(sl); after_ignition(); now(S_, r)
    if '--no-chart' not in sys.argv: chart()
    os.makedirs(os.path.join(HERE, "output"), exist_ok=True); open(os.path.join(HERE, "output", "sol_btc_ignition_study.txt"), "w").write("\n".join(LINES) + "\n")
