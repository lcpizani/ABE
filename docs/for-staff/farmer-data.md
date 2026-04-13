# Farmer Data and Privacy

This page describes how ABE stores farmer information, what it retains, and what it never records.

---

## How farmer profiles work

When a farmer first messages ABE, a profile file is created at:

```
memory/farmers/<telegram_id>.md
```

The filename is the farmer's Telegram numeric ID (not their username). ABE adds information to this file as it learns it through conversation — never through a form or intake questionnaire.

ABE asks only what it needs to answer the current question. For example, if a farmer asks whether a quoted rent is fair, ABE asks their county and land quality tier before looking up benchmarks. That information is then saved to their profile so ABE does not ask again.

---

## What is stored in a farmer profile

Profiles are short Markdown files with a YAML frontmatter block. They contain only information the farmer has shared directly.

Example profile:

```markdown
---
name: Jake
telegram_id: 000000001
county: Linn County
crops: corn, soybeans
acres: 320
owns_or_rents: rents
years_farming: 4
lease_renewal: March
---
```

Fields ABE collects (only if shared):
- First name
- County
- Crops
- Acres
- Owns or rents
- Years farming
- Tenure situation (lease terms, renewal timing)

---

## What ABE never records

ABE has a hard restriction on what it may write to disk.

**The only file ABE may create or modify is `memory/farmers/<telegram_id>.md`.**

ABE will not create:
- Session logs
- Conversation transcripts
- Daily notes or date-stamped files
- Files in any other directory

This restriction is enforced in `AGENTS.md` and `SOUL.md` and cannot be overridden by a user message.

---

## Protecting farmer files from git

The `memory/farmers/` directory has a `.gitignore` file that prevents farmer profile files from being committed to the repository. Farmer profiles are local only.

**Do not remove this `.gitignore`.** It protects farmer privacy by ensuring profiles are never pushed to a remote repository.

---

## What ABE does on return visits

When a farmer messages ABE again, ABE reads their profile file and picks up where the conversation left off. It greets them by name, does not re-introduce itself, and does not ask questions it already has answers to.

ABE updates the profile any time new information is shared — for example, if a farmer mentions they signed a new lease or switched from renting to owning.

---

## Farmer data access

Farmer profiles are plain text files stored locally. There is no external database, analytics service, or third-party system involved in storing farmer data. The only information transmitted to external services is what is necessary to run a query — for example, a county name sent to Open-Meteo for a weather request.

ABE does not send farmer profile contents to any external service.
