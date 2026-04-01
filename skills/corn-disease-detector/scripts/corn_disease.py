"""
skills/corn-disease-detector/scripts/corn_disease.py

Skill entry point for corn leaf disease detection.

Loads the CornCNN2 model once at import time and exposes:
  - run_corn_disease_check(image_path) -> str   plain-language diagnosis
  - TOOL                                        Anthropic API tool definition

Supported classes (from meta_data.json):
  0 Blight | 1 Common_Rust | 2 Grey_Leaf_Spot | 3 Healthy
  4 Lethal_Necrosis | 5 Streak_Virus
"""

import json
import os
import sys

import torch
from PIL import Image
from torchvision import transforms

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from CornCNN import CornCNN2  # noqa: E402

# ── Load once at import time ───────────────────────────────────────────────────

with open(os.path.join(BASE_DIR, "meta_data.json")) as f:
    _meta = json.load(f)
    INDEX_TO_LABEL = {
        int(k): v for k, v in _meta["mapping"].items() if int(k) != -1
    }

_device = torch.device("cpu")
_model = CornCNN2(number_classes=len(INDEX_TO_LABEL))
_model.load_state_dict(
    torch.load(
        os.path.join(BASE_DIR, "parameters.pth"),
        map_location=_device,
        weights_only=True,
    )
)
_model.to(_device)
_model.eval()

_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

# ── Farmer-facing advice per class ────────────────────────────────────────────

_ADVICE = {
    "Blight": (
        "This looks like corn blight. Scout for tan or gray lesions starting on lower "
        "leaves. If conditions stay wet and lesions spread to upper leaves before "
        "silking, a fungicide application may be worth the cost. Contact your county "
        "extension office to confirm."
    ),
    "Common_Rust": (
        "This looks like common rust. Small, brick-red pustules are typical. It's "
        "usually manageable — monitor and see if it moves to the upper canopy before "
        "tasseling. Fungicide is rarely needed unless it spreads quickly."
    ),
    "Grey_Leaf_Spot": (
        "This looks like grey leaf spot. It thrives in warm, humid conditions with "
        "heavy dews. Long-term, crop rotation and tillage help. If lesions reach the "
        "ear leaf or above before grain fill, a fungicide may be worth considering."
    ),
    "Healthy": (
        "This plant looks healthy — no disease detected. "
        "Keep scouting as the season progresses."
    ),
    "Lethal_Necrosis": (
        "This may be maize lethal necrosis (MLN). This is a serious disease with no "
        "cure. Contact your county extension office immediately. Infected plants "
        "should be removed to slow the spread. Do not save seed from affected fields."
    ),
    "Streak_Virus": (
        "This looks like maize streak virus, spread by leafhoppers. Remove infected "
        "plants to slow the spread. For next season, consider resistant hybrids and "
        "early planting to reduce leafhopper pressure during the vulnerable seedling "
        "stage."
    ),
}

CONFIDENCE_THRESHOLD = 0.60  # Below this, ask for a better photo


# ── Public function ────────────────────────────────────────────────────────────

def run_corn_disease_check(image_path: str) -> str:
    """
    Classify a corn leaf image and return a plain-language diagnosis.

    Args:
        image_path: Local filesystem path to a .jpg or .png image.

    Returns:
        A plain-language string suitable for sending directly to a farmer via Telegram.
    """
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        return (
            "I wasn't able to open that photo. "
            f"Try sending it again as a .jpg or .png file. (Error: {e})"
        )

    tensor = _transform(image).unsqueeze(0).to(_device)

    with torch.no_grad():
        output, _ = _model(tensor)
        probs = torch.softmax(output, dim=1)
        confidence, pred_idx = torch.max(probs, dim=1)
        label = INDEX_TO_LABEL.get(pred_idx.item(), "Unknown")
        conf = confidence.item()

    if conf < CONFIDENCE_THRESHOLD:
        return (
            f"I got a possible match for {label.replace('_', ' ')} "
            f"but I'm only {conf * 100:.0f}% confident. "
            "The photo may be blurry, too far away, or at an angle that makes it hard "
            "to read. Try a close-up of a single leaf in good daylight, and I'll take "
            "another look. You can also send it to your county extension office to confirm."
        )

    advice = _ADVICE.get(label, "Consult your county extension office for guidance.")
    return f"{advice}\n\n_(Diagnosis: {label.replace('_', ' ')}, {conf * 100:.0f}% confidence)_"


# ── Anthropic API tool definition ─────────────────────────────────────────────

TOOL = {
    "name": "corn_disease_check",
    "description": (
        "Diagnose corn leaf disease from a photo. Use this tool when a farmer uploads "
        "an image of a corn plant, mentions that their crop looks off, has spots, is "
        "yellowing, or asks what is wrong with their corn. Also use it when the farmer "
        "shares any image in the context of crop health, plant symptoms, or disease "
        "scouting. Input must be a local file path to a .jpg or .png image of a corn "
        "leaf. Do NOT use for non-corn crops — this model was trained on corn only."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Local filesystem path to a .jpg or .png image of a corn leaf.",
            },
        },
        "required": ["image_path"],
    },
    "handler": run_corn_disease_check,
}


# ── Quick test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python corn_disease.py <image_path>")
        sys.exit(1)

    print(run_corn_disease_check(sys.argv[1]))
