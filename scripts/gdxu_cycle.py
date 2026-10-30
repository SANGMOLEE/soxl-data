# -*- coding: utf-8 -*-
"""
GDXU 금광주 사이클 연구 — 분석기 (v0.1, 2026-10-30)

SOXL 연구와 같은 틀로 레버리지 ETN(GDXU)과 기초 1x(GDX/HUI)의
사이클 저점·낙폭·회복 배수·감쇠·거시 블록을 한 번에 출력한다.

사용
  python scripts/gdxu_cycle.py                    # 기본: --lev GDXU --base GDX
  python scripts/gdxu_cycle.py --lev SOXL --base SOX   # SOXL 연구와 교차 검증
  python scripts/gdxu_cycle.py --base HUI --no-lev     # 장기 지수만

필요 파일 (없으면 해당 블록만 건너뜀)
  data/prices/{lev,base,GLD,NEM,SLV}.csv
  data/macro/{VIXCLS,NFCI,BAMLH0A0HYM2,DFII10,DTWEXBGS}.csv
  data/sentiment/fear_greed.csv
"""
import os, sys, argparse
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, "data", *a)


def rd(path, col="close"):
    if not os.path.exists(path):
        return None
    d = pd.read_csv(path, parse_dates=["date"]).sort_values("date")
    s = d.set_index("date")[col].astype(float).dropna()
    return s[s > 0] if col == "close" else s      # 거시 시리즈는 음수가 정상값


# ── 사이클 저점 탐지 ─────────────────────────────────────────
def cycle_bottoms(c, min_dd=0.30, rebound=0.30):
    """
    지그재그 방식. 직전 고점 대비 min_dd 이상 하락하면 '하락 사이클'로 보고,
    그 뒤 최저점에서 rebound 이상 반등하면 저점을 확정한다.
    (단순 cummax 방식은 2000~2008처럼 전고점 미회복 구간을 하나로 합쳐 버린다)
    반환: peak_date, peak, trough_date, trough, dd, days(고점→저점 거래일),
          next_peak(다음 하락 사이클 직전 고점), mult(저점→다음 고점 배수)
    """
    idx = c.index; v = c.values
    rows = []
    pk_i = 0; tr_i = None; state = "up"
    for i in range(1, len(v)):
        if state == "up":
            if v[i] >= v[pk_i]:
                pk_i = i
            elif v[i] / v[pk_i] - 1 <= -min_dd:
                state = "down"; tr_i = i
        else:
            if v[i] <= v[tr_i]:
                tr_i = i
            elif v[i] / v[tr_i] - 1 >= rebound:
                rows.append(dict(peak_date=idx[pk_i].date(), peak=round(v[pk_i], 2),
                                 trough_date=idx[tr_i].date(), trough=round(v[tr_i], 2),
                                 dd=round(v[tr_i] / v[pk_i] - 1, 3), days=tr_i - pk_i,
                                 _tr=tr_i))
                state = "up"; pk_i = i
    # 미확정 하락 사이클(현재 진행 중)도 표시
    if state == "down":
        rows.append(dict(peak_date=idx[pk_i].date(), peak=round(v[pk_i], 2),
                         trough_date=idx[tr_i].date(), trough=round(v[tr_i], 2),
                         dd=round(v[tr_i] / v[pk_i] - 1, 3), days=tr_i - pk_i, _tr=tr_i))
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    nxt = []
    for r, (_, row) in enumerate(df.iterrows()):
        end = int(df.iloc[r + 1]._tr) if r + 1 < len(df) else len(v)
        seg_max = v[int(row._tr):end].max()
        nxt.append(seg_max)
    df["next_peak"] = np.round(nxt, 2); df["mult"] = np.round(df.next_peak / df.trough, 2)
    df.loc[df.index[-1], "status"] = "진행중(미확정)" if state == "down" else "확정"
    df["status"] = df["status"].fillna("확정")
    return df.drop(columns="_tr")


