# -*- coding: utf-8 -*-
"""사이클 전략 엔진 v2 — 전략서(FINAL_STRATEGY_SOLT_BITU.md v2)의 규칙을 유일한 기준으로 구현.
v1(full_cycle_backtest.py) 대비 변경:
  1) 체결 달력: ETF 는 미국 거래일에만 체결(SPY.csv 달력). 신호는 직전 체결일 이후 ~ 체결일 전날(UTC 종가)까지의 크립토 일봉으로 판정.
     현물(spot) 모드는 크립토 7일 달력.
  2) 상장 전 합성 ETF 에 실측 레버리지 비용 적용: BITU 연 16%, SOLT 연 20% (실제 ETF 대 2배 현물 괴리 실측치). 상장 후는 실제 조정종가.
  3) 문서 규칙으로 통일: 최종 매도 후 -35% 재성립 필요 / 분할익절 현금은 그 사이클 재투입 금지(금고) / 대피 중에도 200일선 규칙 적용 /
     손절 후 복귀는 사다리 조건 / 눈금 40(저점×2.7) 이상 신규 진입 금지 / 200일선 하회 일수는 사이클 진입일부터 셈 / 초기화는 3차 진입 전까지.
  4) core 모드: 솔라나 규칙(로테이션·사다리·손절·대피)을 끄고 뼈대(진입·초기화·200일선·분할익절·최종매도)만. 2015~2020 BTC 표본 외 시험용.
"""
import numpy as np, pandas as pd, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "data", "crypto"); SPY = os.path.join(ROOT, "data", "prices", "SPY.csv")
HALVINGS = [pd.Timestamp(x) for x in ("2012-11-28", "2016-07-09", "2020-05-11", "2024-04-20", "2028-04-15")]
TOP_FORCE_FROM = pd.Timestamp("2028-01-01")   # 전략서 §6-1: 2028-01 부터 최종매도 규칙 활성화

def _ld(n, c="close"):
    return pd.read_csv(os.path.join(D, n + ".csv"), parse_dates=["date"]).set_index("date")[c].astype(float).sort_index()
BTC_RAW, SOL_RAW = _ld("BTCUSD"), _ld("SOLUSD")
CAL7 = pd.date_range(BTC_RAW.index[0], BTC_RAW.index[-1])
BTC = BTC_RAW.reindex(CAL7).ffill(); SOL = SOL_RAW.reindex(CAL7).ffill()
REAL = {"SOLT": _ld("SOLT", "adj_close"), "BITU": _ld("BITU", "adj_close")}
US = pd.DatetimeIndex(pd.read_csv(SPY, parse_dates=["date"])["date"]); US = US[(US >= CAL7[0]) & (US <= CAL7[-1])]
SPOT = {"SOLT": SOL, "BITU": BTC}
DRAG = {"SOLT": 0.20, "BITU": 0.16}       # 실측 연간 괴리
FEE_ONLY = {"SOLT": 0.0185, "BITU": 0.0095}

def instrument(name, cal, lev=2.0, drag=None, use_real=True):
    """체결 달력 위의 상품 가격(시작 1). 상장 전: 체결일 간 현물 수익×lev − 연비용 일할. 상장 후: 실제 조정종가 수익."""
    spot = SPOT[name].reindex(cal); d = DRAG[name] if drag is None else drag
    days = pd.Series(cal, index=cal).diff().dt.days.fillna(0)
    r = np.clip(lev * spot.pct_change(), -0.999, None) - d * days / 365.0
    if use_real and lev == 2.0:
        rr = REAL[name].reindex(cal).pct_change(); live = cal > REAL[name].index[0]
        r = r.where(~live, rr.fillna(0.0))
    return (1 + r.fillna(0.0)).cumprod()

P0 = dict(start="2020-04-11", end=None, mode="etf", lev=2.0, cost=0.003, drag=None, use_real=True,
          core=False, dd_bear=0.35, ma_bottom=100, below_days=60, surge=0.15, cap_mult=2.7,
          rot_n=20, rot_in=0.0, rot_out=-0.05, x_ladder=1.5, dip=0.30, brk=0.30, tmax=60, stop=0.25,
          evac=0.10, re_up=0.20, tp_levels=(4, 8), top_win=(300, 600), final_dd=0.10)

def signals(P):
    ma_b = BTC.rolling(P["ma_bottom"]).mean(); ma200 = BTC.rolling(200).mean()
    bl = (BTC < ma_b).astype(int); run_bl = bl.groupby((bl == 0).cumsum()).cumsum()
    rec = (BTC > ma_b) & (run_bl.shift(1) >= P["below_days"])
    a2 = (BTC > ma200).astype(int); run_a2 = a2.groupby((a2 == 0).cumsum()).cumsum()
    g7 = BTC / BTC.shift(7) - 1; ratio = SOL / BTC; rmom = ratio / ratio.shift(P["rot_n"]) - 1
    return pd.DataFrame(dict(btc=BTC, sol=SOL, rec=rec, ab5=run_a2 >= 5, above200=BTC > ma200, below200=BTC < ma200,
                             surge=g7 >= P["surge"], rmom=rmom))

