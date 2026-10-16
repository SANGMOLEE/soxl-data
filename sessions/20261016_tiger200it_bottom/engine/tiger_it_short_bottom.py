# -*- coding: utf-8 -*-
"""TIGER 200 IT (139260) 단기저점 스코어 엔진 v1 (2026-10-16 사전 고정 규칙)

표시점수 = 100 − 조건점수. 0에 가까울수록 단기 저점.
실행: python3 -I tiger_it_short_bottom.py --session <세션 폴더> --repo <soxl-data 루트> [--out <출력 폴더>]
출력: daily.csv (일별 블록·점수), status.json, LATEST.md
"""
import os, sys, json, argparse, glob, io
import numpy as np
import pandas as pd

# ───────────────────────────── 규칙 (PREREGISTRATION.md §2)
P1_CUTS, P1_PTS = (-0.06, -0.10, -0.15, -0.20), (4, 8, 12, 15)
P2_CUTS, P2_PTS = (40, 35, 30, 25), (3, 6, 9, 12)
P3_CUTS, P3_PTS = (-0.05, -0.08, -0.12), (3, 5, 7)
P4_CUTS, P4_PTS = (-0.06, -0.10, -0.15), (2, 4, 6)
V1_CUTS, V1_PTS = (1.5, 2.0, 3.0), (2, 4, 6)
V2_CUTS, V2_PTS = (20, 10, 5), (2, 4, 7)
V3_CUTS, V3_PTS = (20, 10, 5), (2, 4, 7)
S1_CUTS, S1_PTS = (22, 27, 33, 40), (2, 4, 6, 8)      # VKOSPI (대체: 실현변동성 % 같은 경계)
S2_CUTS, S2_PTS = (20, 25, 33, 45), (2, 4, 6, 8)
S3_CUTS, S3_PTS = (35, 25, 15), (2, 4, 6)
S4_CUTS, S4_PTS = (0.02, 0.035, 0.05), (1, 2, 3)
G1_CUTS, G1_PTS = (-0.06, -0.10, -0.15), (3, 6, 9)
G2_CUTS, G2_PTS = (40, 35, 30), (2, 4, 6)
BUY_RULE = {"t1": 60, "t2": 50, "t3": 40, "w": (0.2, 0.3, 0.5), "gap": 0.95, "min_days": 2, "rearm_dd": -0.03}

# ───────────────────────────── 공통 도구 (NAIL 엔진과 같은 꼴)
def bands_le(x, cuts, pts):
    x = np.asarray(x, float); out = np.zeros(len(x))
    for c, p in zip(cuts, pts): out = np.where((x <= c) & (p > out), p, out)
    return np.where(np.isnan(x), 0.0, out)

def bands_ge(x, cuts, pts):
    x = np.asarray(x, float); out = np.zeros(len(x))
    for c, p in zip(cuts, pts): out = np.where((x >= c) & (p > out), p, out)
    return np.where(np.isnan(x), 0.0, out)

def wilder_rsi(x, n=14):
    d = x.diff().values; up = np.clip(d, 0, None); dn = np.clip(-d, 0, None)
    out = np.full(len(x), np.nan)
    if len(x) <= n: return pd.Series(out, index=x.index)
    au = np.nanmean(up[1:n + 1]); ad = np.nanmean(dn[1:n + 1])
    out[n] = 100 - 100 / (1 + au / ad) if ad > 0 else 100.0
    for i in range(n + 1, len(x)):
        au = (au * (n - 1) + up[i]) / n; ad = (ad * (n - 1) + dn[i]) / n
        out[i] = 100 - 100 / (1 + au / ad) if ad > 0 else 100.0
    return pd.Series(out, index=x.index)

def asof_strict(series, tdays):
    """날짜 < t 인 마지막 값 (한국 아침에 아는 미국 값)."""
    s = series.dropna(); idx = s.index.searchsorted(tdays, side='left') - 1
    return pd.Series([s.iloc[j] if j >= 0 else np.nan for j in idx], index=tdays)

