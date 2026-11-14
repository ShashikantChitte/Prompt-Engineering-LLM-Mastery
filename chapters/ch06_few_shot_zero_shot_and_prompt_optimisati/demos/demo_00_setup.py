"""
Chapter 6: Few-Shot, Zero-Shot and Prompt Optimisation (Advanced)
Demo 0 - Setup

Auto-generated from the course document. Run: python demo_00_setup.py
"""
import dspy
lm = dspy.LM("openai/gpt-4o-mini")
dspy.configure(lm=lm)
# Define the task signature: what goes in, what comes out
class ClassifyIntent(dspy.Signature):
    """Classify the intent of a customer support message."""
    message: str = dspy.InputField()
    intent: str = dspy.OutputField(desc="one of: billing, technical, general")
# Define the module - DSPy handles the prompt internally
classifier = dspy.Predict(ClassifyIntent)
result = classifier(message="My invoice shows the wrong amount")
print(result.intent)  # billing
# To optimize: give it examples and a metric, then compile
trainset = [dspy.Example(message="...", intent="billing").with_inputs("message")]
optimizer = dspy.BootstrapFewShot(metric=lambda ex, pred, **_: ex.intent == pred.intent)
optimized = optimizer.compile(classifier, trainset=trainset)
# Setup - run this first
# !pip install openai scikit-learn numpy --quiet

import os
from openai import OpenAI

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"  # replace with your key
client = OpenAI()

print("Setup complete.")
