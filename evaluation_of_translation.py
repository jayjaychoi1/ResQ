import nltk
import pyter
import sacrebleu

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('wordnet')

from nltk.translate.meteor_score import meteor_score

# Load reference Korean sentences
with open("normalized_reference_sentences.txt", "r", encoding="utf-8") as f:
    reference_sentences = [line.strip() for line in f.readlines()]

# Load model-generated Korean translations
with open("normalized_translated_sentences.txt", "r", encoding="utf-8") as f:
    hypothesis_sentences = [line.strip() for line in f.readlines()]

# Ensure lengths match
assert len(reference_sentences) == len(hypothesis_sentences), "Mismatch between reference and hypothesis sentence counts."

# BLEU score
bleu = sacrebleu.corpus_bleu(hypothesis_sentences, [reference_sentences])
print(f"BLEU Score: {bleu.score}")

# Simple tokenization approach to ensure no punkt_tab issues
def simple_tokenize(text):
    return text.split()

# METEOR Score (average)
meteor_scores = [meteor_score([simple_tokenize(ref)], simple_tokenize(hyp)) for ref, hyp in zip(reference_sentences, hypothesis_sentences)]
avg_meteor_score = sum(meteor_scores) / len(meteor_scores)
print(f"Average METEOR Score: {avg_meteor_score}")

# TER Score (average)
ter_scores = [pyter.ter(simple_tokenize(hyp), simple_tokenize(ref)) for hyp, ref in zip(hypothesis_sentences, reference_sentences)]
avg_ter_score = sum(ter_scores) / len(ter_scores)
print(f"Average TER Score: {avg_ter_score}")
