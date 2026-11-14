# Chapter 11 - Part 1: Vision Prompting: How multimodal models process images, image tokens, what models can and cannot reliably see

> Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem

**Vision Prompting** is the practice of crafting inputs that combine images (or video frames) alongside text instructions to guide a multimodal Large Language Model (VLM) in analyzing, interpreting, or extracting data from visual content.

Just like text-only prompting, the quality of a VLM's output depends heavily on how clearly you frame the visual context and your text instructions.

## Core Techniques in Vision Prompting

- **Be Specific About Where to Look:** Direct the model's attention to exact regions, objects, or corners of the image (e.g., *"Read the serial number in the bottom-right corner"* instead of *"What does this say?"*).
- **Combine with Structured Outputs:** Pair images with a strict JSON Schema or Pydantic model to reliably turn unstructured visuals—like receipts, invoices, or handwritten forms—into clean database records.
- **Use Few-Shot Visual Examples:** Provide 1 or 2 sample image-and-answer pairs in the prompt before your target image to teach the model exact formatting, classification labels, or edge-case rules.
- **Apply Visual Chain-of-Thought (CoT):** Ask the model to describe what it sees step-by-step before drawing a conclusion (e.g., *"First list every component visible on the circuit board, then identify which part appears damaged"*).
- **Use Visual Grounding (Bounding Boxes & Markers):** Draw boxes, arrows, or numbered labels directly onto an image before sending it (a technique known as **Set-of-Mark prompting**) so you can reference items unambiguously like *"What is inside box #3?"*.

## Common Use Cases

- **Document & OCR Extraction:** Parsing tables, receipts, ID cards, and complex multi-column PDFs where traditional OCR fails.
- **UI & Frontend Debugging:** Passing a screenshot of a broken webpage or app layout to identify CSS bugs or generate matching HTML/React code.
- **Visual Quality Inspection:** Checking product photos for defects, verifying shelf inventory, or analyzing medical and satellite imagery.

## Best Practices for Image Inputs

- **Optimize Resolution & Cropping:** High-resolution images capture fine text better, while cropping out irrelevant background noise reduces token costs and prevents hallucinations.
- **Avoid Spatial Guessing:** VLMs can struggle with exact pixel coordinates or counting dense, overlapping objects unless you guide them with grids or step-by-step counting instructions.

## How multimodal models process images, image tokens, what models can and cannot reliably see

Multimodal Large Language Models (VLMs) process images by converting pixels into visual embeddings (image tokens) that sit in the same mathematical space as text tokens, allowing a single Transformer architecture to reason across both modalities simultaneously.

### 1. How Multimodal Models Process Images

Most modern Vision-Language Models follow a three-stage pipeline:

- **Vision Encoder (e.g., ViT / CLIP):** An image is fed into a Vision Transformer (ViT), which slices the picture into a grid of small square patches (such as 14×14 or 16×16 pixels) and converts each patch into a numerical vector.
- **Multimodal Projector (Adapter):** Because a vision encoder and a text LLM speak different mathematical "languages," a projection layer (like an MLP or Q-Former) translates those visual patch vectors into the exact same embedding dimension as the LLM's word tokens.
- **Unified Transformer Backbone:** Once projected, the image tokens are concatenated directly alongside your text prompt tokens, allowing the LLM's self-attention mechanism to read image patches and words together.

### 2. Understanding Image Tokens

Just like words are broken into text tokens, images are broken into **image tokens**, which directly govern both model intelligence and API cost:

- **Resolution & Patch Tiling:** Low-resolution modes shrink an image into a single fixed square (often costing a flat rate like 85 tokens), whereas high-resolution modes slice a large image into multiple detailed crops or tiles—each generating hundreds of additional tokens.
- **Detail vs. Cost & Latency:** More image tokens preserve crisp details like small text and chart axes, while fewer tokens keep inference fast and inexpensive for simple tasks like broad object classification.
- **Context Window Consumption:** Every image tile consumes space inside the model's context window, meaning high-resolution multi-image prompts can quickly fill token limits.

### 3. What Models Can and Cannot Reliably See

| What Models See Reliably | What Models Struggle With (Blind Spots) |
| --- | --- |
| Semantic Content & Context: Identifying objects, scenes, animals, emotions, styles, and brand logos. | **Exact Spatial Coordinates:** Estimating precise pixel locations, exact distances, or subtle geometric angles. |
| Clear Printed Text (OCR): Reading structured documents, receipts, signs, and screenshots with high accuracy. | **Dense Counting:** Accurately counting large numbers of overlapping, tiny, or tightly packed items (e.g., crowds or pills). |
| High-Level Chart & UI Trends: Interpreting bar charts, line trends, and website layouts. | **Tiny, Blurry, or Rotated Text:** Reading low-resolution watermarks, upside-down labels, or heavily stylized handwriting. |
| Cross-Modal Reasoning: Connecting visual clues to world knowledge (e.g., diagnosing a plant disease from a leaf photo). | **Optical Illusions & Visual Priors:** Relying on memorized expectations rather than actual pixels (e.g., hallucinating a 5th finger or misreading an altered famous logo). |

## Where multimodal came from and why it matters

Multimodal AI emerged from the need to break down the walls between separate, single-purpose AI models (like text-only NLP models and image-only computer vision models) so machines can perceive and reason across text, images, audio, and video simultaneously—just like humans do.

### 1. Where Multimodal AI Came From (Evolution)

Multimodal models evolved through four major breakthroughs:

