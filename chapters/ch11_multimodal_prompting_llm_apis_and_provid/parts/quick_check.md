# Chapter 11: Quick Check

**1. A 1024x1024 image sent with detail: high costs more input tokens than the same image sent with detail: low. Why - what is the model actually doing differently in each mode?**

A 1024×1024 image sent with detail: high costs significantly more input tokens than detail: low because detail: low shrinks the entire image into a single low-resolution thumbnail, whereas detail: high slices the image into a grid of separate high-resolution tiles and encodes every tile individually.

What the Model Does in Each Mode

* **detail: low (Single Global Overview):**
  * **Resizing:** The API immediately downsamples the 1024×1024 image into a single fixed 512×512 thumbnail.
  * **Tokenization:** Only that one 512×512 square is passed through the vision encoder, generating a flat, fixed token budget (typically 85 tokens in OpenAI's vision pricing).
  * **Trade-off:** Fine details like small text, serial numbers, or dense chart labels become blurry and unreadable, though broad shapes, colors, and overall scene context remain clear.
* **detail: high (Global Thumbnail + High-Res Tile Grid):**
  * **Step 1 — Global Context Thumbnail:** First, the model still creates the same downsampled 512×512 overview image (85 tokens) so it understands the big picture and how everything connects spatially.
  * **Step 2 — High-Res Tiling:** Next, the API takes the full 1024×1024 image and slices it into a 2×2 grid of four 512×512 square tiles (four quadrants: top-left, top-right, bottom-left, bottom-right).
  * **Step 3 — Per-Tile Encoding:** Each of those four 512×512 tiles is encoded at full crisp resolution (costing 170 tokens per tile × 4 tiles = 680 tokens).
  * **Total Token Cost:** 85 (overview) + 680 (4 tiles) = 765 input tokens—exactly 9× more tokens than detail: low for the exact same 1024×1024 image.

Summary Comparison (1024×1024 Image)

| Setting | Image Processing Steps | Visual Detail Preserved | Typical Input Token Cost |
| :--- | :--- | :--- | :--- |
| detail: low | Downsampled to one 512×512 image | Broad scene, objects, and colors only; fine text is lost | 85 tokens (flat cost) |
| detail: high | One 512×512 overview + four 512×512 high-res crops | Full native sharpness across every quadrant for OCR, tables, and charts | 765 tokens (85 + 4 × 170) |

---

**2. You are building a tool that reads scanned receipts to extract the total amount. During testing, the model sometimes returns 87.50 when the receipt shows 87.60. What is the likely cause and how would you work around it?**

Misreading 87.60 as 87.50 happens because small, low-contrast, or crumpled receipt characters get compressed during vision patch encoding, making visually similar digits (6 vs 5, or 8 vs 0) blur together so the model falls back on statistical guessing.

**1. Likely Causes**

* **Insufficient Image Resolution / Patch Compression:** Vision encoders slice images into small pixel patches (e.g., 14×14 pixels). On thermal paper receipts, faded ink, low DPI scans, or detail: low settings blur the tiny gap in a 6, making it look identical to a 5.
* **Visual Noise & Skew:** Receipt creases, shadows, background clutter, or tilted angles distort character shapes across patch boundaries.
* **Lack of Cross-Verification:** Extracting only the final total field in isolation prevents the model from checking whether the numbers actually add up mathematically.

**2. How to Work Around It (Engineering & Prompting Fixes)**

* **Image Preprocessing & Resolution Controls:**
  * Force detail: high (High Resolution): Ensure the API runs in high-detail tile mode rather than downsampling the receipt into a blurry thumbnail.
  * Crop & Deskew Before Sending: Automatically crop out empty background space around the receipt and straighten tilted scans so maximum pixel resolution is dedicated to the text.
  * Enhance Contrast: Convert faded thermal scans to high-contrast grayscale or apply adaptive thresholding so faint ink strokes stand out sharply.
* **Prompting & Schema Workarounds (Math Self-Verification):**
  * Extract Line Items + Subtotal + Tax First: Design your Pydantic/JSON schema to extract all line_items, subtotal, and tax before the total_amount field. Because LLMs generate tokens left-to-right, extracting the components first anchors the model's reasoning to the true sum (87.60).
  * Add a Verification Field: Include a math_check_notes or calculated_sum field in your schema instructing the model to sum the extracted line items and compare them against the printed total.
* **Deterministic Code Validation (Post-Processing):**
  * Programmatic Arithmetic Check: In your Python code, sum the extracted line_items + tax and compare it against total_amount. If calculated_total != extracted_total (e.g., 87.60 != 87.50), flag the receipt for a high-resolution re-crop retry or human-in-the-loop review.

---

**3. Write the key structural differences between an OpenAI chat.completions.create call and an Anthropic messages.create call. Name at least three fields that differ.**

The core structural difference between OpenAI's chat.completions.create and Anthropic's messages.create is how they handle system instructions, required token limits, and content block formatting. OpenAI places system instructions inside the messages list and treats max_tokens as optional, whereas Anthropic separates system instructions into a top-level parameter, mandates max_tokens, and enforces strict user/assistant message alternation.

Key Structural Differences (Side-by-Side)

| Request / Response Field | OpenAI (client.chat.completions.create) | Anthropic (client.messages.create) |
| :--- | :--- | :--- |
| 1. system Instructions | Passed inside the messages array as the first item with {"role": "system", "content": "..."} (or role: "developer"). | Passed as a top-level parameter (system="...") completely outside the messages array. |
| 2. max_tokens | Optional. If omitted, the model generates up to its default maximum output limit. | Strictly Required. Omitting max_tokens raises an immediate 400 Bad Request validation error. |
| 3. Tool Definitions & Results | Tools use parameters inside a nested function object. Tool outputs are sent back as a separate message with role: "tool" and tool_call_id. | Tools use input_schema at the top level of the tool dict. Tool outputs are sent back inside a role: "user" message containing a tool_result content block (tool_use_id). |
| 4. Response Text Location | Nested inside a choices list: response.choices[0].message.content (a plain string). | Nested inside a typed content block array: response.content[0].text (alongside thinking or tool_use blocks). |
| 5. Message Role Alternation | Flexible; allows consecutive user messages or starting with system. | Strictly requires user and assistant roles to alternate (and the first message must be role: "user"). |

Side-by-Side Code Comparison

**OpenAI (chat.completions.create):**

```python
response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Be concise."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
