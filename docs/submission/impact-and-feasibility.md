# Impact and Feasibility Analysis

---

## Target audience

ABE is built for **Iowa beginning farmers** — operators in their first ten years of farming. This includes:

- Young farmers who grew up on farms and are transitioning into ownership or independent operation
- Career changers entering agriculture without a family farming background
- Farmers expanding their operation and encountering new financial and program decisions for the first time
- Tenant farmers negotiating cash rent for the first time and unsure whether a quoted rate is fair

**Secondary audiences:**

- Agricultural lenders and FSA loan officers, who benefit when farmers arrive at their office already familiar with program criteria
- ISU Extension agents, who can refer farmers to ABE for baseline calculations before a consultation
- Farm landlords, who may use ABE to understand what Iowa Beginning Farmer Tax Credit implications their tenants can inform them about

---

## Social impact

**Access to guidance that currently requires money or connections.**

A farm management consultant in Iowa charges $150–$300/hour. County extension agents serve hundreds of farms each. The knowledge beginning farmers need — whether a rent is fair, whether a margin is positive, which programs they qualify for — is publicly available but scattered and inaccessible to most people without significant time or a personal connection.

ABE makes a knowledgeable first conversation available to any Iowa farmer with a smartphone, at any hour, at no cost to them.

**Specific social benefits:**

- Beginning farmers make better-informed rent and lease decisions, reducing the risk of signing into unprofitable arrangements
- Farmers who would never call an FSA office on their own discover they may qualify for beginning farmer loans, EQIP cost-share, or Iowa state financing programs
- Disease identification that previously required a field visit or waiting for extension office hours is available instantly from a photo
- Proactive price and margin alerts reach farmers who don't track commodity markets daily

**Equity dimension:**

Beginning farmers who are not from farming families — first-generation operators — are disproportionately disadvantaged by the current information gap. They lack the informal networks, family knowledge, and existing professional relationships that inherited-operation farmers rely on. ABE is available equally to all.

---

## Economic value

**To the individual farmer:**

A single accurate rent decision — knowing a quoted rate is $30/acre above the ISU benchmark for that county before signing — can be worth $9,000/year on a 300-acre operation. A missed FSA beginning farmer loan, which offers below-market interest rates on amounts up to $600,000, represents a significant financing cost difference over the life of the loan.

ABE does not create this value directly — it gives farmers the information to make better decisions. The economic value is in the decisions the farmer makes with that information.

**Cost to operate:**

| Item | Cost |
|---|---|
| Anthropic API (Claude Sonnet) | ~$5–15/month per active farmer |
| VPS hosting (if deployed on server) | ~$10–20/month total |
| USDA NASS API | Free |
| Open-Meteo | Free |
| gno | Free (open source) |
| ISU Extension publications | Free (publicly available) |

The total cost of running ABE for 100 active farmers is estimated at under $200/month — less than the hourly rate of a single farm management consultation.

---

## Environmental sustainability

ABE directly supports sustainable agricultural practices through two channels:

**EQIP and CSP program access.** ABE's program screener surfaces EQIP (Environmental Quality Incentives Program) and CSP (Conservation Stewardship Program) to farmers who may not know these programs exist or how to access them. These programs pay farmers to implement conservation practices — cover crops, reduced tillage, nutrient management, waterway protection. A farmer who learns about EQIP through ABE and applies is a farmer who may implement practices that reduce runoff, improve soil health, and cut input costs over time.

**Disease detection and reduced fungicide overuse.** A farmer who can identify grey leaf spot versus common rust from a photo makes a more targeted treatment decision. Misidentification leads to either over-application of fungicide (cost and environmental burden) or under-treatment (yield loss). Accurate, fast diagnosis supports more precise management.

**Margin visibility and input efficiency.** When a farmer can see their exact cost-per-acre breakdown and current margin, they have a concrete basis for evaluating whether input levels are appropriate. Visibility into fixed vs. variable costs supports decisions that reduce unnecessary input spending.

---

## Feasibility study

### Technical feasibility

ABE is fully built and operational. It runs on a local machine with a Telegram interface. The core components — OpenClaw agent runtime, gno knowledge base daemon, SQLite database, Python skill scripts, and CornCNN2 model — are all deployed and tested.

The system has no hard technical barriers to scaling. The main constraints are operational (hosting, monitoring) rather than architectural.

### Operational feasibility

| Requirement | Current state | At scale (1,000+ farmers) |
|---|---|---|
| Hosting | Local machine or single VPS | Multi-instance VPS deployment |
| Monitoring | Manual log review | Automated alerting on skill error rates and API failures |
| Data updates | Manual annual update of ISU benchmarks | Scripted with annual calendar reminders |
| Knowledge base updates | Manual document drop | Same process; could be automated via RSS/scraping ISU Extension |
| API costs | ~$5–15/month per active farmer | Covered by grant funding, institutional support, or per-farmer subscription |

### Financial feasibility

ABE's per-farmer operating cost is low enough to be covered by:

- **Grant funding** — USDA Beginning Farmer and Rancher Development Program (BFRDP) grants fund exactly this type of educational tool
- **Iowa-based agricultural foundations** — Iowa Farm Bureau Foundation, Iowa Corn Promotion Board, and similar organizations fund farmer education programs
- **Institutional partnerships** — ISU Extension or USDA could embed ABE as a supplemental resource, covering costs through existing program budgets
- **Freemium subscription** — A low-cost monthly subscription ($5–10/farmer) would cover API costs while keeping ABE accessible to beginning farmers with limited resources

### Regulatory and ethical feasibility

ABE does not provide legal advice, make eligibility determinations, or handle financial transactions. It is explicitly designed as an educational tool that supplements, not replaces, professional consultation. This scope definition makes regulatory risk minimal and aligns with how ISU Extension positions its own publications.

Farmer data is stored locally in plain text files, gitignored from the repository, and never transmitted to third-party services beyond what is necessary for a specific query (e.g., a county name sent to Open-Meteo for a weather request). There is no user account system, no login, and no centralized database of farmer information.

### Scalability plan

**Phase 1 — Current (MVP):** Single-machine deployment, Telegram interface, Iowa corn and soybean operations. 8 skills, 5 heartbeat tasks.

**Phase 2 — Institutional partnership:** Deploy on VPS with automated monitoring. Partner with ISU Extension or Iowa FSA to promote ABE to their beginning farmer contacts. Add usage analytics (aggregate, not individual) to track which skills are used most.

**Phase 3 — Multi-state expansion:** Replace Iowa-specific datasets (ISU C2-10, A1-20, BFLP/LPP documents) with equivalent data from target states. Each state requires its own extension publication set and program document index.

**Phase 4 — Multi-agent team:** Expand from one generalist agent to a coordinated team of specialist agents, as described in [Future Work](../README.md#future-work).