def asof_incl(series, tdays):
    s = series.dropna(); idx = s.index.searchsorted(tdays, side='right') - 1
    return pd.Series([s.iloc[j] if j >= 0 else np.nan for j in idx], index=tdays)

def rolling_pct(x, n=250, minp=120):
    """x의 직전 n개(당일 제외) 대비 백분위(0~100) = 과거값 중 x 이하 비율."""
    v = x.values; out = np.full(len(v), np.nan)
    for i in range(len(v)):
        past = v[max(0, i - n):i]; past = past[~np.isnan(past)]
        if len(past) >= minp and not np.isnan(v[i]): out[i] = 100.0 * np.mean(past <= v[i])
    return pd.Series(out, index=x.index)

# ───────────────────────────── 입력
def read_price(path):
    df = pd.read_csv(path, parse_dates=["date"]).sort_values("date").drop_duplicates("date")
    df = df.set_index("date")
    return df

def read_fchart_xml(path):
    """네이버 fchart XML → DataFrame(date, open, high, low, close, volume)."""
    import re
    txt = open(path, encoding="utf-8", errors="ignore").read()
    rows = [r.split("|") for r in re.findall(r'<item data="([^"]+)"', txt)]
    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    for c in ["open", "high", "low", "close", "volume"]: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.set_index("date").sort_index()

def load_flows(naver_dir, code):
    """종목별 외국인·기관 순매매(주). 모바일 API(mapi_trend_*) 우선, 없으면 frgn_* HTML 표."""
    p = os.path.join(naver_dir, f"mapi_trend_{code}.csv")
    if os.path.exists(p):
        df = pd.read_csv(p)
        dcol = "bizdate" if "bizdate" in df.columns else df.columns[0]
        df["date"] = pd.to_datetime(df[dcol].astype(str).str[:10].str.replace("-", ""), format="%Y%m%d")
        f = next((c for c in df.columns if "foreigner" in c.lower() and "pure" in c.lower() and "quant" in c.lower()), None)
        o = next((c for c in df.columns if "organ" in c.lower() and "pure" in c.lower() and "quant" in c.lower()), None)
        if f is None or o is None: return None, f"mapi_trend_{code}: 열 인식 실패 {list(df.columns)}"
        out = pd.DataFrame({"frgn": pd.to_numeric(df[f].astype(str).str.replace(",", ""), errors="coerce"),
                            "inst": pd.to_numeric(df[o].astype(str).str.replace(",", ""), errors="coerce")}, index=df["date"])
        return out.sort_index().groupby(level=0).last(), f"mapi_trend_{code}"
    p = os.path.join(naver_dir, f"frgn_{code}.csv")
    if os.path.exists(p):
        df = pd.read_csv(p)
        df["date"] = pd.to_datetime(df["date"])
        f = next((c for c in df.columns if "외국인" in c and "순매매" in c), None)
        o = next((c for c in df.columns if "기관" in c and "순매매" in c), None)
        if f is None or o is None: return None, f"frgn_{code}: 열 인식 실패 {list(df.columns)}"
        out = pd.DataFrame({"frgn": pd.to_numeric(df[f].astype(str).str.replace(",", "").str.replace("+", ""), errors="coerce"),
                            "inst": pd.to_numeric(df[o].astype(str).str.replace(",", "").str.replace("+", ""), errors="coerce")}, index=df["date"])
        return out.sort_index().groupby(level=0).last(), f"frgn_{code}"
    return None, f"{code}: 수급 자료 없음"

