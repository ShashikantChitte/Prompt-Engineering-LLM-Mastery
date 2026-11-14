# Prompt Engineering & LLM Mastery

Markdown notes and runnable Python demos generated from the course document. Each chapter has one folder with a README, one Markdown file per part, a Quick Check file, and a `demos/` folder.

## Layout

```text
README.md
requirements.txt
.env.example
assets/images/                 diagrams and figures used by the notes
chapters/
  chNN_<chapter>/
    README.md                  chapter overview and links
    parts/part_NN_<part>.md    one file per part
    quick_check.md             questions and answers
    demos/demo_NN_<demo>.py    one script per code demo
  _unassigned/                 content that did not fit a chapter (review)
```

## Chapters

### Chapter 1: Introduction

- Part 1: [Artificial Intelligence](chapters/ch01_introduction/parts/part_01_artificial_intelligence.md)
- Part 2: [Machine Learning](chapters/ch01_introduction/parts/part_02_machine_learning.md)
- Part 3: [Deep Learning](chapters/ch01_introduction/parts/part_03_deep_learning.md)
- Part 4: [Generative AI](chapters/ch01_introduction/parts/part_04_generative_ai.md)
- Part 5: [Large Language Model](chapters/ch01_introduction/parts/part_05_large_language_model.md)
- Part 6: [Natural Language Processing (NLP)](chapters/ch01_introduction/parts/part_06_natural_language_processing_nlp.md)

### Chapter 2: AI Tools Landscape

