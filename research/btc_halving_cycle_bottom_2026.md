# 비트코인 반감기 사이클 저점 연구 보고서
## "저점은 지났는가, 중간선거 이후 다시 찍는가" (기준일: 2026-10-27)

---

## 0. 한 줄 결론

- **7월 1일 $57.7k~57.9k 가 이번 사이클 저점일 확률: 약 55~60%.** 중간선거(11/3) 이후 재하락으로 $50~60k 구간에서 2차 저점(더블바텀 또는 소폭 신저점)을 만들 확률: 약 40~45%.
- 확률이 반반에 가까운 이유: "시간 기준(날짜)" 모델은 **지금(10월 초~11월 중순)이 정확히 과거 저점 창**이라 말하고, "가격·온체인 기준" 모델은 **이미 저점 구조가 완성됐다**고 말하기 때문. 두 축이 충돌하는 희귀한 사이클이다.
- 연구 결론의 실무적 함의: "저점 맞추기"보다 **무효화 조건(50주선 $76.5k, 200주선, 7월 저점 $57.8k)**을 기준으로 분할 대응하는 것이 합리적.

---

## 1. 현재 상태 요약 (2026-10-27)

| 항목 | 값 | 비고 |
|---|---|---|
| 사이클 고점 | $126,080~126,272 (2025-10-06) | 출처별 소폭 차이 |
| 2026 저점 | $57,718~57,950 (2026-07-01) | 고점 대비 약 -54% |
| 현재가 | 약 $80,000~84,000 | 10월 한 달 변동폭 6% 미만, 횡보 |
| 고점 대비 현재 낙폭 | 약 -33~34% | Glassnode/Bitbo |
| 저점 대비 반등 | 약 +40~49% | |
| 50주 이동평균 | 약 $76,540 | 5주 연속 상회 (Galaxy) |
| 200주 이동평균 | 약 $76~77k 추정 (현재가가 200주선 대비 +6%) | 최악 주봉 종가가 200주선 -4.7% |
| 실현가격(Realized Price) | $52k~61k (출처별 상이) | 평균 온체인 매입단가 |
| MVRV Z-score | 약 0.4 | 2022년 저점 때는 0 이하까지 하락 |
| 사이클 조정 MVRV 백분위 | 25.7% (10/18) | 역사적 "축적 구간" |
| FOMC | 10/28 (3.75~4.00% 동결 예상) | 유동성 제약 지속 |
| ETF 흐름 | 혼조 (10/22 -$635M 최대 유출, 이후 소폭 유입) | 누적 유입 약 $57.6B |

---

## 2. 반감기 사이클 날짜 분석 (직접 계산)

### 2-1. 사이클별 핵심 일수

| 사이클 | 반감기 | 고점 | 저점 | 반감기→고점 | 고점→저점 | 반감기→저점 | 낙폭 |
|---|---|---|---|---|---|---|---|
| 1 | 2012-11-28 | 2013-12-04 | 2015-01-14 | 371일 | **406일** | 777일 | -86% |
| 2 | 2016-07-09 | 2017-12-17 | 2018-12-15 | 526일 | **363일** | 889일 | -84% |
| 3 | 2020-05-11 | 2021-11-10 | 2022-11-21 | 548일 | **376일** | 924일 | -77% |
| 4 | 2024-04-20 | 2025-10-06 | 2026-07-01(?) | 534일 | **268일** | 802일 | -54% |

> 참고: 일부 보도(Galaxy)는 6/30 저점을 "반감기 후 916일"로 표현하나, 직접 계산하면 802일이다. 오늘(10/27)이 반감기 후 920일, 고점 후 386일이다.

### 2-2. 과거 패턴을 이번 사이클에 투영하면

| 기준 | 과거 범위 | 2026년 투영 창 |
|---|---|---|
| 고점→저점 363~406일 | | **2026-10-04 ~ 2026-11-16** |
| 반감기→저점 777~924일 | | 2026-06-06 ~ **2026-10-31** |
| 중간선거→저점 +13~+71일 | | **2026-11-16 ~ 2027-01-13** |

