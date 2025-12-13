import re
from LLMService import embed


def cos(a, b):
    import math
    num = sum(x*y for x, y in zip(a, b))
    den = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b))
    return num / den if den != 0 else 0


def get_best_sentence(chunk: str, query: str) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', chunk)
    sentence_embeds = embed(sentences)
    query_embed = embed([query])[0]

    best_sentence = max(sentences, key=lambda s: cos(
        sentence_embeds[sentences.index(s)], query_embed))
    return best_sentence
