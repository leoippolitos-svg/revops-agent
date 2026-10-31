# RevOps methodologies

The analysis methods behind this repository: how to define a number before computing it, and the traps that change the verdict of an analysis. They come from two years of RevOps in a B2B company with yearly sales and renewal cycles, several products and more than one CRM, with every business number removed. The agent can search this page (category `conventions`), and the business skills in `agent/skills/` apply it.

Conventions used throughout:

- **Absolute and relative, always:** `x% (n/N)`. A rate without its denominator is not information.
- **The period in progress is partial**, and is never compared head to head with a closed period.
- **Minimum series:** two closed years, the current year as partial, and a projection labelled with whose it is.

## 0. Principles that apply to everything

1. **Definition before number.** Before computing, write down the universe (who is in), the unit (company, deal, activity, user), the date that counts and the exclusions. Half of all arguments about numbers are different definitions.
2. **Anchor numbers.** Every important line of analysis has three to five official, calibrated numbers per year. A new analysis is reported only after it reproduces them within 2%. If it does not, the method is wrong.
3. **Suspect the method before the business.** A number that contradicts what the operation knows almost always comes from a join, a filter or a duplicate.
4. **A list of ids before a conclusion.** A total that crosses systems becomes a conclusion only with its list of ids. An empty id is declared uncertainty, never zero.
5. **Two ambiguities, two treatments.** An ambiguous slice (period, cycle, profile): use the documented default and say so. An ambiguous definition (the word maps to different metrics): ask first.
6. **A false zero is as bad as an invented number.** An unlikely zero gets a sanity check before it is reported.
7. **Mix versus process.** Every aggregate change splits into a change of composition and a change of rate inside the groups.
8. **One concept, one written rule.** A closed definition becomes a versioned context document, with its date and who decided; a business decision becomes a decision record.

## 1. Ideal customer profile

- **Two rulers at once.** An account that is good to close is not always good to have. Measure **convertibility** (does it close: win rate, meeting-to-win by cell) and **post-sale fit** (does it succeed: activation, usage, renewal, revenue, as a composite score). The fit-by-convertibility matrix shows the trap quadrant: segments that convert well cold and deliver badly after, which look great in SDR metrics and destroy retention.
- **Declared size versus real size.** The CRM's declared size helps prospecting; analysis uses real size, from a cascade of sources (an official industry base, then the CRMs, then a product estimate, then a labelled usage fallback). Penetration above 100% is a data error, and a source with many of them moves down the cascade. Report coverage by source, segment and cohort. A large company often enters small; its value comes from expansion.
- **Cells with a stability filter.** An ICP is a set of cells (segment × size band × account type), not an adjective. A cell becomes a recommendation only with at least two closed years of n ≥ 15, a spread of at most 20 points between years, and the years shown side by side. Classify cells as primary, stable secondary, secondary to monitor, and candidate (do not anchor).
- **Lookalike and anti-ICP.** The top decile of lifetime value: does it collapse into one cell or spread (then size is not the only driver)? The anti-ICP is where retention and fit are worst. Turn the best shallow rule ("IF X AND Y", with retention and n) into an instruction for SDRs.
- **Composition is not cause.** A pattern that survives several controls can still vanish inside the primary ICP; test inside the segment before acting on it.
- **A living ICP.** Revalidate every quarter: leading (meetings and wins by size, in the first quarter), short lagging (activation in 90 days of wins), long lagging (renewal by cohort). Alarm on a ranking drift above five positions, or the core profile below the non-core in two reads in a row.

## 2. Funnel and conversion

- **One canonical funnel**, each rate with an owner: received → accepted (marketing, list quality) → meeting held (SDR) → won (sales); win rate = won / (won + lost), by count **and** value.
- **Accepted** = received minus disqualified, with a closed list of disqualification reasons.
- **The unit is the distinct deal or company.** Counting activities inflates, because one deal gets many.
- **Each source has its date**; meetings count on their due date.
- **Out of the win rate:** anything that is not a commercial loss (internal transfer, disqualification, out-of-scope product).
- **Two universes:** everything (open included) versus closed only.
- **Several pipelines:** the meeting is measured in the entry pipeline, the win in the closing one, with no double count when rebuilding the journey from stage history.
- **Acquisition, renewal and cross-sell are never one number.**
- **The scope of the target:** compare only the portfolio the target covers. A product leaving the pipeline fabricates a "drop" that does not exist.
- **Find the stage that breaks** and give it to its owner: a segment can book meetings well and break in the sales meeting, and then the playbook is about running meetings, not cadence.
- **A list loaded at once has no time series:** if more than 80% of its leads entered in one month, say so instead of drawing a trend.

## 3. Retention, churn and net revenue retention

- **Retention by purchase:** the customer had revenue in period N and in N+1. It already contains renewal, activation and use; never multiply cohort retention by activation and renewal rates (a double discount).
- **Churn on two bases:** churn / (churn + renewal), by count and by value. High by count and low by value means small accounts leave; the reverse is worse. One account cannot be "renewed" in one report and "churned" in another: one classification for every audit, always with n.
- **NRR** = (base + expansion + price increase − churn − downsell) / base. A closed cycle uses recorded values; an open cycle projects with its own empirical rate, apart from the "realised" figures. An at-risk account with no status still enters the projection.
- **Renewing is not keeping volume:** measure the share of renewals that lose more than 20% of volume; it concentrates in small contracts.
- **Early warning signals, separate from the health score:** billing below the contracted minimum, an active downsell, a switch to a substitute, no activation 90 days after sign-up, engagement falling quarter on quarter.

