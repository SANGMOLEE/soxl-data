# Korean-language and grassroots community views on detecting Bitcoin bottoms (as of 2026-11-14)

> **Research conditions the report writer must know (read first).**
> 1. **Page fetching was blocked.** Every WebFetch attempt failed with a DNS/allowlist error (www.blockmedia.co.kr, kr.beincrypto.com, www.mydailybyte.com, economist.co.kr). All findings below therefore come from **search-result summaries and headlines, not from full article text**. Numbers are as reported in those summaries; context inside the articles could not be checked.
> 2. **The shared web-search budget ran out** (200 searches per turn across all agents) after about 30 of my queries. The Chinese-language 关机价 query, Reddit/Bitcointalk/Hacker News deep-dives, brokerage-report queries, YouTube-channel queries and Seibro custody queries either never ran or returned nothing. These are listed as Gaps, not filled from memory.
> 3. **PRICE CONFLICT with the brief.** The brief says BTC is "now about $66,500". The most recent dated prices I could find are **$73,937.78 on 2026-11-11 07:30 ET** (Fortune), **"below $74,000" on 2026-11-10** (The Block) and a **weekly close of $74,968 for the week ending 2026-11-08** (Blockmedia). I found **no source for 11-12 to 11-14** and no source confirming ~$66,500. Either BTC fell a further ~10% in the last three days (not verified) or the brief's figure is stale/wrong. The writer should re-check a live quote before publishing any "current" number.
> 4. Where I could not tell which of two article URLs a summary sentence came from, both candidate URLs are given and the uncertainty is stated.

---

## 1. Korea-specific bottom indicators (kimchi premium / reverse premium, exchange volume and deposits, USDT premium, Upbit sentiment gauges, 서학개미 leveraged-ETF flows)

### Takeaway
In 2026 the Korea-specific picture is one of **record-long reverse premium (35 straight days, 2026-06-20 to 07-24, bracketing the mid-year low), collapsed KRW exchange volume (FIU daily average 5.4 → 3.1 trillion won; Upbit daily volume down more than 80% in a year) and shrinking deposits (-35% in H1)** — conditions that Korean media describe as "식어버린 코인 열기", and that resemble the apathy seen around past bottoms. However, I found **no source that tested the kimchi premium as a bottom-timing rule with data**, the hard numbers for the premium at the 2018-12 / 2020-03 / 2022-06 / 2022-11 bottoms could mostly not be retrieved, and the structural causes cited in 2026 (money moving to KOSPI and to offshore leveraged venues, 2027 crypto tax) mean the discount may be a regime change rather than a capitulation signal.

### Cited Findings

