import re
from utils import cos
from LLMService import LLMChat, embed
from chromaDBService import ChromaDBService


def rag_answer(chroma: ChromaDBService, query: str) -> str:
    retrieved = chroma.retrieve(query)
    merged_text = "\n".join([r["text"] for r in retrieved])
    context = "\n\n".join(
        [f"Source: {r['source']}\n{r['text']}" for r in retrieved]
    )

    prompt = f"""
    You are a helpful assistant. Use the context to answer the question.
    Context:
    {context}
    Question:
    {query}
    """

    llm_output = LLMChat(prompt, 'mistral')
    llm_embed = embed([llm_output])[0]

    sentences = re.split(r'(?<=[.!?])\s+', merged_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_embeds = embed(sentences)

    similarities = [cos(e, llm_embed) for e in sentence_embeds]

    if not similarities:
        print("No sentences found to calculate similarity.")
        return llm_output

    max_similarity = max(similarities)
    dynamic_threshold = max_similarity * 0.90

    print(f"\nMax Similarity: {max_similarity:.4f}")
    print(
        f"Threshold: {dynamic_threshold:.4f}")

    best_index = max(range(len(sentences)), key=lambda i: similarities[i])

    window = 3
    start = max(0, best_index - window)
    end = min(len(sentences), best_index + window + 1)
    new_chunk_sentences = sentences[start:end]

    highlighted_sentences = []
    for i, s in enumerate(new_chunk_sentences):
        global_index = start + i
        sim = similarities[global_index]

        if sim >= dynamic_threshold:
            highlighted_sentences.append(s.upper())
        else:
            highlighted_sentences.append(s.lower())

    highlighted_chunk = " ".join(highlighted_sentences)

    print("\nUtilized Data:\n")
    print(highlighted_chunk)

    return llm_output


def main():
    chroma = ChromaDBService()
    chroma.set_source_enabled("potter", True)

    answer = rag_answer("how many players play in quidditch?")
    print("\nRAG Answer:\n", answer)


if __name__ == "__main__":
    main()