**핵심 관찰**
1. 고점→저점 기간으로 보면 7/1 저점(268일)은 역사상 가장 짧다. 과거 3번은 모두 1년(363~406일) 걸렸다. 이 기준으로는 **"진짜 저점 창은 바로 지금, 10월 초~11월 중순"**이다. 이것이 Cowen과 다수 사이클 분석가가 "10월 저점"을 부른 근거다.
2. 반감기→저점 기준으로는 7/1(802일)이 범위 안(777~924일)에 들어온다. 이 기준으로는 **저점이 이미 나왔어도 전혀 이상하지 않다.** 10/31이면 범위 상단을 벗어난다.
3. 반감기→고점은 534일로 2, 3사이클(526, 548일)과 거의 일치한다. 즉 **고점 타이밍은 사이클이 그대로 작동했다.** 깨진 것은 "저점까지 걸리는 시간과 깊이"뿐이다.

### 2-3. 낙폭 체감(Diminishing Drawdown) 추세
-86% → -84% → -77% → -54%. 매 사이클 얕아지는 추세의 연장선이며, 자산 성숙·ETF·기관 보유 구조와 일치한다. 다만 "얕은 낙폭 = 리셋 미완"이라는 반론(Galaxy 스스로도 언급)이 있다. 2022년 저점 때 MVRV Z-score가 0 이하로 떨어졌던 반면, 이번엔 최저가 0.4 부근이었다.

---

## 3. 중간선거 사이클 관점

### 3-1. 역사
| 중간선거 | BTC 저점 | 선거 후 일수 | 선거 전 6개월 수익률 |
|---|---|---|---|
| 2014-11-04 | 2015-01-14 | +71일 | - |
| 2018-11-06 | 2018-12-15 | +39일 | 약 -29% |
| 2022-11-08 | 2022-11-21 | +13일 | 약 -37% |
| 2026-11-03 | 2026-07-01(?) | **-125일** | 약 +25% (상승) |

### 3-2. 해석 두 가지
- **(A) 지연 단축 추세의 연장**: +71 → +39 → +13 → 다음은 음수가 자연스럽다. 시장이 학습해 선행 매수하는 현상(front-running)으로 설명 가능. 선거 전 6개월이 과거엔 급락 구간이었는데 이번엔 +25% 상승했다는 점 자체가 이미 패턴 이탈.
- **(B) 선거 자체가 원인이 아니다**: 과거 저점이 중간선거 직후였던 것은 단순히 "고점 후 약 1년"과 중간선거가 겹쳤기 때문(2017-12 고점, 2021-11 고점). 즉 중간선거는 **상관이지 인과가 아니다.** 따라서 선거 결과(상하원 구성, 암호화폐 규제 입법)는 변동성 재료지, 저점 결정 요인은 아니다.
- 다만 주식 쪽 중간선거 사이클(선거 전 약세, 선거 후 12개월 강세: 1950년 이후 중간선거 후 12개월 S&P500 전부 플러스)은 BTC에 "위험자산 베타"로 간접 영향을 준다. 2027년(대통령 임기 3년차)은 전통적으로 주식 최강 연도.

### 3-3. 중간선거 이후 재하락 시나리오가 성립하려면
- 11월~1월 사이 **$60k 하향 이탈** 필요(CoinDesk 지적). 이 경우 "고점 후 약 1년 + 선거 후 저점" 패턴이 동시에 복원됨.
- 일부 분석가 범위: 선거 후 $63.3k~74.8k 조정 (이 경우 7월 저점 미달 = 더블바텀 실패 아님 = "고가 저점"으로 오히려 강세 구조).

---

## 4. S2F(Stock-to-Flow) 모델 관점

