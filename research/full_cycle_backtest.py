# -*- coding: utf-8 -*-
"""최종 전략 전체(0~4단계) 통합 백테스트. 2020-01-01 ~ 최근. 신호는 전일 종가, 체결은 당일 종가. 비용 0.3%/회전.
자료: BTC·SOL 현물(Yahoo). SOLT/BITU 는 상장 후 실제 조정종가, 상장 전은 현물 일일수익×2 − 보수 합성(수익률로 이어붙임).
가격 자료가 없는 저점 조건(공포탐욕·청산·ETF)은 가격 대용으로 대체:
  저점확인 = BTC 사이클 고점 대비 -35% 이상 경험 후, BTC 종가가 100일선을 60일 이상 하회하다 회복.
"""
import numpy as np, pandas as pd, os
D = os.path.join(os.path.dirname(__file__), "..", "data", "crypto")
ld = lambda n, c="close": pd.read_csv(os.path.join(D, n + ".csv"), parse_dates=["date"]).sort_values("date").set_index("date")[c].astype(float)
btc, sol = ld("BTCUSD"), ld("SOLUSD"); solt_r, bitu_r = ld("SOLT", "adj_close"), ld("BITU", "adj_close")
def spliced(spot, real, fee):
    """상장 전: 현물×2 합성 일일수익. 상장 후: 실제 ETF 일일수익(ETF 비거래일은 0)."""
    syn = np.clip(2 * spot.pct_change().fillna(0), -0.999, None) - fee / 365
    rr = real.pct_change().fillna(0); ix = syn.index.union(rr.index)
    syn = syn.reindex(ix).fillna(0); rr = rr.reindex(ix).fillna(0)
    r = syn.where(ix < real.index[0], rr)
    return (1 + r).cumprod()
SOLT = spliced(sol, solt_r, 0.0195); BITU = spliced(btc, bitu_r, 0.0095)
HALVINGS = [pd.Timestamp("2020-05-11"), pd.Timestamp("2024-04-20"), pd.Timestamp("2028-04-15")]
P = dict(start="2020-01-01", dd_bear=0.35, ma_bottom=100, below_days=60, x_ladder=1.5, dip=0.3, brk=0.3, tmax=60, stop=0.25,
         rot_n=20, rot_in=0.0, rot_out=-0.05, tp_levels=(4, 8), final_dd=0.10, re_up=0.20, top_win=(300, 600), cost=0.003, surge=0.15,
         manage_from_t1=True, dd_outside_top=True, min_hold=0, reenter_new_high=False)