- **Siloed Single-Modality Era (Pre-2017):** Text models (RNNs) and vision models (CNNs) were trained completely separately on narrow tasks like translation or object detection, with no shared understanding of concepts across formats.
- **The Transformer Architecture (2017):** Originally built for text, the self-attention mechanism proved universal—capable of finding relationships between any sequence of tokens, whether words, image patches, or audio waves.
- **Vision-Language Alignment — CLIP (2021):** OpenAI’s CLIP trained on 400 million image-text pairs from the web, teaching a model to map matching images and captions into the **exact same mathematical vector space** (shared embeddings).
- **Native & Unified Multimodal LLMs (2023–Present):** Early systems bolted vision encoders onto existing text LLMs (like LLaVA and GPT-4V), which quickly evolved into **natively multimodal models** (like Gemini and GPT-4o) trained from scratch on interleaved text, images, audio, and video tokens together.

### 2. Why Multimodal AI Matters

Moving beyond text-only AI fundamentally expands what software can automate and understand:

- **Unlocking Unstructured Real-World Data:** Most real-world information isn't clean text—it lives in scanned PDFs, handwritten forms, medical X-rays, charts, engineering blueprints, and security camera feeds.
- **Eliminating Fragile Pipelines:** Previously, extracting data from a receipt required chaining separate OCR software, layout parsers, and text LLMs—where one error broke the whole pipeline. A single multimodal model reads the layout and text natively in one step.
- **Human-Like Interaction & Accessibility:** Users can interact naturally by showing a model a broken appliance via camera, sharing a screenshot of a software bug, or speaking aloud while pointing at a diagram.
- **Embodied AI & Robotics:** For AI agents and robots to navigate physical spaces, drive cars, or use computer interfaces (GUI agents), they must continuously see their environment and act on visual feedback.

## How images become tokens

Images become tokens by slicing a picture into a grid of small square patches and converting each patch's pixel values into a mathematical vector (embedding) that matches the exact format of word tokens.

Here is the step-by-step pipeline of how raw pixels turn into tokens inside a multimodal model:

### 1. Slicing into Patches (Patchification)

- **Grid Division:** Instead of reading an image one pixel at a time (which would create millions of tokens), a **Vision Transformer (ViT)** divides the image into a neat grid of non-overlapping squares—typically **14×14** or **16×16 pixels** each.
- **High-Resolution Tiling:** If an image is very large, modern models first crop it into several smaller high-resolution "tiles" (for example, 512×512 squares) alongside one shrunk-down thumbnail of the full image so both fine details and the big picture are preserved.

### 2. Linear Projection (Pixels to Numbers)

- **Flattening:** Each square patch contains raw Red, Green, and Blue (RGB) pixel numbers. The model flattens those numbers into a single long list of values.
- **Patch Embedding:** A mathematical layer multiplies those pixel values to compress them into a dense vector (an embedding), much like turning a word into a word vector.

### 3. Adding Positional Embeddings

- **Tracking Location:** Because a Transformer processes tokens all at once rather than left-to-right, the model attaches a **positional embedding** (coordinate tag) to every patch vector. This tells the model whether a patch came from the top-left corner, the center, or the bottom-right edge.

### 4. Multimodal Projection (Translating to "LLM Language")

- **Dimension Alignment:** The vectors coming out of the Vision Encoder live in a "visual vector space" and often have a different size than the LLM's text embeddings.
- **The Adapter Layer:** A small neural network (called a **Multimodal Projector** or **MLP Adapter**) translates and resizes each visual patch vector so its dimensions match the LLM's text tokens exactly.

### 5. Sequence Concatenation

- **Unified Input:** Finally, those translated image tokens are dropped right into the prompt sequence alongside your text tokens (e.g., [Image Token 1, Image Token 2, ..., "Describe", "this", "chart"]). From this point forward, the LLM's attention layers treat the image patches just like words.

## What models can and cannot reliably see

Vision-Language Models (VLMs) excel at high-level semantic comprehension, clear document reading, and contextual reasoning, but struggle with tasks requiring **pixel-level precision, spatial geometry, or dense counting** because slicing an image into compressed patches discards fine spatial relationships.

## What Models Can Reliably See

- **High-Level Scenes & Object Recognition:** Models accurately identify everyday objects, animals, environments, human activities, clothing styles, and artistic mediums.
- **Clear Printed Text & Structured Documents:** They reliably read clean text from screenshots, signs, receipts, invoices, and multi-column PDFs, preserving layout context like table rows and columns.
- **Charts, Diagrams & UI Layouts:** Models interpret bar charts, line graph trends, flowcharts, and website wireframes well enough to summarize data or generate matching HTML/CSS code.
- **Contextual & Cross-Modal Clues:** They combine visual details with world knowledge—such as identifying a landmark from architectural clues, diagnosing plant issues from leaf discoloration, or spotting a missing safety helmet on a construction site.

## What Models Cannot Reliably See (Core Blind Spots)

- **Dense Counting:** When an image contains dozens of small, overlapping, or identical items (such as pills in a bottle, bricks in a wall, or people in a crowd), models frequently guess or drift off count.
- **Exact Spatial Coordinates & Geometry:** Models struggle to measure exact pixel distances, read subtle analog clock hands, judge precise angles, or tell whether two lines are strictly parallel.
- **Tiny, Blurry, or Rotated Text:** Low-resolution watermarks, distant street signs, upside-down labels, and messy cursive handwriting often fall below the patch resolution of the vision encoder, leading to hallucinated words.
- **Subtle Visual Differences ("Spot the Difference"):** Comparing two nearly identical images to catch a missing screw, a single altered pixel, or a minor UI shift is unreliable because patch embeddings compress away tiny local variations.
- **Optical Illusions & Strong Visual Priors:** When an image contradicts what the model *expects* to see (such as a six-fingered hand, a modified famous logo, or an upside-down face), strong language and training priors often override the actual pixels.
