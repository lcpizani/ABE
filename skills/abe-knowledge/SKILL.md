---
name: abe-knowledge
description: >
  Search ABE's local knowledge base of Iowa farm business documents
  using hybrid BM25 + vector search. Covers FSA beginning farmer loans,
  EQIP conservation cost-share, ARC-CO vs PLC program selection, Iowa
  Beginning Farmer Tax Credit and Loan Program, Iowa Loan Participation
  Program, cash rent calculation methods, flexible lease agreements,
  and farmland financing options. Use when a farmer asks about government
  programs, loan eligibility, conservation cost-share, farm bill programs,
  lease agreements, or any policy question needing a sourced answer.
  Do NOT use for crop margin calculations or rent benchmarks — those
  use the SQLite database skills.
---

# ABE knowledge base

## When to use this skill

Search the knowledge base before answering any question about:
- FSA loans (beginning farmer, operating, ownership, microloan)
- EQIP or CSP conservation cost-share programs
- ARC-CO vs PLC program selection and decision logic
- Iowa Beginning Farmer Tax Credit
- Iowa Beginning Farmer Loan Program
- Iowa Loan Participation Program
- Cash rent calculation methods (computing a fair rent)
- Flexible lease agreements and trigger mechanisms
- Lease negotiation and what to include in a written lease
- Building a farm resume for a landlord
- Farmland financing options for beginning farmers

## How to search

Run via exec:
```bash
gno query "TOPIC" -c abe-knowledge -n 3 --json
```

Replace TOPIC with the farmer's actual question or key topic.
Keep queries concise — 5-10 words works better than full sentences.

Good query examples:
  gno query "FSA beginning farmer loan eligibility" -c abe-knowledge -n 3
  gno query "EQIP cost share percentage beginning farmers" -c abe-knowledge -n 3
  gno query "ARC-CO PLC Iowa corn which program" -c abe-knowledge -n 3
  gno query "Iowa Beginning Farmer Tax Credit landlord" -c abe-knowledge -n 3
  gno query "flexible cash rent lease trigger price" -c abe-knowledge -n 3

## For a synthesized answer with citations
```bash
gno ask "QUESTION" --answer -c abe-knowledge
```

Use this when you want gno to synthesize an answer, not just
retrieve chunks. Good for complex questions like "what are all
the programs a beginning Iowa farmer might qualify for."

## How to present results

Always cite the source document in your response.
Example: "According to ISU Extension C2-20..."
Example: "The FSA Beginning Farmer fact sheet states..."

Only use results that are clearly relevant to the farmer's question.
If results look off-topic, try rephrasing the query.

If no relevant results are found, say so and direct the farmer to:
- ISU Extension: extension.iastate.edu/agdm
- Local FSA office for loan and program questions
- Local NRCS office for EQIP questions

Never present knowledge base content as your own knowledge.
Always attribute it to the source document.

## Verbose Reasoning

When verbose mode is active, narrate these steps out loud before and
during the search, in plain English the farmer can follow:

**Before searching:**
> "You asked about [topic]. I don't want to answer this one from the top
> of my head — I want to find the actual document so I can give you a
> sourced answer. I'm going to search through the files I have on Iowa
> farm programs and see what comes up for [plain-English description of
> what you're looking for]."

**While searching:**
> "Searching now."

**When results come back and are relevant:**
> "Found something relevant — [name the document or source in plain
> terms, e.g. 'an ISU Extension piece on EQIP beginning farmer rates'].
> Let me read through what it says and pull out what matters for your
> question."

**When results come back but are not clearly relevant:**
> "What came back isn't quite on point. Let me try a different angle on
> the search before I give up on it."

**When no results are found:**
> "I'm not finding anything in the documents I have that covers this well
> enough to cite. I'd rather point you to the right place than guess at it."

---

## Adding new documents

To add a new document to the knowledge base:
1. Drop the .pdf or .txt or .md file into the knowledge folder
2. The gno daemon will detect it and re-index automatically
3. No manual steps needed

If the daemon is not running, manually re-index:
  gno index
