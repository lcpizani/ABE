"""
predict.py — CornCNN2 inference engine.

Loads the model once at module level (singleton). All callers share the same
loaded model — no repeated disk reads.

Public API
----------
predict_image(image_path) -> dict
    {"label": str, "confidence": float, "error": str | None}
"""

import json
import os

import torch  # type: ignore
from PIL import Image  # type: ignore
from torchvision import transforms  # type: ignore

from CornCNN import CornCNN2

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "parameters.pth")
META_PATH  = os.path.join(BASE_DIR, "meta_data.json")

# ── Load metadata ──────────────────────────────────────────────────────────────

with open(META_PATH) as f:
    _meta = json.load(f)
    INDEX_TO_LABEL = {
        int(k): v for k, v in _meta["mapping"].items() if int(k) != -1
    }

# ── Load model once ────────────────────────────────────────────────────────────

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model  = None
_model_load_error = None

try:
    _model = CornCNN2(number_classes=len(INDEX_TO_LABEL))
    _model.load_state_dict(
        torch.load(MODEL_PATH, map_location=_device, weights_only=True)
    )
    _model.to(_device)
    _model.eval()
except Exception as _e:
    _model_load_error = str(_e)

_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])


# ── Public function ────────────────────────────────────────────────────────────

def predict_image(image_path: str) -> dict:
    """
    Run inference on a corn leaf image.

    Args:
        image_path: Local path to a .jpg or .png image.

    Returns:
        dict:
            label      (str | None)  — predicted class name, or None on error
            confidence (float)       — 0.0–1.0
            error      (str | None)  — error message if something went wrong
    """
    if _model is None:
        return {"label": None, "confidence": 0.0, "error": _model_load_error}

    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"label": None, "confidence": 0.0, "error": str(e)}

    tensor = _transform(image).unsqueeze(0).to(_device)

    with torch.no_grad():
        output, _ = _model(tensor)
        probs      = torch.softmax(output, dim=1)
        confidence, pred_idx = torch.max(probs, dim=1)
        label = INDEX_TO_LABEL.get(pred_idx.item(), "Unknown")

    return {"label": label, "confidence": confidence.item(), "error": None}