def run(P, verbose=True):
    idx = sol.index[sol.index >= P["start"]]; idx = idx[idx.isin(btc.index)]
    F = pd.DataFrame({"btc": btc, "sol": sol, "SOLT": SOLT, "BITU": BITU}).reindex(idx).ffill()
    F["b100"] = btc.rolling(P["ma_bottom"]).mean().reindex(idx); F["b200"] = btc.rolling(200).mean().reindex(idx)
    F["g7"] = (btc / btc.shift(7) - 1).reindex(idx); ratio = sol / btc; F["rmom"] = (ratio / ratio.shift(P["rot_n"]) - 1).reindex(idx)
    R = F[["SOLT", "BITU"]].pct_change().fillna(0)
    # 상태
    phase = "WAIT"; cyc_hi = btc[:idx[0]].max(); bear_lo = None; below = 0; tranche = 0; trn_dates = []
    units = {"SOLT": 0.0, "BITU": 0.0}; cash = 1.0; eq = []; log = []; ent_sol = None; ladder = None; lo_since = None; stop_px = None
    cyc_start_eq = None; tp_done = 0; peak_btc = None; top_ex = False; reenter_lo = None; b200_below = 0; stop_bitu = False; last_sw = 0; final_hi = None; bottom_ref = None
    def val(i): return cash + units["SOLT"] * F.SOLT.iloc[i] + units["BITU"] * F.BITU.iloc[i]
    def to(i, target, why):  # target: 'SOLT'|'BITU'|'CASH', 보유 레버리지 전량 전환
        nonlocal cash, units
        v = units["SOLT"] * F.SOLT.iloc[i] + units["BITU"] * F.BITU.iloc[i]
        if v <= 0: return
        v *= 1 - P["cost"] * 2; units = {"SOLT": 0.0, "BITU": 0.0}
        if target == "CASH": cash += v
        else: units[target] = v / F[target].iloc[i]
        log.append((idx[i].date(), f"→{target}", why, round(val(i), 3), round(F.btc.iloc[i]), round(F.sol.iloc[i], 1)))
    def buy(i, frac, why):
        nonlocal cash, units, ent_sol
        amt = cash * frac * (1 - P["cost"]); cash -= cash * frac  # 분할: 남은 현금의 비율
        tgt = "SOLT" if F.rmom.iloc[i - 1] > P["rot_in"] else "BITU"; units[tgt] += amt / F[tgt].iloc[i]; ent_sol = F.sol.iloc[i]
        log.append((idx[i].date(), f"매수{tgt}", why, round(val(i), 3), round(F.btc.iloc[i]), round(F.sol.iloc[i], 1)))
    for i in range(1, len(idx)):
        d = idx[i]; p = i - 1; b = F.btc.iloc[p]; s = F.sol.iloc[p]
        cyc_hi = max(cyc_hi, b)
        if phase == "WAIT":
            if b <= cyc_hi * (1 - P["dd_bear"]): bear_lo = b if bear_lo is None else min(bear_lo, b)
            below = below + 1 if b < F.b100.iloc[p] else 0
            if bear_lo is not None:
                # 저점 확인 대용: 60일 이상 100일선 하회 후 회복
                F_below = (btc[:idx[p]] < btc.rolling(P["ma_bottom"]).mean()[:idx[p]]).iloc[-P["below_days"]-1:-1]
                if b > F.b100.iloc[p] and len(F_below) >= P["below_days"] and F_below.all():
                    phase = "UP" if P["manage_from_t1"] else "ENTRY"; tranche = 0; cyc_start_eq = val(i); peak_btc = b; tp_done = 0; b200_below = 0
                    buy(i, 1 / 3, "1차 저점확인(100일선 회복)"); tranche = 1; bottom_ref = bear_lo; ladder = None; stop_px = ent_sol * (1 - P["stop"]); stop_bitu = False; last_sw = i; final_hi = None
            eq.append(val(i)); continue
        if phase == "TOPWAIT":
            hal = max([h for h in HALVINGS if h <= d], default=None); in_top = hal is not None and (d - hal).days <= P["top_win"][1]
            if not in_top or b <= final_hi * 0.65: phase = "WAIT"; bear_lo = b; cyc_hi = final_hi
            elif b > final_hi:
                phase = "UP"; tranche = 3; peak_btc = b; buy(i, 1.0, "고점창 신고가 재진입"); ladder = None; stop_px = ent_sol * (1 - P["stop"]); stop_bitu = False; last_sw = i
            eq.append(val(i)); continue
        if phase == "ENTRY":
            # 무효화: 직전 저점 이탈
            if b < bottom_ref: to(i, "CASH", "저점 이탈→초기화"); phase = "WAIT"; bear_lo = b; cyc_hi = b; eq.append(val(i)); continue
            if tranche == 1 and b > F.b200.iloc[p] and F.btc.iloc[p - 4:p + 1].gt(F.b200.iloc[p - 4:p + 1]).all(): buy(i, 1 / 2, "2차 200일선 회복"); tranche = 2
            elif tranche >= 1 and F.g7.iloc[p] > P["surge"] and tranche < 3:
                buy(i, 1.0, "3차 7일 급등"); tranche = 3; phase = "UP"; ladder = None; stop_px = ent_sol * (1 - P["stop"])
        if phase == "UP" and tranche < 3:
            if b < bottom_ref: to(i, "CASH", "저점 이탈→초기화"); phase = "WAIT"; bear_lo = b; cyc_hi = b; eq.append(val(i)); continue
            if tranche == 1 and b > F.b200.iloc[p] and F.btc.iloc[p - 4:p + 1].gt(F.b200.iloc[p - 4:p + 1]).all(): buy(i, 1 / 2, "2차 200일선 회복"); tranche = 2
            elif F.g7.iloc[p] > P["surge"]: buy(i, 1.0, "3차 7일 급등"); tranche = 3
        if phase == "UP":
            peak_btc = max(peak_btc, b); v_tot = val(i)
            hal = max([h for h in HALVINGS if h <= d], default=None); in_top = hal is not None and P["top_win"][0] <= (d - hal).days <= P["top_win"][1]
            # 3단계 분할익절
            if tp_done < len(P["tp_levels"]) and v_tot >= cyc_start_eq * P["tp_levels"][tp_done]:
                v = units["SOLT"] * F.SOLT.iloc[i] + units["BITU"] * F.BITU.iloc[i]; take = v / 3
                for k in units:
                    if units[k] > 0: sellu = units[k] * (take / v); units[k] -= sellu; cash += sellu * F[k].iloc[i] * (1 - P["cost"])
                tp_done += 1; log.append((d.date(), "분할익절 1/3", f"{P['tp_levels'][tp_done-1]}배", round(val(i), 3), round(b), round(s, 1)))
            # 최종 매도 / 대피
            if b <= peak_btc * (1 - P["final_dd"]):
                if in_top:
                    to(i, "CASH", "고점창 BTC -10% 최종매도")
                    if P["reenter_new_high"]: phase = "TOPWAIT"; final_hi = peak_btc
                    else: phase = "WAIT"; bear_lo = b; cyc_hi = peak_btc
                    eq.append(val(i)); continue
                elif P["dd_outside_top"] and units["SOLT"] > 0 and not stop_bitu: to(i, "BITU", "BTC -10% 대피"); stop_bitu = True; reenter_lo = b
            if stop_bitu:
                reenter_lo = min(reenter_lo, b)
                if b >= reenter_lo * (1 + P["re_up"]):
                    stop_bitu = False; peak_btc = b; ladder = None; ent_sol = s; stop_px = s * (1 - P["stop"])
                    to(i, "SOLT" if F.rmom.iloc[p] > P["rot_in"] else "BITU", "BTC +20% 반등 복귀")
                eq.append(val(i)); continue
            # BTC 200일선 5일 이탈 → 현금(약세 판정), 회복 시 복귀
            b200_below = b200_below + 1 if b < F.b200.iloc[p] else 0
            if b200_below >= 5 and (units["SOLT"] + units["BITU"]) > 0: to(i, "CASH", "BTC 200일선 5일 이탈"); held_cash = True
            if (units["SOLT"] + units["BITU"]) == 0 and cash > 0 and b > F.b200.iloc[p] and b200_below == 0:
                buy(i, 1.0, "200일선 복귀 재진입"); ladder = None; stop_px = ent_sol * (1 - P["stop"])
            # 2단계 로테이션 + 사다리 + 손절
            if units["SOLT"] > 0:
                if s <= stop_px: to(i, "BITU", "SOL -25% 손절"); ladder = None
                elif F.rmom.iloc[p] < P["rot_out"] and i - last_sw >= P["min_hold"]: to(i, "BITU", "비율모멘텀<-5%"); ladder = None; last_sw = i
                elif s / ent_sol >= P["x_ladder"]: to(i, "BITU", "1.5배 익절"); ladder = {"xp": s, "lo": s, "t": i}
            elif units["BITU"] > 0:
                ok = False
                if ladder is not None:
                    ladder["lo"] = min(ladder["lo"], s)
                    if ladder["lo"] <= ladder["xp"] * (1 - P["dip"]) or s >= ladder["xp"] * (1 + P["brk"]) or i - ladder["t"] >= P["tmax"]: ok = True; why = "사다리 복귀"
                elif F.rmom.iloc[p] > P["rot_in"] and i - last_sw >= P["min_hold"]: ok = True; why = "비율모멘텀>0"
                if ok: to(i, "SOLT", why); ladder = None; ent_sol = s; stop_px = s * (1 - P["stop"]); last_sw = i
        eq.append(val(i))
    E = pd.Series(eq, index=idx[1:]); return E, log, F
