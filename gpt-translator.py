from openai import OpenAI
import re
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
            {"role": "system", "content": "Translate the following English text to Korean. When translating from English to Korean, use polite language in a friendly and natural 'haeyo-che' (해요체) style. Ensure that the tone remains respectful but informal and approachable."}, # Order model how to work
            {"role": "user", "content": parsed} # send parsed sentence
        ]
    )
    translatedSentence = completion.choices[0].message.content # rename it (copy value -> easy to understand)
    finalSentences.append(translatedSentence) # adjust and append to final list

with open("gpt_normalized_translated_sentences.txt", "w", encoding="utf-8") as f:
    for finalSentence in finalSentences:
        f.write(finalSentence.lower() + "\n") # record it

print("done!")
