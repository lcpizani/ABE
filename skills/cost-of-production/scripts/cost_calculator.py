"""
skills/cost-of-production/scripts/cost_calculator.py

Cost-of-production calculator for Iowa corn and soybean operations.

Mirrors the ISU CARD / AgDM A1-20 digital calculator structure:
    1. Pre-harvest Machinery  (fixed + variable)
    2. Seed, Chemicals & Inputs (variable, with unit rates)
    3. Harvest Machinery  (fixed + variable)
    4. Labor
    5. Land
    ── Total production cost per acre ──
    6. Net returns (at a given price × yield)

Public API
----------
calculate_cost(crop, acres, rotation, yield_tier, price_per_bu,
               farmer_overrides=None) -> CostResult

How it works
------------
1. Loads line-item defaults from crop_production_costs in data/abe.db
   (populated by scripts/update_data.py parsing knowledge/a1-20.xlsx).
2. If the farmer supplies overrides {cost_item_key: $/acre}, those values
   replace the matching DB row. Unknown keys are silently ignored.
   Only cost rows (not section totals / summary rows) are ever overridden.
3. Computes section subtotals, total fixed + variable, per-bushel totals,
   and net returns. Calculates each item's % of total production cost.
4. Returns a CostResult dataclass with the full breakdown.

Rotation map
------------
crop="corn",     rotation="following_soybeans" → "Corn Following Soybeans"
crop="corn",     rotation="following_corn"      → "Corn Following Corn"
crop="corn",     rotation="silage"              → "Corn Silage Following Corn"
crop="soybeans", rotation=any                   → "Herbicide Tolerant Soybeans Following Corn"

Yield tiers
-----------
"low" | "mid" | "high"  (ISU A1-20 2026 default: mid)
"""

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────────────────────
# File lives at: ABE/skills/cost-of-production/scripts/cost_calculator.py
# parents[0] = scripts/, parents[1] = cost-of-production/, parents[2] = skills/
# parents[3] = ABE/ (project root)
ROOT   = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "abe.db"

# ── Constants ──────────────────────────────────────────────────────────────────
ALLOWED_CROPS    = {"corn", "soybeans"}
ALLOWED_TIERS    = {"low", "mid", "high"}
ALLOWED_ROTATIONS = {
    "corn":     {"following_soybeans", "following_corn", "silage"},
    "soybeans": {"following_corn"},
}

_ROTATION_TO_BUDGET = {
    ("corn",     "following_soybeans"): "Corn Following Soybeans",
    ("corn",     "following_corn"):     "Corn Following Corn",
    ("corn",     "silage"):             "Corn Silage Following Corn",
    ("soybeans", "following_corn"):     "Herbicide Tolerant Soybeans Following Corn",
}

# Sections that contain overrideable line items (excludes summary rows)
_DATA_SECTIONS = {
    "Preharvest Machinery",
    "Seed Chemical Etc",
    "Harvest Machinery",
    "Labor",
    "Land",
}

# Summary sections — read-only; never overridden
_SUMMARY_SECTIONS = {"Summary", "Total fixed, variable", "Historical Summary"}


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class CostLineItem:
    """One line within a section (e.g. 'Nitrogen [$0.53 per pound]')."""
    section:        str
    cost_item:      str
    cost_type:      str          # "fixed" | "variable"
    units_quantity: Optional[float]
    cost_per_acre:  float
    isu_cost_per_acre: float     # unmodified ISU default
    is_overridden:  bool = False

    @property
    def savings_per_acre(self) -> float:
        """Positive = farmer pays less than ISU. Only meaningful if overridden."""
        return round(self.isu_cost_per_acre - self.cost_per_acre, 2)


@dataclass
class SectionSummary:
    section:            str
    fixed_per_acre:     float = 0.0
    variable_per_acre:  float = 0.0
    pct_of_total:       float = 0.0   # filled in after totals are known

    @property
    def total_per_acre(self) -> float:
        return round(self.fixed_per_acre + self.variable_per_acre, 2)


