# Adding a Skill

This page explains how to build and integrate a new skill into ABE.

---

## What a skill is

A skill is a capability ABE invokes in response to a specific type of farmer question. Skills are isolated: each has its own directory, its own Python scripts, and its own `SKILL.md` that tells ABE when and how to use it.

ABE never runs a skill unprompted. It offers to run it, waits for the farmer to say yes, then invokes it.

---

## Step 1 — Create the skill directory

```bash
mkdir -p skills/my-skill-name/scripts
```

Skill directory names use lowercase and hyphens (e.g., `rental-rate-check`, `crop-margin-simulator`).

---

## Step 2 — Write the Python script

Create the main script in `skills/my-skill-name/scripts/`. The script must:

- Accept inputs as command-line arguments (use `argparse`)
- Return a valid JSON object to stdout
- Exit with code 0 on success, non-zero on failure
- Include a `source` field in the JSON output naming the data source

**Example skeleton:**

```python
# skills/my-skill-name/scripts/my_skill.py
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-one", required=True)
    parser.add_argument("--input-two", type=float)
    args = parser.parse_args()

    # ... do the work ...

    result = {
        "input_one": args.input_one,
        "output_value": 42.0,
        "source": "ISU AgDM Publication X"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

Test the script directly:

```bash
.venv/bin/python skills/my-skill-name/scripts/my_skill.py --input-one "test"
```

---

## Step 3 — Add a CLI wrapper in `scripts/`

Most skills have a wrapper script in `scripts/` (e.g., `scripts/run_margin.py`). This is optional but recommended for skills that are also used by heartbeat tasks or tested independently.

---

## Step 4 — Write `SKILL.md`

The `SKILL.md` is what ABE reads to know when and how to use the skill. It must include:

1. **YAML frontmatter** with `name` and `description`
2. **When to use this skill** — specific trigger conditions (farmer questions, farmer context)
3. **What inputs to collect** from the farmer before running
4. **The exact command** to run, with all argument names
5. **How to interpret the output** — what each field means
6. **How to present results** to the farmer (voice, structure, what to cite)

**Template:**

```markdown
---
name: my-skill-name
description: >
  One or two sentences describing what this skill does and when ABE
  should use it. Be specific about the trigger conditions.
---

# My Skill Name

## When to use this skill

Use this skill when the farmer asks about [specific topic]. Trigger phrases:
- "..."
- "..."

Do NOT use for [adjacent use case] — that uses [other skill].

## What to collect first

Before running, make sure you have:
- **Input one** — ask if not in profile
- **Input two** — ask if not already mentioned

## How to run

\`\`\`bash
.venv/bin/python skills/my-skill-name/scripts/my_skill.py \
  --input-one "VALUE" \
  [--input-two 42.0]
\`\`\`

## Output fields

| Field | Description |
|---|---|
| `output_value` | What this number means |
| `source` | Where the data came from |

## How to present results

Walk through the key numbers in plain language. Cite the source inline. If [condition], offer [one follow-up].
```

---

## Step 5 — Update `AGENTS.md` routing

Open `AGENTS.md` and add the new skill to the skill routing section. Define:

- What question or context triggers this skill
- What inputs ABE needs to collect before running it
- What one follow-up ABE should offer after presenting results (if any)

---

## Step 6 — Test end-to-end

1. Verify the script returns valid JSON:
   ```bash
   .venv/bin/python skills/my-skill-name/scripts/my_skill.py --input-one "test" | python3 -m json.tool
   ```

2. Check that ABE routes to the skill correctly by asking the trigger question in a test conversation.

3. Verify ABE cites the source from the JSON output inline in its response.

---

## Checklist

- [ ] Script in `skills/my-skill-name/scripts/`
- [ ] Script returns JSON with a `source` field
- [ ] Script uses `.venv/bin/python` (documented, never hardcoded)
- [ ] `SKILL.md` with frontmatter, trigger conditions, command, output reference, presentation guidance
- [ ] Routing entry added to `AGENTS.md`
- [ ] Manual test passes
- [ ] End-to-end conversation test passes
