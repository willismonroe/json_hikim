import oracc_corpus
from collections import Counter

saa10_path = "saao/saa10"
c = oracc_corpus.guess_filenames(saa10_path)

print("Loading corpus")
c.load_corpus()

lim = 5
print(f"\n{lim} most common normalized words in the corpus:")
most_common_words = Counter(c.bow_norm()).most_common(lim)
for [word, freq] in most_common_words:
    print(f"{word}\t{freq}")

print("\nPrinting one text")
pnum = list(c.texts.keys())[100]
text = c.texts[pnum]
print(f"Transliteration of: {pnum}")
print(f"Title: {text.metadata.get('title')}")
c.texts[pnum].pprint_translit()

c.pprint_kwic('šarri')