## 4. Health score

- A weighted average of 0-100 criteria. **A criterion without a source is not zero:** re-normalise the weights over the available ones, store weights as fractions, record how many criteria entered, and leave an account with none as null.
- A partial score carries a visible "partial" label. Weights live in configuration, so a new source is a number change, not a rewrite. How each criterion is scored is a decision that needs approval.
- **A health score is not a churn prediction.** It reads the present.

## 5. Deal score

- Start with **explainable weighted rules**: stage (historical rate from it), recent engagement with decay, decision maker involved, ICP fit, proposal status, origin.
- **Calibrate on a closed cohort:** score as of a past date, group into bands, and check that the real rate rises with the band.
- **A large deal is a binary event:** above a threshold it leaves the score for a watchlist. Large proposals often convert worse; size is not a positive signal.
- Order the risk list by `value × (1 − score)`.

## 6. Cohorts

- A cohort is the customers whose entry event fell in the same period; in a seasonal business, cohort N can be sold in year N−1, so use the field that really defines it.
- Use a cohort × period-since-entry matrix with **conditional retention** (k → k+1); the bottleneck is usually the first renewal.
- **Integrity per cohort:** a bulk deletion in the source creates an artificial cohort; investigate before concluding "collapse".
- **Declare the denominator:** "everyone created" (measures the funnel, non-activated included) versus "only those active at the end" (the team's view). Both are valid; never mix them.
- **A status recalculated at cycle end is not history-stable:** a series filtered on it changes the past.

## 7. Forecast

`Projection = realised + open pipeline × historical rate (by origin or stage) + expected new pipeline + large deals (flat, watchlist)`

- **Never project with the rate of a cohort still open:** losses arrive late, so a partial rate can be wrong several times over.
- **New pipeline is not a refinement:** often most of what closes comes from deals created after the projection date; without it the answer is "target unreachable" while it is still in play.
- **A range, not a point:** pessimistic, realistic, optimistic, or a floor and a ceiling; the width is the uncertainty and must be said.
- **Large deals** (above about 10% of the open pipeline) leave the tail and enter flat at their stage rate.
- **A stress variant** treats the old open deals of the base cohort as lost.
- Parameters (rates with numerator and denominator, thresholds, targets with their source) live in versioned configuration.

## 8. Prioritisation and distributing accounts

- **Prioritise by the history of the same month:** qualified accounts in the window, then meetings in that month, then wins over meetings, by segment and region, years side by side. The table goes to a human decision, not to an automatic action.
- **Stratified distribution to SDRs:** for each SDR's quota, split by segment, then evenly by region, then evenly by quartile of a propensity index, and draw at random inside each stratum, with explicit exclusions (active customer, open deal, minimum size, recent activity). Quotas become comparable, so performance can be measured without portfolio bias.

## 9. Protocol for diagnosing a line of business

Each step inherits the calibrated universe and never redefines filters:

0. **Hygiene**: exclude internal, test and intermediated accounts; deduplicate.
1. **Funnel over N years**: volume, revenue, delivery, conversion, calibrated against the anchors.
2. **Retention**: by purchase (N and N+1), by customer type, and NRR.
3. **Segments**: ICP by size and type, tenure, audience, groups.
4. **Causes**: quality of the sale (mix by cohort), implementation capacity, saturation, pricing and discounts.
5. **Plan**: simulate mix and levers against the target.

Rules: calibrate against the anchors first; change one thing at a time and show its effect; no coverage → stop and report (a proxy only declared and labelled); record each hypothesis with a verdict (confirmed, refuted, supported, does not exist), so refuted ones do not come back; classify heterogeneous segments before reporting; a measure with two lenses (per account, per user) names its lens; when every group falls together at the same moment, the next step is a conversation with the operation, not more data.

## 10. Revenue rules that catch everyone

- **Revenue per order, never per item:** a join with items multiplies. Allocation per item is fine only if the allocated sum is reconciled with official revenue and the gap reported.
- **Official revenue is not gross revenue:** separate intermediation and unmapped lines.
- A valid sale is payment confirmed, complete status, not deleted.

## 11. Evaluating what a model generates

- The repository is the source of truth of the prompt; check by hash that what runs is what is in the repository.
- Freeze the prompt before a batch; changing it in the middle invalidates the batch.
- Evaluate by line of argument or intent, not globally; a line with n < 3 is not a conclusion. A failure spread across lines is a writing problem; concentrated in one line, it is that argument.
- **An input failure is not a model failure:** do not tune the prompt to compensate for incomplete CRM data.
- No human feedback means "not reviewed", not "approved"; report review coverage apart from the mechanical rate.
- Measure tokens and cost per run, and keep the history outside the tool that runs it.

## 12. Measuring the impact of an automation

- Separate **volume** (records handled) from **result** (meetings, wins).
- Compare the same month year on year, with the list of active people each year (headcount changes).
- A validated intermediate export makes the comparison reproducible.
- An executive report in four blocks: context, inventory of automations, effect on volume and result, reading and limits.

## Appendix: BI modelling traps

A slicer on the wrong date table inflates instead of zeroing; iterate by year-month, not month number; trim keys when matching across systems; a status filter inside the query hides records that changed status, so filter in the visual; a card can be a snapshot while the chart is year-to-date, so label which; never put an API token in a report's query.
