from openai import OpenAI
import re


def adjust_formality(sentence):
    # Remove the polite ending '요' if present
    if sentence.endswith("요"):
        return sentence[:-1]
    return sentence

def remove_punctuation(sentence):
    # Remove punctuation marks (!, ., ?)
    return re.sub(r'[!.?]', '', sentence)

client = OpenAI(
) # warning: insert key

with open("english_sentences.txt", "r", encoding="utf-8") as f: # open original text
    parsedSentences = [line.strip() for line in f.readlines()] # parse sentences and assign in parsedSentences

finalSentences = [] # empty list for translated-adjusted sentences

for parsed in parsedSentences:
    completion = client.chat.completions.create( # call gpt-4
        model="gpt-4o", # AI model
        messages=[
            {"role": "system", "content": "You are a English to Korean translator."}, # Order model how to work
            {"role": "user", "content": parsed} # send parsed sentence
        ]
    )
    translatedSentence = completion.choices[0].message.content # rename it (copy value -> easy to understand)
    print("before: ", translatedSentence)
    finalSentence = adjust_formality(remove_punctuation(translatedSentence))
    finalSentences.append(finalSentence) # adjust and append to final list
    print("after: ", finalSentence)

with open("gpt_normalized_translated_sentences.txt", "w", encoding="utf-8") as f:
    for finalSentence in finalSentences:
        f.write(finalSentence.lower() + "\n") # record it

print("done!")