@dataclass
class CostResult:
    # Inputs
    crop:        str
    rotation:    str
    budget_type: str
    acres:       float
    yield_tier:  str
    yield_bu:    float
    price_per_bu: float

    # Line items (all sections, in order)
    line_items: list = field(default_factory=list)

    # Section subtotals (ordered: Preharvest, Seed/Chem, Harvest, Labor, Land)
    sections: dict = field(default_factory=dict)

    # Overrides applied
    overrides_applied: dict = field(default_factory=dict)
    # {cost_item: {"farmer_cost": x, "isu_cost": y, "savings_per_acre": z}}

    # Totals
    fixed_per_acre:    float = 0.0
    variable_per_acre: float = 0.0
    total_per_acre:    float = 0.0
    total_per_bushel:  float = 0.0
    total_operation:   float = 0.0   # total_per_acre × acres

    gross_revenue_per_acre: float = 0.0
    net_return_per_acre:    float = 0.0
    net_return_total:       float = 0.0

    data_year: int = 0
    source:    str = ""


# ── Helpers ────────────────────────────────────────────────────────────────────

def _budget_type(crop: str, rotation: str) -> str:
    key = (crop, rotation)
    if key not in _ROTATION_TO_BUDGET:
        raise ValueError(
            f"Invalid crop/rotation combination: {crop!r} / {rotation!r}. "
            f"Allowed: {sorted(_ROTATION_TO_BUDGET)}"
        )
    return _ROTATION_TO_BUDGET[key]


def _load_rows(crop: str, rotation: str, yield_tier: str) -> tuple[list, int, str]:
    """
    Fetch line-item rows from crop_production_costs for the given budget + tier.
    Returns (rows, data_year, source).
    """
    budget = _budget_type(crop, rotation)

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"abe.db not found at {DB_PATH}. Run scripts/update_data.py first."
        )

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        # Get most recent year available
        year_row = conn.execute(
            "SELECT MAX(year) AS y FROM crop_production_costs WHERE budget_type = ?",
            (budget,),
        ).fetchone()
        if year_row is None or year_row["y"] is None:
            raise ValueError(
                f"No data for budget '{budget}' in crop_production_costs. "
                "Run scripts/update_data.py first."
            )
        year = year_row["y"]

        rows = conn.execute(
            """
            SELECT section, cost_item, cost_type, units_quantity, cost_per_acre
            FROM crop_production_costs
            WHERE budget_type = ?
              AND year       = ?
              AND yield_tier = ?
              AND section NOT IN ('Summary', 'Total fixed, variable', 'Historical Summary')
              AND cost_item  NOT IN ('Total', 'Per acre', 'Per bushel', 'Total cost per acre',
                                     'Total cost per bushel')
            ORDER BY rowid
            """,
            (budget, year, yield_tier),
        ).fetchall()

    return [dict(r) for r in rows], year, "ISU AgDM A1-20"


