"""
abe.py — ABE agent entry point.

Loads SOUL.md and AGENTS.md as system context, then runs a conversation loop
that routes profitability questions through calculate_margin() before any
financial figures reach the model's response.
"""

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from skills.margin_calculator import calculate_margin
from skills.margin_calculator.calculator import MarginResult

load_dotenv()

ROOT = Path(__file__).parent.parent
SOUL = (ROOT / "SOUL.md").read_text()
AGENTS = (ROOT / "AGENTS.md").read_text()

SYSTEM_PROMPT = f"{SOUL}\n\n---\n\n{AGENTS}"

# Tool definition ABE can call when it needs margin data.
TOOLS = [
    {
        "name": "calculate_margin",
        "description": (
            "Calculate gross revenue, costs by category, and net margin per acre "
            "for corn or soybeans. Compare to ISU Extension benchmark. "
            "Call this whenever a farmer asks about profitability, whether a crop "
            "is worth planting, or what their net income would look like."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "crop": {
                    "type": "string",
                    "enum": ["corn", "soybeans"],
                    "description": "The crop being evaluated.",
                },
                "acres": {
                    "type": "number",
                    "description": "Total acres planted.",
                },
                "yield_bu": {
                    "type": "number",
                    "description": "Expected yield in bushels per acre.",
                },
                "price_per_bu": {
                    "type": "number",
                    "description": "Expected or contracted price in dollars per bushel.",
                },
                "rental_rate": {
                    "type": "number",
                    "description": "Cash rent per acre being paid.",
                },
            },
            "required": ["crop", "acres", "yield_bu", "price_per_bu", "rental_rate"],
        },
    }
]


def run_tool(name: str, inputs: dict) -> str:
    if name == "calculate_margin":
        try:
            result: MarginResult = calculate_margin(**inputs)
            return _format_result(result)
        except (ValueError, FileNotFoundError) as e:
            return f"Error running calculate_margin: {e}"
    return f"Unknown tool: {name}"


def _format_result(r: MarginResult) -> str:
    cost_lines = "\n".join(
        f"  {cat.replace('_', ' ').title()}: ${v:.2f}/acre"
        for cat, v in r.costs_by_category.items()
    )
    return (
        f"MARGIN CALCULATION RESULT ({r.data_year} ISU data)\n"
        f"Crop: {r.crop} | Acres: {r.acres}\n"
        f"Yield: {r.yield_bu} bu/acre | Price: ${r.price_per_bu}/bu | Rent: ${r.rental_rate}/acre\n\n"
        f"Gross revenue:         ${r.gross_revenue_per_acre:.2f}/acre\n"
        f"Production costs:\n{cost_lines}\n"
        f"  Cash rent:           ${r.rental_rate:.2f}/acre\n"
        f"Total cost:            ${r.total_cost_per_acre:.2f}/acre\n"
        f"Net margin/acre:       ${r.net_margin_per_acre:.2f}\n"
        f"Net margin total:      ${r.net_margin_total:.2f}\n\n"
        f"ISU benchmark margin:  ${r.isu_net_margin_per_acre:.2f}/acre\n"
        f"Your margin vs. ISU:   ${r.margin_vs_benchmark:+.2f}/acre\n\n"
        f"Source: {r.source}"
    )


def chat():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    messages = []

    print("ABE — Agricultural Business Expert")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # Agentic loop — keep going until stop_reason is not "tool_use"
        while True:
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                # Append assistant's tool-call turn
                messages.append({"role": "assistant", "content": response.content})

                # Run each requested tool
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        output = run_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": output,
                            }
                        )

                messages.append({"role": "user", "content": tool_results})
                # Loop again so the model can form its final response

            else:
                # Final text response
                reply = next(
                    (b.text for b in response.content if hasattr(b, "text")), ""
                )
                print(f"\nABE: {reply}\n")
                messages.append({"role": "assistant", "content": response.content})
                break


if __name__ == "__main__":
    chat()
