import os
from dotenv import load_dotenv
from groq import Groq
from typing import List, Dict, Generator

# Load environment variables from .env file (only once, safe to call multiple times)
load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("Please make sure you have API_KEY in your .env file.")

client = Groq(api_key=API_KEY)


def stream_llama_chat(messages: List[Dict],
                      model: str = "llama-3.1-8b-instant",
                      temperature: float = 0.7,
                      max_tokens: int = 1024,
                      top_p: float = 1.0,
                      stop=None) -> Generator[str, None, None]:
    """
    Streams chat completion from Groq's Llama model.
    Args:
        messages: List of dicts with 'role' and 'content'.
        model: Model name (default: llama-3.1-8b-instant).
        temperature: Sampling temperature.
        max_tokens: Max tokens in response.
        top_p: Nucleus sampling parameter.
        stop: Optional stop sequence.
    Yields:
        str: The next chunk of the model's response.
    """
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=True,
            stop=stop,
        )
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"Error: {e}" 