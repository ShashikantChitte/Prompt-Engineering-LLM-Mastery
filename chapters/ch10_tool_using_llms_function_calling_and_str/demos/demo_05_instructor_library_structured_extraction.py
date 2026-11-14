"""
Chapter 10: Tool-Using LLMs: Function Calling and Structured Outputs
Demo 5 - instructor Library: Structured Extraction from Free Text

Auto-generated from the course document. Run: python demo_05_instructor_library_structured_extraction.py
"""
# pip install instructor openai pydantic
import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional

# instructor patches the OpenAI client - one line change from standard usage
client = instructor.from_openai(OpenAI())

# Define the schema you want to extract
class JobPosting(BaseModel):
    role: str = Field(description="Job title")
    company: Optional[str] = Field(description="Company name if mentioned")
    required_skills: list[str] = Field(description="List of required technical skills")
    experience_years: Optional[int] = Field(description="Required years of experience")
    is_remote: bool = Field(description="True if the role is fully remote")

# Raw free text - no structure, no labels
free_text = """
We are looking for a Senior Backend Engineer at Razorpay to join our payments
infrastructure team. Must have 5+ years with Go or Python. Strong understanding
of distributed systems and Kafka required. PostgreSQL experience a plus.
This is a hybrid role, 3 days from our Bangalore office.
"""

# instructor handles schema conversion, API call, validation, and retries
posting = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=JobPosting,
    messages=[{"role": "user", "content": f"Extract job posting details:\n\n{free_text}"}]
)

print(f"Role:        {posting.role}")
print(f"Company:     {posting.company}")
print(f"Skills:      {posting.required_skills}")
print(f"Experience:  {posting.experience_years} years")
print(f"Remote:      {posting.is_remote}")
print(f"\nType: {type(posting)}")  # a real Python object, not a dict

# ---------------- Expected output ----------------
# Role:        Senior Backend Engineer
# Company:     Razorpay
# Skills:      ['Go', 'Python', 'Distributed Systems', 'Kafka', 'PostgreSQL']
# Experience:  5 years
# Remote:      False
#
# Type: <class '__main__.JobPosting'>
