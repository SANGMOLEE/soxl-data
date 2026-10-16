# -*- coding: utf-8 -*-
"""단기저점 스코어 v1 백테스트 (PREREGISTRATION.md §4 고정 방법)
실행: python3 -I backtest.py --session <세션 폴더> --repo <soxl-data 루트>
출력: research/output/*.csv, research/output/backtest_summary.md
"""
import os, sys, json, argparse
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
from tiger_it_short_bottom import compute, simulate, BUY_RULE
from scipy.stats import beta

def clopper(k, n, a=0.05):
    lo = beta.ppf(a / 2, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(1 - a / 2, k + 1, n - k) if k < n else 1.0
    return lo, hi

def short_bottoms(close, w=10, fwd=20, rebound=0.06, decline=0.93, back=30):
    """§4 정의: ±w 최저 종가, 이후 fwd일 최고 ≥ 1+rebound, 직전 back일 최고 대비 ≤ decline."""
    c = close.values; n = len(c); out = []
    for t in range(back, n - fwd):
        if c[t] != c[t - w:t + w + 1].min(): continue
        if c[t + 1:t + fwd + 1].max() < c[t] * (1 + rebound): continue
        if c[t] > c[t - back:t + 1].max() * decline: continue
        out.append(t)
    return out

def episodes(disp, thr, gap=20):
    """thr 이하로 처음 내려간 날(직전 gap일 안에 같은 신호 없음)."""
    idx = []; last = -10**9
    v = disp.values
    for i in range(len(v)):
        if not np.isnan(v[i]) and v[i] <= thr and i - last > gap:
            idx.append(i); last = i
    return idx

def fwd_stats(df, idxs, bottoms, label):
    """신호일 i → 다음날 시가 체결. 5/10/20일 수익률, 20일 최저 종가 추가 하락, ±5일 안 단기 저점, 다음 저점까지 일수."""
    c = df["close"].values; o = df["open"].values; n = len(c); rows = []
    bset = np.array(bottoms)
    for i in idxs:
        if i + 1 >= n: continue
        px = o[i + 1]
        r = {"signal": df.index[i].date(), "display": df["display"].values[i], "fill_px": px}
        for h in (5, 10, 20):
            r[f"ret{h}"] = c[i + 1 + h] / px - 1 if i + 1 + h < n else np.nan
        r["mae20"] = c[i + 1:i + 21].min() / px - 1 if i + 21 <= n else np.nan
        r["mfe20"] = c[i + 1:i + 21].max() / px - 1 if i + 21 <= n else np.nan
        near = bset[(bset >= i - 5) & (bset <= i + 5)]
        r["bottom_within5"] = len(near) > 0
        nxt = bset[bset >= i]
        r["days_to_bottom"] = int(nxt[0] - i) if len(nxt) else np.nan
        r["bottom_vs_fill"] = c[nxt[0]] / px - 1 if len(nxt) else np.nan
        rows.append(r)
    out = pd.DataFrame(rows); out["set"] = label
    return out

def summarize(tab, name):
    if len(tab) == 0: return {"set": name, "n": 0}
    done = tab.dropna(subset=["ret20"])
    k = int(tab["bottom_within5"].sum()); n = len(tab); lo, hi = clopper(k, n)
    return {"set": name, "n": n,
            "ret5_med": done["ret5"].median(), "ret10_med": done["ret10"].median(), "ret20_med": done["ret20"].median(),
            "ret20_mean": done["ret20"].mean(), "win20": (done["ret20"] > 0).mean(),
            "mae20_med": done["mae20"].median(), "mae20_worst": done["mae20"].min(),
            "bottom5_rate": k / n, "bottom5_ci": f"{lo:.0%}~{hi:.0%}", "days_to_bottom_med": tab["days_to_bottom"].median(),
            "bottom_vs_fill_med": tab["bottom_vs_fill"].median()}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--session"); ap.add_argument("--repo"); a = ap.parse_args()
    out_dir = os.path.join(a.session, "research", "output"); os.makedirs(out_dir, exist_ok=True)
    df, meta = compute(a.session, a.repo)
    df = df[df.index >= "2011-06-01"]
    # 평가 가능한 마지막 날(이후 20일 필요)
    bottoms = short_bottoms(df["close"])
    bdf = df.iloc[bottoms][["close", "display", "P", "V", "S", "G", "P1", "P2", "P3", "P4", "V1", "V2", "V3", "S1", "S2", "S3", "S4", "G1", "G2"]].copy()
    # 저점 ±3일 최저 표시점수
    bdf["display_min_pm3"] = [df["display"].iloc[max(0, t - 3):t + 4].min() for t in bottoms]
    bdf["drop_from_30d_high"] = [df["close"].iloc[t] / df["close"].iloc[t - 30:t + 1].max() - 1 for t in bottoms]
    bdf["rebound20"] = [df["close"].iloc[t + 1:t + 21].max() / df["close"].iloc[t] - 1 for t in bottoms]
    bdf.to_csv(os.path.join(out_dir, "short_bottoms.csv"), float_format="%.4g")

    # 블록 조합별 표시점수
    variants = {"full": df["display"], "P_only": 100 - df["P"], "P+S": 100 - df["P"] - df["S"],
                "P+S+G": 100 - df["P"] - df["S"] - df["G"], "P+G": 100 - df["P"] - df["G"]}
    rows = []; alltab = []
    thrs = [70, 65, 60, 55, 50, 45, 40, 35]
    for vname, disp in variants.items():
        d2 = df.copy(); d2["display"] = disp
        for thr in thrs:
            ep = episodes(disp, thr)
            tab = fwd_stats(d2, ep, bottoms, f"{vname}<= {thr}")
            s = summarize(tab, f"{vname}<= {thr}"); s["variant"] = vname; s["thr"] = thr; rows.append(s); alltab.append(tab)
            for per, (a0, a1) in {"2011-2018": ("2011-01-01", "2018-12-31"), "2019-2026": ("2019-01-01", "2026-12-31")}.items():
                sub = tab[(pd.to_datetime(tab["signal"]) >= a0) & (pd.to_datetime(tab["signal"]) <= a1)] if len(tab) else tab
                s2 = summarize(sub, f"{vname}<= {thr} {per}"); s2["variant"] = vname; s2["thr"] = thr; s2["period"] = per; rows.append(s2)
    # 기준: 전체 거래일
    allidx = list(range(0, len(df) - 21))
    base = fwd_stats(df, allidx, bottoms, "all_days"); sb = summarize(base, "all_days"); sb["variant"] = "all_days"; rows.append(sb)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "threshold_table.csv"), index=False, float_format="%.4g")
    pd.concat(alltab).to_csv(os.path.join(out_dir, "episodes_all.csv"), index=False, float_format="%.4g")

    # 항목별 단독 예측력: 각 항목 점수 구간별 이후 10일 수익률 중앙·저점 ±5일 비율
    c = df["close"].values; n = len(c)
    f10 = pd.Series([c[i + 10] / c[i] - 1 if i + 10 < n else np.nan for i in range(n)], index=df.index)
    isb = pd.Series(False, index=df.index); 
    for t in bottoms: isb.iloc[max(0, t - 5):t + 6] = True
    item_rows = []
    for item in ["P1", "P2", "P3", "P4", "V1", "V2", "V3", "S1", "S2", "S3", "S4", "G1", "G2"]:
        for val, g in df.groupby(item):
            m = g.index
            item_rows.append({"item": item, "points": val, "n_days": len(g), "fwd10_med": f10[m].median(), "fwd10_mean": f10[m].mean(),
                              "near_bottom_rate": isb[m].mean()})
    pd.DataFrame(item_rows).to_csv(os.path.join(out_dir, "item_predictive.csv"), index=False, float_format="%.4g")

    # v1 매수 규칙 시뮬레이션: 캠페인별 평균 매수가 대비 20일/60일 뒤
    fills = simulate(df)
    fills.to_csv(os.path.join(out_dir, "fills_v1.csv"), index=False)

    # 요약 md
    T = pd.DataFrame(rows)
    md = ["# 백테스트 요약 (자동 생성)", "", f"기간 {df.index[0].date()} ~ {df.index[-1].date()}, 단기 저점 {len(bottoms)}개", "",
          "## 단기 저점일 표시점수 분포", "",
          f"- 저점일: 중앙 {bdf['display'].median():.0f}, 25% {bdf['display'].quantile(.25):.0f}, 75% {bdf['display'].quantile(.75):.0f}, 최소 {bdf['display'].min():.0f}, 최대 {bdf['display'].max():.0f}",
          f"- 저점 ±3일 최저: 중앙 {bdf['display_min_pm3'].median():.0f}, 25% {bdf['display_min_pm3'].quantile(.25):.0f}, 75% {bdf['display_min_pm3'].quantile(.75):.0f}",
          "", "| 저점일 표시 | 개수 | 비율 |", "|---|---:|---:|"]
    for thr in thrs:
        k = int((bdf["display"] <= thr).sum()); md.append(f"| ≤{thr} | {k} | {k/len(bdf):.0%} |")
    md += ["", "## 기준선별 에피소드 성과 (full = 전 블록)", "", "| 변형 | 기준 | n | 5일 중앙 | 10일 중앙 | 20일 중앙 | 20일 승률 | 20일 추가하락 중앙 | 최악 | ±5일 저점 비율 (95% CI) | 저점까지 일수 중앙 | 저점가/체결가 중앙 |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|"]
    for _, r in T[T.get("period").isna() if "period" in T else [True]*len(T)].iterrows():
        if r["n"] == 0: continue
        md.append(f"| {r['variant']} | {r.get('thr', '')} | {r['n']} | {r['ret5_med']:+.1%} | {r['ret10_med']:+.1%} | {r['ret20_med']:+.1%} | {r['win20']:.0%} | {r['mae20_med']:+.1%} | {r['mae20_worst']:+.1%} | {r['bottom5_rate']:.0%} ({r['bottom5_ci']}) | {r['days_to_bottom_med']:.0f} | {r['bottom_vs_fill_med']:+.1%} |")
    open(os.path.join(out_dir, "backtest_summary.md"), "w", encoding="utf-8").write("\n".join(md))
    print("\n".join(md))
    print("\nwarnings:", meta["warn"])