def drawdown_table(c, name):
    peak = c.cummax(); dd = c / peak - 1
    ath_d = c.idxmax()
    out = {
        "종목": name, "최근일": c.index[-1].date(), "종가": round(c.iloc[-1], 2),
        "사상최고": round(c.max(), 2), "최고일": ath_d.date(),
        "고점대비": f"{dd.iloc[-1]:.1%}",
        "고점후 거래일": int((c.index > ath_d).sum()),
        "1개월": f"{c.iloc[-1] / c.iloc[-22] - 1:.1%}" if len(c) > 22 else None,
        "3개월": f"{c.iloc[-1] / c.iloc[-64] - 1:.1%}" if len(c) > 64 else None,
        "52주 저점": round(c.iloc[-252:].min(), 2), "52주 저점일": c.iloc[-252:].idxmin().date(),
        "저점대비": f"{c.iloc[-1] / c.iloc[-252:].min() - 1:+.1%}",
    }
    return out


# ── 레버리지 감쇠 실측 ───────────────────────────────────────
def decay(lev, base, k=3, windows=(21, 63, 126, 252)):
    j = pd.concat([lev, base], axis=1, keys=["lev", "base"], sort=True).dropna()
    rows = []
    for w in windows:
        if len(j) <= w:
            continue
        rl = j.lev.iloc[-1] / j.lev.iloc[-1 - w] - 1
        rb = j.base.iloc[-1] / j.base.iloc[-1 - w] - 1
        # 일간 k배 복리 경로의 이론값
        rk = float(np.prod(1 + k * j.base.pct_change().iloc[-w:]) - 1)
        rows.append({"창(거래일)": w, "기초": f"{rb:+.1%}", f"선형 {k}x": f"{k * rb:+.1%}",
                     f"일간복리 {k}x": f"{rk:+.1%}", "실제": f"{rl:+.1%}",
                     "경로감쇠(실제-선형)": f"{rl - k * rb:+.1%}"})
    beta = np.polyfit(j.base.pct_change().dropna().iloc[-252:],
                      j.lev.pct_change().dropna().iloc[-252:], 1)[0] if len(j) > 260 else np.nan
    return pd.DataFrame(rows), beta


# ── 낙폭비율 (SOXL 연구의 NVDA 필터와 같은 발상) ──────────────
def dd_ratio(leader, index, window=504):
    j = pd.concat([leader, index], axis=1, keys=["L", "I"], sort=True).dropna().iloc[-window:]
    dl = j.L.iloc[-1] / j.L.max() - 1
    di = j.I.iloc[-1] / j.I.max() - 1
    return dl, di, (dl / di if di < 0 else np.nan)