**Definition and data sources**
- CryptoQuant defines the Korea Premium Index (김치 프리미엄 지표) as the percentage gap between prices on Korean exchanges and overseas exchanges; it notes arbitrage is constrained by legal risk, transfer speed, the Travel Rule and fees. — [CryptoQuant data guide (Korean)](https://dataguide.cryptoquant.com/korean/fund-data-premium/korea-premium-index); [CryptoQuant user guide](https://userguide.cryptoquant.com/ko/cryptoquant-metrics/fund-premium/korea-premium-index); live chart: [CryptoQuant BTC Korea Premium Index](https://cryptoquant.com/asset/btc/chart/market-data/korea-premium-index)

**History of the premium (what could be retrieved)**
- The premium peaked at about 47% in January 2018 (the cycle TOP, not a bottom). — CoinDesk, one of [this piece](https://www.coindesk.com/bitcoin-analysts-kimchi-premium-distress-signal) or [this piece](https://www.coindesk.com/kimchi-premium-reappears-retail-fomo-south-korea/) (search summary did not say which)
- The premium's disappearance in early 2018 was tied to the Korean government's announced crackdown on crypto trading. — [Cointelegraph](https://cointelegraph.com/news/south-korea-s-kimchi-premium-turns-to-discount)
- 2020: a second-hand remark quoted by Decrypt says "for most of 2020, there was actually a Korean discount of 1-3%" (not CryptoQuant's own series). — [Decrypt](https://decrypt.co/53159/the-bitcoin-premium-on-korean-exchanges-is-back)
- 2022 (date within the year not confirmed): the premium "dropped to around 3.39% on Wednesday after climbing up to its highest since December, 6.28%, on Tuesday", per CryptoQuant data. — [Forkast](https://forkast.news/bitcoin-kimchi-premium-2022-high-drop/)
- Around the FTX collapse: a Blockmedia piece reports Upbit BTC at 28,516,000 won versus about 28.9 million won on FTX, i.e. Upbit roughly 1.4% cheaper than the international price (a reverse premium). The article's exact date is not shown in the summary (image path points to October 2022). — [Blockmedia](https://www.blockmedia.co.kr/archives/265965)
- 2022-11-21: in the FTX aftermath the kimchi premium "raised its head again" in individual altcoins — Upbit flagged Kava (>70%) and Serum (>25%) for gaps versus global prices; Serum traded at 357 won on Binance vs 373 on Bithumb and 467 on Upbit. This was a deposit/withdrawal-suspension ("가두리") effect in alts, not a BTC signal. — [Newstomato](https://www.newstomato.com/ReadNews.aspx?no=1161409)
- 2022-12-21: headline says the kimchi premium persisted despite the FTX crisis (body figures not retrieved). — [Asia Economy (EN)](https://www.asiae.co.kr/en/article/2022122109224450534)
- 2023-02-17 to 02-19: CryptoQuant's index moved in a -0.24 to 0.01 range ("kimchi premium gives way to kimchi discount"). — [ForkLog](https://forklog.com/en/kimchi-premium-on-bitcoin-in-south-korea-gives-way-to-kimchi-discount/); [Cointelegraph](https://cointelegraph.com/news/south-korea-s-kimchi-premium-turns-to-discount)
- An undated CryptoSlate article reports a discount of -0.74% and says the last time the premium was negative was October 2023. — [CryptoSlate](https://cryptoslate.com/bitcoin-trades-at-discount-in-korea-destroying-historical-kimchi-premium/)
- July 2025: Blockmedia headline "연중 최대 비트코인 '김치 디스카운트' 끝⋯가격차 감소세" (largest discount of the year ending, gap narrowing). — [Blockmedia](https://www.blockmedia.co.kr/archives/953933)
- Cointelegraph ran a piece framing a collapse in the kimchi premium as "short-term top signal or a reset for bitcoin" (title only retrieved; shows the premium is used globally as a TOP/froth gauge more than a bottom gauge). — [Cointelegraph](https://cointelegraph.com/news/kimchi-premium-collapses-short-term-top-signal-or-a-reset-for-bitcoin)

**2026 readings**
- Reverse kimchi premium (역 김치프리미엄) persisted through 2026. Of the 221 days up to 2026-08-09, BTC was cheaper in Korea than overseas on 123 days; average gap for the period was -0.49%. — [Daily Byte, "식어버린 코인 열기, 역전된 가상자산 시장" (Aug 2026)](https://www.mydailybyte.com/post/%EC%97%AD%EA%B9%80%EC%B9%98%ED%94%84%EB%A6%AC%EB%AF%B8%EC%97%84-2608)
- **2026-06-20 to 2026-07-24: 35 consecutive days of reverse premium — the longest streak on record.** — [Daily Byte](https://www.mydailybyte.com/post/%EC%97%AD%EA%B9%80%EC%B9%98%ED%94%84%EB%A6%AC%EB%AF%B8%EC%97%84-2608)
- The highest BTC kimchi premium of 2026 (to August) was only 4.05% on 2026-01-30, lower than past peaks. — [Daily Byte](https://www.mydailybyte.com/post/%EC%97%AD%EA%B9%80%EC%B9%98%ED%94%84%EB%A6%AC%EB%AF%B8%EC%97%84-2608)
- Causes cited for the 2026 discount: money moving to the domestic stock market, greater use of overseas exchanges, and the crypto tax burden due next year. — [Daily Byte](https://www.mydailybyte.com/post/%EC%97%AD%EA%B9%80%EC%B9%98%ED%94%84%EB%A6%AC%EB%AF%B8%EC%97%84-2608)
- **2026-11-09 06:56 KST: kimchi premium 2.6% (CoinNess figure relayed by CBC뉴스)** — i.e. the premium had turned positive again by early November. — [CBC뉴스](https://cbci.co.kr/news/articleView.html?idxno=624606)
- A Bizwatch article dated 2026-03-30 on the reverse premium surfaced in results (body not retrieved). — [Bizwatch](https://news.bizwatch.co.kr/article/consumer/2026/03/30/0010)
- Community opinion (DC Inside gallery post, January 2026): near-zero kimchi premium should be read as the market being "무방비" (defenceless), not stable. Opinion only, no data test. — [DC Inside](https://gall.dcinside.com/cobak/1289)

**USDT (테더) won premium**
- 2026-06-02 14:11 KST: USDT traded at 1,461 won on Bithumb while USD/KRW was 1,519 — a stablecoin reverse premium of roughly -3.8% (my arithmetic: 1,461/1,519 − 1). — [Blockmedia](https://www.blockmedia.co.kr/archives/1099900)
- Blockmedia also reports that a widening USDT reverse premium despite a strong dollar reflected cooling domestic sentiment and was affecting exchange strategy (date unclear; article is about Coinone/Korbit/Gopax delisting more than listing). — [Blockmedia](https://www.blockmedia.co.kr/archives/1097082)
- Counter-example (panic = premium UP): during the US-China trade-conflict shock, domestic USDT traded more than 5% above USD/KRW (date not confirmed in summary). — [Tokenpost](https://www.tokenpost.kr/news/cryptocurrency/294040)

**Exchange volume, deposits, exchange earnings**
- FIU (금융정보분석원) survey: total volume on domestic exchanges in the first half was 555 trillion won versus 1,001 trillion won in the prior half (-44%); average daily volume fell from 5.4 trillion to 3.1 trillion won. (Search summary did not identify which article; candidates: [Blockmedia "거래량 감소에 상폐 증가…거래소 경쟁력 약화"](https://www.blockmedia.co.kr/archives/1113609), [Dealsite](https://dealsite.co.kr/articles/169975).)
- Upbit's average daily trading value fell from about $9 billion (≈13 trillion won) to about $1.8 billion (≈2.6 trillion won) within one year, a drop of more than 80%; KOSPI strength and rising retail brokerage accounts were named as where the money went. — Blockmedia, one of [this](https://www.blockmedia.co.kr/archives/1097082) or [this](https://www.blockmedia.co.kr/archives/1002789)
- Won deposits at the five KRW-licensed exchanges fell 35% in H1 2026; Dunamu's interim report blamed competition from overseas leveraged products. — [OneBullEx news](https://www.onebullex.com/ko-kr/news/articles/korean-won-deposits-fall-35-as-traders-flee-to-offshore-100x-leverage-5) (non-primary outlet; should be cross-checked against exchange disclosures)
- Upbit + Bithumb deposits were 3.7 trillion won below their peak; market share roughly Upbit 60%s / Bithumb 30%s; volume halved and fee revenue plunged (2026-06-02). — [New Daily](https://biz.newdaily.co.kr/site/data/html/2026/06/02/2026060200106.html)
- "코인서 돈 빠지고 국장에 79조 몰렸다…거래소 실적 '반토막'" (2026-05-19). — [Newsis](https://www.newsis.com/view/NISX20260519_0003635846)
- "거래대금 '반토막'에 업비트·빗썸 상장 봇물…'수수료 방어전' 총력" (2026-08-09). — [Daum/뉴스](https://v.daum.net/v/20260809182843605)
- "거래절벽에 이자부담까지…업비트·빗썸 '2% 예치금' 겹고통" (2026-07-03). — [Digital Daily](https://www.ddaily.co.kr/page/view/2026070315232943331)
- Dunamu's H1 operating profit fell close to 80% year on year, yet customer-deposited holdings of major coins increased (coins stayed, trading stopped). — [IB토마토](https://ibtomato.com/View.aspx?no=19899&type=1); [Newstomato](https://www.newstomato.com/ReadNews.aspx?no=1317758)

**Upbit / Dunamu sentiment gauges**
- Dunamu launched the 디지털 자산 공포-탐욕 지수 in January 2021; it is calculated from Upbit price and volume data, refreshed every 5 minutes on the prior 24 hours, with five bands (매우 탐욕 / 탐욕 / 중립 / 공포 / 매우 공포). It was built by the same Dunamu data team that launched the UBCI index family in 2018. — [DI Today](https://ditoday.com/?p=110317); [Blockmedia](https://www.blockmedia.co.kr/archives/167892)
- UBCI was reorganised into 업비트 데이터 랩 in April 2025; the Fear & Greed index, altcoin-season index and market-cap trend sit in its "인사이트" category. — [Bizwatch](https://news.bizwatch.co.kr/article/mobile/2025/04/16/0007); [FN News](https://www.fnnews.com/news/202504192000331576)
- A Tokenpost item reports the (global) crypto Fear & Greed index dropping to 20, the lowest of the year (date not confirmed in summary). — [Tokenpost](https://www.tokenpost.kr/news/cryptocurrency/339151)
- February 2026 (global gauge, for comparison): Fear & Greed hit an "extreme fear" reading of 12. — [Cointelegraph](https://cointelegraph.com/markets/three-signs-bitcoin-price-near-full-capitulation)

**서학개미 flows into US-listed leveraged crypto products**
- Late August 2026, with BTC moving sideways near $80,000, Korean investors net-bought BITX ("2X Bitcoin Strategy ETF") $11,011,684 and BITU (ProShares Ultra Bitcoin) $6,515,961; the article reads this as investors chasing a sharp short-term rebound with leverage. It also explains BITU holds futures/swaps to target 2x the daily return. — [Economist Korea, 2026-08-27](https://economist.co.kr/article/view/ecn202608270044)
- 2026-08-14: "서학개미 장바구니 1년새 달라졌다…'반도체·레버리지'로 쏠림" — the top-holdings list is now dominated by leveraged products and semiconductors. — [Money Today](https://www.mt.co.kr/article/2026081416230486223)
- Earlier episode: Toss Securities' top three popular tickers were MSTU, MSTX (both 2x MicroStrategy) and MicroStrategy itself (date not confirmed in summary; headline "아마존 제치고 관련 ETF도 매수세 몰려"). — [Blockmedia](https://www.blockmedia.co.kr/archives/789487)
- Shortly after BITU's listing, Korean investors (retail + institutions) had net-bought $26.45 million (≈36.7 billion won) of it. — [Blockmedia](https://www.blockmedia.co.kr/archives/483685)
- ETFGI: "strong and consistent demand by Korean retail investors throughout 2025 for overseas listed ETFs". — [ETFGI](https://etfgi.com/node/28418)
- 서학개미 US-stock holdings approached $200 billion again (SBS Biz, autumn 2026; aggregate only, no ticker breakdown). — [SBS Biz](https://biz.sbs.co.kr/amp/article/20000336701)

**Won price check**
- Upbit KRW-BTC was 110,449,000 won on 2026-10-18. — [시세.com kimchi-premium page](https://www.xn--vj4b13a.com/crypto/kimchi-premium/)
- Around July 2026 a blog quoted Upbit at 96.13 million won with a dollar price of $64,115.9. — [Bullstory blog](https://bullstory.io/blog/업비트-비트코인-현재가-9613만원-오늘-시세와-사는법-총정리)
- No Upbit/Bithumb quote dated 2026-11-12 to 11-14 was found.

### Inferences
- The record 35-day reverse-premium streak (06-20 to 07-24) overlaps the mid-year low (the brief dates it 2026-07-01 at ~$57,700; Hankyung dates a $59K print to 06-06 — see Section 2). So in 2026 the deepest/longest Korean discount did coincide with the lowest price zone so far. That is one observation, not a tested rule.
- By 2026-11-09 the premium was +2.6% while BTC was sliding from ~$80K to ~$74K. A positive premium during a decline is not the "retail has left" configuration; on the folklore reading, Korean retail was not yet capitulating in early November. Alternatively it may simply reflect won weakness/FX frictions. Either way it does not currently show a reverse-premium "bottom" print.
- The premium behaves asymmetrically: it is well documented as a top/froth gauge (47% in January 2018; 4.05% max in 2026 shows no froth this year), but at crashes it can go either way (FTX: BTC discount ~1.4% yet alt premiums of 25-70%; trade-war shock: USDT premium >5%). A sudden premium spike during a crash reflects FX/transfer frictions and local panic buying of dollars, so "reverse premium = bottom" is at best a slow apathy indicator, not a capitulation trigger.
- Volume and deposit collapse (-44% half-on-half volume, -80% Upbit daily volume, -35% deposits) is the Korean analogue of the "apathy phase". But the cited causes are structural (KOSPI rally, offshore leverage, tax), so these series may not mean-revert the way they did after 2018 and 2022.
- 서학개미 leveraged-ETF buying appears pro-cyclical: the documented net buying of BITX/BITU in late August 2026 came after a rebound to ~$80K and before the September high (~$87K per the brief) and the subsequent drop — consistent with a contrarian reading, but based on a single data point.
- For a BITU/SOLT holder, the won-denominated picture also carries FX risk: USD/KRW was ~1,519 in June 2026, so won prices have fallen less than dollar prices.

### Gaps
- **Exact kimchi-premium values on the bottom dates 2018-12-15, 2020-03-13, 2022-06-18 and 2022-11-21 were not found.** CryptoQuant chart pages returned only descriptions. The writer should pull the series directly (CryptoQuant Korea Premium Index, kimpga.com, cryprice) before asserting any number.
- No kimchi-premium readings for the 2026-02-06 low or for 2026-11-12 to 11-14.
- A news.jkn.co.kr item claiming "김치프리미엄 6~7%대" surfaced next to July-2026 results; it conflicts with the documented 35-day reverse premium and is almost certainly an older article. Treat as unreliable. ([link](https://news.jkn.co.kr/post/830123))
- No current Upbit 공포탐욕지수 reading and no history of its value at the 2022 or 2026 lows was found (it only exists since January 2021, so it has seen exactly one prior cycle bottom).
- No data found on Korean exchange new-account openings, Upbit/Bithumb volume share of global spot at past bottoms, CoinNess or Xangle sentiment gauges.
- **No Seibro (세이브로) custody ranking for BITU/BITX/MSTR/MSTU/MSTX/SOLT in October-November 2026 was found**; only the late-August net-purchase figures above.
- The FIU half-year volume figures could not be tied to a single article URL, and the period labels ("상반기" vs "지난해 하반기") should be checked against the FIU 실태조사 itself.
- No source was found that back-tests "reverse premium → buy" or "volume collapse → buy" on Korean data. This is folklore-plus-anecdote as far as this research could establish.
- Unverified background from researcher memory (NOT sourced this session, do not cite as fact): the premium was near zero to slightly negative through most of the 2019 and 2022-23 bear phases, which is why the folklore says "역프 = 바닥권"; this needs the actual series to confirm.

---

## 2. Korean analysts and media in 2026: what bottom levels/timing are being given (October-November 2026) and by what method

### Takeaway
The dominant Korean-language framing in early November 2026 is **"bottom zone $55K-60K in H2 2026, most likely September-November" (CryptoQuant / 주기영), set against a break below the 50-week moving average in the week ending 11-08 and downside warnings to $58K-70K**. Timing arguments cited are cycle-length rules (about 60 weeks from the all-time high → late November 2026; "post-midterm bottom within 13-71 days"), and level arguments are realized price (≈$53.6K-55K). I found **no Korean brokerage (증권사) reports and no Korbit/Xangle/Tiger Research/Four Pillars/Hashed/DeSpread bottom calls for October-November 2026**; Korbit's December 2025 outlook ($140K-170K in 2026) has clearly missed.

### Cited Findings

**Price path as reported (dated)**
- 2026-06-13 (Hankyung Business): "비트코인 '와르르'…최고가 대비 반토막"; CoinMarketCap data showed BTC falling to the $59,000s on the morning of 2026-06-06. — [Hankyung Magazine](https://magazine.hankyung.com/business/article/202606134206b)
- 2026-11-03: Blockmedia headline "비트코인, 미국 중간선거 약세 공식 깼다…12년 만의 변화"; BTC in the $76,000s that day. — Blockmedia, one of [1161164](https://www.blockmedia.co.kr/archives/1161164) / [1160712](https://www.blockmedia.co.kr/archives/1160712) / [1160343](https://www.blockmedia.co.kr/archives/1160343)
- 2026-11-05: "민주당 압승 이후 8만달러 탈환한 비트코인". 2026-11-06: "[코인시황] 비트코인, 美 증시 급락 여파에 7만5000달러대로…나스닥 5.5% 폭락" and "'가짜 반등'에 물렸다… 비트코인 급락에 11억달러 강제 청산". — Blockmedia, among [1162163](https://www.blockmedia.co.kr/archives/1162163), [1162099](https://www.blockmedia.co.kr/archives/1162099), [1162415](https://www.blockmedia.co.kr/archives/1162415)
- "비트코인, 중간선거 급락 딛고 7만8천 달러 되찾았다…ETF는 사흘째 자금 이탈". — [Wikitree](https://www.wikitree.co.kr/articles/1171908)
- Week ending 2026-11-08: BTC closed at $74,968, 0.7% below its 50-week moving average — the first break of the 50-week MA in seven weeks; Blockmedia says the market is watching whether "the low formed in June" holds. — Blockmedia, one of [1164151](https://www.blockmedia.co.kr/archives/1164151) / [1163287](https://www.blockmedia.co.kr/archives/1163287); related: [BeInCrypto Korea](https://kr.beincrypto.com/bitcoin-50-week-moving-average-break/)
- 2026-11-10: BTC slid below $74,000 after a hotter-than-expected US CPI; analysts warned of a drop to $70K. — [The Block](https://theblock.co/news/markets/2026-11-10-bitcoin-price-cpi-inflation-73000-support-437301)
- 2026-11-11 07:30 ET: BTC $73,937.78 (ETH ≈ $2,054.82); about 10-12% below a month earlier and about 29% below a year earlier. — [Fortune 11-11](https://fortune.com/article/price-of-bitcoin-11-11-2026/); [Fortune 11-10](https://fortune.com/article/price-of-bitcoin-11-10-2026/)
- Blockmedia 11-09 to 11-11 headlines: Peter Schiff warns of further decline after the fall to $75,000; a Bloomberg strategist flags US-equity risk after the loss of $80,000; "비트코인 200일선 위태, 7만2000달러가 마지막 방어선"; "비트코인 5만8000달러까지 추락할 수도"; and on the other side "지금이 저가 매수 기회?… 14만6000달러까지 상승 여력". — Blockmedia [1164166](https://www.blockmedia.co.kr/archives/1164166), [1164151](https://www.blockmedia.co.kr/archives/1164151), [1162585](https://www.blockmedia.co.kr/archives/1162585) (headline-level only)
- ETF flows: BTC+ETH ETFs saw about $600 million of net outflows in the last week of October 2026; a 11-09 item reports $500 million net outflow from BTC ETFs. — Blockmedia (same cluster as above: [1163287](https://www.blockmedia.co.kr/archives/1163287))

**주기영 (Ki Young Ju) / CryptoQuant**
- 주기영: "비트코인 5만5000달러서 진짜 반등 나올 것". Diagnosis: selling pressure is overwhelming new capital inflow; institutional position unwinds and absence of buyers define this cycle. Two scenarios for a real rebound: a fall to the realized price near $55,000, or a prolonged $60K-70K sideways range. (Article date not shown in summary.) — [BeInCrypto Korea](https://kr.beincrypto.com/ki-young-ju-bitcoin-55k/)
- CryptoQuant report (April 2026 per the search summary): the next bear-market low may form in H2 2026 in the $55,000-60,000 zone. — [Blockmedia](https://www.blockmedia.co.kr/archives/1076884)
- CryptoQuant's bottom window: June-December 2026, with September-November most likely. — [BeInCrypto Korea (Grayscale piece)](https://kr.beincrypto.com/grayscale-bitcoin-bottom-65k-70k/); [BeInCrypto Korea (Cowen piece)](https://kr.beincrypto.com/bitcoin-bear-market-bottom-benjamin-cowen-prediction/)
- CryptoQuant: at one point in 2026 price had fallen to only 9% above realized price, a condition also seen near past market bottoms; Blockmedia added that further downside remained possible. — Blockmedia [1105113](https://www.blockmedia.co.kr/archives/1105113) / [1066618](https://www.blockmedia.co.kr/archives/1066618)
- "BTC is down 50% but CryptoQuant says the cycle bottom has not arrived yet" (Korean edition headline). — [Bitcoin.com News (ko)](https://news.bitcoin.com/ko/biteukoin-gagyeogi-50-harakhatjiman-keuriptokweonteuneun-ajik-saikeul-jeongjeomi-oji-anatdago-bunseokhaetda/)
- CryptoQuant Quicktake "Has Bitcoin Finally Bottomed?" (author "Easy On Chain") cites STH-SOPR plunging to 0.9215 in January 2026. — [CryptoQuant Insights](https://cryptoquant.com/insights/quicktake/69fe928a74e3a32a7dd4c3fa-Has-Bitcoin-Finally-Bottomed)
- CryptoQuant's Bitcoin Bull Score hit a six-month high on 2026-04-22 while "2022 bear market fears linger". — [FXStreet](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-bull-score-hits-six-month-high-as-2022-bear-market-fears-linger-202604221158); index docs: [CryptoQuant docs](https://docs.cryptoquant.com/v2/community/bitcoin-bull-score.md)

**Other calls carried by Korean media**
- Galaxy Research: realized price $53,600; base-case bottom range $40,000-46,000; confirmation signals for a bottom are not yet sufficient. — [Blockmedia](https://www.blockmedia.co.kr/archives/1105207)
- Grayscale: bottom diagnosed in the $65K-70K area, "early bull-market signal". — [BeInCrypto Korea](https://kr.beincrypto.com/grayscale-bitcoin-bottom-65k-70k/)
- VanEck CEO Jan van Eck: 2026 is the bear "year four" of the four-year cycle and the market is forming a bottom; other analysts quoted were sceptical. Views split between "the February drop was the low" and "late September-early October" (Alphractal CEO). — [BeInCrypto Korea](https://kr.beincrypto.com/vaneck-ceo-bitcoin-bottom-four-year-cycle/)
- Fidelity framing (September 2026 article): the bottom either has not come or has already passed; if the four-year pattern repeats, around November 2026 is the next bottom candidate. — Tokenpost [313812](https://www.tokenpost.kr/news/cryptocurrency/313812) / [318185](https://www.tokenpost.kr/news/cryptocurrency/318185)
- Cycle-length rule: "bear cycles typically bottom about 60 weeks after the all-time high, implying a low in late November 2026". — [ChainCatcher (ko)](https://www.chaincatcher.com/ko/article/2278136)
- Midterm rule: "미 중간선거 이후 비트코인 바닥 왔다…과거 3차례 모두 13~71일 뒤 저점"; the same article cautions that three cases cannot prove elections drive the cycle and that this time a major low may already have formed before the election. — [Blockmedia](https://www.blockmedia.co.kr/archives/1159899)
- Counter-view on the midterm rule: DWF Labs found that in two of three past cases price fell first in the 3-6 months after the election; BTC fell more than 60% in each of the midterm years 2014, 2018 and 2022, and the following-12-month average gain exceeded 50%, with no causal link established. — [BeInCrypto Korea](https://kr.beincrypto.com/bitcoin-us-midterm-election-year-volatility/)
- Tokenpost insight piece: mechanically extrapolating a 2026 bottom from past cycle patterns is dangerous. — [Tokenpost](https://www.tokenpost.kr/news/insights/331556)
- Tokenpost: long-term-holder holding, institutional option hedging and technical rebound signals were "raising confidence in the low" (date unclear). — [Tokenpost](https://www.tokenpost.kr/news/cryptocurrency/284048)
- Swissblock: RSI fell to past-low levels and a large bullish candle appeared, but calling a reversal is premature. — [Bloomingbit](https://bloomingbit.io/feed/news/114906)
- 코빗 리서치센터 (December 2025 outlook, 김민승 센터장): "4년 주기론 깨졌다 … 2026년 유동성 장세"; expected BTC at $140,000-170,000 in 2026 on US fiscal reform and structural institutional demand. — [Digital Daily](https://www.ddaily.co.kr/page/view/2025120809464348933); [BeInCrypto Korea](https://kr.beincrypto.com/bitcoin-institutional-demand-price-forecast-2026/)

### Inferences
- The numeric cluster in Korean-language coverage is: realized price ≈ $53.6K-55K (Galaxy, 주기영) as the "true bottom" anchor; $55K-60K (CryptoQuant) as the expected zone; $58K as a published downside warning in November; $40K-46K (Galaxy base case) as the deep scenario. The 2026 lows so far (~$60K in February, ~$57.7K-59K mid-year) already sit inside the CryptoQuant zone but above realized price.
- The timing cluster points at **now**: 60 weeks after the 2025-10-06 high is 2026-11-30 (my arithmetic); CryptoQuant's "most likely September-November"; Fidelity's "around November"; the midterm rule's 13-71 days after 2026-11-03 gives 2026-11-16 to 2027-01-13 (my arithmetic). These rules rest on three or four prior cycles and their own authors hedge them.
- The 50-week MA break in the week ending 11-08 and "June low validity" language show Korean desks are treating a retest of the mid-year low as the live question, not a confirmed bottom.
- Korbit's $140K-170K call for 2026 is a documented miss by a Korean research house that declared the four-year cycle "broken"; ironically the cycle-length rules it dismissed have so far described 2026 better.

### Gaps
- **No Korean brokerage reports (한화투자증권, 미래에셋, 키움, NH, iM증권 등) on a BTC bottom in October-November 2026 were found** — the search returned only crypto-media articles. Not evidence that none exist.
- No 2026 bottom views retrieved for 쟁글(Xangle), 타이거리서치, 포필러스, 해시드, 디스프레드, 업비트 투자자보호센터, 빗썸 리서치, 코인데스크코리아, 디센터, 매일경제/한국경제 daily coverage.
- Dates of the 주기영 "$55K" article and several Blockmedia items could not be confirmed because pages could not be opened; nothing from 주기영 dated November 2026 was found.
- **No price source for 2026-11-12 to 11-14**; the brief's ~$66,500 is unconfirmed (see note at top).
- The brief dates the second low to 2026-07-01 (~$57,700); Korean media refer to a "June low" and a $59K print on 06-06. The exact date/level of the 2026 cycle low should be verified from price data.
- A 24/7 Wall St. item (no URL returned) reportedly said BTC fell 7.3% in October 2026, its second straight losing October — unlinked, verify before use.

---

## 3. Korean communities and YouTubers: recurring "저점 신호" folklore and whether anyone tested it

### Takeaway
I could verify almost nothing here. The folklore itself (인간지표, 곡소리, 글 리젠 감소, "비트코인 망했다" 여론, 단톡방 지표) is real in the sense that it is widely referenced, but **this research found no Korean community post or video that tested any of these rules with data, and no verifiable 2026 statements from named YouTubers**. Everything in this section should be labelled anecdote/folklore.

### Cited Findings
- Explainer pages on DC Inside 비트코인 갤러리 slang describe the gallery's memes as a condensed expression of member psychology and market perception, and warn that much of the information there is unverified "카더라". — [Tilnote](https://tilnote.io/pages/6884ca3765132c82f72127b9)
- Blind (teamblind) post: a user says he bought "because 곡소리 was being heard" and ended up in the same loss ("곡소리 난다고 들어갔다가 지금 나도 이 꼴 났다"), with a reply joking that the lack of posts means it is time to accumulate BTC. A single anecdote, and about memecoins — but a documented case of the "buy the wailing" rule failing its user. — [Blind](https://www.teamblind.com/kr/post/저번주-곡소리-난다고-들어간-형들-ae3ifddt)
- DC Inside post (January 2026): interprets the absence of a kimchi premium as "무방비" rather than stability — an example of community members reading the premium as a sentiment gauge. Opinion. — [DC Inside](https://gall.dcinside.com/cobak/1289)
- 2025-11-24 news item reposted on DC Inside: after a >20% monthly drop the mood turned to fear and investors were asking "대체 바닥이 어디예요?" — BTC was then around $80K-90K and went on to fall to ~$60K in February 2026, i.e. that wave of "where is the bottom" talk was not the bottom. — [DC Inside (나남뉴스 갤러리)](https://gall.dcinside.com/nanammedia/15827)
- A Korean-language TradingView idea "비트코인 진짜 바닥일까?" argues that some indicators flash strong bottom signals but the price zone where several key indicators agree lies below the then-current price. Individual opinion. — [TradingView](https://vn.tradingview.com/chart/BTCUSD/AiCgDN2h/)
- A Korean Substack essay argues sideways price action is the best condition for long-term accumulators. — [Substack (billyjo)](https://billyjo.substack.com/p/--59f)

### Inferences
- The Korean "human indicator" folklore has measurable proxies that ARE documented in Section 1 — exchange volume, deposits, reverse premium — and those are a more defensible way to operationalise "글 리젠 감소 / 아무도 코인 얘기 안 함" than counting posts.
- The two retrievable anecdotes both cut against naive use: "곡소리" buyers lost money, and loud "where is the bottom?" chatter in November 2025 preceded another ~25-30% decline. Loud fear appears early; silence/apathy (volume collapse) appears late.

### Gaps
- No verified 2026 content from 디시 비트코인 갤러리 개념글, 코인판, 클리앙, 뽐뿌, 에펨코리아, 네이버 카페 or Telegram channels could be retrieved (search engines index these poorly, and pages could not be fetched).
- **No verified 2026 bottom views from Korean YouTubers.** A query for 박작가 / 알고란 returned nothing about them. I cannot confirm any channel's current stance, and none should be attributed in the report.
- No Korean post back-testing 인간지표, 커뮤니티 글 수, "거래소 점검/출금정지 뉴스", or 군대/회사 단톡방 indicators was found. Status: folklore, untested as far as this research can tell.
- Not searched (budget exhausted): Naver DataLab / Google Trends Korea "비트코인" search-volume lows as a quantified apathy gauge.

---

## 4. Global community research: composite indices, dashboards, checklists and long-running threads

### Takeaway
The most concrete, checkable community tools are composite scores: **CBBI (nine-metric 0-100 confidence score; open-source Python on GitHub)** and newer "bottom index" dashboards (e.g. Crypto Value Lab's Bitcoin Bottom Index, which reportedly read **59 versus 91 and 86 at the 2018 and 2022 bottoms**, i.e. "not yet a classic bottom"). 2026 community/analyst bottom calls have already produced one clear partial failure: February's "capitulation-like" readings (RSI 15.9, Fear & Greed 12) marked a tradeable low at ~$60K that was later undercut. I could not retrieve current CBBI/Capriole/Decentrader/Alphractal values or any Reddit/Bitcointalk thread content.

### Cited Findings

**CBBI (Colin Talks Crypto Bitcoin Bull Run Index)**
- CBBI aggregates multiple indicators into one confidence score from 0 to 100; it "can reach upwards of 80 near the top of a bull market or as low as under 10 close to the bottom". — [CoinMarketCap Academy](https://coinmarketcap.com/academy/article/is-the-crypto-bear-market-over)
- It uses nine metrics; a Korean explainer names price trend, MVRV, RHODL ratio, NUPL and Reserve Risk among them, and gives rules of thumb of >80-90 = overheated and <20 = accumulation zone. The same article says CBBI was about 70 on March 25 (CoinGlass), down from a peak of 88 in January-February — year not stated; the article ID suggests 2025. — [Blockmedia](https://www.blockmedia.co.kr/archives/878010)
- Official open-source Python implementation: Zaczero/CBBI on GitHub. — [ecosyste.ms listing](https://awesome.ecosyste.ms/projects/github.com%2Fzaczero%2Fcbbi)
- A TradingView user post says the CBBI confidence reading was 100 at the November 2013 and December 2017 tops but only 76 at the April 2021 top (user post, not official). — [TradingView](https://my.tradingview.com/chart/BTCUSD/T6pKUiBf-The-CBBI-identify-the-timing-the-end-of-the-Bull-Run-cryptos)
- Critical view: a Substack piece titled "Don't Be Fooled by CBBI - Is It Any Good?" argues its credibility is "very low, if any at all". — [Cryptofolks Substack](https://cryptofolks.substack.com/p/dont-be-fooled-by-cbbi-is-it-any)
- TradingView hosts community approximations (e.g. "CBBI Rainbow Approximation (BTC Only)") and a CBBI ideas stream. — [TradingView ideas](https://www.tradingview.com/ideas/cbbi)

**Other composite "bottom" dashboards and open-source tools**
- Crypto Value Lab "Bitcoin Bottom Index": research essay titled "Bitcoin Bottom Index 59; prior bottoms 90+", with scores of 91 at the 2018 bottom and 86 at the 2022 bottom; buckets include market structure, Puell Multiple and hash-ribbon recovery, with MVRV-Z as a "watch" condition. Reading date not shown; not confirmed open source. — [Crypto Value Lab essay](https://astro-blog-starter-cryptovaluelab.pages.dev/research/bitcoin-bottom-index-59-prior-bottoms-90/); [dashboard](https://astro-blog-starter-cryptovaluelab.pages.dev/bitcoin-bottom-conditions/)
- BGeometrics "Bitcoin Identify Market Bottoms" dashboard (free on-chain floor charts). — [BGeometrics](https://charts.bgeometrics.com/dashboard_market_floors.html)
- "BitcoinCycle Clock" community dashboard. — [BitcoinCycle Clock](https://bitcoincycle-clock.pages.dev/about)
- GitHub handiko/pi-cycle-bitcoin-bottom: a TradingView script approximating the cycle bottom from Pi-Cycle-style moving averages; last pushed 2022 (stale). — [ecosyste.ms listing](https://awesome.ecosyste.ms/projects/github.com%2Fhandiko%2Fpi-cycle-bitcoin-bottom)
- TradingView open-source scripts: "Leonid's Bitcoin MVRV & Puell Multiple Z-Score Cycle Indicator"; "MVRV Ratio [Alpha Extract]"; "Bitcoin Cycle History Visualization [SwissAlgo]" (4-year cycle tops and bottoms); "BTC - BEAM: Adaptive Multiple". — [Leonid's indicator](https://my.tradingview.com/script/XLSwrlcE-Leonid-s-Bitcoin-MVRV-Puell-Multiple-Z-Score-Cycle-Indicator); [MVRV Alpha Extract](https://www.tradingview.com/script/mD1VZUyf-MVRV-Ratio-Alpha-Extract); [btcbottom tag](https://www.tradingview.com/scripts/btcbottom/)
- Caution: one TradingView "BTC Cycle Composite" script (MVRV-Z, Puell, CVDD, NUPL plus momentum) states it currently uses **simulated** MVRV/Puell values for demonstration — check code before relying on such scripts. — [TradingView script](https://fr.tradingview.com/script/RgYhOooA)
- Reference write-ups: LookIntoBitcoin "Where does Bitcoin actually bottom according to the data"; Glassnode "Ten Indicators for Tracking a Bear Market Recovery"; Project10x Substack "Buying the Bottom (BTB) Indicators". — [LookIntoBitcoin](https://www.lookintobitcoin.com/bitcoin-research/where-does-bitcoin-actually-bottom-according-to-the-data/); [Glassnode Insights](https://insights.glassnode.com/ten-indicators-for-tracking-a-bear-market-recovery); [Project10x](https://project10x.substack.com/p/buying-the-bottom-btb-indicators)
- News coverage of other composites in 2026: "Bitcoin BCMI drops toward bear market territory: how close is BTC to a real buy zone?" and "Bitcoin Bull-Bear cycle indicator drops to deepest level since FTX bottom" (dates not shown). — [altFINS summary 1](https://altfins.com/crypto-news/crypto-news-summary/207938); [altFINS summary 2](https://altfins.com/crypto-news/crypto-news-summary/212666)

**2026 bottom calls in English-language community/analyst discussion (dated where known)**
- February 2026, K33 Research "A strong case for BTC having bottomed": daily RSI fell to 15.9, the sixth most oversold reading since 2015; "capitulation-like conditions" across spot, ETFs and derivatives; ~$60,000 called a likely (local) bottom. — [K33](https://k33.com/research/articles/a-strong-case-for-btc-having-bottomed); [The Block](https://www.theblock.co/post/389410/k33-bitcoin-bottom)
- February 2026: panic selling by short-term holders, extreme fear and oversold RSI listed as "three signs BTC is near full capitulation". — [Cointelegraph](https://cointelegraph.com/markets/three-signs-bitcoin-price-near-full-capitulation)
- Bitwise CIO Matt Hougan: the February plunge was not the cycle's final bottom. — [ForkLog](https://forklog.com/en/news/bitwise-cio-bitcoin-has-yet-to-hit-cycles-bottom)
- "Bitcoin in capitulation zone as traders debate when BTC will bottom": one pundit projected $40K-50K, most likely forming between mid-September and late November 2026; the piece notes capitulation does not guarantee an immediate bottom. — [Cointelegraph](https://cointelegraph.com/markets/bitcoin-in-capitulation-zone-as-traders-debate-when-btc-price-will-bottom)
- July 2026: "BTC speculators in focus as analysis says textbook bitcoin bottom is underway", with a dissenting contributor noting the metric was not near the ~0.93 level seen at prior local bottoms. — [Cointelegraph](https://cointelegraph.com/news/btc-speculators-in-focus-as-analysis-says-textbook-bitcoin-bottom-is-underway)
- 2026-08-17 video note "Bitcoin bottom signals confirmed", arguing top signals have become less reliable while bottom signals "have been clear in every bear market". — [Lilys note](https://lilys.ai/notes/en/bitcoin-20260817/bitcoin-bottom-signals-confirmed)
- Cycle-timing posts: "The Bitcoin 400-day cycle" and Jason Pizzino's view that bottoming could extend to October 2026; other forecasts put the low between late 2026 and early 2027. — [MetaTrader news](https://www.metatrader.com/ko/news/1743134-the-bitcoin-400-day-cycle-historical-performance-shows-how); [Bitcoin News Digest Substack](https://bitcoinnewsdigest.substack.com/p/deep-dive-special-when-will-bitcoin)
- BTC priced in gold: analysis that BTC is nearing a low against gold. — [Digital Today (EN)](https://www.digitaltoday.co.kr/en/view/14860/bitcoin-nears-bottom-against-gold-bottom-calls-gain-traction)
- Headline "Bitcoin data calls $80K the bottom as analysts say BTC bulls are back" (date not shown). — [Cointelegraph via TradingView](https://ru.tradingview.com/news/cointelegraph%3A9efa717af094b%3A0-bitcoin-data-calls-80k-the-bottom-as-analysts-say-btc-bulls-are-back)

### Inferences
- If the Crypto Value Lab reading of 59 is recent, the community composite view is "meaningfully de-risked but not at the 85-90+ readings of true cycle bottoms" — consistent with Korean analysts' "zone reached, confirmation lacking".
- The February 2026 episode is the cleanest lesson on indicator reliability this cycle: momentum/sentiment extremes (RSI 15.9, F&G 12) identified a multi-month low (~$60K) and a rally, but the level was undercut mid-year by ~2-4%. For a 2x-leveraged-ETF holder that distinction matters less for entry price than for holding-period decay through the retest.
- Any "$80K is the bottom" call (whenever made) was wrong given later prints at $60K and below — an example of "data says bottom" headlines failing.
- Open-source/community scripts vary greatly in quality (one admits to simulated inputs; one is stale since 2022); CBBI's GitHub implementation is the only verified reproducible composite found.

### Gaps
- **Current (November 2026) CBBI value and its exact values at the December 2018, March 2020 and November 2022 bottoms were not found.** Check colintalkscrypto.com/cbbi or CoinGlass directly.
- Unverified background from researcher memory (NOT sourced this session): CBBI's nine components are, to my recollection, Pi Cycle Top, RUPL/NUPL, RHODL Ratio, Puell Multiple, 2-Year MA Multiplier, MVRV Z-Score, Reserve Risk, Woobull Top Cap vs CVDD, and a logarithmic trend ("Trolololo") line, and it printed in the low single digits to ~10 around the 2018 and 2022 bottoms. Confirm on the CBBI site before citing.
- **No Reddit (r/BitcoinMarkets daily thread, r/Bitcoin, r/CryptoCurrency), Bitcointalk ("Wall Observer"), Hacker News or X thread content was retrieved.** The targeted search returned only news articles. I cannot report what these communities say in November 2026.
- No readings found for Capriole Bitcoin Macro Index, Decentrader, Material Indicators, Alphractal dashboards, Bitcoin CounterFlow or Bitcoin Magazine Pro in 2026.
- No community "bottom checklist" spreadsheet was located.
- Dates for several Cointelegraph/altFINS items are missing from the summaries.

---

## 5. Miner shutdown price (关机价) and other Chinese/Japanese-language angles

### Takeaway
Only English-language relays of pool data were retrievable, and they date from **February-March 2026, not November**. They put the electricity-only shutdown price of the mainstream S21 class at roughly **$69K-74K at $0.08/kWh** (Antpool data), with the newest S23-class machines far lower (mid-$40Ks), so in 2026 spot has repeatedly traded below the shutdown price of the fleet's workhorse machines. Sources disagree widely (another puts S21 models at $46K-67K), which shows shutdown price is a band that depends on power cost, not a single floor.

### Cited Findings
- Antpool data (reported February-March 2026): at $0.08/kWh the S21 series (S21, S21+, S21 Hyd) has a shutdown BTC price of about $69,000-74,000; the most efficient models (U3S23H, S23 Hyd) are quoted with shutdown prices around/above $44,000. — [Bitcoin.com News](https://news.bitcoin.com/bitcoin-miners-hit-shutdown-prices-as-profitability-slumps-to-14-month-low); [MEXC news relay](https://www.mexc.com/news/618563)
- A different source (Coin Bureau video summary) puts most S21 models' shutdown prices between $46,000 and $67,000. — [Rosetta/Coin Bureau summary](https://rosetta.to/u/coinbureau/bitcoin-miners-are-abandoning-btc-and-no-one-is-talking-about-why)
- KuCoin's 2026 guide: electricity-only break-even is around $74,000, while full-cost models can exceed $100,000 per BTC; shutdown price is better understood as a range. — [KuCoin blog](https://www.kucoin.com/blog/bitcoin-shutdown-price-2026-profitability-guide); see also [KuCoin "BTC Below Shutdown Price: How Miner Capitulation Triggers Crypto Chain Reactions"](https://www.kucoin.com/blog/BTC-Below-Shutdown-Price)
- CoinShares estimate (March 2026): 15-20% of the global mining fleet was operating at a loss. — [CryptoSlate](https://cryptoslate.com/bitcoins-hashrate-continues-to-fall-as-this-price-spike-doesnt-convince-miners-to-turn-machines-back-on/)
- F2Pool's founder told CoinDesk (late 2025) that an estimated 600,000-800,000 machines had been taken offline since mid-November and F2Pool itself lost more than 10% of its hashrate; F2Pool data showed most older machines below shutdown price. — [BTC-ECHO](https://www.btc-echo.de/bitcoin-mining-bis-zu-800-000-geraete-abgeschaltet/); [DiarioBitcoin](https://www.diariobitcoin.com/mineria/reportes-indican-que-al-menos-600-mil-mineros-bitcoin-han-dejado-de-operar-sus-dispositivos/); [ForkLog](https://forklog.com/en/news/bitcoin-miners-power-down-en-masse-as-losses-hit-records)
- Hashprice fell to an all-time low near $34-35 per PH/s per day in November 2025 and stayed weak into year-end. — [Whale Alert story](https://whale-alert.io/stories/b8607920c004/Record-low-hashprice-and-structural-risks-squeeze-Bitcoin-miners-into-2026); [CryptoSlate](https://cryptoslate.com/how-long-can-bitcoins-hashrate-hold-as-miners-shut-down-across-the-sector/); [Cointelegraph](https://cointelegraph.com/news/miner-hashprice-near-40-miners-survival-mode)
- 2026: mining difficulty fell 19% amid the miners' AI pivot (date within 2026 not shown). — [crypto.news](https://crypto.news/bitcoin-mining-difficulty-falls-19-percent-ai-pivot/)
- Structural exits: Binance's BTC mining pool was scheduled to shut on 2026-11-10 after mining only one block in seven days; Core Scientific announced plans to end BTC mining by Q4 2026. — [Analytics Insight](https://www.analyticsinsight.net/news/binance-bitcoin-mining-pool-mines-just-one-block-as-november-10-shutdown-approaches); [The Currency Analytics](https://thecurrencyanalytics.com/altcoins/binance-shuts-down-bitcoin-mining-pool-nov-10-308617)
- Hashrate Index explainer on why hashrate is falling. — [Hashrate Index](https://hashrateindex.com/blog/why-is-bitcoin-mining-hashrate-falling/)

### Inferences
- With S21-class shutdown at ~$69K-74K (at $0.08/kWh) and the latest verified price ~$74K (11-11), spot is sitting on the workhorse fleet's cash break-even; at the brief's $66,500 it would be below it. The classic "price cannot stay below shutdown cost" folklore has therefore already been violated for extended periods in 2026 (lows of $57.7K-60K), with the adjustment coming through difficulty (-19%) rather than a price floor.
- The 2026 miner story is confounded by the AI/HPC pivot (Core Scientific exit, pool closures): hashrate declines now partly reflect capital reallocation, so hash-ribbon-style "miner capitulation → bottom" signals may fire for non-capitulation reasons.
- Shutdown-price tables are sensitive to the assumed tariff; Chinese-style tables at ¥0.3-0.4/kWh (lower than $0.08) would give materially lower shutdown prices than the Antpool $0.08 figures. That is a reasoned expectation, not a retrieved number.

### Gaps
- **No November 2026 shutdown-price table (f2pool/Antpool) was obtained**; the Chinese-language query could not run because the search budget was exhausted. Current S19 XP / S21 / S23 shutdown prices should be read directly from f2pool's miner page or Antpool.
- No current hashprice, difficulty-adjustment or hash-ribbon status for November 2026.
- No Japanese-language community material was searched or found.
- The $69K-74K and $46K-67K S21 figures conflict; I could not open either source to reconcile assumptions.

---

## 6. Contrarian "human indicator" evidence: where peak pessimism did and did not coincide with bottoms

### Takeaway
The retrievable evidence supports a weak, asymmetric conclusion: **extreme-fear readings tend to precede positive ~90-day returns and marked a multi-month low in February 2026, but they did not mark the final low (it was undercut mid-year), and loud "where is the bottom?" chatter in November 2025 was simply early.** No systematic study of Korean community pessimism versus bottoms was found.

### Cited Findings
- February 2026: Fear & Greed at 12, daily RSI 15.9 (sixth most oversold since 2015), "capitulation-like" conditions; K33 called ~$60K a likely local bottom. — [K33](https://k33.com/research/articles/a-strong-case-for-btc-having-bottomed); [Cointelegraph](https://cointelegraph.com/markets/three-signs-bitcoin-price-near-full-capitulation)
- Mid-2026: BTC fell to the $59,000s on 2026-06-06, "half the all-time high" — i.e. at or below the February capitulation low. — [Hankyung Magazine](https://magazine.hankyung.com/business/article/202606134206b)
- A Korean article citing Forbes: after prolonged periods of extreme fear, returns about 90 days later have often been positive (historical tendency, not a signal). — surfaced among [Bloomingbit](https://bloomingbit.io/feed/news/107480) / [Tokenpost](https://www.tokenpost.kr/news/cryptocurrency/397709) (exact article not identified)
- 2025-11-24: Korean coverage of fearful investors asking "대체 바닥이 어디예요?" after a >20% monthly drop — months before the February 2026 low. — [DC Inside (나남뉴스)](https://gall.dcinside.com/nanammedia/15827)
- Blind anecdote of a user who bought on "곡소리" and lost. — [Blind](https://www.teamblind.com/kr/post/저번주-곡소리-난다고-들어간-형들-ae3ifddt)
- Korean retail leveraged-ETF net buying (BITX $11.0M, BITU $6.5M) clustered in late August 2026 after a rebound to ~$80K. — [Economist Korea](https://economist.co.kr/article/view/ecn202608270044)
- Korean apathy measures at the 2026 mid-year low: 35-day record reverse premium (06-20 to 07-24); exchange volumes halved. — [Daily Byte](https://www.mydailybyte.com/post/%EC%97%AD%EA%B9%80%EC%B9%98%ED%94%84%EB%A6%AC%EB%AF%B8%EC%97%84-2608); [Daum](https://v.daum.net/v/20260809182843605)
- Cointelegraph's capitulation piece explicitly cautions that capitulation readings do not guarantee an immediate bottom. — [Cointelegraph](https://cointelegraph.com/markets/bitcoin-in-capitulation-zone-as-traders-debate-when-btc-price-will-bottom)

### Inferences
- Reliability ranking implied by the 2025-26 record: (a) loud fear/"바닥 어디냐" chatter — early and unreliable (November 2025); (b) quantified extreme fear plus oversold momentum — good for a multi-month low, not the final low (February 2026); (c) quiet apathy — reverse premium, halved volume, falling deposits — coincided with the lowest prices so far (June-July 2026). Sample size is one cycle; treat as a hypothesis.
- As of the latest verified data (11-09 to 11-11) the Korean apathy configuration is NOT fully present: the premium is +2.6% rather than negative, and I have no evidence of a new sentiment extreme. If price really is ~$66,500 on 11-14, sentiment gauges need re-reading before applying any contrarian rule.
- Korean retail flows into 2x products look like a usable contrarian gauge in principle (bought the August rebound), but only one observation was retrieved.

### Gaps
- No documented, dated case studies of Korean community sentiment at the 2018-12, 2020-03, 2022-06 or 2022-11 bottoms were retrieved.
- No quantified series (post counts, 99Bitcoins-style "obituary" counts, Google/Naver search volume, Santiment social dominance) for 2026 was obtained — search budget exhausted. Known-by-reputation but unverified this session: the 99Bitcoins "Bitcoin Obituaries" tally and Google Trends lows are the usual quantified versions of this folklore.
- The Forbes 90-day statistic could not be traced to its original article or sample definition.
