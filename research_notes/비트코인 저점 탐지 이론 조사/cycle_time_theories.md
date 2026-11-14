# Cycle-based and time-based theories of Bitcoin bear-market bottoms, and what they imply for 2025-2026

> Research date: 2026-11-14. Reference facts given by the coordinator: halving 2024-04-20; cycle high about $126,000 on 2025-10-06; lows 2026-02-06 (about $60,000) and 2026-07-01 (about $57,700); rally high about $87,000 on 2026-09-21; price now about $66,500.
>
> Source-quality notes that apply to every section:
> - Page fetching was blocked in this session (cointelegraph.com, galaxy.com, beincrypto.com, cryptoslate.com, cryptopotato.com, stocktwits.com, metatrader.com all failed DNS resolution in the sandbox). Every web finding below therefore comes from **search-result summaries of the linked pages, not from reading the full page**. Treat every quoted number as "secondary summary" unless marked LOCAL.
> - The web-search budget ran out before the last five queries (Cowen's October "Cycle Clock" memo text, CoinDesk Nov 13 live blog text, equity presidential-cycle statistics, ISM/DXY/Fed status, Cowen's 2014/2022 gap statistics). Those items are listed under Gaps.
> - Items marked **LOCAL** were computed by this researcher from the repository's own data files: `data/crypto/extra/BTC_BITSTAMP_1D.csv` (Bitstamp daily OHLC, 2011-08-18 to 2026-11-14) and `data/crypto/BTC_ONCHAIN.csv` (CoinMetrics price, realized price, MVRV, to 2026-11-13). These are measurements, not forecasts. "200-week MA" in LOCAL rows is a 1,400-day simple average of daily closes.

## 1. Halving / four-year cycle theories (days from halving, days from top, Rekt Capital, Cowen, Loukas, cycle translation)

### Takeaway
Every calendar rule built on the three prior cycles (top + 363 to 410 days, halving + 777 to 924 days, 513 to 542 days before the next halving, 13 to 71 days after the US midterm) pointed to a low between early October 2026 and mid-January 2027, and today (day 404 from the top, day 938 from the halving) sits at or past the end of most of those windows. The named cycle analysts have split: Loukas (since 2026-10-01) and Galaxy (2026-10-26) treat 2026-07-01 as the four-year-cycle low, while Cowen (July memo through 2026-11-09) and Rekt Capital (2026-08-20) still allow a Q4 low, with Rekt Capital's window ending 2026-12-31.

### Cited Findings

**Historical day counts (LOCAL measurements, Bitstamp intraday highs and lows)**

| Cycle | Halving | Top (high) | Low (low) | Halving to top | Top to low | Halving to low | Low to next halving | Drawdown |
|---|---|---|---|---|---|---|---|---|
| 2011 (pre-halving) | none | 2011-06-08, $29.03 close | 2011-11-18, $2.11 close | n/a | 163 d | n/a | 376 d | -92.7% (closing basis, CoinMetrics) |
| 2013-15 | 2012-11-28 | 2013-11-30, $1,163 | 2015-01-14, $152.40 | 367 d | 410 d | 777 d | 542 d | -86.9% |
| 2017-18 | 2016-07-09 | 2017-12-17, $19,666 | 2018-12-15, $3,122.28 | 526 d | 363 d | 889 d | 513 d | -84.1% |
| 2021-22 | 2020-05-11 | 2021-11-10, $69,000 | 2022-11-21, $15,479 | 548 d | 376 d | 924 d | 516 d | -77.6% |
| 2025-26 (so far) | 2024-04-20 | 2025-10-06, $126,272 | 2026-07-01, $57,734.63 | 534 d | 268 d | 802 d | about 656 d to an estimated April 2028 halving | -54.3% |