def scenarios(lev_now, base_now, base_targets, k=3, sig=0.035, n=40):
    rows = []
    for label, tgt in base_targets:
        r = tgt / base_now - 1
        lin = max(lev_now * (1 + k * r), 0)
        geo = lev_now * (tgt / base_now) ** k * np.exp(-0.5 * k * (k - 1) * sig ** 2 * n)
        rows.append({"시나리오": label, "기초 목표": round(tgt, 2), "기초 변화": f"{r:+.1%}",
                     f"선형{k}x": round(lin, 1), f"기하{k}x(σ{sig:.1%},{n}일)": round(geo, 1)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lev", default="GDXU"); ap.add_argument("--base", default="GDX")
    ap.add_argument("--no-lev", action="store_true"); ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--min-dd", type=float, default=0.30)
    a = ap.parse_args()
    pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)

    base = rd(P("prices", f"{a.base}.csv"))
    if base is None:
        sys.exit(f"기초 파일 없음: data/prices/{a.base}.csv — collect.py 가 한 번 돌아야 한다")
    lev = None if a.no_lev else rd(P("prices", f"{a.lev}.csv"))

    print(f"\n━━ A블록. 가격 수준 ({a.base}{'' if lev is None else ' / ' + a.lev}) ━━")
    print(pd.DataFrame([drawdown_table(base, a.base)] + ([drawdown_table(lev, a.lev)] if lev is not None else [])).T.to_string())

    print(f"\n━━ A블록. {a.base} 사이클 저점 (고점대비 -{a.min_dd:.0%} 이상) ━━")
    cb = cycle_bottoms(base, a.min_dd)
    print(cb.to_string(index=False) if len(cb) else "해당 없음")
    if len(cb):
        cur = base.iloc[-1] / base.cummax().iloc[-1] - 1
        done = cb[cb.status == "확정"] if "status" in cb else cb
        med = done.dd.median() if len(done) else cb.dd.median()
        print(f"\n현재 낙폭 {cur:.1%} / 과거 저점 낙폭 중앙값 {med:.1%} → 낙폭비율 {cur / med:.2f} "
              f"(1.0 이상 = 과거 평균 저점 깊이 도달)")
        if len(done):
            print(f"과거 저점 → 다음 고점 배수: 중앙값 {done.mult.median():.2f}x, 최소 {done.mult.min():.2f}x, 최대 {done.mult.max():.2f}x")
            print(f"과거 고점→저점 소요: 중앙값 {done.days.median():.0f} 거래일, 최장 {done.days.max()} 거래일")

    if lev is not None:
        print(f"\n━━ C블록. {a.lev} 경로감쇠 실측 ━━")
        dt, beta = decay(lev, base, a.k)
        print(dt.to_string(index=False)); print(f"최근 252일 일간 회귀기울기(β): {beta:.3f}  (목표 {a.k})")

        print(f"\n━━ 시나리오. 기초 목표 → {a.lev} 추정 ━━")
        ath = base.max(); b0 = base.iloc[-1]
        tg = [("최근 52주 저점 재시험", base.iloc[-252:].min()),
              ("고점대비 -45% (2018·2020형)", ath * 0.55), ("고점대비 -52% (2022형)", ath * 0.48),
              ("고점대비 -72% (2008형)", ath * 0.28), ("고점대비 -81% (2011~16형)", ath * 0.19)]
        print(scenarios(lev.iloc[-1], b0, tg, a.k).to_string(index=False))

    # 상대강도·필터
    gld = rd(P("prices", "GLD.csv")); nem = rd(P("prices", "NEM.csv")); slv = rd(P("prices", "SLV.csv"))
    print("\n━━ E블록. 상대강도·필터 ━━")
    if gld is not None:
        r = (base / gld).dropna()
        print(f"{a.base}/GLD 비율: {r.iloc[-1]:.3f}  (252일 고 {r.iloc[-252:].max():.3f} / 저 {r.iloc[-252:].min():.3f}, "
              f"고점대비 {r.iloc[-1] / r.iloc[-252:].max() - 1:.1%})")
        if slv is not None:
            gs = (gld / slv).dropna(); print(f"GLD/SLV(금은비율 대용): {gs.iloc[-1]:.2f}  (252일 범위 {gs.iloc[-252:].min():.2f}~{gs.iloc[-252:].max():.2f})")
    if nem is not None:
        for w in (504, 756):
            dl, di, ratio = dd_ratio(nem, base, w)
            print(f"NEM 필터 {w}일: NEM 낙폭 {dl:.1%} / {a.base} 낙폭 {di:.1%} → 비율 {ratio:.2f} (≥0.80 = 대장주 동반 항복)")

    # 거시 블록
    print("\n━━ B·D블록. 거시·심리 (SOXL 연구와 공용) ━━")
    vix = rd(P("macro", "VIXCLS.csv"), "value")
    if vix is not None:
        print(f"VIX {vix.iloc[-1]:.2f} ({vix.index[-1].date()})  60일 최고 {vix.iloc[-60:].max():.2f}")
    for sid, lab in (("NFCI", "NFCI(0 초과=긴축)"), ("BAMLH0A0HYM2", "하이일드 스프레드(3.41% 감시)"),
                     ("DFII10", "10년 실질금리"), ("T10YIE", "10년 BEI"), ("DTWEXBGS", "광의 달러지수")):
        s = rd(P("macro", f"{sid}.csv"), "value")
        if s is not None:
            print(f"{lab}: {s.iloc[-1]:.3f} ({s.index[-1].date()})  126일 범위 {s.iloc[-126:].min():.3f}~{s.iloc[-126:].max():.3f}")
    fg = rd(P("sentiment", "fear_greed.csv"), "value")
    if fg is not None:
        print(f"공포탐욕 {fg.iloc[-1]:.1f} ({fg.index[-1].date()})  60일 최저 {fg.iloc[-60:].min():.1f}")


if __name__ == "__main__":
    main()
