# How We Evaluated ABE

Unlike traditional ML models, conversational AI agents cannot be evaluated with standard metrics like precision, recall, or F1 score. There is no single correct output to compare against. A response can be technically accurate but tonally wrong. It can cite a source but route to the wrong skill. It can be warm but financially useless.

So we evaluated ABE across six dimensions that reflect what actually matters for a farmer-facing advisory tool: accuracy, reliability, persona, cost, memory, and skill execution. Each dimension was tested independently with defined criteria and target thresholds.

---

## 1. 50-Question Benchmark

**What we tested:** Whether ABE gives correct, sourced answers to the questions Iowa beginning farmers actually ask.

**Method:** We wrote 50 questions covering the full range of ABE's skill areas — rental rate queries, margin calculations, program eligibility, disease identification, weather interpretation, lease guidance, and budget scenarios. For each question, we wrote a model answer defining what a correct, well-sourced, appropriately-toned response looks like. We then ran each question through ABE and scored the actual response against the model answer on three criteria:

| Criterion | Description |
|---|---|
| Factual accuracy | Is the answer correct given the underlying data? |
| Source citation | Does ABE name the source (ISU, USDA, Open-Meteo) inline? |
| Response quality | Is the answer direct, appropriately scoped, and free of hallucination? |

**Question distribution:**

| Skill area | Questions |
|---|---|
| Rental rate check | 7 |
| Crop margin simulator | 10 |
| Cost of production | 6 |
| Program screener (FSA, EQIP, ARC/PLC, Iowa programs) | 10 |
| Weather forecast and alerts | 5 |
| Corn disease detection | 5 |
| Budget planner | 4 |
| Knowledge base (lease, financing, policy) | 3 |

**Results:** *(See attached spreadsheet — Benchmark Results tab)*

---

## 2. Source Citation Rate

**What we tested:** Whether ABE attributes every financial figure to a named, authoritative source.

**Method:** Across all 50 benchmark responses and the 5 full profile runs, we logged every numeric claim ABE made (prices, costs, benchmarks, yields) and checked whether it was followed by a named source citation. Citations counted as valid only when they named the specific publication or API — "ISU Extension A1-20 (2026)", "ISU C2-10", "USDA NASS", "USDA MARS", "Open-Meteo" — not vague references like "according to data" or "based on Iowa averages."

**Target:** 100% of financial figures cited.

**Why this matters:** ABE's core promise is that it never invents numbers. A figure without a source is indistinguishable from a hallucination. This dimension directly tests that promise.

**Results:** *(See attached spreadsheet — Citation Rate tab)*

---

## 3. Skill Calling Errors

**What we tested:** Whether ABE routes to the correct skill, calls scripts with valid arguments, and handles failures gracefully.

**Method:** We logged every skill invocation across the benchmark and profile runs. For each invocation, we checked:

| Check | Pass condition |
|---|---|
| Correct skill selected | ABE chose the skill appropriate for the question |
| Arguments complete | All required arguments were passed to the script |
| Arguments valid | No type errors, missing county names, or invalid crop values |
| Output parsed correctly | ABE interpreted the JSON output accurately |
| Error handling | If a script failed or an API was unavailable, ABE recovered gracefully |

We also deliberately tested edge cases: querying a county that exists in the database but has sparse data, sending a blurry disease photo below the 60% confidence threshold, asking about a crop ABE does not support (livestock), and triggering a MARS API timeout to verify fallback behavior.

**Results:** *(See attached spreadsheet — Skill Errors tab)*

---

## 4. 5 Full Profile Runs

**What we tested:** Whether ABE behaves correctly across a complete farmer relationship — from first contact through return visits with context carryover.

**Method:** We designed five end-to-end conversation arcs, each representing a distinct farmer profile and situation. Each arc ran across multiple sessions to test memory persistence.

