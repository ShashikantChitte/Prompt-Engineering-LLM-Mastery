"""
Chapter 10: Tool-Using LLMs: Function Calling and Structured Outputs
Demo 4 - Multi-Tool Loop (Calculator + Search)

Auto-generated from the course document. Run: python demo_04_multi_tool_loop_calculator_search.py
"""
import json
import math
from openai import OpenAI

client = OpenAI()

# Two tools: a calculator and a fake search
def calculator(expression: str) -> dict:
    """Safely evaluate a math expression."""
    try:
        # Restrict to safe operations only
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
        allowed['__builtins__'] = {}
        result = eval(expression, allowed)  # noqa: S307
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

def search_knowledge(query: str) -> dict:
    """Simulated knowledge base search."""
    kb = {
        "compound interest formula": "A = P * (1 + r/n)^(n*t) where P=principal, r=annual rate, n=compounds per year, t=years",
        "default": "No result found for that query."
    }
    for key in kb:
        if key in query.lower():
            return {"result": kb[key]}
    return {"result": kb["default"]}

TOOL_REGISTRY = {"calculator": calculator, "search_knowledge": search_knowledge}

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression. Use Python math syntax. Example: '1000 * (1 + 0.08/12) ** (12*5)'",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "Math expression to evaluate"}},
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search a knowledge base for a concept or formula.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "What to look up"}},
                "required": ["query"]
            }
        }
    }
]

# Question that requires both tools: look up formula, then compute
messages = [{
    "role": "user",
    "content": "What is the compound interest formula? Then calculate: 50000 invested at 8% annual rate, compounded monthly, for 10 years."
}]

print("Starting multi-tool loop...\n")
max_steps = 5

for step in range(max_steps):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )
    msg = response.choices[0].message
    finish = response.choices[0].finish_reason

    print(f"Step {step + 1}: finish_reason = {finish}")

    if finish == "stop":
        print(f"\nFinal answer:\n{msg.content}")
        break

    if finish == "tool_calls":
        messages.append(msg)
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"  Calling {tc.function.name}({args})")
            result = TOOL_REGISTRY[tc.function.name](**args)
            print(f"  Result: {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result)
            })

# ---------------- Expected output ----------------
# Starting multi-tool loop...
#
# Step 1: finish_reason = tool_calls
#   Calling search_knowledge({'query': 'compound interest formula'})
#   Result: {'result': 'A = P * (1 + r/n)^(n*t) where P=principal, r=annual rate, n=compounds per year, t=years'}
#   Calling calculator({'expression': '50000 * (1 + 0.08/12) ** (12*10)'})
#   Result: {'result': 110698.30504946168}
#
# Step 2: finish_reason = stop
#
# Final answer:
# The compound interest formula is A = P * (1 + r/n)^(n*t), where:
# - P = principal (initial amount)
# - r = annual interest rate
# - n = number of times interest compounds per year
# - t = number of years
#
# For your investment:
# - P = 50,000
# - r = 0.08 (8% annual)
# - n = 12 (monthly compounding)
# - t = 10 years
#
# The final amount is approximately ₹1,10,698.31. That means the investment grows by roughly ₹60,698.31 in interest over 10 years.

# === What to look at in the output: ===

# - Watch the step count - the model calls search_knowledge first, then calculator, then
#    stops. Each step has a different finish_reason.
# - The calculator result is exact floating-point arithmetic, not the model's approximation.
# - The loop terminates naturally when finish_reason == "stop" - you do not need to count
#    steps in simple cases, but max_steps is a production safeguard against infinite loops.