def _get_yield_for_tier(crop: str, rotation: str, yield_tier: str) -> float:
    """Read the yield value for a given budget type + tier from the DB."""
    budget = _budget_type(crop, rotation)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT yield_value
            FROM crop_production_costs
            WHERE budget_type = ?
              AND yield_tier  = ?
              AND year = (SELECT MAX(year) FROM crop_production_costs WHERE budget_type = ?)
            LIMIT 1
            """,
            (budget, yield_tier, budget),
        ).fetchone()
    if row and row["yield_value"]:
        return float(row["yield_value"])
    # Fallback to known ISU A1-20 2026 middle-tier values
    fallback = {
        ("corn",     "following_soybeans", "mid"): 211.0,
        ("corn",     "following_corn",     "mid"): 193.0,
        ("soybeans", "following_corn",     "mid"):  61.0,
    }
    return fallback.get((crop, rotation, yield_tier), 200.0)


# ── Public function ────────────────────────────────────────────────────────────

def calculate_cost(
    crop:              str,
    acres:             float,
    rotation:          str,
    yield_tier:        str              = "mid",
    price_per_bu:      Optional[float]  = None,
    farmer_overrides:  Optional[dict]   = None,
) -> CostResult:
    """
    Calculate the full cost-of-production breakdown for an Iowa corn or soybean operation.

    Args:
        crop:             "corn" or "soybeans" (case-insensitive).
        acres:            Total acres in the operation.
        rotation:         For corn: "following_soybeans" | "following_corn" | "silage".
                          For soybeans: "following_corn".
        yield_tier:       "low" | "mid" | "high" (default: "mid").
        price_per_bu:     Expected $/bu for net-return calculation. If None,
                          only costs are computed (gross_revenue = 0).
        farmer_overrides: Optional {cost_item_key: actual_$/acre} for any line
                          the farmer knows. cost_item_key must match the
                          cost_item string from the DB exactly, or use the
                          convenience aliases below. Unknown keys are ignored.

    Convenience override aliases (case-insensitive, partial match on left side):
        "seed"          → Seed [...per 1,000 kernels] or Seed [...per unit]
        "nitrogen"      → Nitrogen [...]
        "phosphate"     → Phosphate [...]
        "potash"        → Potash [...]
        "lime"          → Lime [yearly cost]
        "herbicide"     → Herbicide
        "crop_insurance"→ Crop insurance
        "miscellaneous" → Miscellaneous
        "interest"      → Interest on preharvest variable costs [...]
        "labor"         → [Labor section] 2.55 hours [...]  (or similar)
        "cash_rent"     → Cash rent equivalent
        "drying"        → Dry [LP gas, ...]
        "haul"          → Haul
        "combine"       → Combine
        "grain_cart"    → Grain cart
        "handle"        → Handle [auger]
        "preharvest"    → Preharvest Machinery [...]

    Returns:
        CostResult with full line-item breakdown, section subtotals, fixed/variable
        split, per-acre and per-bushel totals, breakdown percentages, and net returns.

    Raises:
        ValueError:       crop, rotation, or yield_tier out of range.
        FileNotFoundError: abe.db not found.
    """
    crop      = crop.strip().lower()
    rotation  = rotation.strip().lower()
    yield_tier = yield_tier.strip().lower()

    if crop not in ALLOWED_CROPS:
        raise ValueError(f"crop must be one of {sorted(ALLOWED_CROPS)}, got {crop!r}")
    if yield_tier not in ALLOWED_TIERS:
        raise ValueError(f"yield_tier must be one of {sorted(ALLOWED_TIERS)}, got {yield_tier!r}")
    if acres <= 0:
        raise ValueError("acres must be > 0")

    budget_type = _budget_type(crop, rotation)
    raw_rows, data_year, source = _load_rows(crop, rotation, yield_tier)

    if not raw_rows:
        raise ValueError(
            f"No line items found for budget='{budget_type}', tier='{yield_tier}'. "
            "Ensure update_data.py ran successfully."
        )

    # ── Build convenience alias lookup ─────────────────────────────────────────
    # Normalize override keys: lowercase + strip → match against cost_item prefix
    _ALIAS_PREFIXES = {
        "seed":           "seed",
        "nitrogen":       "nitrogen",
        "phosphate":      "phosphate",
        "potash":         "potash",
        "lime":           "lime",
        "herbicide":      "herbicide",
        "crop_insurance": "crop insurance",
        "miscellaneous":  "miscellaneous",
        "interest":       "interest",
        "labor":          "labor",          # matched against Labor section
        "cash_rent":      "cash rent",
        "drying":         "dry ",
        "dry":            "dry ",
        "haul":           "haul",
        "combine":        "combine",
        "grain_cart":     "grain cart",
        "handle":         "handle",
        "preharvest":     "preharvest machinery",
    }

    def _resolve_alias(key: str) -> str:
        """Map override alias → DB cost_item prefix (lowercase)."""
        k = key.strip().lower()
        return _ALIAS_PREFIXES.get(k, k)

    # Build {resolved_prefix: value} for farmer overrides
    resolved_overrides: dict[str, float] = {}
    if farmer_overrides:
        for k, v in farmer_overrides.items():
            resolved_overrides[_resolve_alias(k)] = float(v)

    def _match_override(cost_item: str, section: str) -> Optional[float]:
        """Return farmer override $/acre if this item matches any resolved key, else None."""
        ci_lower = cost_item.lower()
        sec_lower = section.lower()
        for prefix, val in resolved_overrides.items():
            if prefix == "labor":
                if sec_lower == "labor":
                    return val
            elif ci_lower.startswith(prefix):
                return val
        return None

    # ── Apply overrides and build line_items ───────────────────────────────────
    line_items: list[CostLineItem] = []
    overrides_applied: dict[str, dict] = {}

    for row in raw_rows:
        section    = row["section"]
        cost_item  = row["cost_item"]
        cost_type  = row["cost_type"]
        units_qty  = row["units_quantity"]
        isu_cost   = float(row["cost_per_acre"]) if row["cost_per_acre"] is not None else 0.0
        actual_cost = isu_cost
        is_overridden = False

        override_val = _match_override(cost_item, section)
        if override_val is not None:
            actual_cost   = override_val
            is_overridden = True
            key = cost_item
            overrides_applied[key] = {
                "farmer_cost":      round(actual_cost, 2),
                "isu_cost":         round(isu_cost, 2),
                "savings_per_acre": round(isu_cost - actual_cost, 2),
            }

        line_items.append(CostLineItem(
            section          = section,
            cost_item        = cost_item,
            cost_type        = cost_type,
            units_quantity   = units_qty,
            cost_per_acre    = round(actual_cost, 2),
            isu_cost_per_acre = round(isu_cost, 2),
            is_overridden    = is_overridden,
        ))

    # ── Compute section subtotals ──────────────────────────────────────────────
    section_order = ["Preharvest Machinery", "Seed Chemical Etc",
                     "Harvest Machinery", "Labor", "Land"]

    sections: dict[str, SectionSummary] = {s: SectionSummary(s) for s in section_order}

    for item in line_items:
        sec = item.section
        if sec not in sections:
            sections[sec] = SectionSummary(sec)
        if item.cost_type == "fixed":
            sections[sec].fixed_per_acre    = round(sections[sec].fixed_per_acre    + item.cost_per_acre, 2)
        elif item.cost_type == "variable":
            sections[sec].variable_per_acre = round(sections[sec].variable_per_acre + item.cost_per_acre, 2)

    # ── Grand totals ───────────────────────────────────────────────────────────
    fixed_total    = sum(s.fixed_per_acre    for s in sections.values())
    variable_total = sum(s.variable_per_acre for s in sections.values())
    total_per_acre = round(fixed_total + variable_total, 2)

    # Backfill % of total into each section
    for s in sections.values():
        s.pct_of_total = round(s.total_per_acre / total_per_acre * 100, 1) if total_per_acre else 0.0

    # ── Yield & net returns ────────────────────────────────────────────────────
    yield_bu = _get_yield_for_tier(crop, rotation, yield_tier)

    total_per_bushel = round(total_per_acre / yield_bu, 4) if yield_bu else 0.0

    gross_revenue_per_acre = 0.0
    net_return_per_acre    = 0.0
    net_return_total       = 0.0
    if price_per_bu is not None:
        gross_revenue_per_acre = round(yield_bu * price_per_bu, 2)
        net_return_per_acre    = round(gross_revenue_per_acre - total_per_acre, 2)
        net_return_total       = round(net_return_per_acre * acres, 2)

    return CostResult(
        crop              = crop,
        rotation          = rotation,
        budget_type       = budget_type,
        acres             = acres,
        yield_tier        = yield_tier,
        yield_bu          = yield_bu,
        price_per_bu      = price_per_bu or 0.0,
        line_items        = line_items,
        sections          = sections,
        overrides_applied = overrides_applied,
        fixed_per_acre    = round(fixed_total, 2),
        variable_per_acre = round(variable_total, 2),
        total_per_acre    = total_per_acre,
        total_per_bushel  = total_per_bushel,
        total_operation   = round(total_per_acre * acres, 2),
        gross_revenue_per_acre = gross_revenue_per_acre,
        net_return_per_acre    = net_return_per_acre,
        net_return_total       = net_return_total,
        data_year         = data_year,
        source            = source,
    )


# ── OpenClaw tool definition ───────────────────────────────────────────────────

TOOL = {
    "name": "cost_of_production",
    "description": (
        "Calculates a detailed, line-by-line cost-of-production breakdown for an Iowa "
        "corn or soybean operation using ISU Extension A1-20 benchmarks. Use this skill "
        "when a farmer asks about their production costs, wants to know what they're "
        "spending per acre, wants to break down fixed vs. variable costs, or needs to "
        "know their cost per bushel. You should ask the farmer what they actually pay "
        "for each major input (seed, fertilizer, rent, etc.) — if they don't know, "
        "use the ISU benchmark and note it. "
        "Trigger phrases: 'what does it cost to raise corn', 'how much am I spending per acre', "
        "'break down my production costs', 'what's my cost per bushel', "
        "'how do my costs compare to average'. "
        "Do NOT use for simple margin/profitability questions — use crop_margin_simulator instead."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "crop": {
                "type": "string",
                "enum": ["corn", "soybeans"],
                "description": "Crop being evaluated.",
            },
            "acres": {
                "type": "number",
                "description": "Total acres in the operation.",
            },
            "rotation": {
                "type": "string",
                "enum": ["following_soybeans", "following_corn", "silage"],
                "description": (
                    "Crop rotation. For corn: 'following_soybeans' (default, most common), "
                    "'following_corn', or 'silage'. For soybeans: always 'following_corn'."
                ),
            },
            "yield_tier": {
                "type": "string",
                "enum": ["low", "mid", "high"],
                "description": (
                    "ISU yield tier to use as default. 'mid' = ISU statewide average. "
                    "Use 'low' or 'high' if farmer reports below- or above-average yields."
                ),
            },
            "price_per_bu": {
                "type": "number",
                "description": (
                    "Expected price per bushel. Used to compute net returns. "
                    "Optional — if omitted, only costs are shown."
                ),
            },
            "farmer_overrides": {
                "type": "object",
                "description": (
                    "Optional {cost_category: actual_$/acre} for inputs the farmer knows. "
                    "Accepted keys: 'seed', 'nitrogen', 'phosphate', 'potash', 'lime', "
                    "'herbicide', 'crop_insurance', 'miscellaneous', 'interest', 'labor', "
                    "'cash_rent', 'drying', 'haul', 'combine', 'grain_cart', 'handle', "
                    "'preharvest'. Unknown keys are ignored."
                ),
                "additionalProperties": {"type": "number"},
            },
        },
        "required": ["crop", "acres"],
    },
    "handler": lambda **kw: _tool_handler(**kw),
}


def _tool_handler(
    crop: str,
    acres: float,
    rotation: str = "following_soybeans",
    yield_tier: str = "mid",
    price_per_bu: float = None,
    farmer_overrides: dict = None,
) -> dict:
    """Adapter between the OpenClaw tool schema and calculate_cost()."""
    # Default rotation by crop
    if crop.strip().lower() == "soybeans":
        rotation = "following_corn"

    result = calculate_cost(
        crop             = crop,
        acres            = acres,
        rotation         = rotation,
        yield_tier       = yield_tier,
        price_per_bu     = price_per_bu,
        farmer_overrides = farmer_overrides,
    )

    # Serialize sections
    sections_out = {}
    for name, sec in result.sections.items():
        sections_out[name] = {
            "fixed_per_acre":    sec.fixed_per_acre,
            "variable_per_acre": sec.variable_per_acre,
            "total_per_acre":    sec.total_per_acre,
            "pct_of_total":      sec.pct_of_total,
        }

    # Serialize line items (include overridden flag)
    items_out = []
    for li in result.line_items:
        items_out.append({
            "section":          li.section,
            "cost_item":        li.cost_item,
            "cost_type":        li.cost_type,
            "units_quantity":   li.units_quantity,
            "cost_per_acre":    li.cost_per_acre,
            "isu_benchmark":    li.isu_cost_per_acre,
            "is_overridden":    li.is_overridden,
            "savings_per_acre": li.savings_per_acre if li.is_overridden else None,
        })

    return {
        "crop":                  result.crop,
        "rotation":              result.budget_type,
        "acres":                 result.acres,
        "yield_tier":            result.yield_tier,
        "yield_bu_per_acre":     result.yield_bu,
        "price_per_bu":          result.price_per_bu,
        "fixed_per_acre":        result.fixed_per_acre,
        "variable_per_acre":     result.variable_per_acre,
        "total_per_acre":        result.total_per_acre,
        "total_per_bushel":      result.total_per_bushel,
        "total_operation":       result.total_operation,
        "gross_revenue_per_acre":result.gross_revenue_per_acre,
        "net_return_per_acre":   result.net_return_per_acre,
        "net_return_total":      result.net_return_total,
        "sections":              sections_out,
        "line_items":            items_out,
        "overrides_applied":     result.overrides_applied,
        "data_year":             result.data_year,
        "source":                result.source,
    }


# ── Quick smoke test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("=== Corn Following Soybeans, 500 acres, mid tier, $4.50/bu ===\n")
    result = calculate_cost(
        crop         = "corn",
        acres        = 500,
        rotation     = "following_soybeans",
        yield_tier   = "mid",
        price_per_bu = 4.50,
    )

    print(f"Budget type : {result.budget_type}")
    print(f"Yield       : {result.yield_bu} bu/acre")
    print(f"Source      : {result.source} {result.data_year}")
    print()
    print(f"{'Section':<30} {'Fixed':>8} {'Variable':>10} {'Total':>8}  {'%':>5}")
    print("-" * 68)
    for name, sec in result.sections.items():
        print(f"{name:<30} {sec.fixed_per_acre:>8.2f} {sec.variable_per_acre:>10.2f} "
              f"{sec.total_per_acre:>8.2f}  {sec.pct_of_total:>4.1f}%")
    print("-" * 68)
    print(f"{'TOTAL':<30} {result.fixed_per_acre:>8.2f} {result.variable_per_acre:>10.2f} "
          f"{result.total_per_acre:>8.2f}  100.0%")
    print()
    print(f"Cost per bushel : ${result.total_per_bushel:.2f}/bu")
    print(f"Gross revenue   : ${result.gross_revenue_per_acre:.2f}/acre")
    print(f"Net return/acre : ${result.net_return_per_acre:.2f}/acre")
    print(f"Net return total: ${result.net_return_total:,.2f} ({result.acres:.0f} acres)")

    print("\n=== With farmer overrides (seed=$95, nitrogen=$70) ===\n")
    r2 = calculate_cost(
        crop              = "corn",
        acres             = 500,
        rotation          = "following_soybeans",
        yield_tier        = "mid",
        price_per_bu      = 4.50,
        farmer_overrides  = {"seed": 95.0, "nitrogen": 70.0},
    )
    for k, v in r2.overrides_applied.items():
        print(f"  {k}: farmer=${v['farmer_cost']}/ac, ISU=${v['isu_cost']}/ac, "
              f"savings=${v['savings_per_acre']}/ac")
    print(f"  Adjusted total: ${r2.total_per_acre:.2f}/acre")
    print(f"  Adjusted net  : ${r2.net_return_per_acre:.2f}/acre")
