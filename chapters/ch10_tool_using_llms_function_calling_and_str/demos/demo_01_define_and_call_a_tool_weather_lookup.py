"""
Chapter 10: Tool-Using LLMs: Function Calling and Structured Outputs
Demo 1 - Define and Call a Tool (Weather Lookup)

Auto-generated from the course document. Run: python demo_01_define_and_call_a_tool_weather_lookup.py
"""
# pip install openai
import json
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from environment

# Step 1: Define the tool schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city. Returns temperature in Celsius and a condition string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'Bangalore'"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# Step 2: First API call - model decides to use the tool
messages = [{"role": "user", "content": "What is the weather in Bangalore right now?"}]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools
)

first_message = response.choices[0].message
print("Model's response (raw):")
print(f"  finish_reason: {response.choices[0].finish_reason}")
print(f"  tool_calls: {first_message.tool_calls}")

# Step 3: Extract the tool call and simulate execution
tool_call = first_message.tool_calls[0]
tool_name = tool_call.function.name
tool_args = json.loads(tool_call.function.arguments)
print(f"\nModel wants to call: {tool_name}({tool_args})")

# Simulate the real tool (in production this calls a real weather API)
def get_weather(city: str) -> dict:
    return {"city": city, "temperature_c": 28, "condition": "partly cloudy"}

tool_result = get_weather(**tool_args)
print(f"Tool returned: {tool_result}")

# Step 4: Feed result back and get final response
messages.append(first_message)  # append the assistant's tool call
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": json.dumps(tool_result)
})

final_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools
)

print(f"\nFinal answer: {final_response.choices[0].message.content}")

# ---------------- Expected output ----------------
# Model's response (raw):
#   finish_reason: tool_calls
#   tool_calls: [ChatCompletionMessageToolCall(id='call_abc123...', function=Function(arguments='{"city":"Bangalore"}', name='get_weather'), type='function')]
#
# Model wants to call: get_weather({'city': 'Bangalore'})
# Tool returned: {'city': 'Bangalore', 'temperature_c': 28, 'condition': 'partly cloudy'}
#
# Final answer: The current weather in Bangalore is 28°C and partly cloudy.
