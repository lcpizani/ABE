---
name: corn-disease-detector
description: >
  Diagnose corn leaf disease from a farmer-uploaded photo using the CornCNN2
  model. Use when a farmer sends an image of a corn plant, mentions that their
  crop "looks off", "has spots", "is yellowing", or asks what is wrong with
  their corn. Also triggers when the farmer uploads any image in the context
  of crop health, plant symptoms, or disease scouting. Do NOT trigger for
  general crop questions without an image. Do NOT use for soybean or other
  non-corn photos — this model was trained on corn only.
---

# Corn Disease Detector

## When to run this skill

Only run this skill when:
- The farmer has uploaded a photo, AND
- The context is crop health, plant symptoms, or disease scouting

Never run this skill on a text-only message, even if the farmer describes
visual symptoms. You cannot see the plant: the photo is required.

If the farmer describes symptoms but has not sent a photo, ask for one:
> "Can you send me a close-up photo of the affected leaf? That way I can
> take a proper look."

## What you need

1. A photo of a corn leaf — .jpg or .png, close-up, single leaf in good light.
   If the photo is blurry, a wide field shot, or clearly not a corn leaf,
   ask for a better one before running.

No other inputs are required. The model handles the rest.

## Running the detection

Run this command via exec:

```
.venv/bin/python skills/corn-disease-detector/scripts/corn_disease.py IMAGE_PATH
```

Required input:
- `IMAGE_PATH` — local filesystem path to the downloaded image (.jpg or .png)

Do not read the script or inspect its source. Just run the command with the image path.

The function returns a plain-language string directly suitable for the farmer.
It handles three cases internally:
- **High confidence (≥ 60%)** — returns diagnosis + farmer-appropriate advice
- **Low confidence (< 60%)** — returns a polite ask for a better photo
- **File error** — returns a message asking the farmer to resend

Supported classes:

| Label | Disease |
|-------|---------|
| Blight | Northern or southern corn blight |
| Common_Rust | Common rust fungus |
| Grey_Leaf_Spot | Cercospora leaf spot |
| Healthy | No disease detected |
| Lethal_Necrosis | Maize lethal necrosis — serious |
| Streak_Virus | Maize streak virus (leafhopper-spread) |

## How to present the result

Do not just paste the raw function output. Deliver it conversationally, like
you are standing in the field with the farmer.

**Step 1 — Name what you see.**
Lead with the disease plainly. "Looking at that leaf, this looks like [disease]."
If the plant is healthy, say so clearly and positively — farmers worry when they
send a photo, so a clean bill of health deserves a direct answer.

**Step 2 — Explain what it means.**
One or two sentences on what the disease is and how it spreads, in plain
language. No Latin, no textbook tone. "It's a fungus that moves in when things
stay wet and warm for a few days."

**Step 3 — Pull management advice from the knowledge base.**
Before responding, run:
  gno ask "management and treatment of [disease] in corn" --answer -c abe-knowledge

Use the result to give the farmer one clear, practical next step. Not a menu
of options — lead with the most important action. Fungicide recommendations
should be framed as something to consider, not a prescription. Always cite
the source document (e.g., "According to ISU Extension..." or "UMN Extension
recommends...") so the farmer knows the advice is grounded.

**Step 4 — Invite their read.**
Close with a question that gives the farmer room to push back or add context:
> "Does that match what you've been seeing out there?"

This is not optional. The farmer may know the field better than the model does.

**After the farmer responds**, follow up based on severity:
- Lethal Necrosis or any low-confidence result: direct them to the county
  extension office immediately. Do not let the conversation end without this.
- Fungal diseases (Blight, Common Rust, Grey Leaf Spot): ask whether conditions
  have been wet recently — it affects how seriously to treat the finding.
- Streak Virus: ask about leafhopper pressure earlier in the season.
- Healthy: offer to check another leaf or area of the field if they are still
  concerned.

Always cite the confidence level inline so the farmer knows how certain the
model is. "The model is about 85% confident on this one" is more useful than
a bare diagnosis.

---

## Hard limits

- **Never diagnose from a non-corn image.** If the photo is clearly off-topic
  (a selfie, a field panorama, a soybean plant), say so:
  "I can only check corn leaf photos — send me a close-up of a single corn
  leaf and I'll take a look."
- **Never recommend specific product brands.** ABE can say "a fungicide may
  be worth considering" but not "use product X at Y rate."
- **Always refer to the extension office** for Lethal Necrosis and for any
  result under the confidence threshold. These are the two cases where a
  wrong answer causes real harm.
- **No soybean disease.** If a farmer sends a soybean photo, say clearly
  that this model only covers corn rather than returning a corn diagnosis.