def load_market_flows(naver_dir):
    """코스피 투자자별 순매수(억원). investor_KOSPI.csv 또는 mapi_trend_KOSPI.csv."""
    p = os.path.join(naver_dir, "investor_KOSPI.csv")
    if os.path.exists(p):
        df = pd.read_csv(p); df["date"] = pd.to_datetime(df["date"])
        f = next((c for c in df.columns if "외국인" in c), None)
        if f is None: return None, "investor_KOSPI: 외국인 열 없음"
        return pd.to_numeric(df.set_index("date")[f].astype(str).str.replace(",", ""), errors="coerce").sort_index(), "investor_KOSPI"
    p = os.path.join(naver_dir, "mapi_trend_KOSPI.csv")
    if os.path.exists(p):
        df = pd.read_csv(p)
        dcol = "bizdate" if "bizdate" in df.columns else df.columns[0]
        df["date"] = pd.to_datetime(df[dcol].astype(str).str[:10].str.replace("-", ""), format="%Y%m%d")
        f = next((c for c in df.columns if "foreigner" in c.lower() and "pure" in c.lower()), None)
        if f is None: return None, f"mapi_trend_KOSPI: 열 인식 실패 {list(df.columns)}"
        return pd.to_numeric(df.set_index("date")[f].astype(str).str.replace(",", ""), errors="coerce").sort_index().groupby(level=0).last(), "mapi_trend_KOSPI"
    return None, "코스피 투자자별 자료 없음"

def load_vkospi(naver_dir):
    for name in ["index_VKOSPI.csv", "vkospi.csv"]:
        p = os.path.join(naver_dir, name)
        if os.path.exists(p):
            df = pd.read_csv(p); df["date"] = pd.to_datetime(df["date"])
            c = next((c for c in df.columns if "체결" in c or "close" in c.lower() or "종가" in c), df.columns[1])
            return pd.to_numeric(df.set_index("date")[c].astype(str).str.replace(",", ""), errors="coerce").sort_index(), name
    return None, "VKOSPI 없음 → 코스피 20일 실현변동성으로 대체"

