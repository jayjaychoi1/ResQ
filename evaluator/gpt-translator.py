from openai import OpenAI
import re

template = """
|Start of document|
Document = {document}
|End of document|

|Start of task instructions|
- You are not allowed to output text between |Start of task instructions| and |End of output format instructions|
- I will give you english sentence, and you translate it into korean.
|End of task instruction|
"""

def adjust_formality(sentence):
    # Remove the polite ending '요' if present
    if sentence.endswith("요"):
        return sentence[:-1]
    return sentence

def remove_punctuation(sentence):
    # Remove punctuation marks (!, ., ?)
    return re.sub(r'[!.?]', '', sentence)
# warning: insert key
client = OpenAI(
    api_key = ""
)

# open original text
with open("english_sentences.txt", "r", encoding="utf-8") as f:
    # parse sentences and assign in parsedSentences
    parsedSentences = [line.strip() for line in f.readlines()]
# empty list for translated-adjusted sentences
finalSentences = []

for parsed in parsedSentences:
    # call gpt-4
    completion = client.chat.completions.create(
        # AI model
        model="gpt-4o",
        messages=[
            {"role": "system", "content": template},
            {"role": "user", "content": parsed},
        ]
    )
    # rename it (copy value -> easy to understand)
    translatedSentence = completion.choices[0].message.content
    print("before: ", translatedSentence)
    finalSentence = adjust_formality(remove_punctuation(translatedSentence))
    # adjust and append to final list
    finalSentences.append(finalSentence)
    print("after: ", finalSentence)

with open("gpt_normalized_translated_sentences.txt", "w", encoding="utf-8") as f:
    for finalSentence in finalSentences:
        # record it
        f.write(finalSentence.lower() + "\n")

print("done!")