### 4-1. 모델 상태
- 2024년 4월 반감기 이후 S2F 비율 약 120 (연간 신규 공급 약 164,250 BTC). 금(약 60)의 2배 희소성.
- PlanB 원모델 2024~2028 구간 예측 약 $288k(S2FX 기준) ~ $500k. **실제 고점 $126k → 모델 대비 약 1/2~1/4.** 2021 사이클($69k vs 모델 $100k+)에 이어 2연속 미달.
- 결론: **가격 수준 예측 도구로는 사실상 폐기.** 공급(stock)이 양변에 들어가는 회귀의 통계적 결함(spurious regression), 수요·거시 변수 부재가 원인.

### 4-2. 그래도 남는 것
- S2F의 "핵심 직관"인 **반감기 공급 충격 → 12~18개월 후 고점**은 이번에도 타이밍은 맞았다(534일). 즉 S2F는 "언제"에는 쓸만하고 "얼마"에는 쓸모없다.
- 공급 충격의 한계효용 체감: 반감기 때마다 신규 공급 감소분의 절대량이 작아져(2024: 일 900 → 450 BTC) 시총 대비 효과가 미미해지고, 대신 **ETF/기관 수요가 가격의 지배 변수**가 됐다. 이것이 낙폭 축소·사이클 평탄화의 구조적 배경.
- 저점 연구에서 S2F의 실무적 쓸모: 각 반감기 에포크의 **S2F 모델 하단(실현가격·생산원가와 비슷하게 움직임)**이 과거 저점 근처였다는 점 정도. 이번 에포크 하단은 대략 $50k 중반으로, CryptoQuant의 $55k 목표와 겹친다.

---

## 5. 온체인·기술적 저점 신호 점검표

| 신호 | 과거 저점 조건 | 2026 현재 | 판정 |
|---|---|---|---|
| 200주 이평 | 저점에서 터치/소폭 이탈 | 주봉 종가 최대 -4.7% 이탈 후 회복 | ✅ 충족 |
| 50주 이평 회복 | 저점 후 수개월 내 회복·유지 | 44주 하회 후 5주 연속 상회 | ✅ 충족 |
| MVRV Z-score | 0 이하 (2015/2018/2022 모두) | 최저 약 0.4, 미달 | ❌ 미충족 (핵심 반론) |
| MVRV 백분위 | 하위 20~30% | 25.7% | ✅ 축적 구간 |
| 실현가격 하회 | 저점 때 가격 < 실현가격 | 7월 저점 $57.8k vs 실현가 $52~61k | △ 출처 따라 간신히 터치 |
| 해시리본 / 채굴자 항복 | 저점 전후 발생 | 2025-11-29 반전, 2026-02 회복 | ✅ 종료 |
| 장기보유자(LTH) 분배 | 저점 후 LTH 매도 둔화 | 7/30~10/19 -345k BTC, 30일 -195k (둔화 중) | △ 진행 중 |
| 낙폭 | -77~-86% | -54% | ❌ 역사 대비 얕음 |
| 고점→저점 기간 | 363~406일 | 268일 | ❌ 역사 대비 짧음 |

요약: **가격·구조 신호는 저점 완성에 가깝고, 시간·깊이 신호는 미완.** 이 괴리가 바로 "두 번째 저점" 논쟁의 본질이다.

---

## 6. 주요 기관·분석가 입장 (2026-10 기준)

| 주체 | 입장 | 근거 | 무효화 조건 |
|---|---|---|---|
| Galaxy Research (Alex Thorn, 10/22~26) | **6월 저점 = 약세장 종료, 축적 단계** | 200주선 사수, 50주선 5주 회복, 반감기 후 저점 창 통과 | 50주선($76,540) 주봉 이탈 후 1개월 내 미회복 |
| Benjamin Cowen | 2월~8월: "10월 저점, $60k 재방문" → **9/21 철회** | 고점 후 1년 룰 | 반등 지속으로 스스로 철회 |
| CryptoQuant (상반기) | 10~12월 $55~60k "철바닥" | MVRV Z<0 필요 | Z-score 0 이하 미발생 시 미완 |
| NYDIG 계열 시나리오 | 하단 $38~39k | 유동성·수요 약화 | - |
| Mudrex 등 | 7월 저점 확정 확률 75% | 가격 구조 | $57.8k 이탈 |
| Coinbase Institutional / QCP (Q4) | $80~90k 박스, 유동성 제약 | ETF 혼조·Fed 매파 | 유동성 개선 |