# ───────────────────────────── 계산
def compute(session_dir, repo_dir):
    warn = []
    P = os.path.join(session_dir, "data", "prices"); N = os.path.join(session_dir, "data", "naver")
    etf = read_price(os.path.join(P, "TIGER200IT.csv"))
    # 네이버 fchart가 있으면 더 긴/최신 쪽으로 보완 (가격 불일치 0.5% 초과 시 경고)
    fx = os.path.join(N, "try_fchart_139260.txt")
    if os.path.exists(fx):
        nv = read_fchart_xml(fx)
        common = etf.index.intersection(nv.index)[-30:]
        diff = (etf.loc[common, "close"] / nv.loc[common, "close"] - 1).abs().max()
        if diff > 0.005: warn.append(f"TIGER200IT: Yahoo·네이버 최근 30일 종가 차이 최대 {diff:.2%}")
        extra = nv.index.difference(etf.index)
        if len(extra): etf = pd.concat([etf, nv.loc[extra].assign(adj_close=np.nan, source="naver")]).sort_index()
    etf = etf[etf["close"].notna()]
    # 거래량 0인 날(유령행) 제거: 종가가 전일과 같고 거래량 0
    ghost = (etf["volume"] == 0) & (etf["close"] == etf["close"].shift())
    if ghost.any(): warn.append(f"TIGER200IT: 거래량 0·종가 동일 유령행 {int(ghost.sum())}건 제거 {list(etf.index[ghost].strftime('%Y-%m-%d'))[:5]}")
    etf = etf[~ghost]
    tdays = etf.index
    c = etf["close"]

    # P 블록
    p1 = c / c.rolling(20, min_periods=20).max() - 1
    p2 = wilder_rsi(c)
    p3 = c / c.rolling(20, min_periods=20).mean() - 1
    p4 = c / c.shift(5) - 1
    P1 = bands_le(p1, P1_CUTS, P1_PTS); P2 = bands_le(p2, P2_CUTS, P2_PTS)
    P3 = bands_le(p3, P3_CUTS, P3_PTS); P4 = bands_le(p4, P4_CUTS, P4_PTS)

    # V 블록
    vol = etf["volume"].replace(0, np.nan)
    v1 = vol / vol.shift(1).rolling(20, min_periods=15).mean()
    V1 = bands_ge(v1, V1_CUTS, V1_PTS)
    mkt, mkt_src = load_market_flows(N)
    etf_flow, etf_flow_src = load_flows(N, "139260")
    if mkt is not None:
        v2raw = mkt.reindex(tdays).rolling(5, min_periods=5).sum(); v2_src = f"코스피 외국인 순매수(억원) 5일 누적 [{mkt_src}]"
    elif etf_flow is not None:
        amt = (etf_flow["frgn"] + etf_flow["inst"]).reindex(tdays) * c
        v2raw = amt.rolling(5, min_periods=5).sum(); v2_src = f"대체: 139260 (외국인+기관) 순매매 금액 5일 누적 [{etf_flow_src}]"
        warn.append("V2: 코스피 투자자별 자료 없음 → ETF 자체 수급으로 대체 (사전 고정 대체 규칙)")
    else:
        v2raw = pd.Series(np.nan, index=tdays); v2_src = "없음"; warn.append("V2: 수급 자료 없음 → 0점")
    v2 = rolling_pct(v2raw)
    V2 = bands_le(v2, V2_CUTS, V2_PTS)
    parts3 = []; srcs3 = []
    for code, name in [("005930", "SAMSUNG"), ("000660", "HYNIX")]:
        fl, src = load_flows(N, code)
        if fl is None: warn.append(f"V3: {code} 수급 없음 ({src})"); continue
        px = read_price(os.path.join(P, f"{name}.csv"))["close"]
        parts3.append(((fl["frgn"] + fl["inst"]) * px.reindex(fl.index)).reindex(tdays)); srcs3.append(src)
    if parts3:
        v3raw = sum(parts3).rolling(5, min_periods=5).sum(); v3_src = "삼성전자+SK하이닉스 (외국인+기관) 순매매 금액 5일 누적 [" + ", ".join(srcs3) + "]"
    else:
        v3raw = pd.Series(np.nan, index=tdays); v3_src = "없음"
    v3 = rolling_pct(v3raw)
    V3 = bands_le(v3, V3_CUTS, V3_PTS)

    # S 블록
    vk, vk_src = load_vkospi(N)
    kospi = read_price(os.path.join(P, "KOSPI.csv"))["close"]
    fk = os.path.join(N, "try_fchart_KOSPI.txt")
    if os.path.exists(fk):
        nk = read_fchart_xml(fk)["close"]; kospi = pd.concat([kospi, nk[nk.index.difference(kospi.index)]]).sort_index()
    if vk is not None:
        s1 = asof_incl(vk, tdays); s1_src = f"VKOSPI [{vk_src}]"
    else:
        lr = np.log(kospi).diff(); rv = lr.rolling(20, min_periods=20).std() * np.sqrt(252) * 100
        s1 = asof_incl(rv, tdays); s1_src = "대체: 코스피 20일 실현변동성(연율 %)"; warn.append("S1: " + vk_src)
    S1 = bands_ge(s1, S1_CUTS, S1_PTS)
    vix = read_price(os.path.join(P, "VIX.csv"))["close"]
    vix20 = vix.rolling(20, min_periods=20).max()
    s2 = asof_strict(vix20, tdays); S2 = bands_ge(s2, S2_CUTS, S2_PTS)
    fgp = os.path.join(repo_dir, "data", "sentiment", "fear_greed.csv")
    if os.path.exists(fgp):
        fg = pd.read_csv(fgp, parse_dates=["date"]).set_index("date")["value"].sort_index()
        s3 = asof_strict(fg, tdays)
    else:
        s3 = pd.Series(np.nan, index=tdays); warn.append("S3: 공포탐욕 자료 없음")
    S3 = bands_le(s3, S3_CUTS, S3_PTS)
    krw = read_price(os.path.join(P, "USDKRW.csv"))["close"]
    s4 = asof_incl(krw / krw.shift(20) - 1, tdays); S4 = bands_ge(s4, S4_CUTS, S4_PTS)

    # G 블록
    sox = read_price(os.path.join(P, "SOX.csv"))["close"]
    g1 = asof_strict(sox / sox.rolling(20, min_periods=20).max() - 1, tdays)
    g2 = asof_strict(wilder_rsi(sox), tdays)
    G1 = bands_le(g1, G1_CUTS, G1_PTS); G2 = bands_le(g2, G2_CUTS, G2_PTS)

    df = pd.DataFrame({
        "close": c, "open": etf["open"], "volume": etf["volume"],
        "p1_dd20": p1, "p2_rsi14": p2, "p3_ma20": p3, "p4_ret5": p4,
        "v1_volratio": v1, "v2_raw": v2raw, "v2_pct": v2, "v3_raw": v3raw, "v3_pct": v3,
        "s1_vkospi": s1, "s2_vix20max": s2, "s3_fg": s3, "s4_krw20": s4,
        "g1_soxdd20": g1, "g2_soxrsi": g2,
        "P1": P1, "P2": P2, "P3": P3, "P4": P4, "V1": V1, "V2": V2, "V3": V3,
        "S1": S1, "S2": S2, "S3": S3, "S4": S4, "G1": G1, "G2": G2,
    }, index=tdays)
    df["P"] = df[["P1", "P2", "P3", "P4"]].sum(axis=1); df["V"] = df[["V1", "V2", "V3"]].sum(axis=1)
    df["S"] = df[["S1", "S2", "S3", "S4"]].sum(axis=1); df["G"] = df[["G1", "G2"]].sum(axis=1)
    df["cond"] = df[["P", "V", "S", "G"]].sum(axis=1); df["display"] = 100 - df["cond"]
    meta = {"v2_src": v2_src, "v3_src": v3_src, "s1_src": s1_src,
            "last": {"ETF": str(tdays[-1].date()), "VIX": str(vix.index[-1].date()), "SOX": str(sox.index[-1].date()),
                     "KOSPI": str(kospi.index[-1].date()), "USDKRW": str(krw.index[-1].date()),
                     "FG": str(fg.index[-1].date()) if os.path.exists(fgp) else None,
                     "flow_ETF": str(etf_flow.index[-1].date()) if etf_flow is not None else None,
                     "flow_mkt": str(mkt.index[-1].date()) if mkt is not None else None},
            "warn": warn}
    return df, meta

