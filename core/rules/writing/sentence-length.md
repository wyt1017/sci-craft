# Sentence Length Rule

## Rule
Every sentence must not exceed {{max_sentence_words}} words (configured per journal).

## Enforcement
1. Count words in each sentence individually
2. The last sentence of a paragraph is most likely to fail — check it first
3. Split long sentences by:
   - Identifying the primary claim and subordinate clauses
   - Breaking at natural boundaries (conjunctions, relative pronouns)
   - Ensuring each new sentence has its own subject and verb

## Examples

### Too long (32 words)
> "Our results demonstrate that the proposed method significantly outperforms existing approaches across all evaluated metrics, which suggests that the integration of multi-scale features provides a substantial advantage in this task."

### Fixed (2 sentences, 15 + 14 words)
> "Our results demonstrate that the proposed method significantly outperforms existing approaches across all evaluated metrics. This suggests that integrating multi-scale features provides a substantial advantage in this task."
