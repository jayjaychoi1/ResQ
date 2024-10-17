import re


def adjust_formality(sentence):
    # Remove the polite ending '요' if present
    if sentence.endswith("요"):
        return sentence[:-1]
    return sentence

def remove_punctuation(sentence):
    # Remove punctuation marks (!, ., ?)
    return re.sub(r'[!.?]', '', sentence)

# Read translated sentences from the file
with open("adjusted_korean_sentences.txt", "r", encoding="utf-8") as f:
    translated_sentences = [line.strip() for line in f]

# Adjust formality for each sentence and remove punctuation
adjusted_translated_sentences = [
    remove_punctuation(adjust_formality(sentence)) for sentence in translated_sentences
]

# Write adjusted translated sentences to a new file
with open("normalized_translated_sentences.txt", "w", encoding="utf-8") as f:
    for sentence in adjusted_translated_sentences:
        f.write(sentence.lower() + "\n")

# Now read original reference Korean sentences
with open("adjusted_reference_korean_sentences.txt", "r", encoding="utf-8") as f:
    reference_sentences = [line.strip() for line in f]

# Remove punctuation from each reference sentence and remove polite endings if present
adjusted_reference_sentences = [
    remove_punctuation(adjust_formality(sentence)).lower() for sentence in reference_sentences
]

# Write adjusted reference sentences to a new file
with open("normalized_reference_sentences.txt", "w", encoding="utf-8") as f:
    for sentence in adjusted_reference_sentences:
        f.write(sentence + "\n")

print("Normalization of formality and punctuation completed. Normalized sentences saved.")