- Part 1: [The LLM Landscape: ChatGPT, Claude, Gemini](chapters/ch02_ai_tools_landscape/parts/part_01_the_llm_landscape_chatgpt_claude_gemini.md)
- Part 2: [Coding Assistants: GitHub Copilot vs Cursor](chapters/ch02_ai_tools_landscape/parts/part_02_coding_assistants_github_copilot_vs_cursor.md)
- Part 3: [Real-World Applications Across Roles](chapters/ch02_ai_tools_landscape/parts/part_03_real_world_applications_across_roles.md)
- Part 4: [No-Code AI Tools: Bolt, Lovable, V0, n8n](chapters/ch02_ai_tools_landscape/parts/part_04_no_code_ai_tools_bolt_lovable_v0_n8n.md)
- [Quick Check](chapters/ch02_ai_tools_landscape/quick_check.md)
- Demo 0: [Install dependencies](chapters/ch02_ai_tools_landscape/demos/demo_00_install_dependencies.py)
- Demo 1: [Set API keys](chapters/ch02_ai_tools_landscape/demos/demo_01_set_api_keys.py)
- Demo 2: [Call OpenAI's GPT-4o](chapters/ch02_ai_tools_landscape/demos/demo_02_call_openai_s_gpt_4o.py)
- Demo 3: [Call Anthropic's Claude with the same prompt](chapters/ch02_ai_tools_landscape/demos/demo_03_call_anthropic_s_claude_with_the_same_pr.py)
- Demo 4: [Side-by-Side Comparison](chapters/ch02_ai_tools_landscape/demos/demo_04_side_by_side_comparison.py)
- Demo 5: [Try a Different Prompt (Optional Extension)](chapters/ch02_ai_tools_landscape/demos/demo_05_try_a_different_prompt_optional_extensio.py)

### Chapter 3: What is an LLM? + Transformers and How They Work

- Part 1: [What an LLM actually is (the idea, before the architecture)](chapters/ch03_what_is_an_llm_transformers_and_how_they/parts/part_01_what_an_llm_actually_is_the_idea_before_the.md)
- Part 2: [NLP history: word2vec → RNN/LSTM → the sequential bottleneck that broke everything](chapters/ch03_what_is_an_llm_transformers_and_how_they/parts/part_02_nlp_history_word2vec_rnn_lstm_the_sequential.md)
- Part 3: [Attention is All You Need: what Vaswani et al. 2017 actually figured out](chapters/ch03_what_is_an_llm_transformers_and_how_they/parts/part_03_attention_is_all_you_need_what_vaswani_et_al.md)
- Part 4: [Transformer architecture: self-attention mechanics, encoder-only vs decoder-only](chapters/ch03_what_is_an_llm_transformers_and_how_they/parts/part_04_transformer_architecture_self_attention_mech.md)
- Part 5: [KV Cache: prefill phase, decode phase, and why it matters for latency](chapters/ch03_what_is_an_llm_transformers_and_how_they/parts/part_05_kv_cache_prefill_phase_decode_phase_and_why.md)
- Part 6: [Inference optimisations: Flash Attention, continuous batching](chapters/ch03_what_is_an_llm_transformers_and_how_they/parts/part_06_inference_optimisations_flash_attention_cont.md)
- Part 7: [Mixture of Experts (MoE): how GPT-4, Mistral, and Gemini avoid paying full compute cost](chapters/ch03_what_is_an_llm_transformers_and_how_they/parts/part_07_mixture_of_experts_moe_how_gpt_4_mistral_and.md)
- Part 8: [Reasoning models: o1/o3/Claude Extended Thinking - compute at inference time](chapters/ch03_what_is_an_llm_transformers_and_how_they/parts/part_08_reasoning_models_o1_o3_claude_extended_think.md)
- [Quick Check](chapters/ch03_what_is_an_llm_transformers_and_how_they/quick_check.md)
- Demo 0: [Setup](chapters/ch03_what_is_an_llm_transformers_and_how_they/demos/demo_00_setup.py)
- Demo 1: [Attention Cost Scaling (O(n^2) visualised)](chapters/ch03_what_is_an_llm_transformers_and_how_they/demos/demo_01_attention_cost_scaling_o_n_2_visualised.py)
- Demo 2: [Self-Attention from Scratch](chapters/ch03_what_is_an_llm_transformers_and_how_they/demos/demo_02_self_attention_from_scratch.py)
- Demo 3: [KV Cache Speedup Simulation](chapters/ch03_what_is_an_llm_transformers_and_how_they/demos/demo_03_kv_cache_speedup_simulation.py)
- Demo 4: [Token Generation Timing](chapters/ch03_what_is_an_llm_transformers_and_how_they/demos/demo_04_token_generation_timing.py)

### Chapter 4: Tokenization and Token Management

- Part 1: [Why tokenization exists - models never see words, only integers](chapters/ch04_tokenization_and_token_management/parts/part_01_why_tokenization_exists_models_never_see_wor.md)
- Part 2: [Byte-Pair Encoding (BPE) - how the algorithm builds a vocabulary from scratch](chapters/ch04_tokenization_and_token_management/parts/part_02_byte_pair_encoding_bpe_how_the_algorithm_bui.md)
- Part 3: [WordPiece - BERT's approach and how it differs from BPE](chapters/ch04_tokenization_and_token_management/parts/part_03_wordpiece_bert_s_approach_and_how_it_differs.md)
- Part 4: [Why the same word costs different tokens in different contexts](chapters/ch04_tokenization_and_token_management/parts/part_04_why_the_same_word_costs_different_tokens_in.md)
- Part 5: [Context window limits - hard limits, soft limits, and the LostInTheMiddle failure](chapters/ch04_tokenization_and_token_management/parts/part_05_context_window_limits_hard_limits_soft_limit.md)
- [Quick Check](chapters/ch04_tokenization_and_token_management/quick_check.md)
- Demo 1: [Setup](chapters/ch04_tokenization_and_token_management/demos/demo_01_setup.py)
- Demo 2: [Basic Tokenization: Seeing the Integer Sequence](chapters/ch04_tokenization_and_token_management/demos/demo_02_basic_tokenization_seeing_the_integer_se.py)
- Demo 3: [Same Information, Different Token Counts (Non-English Cost)](chapters/ch04_tokenization_and_token_management/demos/demo_03_same_information_different_token_counts.py)
- Demo 4: [How Numbers Tokenize (Unpredictable Splits)](chapters/ch04_tokenization_and_token_management/demos/demo_04_how_numbers_tokenize_unpredictable_split.py)
- Demo 5: [Context Window: Token Counting Before You Send](chapters/ch04_tokenization_and_token_management/demos/demo_05_context_window_token_counting_before_you.py)
- Demo 6: [Cost Estimation with tiktoken](chapters/ch04_tokenization_and_token_management/demos/demo_06_cost_estimation_with_tiktoken.py)
- Demo 7: [LostInTheMiddle: Position Matters](chapters/ch04_tokenization_and_token_management/demos/demo_07_lostinthemiddle_position_matters.py)
- Demo 8: [Prompt Compression: Measuring Token Reduction](chapters/ch04_tokenization_and_token_management/demos/demo_08_prompt_compression_measuring_token_reduc.py)

### Chapter 5: Prompt Design Patterns and Frameworks

- Part 1: [The 4-Part Prompt: what the structure is, why it works, what each component contributes](chapters/ch05_prompt_design_patterns_and_frameworks/parts/part_01_the_4_part_prompt_what_the_structure_is_why.md)
- Part 2: [Zero-Shot vs Few-Shot: when examples help, how many to use, how to pick them](chapters/ch05_prompt_design_patterns_and_frameworks/parts/part_02_zero_shot_vs_few_shot_when_examples_help_how.md)
- Part 3: [Persona and Tone Control: system prompts that define model behaviour](chapters/ch05_prompt_design_patterns_and_frameworks/parts/part_03_persona_and_tone_control_system_prompts_that.md)
- Part 4: [Output Format Control: prompting for JSON, bullet lists, code, and tables](chapters/ch05_prompt_design_patterns_and_frameworks/parts/part_04_output_format_control_prompting_for_json_bul.md)
- Part 5: [Code Generation Prompting: prompting for code generation and review](chapters/ch05_prompt_design_patterns_and_frameworks/parts/part_05_code_generation_prompting_prompting_for_code.md)
- [Quick Check](chapters/ch05_prompt_design_patterns_and_frameworks/quick_check.md)
- Demo 1: [The 4-Part Prompt: Before vs After](chapters/ch05_prompt_design_patterns_and_frameworks/demos/demo_01_the_4_part_prompt_before_vs_after.py)
- Demo 2: [Zero-Shot vs Few-Shot Classification](chapters/ch05_prompt_design_patterns_and_frameworks/demos/demo_02_zero_shot_vs_few_shot_classification.py)
- Demo 3: [Persona and Tone via System Prompt](chapters/ch05_prompt_design_patterns_and_frameworks/demos/demo_03_persona_and_tone_via_system_prompt.py)
- Demo 4: [Output Format Control: JSON, Table, Bullet List](chapters/ch05_prompt_design_patterns_and_frameworks/demos/demo_04_output_format_control_json_table_bullet.py)
- Demo 5: [Full 4-Part Prompt: All Components Together](chapters/ch05_prompt_design_patterns_and_frameworks/demos/demo_05_full_4_part_prompt_all_components_togeth.py)
- Demo 6: [Code Generation Prompt](chapters/ch05_prompt_design_patterns_and_frameworks/demos/demo_06_code_generation_prompt.py)

### Chapter 6: Few-Shot, Zero-Shot and Prompt Optimisation (Advanced)

- Part 1: [Zero-Shot Chain-of-Thought: Why It Works](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/parts/part_01_zero_shot_chain_of_thought_why_it_works.md)
- Part 2: [Designing Few-Shot Examples](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/parts/part_02_designing_few_shot_examples.md)
- Part 3: [Dynamic Few-Shot Retrieval](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/parts/part_03_dynamic_few_shot_retrieval.md)
- Part 4: [DSPy: Compiling Prompts Instead of Writing Them](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/parts/part_04_dspy_compiling_prompts_instead_of_writing_th.md)
- Part 5: [Decision Framework: Prompt vs Automate](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/parts/part_05_decision_framework_prompt_vs_automate.md)
- [Quick Check](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/quick_check.md)
- Demo 0: [Setup](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/demos/demo_00_setup.py)
- Demo 1: [Zero-Shot vs Zero-Shot CoT](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/demos/demo_01_zero_shot_vs_zero_shot_cot.py)
- Demo 2: [Few-Shot Ordering Effects](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/demos/demo_02_few_shot_ordering_effects.py)
- Demo 3: [Dynamic Few-Shot Retrieval with Embeddings](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/demos/demo_03_dynamic_few_shot_retrieval_with_embeddin.py)
- Demo 4: [Few-Shot Quality: Diverse vs Repetitive Examples](chapters/ch06_few_shot_zero_shot_and_prompt_optimisati/demos/demo_04_few_shot_quality_diverse_vs_repetitive_e.py)

### Chapter 7: Chain-of-Thought and Reasoning Techniques

- Part 1: [The Problem That CoT Solves](chapters/ch07_chain_of_thought_and_reasoning_technique/parts/part_01_the_problem_that_cot_solves.md)
- Part 2: [Standard Chain-of-Thought](chapters/ch07_chain_of_thought_and_reasoning_technique/parts/part_02_standard_chain_of_thought.md)
- Part 3: [Self-Consistency](chapters/ch07_chain_of_thought_and_reasoning_technique/parts/part_03_self_consistency.md)
- Part 4: [Tree-of-Thought](chapters/ch07_chain_of_thought_and_reasoning_technique/parts/part_04_tree_of_thought.md)
- Part 5: [Reflection and self-critique](chapters/ch07_chain_of_thought_and_reasoning_technique/parts/part_05_reflection_and_self_critique.md)
- Part 6: [Choosing the right technique for a given problem](chapters/ch07_chain_of_thought_and_reasoning_technique/parts/part_06_choosing_the_right_technique_for_a_given_pro.md)
- Part 7: [Connection back to reasoning models (Class 3: o1/o3/Claude Extended Thinking)](chapters/ch07_chain_of_thought_and_reasoning_technique/parts/part_07_connection_back_to_reasoning_models_class_3.md)
- [Quick Check](chapters/ch07_chain_of_thought_and_reasoning_technique/quick_check.md)
- Demo 0: [Setup](chapters/ch07_chain_of_thought_and_reasoning_technique/demos/demo_00_setup.py)
- Demo 1: [Direct Answer vs Chain-of-Thought](chapters/ch07_chain_of_thought_and_reasoning_technique/demos/demo_01_direct_answer_vs_chain_of_thought.py)
- Demo 2: [Self-Consistency with Majority Vote](chapters/ch07_chain_of_thought_and_reasoning_technique/demos/demo_02_self_consistency_with_majority_vote.py)
- Demo 4: [Reflection and Self-Critique](chapters/ch07_chain_of_thought_and_reasoning_technique/demos/demo_04_reflection_and_self_critique.py)

### Chapter 8: Advanced Prompting: ReAct, Safety and Responsible AI

- Part 1: [ReAct: Reason + Act - where it came from, the Thought-Action-Observation loop, when it beats plain CoT](chapters/ch08_advanced_prompting_react_safety_and_resp/parts/part_01_react_reason_act_where_it_came_from_the_thou.md)
- Part 2: [Plan-and-Execute - upfront planning vs reactive reasoning, why it handles multi-step tasks better](chapters/ch08_advanced_prompting_react_safety_and_resp/parts/part_02_plan_and_execute_upfront_planning_vs_reactiv.md)
- Part 3: [Safety Prompting](chapters/ch08_advanced_prompting_react_safety_and_resp/parts/part_03_safety_prompting.md)
- Part 4: [Responsible AI Basics](chapters/ch08_advanced_prompting_react_safety_and_resp/parts/part_04_responsible_ai_basics.md)
- Part 5: [Prompt Chaining](chapters/ch08_advanced_prompting_react_safety_and_resp/parts/part_05_prompt_chaining.md)
- [Quick Check](chapters/ch08_advanced_prompting_react_safety_and_resp/quick_check.md)
- Demo 2: [Prompt Chaining Pipeline (Conceptual Walkthrough)](chapters/ch08_advanced_prompting_react_safety_and_resp/demos/demo_02_prompt_chaining_pipeline_conceptual_walk.py)
- Demo 2: [Prompt Chaining: 3-Step Pipeline (Conceptual Walkthrough)](chapters/ch08_advanced_prompting_react_safety_and_resp/demos/demo_02_prompt_chaining_3_step_pipeline_conceptu.py)
- Demo 3: [Safety: Jailbreak Pattern Detection (Pseudocode Walkthrough)](chapters/ch08_advanced_prompting_react_safety_and_resp/demos/demo_03_safety_jailbreak_pattern_detection_pseud.py)
- Demo 3: [Safety: Jailbreak Pattern Detection (Pseudocode Walkthrough)](chapters/ch08_advanced_prompting_react_safety_and_resp/demos/demo_03_safety_jailbreak_pattern_detection_pseud.py)
- Demo 4: [Plan-and-Execute (Pseudocode Walkthrough)](chapters/ch08_advanced_prompting_react_safety_and_resp/demos/demo_04_plan_and_execute_pseudocode_walkthrough.py)
- Demo 4: [Plan-and-Execute (Pseudocode Walkthrough)](chapters/ch08_advanced_prompting_react_safety_and_resp/demos/demo_04_plan_and_execute_pseudocode_walkthrough.py)
- Demo 1: [ReAct Loop Simulation (Pseudocode Walkthrough)](chapters/ch08_advanced_prompting_react_safety_and_resp/demos/demo_01_react_loop_simulation_pseudocode_walkthr.py)

### Chapter 9: System Prompt Architecture

- Part 1: [What System Prompts Are and Why They Exist](chapters/ch09_system_prompt_architecture/parts/part_01_what_system_prompts_are_and_why_they_exist.md)
- Part 2: [System Prompt Anatomy](chapters/ch09_system_prompt_architecture/parts/part_02_system_prompt_anatomy.md)
- Part 3: [Multi-Turn Prompt Design](chapters/ch09_system_prompt_architecture/parts/part_03_multi_turn_prompt_design.md)
- Part 4: [Prompt Injection Attacks and Defences](chapters/ch09_system_prompt_architecture/parts/part_04_prompt_injection_attacks_and_defences.md)
- [Quick Check](chapters/ch09_system_prompt_architecture/quick_check.md)
- Demo 1: [System vs No-System: Identity Without a Prompt](chapters/ch09_system_prompt_architecture/demos/demo_01_system_vs_no_system_identity_without_a_p.py)
- Demo 2: [Prompt Injection: Attack Patterns in Practice](chapters/ch09_system_prompt_architecture/demos/demo_02_prompt_injection_attack_patterns_in_prac.py)
- Demo 3: [System Prompt Anatomy: Building Each Component](chapters/ch09_system_prompt_architecture/demos/demo_03_system_prompt_anatomy_building_each_comp.py)
- Demo 4: [Multi-Turn: How Conversation History Accumulates](chapters/ch09_system_prompt_architecture/demos/demo_04_multi_turn_how_conversation_history_accu.py)
- Demo 5: [Product Spec Generator (Full Build)](chapters/ch09_system_prompt_architecture/demos/demo_05_product_spec_generator_full_build.py)
- Demo 6: [Prompt Chaining: 2-Step Chain](chapters/ch09_system_prompt_architecture/demos/demo_06_prompt_chaining_2_step_chain.py)

### Chapter 10: Tool-Using LLMs: Function Calling and Structured Outputs

- Part 1: [Why Tools Exist: three fundamental LLM problems](chapters/ch10_tool_using_llms_function_calling_and_str/parts/part_01_why_tools_exist_three_fundamental_llm_proble.md)
- Part 2: [How Function Calling Works Mechanically](chapters/ch10_tool_using_llms_function_calling_and_str/parts/part_02_how_function_calling_works_mechanically.md)
- Part 3: [The Tool Arbiter Pattern](chapters/ch10_tool_using_llms_function_calling_and_str/parts/part_03_the_tool_arbiter_pattern.md)
- Part 4: [Tool Schemas and Validation](chapters/ch10_tool_using_llms_function_calling_and_str/parts/part_04_tool_schemas_and_validation.md)
- Part 5: [Structured Outputs and JSON Mode](chapters/ch10_tool_using_llms_function_calling_and_str/parts/part_05_structured_outputs_and_json_mode.md)
- Demo 1: [Define and Call a Tool (Weather Lookup)](chapters/ch10_tool_using_llms_function_calling_and_str/demos/demo_01_define_and_call_a_tool_weather_lookup.py)
- Demo 2: [The Tool Arbiter Pattern](chapters/ch10_tool_using_llms_function_calling_and_str/demos/demo_02_the_tool_arbiter_pattern.py)
- Demo 3: [Structured Output with Pydantic](chapters/ch10_tool_using_llms_function_calling_and_str/demos/demo_03_structured_output_with_pydantic.py)
- Demo 4: [Multi-Tool Loop (Calculator + Search)](chapters/ch10_tool_using_llms_function_calling_and_str/demos/demo_04_multi_tool_loop_calculator_search.py)
- Demo 5: [instructor Library: Structured Extraction from Free Text](chapters/ch10_tool_using_llms_function_calling_and_str/demos/demo_05_instructor_library_structured_extraction.py)

### Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem

- Part 1: [Vision Prompting: How multimodal models process images, image tokens, what models can and cannot reliably see](chapters/ch11_multimodal_prompting_llm_apis_and_provid/parts/part_01_vision_prompting_how_multimodal_models_proce.md)
- Part 2: [Document Understanding: Analysing screenshots, diagrams, PDFs with vision](chapters/ch11_multimodal_prompting_llm_apis_and_provid/parts/part_02_document_understanding_analysing_screenshots.md)
- Part 3: [Code Generation and Review Prompting: Structuring prompts that produce clean, reviewable code](chapters/ch11_multimodal_prompting_llm_apis_and_provid/parts/part_03_code_generation_and_review_prompting_structu.md)
- Part 4: [LLM API Deep Dive: OpenAI vs Anthropic vs Gemini - design differences, streaming, rate limits, context windows, pricing, function calling](chapters/ch11_multimodal_prompting_llm_apis_and_provid/parts/part_04_llm_api_deep_dive_openai_vs_anthropic_vs_gem.md)
- Part 5: [Prompt Versioning and A/B Testing: Managing prompts like code, measuring which version works better](chapters/ch11_multimodal_prompting_llm_apis_and_provid/parts/part_05_prompt_versioning_and_a_b_testing_managing_p.md)
- Demo 0: [Setup](chapters/ch11_multimodal_prompting_llm_apis_and_provid/demos/demo_00_setup.py)
- Demo 1: [Vision API: Analyse an image with GPT-4o](chapters/ch11_multimodal_prompting_llm_apis_and_provid/demos/demo_01_vision_api_analyse_an_image_with_gpt_4o.py)
- Demo 2: [Streaming API call: OpenAI with visible chunk delivery](chapters/ch11_multimodal_prompting_llm_apis_and_provid/demos/demo_02_streaming_api_call_openai_with_visible_c.py)
- Demo 3: [Streaming with Anthropic API](chapters/ch11_multimodal_prompting_llm_apis_and_provid/demos/demo_03_streaming_with_anthropic_api.py)
- Demo 4: [API comparison: same prompt, three providers, side by side](chapters/ch11_multimodal_prompting_llm_apis_and_provid/demos/demo_04_api_comparison_same_prompt_three_provide.py)
- Demo 5: [Prompt versioning and simple A/B test](chapters/ch11_multimodal_prompting_llm_apis_and_provid/demos/demo_05_prompt_versioning_and_simple_a_b_test.py)

## Running the demos

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API keys, then export them
python chapters/ch03_what_is_an_llm_transformers_and_how_they_work/demos/demo_01_attention_cost_scaling_o_n_2_visualised.py
```

Demos that call provider APIs need the matching key and will bill your account. Demos marked "pseudocode" in the source are illustrative and may not run as-is.
