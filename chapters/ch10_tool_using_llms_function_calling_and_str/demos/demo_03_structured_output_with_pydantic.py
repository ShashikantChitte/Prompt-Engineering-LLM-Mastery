"""
Chapter 10: Tool-Using LLMs: Function Calling and Structured Outputs
Demo 3 - Structured Output with Pydantic

Auto-generated from the course document. Run: python demo_03_structured_output_with_pydantic.py
"""
# pip install openai pydantic
from pydantic import BaseModel, Field
from openai import OpenAI
import json

client = OpenAI()

# Define the output schema as a Pydantic model
class CandidateEvaluation(BaseModel):
    candidate_name: str = Field(description="Full name of the candidate")
    technical_score: int = Field(description="Technical skill score from 0 to 10")
    communication_score: int = Field(description="Communication clarity score from 0 to 10")
    hire_recommendation: bool = Field(description="True if candidate should advance to next round")
    summary: str = Field(description="One sentence summary of the evaluation")

# Interview transcript to evaluate
transcript = """
Interviewer: Can you explain how a hash map works?
Candidate: Sure! A hash map stores key-value pairs. When you insert a key, it runs the key through a hash function that converts it to an index in an underlying array. Then the value is stored at that index. Lookup is O(1) average case. Collisions are handled by chaining or open addressing.
Interviewer: What is O(1) mean?
Candidate: It means constant time - the operation takes roughly the same amount of time regardless of how many items are in the map.
"""

# Method 1: JSON mode (model chooses keys)
response_json_mode = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Evaluate this interview transcript. Return JSON only."},
        {"role": "user", "content": transcript}
    ],
    response_format={"type": "json_object"}
)
raw_json = json.loads(response_json_mode.choices[0].message.content)
print("JSON mode output (model chooses schema):")
print(json.dumps(raw_json, indent=2))

print("\n" + "-"*50 + "\n")

# Method 2: Structured output with enforced schema (OpenAI Structured Outputs)
schema = CandidateEvaluation.model_json_schema()
response_structured = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Evaluate this interview transcript. The candidate's name is not given - use 'Unknown'."},
        {"role": "user", "content": transcript}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "CandidateEvaluation",
            "strict": True,
            "schema": schema
        }
    }
)

raw = json.loads(response_structured.choices[0].message.content)
evaluation = CandidateEvaluation(**raw)  # parse into typed object

print("Structured output (schema-enforced, Pydantic-parsed):")
print(f"  Technical score:     {evaluation.technical_score}/10")
print(f"  Communication score: {evaluation.communication_score}/10")
print(f"  Hire recommendation: {evaluation.hire_recommendation}")
print(f"  Summary: {evaluation.summary}")
print(f"\nType of evaluation object: {type(evaluation)}")

# ---------------- Expected output ----------------
# JSON mode output (model chooses schema):
# {
#   "candidate_name": "Unknown",
#   "technical_score": 8,
#   "communication_score": 9,
#   "hire_recommendation": true,
#   "summary": "Strong understanding of hash maps with clear explanation of O(1) complexity."
# }
#
# --------------------------------------------------
#
# Structured output (schema-enforced, Pydantic-parsed):
#   Technical score:     8/10
#   Communication score: 9/10
#   Hire recommendation: True
#   Summary: Strong understanding of hash maps with clear explanation of O(1) complexity.
#
# Type of evaluation object: <class '__main__.CandidateEvaluation'>
