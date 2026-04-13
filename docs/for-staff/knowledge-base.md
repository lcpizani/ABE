# Managing the Knowledge Base

The knowledge base is a folder of documents that ABE searches when a farmer asks about programs, leases, financing, or disease management. The `gno` daemon watches this folder and indexes documents automatically.

---

## How the knowledge base works

Documents in the `knowledge/` folder are indexed by the `gno` daemon using a hybrid approach:
- **BM25** for keyword relevance
- **Vector embeddings** (Qwen3-Embedding-0.6B) for semantic similarity

Both methods are combined and re-ranked to surface the most relevant content for each query. ABE then cites the specific document in its response.

---

## Adding a document

To add a new document to the knowledge base:

1. Drop the file into the `knowledge/` folder. Supported formats: `.pdf`, `.txt`, `.md`.
2. The daemon detects the new file within its next sync cycle and indexes it automatically.
3. No manual steps required.

If you want to use the helper script:

```bash
bash scripts/add_document.sh /path/to/your-document.pdf
```

This copies the file into `knowledge/` and logs the addition.

If the daemon is not running, index manually:

```bash
gno index
```

---

## Verifying a document was indexed

Check the daemon log for confirmation:

```bash
bash scripts/gno-daemon.sh logs
```

Look for a line showing the document was added and embeddings were generated. For example:

```
[sync] documents: 1 added, 0 updated, 40 unchanged, 0 skipped
[embeddings] generated for: your-document.pdf
```

You can also run a test query to confirm the content is retrievable:

```bash
gno query "topic from your document" -c abe-knowledge -n 3
```

---

## Updating an existing document

Replace the file in `knowledge/` with the new version, using the same filename. The daemon detects the change and re-indexes automatically.

If the document has a new name (for example, a newer edition of an ISU publication), add the new file and optionally remove the old one.

---

## Removing a document

Delete the file from `knowledge/`. The daemon removes it from the index on its next sync cycle.

**Important:** If ABE's responses currently cite that document, removing it means ABE can no longer source those answers. Verify that equivalent content exists in another document before removing.

---

## What types of documents work well

The knowledge base works best with:
- Official program fact sheets and eligibility summaries (PDF or TXT)
- ISU Extension AgDM publications
- USDA program web pages saved as text
- Plain-language summaries and FAQs

Avoid:
- Scanned PDFs without OCR (text is not extractable)
- Large spreadsheets (use the database for structured data instead)
- Documents with heavily formatted tables where context is lost without the structure

---

## Current document inventory

See [Knowledge Documents](../reference/knowledge-documents.md) for a full list of all currently indexed documents organized by category.

---

## Keeping documents current

Key documents to update annually:

| Document | Typical update cycle | What changes |
|---|---|---|
| ISU A1-20 (cost of production) | Each fall for the following crop year | Cost benchmarks |
| ISU C2-10 (cash rental rates) | Each fall | County rental benchmarks |
| FSA program fact sheets | When USDA issues updates | Loan limits, interest rates |
| Iowa BFLP/LPP documents | When IFA/IADD issues updates | Program terms, rates |

When you update a document, re-seed the database if the document feeds structured data:

```bash
# After updating a1-20.xlsx:
.venv/bin/python scripts/update_data.py
.venv/bin/python scripts/seed_costs.py

# After updating C2-10 data:
.venv/bin/python scripts/seed_cash_rent.py
```