---

## 7. 거시 요인

- **Fed**: 10/28 FOMC 3.75~4.00% 동결 전망. 국채금리 고공, 유가 상승 → 인플레 재부각. 금리 인상 가능성까지 일부 거론. 유동성 측면에서 BTC에 비우호적이며, "2차 저점" 시나리오의 최대 촉매는 **Fed 매파 선회 + ETF 지속 유출**.
- **ETF**: 10/19~21 +$1.08B, 10/22 -$635M(6월 이후 최대), 10/26 +$110M(IBIT 단독). 방향성 없음. ETF가 BTC의 약 8.5% 보유.
- **중간선거 결과 자체**: 암호화폐 규제·시장구조법 입법 속도에 영향. 선거 후 불확실성 해소는 전통적으로 위험자산 우호적.
- **주식 사이클**: 중간선거 후 12개월 S&P500 역사적 전승. BTC가 나스닥 베타를 유지한다면 2027년 상반기는 순풍.

---

## 8. 시나리오와 확률 (연구용 주관 추정)

| 시나리오 | 확률 | 경로 | 확인 신호 |
|---|---|---|---|
| **A. 저점 완료, 횡보 후 상승** | 35% | $76k 이상 유지, 2027 상반기 $100k 재도전 | 50주선 유지, ETF 순유입 전환, Z-score 1 이상 |
| **B. 선거 후 고가 저점(더블바텀 실패 없음)** | 25% | 11~12월 $63~75k 조정 후 반등. 7월 저점 미달 | $60k 사수, LTH 분배 종료 |
| **C. 선거 후 신저점(전통 패턴 복원)** | 30% | 12월~1월 $50~57k, MVRV Z<0 터치 | $60k 주봉 이탈, 200주선 이탈 |
| **D. 깊은 하락** | 10% | $38~48k, 거시 쇼크 | Fed 인상, 신용 이벤트 |

A+B(7월 저점이 사이클 최저점) ≈ 60%, C+D(신저점) ≈ 40%.

---

## 9. 연구자(주인님)를 위한 감시 체크리스트

1. **주봉 종가 $76,540(50주선)**: 이탈 후 4주 내 미회복 = Galaxy 테제 무효, 시나리오 C 확률 급등.
2. **$60,000 / 200주 이평**: 이탈 시 "고점 후 1년 + 선거 후 저점" 전통 패턴 복원.
3. **MVRV Z-score 0 이하**: 발생하면 역사적 "진짜 바닥" 조건 충족 → 최대 매수 구간.
4. **ETF 20일 누적 순흐름**: 연속 유출 2주 이상이면 수요 공백.
5. **LTH 공급 30일 변화율 플러스 전환**: 분배 종료 = 축적 전환 확인.
6. **해시레이트 신고가 회복**: 채굴자 건전성.
7. **FOMC 10/28, 12월**: 점도표·QT 종료 여부.
8. **중간선거 11/3 결과 + 시장구조법 진행**.
9. **달력**: 11/16(고점 후 406일), 1/13/2027(선거 후 71일)이 "역사적 저점 창"의 마지막 경계. 이 날짜를 신저점 없이 지나면 사이클 분석상 저점 확정으로 간주 가능.

---

## 10. 방법론적 주의

- 표본이 3~4개. 모든 "패턴"은 통계적으로 유의하지 않으며 서사(narrative)에 가깝다.
- 출처 간 수치 불일치(고점 $124~126k, 저점 $57.7~58.6k, 실현가 $52~61k). 본 보고서는 범위로 표기.
- 분석가 입장은 가격에 따라 바뀐다(Cowen 철회 사례). 입장보다 **무효화 조건**을 추적할 것.
- 이번 사이클의 구조 변화(ETF, 기업 재무, 국가 비축)는 과거 사이클과의 비교 가능성 자체를 낮춘다. 사이클 모델은 "참고 달력", 온체인·유동성은 "현재 상태", 두 개를 분리해 볼 것.

