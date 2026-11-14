# Chapter 11 - Part 2: Document Understanding: Analysing screenshots, diagrams, PDFs with vision

> Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem

**Document Understanding** is the use of multimodal AI to read, interpret, and extract structured information from complex files—such as scanned PDFs, invoices, forms, contracts, and handwritten notes—by analyzing both **text and visual layout** together.

Unlike traditional Optical Character Recognition (OCR), which only transcribes raw characters from top to bottom, multimodal Document Understanding sees the entire page as an image so it understands how tables, checkboxes, columns, headers, and signatures relate to one another.

### 1. Traditional OCR vs. Multimodal Document Understanding

| Feature | Traditional OCR Pipeline | Multimodal Document Understanding |
| --- | --- | --- |
| How It Reads | Extracts plain text line-by-line, often scrambling multi-column layouts. | Reads the page visually as image tokens, preserving spatial layout and hierarchy. |
| Tables & Forms | Struggles with merged cells, borderless tables, and misaligned rows. | Understands row-column relationships and pairs labels directly with their values. |
| Visual Elements | Ignores checkboxes, radio buttons, signatures, stamps, and embedded charts. | Detects whether checkboxes are ticked, verifies signatures, and reads charts. |
| Pipeline Complexity | Requires chaining OCR engines, layout detectors, regex rules, and text LLMs. | Handles perception, reasoning, and JSON extraction in a single API call. |

### 2. How Document Understanding Pipelines Work

When processing multi-page documents (like a 50-page PDF), production systems typically follow three steps:

- **Page-to-Image Rasterization:** Each PDF page is converted into a high-resolution image (usually 150–300 DPI) so the vision encoder can clearly read small print and table borders.
- **Multimodal Prompting + Structured Outputs:** The page images are sent to a Vision-Language Model alongside a strict **JSON Schema** (or Pydantic model) defining the exact fields to extract (e.g., invoice_number, line_items, total_amount).
- **Confidence & Verification Checks:** The application validates math totals (e.g., checking if line items add up to the extracted total) and flags low-confidence or blurry pages for human review.

### 3. Common Real-World Use Cases

- **Financial & Invoice Processing:** Extracting vendor details, GST/tax breakdowns, line-item tables, and due dates from varied supplier bills.
- **KYC & Identity Verification:** Reading passports, Aadhaar/PAN cards, and driver's licenses while checking for tampering or glare.
- **Healthcare & Insurance Claims:** Digitizing handwritten doctor prescriptions, lab reports, and multi-page claim forms.
- **Legal & Contract Analysis:** Pulling specific clauses, signature blocks, and renewal dates from scanned agreements.

### 4. Key Challenges & Best Practices

- **Resolution vs. Token Cost:** Very dense pages (like bank statements) need high-resolution image settings so small numbers aren't misread, whereas simple cover pages can use lower resolution to save tokens.
- **Multi-Page Context:** When a table spans across two pages, pass consecutive pages together in the same prompt so the model connects the table headers on Page 1 to the rows on Page 2.
- **Handling Handwriting & Scans:** Skewed, faded, or low-DPI scans increase hallucination risk; pre-processing images (deskewing and boosting contrast) significantly improves accuracy.

```text
Prompting for image analysis
```

**Prompting for image analysis** requires pairing clear visual anchors with structured reasoning steps so a Vision-Language Model (VLM) inspects actual pixels rather than guessing from memory.

### 1. Core Prompting Patterns for Image Analysis

- **Anchor Attention to Specific Regions:** Tell the model exactly where to look using spatial cues (top-left, foreground, background, second row) so it does not overlook small details.
  - *Weak:* "What is wrong with this machine?"
  - *Strong:* "Inspect the pressure gauge in the upper-right quadrant and the wiring harness at the bottom center. Report any readings in the red zone or frayed insulation."
- **Visual Chain-of-Thought (Describe Before Concluding):** Force the model to list objective visual evidence before making a judgment or classification.
  - *Example:* "Step 1: List all visible text, warning labels, and icons on the packaging. Step 2: Based strictly on those labels, determine if the item is flammable."
