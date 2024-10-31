with open("english_sentences.txt", "r", encoding="utf-8") as f: # open original text
    parsedProb = [line.strip() for line in f.readlines()] # parse sentences and assign in parsedSentences

with open("korean_sentences.txt", "r", encoding="utf-8") as g: # open original text
    parsedAns = [line.strip() for line in g.readlines()] # parse sentences and assign in parsedSentences

with open("gpt_normalized_translated_sentences.txt", "r", encoding="utf-8") as h: # open original text
    parsedGpt = [line.strip() for line in h.readlines()] # parse sentences and assign in parsedSentences

with open("adjusted_translated_korean_sentences.txt", "r", encoding="utf-8") as i: # open original text
    parsedJunia = [line.strip() for line in i.readlines()] # parse sentences and assign in parsedSentences

with open("compareText.txt", "w", encoding="utf-8") as k:
    for (parsedProb1, parsedAns1, parsedGpt1, parsedJunia1) in zip(parsedProb, parsedAns, parsedGpt, parsedJunia):
        lf = "=========================="
        p = "P: " + parsedProb1
        a = "A: " + parsedAns1
        g = "G: " + parsedGpt1
        j = "J: " + parsedJunia1
        k.write(lf.lower() + "\n") # record it
        k.write(p.lower() + "\n") # record it
        k.write(a.lower() + "\n") # record it
        k.write(g.lower() + "\n") # record it
        k.write(j.lower() + "\n") # record it