- Source for the table: [LOCAL: data/crypto/extra/BTC_BITSTAMP_1D.csv](/home/user/soxl-data/data/crypto/extra/BTC_BITSTAMP_1D.csv) and [LOCAL: data/crypto/BTC_ONCHAIN.csv](/home/user/soxl-data/data/crypto/BTC_ONCHAIN.csv). The coordinator's 406-day figure for 2013-15 uses a 2013-12-04 top on other exchanges; Bitstamp's own high was 2013-11-30, which gives 410 days.
- Published summaries agree on the range: "363 to 406 days for the three complete cycles", "360 to 410 days, average near 384 days", and Binance Research's "11 to 13 months from peak to bottom" — [Pintu Academy](https://pintu.co.id/en/academy/post/is-the-crypto-bear-market-over-2026); [Mudrex](https://mudrex.com/learn/when-will-bitcoin-bear-market-end/)
- One cycle-length model put the bottom between 2026-10-04 and 2026-10-17 (this equals top + 363 and top + 376 days) — [NewsBTC via cryptonewsnavigator](https://www.cryptonewsnavigator.com/news/newsbtc/bitcoin-correction-timeline-analyst-predicts-potential-bottom-in-october-2026-56353366)
- A "91-day window" framing (July to early October 2026) said Bitcoin had entered the same window that ended each of the last three bear markets, and attached a regression-model bottom near $47,000 — [BeInCrypto via Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/bitcoin-bear-market-may-end-134412151.html)
- Alphractal: the lowest price of this cycle so far was on 2026-06-30, "just 267 days after the peak" — [Cryptonews.net](https://cryptonews.net/news/bitcoin/33660705/)
- DC Forecasts (about 2026-11-09): Bitcoin closed at $74,754 on 2026-11-08, which was 398 days after the October 2025 high and 40.1% below the peak — [DC Forecasts](https://www.dcforecasts.com/analysis/bitcoin-bear-market-drawdowns-shrink-three-cycles/)
- Korean coverage: CryptoQuant said post-halving lows cluster in September to November and expected a low in the second half of 2026 — [블록미디어](https://www.blockmedia.co.kr/archives/1052687). On-chain firms and analysts expected Q4 2026, slipping to Q1 2027 if recession or regulation shocks pile up (2026-08-04) — [디지털투데이](https://www.digitaltoday.co.kr/news/articleView.html?idxno=689784). Mudrex's most likely window was October to December 2026 at $50,000 to $55,000 — [Mudrex](https://mudrex.com/learn/when-will-bitcoin-bottom-prediction/)

**US midterm-year rule**
- CoinDesk (2026-10-23): prior lows came in January 2015, December 2018 and November 2022, about 71, 38 and 13 days after the midterm election. The 2026 low of $57,850 on 2026-07-01 came 125 days before the 2026-11-03 vote, and Bitcoin had recovered about 40% to roughly $81,455 by 2026-10-22 — [CoinDesk](https://www.coindesk.com/markets/2026/10/23/bitcoin-approaches-midterms-as-july-low-challenges-historical-cycle-pattern)
- Same article: QQQ fell about 23% from end-September to its December 2018 low and fell 17% in the three months before the 2022 vote, but rose 17% in the six months before the 2014 midterm. CoinDesk's conclusion was that Bitcoin's midterm weakness is tied to its own cycle more than to elections — [CoinDesk](https://www.coindesk.com/markets/2026/10/23/bitcoin-approaches-midterms-as-july-low-challenges-historical-cycle-pattern)

**Benjamin Cowen (Into The Cryptoverse)**
- Rule: post-halving year is the top, midterm year is the bear year, and the low comes about a year after the top. His base case (stated late 2025 and repeated in early 2026) was October 2026, citing the December 2018 and November 2022 lows — [BeInCrypto](https://beincrypto.com/bitcoin-bear-market-bottom-benjamin-cowen-prediction); [CoinTurk](https://en.coin-turk.com/bitcoin-projected-to-bottom-in-october-2026-says-benjamin-cowen/)
- February 2026: his best guess was a low in June, a counter-trend rally, then another low in October. A low as early as May would need far larger selling than a typical midterm year. His test is whether the year-to-date return stays within one standard deviation of the 2014/2018/2022 midterm-year average — [The Welsh Bull newsletter](https://thewelshbull.beehiiv.com/p/bitcoin-is-in-denial-the-data-agrees); [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/bitcoin-price-bottom-benjamin-cowen-223000084.html)
- 2026-04-17 (Korean coverage): Cowen still saw the trough in autumn 2026 — [네이트 뉴스](https://m.news.nate.com/view/20260417n00333)
- 2026-07-01: Cowen called an "accumulation phase". Seven weeks later the July low was still holding, but he kept a "decent chance" of one more leg down in Q4 with a floor near $44,000 if prior midterm years repeat. He also said Bitcoin has historically put in three lows in a midterm year: February, summer and Q4 — [BeInCrypto](https://beincrypto.com/cowen-bitcoin-cycle-accumulation-stage/); [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/benjamin-cowen-midterm-cycle-thesis-082004321.html)
- July 2026 memo: Q4 2026 bottom, with a seasonal "midterm decay" floor near $44,000 that coverage calls illustrative. Related numbers quoted: logarithmic Fibonacci midpoint $44,428, 200-week SMA near $63,100, 50-week SMA near $86,500 as the confirmation level (two consecutive weekly closes above it), MVRV Z-Score 0.395 against below-zero readings at prior bottoms. Cowen wrote that the low was "most likely a matter of months rather than weeks away" — [BeInCrypto](https://beincrypto.com/benjamin-cowen-memo-q4-bitcoin-bottom/); [BlockWeeks](https://paragraph.com/@blockweeks/benjamin-cowen-%E6%9C%80%E6%96%B0%E6%8A%A5%E5%91%8A%EF%BC%9A%E6%AF%94%E7%89%B9%E5%B8%81-q4-%E5%BA%95%E9%83%A8%E6%88%96%E5%9C%A8-44000-%E7%BE%8Eyuan%E9%99%84%E8%BF%91-%E5%8C%BA%E5%9D%97%E5%91%A8%E5%88%8Ablockweeks); [BigGo Finance](https://finance.biggo.com/news/51312e7f-ae15-40e8-9ba1-0a3dbaf34f0e)
- October 2026: Cowen warned the rally above $80,000 could "wreck a lot of people" and might be a fakeout. His thesis assumed rising energy prices, yields and the dollar would push Bitcoin into a Q4 low — [Benzinga](https://www.benzinga.com/crypto/cryptocurrency/26/10/62261331/bitcoins-rally-above-80000-could-wreck-a-lot-of-people-analyst-warns)
- October 2026 memo "Bitcoin and the Cycle Clock" exists on his site and cites weekly closes of $82,002 (2026-10-18) and $80,048 (2026-10-25) — [benjamincowen.com](https://benjamincowen.com/reports/bitcoin-and-the-cycle-clock-october-2026)
- About 2026-11-09: Cowen tied the expected bottom to an equity correction and warned of a retest of the July lows using a late-2018 parallel: "If Nasdaq can test its July lows, why can't Bitcoin?" — [Bitcoin.com News](https://news.bitcoin.com/price-predictions/benjamin-cowen-bitcoin-q4-stock-correction/); [BigGo Finance](https://finance.biggo.com/news/17258aba-360a-4a05-8223-bc35ee4f0bfc)
- Cowen expects the midterm-year weakness to have played out by 2027 whether or not a new low prints, and expects a new bull run in 2027 — [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/benjamin-cowen-midterm-cycle-thesis-082004321.html)

**Rekt Capital**
- Late 2025 framing: 2025 peak year, 2026 full bear market, bottoming period in 2027 — [Yellow.com](https://yellow.com/news/bitcoin-eyes-dollar93000-recovery-before-2026-bear-market-top-analyst-predicts)
- June 2026 (X): the 2022 bottom was 22% below the 2017 all-time high, while 2026 had so far gone only 10.5% below the 2021 high. "Bitcoin is getting close to a bottom but it's not" there yet — [Rekt Capital on X](https://x.com/rektcapital/status/2062785677406646467)
- 2026-06-30: resistance at $66,000 and potential drop toward the $45,000 band — [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/bitcoin-bulls-bears-agree-bottom-142029883.html)
- 2026-07-03 video: about 270 days past the peak against roughly 365 days in prior bear markets; he called the range "yet another redistribution range" — [The Daily Hodl](https://dailyhodl.com/2026/07/03/analyst-says-bitcoin-not-quite-near-bottom-warns-btc-has-room-for-further-downside-if-history-repeats/amp/)
- 2026-08-20 (X, via secondary): by four-year-cycle tendencies Bitcoin "could have the time until the 31st of December 2026 to perform a Bear Market low" — [Bloomingbit](https://en.bloomingbit.io/feed/news/115578); [Bitget News](https://www.bitget.com/news/detail/12560605489361)
- Undated 2026 X post: the bear cycle has produced "macro price action clusters" with fake breakouts; if the bottom is in, Bitcoin "will need to sustain itself at these highs" — [Rekt Capital on X](https://x.com/rektcapital/status/2090434463742230791)

**Bob Loukas (4-year cycle, weekly cycle, 60-day cycle)**
- Method: Bitcoin tends to form a price low roughly every 60 days; these 60-day cycles nest inside the four-year cycle, which he treats as a multi-year framework, and he also posits a 16-year cycle — [Kitco](https://www.kitco.com/opinion/2025-06-10/bitcoins-surprise-pump-60-day-cycle-theory-and-why-final-bullish-phase-may-be); [Metaverse Post profile](https://mpost.io/people/bob-loukas-cycle-trader-founder-of-bitcoin-live/)
- Translation: a left-translated cycle peaks before its midpoint (before day 30 of a 60-day cycle) and is followed by weakness; a right-translated cycle peaks after the midpoint and signals strength — [Whaleportal](https://whaleportal.com/blog/bitcoin-60-day-cycle-explained/)
- 2026-06-04 update: Bitcoin was in month 43 of the four-year cycle; prior cycle lows formed at months 47 to 48. Base case was a cycle low in October to November 2026 (December possible), with about 25% probability for a bullish double-bottom scenario. He named $53,000 as the "cycle midpoint", about a 57% decline, and said "There's generally always a lower low, at least one lower low, if not a second lower low." The article's headline places the next cycle high in 2028 — [Cointelegraph](https://cointelegraph.com/news/bitcoin-normal-four-year-cycle-puts-focus-on-53k-low-before-2028-btc-price-high); [NewsBTC via TradingView](https://www.tradingview.com/news/newsbtc:6a2b391c7094b:0-veteran-analyst-eyes-53-000-bitcoin-as-final-cycle-stage-begins/)
- 2026-10-01: "the slightly early Cycle Low (44 months vs 47), and lack of deeper move in June/July sets up a possibility of a Cycle that could well (upside) surprise" — [Gokhshtein](https://gokhshtein.com/news/2026-10-01-bob-loukas-says-bitcoin-cycle-factors-are-now-confirmed)
- 2026-10-21: Bitcoin "appears to be confirming the new cycle"; upside window of 30 to 45 days; $79,600 is the level below which a "highly defensive posture" is needed — [Gokhshtein](https://gokhshtein.com/news/2026-10-21-bob-loukas-says-bitcoin-cycle-confirmed-sets-79600); [TokenPost](https://www.tokenpost.com/news/investing/38378)
- 2026-11-09 (X, via secondary): Bitcoin is showing a cycle top (he cited week 14 or 20 price action), the declining part of the cycle has taken control, and he expects weakness into January, "within the context of 4yr cycle having already found bottom". A close above $82,000 would change his bias — [Gokhshtein](https://gokhshtein.com/news/2026-11-09-bob-loukas-calls-bitcoin-cycle-top-forecasts-weakness-into)

**Galaxy Research (cycle clock)**
- June 2026 report: the four-year cycle "remains valid, but its amplitude has narrowed"; the cycle clock's bear-low window does not open until late 2026; base-case floor $40,000 to $46,000, severe case $30,000 to $37,000; only 4 of 13 historical bottom indicators had triggered — [Galaxy Research](https://galaxy.com/insights/research/bitcoin-four-year-cycle-where-is-the-bottom); [Blockonomi](https://blockonomi.com/galaxy-research-says-bitcoin-bottom-is-not-in-projects-40k-46k-base-case-floor-by-late-2026); [crypto.news](https://crypto.news/bitcoin-cycle-data-points-to-40k-46k-bottom-galaxy-says/)
- 2026-10-26 report (Alex Thorn): the bear market bottomed on 2026-06-30 and Bitcoin is in accumulation; "now is an attractive time to buy and hold bitcoin". Invalidation is a weekly close below the 50-week moving average of $76,540 that is not recovered within a month — [The Block](https://www.theblock.co/news/markets/2026-10-26-galaxy-says-bitcoin-bear-market-is-over-now-is-the-time-to-buy-and-hold-431720); [Decrypt](https://decrypt.co/381786/bitcoin-bear-market-is-over-galaxy-research-says)

### Inferences
- Projected windows for this cycle from the LOCAL table (arithmetic only): top + 363/376/406/410 days = 2026-10-04 / 10-17 / 11-16 / 11-20. Halving + 777/889/924 days = 2026-06-06 / 09-26 / 10-31. An estimated April 2028 halving minus 542/516/513 days = about 2026-10-23 / 11-18 / 11-21 (the halving date is this researcher's 10-minute-block estimate of 2028-04-17). Election day + 13/39/71 days = 2026-11-16 / 12-12 / 2027-01-13.
- The 2026-07-01 low fits the halving-to-low range (802 days, inside 777 to 924) but not the top-to-low range (268 days against 363 to 410). Today is day 938 from the halving, so any new low from here would be the longest halving-to-low interval on record.
- Loukas's "44 months" is measured from the 2022-11-21 low; 2026-07-01 is 43.3 months and 2026-11-14 is 47.8 months after it. His 2026-11-09 "cycle top" most plausibly refers to the weekly (intermediate) cycle that began at the July low, since 2026-11-09 is week 18.7 from 2026-07-01 and he cited "week 14 or 20". On that reading his call is a higher low around January 2027, not a new four-year-cycle low.
- Two stated tripwires have already fired in the LOCAL data. Loukas's $79,600 level was lost on a closing basis on 2026-10-29 (close $77,792.67). Galaxy's 50-week level of $76,540 was lost on the weekly close of 2026-11-08 ($74,742.52), which starts Galaxy's one-month recovery clock (to about 2026-12-08).
- Rekt Capital's depth rule applied to this cycle: 22% below the $69,000 2021 high is about $53,800. The July low was 16.3% below it.
- Cowen's "three lows in a midterm year" maps onto 2026-02-06, 2026-07-01 and a still-open Q4 slot. The current decline from $87,374 (2026-09-21) to $66,397 (2026-11-14) is the candidate for that third low.

### Gaps
- Cowen's October 2026 "Cycle Clock" memo and his November statements could not be read in full (search budget exhausted, fetch blocked). No statement dated after about 2026-11-09 was found.
- No Rekt Capital statement dated after August 2026 was found. His well-known "phases" (pre-halving rally, re-accumulation, parabolic phase, bear market) and his halving-distance statistics could not be sourced in this session.
- Loukas's own videos/posts were not readable; all 2026 quotes are from secondary sites (Cointelegraph, NewsBTC, Gokhshtein, TokenPost). The Cointelegraph summary's phrase "10% either side of week 46" looks garbled (his counts are normally in months). His weekly-cycle length and "failed cycle" definition were not found in a primary source.
- The 2011 bottom predates the first halving, so halving-based rules have only three completed observations.

## 2. Valuation-band models (power law, S2F, rainbow / log regression, 200-week and 300-week MA, realized price, diminishing drawdowns)

### Takeaway
At about $66,500 Bitcoin is sitting on the two most-watched floors at once: the 200-week MA (about $68,000, just lost on 2026-11-13) and the power-law support line (about $65,000 to $66,700 today and rising to $68,000 to $69,500 by year-end), while realized price ($53,800) and the 300-week MA ($57,800) are 13% to 19% lower. Models that extrapolate past drawdowns (60% to 70%) or midterm seasonality give $38,000 to $50,000, a zone the price has not approached.

### Cited Findings

**Floor levels as of 2026-11-14**

| Model | Floor / level now | Basis |
|---|---|---|
| 200-week MA | $67,983 (LOCAL, week ending 2026-11-15); press: "around $68,000", "$67,992" | [LOCAL](/home/user/soxl-data/data/crypto/extra/BTC_BITSTAMP_1D.csv); [CoinDesk](https://www.coindesk.com/tech/2026/11/13/live-news-bitcoin-drops-below-200-week-moving-average-as-dollar-strength-pressures-risk-assets); [AltcoinBuzz](https://www.altcoinbuzz.io/bitcoin-breaks-below-200-week-average-as-etf-outflows-and-liquidations-grow) |
| 300-week MA | $57,774 (LOCAL) | [LOCAL](/home/user/soxl-data/data/crypto/extra/BTC_BITSTAMP_1D.csv) |
| Realized price | $53,762 on 2026-11-13, MVRV 1.27 (LOCAL, CoinMetrics); Ki Young Ju said about $54,000 on 2026-10-21 | [LOCAL](/home/user/soxl-data/data/crypto/BTC_ONCHAIN.csv); [TokenPost](https://www.tokenpost.com/news/investing/36786) |
| Power-law floor, Newhedge fit | $51,128 in February 2026; projected $64,400 by late October and $68,000 by year-end 2026 | [CryptoSlate](https://cryptoslate.com/if-bitcoin-stays-near-67k-it-breaks-the-power-law-floor-by-mid-december/); [Threads summary](https://www.threads.com/@100xwithnavi/post/DVARYMZEvmK/bitcoin-near-67k-risks-power-law-break-floor-at-68k-year-end) |
| Power-law support, Bitbo fit | End-2026: support $69,500, fair value $198,700, resistance $615,000 (which page carried the Bitbo figures is uncertain) | [Kucoin news](https://www.kucoin.com/news/flash/bitcoin-power-law-predicts-btc-to-cross-100-000-by-2028); [CryptoRank](https://cryptorank.io/news/feed/8927e-bitcoin-power-law-2026-2030-when-will-btc-permanently-clear-100000) |
| Power-law support, Fidelity (Timmer) | About $58,000 in mid-July 2026 with price near $62,700 | [crypto.news](https://crypto.news/bitcoin-price-nears-fidelitys-power-law-support-accumulation-zone-or-missing-catalyst/); [Blockstream Media](https://blockstreammedia.com/2026/07/14/bitcoin-nears-power-law-support-line-fidelity-has-tracked-since-2015/) |
| Rainbow chart | 2026-11-12: close $71,288 in the "Green" band of $57,233 to $90,708; midline $143,762 | [Cryptoticker](https://cryptoticker.io/en/bitcoin-rainbow-chart-explained/) |
| Diminishing-drawdown extrapolation | 60% to 70% drawdown; Terpin's best estimate 66%, about $42,000, range $39,000 to $55,000 | [Mudrex](https://mudrex.com/learn/when-will-bitcoin-bottom-prediction/) |
| Cowen midterm seasonal floor | About $44,000 (illustrative), log-Fib midpoint $44,428 | [BeInCrypto](https://beincrypto.com/benjamin-cowen-memo-q4-bitcoin-bottom/) |
| Galaxy 13-indicator study (June 2026, superseded 2026-10-26) | Base $40,000 to $46,000; severe $30,000 to $37,000 | [Blockonomi](https://blockonomi.com/galaxy-research-says-bitcoin-bottom-is-not-in-projects-40k-46k-base-case-floor-by-late-2026) |
| Loukas cycle midpoint | $53,000 | [Cointelegraph](https://cointelegraph.com/news/bitcoin-normal-four-year-cycle-puts-focus-on-53k-low-before-2028-btc-price-high) |
| Glassnode cost-basis cluster | $62,000 to $66,000 | [AltcoinBuzz](https://www.altcoinbuzz.io/bitcoin-breaks-below-200-week-average-as-etf-outflows-and-liquidations-grow) |

**Power law (Giovanni Santostasi; variants by Harold Burger/porkopolis, Bitbo, Newhedge, Fidelity)**
- Rule: price follows a power law of time since the genesis block on a log-log chart; the lower band is a fixed offset below the fitted line. Coverage describes the floor as about intercept minus 0.6 in log terms, and Santostasi also publishes a hashrate-based floor — [BIT Knowledge Hub](https://www.bit.com/knowledge-hub/bitcoin-power-law)
- CryptoSlate (about 2026-02-22): if Bitcoin stays flat near $67,000 the rising floor "catches it by mid-December"; the floor enters the mid-$60,000s by late October. The author says the model is not a prophecy, and a break would invalidate a specific parameterization (site, bands, data source), not Bitcoin — [CryptoSlate](https://cryptoslate.com/if-bitcoin-stays-near-67k-it-breaks-the-power-law-floor-by-mid-december/); [CryptoSlate, ETF-era test](https://cryptoslate.com/bitcoins-power-law-model-faces-its-biggest-test-yet-as-etf-flows-challenge-the-curve/)
- Different fits disagree: floors near $51,000, $56,488 and $58,000 were all quoted for mid-2026 — [crypto.news](https://crypto.news/bitcoin-price-nears-fidelitys-power-law-support-accumulation-zone-or-missing-catalyst/)
- Timmer (2026-07-14): the support line has coincided with major bottoms since 2015, Bitcoin can sit near it for months, and it is a valuation framework, not a timing tool — [Blockstream Media](https://blockstreammedia.com/2026/07/14/bitcoin-nears-power-law-support-line-fidelity-has-tracked-since-2015/)
- Timmer (August 2026, X): "Bitcoin has held the floor of its power law curve and has now corrected long enough to satisfy the time element of its mild 4-year cycle winter." — [Jurrien Timmer on X](https://x.com/TimmerFidelity/status/2093468417802084800)
- Timmer (about late September 2026): a new cyclical bull market is under way after Bitcoin held $60,000, his "line in the sand"; target $300,000 by 2029; a power-law line value of $81,218 was quoted for 2026-09-20 — [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/fidelity-macro-chief-jurrien-timmer-142523323.html)
- Timmer (January 2026, X): Bitcoin "is following the internet S-curve a lot closer now than the power law curve" — [Jurrien Timmer on X](https://x.com/TimmerFidelity/status/2009641313378136363)
- An earlier Fidelity model framed the 2026 downside as $56,000 or $29,000 — [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/bitcoin-price-56k-29k-fidelity-114215468.html)
- BIT research (2026-10-19): Bitcoin trades 40% to 50% below the power-law trend but above the floor — [BIT research](https://www.bit.com/es/research/Has-Bitcoin-Bear-Market-Run-Its-Course)

**PlanB (stock-to-flow, 200-week MA, realized price)**
- October 2025 (X): PlanB called the idea that $126,000 was the top and 2026 would be a bear market "a BIG misunderstanding" — [PlanB on X](https://x.com/100trillionUSD/status/1980259495902109832)
- February 2026: four scenarios. (1) 80% drop to about $25,000; (2) bottom near the 200-week MA and realized price, $50,000 to $60,000; (3) shallow bear near the prior all-time high, about $70,000; (4) local bottom already in at about $72,900 — [NewsBTC via TradingView](https://www.tradingview.com/news/newsbtc:db857a3e5094b:0-planb-lays-out-four-bitcoin-bear-market-scenarios/); [Bitbo](https://bitbo.io/news/planb-bitcoin-bear-scenarios/)
- June 2026: "50/50 on if February $60k was the bottom, or the bear will continue"; he then said Bitcoin would "likely bottom below" realized price (about $53,000) because all previous bear bottoms were below it. He also said "Stock to flow says nothing about tops and bottoms" while keeping a roughly $500,000 average ($250,000 to $1,000,000) for 2026 to 2028 — [Cointelegraph](https://cointelegraph.com/markets/bitcoin-is-just-a-5k-drop-away-from-its-best-investment-opportunity-analysis); [Bitcoin Foundation news](https://bitcoinfoundation.org/news/bitcoin/bitcoin-price-drop-below-53k/)
- A call tracker scores the "below realized price" argument as failed after the 2026-07-01 low of about $58,500 — [BuyCrypt tracker](https://buycrypt.com/traders/planb/)

**Track record of the moving-average and realized-price floors (LOCAL measurements)**

| Bottom | Low vs 200-week MA | Days closing below 200-week MA | Minimum MVRV (price / realized price) | Days with MVRV below 1 |
|---|---|---|---|---|
| 2011-11 | not measurable (insufficient history) | n/a | 0.387 (2011-10-19) | 152 |
| 2015-01 | 0.91x (CoinMetrics closes, short history) | 31 (January and August to September 2015) | 0.564 (2015-01-14) | 304 |
| 2018-12 | 0.986x (touch) | 0 on Bitstamp closes | 0.690 (2018-12-15) | 134 |
| 2020-03 (COVID) | 0.70x | 6 | 0.877 | 6 |
| 2022-11 | 0.645x | 317 (2022-06-14 to 2023-10-15, non-contiguous) | 0.754 (2022-11-09) | 179 |
| 2026 (to date) | 0.924x on 2026-07-01 | 27 (11 in June, 6 in July, 9 in August, 1 in November) | 1.103 (2026-06-30) | 0 |

- Source: [LOCAL: BTC_BITSTAMP_1D.csv](/home/user/soxl-data/data/crypto/extra/BTC_BITSTAMP_1D.csv) and [LOCAL: BTC_ONCHAIN.csv](/home/user/soxl-data/data/crypto/BTC_ONCHAIN.csv)
- Press descriptions match: the 200-week MA marked the 2015 and 2018 lows, and in 2022 the price spent roughly 16 months around or below it — [TradeWize](https://tradewize.io/blog/bitcoin-200-week-moving-average)
- Galaxy (2026-10-26) presents the fact that market value stayed above realized value as a first for any bear market and as evidence of a shallower cycle (53% drawdown against 93%, 85%, 84%, 77%) — [Decrypt](https://decrypt.co/381786/bitcoin-bear-market-is-over-galaxy-research-says)
- A realized-price argument that more downside is needed because price never touched realized price — [Blockonomi](https://blockonomi.com/has-bitcoin-finally-bottomed-realized-price-theory-points-to-more-downside-ahead/)

**Rainbow / log regression**
- The rainbow chart fits a logarithmic regression and splits it into fixed-multiple bands; Blockchaincenter states there is "no scientific basis" for it — [Blockchaincenter](https://www.blockchaincenter.net/bitcoin-rainbow-chart/); [Cryptoticker](https://cryptoticker.io/en/bitcoin-rainbow-chart-explained/)
- A Finbold-style piece said the rainbow chart "is warning BTC could crash below $60,000 in November" 2026 — [Cryptonews.net](https://cryptonews.net/news/bitcoin/33619547/)

**Diminishing drawdowns**
- Series quoted: 94%, 87%, 84%, 77%, then "potentially 50% to 60%" this cycle; Wintermute's version is 83%, 77%, 50% — [Kucoin news](https://www.kucoin.com/news/flash/bitcoin-drawdowns-shrink-recovery-speeds-up-in-2026-cycle); [DC Forecasts](https://www.dcforecasts.com/analysis/bitcoin-bear-market-drawdowns-shrink-three-cycles/)
- A 2026-06-29 note warned of a 75% drawdown with four months of bear market still ahead — [TMGM](https://www.tmgm.com/en/analysis/market-news/article/bitcoin-four-year-cycle-btc-risks-75-drawdown-with-four-months-of-bear-market-still-ahead-202606291041)

### Inferences
- Scaling the cited power-law floors with a 5.7 to 5.9 time exponent (this researcher's arithmetic, not a published figure) gives for 2026-11-14: Newhedge fit about $65,000, Bitbo fit about $66,700, Fidelity fit about $64,800. For 2026-12-31: $67,800, $69,500, $67,500. For 2027-03-31: about $73,400, $75,200, $73,100. For 2027-06-30: about $79,400, $81,400, $79,000. Fair value on the Bitbo fit is about $190,600 today, so price is about 0.35x fair value.
- The same scaling puts the floor on 2026-07-01 at about $57,300 to $59,000, so the $57,735 July low was a touch (Newhedge, Fidelity fits) or a 2% pierce (Bitbo fit) of the power-law floor. The CryptoSlate "flat at $67,000 meets the floor in mid-December" scenario is now live about a month early because price fell to the floor instead of waiting for it.
- Because the floor rises about 2.7% per month (roughly $2,800 between now and year-end), a sideways market at $66,500 is already at the Bitbo-fit support and would cross below the Newhedge-fit floor in about three to four weeks (around 2026-12-09). Per CryptoSlate's caveat, a break tests a parameterization, not Bitcoin.
- Drawdown arithmetic from the $126,272 high: 60% = $50,500; 65% = $44,200; 66% = $42,900; 70% = $37,900; 77% = $29,000. The realized-price rule (all prior lows at MVRV 0.39 to 0.75) would imply $21,000 to $40,000 at today's realized price, which no 2026 forecaster found in this search is calling for except PlanB's and Galaxy's tail scenarios.
- The ordering of supports below price is: Glassnode cluster $62,000 to $66,000, February and July lows $59,930 and $57,735, 300-week MA $57,774, realized price $53,762, Loukas $53,000, then the $44,000 to $46,000 cluster (Cowen seasonal, Galaxy June base case, Terpin, 65% drawdown).

### Gaps
- No live, primary 2026 reading was obtained from Santostasi himself, porkopolis, bitbo.io charts or newhedge (fetch blocked). The floor values for today are this researcher's extrapolation from two cited anchor points.
- Stock-to-flow: no 2026 "floor" value was found; PlanB himself says the model gives no bottoms. The model's 2021-2022 and 2025 misses are widely discussed but were not sourced in this session.
- Cowen's logarithmic-regression "fair value" band level for late 2026: not found. Trolololo regression value for late 2026: not found. Rainbow band values differ between Cryptoticker, CoinCodex, Coinank and Blockchaincenter, and the Cryptoticker page is internally inconsistent ($140,000 vs $143,762 midline).
- The 300-week MA has little published track record; the LOCAL data show the 2022 low at 0.86x the 300-week MA and the 2018 low at 1.40x, so it has not acted as a consistent floor.
- "Diminishing drawdowns" rests on four observations and the fitted "trendline" value for this cycle varies by author (50% to 70%).

## 3. Macro-liquidity cycle theories (global liquidity / M2, Howell's 65-month cycle, ISM, dollar, Fed, presidential cycle)

### Takeaway
The macro-liquidity camp gives the latest bottom timing of any school: Michael Howell places the trough of his 65-month global liquidity cycle around mid-2027 to the second half of 2027 and does not expect Bitcoin strength before then. Raoul Pal's liquidity/ISM thesis predicted a stretched cycle peaking in Q2 2026, which did not happen, and no late-2026 revision from him was found.

### Cited Findings
- Howell's rule: global liquidity moves in a roughly 65-month cycle driven by debt-refinancing needs (tied to the average maturity of global debt). He argues this explains Bitcoin's rhythm better than the halving, and that Bitcoin tracks wholesale financial-market liquidity, not conventional M2 — [Bankless](https://www.bankless.com/podcast/the-real-crypto-cycle-what-happens-when-global-liquidity-peaks-michael-howell); [Capital Wars](https://capitalwars.substack.com/p/bitcoin-and-global-liquidity)
- Peak timing: sources differ. One interview write-up says the cycle peaked in Q3 2025; others say the turn of 2025/2026 or early 2026 (reaffirmed in a 2026-03-29 interview). A TFTC piece is titled "Global Liquidity Peaked at $189T" — [51 Insights](https://51insights.substack.com/p/liquidity-debt-and-bitcoin-cycle); [TFTC](https://www.tftc.io/global-liquidity-peak-189-trillion-michael-howell-crossborder-capital); [What Bitcoin Did](https://www.whatbitcoindid.com/episodes/wbd1048-michaelhowell)
- Trough timing: "should bottom around the middle of 2027", and in another write-up "may not bottom until the second half of 2027". Howell said 2026 would not be a big year for Bitcoin and expected a higher 30-year yield — [Stocktwits](https://stocktwits.com/news-articles/markets/cryptocurrency/michael-howell-bitcoin-2026-outlook-30-year-yield/cZYQe8bRJVn); [51 Insights](https://51insights.substack.com/p/liquidity-debt-and-bitcoin-cycle)
- One article with Bitcoin at about $66,000 (down 47% from about $126,000) says Howell expects the downswing to last through 2027; he calls Bitcoin the most liquidity-sensitive major asset — [51 Insights](https://51insights.substack.com/p/liquidity-debt-and-bitcoin-cycle); [Capital Wars, "What Is Bitcoin Telling Us?"](https://capitalwars.substack.com/p/what-is-bitcoin-telling-us)
- The Foundation for the Study of Cycles reports independently confirming a 65-month periodicity — [Lars von Thienen / cycles.org](https://lars.cycles.org/p/global-liquidity-bitcoin-cycles-michael-howell-lars-von-thienen)
- Cointelegraph's caveat: if debt pressure forces central banks to inject liquidity, the outcome could differ — [Cointelegraph](https://cointelegraph.com/markets/bitcoin-tradfi-cycles-set-to-collide-in-2026-good-or-bad)
- Raoul Pal's rule: Bitcoin is about 90% correlated with global M2 (later stated as 85% to 87% with global liquidity). He argued the four-year cycle had stretched to five years because of a weak ISM and longer Treasury maturities, with the most likely peak in Q2 2026, and he uses ISM above 50 as the altcoin-rotation signal — [The Crypto Basic](https://thecryptobasic.com/2025/09/25/raoul-pal-says-this-is-a-5-year-market-cycle-heres-the-exact-time-bitcoin-will-peak/); [Bitget News](https://www.bitget.com/news/detail/12560604994697)
- Pal (May 2026): odds of a "supercycle" had risen; a $450,000 target depends on central banks injecting liquidity by the end of 2026 — [Bitcoin.com News](https://news.bitcoin.com/raoul-pal-bitcoin-supercycle-2026/)
- Arthur Hayes ("Long Live the King!", October 2025): the 2014, 2018 and 2022 bear markets were caused by monetary tightening, not the halving calendar; US dollar and Chinese yuan liquidity set the price; he said a crash was off the table and "the meat of the bull market is going to happen in mid 2026 to mid 2027" — [CoinDesk](https://www.coindesk.com/markets/2025/10/09/bitcoin-crash-off-the-table-as-four-year-cycle-is-dead-arthur-hayes); [Coinage](https://www.coinage.media/s4/why-arthur-hayes-is-confident-the-fed-just-set-up-new-bitcoin-highs-in-2026)
- Cowen's macro link (October to November 2026): rising energy prices, yields and the dollar push Bitcoin into a Q4 low, and the low is tied to an equity correction — [Benzinga](https://www.benzinga.com/crypto/cryptocurrency/26/10/62261331/bitcoins-rally-above-80000-could-wreck-a-lot-of-people-analyst-warns); [Bitcoin.com News](https://news.bitcoin.com/price-predictions/benjamin-cowen-bitcoin-q4-stock-correction/)
- CoinDesk's 2026-11-13 live blog headline attributes the break below the 200-week MA to dollar strength — [CoinDesk](https://www.coindesk.com/tech/2026/11/13/live-news-bitcoin-drops-below-200-week-moving-average-as-dollar-strength-pressures-risk-assets)

### Inferences
- Howell's framework implies a bottoming process that extends well past the four-year-cycle windows: a liquidity trough in mid-to-late 2027 would make late 2026 an early point in a long base, comparable to how the 2022 low preceded a year of sub-200-week-MA trading.
- Pal's Q2 2026 peak call and Hayes's "crash off the table" call both failed against the realized path (peak 2025-10-06, 54% drawdown by 2026-07-01). The liquidity school's directional claim (tightening liquidity explains the decline) survived, but its timing claims for this cycle did not beat the simple four-year calendar.
- Howell's stated cycle length and his stated trough do not reconcile by simple arithmetic in the sources found (peak dates range from Q3 2025 to early 2026 and trough dates from mid-2027 to H2 2027), so the liquidity window should be carried as "2027", not as a specific month.

### Gaps
- No Howell or CrossBorder Capital primary text with an exact trough month was read. No statement dated October or November 2026 was found.
- Not found (search budget exhausted): 2026 ISM/PMI readings and any 2026 ISM-based Bitcoin bottom forecast; DXY level and Fed policy stance in November 2026; equity presidential-cycle statistics (midterm-year low and post-midterm 12-month returns) and their application to 2026-2027; Lyn Alden's 2026 liquidity view; Pal's or Hayes's statements after mid-2026; Global M2 lead/lag (the 10-to-12-week offset charts) status in late 2026.

## 4. "The four-year cycle is dead / changed by ETFs" versus its defenders

### Takeaway
The 2025 "cycle is dead" camp (Hougan, Ki Young Ju, Hayes, Pal) was wrong on direction, since 2026 was a bear year on the classic schedule, and Hougan conceded this in February 2026. The debate in late 2026 has moved to amplitude and timing: Galaxy, Timmer and Ki Young Ju argue ETFs compressed the bear to about 54% and ended it early (June/July), while Cowen and Rekt Capital argue the calendar has not finished.

### Cited Findings
- Matt Hougan (Bitwise), July 2025: the four-year cycle is dead and 2026 will be an "up year", because halving effects shrink and the rate backdrop is favorable; "I could be wrong" — [Cointelegraph](https://cointelegraph.com/news/bitcoin-upside-2026-four-year-cycle-dead-bitwise-invest-cio); [The Block](https://www.theblock.co/post/382690/bitwise-cio-bitcoin-break-4-year-cycle-new-all-time-highs-2026)
- Hougan, 2026-02-10 (CNBC): listed "the four-year cycle" as the number one reason for Bitcoin's losses — [CNBC](https://www.cnbc.com/2026/02/10/bitcoin-crash-bitwise-cio-cites-the-four-year-cycle-for-losses.html); [Bitget News](https://www.bitget.com/news/detail/12560605192626)
- Hougan, 2026-02-23 (The Block podcast): crypto is in a self-fulfilling four-year-cycle bear market; 2026 is a grinding bottom with fundamentals outpacing price, setting up 2027 — [The Block](https://www.theblock.co/podcasts/the-crypto-beat/2026-02-23-the-optimistic-case-for-crypto-in-2026-with-bitwise-cio-matt-hougan-390850)
- Ki Young Ju (CryptoQuant), July 2025: the cycle theory is dead because whales now sell to long-term institutions instead of retail — [The Defiant](https://thedefiant.io/news/markets/bitcoin-4-year-cycle-theory-dead-as-whale-strategy-shifts-analysts)
- Ki Young Ju, 2026-08-25: "The Bitcoin bear cycle is over"; CryptoQuant's Bull/Bear Market Cycle Indicator turned positive (0.042) after bottoming at -1.244 on 2026-02-05 — [Cointelegraph](https://cointelegraph.com/markets/bitcoin-bear-market-over-as-price-metric-copies-2023-recovery-cryptoquant-ceo)
- Ki Young Ju, 2026-10-13 and 2026-10-21: price should move up or sideways for 12 to 24 months; realized price about $54,000 with market price about $80,000; MVRV stayed above 1 this cycle; expects 3x to 5x upside, not another 10x — [BigGo Finance](https://finance.biggo.com/news/338becaf-d25d-45d8-9958-ee9ec3c3d06f); [TokenPost](https://www.tokenpost.com/news/investing/36786); [Tekedia](https://www.tekedia.com/bitcoins-bear-market-is-over-cryptoquant-ceo-says-predicting-3-5x-upside/)
- Arthur Hayes, October 2025: "The four-year cycle? I think that's dead. We're in an extended cycle." — [CoinDesk](https://www.coindesk.com/markets/2025/10/09/bitcoin-crash-off-the-table-as-four-year-cycle-is-dead-arthur-hayes)
- Galaxy Research: June 2026, "the four-year cycle remains valid, but its amplitude has narrowed" and the halving rule is losing impact. On 2026-10-26, evidence for a completed, shallower bear: 53% drawdown, market value never below realized value, spot ETFs added 87,000 BTC after the June low. Galaxy and Thorn disclose they hold Bitcoin — [Kucoin news](https://www.kucoin.com/news/flash/galaxy-research-bitcoin-s-four-year-cycle-remains-valid-halving-rule-losing-impact); [Decrypt](https://decrypt.co/381786/bitcoin-bear-market-is-over-galaxy-research-says)
- Standard Chartered argued the bottom was in at $59,000 while Galaxy (June) argued the low was months away — [BeInCrypto via Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/bitcoin-bottom-debate-standard-chartered-183247020.html)
- Fidelity's Timmer calls this a "mild 4-year cycle winter", accepting the cycle's timing with reduced amplitude — [Jurrien Timmer on X](https://x.com/TimmerFidelity/status/2093468417802084800)
- Defenders: Cowen ("The Four Year Cycle Did Not Die") and Cointelegraph Magazine's cycle debate feature Cowen expecting 2026 to be a bear-market year — [Cointelegraph Magazine](https://cointelegraph.com/magazine/bitcoin-four-year-cycle-dead-debate-bear-market-2026-benjamin-cowen); [Into The Cryptoverse summary](https://rosetta.to/u/intothecryptoverse/bitcoin-the-four-year-cycle-did-not-die)
- Bernstein appears only in a list of firms that saw the cycle as stretched or broken — [Investing.com](https://www.investing.com/news/cryptocurrency-news/is-the-bitcoin-halving-cycle-dead-heres-what-comes-next-4704374)

### Inferences
- Scorecard to date: timing of the top (534 days after the halving against 526 and 548) and the existence of a bear year both matched the classic cycle; depth (54% against 77% to 87%) and top-to-low duration (268 days against 363 to 410) did not, unless a lower low still arrives.
- The "ETF-compressed cycle" claim and the "calendar not finished" claim make opposite predictions for the next few weeks: the first requires the $57,735 July low to hold through the 2026-11-16 to 2027-01-13 window, the second expects it to be tested or broken inside that window. Price at $66,400 on 2026-11-14 is 15% above the July low.
- The on-chain evidence Galaxy and Ju cite as bullish (MVRV never below 1) is the same evidence PlanB and realized-price users cite as "bottom not in". The two readings cannot both be right, and four prior cycles all bottomed with MVRV between 0.39 and 0.75 (LOCAL).

### Gaps
- Bernstein's 2026 bottom call: not found. Bitwise statements after February 2026: not found. Hayes statements in 2026 about the cycle: not found. VanEck, Coinbase/Glassnode quarterly report positions: not found.
- The Cointelegraph Magazine debate piece could not be read in full.

## 5. Historical analogs for double bottoms and re-tests (2015, 2018-2019, 2022) mapped onto February / July 2026

### Takeaway
The February-to-July 2026 structure (second low 3.7% below the first, 145 days later) is numerically closest to February-to-June 2018 (2.5% lower, 143 days later), which was followed about five and a half months later by a 46% breakdown; the 2022 analog (June low, 43% rally, then a low 12% lower after 156 days) would put a final low near $50,800 around early December 2026. The benign analog is 2015, where the re-test held 30% above the low, and 2026 is already trading closer to its low than that.

### Cited Findings

**Analog measurements (LOCAL, Bitstamp intraday lows and highs)**

| Episode | First low | Rally high between | Second / final low | Gap | Second low vs first |
|---|---|---|---|---|---|
| 2015 | 2015-01-14, $152.40 | 2015-07-12, $317.99 (+109%) | 2015-08-25, $198.12 (re-test) | 223 d | +30.0% (higher low) |
| 2018 a | 2018-02-06, $5,920.72 | 2018-02-20, $11,780 (+99%) | 2018-06-29, $5,774.72 | 143 d | -2.5% |
| 2018 b | 2018-06-29, $5,774.72 | (range, 2018-08-14 low $5,880) | 2018-12-15, $3,122.28 | 169 d | -45.9% |
| 2018-19 | 2018-12-15, $3,122.28 | n/a | 2019-01-29, $3,322.19 (re-test) | 45 d | +6.4% (higher low) |
| 2022 | 2022-06-18, $17,592.78 | 2022-08-15, $25,212 (+43%) | 2022-11-21, $15,479 | 156 d | -12.0% |
| 2026 | 2026-02-06, $59,930 | n/a | 2026-07-01, $57,734.63 | 145 d | -3.7% |
| 2026 (open) | 2026-07-01, $57,734.63 | 2026-09-21, $87,373.64 (+51.3%) | so far 2026-11-14, $66,397.36 | 136 d | +15.0% so far |

- Source: [LOCAL: BTC_BITSTAMP_1D.csv](/home/user/soxl-data/data/crypto/extra/BTC_BITSTAMP_1D.csv)
- A press comparison of the post-low bounce: from the 2026-07-01 low Bitcoin made an initial 8% reversal and gained about 41% within 54 days, against a 7% reversal and about 38% within 53 days after the 2022-11-22 low (source attribution uncertain; returned with these pages) — [Coinjuice](https://coinjuice.com/research-hub/bitcoin-bear-market-bottom-july-2026); [Bloomingbit](https://en.bloomingbit.io/feed/news/122812)
- Cowen's gap statistics as summarized: in 2014 the market did not find its final capitulation level until about 174 days after the first low, and in 2022 about 140 days passed between the June low and the break of that support (source attribution uncertain) — [BigGo Finance](https://finance.biggo.com/news/a100483c-c617-49cc-99e4-69891d85591d); [Crowdfund Insider](https://www.crowdfundinsider.com/2026/06/287701-bitcoin-btc-and-crypto-bear-market-exhibiting-characteristics-similar-to-previous-cycles/)
- Cowen's 2018 playbook (early November 2026): Bitcoin may retest its July lows the way it broke down in late 2018 alongside an equity slide — [BigGo Finance](https://finance.biggo.com/news/17258aba-360a-4a05-8223-bc35ee4f0bfc)
- BloFin Research argued for "one more flush before the bottom" — [BloFin via Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/blofin-research-bitcoin-one-more-123554873.html)
- Loukas (2026-06-04) gave about 25% to a bullish double-bottom outcome and said a lower low is the norm — [Cointelegraph](https://cointelegraph.com/news/bitcoin-normal-four-year-cycle-puts-focus-on-53k-low-before-2028-btc-price-high)
- One analysis argued the June/July low near $58,000 does not meet the conditions that marked prior cycle bottoms; another called the 2026 low a break from past midterm timing — [TerabyteTriangle](https://terabytetriangle.com/en/tutorial/bitcoin-cycle-bottom-signals-2026.html); [Cryptobriefing](https://cryptobriefing.com/bitcoin-midterm-cycle-bottom-history/)
- February 2026 context: Bitcoin dipped below an estimated production cost of about $66,000 — [Coinjuice](https://coinjuice.com/research-hub/bitcoin-bear-market-bottom-july-2026)

### Inferences
- Mapping each analog onto 2026 (arithmetic from the LOCAL table):
  - 2022 path: final low 156 days after the summer low and 12% below it gives about 2026-12-04 and about $50,800. Cowen's 140-day and 174-day gaps give 2026-11-18 and 2026-12-22.
  - 2018 path: the 2018 June low held for 169 days, then broke by 46%. Applied to 2026-07-01 this gives about 2026-12-17 and about $31,200. That depth matches Galaxy's June "severe" case ($30,000 to $37,000) and nothing else in the current forecast set.
  - 2015 path: a higher-low re-test 223 days after the low and 30% above it gives about 2027-02-09 and about $75,000. Price is already below that level, so a 2015-style outcome would now mean a deeper re-test than 2015 had (currently +15%).
  - 2018-19 re-test path: a quick higher low within 45 days and 6% above the low gives about $61,400.
- The 2026 rally between lows (+51.3% in 82 days) is larger than 2022's (+43% in 58 days) and smaller than 2015's (+109% in 179 days). In 2022 the rally was fully retraced within 98 days; the 2026 rally has retraced 71% of its range in 54 days.
- In all three prior cycles the final low was the lowest print, and in two of three (2018, 2022) an earlier "apparent bottom" several months before was broken. In 2026 the February apparent bottom was already broken once (by July). A second break would make 2026 a three-low sequence, which is what Cowen's midterm-year template describes.

### Gaps
- No published study was found that explicitly lays February/July 2026 beside January/August 2015; the 2015 mapping above is this researcher's arithmetic.
- The exact articles carrying the "8% / 41% in 54 days" comparison and Cowen's "174 / 140 days" figures could not be pinned down because pages could not be opened.
- Sources disagree on the 2026 low itself: $57,748 or $57,850 on 2026-07-01, $58,589, "June 30", and a CoinGecko figure of about $60,862 on 2026-06-07 appear in different pieces. The LOCAL Bitstamp low is $57,734.63 on 2026-07-01 with the lowest daily close ($58,526.17) on 2026-06-30.

## 6. Quantitative evidence on how long Bitcoin stays near its bottom

### Takeaway
No published study measuring "time within 10% to 20% of the low" was found, so the numbers here are this researcher's measurements: in 2018-19 and 2022-23 Bitcoin spent 22 to 58 days within 10% of the lowest close and 70 to 72 days within 20%, with the bottoming zone spanning roughly 100 to 130 days and the last visit coming 52 to 79 days after the low. The 2026 base is already longer and looser: 58 closes within 10% and 127 within 20% of the 2026-06-30 closing low, spread over 282 days from February to today.

### Cited Findings

**Days spent near the lowest daily close (LOCAL, Bitstamp daily closes, window = cycle top to top + 900 days; 2025-26 to 2026-11-14)**

| Cycle (lowest close) | Closes within 10% | Closes within 20% | Closes within 30% | First to last day within 20% | Last day within 20% after the low | First close at 1.5x the low | First close at 2x the low |
|---|---|---|---|---|---|---|---|
| 2013-15 (2015-01-14, $171.41) | 1 | 2 | 19 | 3 d | 3 d | 12 d | 292 d |
| 2017-18 (2018-12-15, $3,179.54) | 22 | 72 | 125 | 100 d (2018-11-24 to 2019-03-04) | 79 d | 108 d | 147 d |
| 2021-22 (2022-11-21, $15,766) | 58 | 70 | 145 | 128 d (2022-09-06 to 2023-01-12) | 52 d | 69 d | 336 d |
| 2025-26 so far (2026-06-30, $58,526.17) | 58 | 127 | 176 | 282 d (2026-02-05 to 2026-11-14) | 137 d and counting | not yet (needs $87,789) | not yet (needs $117,052) |

- Source: [LOCAL: BTC_BITSTAMP_1D.csv](/home/user/soxl-data/data/crypto/extra/BTC_BITSTAMP_1D.csv). The 2015 row is distorted by a one-day capitulation spike (and Bitstamp's January 2015 outage); the 30% band, which includes the August 2015 re-test 223 days later, is the fairer measure of that base.
- K33 Research's timing measure: after Bitcoin's supply-in-loss crosses 50%, the bottom followed in 13 days (2022), 23 days (2018) and 101 days (2014) (source attribution uncertain; returned with these pages) — [Crowdfund Insider](https://www.crowdfundinsider.com/2026/06/287701-bitcoin-btc-and-crypto-bear-market-exhibiting-characteristics-similar-to-previous-cycles/); [Bitcoin Suisse](https://bitcoinsuisse.com/industry-blog/bitcoin-bottom-on-chain-signals-bear-market)
- Timmer (2026-07-14): Bitcoin can sit near the power-law support line "for months" before turning — [Blockstream Media](https://blockstreammedia.com/2026/07/14/bitcoin-nears-power-law-support-line-fidelity-has-tracked-since-2015/)
- Time below valuation floors at past bottoms (LOCAL): MVRV below 1 for 152 days (2011-12), 304 days (2014-15), 134 days (2018-19), 179 days (2022-23) and 0 days in 2026; closes below the 200-week MA for 317 days in 2022-23 and 27 days so far in 2026 — [LOCAL: BTC_ONCHAIN.csv](/home/user/soxl-data/data/crypto/BTC_ONCHAIN.csv)
- Ki Young Ju's 2026-10-13 expectation of 12 to 24 months of upward or sideways action is the only explicit 2026 forecast of base duration found — [CaptainAltcoin](https://captainaltcoin.com/bitcoin-bear-market-is-over-cryptoquant-ceo-expects-12-24-months-of-bullish-action/)
- Galaxy's 2026-10-26 report describes the post-June period as an accumulation phase in which "hot money has dried up" and older-coin selling pressure has eased — [TechFlow](https://www.techflowpost.com/en-US/article/34882)

### Inferences
- In 2018 and 2022 the buyable zone was short and concentrated around the final low: prices within 10% of the low were available for only 3 to 8 weeks of closes, and the window closed for good 7 to 11 weeks after the low. An investor waiting for confirmation historically paid 1.5x the low within 69 to 108 days.
- The 2026 base does not look like those: price has revisited the within-20% zone 137 days after the closing low, which neither 2018-19 nor 2022-23 allowed (79 and 52 days). Either 2026-07-01 was not the final low, or this cycle's bottom is a wide multi-month range of the 2015 type (where the within-30% zone was revisited 223 days after the low).
- On the 2015 template the base lasted about 9 to 10 months from the low before price left for good (2x the low took 292 days). Applied to 2026-07-01 that runs to roughly April to May 2027, which overlaps Howell's liquidity-trough timing better than it overlaps the four-year-calendar windows.
- A practical band for "near the bottom" in this cycle, if the July low holds, is $57,700 to $70,200 (within 20% of the closing low). Price has closed inside that band on 127 days since 2026-02-05, and is inside it today.

### Gaps
- No third-party quantitative study of time-within-X%-of-the-low was found; the table is original measurement on one exchange's daily closes and should be re-checked against another data source before publication.
- No study was found that estimates typical accumulation-range width (high-to-low of the base) across cycles; Glassnode/Coinbase quarterly reports and Fidelity Digital Assets research were not reachable.
- Four cycles (three of them post-halving) are too few for confidence intervals on any of these durations.
