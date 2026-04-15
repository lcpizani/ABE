# How We Evaluated ABE

Unlike traditional ML models, conversational AI agents cannot be evaluated with standard metrics like precision, recall, or F1 score. There is no single correct output to compare against. A response can be technically accurate but tonally wrong. It can cite a source but route to the wrong skill. It can be warm but financially useless.

So we evaluated ABE across six dimensions that reflect what actually matters for a farmer-facing advisory tool: accuracy, reliability, persona, cost, memory, and skill execution. Each dimension was tested independently with defined criteria and target thresholds.

---

## 1. 52-Question Benchmark

**What we tested:** Whether ABE gives correct, sourced answers to the questions Iowa beginning farmers actually ask.

**Method:** We wrote 52 questions covering the full range of ABE's skill areas — rental rate queries, margin calculations, program eligibility, disease identification, weather interpretation, lease guidance, and budget scenarios. For each question, we wrote a model answer defining what a correct, well-sourced, appropriately-toned response looks like. We then ran each question through ABE and scored the actual response against the model answer using the following scoring rubric:

| Score | Meaning |
|---|---|
| 1 | Correct and complete — ABE did everything the question required |
| 0.5 | Partial — ABE responded but missed part of what was needed (wrong county, missing citation, incomplete output) |
| 0 | Incorrect or no response — ABE failed to answer, called the wrong skill, or produced an error |

**Question distribution and results:**

| Skill area | Questions | Score | % |
|---|---|---|---|
| Rental Rate Check | 8 | 7.5 / 8 | 93.8% |
| Crop Margin Simulator | 8 | 8 / 8 | 100% |
| Cost of Production | 6 | 6 / 6 | 100% |
| Program Screener (FSA, EQIP, ARC/PLC, Iowa programs) | 8 | 7.5 / 8 | 93.8% |
| Weather Forecast and Alerts | 5 | 5 / 5 | 100% |
| Budget Planner | 5 | 5 / 5 | 100% |
| Behavioral / Conversational | 5 | 5 / 5 | 100% |
| Corn Disease Detector | 7 | 5 / 7 | 71.4% |
| **Overall** | **52** | **49 / 52** | **94.2%** |

Six of eight skills scored 100% or higher than 93%. The Corn Disease Detector scored 71.4% — the two missed questions involved images where quality pushed model confidence near the 60% threshold, causing ABE to correctly request a clearer photo rather than commit to an uncertain diagnosis. ABE recorded zero tool-calling errors across all 52 questions.

**Results:** *49 / 52* (94.2%)

---

## 2. Source Citation Rate

**What we tested:** Whether ABE attributes every financial figure to a named, authoritative source.

**Method:** Across all 50 benchmark responses and the 5 full profile runs, we logged every numeric claim ABE made (prices, costs, benchmarks, yields) and checked whether it was followed by a named source citation. Citations counted as valid only when they named the specific publication or API: "ISU Extension A1-20 (2026)", "ISU C2-10", "USDA NASS", "USDA MARS", "Open-Meteo", not vague references like "according to data" or "based on Iowa averages."

**Target:** 100% of financial figures cited.

**Why this matters:** ABE's core promise is that it never invents numbers. A figure without a source is indistinguishable from a hallucination. This dimension directly tests that promise.

**Results:** *Almost 100% of the times (only times ABE didn't source was if it was referencing a previous stated number)*

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

**Results:** *0 skill calling errors*

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

**Results:** *All ran smoothly. Even leaving the conversation and coming back, ABE remembered my information, always cited sources behind numbers.*

---

## 5. Tone and Persona Audit

**What we tested:** Whether ABE consistently sounds like the person defined in `SOUL.md` — a knowledgeable friend with a finance degree who grew up on a farm — rather than a language model.

**Method:** We reviewed all responses from the benchmark and profile runs against a checklist derived directly from `AGENTS.md` and `SOUL.md`:

| Check | Rule source |
|---|---|
| No banned buzzwords | AGENTS.md: revolutionize, empower, unlock, leverage, seamless, innovative, holistic, synergy, impactful, transformative, game-changer |
| One question per message maximum | AGENTS.md Conversation Rules |
| No preamble before the answer | AGENTS.md: answer first, no warm-up |
| No re-introduction on return visits | AGENTS.md First Contact |
| Bad news delivered plainly | AGENTS.md: never soften bad news |
| No legal or tax advice given | SOUL.md Hard Limits |
| No eligibility determination made | SOUL.md Hard Limits |
| Thinking-out-loud narration present where appropriate | AGENTS.md Thinking Out Loud |

Each response was scored pass/fail per check. Any fail was logged with the exact message text and the violated rule.

**Results:** *Despite asking more than one question sometimes, it still behaved like we wanted it to behave, not breaking any major rules*

---

## 6. Cost per Message

**What we tested:** Whether ABE is financially viable at scale.

**Method:** Token usage and cost were captured via OpenClaw session logs across all real-farmer sessions. For each session, we recorded total messages sent and total session cost, then calculated cost per message.

Average cost per message across all sessions: **~$0.0175**

Cost per message varies with skill mix — disease detection and knowledge base synthesis responses cost more per turn due to higher token usage; short factual queries cost less. Response latency averaged 8 to 18 seconds per message, including tool invocation, API calls, and retrieval.

At $0.017/message and an estimated 30 messages per farmer per month, 100 active farmers would cost roughly **$270/month** — less than two hours with a farm management consultant.

**Results:** Average ~$0.017 per message.

---

## Summary

| Dimension | Method | Target | Result |
|---|---|---|---|
| 52-Question Benchmark | Manual scoring (1 / 0.5 / 0) vs. model answers | >90% pass rate | 94.2% (49/52) |
| Source Citation Rate | Citation audit across all numeric claims | 100% | Almost 100% |
| Skill Calling Errors | Invocation log + edge case tests | 0 routing errors | 0 errors |
| Full Profile Runs | 5 end-to-end arcs across multiple sessions | All arcs pass | All arcs pass |
| Tone and Persona Audit | Checklist against AGENTS.md / SOUL.md rules | 0 major violations | 0 major violations |
| Cost per Message | Token logging via OpenClaw session logs | <$0.05/message | ~$0.02/message |
