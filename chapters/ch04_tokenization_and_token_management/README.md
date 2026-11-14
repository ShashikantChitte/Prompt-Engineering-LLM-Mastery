# Chapter 4: Tokenization and Token Management


## Parts
1. [Why tokenization exists - models never see words, only integers](parts/part_01_why_tokenization_exists_models_never_see_wor.md)
2. [Byte-Pair Encoding (BPE) - how the algorithm builds a vocabulary from scratch](parts/part_02_byte_pair_encoding_bpe_how_the_algorithm_bui.md)
3. [WordPiece - BERT's approach and how it differs from BPE](parts/part_03_wordpiece_bert_s_approach_and_how_it_differs.md)
4. [Why the same word costs different tokens in different contexts](parts/part_04_why_the_same_word_costs_different_tokens_in.md)
5. [Context window limits - hard limits, soft limits, and the LostInTheMiddle failure](parts/part_05_context_window_limits_hard_limits_soft_limit.md)

## Quick Check
- [Quick Check questions and answers](quick_check.md)

## Code Demos
- Demo 1: [Setup](demos/demo_01_setup.py)
- Demo 2: [Basic Tokenization: Seeing the Integer Sequence](demos/demo_02_basic_tokenization_seeing_the_integer_se.py)
- Demo 3: [Same Information, Different Token Counts (Non-English Cost)](demos/demo_03_same_information_different_token_counts.py)
- Demo 4: [How Numbers Tokenize (Unpredictable Splits)](demos/demo_04_how_numbers_tokenize_unpredictable_split.py)
- Demo 5: [Context Window: Token Counting Before You Send](demos/demo_05_context_window_token_counting_before_you.py)
- Demo 6: [Cost Estimation with tiktoken](demos/demo_06_cost_estimation_with_tiktoken.py)
- Demo 7: [LostInTheMiddle: Position Matters](demos/demo_07_lostinthemiddle_position_matters.py)
- Demo 8: [Prompt Compression: Measuring Token Reduction](demos/demo_08_prompt_compression_measuring_token_reduc.py)