---

## 출처

- CoinDesk: https://www.coindesk.com/markets/2026/10/23/bitcoin-approaches-midterms-as-july-low-challenges-historical-cycle-pattern
- Yahoo Finance (중간선거 패턴): https://finance.yahoo.com/markets/crypto/articles/bitcoin-usually-bottoms-midterm-elections-000053376.html
- Yahoo Finance (고점 $126,080): https://finance.yahoo.com/markets/crypto/articles/bitcoin-peaked-126-080-october-091605452.html
- Benzinga (선거 후 매도 시나리오): https://www.benzinga.com/crypto/cryptocurrency/26/10/62617803/would-a-bitcoin-selloff-after-the-midterms-present-a-buying-opportunity
- CryptoBriefing (중간선거는 상관): https://cryptobriefing.com/bitcoin-midterm-cycle-bottom-history/
- Galaxy Research 보도: https://bitcoinmagazine.com/markets/bitcoins-bear-market-is-over-galaxy-says , https://cryptobriefing.com/galaxy-research-bitcoin-bear-market-ended/ , https://www.chaincatcher.com/en/article/2299184 , https://coincodex.com/article/94370/galaxy-research-proclaims-end-of-bitcoin-bear-market-says-its-time-to-buy-more-btc
- Cointelegraph / CryptoQuant $55k: https://cointelegraph.com/markets/bitcoin-analysis-sees-55k-btc-price-iron-bottom-by-december-2026
- CryptoQuant Quicktake: https://cryptoquant.com/insights/quicktake/6a4741c97a878621f52766d4-Bitcoin-MVRV-Z-Score-Falls-Below-2%CF%83-Valuation-Premium-Is-Cooling-Not-Collapsing
- Cowen 10월 저점 테제 / 철회: https://beincrypto.com/bitcoin-four-year-cycle-not-dead-benjamin-cowen/ , https://www.cryptotimes.io/2026/09/21/prominent-analysts-folds-bitcoin-price-rally-forces-cowen-to-scrap-october-bottom-call/
- Mudrex (저점 확률 75%): https://mudrex.com/learn/when-will-bitcoin-bottom-prediction/
- 21Shares: https://www.21shares.com/en-eu/insights/bitcoin-cycle-bottom-2026-entry-point
- CCN (반감기 달력): https://www.ccn.com/news/crypto/bitcoin-halving-cycle-2026-btc-crash-predictable/
- S2F: https://hoge.gg/bitcoin-stock-to-flow-model-critique-2026/ , https://theledgermind.com/bitcoin-stock-to-flow-model/ , https://charts.bitbo.io/stock-to-flow/ , https://intellectia.ai/blog/bitcoin-stock-to-flow-scarcity-2026
- 온체인: https://blog.amberdata.io/onchain-valuation-what-bitcoins-realized-price-says-about-2026 , https://crypto.news/price-prediction/bitcoin , https://charts.bitbo.io/mvrv-z-score/
- 채굴자 항복: https://www.coindesk.com/markets/2026/02/25/one-of-longest-mining-capitulations-nears-end-signaling-potential-btc-price-bottom , https://www.coindesk.com/markets/2026/01/19/btc-hashrate-drops-15-from-october-high-as-miner-capitulation-drags-into-almost-60-days
- LTH 분배: https://cryptobriefing.com/bitcoin-long-term-holders-selling-rally-signal/
- ETF/Fed: https://en.coin-turk.com/bitcoin-trades-near-82800-as-etf-outflows-and-fed-policy-shape-2026-outlook/ , https://www.tronweekly.com/fomc-decision-on-october-28-sets-up-major-test-for-bitcoin-and-ethereum/ , https://99bitcoins.com/news/bitcoin-btc/btc-usd-etf-flows-who-owns-bitcoin/
- 낙폭 통계: https://coincentral.com/bitcoin-drawdown-statistics-current-cycle-vs-past-cycles , https://openbitcoin.com/ath