- **Abstention & Anti-Hallucination Guardrails:** Explicitly instruct the model to report "unreadable" or "not visible" when text is blurry, cut off, or obscured instead of guessing.
  - *Example:* "Extract the serial number from the metal plate. If any character is obscured by glare or rust, output null rather than guessing."
- **Structured Output Enforcement:** Pair your image prompt with a strict JSON Schema or Pydantic model so visual observations map directly into clean, predictable fields for your application.

### 2. Advanced Visual Prompting Techniques

- **Few-Shot Visual Examples:** Pass 1–2 labeled example images before your target image to calibrate subjective judgments (such as grading product scratches as minor vs. severe).
- **Set-of-Mark (Visual Overlays):** Before sending the image to the API, programmatically draw numbered bounding boxes, grids, or arrows onto the image so your prompt can reference items cleanly (e.g., *"Compare the alignment of object #2 relative to object #5"*).
- **Multi-Image Comparison:** When comparing "before and after" photos or checking product defects against a golden sample, label each image clearly in the prompt ([Image 1: Reference Standard], [Image 2: Factory Unit]) and ask for a field-by-field diff.

### 3. Pre-Prompt Image Preparation (Context Engineering)

- **Crop to Region of Interest:** If you only care about a small barcode or signature, crop the image before sending it so the model dedicates all its image tokens to that exact area.
- **Choose the Right Detail Level:** Use low-resolution settings for fast, broad classification (e.g., *"Is this a daytime or nighttime photo?"*) and high-resolution settings for dense charts, receipts, or fine defect inspection.
- **Fix Orientation First:** Rotate sideways or upside-down scans upright before calling the model, as VLMs drop significantly in OCR accuracy on rotated text.

```text
PDF + Vision
```

**PDF + Vision** (often called **Vision-based PDF Parsing** or **Multimodal RAG**) is the technique of converting PDF pages into images and feeding them directly to a Vision-Language Model (VLM) instead of extracting raw text with traditional Python libraries like pypdf or pdfplumber.

### 1. Why Use Vision Instead of Text Extraction for PDFs?

Traditional text extractors read underlying character streams, which breaks down on complex real-world documents:

- **Preserves Complex Layouts:** Multi-column academic papers, financial statements, and nested tables stay visually intact rather than getting scrambled into unreadable text strings.
- **Reads Scanned & Handwritten PDFs:** Scanned documents contain zero selectable text, making vision models essential for reading them without a separate OCR engine.
- **Understands Visual Elements:** Charts, bar graphs, flowcharts, architectural diagrams, checkboxes, and signatures are interpreted directly alongside surrounding paragraphs.

### 2. Two Ways to Send PDFs to Multimodal Models

| Approach | How It Works | Best Used For |
| --- | --- | --- |
| Native PDF Upload (API File Input) | Some modern APIs (such as Gemini or Claude) accept raw .pdf files directly, automatically rasterizing each page into image tokens and extracting embedded text under the hood. | Quick prototyping, short-to-medium documents (under ~100 pages), and zero-preprocessing workflows. |
| Manual Page-to-Image Rendering | You convert each PDF page into a PNG/JPEG image locally (using tools like PyMuPDF / fitz or pdf2image) and send selected pages as image inputs. | Production pipelines where you need custom DPI control, page filtering, cropping, or multi-provider compatibility. |

### 3. Production Pipeline Best Practices

- **Control DPI Carefully:** Render pages at **150–200 DPI** for standard text documents and **300 DPI** for dense financial tables or tiny footnotes. Higher DPI improves accuracy but increases image token cost and latency.
- **Filter Before Sending (Page Triage):** For a 200-page PDF, avoid sending every page at high resolution. Use a fast text search or low-resolution pass to find the relevant pages first, then send only those target pages at high resolution.
- **Handle Cross-Page Tables:** Tables and clauses frequently split across page boundaries. Pass consecutive pages together in a single prompt (e.g., [Page 4, Page 5]) and instruct the model to merge split rows.
- **Enforce Structured Outputs:** Always pair PDF page images with a strict JSON Schema or Pydantic model, including a page_number citation field so you can trace every extracted fact back to its exact source page.