# ───────────────────────────── 매수 규칙 v1 시뮬레이션
def simulate(df, rule=BUY_RULE):
    fills = []; tranche = 0; last_px = np.nan; last_i = -99; armed = True
    disp = df["display"].values; close = df["close"].values; opn = df["open"].values; dd = df["p1_dd20"].values
    for i in range(len(df) - 1):
        if tranche > 0 and dd[i] > rule["rearm_dd"]:
            tranche = 0; last_px = np.nan; last_i = -99
        if np.isnan(disp[i]): continue
        if tranche == 0 and disp[i] <= rule["t1"]:
            fills.append((df.index[i], df.index[i + 1], 1, rule["w"][0], opn[i + 1], disp[i])); tranche = 1; last_px = opn[i + 1]; last_i = i
        elif tranche in (1, 2):
            thr = rule["t2"] if tranche == 1 else rule["t3"]
            if disp[i] <= thr and close[i] <= last_px * rule["gap"] and i - last_i >= rule["min_days"]:
                fills.append((df.index[i], df.index[i + 1], tranche + 1, rule["w"][tranche], opn[i + 1], disp[i])); tranche += 1; last_px = opn[i + 1]; last_i = i
    return pd.DataFrame(fills, columns=["signal", "fill", "tranche", "weight", "fill_px", "display_at_signal"])