| Arc | Farmer profile | What it tested |
|---|---|---|
| New farmer, no context | First message ever, no profile file exists | First contact behavior, profile creation, intro exactly once |
| Returning farmer | Existing profile with county, crops, acres on file | Greeting by name, no re-introduction, correct context pickup |
| Budget-limited beginning farmer | 3 years farming, $400K budget, wants to rent | Budget planner routing, program screener, BFLP/LPP mention |
| Disease detection | Photo of corn leaf sent mid-conversation | Correct disease class, confidence threshold respected, weather history auto-run |
| Skeptical farmer | Pushes back on numbers, asks where they come from | Source citation under pressure, no softening of bad news |

For each arc, we verified: profile file created/updated correctly, correct skill invoked, memory used on return, persona maintained throughout, and no banned words or double dashes in any message.

**Results:** *(See attached spreadsheet — Profile Runs tab)*

---

## 5. Tone and Persona Audit

**What we tested:** Whether ABE consistently sounds like the person defined in `SOUL.md` — a knowledgeable friend with a finance degree who grew up on a farm — rather than a language model.

**Method:** We reviewed all responses from the benchmark and profile runs against a checklist derived directly from `AGENTS.md` and `SOUL.md`:

| Check | Rule source |
|---|---|
| No double dashes (— or --) | AGENTS.md — Hard Rule |
| No banned buzzwords | AGENTS.md: revolutionize, empower, unlock, leverage, seamless, innovative, holistic, synergy, impactful, transformative, game-changer |
| One question per message maximum | AGENTS.md Conversation Rules |
| No preamble before the answer | AGENTS.md: answer first, no warm-up |
| No re-introduction on return visits | AGENTS.md First Contact |
| Bad news delivered plainly | AGENTS.md: never soften bad news |
| No legal or tax advice given | SOUL.md Hard Limits |
| No eligibility determination made | SOUL.md Hard Limits |
| Thinking-out-loud narration present where appropriate | AGENTS.md Thinking Out Loud |

Each response was scored pass/fail per check. Any fail was logged with the exact message text and the violated rule.

**Results:** *(See attached spreadsheet — Persona Audit tab)*

---

## 6. Cost per Conversation

**What we tested:** Whether ABE is financially viable at scale.

**Method:** We enabled token logging via the Anthropic API across all benchmark and profile run sessions. For each conversation turn, we recorded:

- Input tokens (context + farmer message)
- Output tokens (ABE's response)
- Total tokens per turn
- Total tokens per full conversation arc

We then calculated cost per turn and cost per full conversation arc at Claude Sonnet pricing, and compared against Claude Haiku as a lower-cost alternative.

We also identified the highest-cost skill invocations (skill routing with large JSON outputs, knowledge base synthesis responses) to understand where token usage concentrates.

| Metric | Value |
|---|---|
| Avg. tokens per turn | *(see spreadsheet)* |
| Avg. tokens per full conversation | *(see spreadsheet)* |
| Avg. cost per conversation (Sonnet) | *(see spreadsheet)* |
| Estimated monthly cost at 100 active farmers | *(see spreadsheet)* |

**Results:** *(See attached spreadsheet — Cost Analysis tab)*

---

## Summary

| Dimension | Method | Target | Result |
|---|---|---|---|
| 50-Question Benchmark | Manual scoring vs. model answers | >90% pass rate | *(see spreadsheet)* |
| Source Citation Rate | Citation audit across all numeric claims | 100% | *(see spreadsheet)* |
| Skill Calling Errors | Invocation log + edge case tests | 0 routing errors | *(see spreadsheet)* |
| Full Profile Runs | 5 end-to-end arcs across multiple sessions | All arcs pass | *(see spreadsheet)* |
| Tone and Persona Audit | Checklist against AGENTS.md / SOUL.md rules | 0 violations | *(see spreadsheet)* |
| Cost per Conversation | Token logging via Anthropic API | <$0.10/conversation | *(see spreadsheet)* |

---

## How to add results

When results are ready:

1. Fill in the spreadsheet tabs referenced above.
2. Replace each `*(see spreadsheet)*` cell in the Summary table with the actual number.
3. Embed the Excel chart images below the Summary table using standard Markdown image syntax:
   ```markdown
   ![Benchmark Results](../assets/benchmark-results.png)
   ```
4. Drop chart exports into a new `docs/assets/` folder.