def stats(E, name):
    dd = (E / E.cummax() - 1).min(); yrs = (E.index[-1] - E.index[0]).days / 365.25
    return f"{name:28s} 최종 {E.iloc[-1]/E.iloc[0]-1:+,.0%}  연복리 {(E.iloc[-1]/E.iloc[0])**(1/yrs)-1:+.0%}  최대낙폭 {dd:.0%}"
def summarize(P, name):
    E, log, F = run(P, False); E2 = E["2022-11-21":]
    dd = lambda e: (e / e.cummax() - 1).min()
    return f"| {name} | {E.iloc[-1]/E.iloc[0]-1:+,.0%} / {dd(E):.0%} | {E2.iloc[-1]/E2.iloc[0]-1:+,.0%} / {dd(E2):.0%} | {len(log)} |", E, log, F
if __name__ == "__main__":
    import itertools
    print("| 변형 | 2020-04~ 수익/낙폭 | 2022-11~ 수익/낙폭 | 거래 |"); print("|---|---|---|---|")
    best = None
    for m1, dout, mh, rnh in itertools.product((False, True), (True, False), (0, 5), (False, True)):
        Q = dict(P, manage_from_t1=m1, dd_outside_top=dout, min_hold=mh, reenter_new_high=rnh)
        row, E, log, F = summarize(Q, f"1차부터관리={m1}, 창밖-10%대피={dout}, 최소보유={mh}, 신고가재진입={rnh}"); print(row)
        sc = E["2022-11-21":].iloc[-1] / E["2022-11-21":].iloc[0]
        if best is None or sc > best[0]: best = (sc, Q, row)
    for nm, ser in (("SOLT 보유", SOLT), ("BITU 보유", BITU), ("SOL 현물", sol), ("BTC 현물", btc)):
        a = ser["2020-04-11":]; b_ = ser["2022-11-21":]; dd = lambda e: (e / e.cummax() - 1).min()
        print(f"| {nm} | {a.iloc[-1]/a.iloc[0]-1:+,.0%} / {dd(a):.0%} | {b_.iloc[-1]/b_.iloc[0]-1:+,.0%} / {dd(b_):.0%} | |")
    print("\n== 2022-11 이후 최고 변형:", best[2]); P = best[1]
    E, log, F = run(P)
    print("기간", E.index[0].date(), "→", E.index[-1].date())
    print(stats(E, "최종 전략(통합)")); print(stats(F.SOLT.reindex(E.index), "SOLT 보유")); print(stats(F.BITU.reindex(E.index), "BITU 보유")); print(stats(F.sol.reindex(E.index), "SOL 현물")); print(stats(F.btc.reindex(E.index), "BTC 현물"))
    print("\n연도별 수익 (전략 / SOLT 보유 / BTC)")
    for y in range(E.index[0].year, E.index[-1].year + 1):
        e = E[str(y)]; s_ = F.SOLT.reindex(E.index)[str(y)]; b_ = F.btc.reindex(E.index)[str(y)]
        if len(e) > 5: print(f"  {y}: {e.iloc[-1]/e.iloc[0]-1:+7.0%} / {s_.iloc[-1]/s_.iloc[0]-1:+7.0%} / {b_.iloc[-1]/b_.iloc[0]-1:+6.0%}")
    print(f"\n거래 로그 {len(log)}건")
    for x in log: print("  ", *x)
    print("\n현재 상태:", "보유" if log and not log[-1][1].startswith("→CASH") else "현금", "| 마지막:", log[-1] if log else None)