# ───────────────────────────── 보고
def write_outputs(df, meta, out_dir, fills):
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "daily.csv"), float_format="%.6g")
    fills.to_csv(os.path.join(out_dir, "fills_v1.csv"), index=False)
    last = df.iloc[-1]; d = df.index[-1].strftime("%Y-%m-%d")
    st = {"date": d, "close": float(last["close"]), "display_score": float(last["display"]), "cond": float(last["cond"]),
          "blocks": {k: float(last[k]) for k in ["P", "V", "S", "G"]},
          "items": {k: float(last[k]) for k in ["P1", "P2", "P3", "P4", "V1", "V2", "V3", "S1", "S2", "S3", "S4", "G1", "G2"]},
          "raw": {k: (None if pd.isna(last[k]) else float(last[k])) for k in
                  ["p1_dd20", "p2_rsi14", "p3_ma20", "p4_ret5", "v1_volratio", "v2_raw", "v2_pct", "v3_raw", "v3_pct",
                   "s1_vkospi", "s2_vix20max", "s3_fg", "s4_krw20", "g1_soxdd20", "g2_soxrsi"]},
          "sources": {"v2": meta["v2_src"], "v3": meta["v3_src"], "s1": meta["s1_src"]}, "last_obs": meta["last"], "warnings": meta["warn"]}
    json.dump(st, open(os.path.join(out_dir, "status.json"), "w"), ensure_ascii=False, indent=1)
    rows = [
        ("P1 20일 낙폭", f"{last['p1_dd20']:+.1%}", last["P1"]), ("P2 RSI14", f"{last['p2_rsi14']:.1f}", last["P2"]),
        ("P3 20일선 이격", f"{last['p3_ma20']:+.1%}", last["P3"]), ("P4 5일 수익률", f"{last['p4_ret5']:+.1%}", last["P4"]),
        ("V1 거래량/20일", f"{last['v1_volratio']:.2f}", last["V1"]), ("V2 수급(시장) 백분위", f"{last['v2_pct']:.0f} (5일 {last['v2_raw']:,.0f})" if pd.notna(last['v2_pct']) else "없음", last["V2"]),
        ("V3 수급(삼성+하이닉스) 백분위", f"{last['v3_pct']:.0f} (5일 {last['v3_raw']:,.0f}원)" if pd.notna(last['v3_pct']) else "없음", last["V3"]),
        (f"S1 {meta['s1_src']}", f"{last['s1_vkospi']:.1f}", last["S1"]), ("S2 VIX 20일 최고", f"{last['s2_vix20max']:.1f}", last["S2"]),
        ("S3 공포탐욕", f"{last['s3_fg']:.0f}" if pd.notna(last['s3_fg']) else "없음", last["S3"]), ("S4 원달러 20일 변화", f"{last['s4_krw20']:+.1%}", last["S4"]),
        ("G1 SOX 20일 낙폭", f"{last['g1_soxdd20']:+.1%}", last["G1"]), ("G2 SOX RSI14", f"{last['g2_soxrsi']:.1f}", last["G2"]),
    ]
    md = [f"# TIGER 200 IT 단기저점 스코어 v1 — 최신 판정 ({d} 종가)", "",
          f"- 종가 {last['close']:,.0f}원 · **표시점수 {last['display']:.0f}** (조건 {last['cond']:.0f} = P {last['P']:.0f} + V {last['V']:.0f} + S {last['S']:.0f} + G {last['G']:.0f})",
          f"- 기준선 v1: 1차 ≤{BUY_RULE['t1']} · 2차 ≤{BUY_RULE['t2']} · 3차 ≤{BUY_RULE['t3']}", "",
          "| 항목 | 원값 | 점수 |", "|---|---|---:|"]
    md += [f"| {a} | {b} | {int(cc)} |" for a, b, cc in rows]
    md += ["", "원천 마지막 관측: " + json.dumps(meta["last"], ensure_ascii=False)]
    if meta["warn"]: md += ["", "경고:"] + [f"- {w}" for w in meta["warn"]]
    if len(fills):
        md += ["", "## 모형 가상 체결 (v1 규칙, 최근 10건)", "", "| signal | fill | tranche | weight | fill_px | display |", "|---|---|---|---|---|---|"]
        for _, r in fills.tail(10).iterrows():
            md.append(f"| {r['signal'].date()} | {r['fill'].date()} | {r['tranche']} | {r['weight']} | {r['fill_px']:,.0f} | {r['display_at_signal']:.0f} |")
    md += ["", "*인샘플 규칙의 기계적 판정이며 투자 권유가 아니다.*"]
    open(os.path.join(out_dir, "LATEST.md"), "w", encoding="utf-8").write("\n".join(md))
    return st

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--repo", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    repo = a.repo or os.path.dirname(os.path.dirname(a.session))
    out = a.out or os.path.join(a.session, "output")
    df, meta = compute(a.session, repo)
    fills = simulate(df)
    st = write_outputs(df, meta, out, fills)
    print(json.dumps({k: st[k] for k in ["date", "close", "display_score", "blocks"]}, ensure_ascii=False))
    for w in meta["warn"]: print("WARN", w)
