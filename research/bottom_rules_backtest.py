# -*- coding: utf-8 -*-
"""외부 조사에서 나온 저점 탐지 후보 규칙을 보유 자료로 검증한다 (reports/비트코인 저점 탐지 이론 조사.md 의 후보 규칙).
모든 신호는 그날까지의 정보만 쓴다. 성과 = 신호일 종가 대비 이후 1년 최저 저가(추가 하락)와 90일·1년 뒤 수익.
기준선 = 약세 구간(종가가 사상 최고가 대비 -45% 이하)의 모든 날.
실행: python research/bottom_rules_backtest.py → research/output/bottom_rules_backtest.txt
"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bottom_anatomy as A
DC = A.DC; EX = A.EX; EX2 = os.path.join(DC, "extra2"); TD = pd.Timedelta; LINES = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); LINES.append(s)
def rd(path, **kw):
    return pd.read_csv(path, **kw) if os.path.exists(path) else None

F = A.unified()                       # 2010-07~ (Coin Metrics 종가 + Bitstamp 일봉)
Y = A.feats(A.load_daily(os.path.join(DC, "BTCUSD.csv")))   # Yahoo 2014-09~ (거래량 기준)
c, h, l = F.close, F.high, F.low
CYCLE_LOWS = {"2011": "2011-11-18", "2015": "2015-01-14", "2018": "2018-12-15", "2020": "2020-03-13", "2022": "2022-11-21", "2026-02": "2026-02-06", "2026-07": "2026-07-01"}
CL = {k: l[pd.Timestamp(v) - TD(days=3):pd.Timestamp(v) + TD(days=3)].idxmin() for k, v in CYCLE_LOWS.items()}

def outcome(d):
    fut = l[d + TD(days=1):d + TD(days=365)]
    more = min(fut.min() / c[d] - 1, 0) if len(fut) else np.nan
    f = lambda n: c.asof(d + TD(days=n)) / c[d] - 1 if d + TD(days=n) <= c.index[-1] else np.nan
    return more, f(90), f(365)
def first_days(mask, gap=30):
    out = []; last = None
    for d in mask[mask.fillna(False)].index:
        if last is None or (d - last).days > gap: out.append(d)
        last = d
    return out
def near(d):
    """가장 가까운 사이클 저점과의 거리(일, 가격)."""
    k = min(CL, key=lambda k: abs((CL[k] - d).days)); return k, (d - CL[k]).days, c[d] / l[CL[k]] - 1
BASE = np.array([outcome(d)[0] for d in c[F.zone].index if d + TD(days=300) <= c.index[-1]])
def report(title, days, note=""):
    P(f"\n### {title}" + (f"  ({note})" if note else ""))
    res = []
    for d in days:
        if d not in c.index: d = c.index[c.index.get_indexer([d], method="nearest")[0]]
        m, f90, f365 = outcome(d); k, dd, pp = near(d); res.append(m)
        P(f"   {d.date()} ${c[d]:>9,.0f} 고점대비 {F.dd[d]:+.0%} | 추가 하락 {m:+5.0%} | 90일 {f90:+5.0%} 1년 {f365:+5.0%} | 가장 가까운 사이클 저점 {k}: {dd:+d}일, 저점 대비 {pp:+.0%}")
    res = np.array([r for r in res if r == r])
    if len(res): P(f"   → n={len(res)} 추가 하락 중앙값 {np.median(res):+.0%}, -10% 이내 {np.mean(res >= -0.10):.0%}, 최악 {res.min():+.0%}  | 기준선 중앙값 {np.median(BASE):+.0%}, -10% 이내 {np.mean(BASE >= -0.10):.0%}")

P("== 외부 조사 후보 규칙 백테스트 (자료 끝:", c.index[-1].date(), ")")

# ── 규칙 1. 50주선 회복·실패 시계 ──
w = F.close.resample("W-SUN").last(); ma50 = w.rolling(50).mean(); wath = F.high.resample("W-SUN").max().cummax(); wzone = (w / wath - 1).rolling(52).min() <= -0.45
above = w > ma50; cross_up = above & ~above.shift(1, fill_value=False)
below_run = (~above).astype(int).groupby(above.cumsum()).cumsum()
first_reclaim = cross_up & (below_run.shift(1) >= 20) & wzone          # 20주 이상 아래 있다가 처음 회복
P("\n### 규칙 1. 약세 구간에서 50주선을 20주 이상 하회한 뒤 주봉 종가로 처음 회복")
for d in first_reclaim[first_reclaim].index:
    seg = w[d:d + TD(weeks=60)]; ab = (seg > ma50[seg.index]); lost = ab[~ab]
    lost_d = lost.index[0] if len(lost) else None
    rec4 = None
    if lost_d is not None:
        nxt = (w[lost_d:lost_d + TD(weeks=4)] > ma50[lost_d:lost_d + TD(weeks=4)]); rec4 = bool(nxt.any())
    prev_low = l[d - TD(days=400):d].min(); fut_low = l[d:d + TD(days=540)].min()
    P(f"   회복 {d.date()} ${w[d]:,.0f} | 다시 이탈 {'없음(60주 내)' if lost_d is None else str(lost_d.date()) + (' → 4주 안에 재회복' if rec4 else ' → 4주 안에 재회복 실패')} | 회복 전 400일 최저 ${prev_low:,.0f}, 회복 후 540일 최저 ${fut_low:,.0f} → {'저점 지켜짐' if fut_low >= prev_low else '신저가 ' + format(fut_low / prev_low - 1, '+.0%')}")

# ── 규칙 2. 30일 평균 펀딩 음수 체제 ──
fu = rd(os.path.join(EX, "FUNDING_BINANCE.csv"), parse_dates=["date"])
if fu is not None:
    fd = fu.set_index("date").rate.resample("D").sum(); f30 = fd.rolling(30).mean(); neg = f30 < 0
    P("\n### 규칙 2. Binance 30일 평균 펀딩비 음수 체제 (2020-01~). 체제별 시작·끝·일수와 그 안의 최저가")
    grp = (neg != neg.shift()).cumsum()
    for _, g in neg.groupby(grp):
        if not g.iloc[0] or len(g) < 5: continue
        a, b = g.index[0], g.index[-1]; lo = l[a:b].min(); lod = l[a:b].idxmin(); m, f90, f365 = outcome(c.index[c.index.get_indexer([a], method="nearest")[0]])
        fut = l[b:b + TD(days=365)].min()
        P(f"   {a.date()} ~ {b.date()} ({len(g)}일) | 시작일 종가 ${c.asof(a):,.0f}, 체제 내 최저 ${lo:,.0f} ({lod.date()}) | 시작일 매수: 추가 하락 {m:+.0%}, 90일 {f90:+.0%}, 1년 {f365:+.0%} | 체제 종료 뒤 1년 안에 체제 내 최저가가 {'깨짐 ' + format(fut / lo - 1, '+.0%') if fut < lo else '지켜짐'}")
    P(f"   현재 30일 평균 펀딩(일 합계): {f30.iloc[-1] * 1e4:+.2f}bp ({f30.index[-1].date()}), 최근 7일 합 {fd.iloc[-7:].sum() * 1e4:+.1f}bp")

# ── 규칙 4. 주간 RSI 30 미만 ──
wr = A.rsi(w); first = first_days((wr < 30).reindex(c.index, method="ffill") & (c.index.dayofweek == 6), gap=120)
report("규칙 4. 주간 RSI(14) 30 미만 첫 발생 (120일 간격)", first)
P(f"   현재 주간 RSI {wr.iloc[-1]:.0f} ({wr.index[-1].date()} 주, 진행 중일 수 있음). 사이클 저점 주의 주간 RSI: " + ", ".join(f"{k} {wr.asof(d):.0f}" for k, d in CL.items() if d >= wr.dropna().index[0]))

# ── 규칙 5. 저점 근처 체류 시간 ──
P("\n### 규칙 5. 최저 종가 +20% 이내 종가가 저점 뒤 며칠째까지 나왔는가 (확정 사이클 저점 vs 2026)")
for k, d in CL.items():
    cd = c[d - TD(days=5):d + TD(days=5)].idxmin(); cl = c[cd]; seg = c[cd:cd + TD(days=500)]; inz = seg[seg <= cl * 1.20]
    P(f"   {k}: 최저 종가 {cd.date()} ${cl:,.0f} | +20% 이내 종가 {len(inz)}일, 마지막 날 저점 후 {(inz.index[-1] - cd).days}일째 ({inz.index[-1].date()}) | +10% 이내 {int((seg <= cl * 1.10).sum())}일")

# ── 규칙 7. MVRV 2단 ──
mv = F.mvrv
for thr in (1.0, 1.15):
    report(f"규칙 7. MVRV ≤ {thr} 첫 진입 (약세 구간, 180일 간격)", first_days((mv <= thr) & F.zone, gap=180))
P("   사이클 저점일 MVRV(일중 저가 기준): " + ", ".join(f"{k} {l[d] / (c[d] / mv[d]):.2f}" for k, d in CL.items()) + f" | 현재 {mv.iloc[-1]:.2f}")

# ── 규칙 8. 저변동 선반 붕괴 플래그 ──
bbw = (4 * c.rolling(20).std()) / c.rolling(20).mean(); sdq = F.sd60[F.zone].quantile(0.20)
P(f"\n### 규칙 8. 5σ 음봉 당일의 '저변동 선반 붕괴' 여부 (60일 변동성 ≤ 약세 구간 하위 20% = {sdq:.2%}/일, 또는 직전 30일 볼린저 폭 최저 ≤ 0.08) 이면서 120일 최저 종가 첫 이탈")
for d in F.index[F.fin]:
    lowvol = (F.sd60[d] <= sdq) or (bbw[d - TD(days=30):d - TD(days=1)].min() <= 0.08)
    newlow = c[d] < c[d - TD(days=120):d - TD(days=1)].min() and not (c[d - TD(days=10):d - TD(days=1)] < c[d - TD(days=130):d - TD(days=11)].min()).any()
    m, f90, f365 = outcome(d)
    P(f"   {d.date()} {F.ret[d]:+.0%} | 60일 변동성 {F.sd60[d]:.2%} 볼린저 폭 최저 {bbw[d - TD(days=30):d - TD(days=1)].min():.2f} | 저변동 {bool(lowvol)} · 120일 신저가 첫 이탈 {bool(newlow)} → 플래그 {bool(lowvol and newlow)} | 추가 하락 {m:+.0%}")
P(f"   현재: 60일 변동성 {F.sd60.iloc[-1]:.2%}/일, 직전 30일 볼린저 폭 최저 {bbw.iloc[-30:].min():.2f}, 120일 최저 종가 ${c.iloc[-120:].min():,.0f}")

# ── 규칙 11. 완전 투매 vs 부분 투매 (DVOL) ──
dv = rd(os.path.join(EX, "DVOL.csv"), parse_dates=["date"])
if dv is not None and fu is not None:
    dvh = dv.set_index("date").high; med90 = dv.set_index("date").close.rolling(90).median().shift(1)
    P("\n### 규칙 11. 투매일(2.5σ·거래량 1.5배, Yahoo)의 DVOL 고가 ÷ 직전 90일 중앙값, 당일 펀딩 합 (2021-06~)")
    for d in Y.index[Y.cap & (Y.index >= "2021-06-25")]:
        if d not in dvh.index: continue
        ratio = dvh[d] / med90[d]; fday = fd.get(d, np.nan); full = ratio >= 1.5 and fday < 0; m, f90, f365 = outcome(d) if d in c.index else (np.nan,) * 3
        P(f"   {d.date()} {Y.ret[d]:+.1%} ({Y.z[d]:.1f}σ) | DVOL {dvh[d]:.0f} = {ratio:.2f}배 | 펀딩 {fday * 1e4:+.1f}bp | {'완전' if full else '부분'} | 추가 하락 {m:+.0%}")

# ── 규칙 12. 데스먼드식 매수 확인: 5σ 음봉 뒤 10일 안 +3σ 양봉 ──
P("\n### 규칙 12. 5σ 음봉 뒤 10일 안에 +3σ 이상 양봉")
for d in F.index[F.fin]:
    seg = F.z[d + TD(days=1):d + TD(days=10)]; up = seg[seg >= 3]
    ud = up.index[0] if len(up) else None; m = outcome(ud)[0] if ud is not None else np.nan
    P(f"   {d.date()} | " + (f"{ud.date()} {F.ret[ud]:+.0%} ({F.z[ud]:+.1f}σ) 종가 ${c[ud]:,.0f} → 그 종가 대비 추가 하락 {m:+.0%}" if ud is not None else "없음"))

# ══ 2차 수집 자료 ══
# ── 김치프리미엄 ──
def krw_rate():
    fr = pd.read_csv(os.path.join(HERE, "..", "data", "macro", "DEXKOUS.csv"), parse_dates=["date"]).set_index("date").value
    fr = pd.to_numeric(fr, errors="coerce").dropna(); y = rd(os.path.join(EX2, "Y_USDKRW.csv"), parse_dates=["date"])
    if y is not None: fr = pd.concat([fr, y.set_index("date").close[fr.index[-1] + TD(days=1):]])
    return fr[~fr.index.duplicated()].sort_index()
bh = rd(os.path.join(EX2, "BTC_KRW_BITHUMB_1D.csv"), parse_dates=["date"]); up = rd(os.path.join(EX2, "BTC_KRW_UPBIT_1D.csv"), parse_dates=["date"])
if bh is not None or up is not None:
    fx = krw_rate().reindex(c.index, method="ffill"); kp = {}
    for nm, d in (("빗썸", bh), ("업비트", up)):
        if d is None: continue
        k = d.set_index("date").close.reindex(c.index); kp[nm] = (k / fx / c - 1)
    KP = pd.DataFrame(kp); kpm = KP.mean(axis=1); KP.assign(mean=kpm).dropna(how="all").to_csv(os.path.join(HERE, "output", "kimchi_premium.csv"))
    P("\n### 김치프리미엄 (원화 거래소 종가 ÷ 환율 ÷ Bitstamp 달러 종가 − 1). 주의: 종가 시각이 거래소마다 달라 급변일에는 ±2~3%p 오차")
    for k, d in CL.items():
        a = kpm[d - TD(days=30):d]; s = "  ".join(f"{nm} {KP[nm].get(d, np.nan):+.1%}" for nm in KP)
        P(f"   {k} 저점 {d.date()}: {s} | 직전 30일 평균 {a.mean():+.1%}, 최저 {a.min():+.1%}, 음수 일수 {int((a < 0).sum())}/30 | 이후 30일 평균 {kpm[d:d + TD(days=30)].mean():+.1%}")
    neg = (kpm.rolling(7).mean() < 0); run = neg.astype(int).groupby((~neg).cumsum()).cumsum()
    report("김치프리미엄 7일 평균이 20일 연속 음수가 된 첫날 (약세 구간, 90일 간격)", first_days((run == 20) & F.zone, gap=90))
    P(f"   최근 값: " + ", ".join(f"{d.date()} {v:+.1%}" for d, v in kpm.dropna().iloc[-5:].items()) + f" | 7일 평균 {kpm.dropna().iloc[-7:].mean():+.1%}")
    if up is not None:
        kv = up.set_index("date").krw_volume; r = kv.rolling(30).mean() / kv.rolling(365).mean()
        P("   업비트 BTC 원화 거래대금 30일 평균 ÷ 1년 평균: " + ", ".join(f"{k} {r.asof(d):.2f}" for k, d in CL.items() if d >= r.dropna().index[0]) + f" | 현재 {r.iloc[-1]:.2f}")

# ── CBBI ──
cb = rd(os.path.join(EX2, "CBBI.csv"), parse_dates=["date"])
if cb is not None:
    cb = cb.set_index("date"); conf = cb["Confidence"] * (100 if cb["Confidence"].max() <= 1.5 else 1)
    P("\n### CBBI 종합 지수(0~100). 사이클 저점일 값과 저점 전후 60일 최저")
    for k, d in CL.items():
        if d < conf.dropna().index[0]: continue
        w_ = conf[d - TD(days=60):d + TD(days=60)]; P(f"   {k} {d.date()}: {conf.asof(d):.0f} | ±60일 최저 {w_.min():.0f} ({w_.idxmin().date()})")
    P(f"   현재 {conf.dropna().iloc[-1]:.0f} ({conf.dropna().index[-1].date()}), 2026년 최저 {conf['2026'].min():.0f} ({conf['2026'].idxmin().date()})")
    for thr in (10, 15, 20):
        report(f"CBBI ≤ {thr} 첫 진입 (180일 간격)", first_days((conf <= thr).reindex(c.index, method="ffill"), gap=180))
    comp = [x for x in cb.columns if x not in ("Price", "Confidence")]
    P("   구성 지표 현재 값(0~1): " + ", ".join(f"{x} {cb[x].dropna().iloc[-1]:.2f}" for x in comp))
    for k in ("2018", "2022", "2026-07"):
        P(f"   구성 지표 {k} 저점일: " + ", ".join(f"{x} {cb[x].asof(CL[k]):.2f}" for x in comp))

# ── 스테이블코인 공급 ──
st = rd(os.path.join(EX2, "STABLECOINS.csv"), parse_dates=["date"])
if st is not None:
    s = st.set_index("date").usd; ch30 = s / s.shift(30) - 1
    P("\n### 스테이블코인 총공급 30일 변화율: " + ", ".join(f"{k} {ch30.asof(d):+.1%}" for k, d in CL.items() if d >= ch30.dropna().index[0]) + f" | 현재 {ch30.iloc[-1]:+.1%} ({ch30.index[-1].date()}), 총 ${s.iloc[-1] / 1e9:,.0f}억달러×10")
    report("스테이블코인 30일 변화율 ≤ -3% 첫 발생 (120일 간격)", first_days((ch30 <= -0.03).reindex(c.index, method="ffill"), gap=120))

# ── 미결제약정 ──
oi = rd(os.path.join(EX2, "BINANCE_OI_1D.csv"), parse_dates=["date"])
if oi is not None:
    o = oi.set_index("date").oi_btc; ch1 = o / o.shift(1) - 1; ch3 = o / o.shift(3) - 1; ch7 = o / o.shift(7) - 1
    P("\n### Binance BTCUSDT 선물 미결제약정(BTC 기준) 변화: 주요 저점일")
    for k, d in {**CL, "2022-06": pd.Timestamp("2022-06-18"), "2024-08": pd.Timestamp("2024-08-05"), "2025-04": pd.Timestamp("2025-04-07"), "2026-06-05": pd.Timestamp("2026-06-05"), "2026-11-13": pd.Timestamp("2026-11-13")}.items():
        if d < o.index[0] or d > o.index[-1]: continue
        P(f"   {k} {d.date()}: 1일 {ch1.asof(d):+.1%}, 3일 {ch3.asof(d):+.1%}, 7일 {ch7.asof(d):+.1%} | 30일 고점 대비 {o.asof(d) / o[d - TD(days=30):d].max() - 1:+.1%} | 롱숏 계정비 {oi.set_index('date').ls_ratio.asof(d):.2f}")
    report("미결제약정 3일 -15% 이하 첫 발생 (30일 간격, 2021-12~)", first_days((ch3 <= -0.15).reindex(c.index).fillna(False), gap=30))

# ── Bitfinex 마진 롱 ──
bf = rd(os.path.join(EX2, "BITFINEX_MARGIN.csv"), parse_dates=["date"])
if bf is not None and len(bf) > 100:
    b = bf.set_index("date").sort_index(); lg = b["long"]
    P("\n### Bitfinex 마진 롱 잔고(BTC): " + ", ".join(f"{k} {lg.asof(d):,.0f} (90일 전 대비 {lg.asof(d) / lg.asof(d - TD(days=90)) - 1:+.0%})" for k, d in CL.items() if d >= lg.dropna().index[0] + TD(days=90)) + f" | 현재 {lg.dropna().iloc[-1]:,.0f} ({lg.dropna().index[-1].date()})")

# ── BGeometrics 온체인 ──
def bg(name):
    d = rd(os.path.join(EX2, f"BG_{name}.csv"))
    if d is None: return None
    vc = [x for x in d.columns if x not in ("d", "unixTs")]
    if "d" not in d.columns or not vc: return None
    idx = pd.to_datetime(d["d"], errors="coerce")
    s = pd.to_numeric(d[vc[-1]], errors="coerce"); s.index = idx; return s[~s.index.isna()].sort_index()
bgs = {n: bg(n) for n in ("sth_realized_price", "lth_realized_price", "realized_price", "true_market_mean", "cvdd", "balanced_price", "terminal_price", "mvrv_zscore", "nupl", "sopr", "sth_sopr", "lth_sopr",
                          "supply_profit", "puell_multiple", "reserve_risk", "sth_mvrv", "realized_loss", "nrpl_usd")}
have = {k: v for k, v in bgs.items() if v is not None and len(v) > 50}
if have:
    P("\n### BGeometrics 무료 온체인 자료: 사이클 저점일 값과 현재 값")
    for n, s in have.items():
        P(f"   {n}: " + ", ".join(f"{k} {s.asof(d):,.2f}" for k, d in CL.items() if d >= s.dropna().index[0]) + f" | 현재 {s.dropna().iloc[-1]:,.2f} ({s.dropna().index[-1].date()})")
    for n in ("sth_realized_price", "lth_realized_price", "true_market_mean", "cvdd", "balanced_price", "realized_price"):
        if n in have:
            s = have[n].reindex(c.index, method="ffill"); P(f"   가격 ÷ {n}: " + ", ".join(f"{k} {l[d] / s[d]:.2f}" for k, d in CL.items() if s[d] == s[d]) + f" | 현재 {c.iloc[-1] / s.iloc[-1]:.2f} (수준 ${s.iloc[-1]:,.0f})")

# ── 실현손실 급증일 ──
rl = bg("realized_loss")
if rl is not None:
    rl = rl.abs()
    P("\n### 실현손실(달러, BGeometrics) 상위 12일 (2022-11~)과 그날 종가 대비 추가 하락")
    for d, v in rl.nlargest(12).sort_index().items():
        dd = c.index[c.index.get_indexer([d], method="nearest")[0]]; m = outcome(dd)[0]
        P(f"   {d.date()} ${v / 1e9:.2f}B | 종가 ${c[dd]:,.0f} | 추가 하락 {m:+.0%}")
    P(f"   최근 7일: " + ", ".join(f"{d.date()} ${v / 1e9:.2f}B" for d, v in rl.dropna().iloc[-7:].items()))
    sp = bg("supply_profit")
    if sp is not None:
        tot = pd.read_csv(os.path.join(EX, "BTC_ONCHAIN_EXTRA.csv"), parse_dates=["date"]).set_index("date").SplyCur; pct = (sp / tot.reindex(sp.index, method="ffill")).dropna()
        P("   이익 상태 물량 비율(이익 물량 ÷ 총공급): " + ", ".join(f"{k} {pct.asof(d):.1%}" for k, d in CL.items() if d >= pct.index[0]) + f" | 현재 {pct.iloc[-1]:.1%} ({pct.index[-1].date()}), 2026년 최저 {pct['2026'].min():.1%} ({pct['2026'].idxmin().date()}), 2022-11~ 최저 {pct.min():.1%} ({pct.idxmin().date()})")

# ── 현물 ETF 흐름 (Farside) ──
ef = rd(os.path.join(EX2, "ETF_FLOWS_FARSIDE.csv"))
if ef is not None:
    ef = ef[ef["Date"].astype(str).str.match(r"\d{2} \w{3} \d{4}")].copy(); ef["date"] = pd.to_datetime(ef["Date"], format="%d %b %Y")
    num = lambda x: pd.to_numeric(str(x).replace(",", "").replace("(", "-").replace(")", ""), errors="coerce")
    tot = ef.set_index("date")["Total"].map(num).dropna().sort_index()
    neg = tot < 0; streak = neg.astype(int).groupby((~neg).cumsum()).cumsum(); s5 = tot.rolling(5).sum(); s10 = tot.rolling(10).sum(); s35 = tot.rolling(35).sum()
    P(f"\n### 미국 현물 ETF 순유입 (Farside, 백만 달러, {tot.index[0].date()} ~ {tot.index[-1].date()})")
    for k, d in {"2024-08": pd.Timestamp("2024-08-05"), "2025-04": pd.Timestamp("2025-04-07"), "2025-11": pd.Timestamp("2025-11-21"), "2026-02": CL["2026-02"], "2026-06-05": pd.Timestamp("2026-06-05"), "2026-07": CL["2026-07"], "현재": tot.index[-1]}.items():
        P(f"   {k} {d.date()}: 당일 {tot.asof(d):+,.0f} | 5일 합 {s5.asof(d):+,.0f} | 10일 합 {s10.asof(d):+,.0f} | 35일(7주) 합 {s35.asof(d):+,.0f} | 연속 유출 {int(streak.asof(d))}일")
    P("   5일 합 역대 최저 8회: " + ", ".join(f"{d.date()} {v:+,.0f}" for d, v in s5.nsmallest(40).sort_index().groupby(pd.Grouper(freq='30D')).min().dropna().nsmallest(8).sort_index().items()))
    ev = first_days((s10 <= -2000).reindex(c.index).fillna(False), gap=30)
    report("ETF 10거래일 순유출 20억 달러 이상 첫 발생 (30일 간격)", ev)
    P(f"   누적 순유입 ${tot.sum() / 1e3:,.1f}B, 고점 대비 {tot.cumsum().iloc[-1] - tot.cumsum().max():+,.0f}M")

# ── 스트래티지(MSTR) ──
ms = rd(os.path.join(EX2, "Y_MSTR.csv"), parse_dates=["date"])
if ms is not None:
    m = ms.set_index("date").close; ratio = (m / c.reindex(m.index)).dropna()
    P("\n### MSTR 주가 ÷ BTC 가격 (mNAV 대용, 주식 수 변화 미반영): " + ", ".join(f"{k} {ratio.asof(d) * 1e3:.2f}" for k, d in CL.items() if d >= ratio.index[0]) + f" | 현재 {ratio.iloc[-1] * 1e3:.2f} ({ratio.index[-1].date()}), 2026년 최저 {ratio['2026'].min() * 1e3:.2f} ({ratio['2026'].idxmin().date()})")

# ── ETH/BTC, 나스닥, 달러 ──
et = rd(os.path.join(EX2, "Y_ETHUSD.csv"), parse_dates=["date"]); nq = rd(os.path.join(EX2, "Y_NASDAQ.csv"), parse_dates=["date"]); dx = rd(os.path.join(EX2, "Y_DXY.csv"), parse_dates=["date"])
if nq is not None:
    n = nq.set_index("date").close; ndd = n / n.cummax() - 1
    P("\n### 나스닥 종합지수의 고점 대비 낙폭: " + ", ".join(f"{k} {ndd.asof(d):+.0%}" for k, d in CL.items()) + f" | 현재 {ndd.iloc[-1]:+.1%} ({ndd.index[-1].date()})")
if dx is not None:
    x = dx.set_index("date").close; P("### 달러지수 60일 변화: " + ", ".join(f"{k} {x.asof(d) / x.asof(d - TD(days=60)) - 1:+.1%}" for k, d in CL.items()) + f" | 현재 {x.iloc[-1] / x.asof(x.index[-1] - TD(days=60)) - 1:+.1%} (수준 {x.iloc[-1]:.1f})")

# ── 원화 기준 가격 ──
if up is not None:
    kc = up.set_index("date"); kl = kc.low; P(f"\n### 업비트 원화 가격: 2026-02-06 저가 {kl.asof(pd.Timestamp('2026-02-06')):,.0f}원, 2026-06~07 최저 {kl['2026-06-01':'2026-07-31'].min():,.0f}원 ({kl['2026-06-01':'2026-07-31'].idxmin().date()}), 최근 5일 저가 " + ", ".join(f"{d.date()} {v:,.0f}" for d, v in kl.iloc[-5:].items()) + f" | 2026년 최저 {kl['2026'].min():,.0f}원 ({kl['2026'].idxmin().date()})")

# ── 예측 시장 ──
pm = rd(os.path.join(EX2, "POLYMARKET_BTC.csv"))
if pm is not None and len(pm):
    pm["volume"] = pd.to_numeric(pm.volume, errors="coerce"); pm = pm[pm.closed.astype(str).str.lower() != "true"]
    q = pm[pm.question.astype(str).str.contains(r"dip|low|below|less than|drop|fall|reach|hit|above", case=False, regex=True)].sort_values("volume", ascending=False).head(45)
    P(f"\n### 폴리마켓 비트코인 계약 (수집 {pm.fetched_utc.iloc[0]} UTC, 가격 수준 관련 거래량 상위)")
    for _, r in q.iterrows(): P(f"   [{r.event}] {r.question} | {r.outcomes} = {r.prices} | 만기 {str(r.end)[:10]} | 거래량 ${r.volume:,.0f}")

os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
open(os.path.join(HERE, "output", "bottom_rules_backtest.txt"), "w").write("\n".join(LINES) + "\n")
