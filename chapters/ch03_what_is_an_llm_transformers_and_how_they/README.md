# Chapter 3: What is an LLM? + Transformers and How They Work


## Parts
1. [What an LLM actually is (the idea, before the architecture)](parts/part_01_what_an_llm_actually_is_the_idea_before_the.md)
2. [NLP history: word2vec → RNN/LSTM → the sequential bottleneck that broke everything](parts/part_02_nlp_history_word2vec_rnn_lstm_the_sequential.md)
3. [Attention is All You Need: what Vaswani et al. 2017 actually figured out](parts/part_03_attention_is_all_you_need_what_vaswani_et_al.md)
4. [Transformer architecture: self-attention mechanics, encoder-only vs decoder-only](parts/part_04_transformer_architecture_self_attention_mech.md)
5. [KV Cache: prefill phase, decode phase, and why it matters for latency](parts/part_05_kv_cache_prefill_phase_decode_phase_and_why.md)
6. [Inference optimisations: Flash Attention, continuous batching](parts/part_06_inference_optimisations_flash_attention_cont.md)
7. [Mixture of Experts (MoE): how GPT-4, Mistral, and Gemini avoid paying full compute cost](parts/part_07_mixture_of_experts_moe_how_gpt_4_mistral_and.md)
8. [Reasoning models: o1/o3/Claude Extended Thinking - compute at inference time](parts/part_08_reasoning_models_o1_o3_claude_extended_think.md)

## Quick Check
- [Quick Check questions and answers](quick_check.md)

## Code Demos
- Demo 0: [Setup](demos/demo_00_setup.py)
- Demo 1: [Attention Cost Scaling (O(n^2) visualised)](demos/demo_01_attention_cost_scaling_o_n_2_visualised.py)
- Demo 2: [Self-Attention from Scratch](demos/demo_02_self_attention_from_scratch.py)
- Demo 3: [KV Cache Speedup Simulation](demos/demo_03_kv_cache_speedup_simulation.py)
- Demo 4: [Token Generation Timing](demos/demo_04_token_generation_timing.py)