def run(P_in, verbose=False):
    P = dict(P0); P.update(P_in)
    cal = CAL7 if P["mode"] == "spot" else US
    start = pd.Timestamp(P["start"]); end = pd.Timestamp(P["end"]) if P["end"] else CAL7[-1]
    cal = cal[(cal >= start) & (cal <= end)]
    lev = 1.0 if P["mode"] == "spot" else P["lev"]
    px = {k: instrument(k, cal, lev, 0.0 if P["mode"] == "spot" else P["drag"], P["use_real"] and P["mode"] != "spot") for k in ("SOLT", "BITU")}
    S = signals(P); A, B = "SOLT", "BITU"; cost = P["cost"]; core = P["core"]
    hold = {A: 0.0, B: 0.0}; cash = 1.0; vault = 0.0
    st = dict(phase="WAIT", cyc_hi=BTC[:cal[0]].iloc[:-1].max(), bear_lo=None, tranche=0, bottom_ref=None, peak=None,
              evac=False, evac_lo=None, ladder=None, ent_sol=None, wait=None, cyc_eq=None, tp_done=0, run200=0)
    log = []; eq = []; last_info = cal[0] - pd.Timedelta(days=1)
    V = lambda t: cash + vault + sum(hold[k] * px[k][t] for k in hold)
    LV = lambda t: sum(hold[k] * px[k][t] for k in hold)
    def to(t, tgt, why):
        nonlocal cash, hold
        v = LV(t)
        if v <= 0: return
        v *= 1 - cost; hold = {A: 0.0, B: 0.0}
        if tgt == "CASH": cash += v
        else: hold[tgt] = v * (1 - cost) / px[tgt][t]
        log.append((t.date(), "→" + tgt, why, round(V(t), 4), round(BTC[t]), round(SOL[t], 1)))
    def buy(t, frac, why, tgt):
        nonlocal cash
        amt = cash * frac
        if amt <= 0: return
        cash -= amt; hold[tgt] += amt * (1 - cost) / px[tgt][t]
        log.append((t.date(), "매수" + tgt, why, round(V(t), 4), round(BTC[t]), round(SOL[t], 1)))
    for t in cal:
        info_end = t - pd.Timedelta(days=1); seg = S.loc[last_info + pd.Timedelta(days=1): info_end]; last_info = info_end
        if len(seg) == 0: eq.append(V(t)); continue
        last = seg.iloc[-1]; b, s = last.btc, last.sol; s_t = SOL[t]
        bmax, bmin, smax, smin = seg.btc.max(), seg.btc.min(), seg.sol.max(), seg.sol.min()
        rm = last.rmom; tool = B if core else (A if rm > P["rot_in"] else B)
        hal = max([h for h in HALVINGS if h <= info_end], default=None)
        in_top = (hal is not None and P["top_win"][0] <= (info_end - hal).days <= P["top_win"][1]) or (info_end >= TOP_FORCE_FROM and hal is not None and (info_end - hal).days <= P["top_win"][1] + 365)
        if st["phase"] == "WAIT":
            for _, r in seg.iterrows():
                st["cyc_hi"] = max(st["cyc_hi"], r.btc)
                if r.btc <= st["cyc_hi"] * (1 - P["dd_bear"]): st["bear_lo"] = r.btc if st["bear_lo"] is None else min(st["bear_lo"], r.btc)
                elif st["bear_lo"] is not None: st["bear_lo"] = min(st["bear_lo"], r.btc)
            if st["bear_lo"] is not None and seg.rec.any() and np.isfinite(px[tool][t]):
                st.update(phase="UP", tranche=1, bottom_ref=st["bear_lo"], peak=b, evac=False, ladder=None, wait=None, tp_done=0, run200=0)
                cash += vault; vault = 0.0; st["cyc_eq"] = V(t)
                buy(t, 1 / 3, "1차 저점확인", tool); st["ent_sol"] = s_t
            eq.append(V(t)); continue
        # ---- UP ----
        st["cyc_hi"] = max(st["cyc_hi"], bmax)
        if st["tranche"] < 3 and bmin < st["bottom_ref"]:
            to(t, "CASH", "초기화(약세장 저점 이탈)"); st.update(phase="WAIT", bear_lo=bmin, tranche=0); eq.append(V(t)); continue
        if st["tranche"] < 3 and cash > 0 and not (b > st["bottom_ref"] * P["cap_mult"]):
            if st["tranche"] == 1 and seg.ab5.any(): buy(t, 1 / 2, "2차 200일선 5일", tool); st["tranche"] = 2; st["ent_sol"] = s_t
            elif seg.surge.any(): buy(t, 1.0, "3차 7일 급등", tool); st["tranche"] = 3; st["ent_sol"] = s_t
        st["peak"] = max(st["peak"], bmax)
        if st["tp_done"] < len(P["tp_levels"]) and V(t) >= st["cyc_eq"] * P["tp_levels"][st["tp_done"]] and LV(t) > 0:
            for k in hold: sell = hold[k] / 3; hold[k] -= sell; vault += sell * px[k][t] * (1 - cost)
            st["tp_done"] += 1; log.append((t.date(), "분할익절 1/3→금고", f"{P['tp_levels'][st['tp_done']-1]}배", round(V(t), 4), round(BTC[t]), round(SOL[t], 1)))
        if bmin <= st["peak"] * (1 - P["final_dd"]) and in_top:
            to(t, "CASH", "최종매도(고점창 -10%)"); st.update(phase="WAIT", cyc_hi=st["peak"], bear_lo=None, tranche=0); eq.append(V(t)); continue
        if not core and not in_top and not st["evac"] and hold[A] > 0 and bmin <= st["peak"] * (1 - P["evac"]):
            to(t, B, "눌림 대피 BTC-10%"); st.update(evac=True, evac_lo=bmin, ladder=None, wait=None)
        if st["evac"]:
            st["evac_lo"] = min(st["evac_lo"], bmin)
            if bmax >= st["evac_lo"] * (1 + P["re_up"]):
                st.update(evac=False, peak=b, ladder=None, wait=None, ent_sol=s_t)
                if hold[B] > 0 and tool == A: to(t, A, "+20% 반등 복귀")
        hit5 = False
        for _, r in seg.iterrows():
            st["run200"] = st["run200"] + 1 if r.below200 else 0
            if st["run200"] >= 5: hit5 = True
        if hit5 and LV(t) > 0: to(t, "CASH", "200일선 5일 하회"); st.update(ladder=None, evac=False, wait="BEAR")
        if LV(t) == 0 and cash > 0 and st["wait"] == "BEAR" and last.above200 and st["run200"] == 0:
            buy(t, 1.0, "200일선 위 재진입", tool); st.update(wait=None, ent_sol=s_t)
        if core: eq.append(V(t)); continue
        if hold[A] > 0 and not st["evac"]:
            if smin <= st["ent_sol"] * (1 - P["stop"]): to(t, "CASH", "손절 SOL-25%"); st.update(wait="STOP", ladder=dict(xp=s_t, lo=s_t, t=t))
            elif rm < P["rot_out"]: to(t, B, "로테이션 이탈"); st["ladder"] = None
            elif smax >= st["ent_sol"] * P["x_ladder"]: to(t, "CASH", "1.5배 익절"); st.update(ladder=dict(xp=s_t, lo=s_t, t=t), wait="LADDER")
        elif hold[A] == 0 and not st["evac"] and (hold[B] > 0 or st["wait"] in ("LADDER", "STOP")):
            ok = False
            if st["ladder"] is not None:
                L = st["ladder"]; L["lo"] = min(L["lo"], smin)
                if L["lo"] <= L["xp"] * (1 - P["dip"]) or smax >= L["xp"] * (1 + P["brk"]) or (t - L["t"]).days >= P["tmax"]: ok, why = True, "사다리 복귀"
            elif rm > P["rot_in"]: ok, why = True, "로테이션 복귀"
            if ok:
                if hold[B] > 0:
                    if tool == A: to(t, A, why)
                elif cash > 0: buy(t, 1.0, why, tool)
                st.update(ladder=None, wait=None, ent_sol=s_t)
        eq.append(V(t))
    E = pd.Series(eq, index=cal); st["hold"] = dict(hold); st["cash"] = cash; st["vault"] = vault
    return E, log, st

def fmt(e, a=None, b=None):
    e = (e[a:b] if (a or b) else e).dropna(); tot = e.iloc[-1] / e.iloc[0]; yrs = max((e.index[-1] - e.index[0]).days / 365.25, 1e-9)
    dd = (e / e.cummax() - 1).min(); cg = tot ** (1 / yrs) - 1
    return f"{tot-1:+,.0%} / 낙폭 {dd:.0%} / 연 {cg:+.0%} / 연÷낙폭 {cg/abs(dd) if dd else 0:.2f}"
def aftertax(e, a, rate=0.22):
    e = e[a:].dropna(); v = 1.0; prev = e.iloc[0]
    for y in sorted(set(e.index.year)):
        ey = e[e.index.year == y]; r = ey.iloc[-1] / prev - 1; v *= 1 + (r * (1 - rate) if r > 0 else r); prev = ey.iloc[-1]
    return v - 1