if __name__ == "__main__":
    main()


# ───────────────────────────── 급락형 저점의 점수 경로 (사후 분석용 보조)
def crash_paths(session, repo, min_drop=-0.17, out_name="crash_bottom_paths.csv"):
    df, meta = compute(session, repo); df = df[df.index >= "2011-06-01"]
    bottoms = short_bottoms(df["close"]); rows = []
    for t in bottoms:
        drop = df["close"].iloc[t] / df["close"].iloc[t - 30:t + 1].max() - 1
        if drop > min_drop: continue
        path = df["display"].iloc[t - 7:t + 6].round(0).astype(int).tolist()
        r = {"bottom": df.index[t].date(), "close": df["close"].iloc[t], "drop30": round(drop, 3),
             "rebound20": round(df["close"].iloc[t + 1:t + 21].max() / df["close"].iloc[t] - 1, 3),
             "display_at_bottom": int(df["display"].iloc[t]), "path_m7_p5": path}
        for thr in (60, 50, 45, 40):
            win = df["display"].iloc[t - 15:t + 1]; hit = win[win <= thr]
            r[f"first_le{thr}_rel"] = int(df.index.get_loc(hit.index[0]) - t) if len(hit) else None
            r[f"close_at_first_le{thr}_vs_bottom"] = round(df["close"].loc[hit.index[0]] / df["close"].iloc[t] - 1, 3) if len(hit) else None
        rows.append(r)
    out = pd.DataFrame(rows); out.to_csv(os.path.join(session, "research", "output", out_name), index=False)
    return out

if __name__ == "__main__" and "--paths" in sys.argv:
    pass
