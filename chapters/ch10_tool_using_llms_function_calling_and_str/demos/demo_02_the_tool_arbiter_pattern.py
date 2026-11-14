"""
Chapter 10: Tool-Using LLMs: Function Calling and Structured Outputs
Demo 2 - The Tool Arbiter Pattern

Auto-generated from the course document. Run: python demo_02_the_tool_arbiter_pattern.py
"""
import json
from openai import OpenAI

client = OpenAI()

# Tool registry - maps names to callables
def search_database(query: str, limit: int) -> list:
    """Simulated DB search."""
    return [{"id": 1, "name": "Alice", "score": 92}, {"id": 2, "name": "Bob", "score": 87}][:limit]

TOOL_REGISTRY = {
    "search_database": search_database
}

# Arbiter: validates the model's tool call before execution
class ToolArbiter:
    MAX_LIMIT = 10
    ALLOWED_TOOLS = {"search_database"}

    def validate_and_dispatch(self, tool_call) -> dict:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        # Check 1: tool must be in the allowed list
        if name not in self.ALLOWED_TOOLS:
            return {"error": f"Tool '{name}' is not permitted."}

        # Check 2: argument types and bounds
        if name == "search_database":
            if not isinstance(args.get("query"), str) or not args["query"].strip():
                return {"error": "query must be a non-empty string"}
            limit = args.get("limit", 5)
            if not isinstance(limit, int) or limit < 1 or limit > self.MAX_LIMIT:
                return {"error": f"limit must be an integer between 1 and {self.MAX_LIMIT}"}
            args["limit"] = limit  # normalize

        # Validation passed - dispatch
        print(f"  [Arbiter] Approved: {name}({args})")
        result = TOOL_REGISTRY[name](**args)
        return {"result": result}

arbiter = ToolArbiter()

tools = [{
    "type": "function",
    "function": {
        "name": "search_database",
        "description": "Search student records by name or keyword. Returns matching students.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term"},
                "limit": {"type": "integer", "description": "Max results to return (1-10)", "default": 5}
            },
            "required": ["query"]
        }
    }
}]

# Run the full loop with arbiter in the middle
messages = [{"role": "user", "content": "Find students named Alice in the database."}]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools
)

msg = response.choices[0].message
if response.choices[0].finish_reason == "tool_calls":
    tool_call = msg.tool_calls[0]
    print(f"Model proposed: {tool_call.function.name}({tool_call.function.arguments})")

    # Arbiter validates and dispatches
    outcome = arbiter.validate_and_dispatch(tool_call)
    print(f"Arbiter outcome: {outcome}")

    # Feed result back
    messages.append(msg)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(outcome)
    })

    final = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
    print(f"\nFinal answer: {final.choices[0].message.content}")

# Test the arbiter's rejection path
print("\n--- Testing arbiter rejection ---")
class FakeBadToolCall:
    class function:
        name = "delete_all_records"
        arguments = '{}'
    id = "fake-id"

result = arbiter.validate_and_dispatch(FakeBadToolCall())
print(f"Arbiter blocked: {result}")

# ---------------- Expected output ----------------
# Model proposed: search_database({"query": "Alice"})
#   [Arbiter] Approved: search_database({'query': 'Alice', 'limit': 5})
# Arbiter outcome: {'result': [{'id': 1, 'name': 'Alice', 'score': 92}]}
#
# Final answer: I found 1 student named Alice in the database — Alice (ID 1) with a score of 92.
#
# --- Testing arbiter rejection ---
# Arbiter blocked: {'error': "Tool 'delete_all_records' is not permitted."}

# === What to look at in the output: ===

# The [Arbiter] Approved line fires between the model's proposal and actual tool execution -
# this is exactly the separation of concerns the pattern enforces.

# The rejection test shows the arbiter blocking a tool the model was not allowed to call, with
# no exception and no execution.

# In production this block would log the attempt and could trigger an alert.
