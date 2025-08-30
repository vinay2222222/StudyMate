from huggingface_hub import InferenceClient
from config.settings import HF_API_KEY, MODEL_ID

# Initialize Hugging Face client
client = InferenceClient(model=MODEL_ID
, token=HF_API_KEY)

def generate_answer(context_chunks, question):
    """
    Generate an answer using the Hugging Face chat API,
    strictly based on the provided context chunks.
    
    Args:
        context_chunks (list): List of text chunks from the document.
        question (str): User's question.
    
    Returns:
        str: Generated answer based on context, formatted with bullet points.
    
    Raises:
        Exception: If the API call fails.
    """
    system_prompt = (
        "You are a helpful AI tutor. Answer strictly based on the given context. "
        "Format your response using bullet points or numbered lists for clarity, especially for definitions, concepts, steps, or multiple items. "
        "Ensure each bullet point starts with a clear, concise statement. "
        "Do not hallucinate or include information outside the context. "
        "Highlight key concepts, definitions, or formulas in bold (**text**) if present."
    )

    context_text = "\n\n".join(context_chunks)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"}
    ]

    try:
        response = client.chat_completion(messages, max_tokens=300)
        answer = response.choices[0].message["content"]

        # Fallback: If no bullet points or lists detected, convert to bullet points
        if not any(char in answer for char in ['-', '*', '1.', '1)']):
            lines = [line.strip() for line in answer.split('\n') if line.strip()]
            if lines:
                answer = '\n'.join(f"- {line}" for line in lines)
            else:
                answer = f"- {answer}"  # Single bullet if no lines

        return answer.strip()
    except Exception as e:
        raise Exception(f"Failed to generate answer with Hugging Face: {str(e)}")

if __name__ == "__main__":
    # Example usage for testing
    sample_chunks = [
        "The Pythagorean theorem states that a² + b² = c².",
        "This applies to right-angled triangles."
    ]
    question = "What is the Pythagorean theorem?"
    try:
        answer = generate_answer(sample_chunks, question)
        print("Answer:\n", answer)
    except Exception as e:
        print("Error:", e)
