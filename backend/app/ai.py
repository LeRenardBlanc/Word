import os
import torch
from transformers import pipeline

# Use a small, efficient model suitable for CPU/standard GPU.
# "LaMini-Flan-T5-77M" is very small and good for instructions.
# "t5-small" is also a safe bet.
MODEL_NAME = "google/flan-t5-small"

# Global variable to hold the pipeline
summarizer = None

def load_model():
    global summarizer
    if summarizer is None:
        try:
            print(f"Loading AI Model: {MODEL_NAME}...")
            # Check for GPU
            device = 0 if torch.cuda.is_available() else -1
            summarizer = pipeline("text2text-generation", model=MODEL_NAME, device=device)
            print(f"Model loaded successfully on {'GPU' if device == 0 else 'CPU'}.")
        except Exception as e:
            print(f"Error loading model: {e}")
            summarizer = None

def summarize_text(text: str) -> str:
    load_model()
    if not summarizer:
        return "AI Model not available. Please check backend logs."

    try:
        # Prompt engineering for summarization
        prompt = f"Summarize the following text: {text}"

        # Truncate if too long (model specific limit, usually 512 tokens)
        if len(prompt) > 2000:
             prompt = prompt[:2000]

        result = summarizer(prompt, max_length=150, min_length=30, do_sample=False)
        return result[0]['generated_text']
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Error processing request."

def generate_flashcards(text: str) -> list[str]:
    load_model()
    if not summarizer:
        return ["AI Model not available."]

    try:
        # Complex prompt for flashcards
        # Since t5-small is small, we might need to iterate or be simple.
        # We will ask it to generate questions based on the text.

        cards = []
        # Split text into chunks if large, but here we keep it simple
        sentences = text.split('. ')

        # Strategy: Pick 3 random or important segments and ask to generate a question
        # For a small model, we can try: "Generate a question for: <sentence>"
        import random
        selected_sentences = [s for s in sentences if len(s) > 20]
        if len(selected_sentences) > 3:
            selected_sentences = random.sample(selected_sentences, 3)

        for sent in selected_sentences:
            prompt = f"Generate a question based on this answer: {sent}"
            result = summarizer(prompt, max_length=64, do_sample=False)
            question = result[0]['generated_text']
            cards.append(f"Q: {question}\nA: {sent}")

        if not cards:
             cards.append("Could not extract enough context for flashcards.")

        return cards

    except Exception as e:
        print(f"Error during flashcard generation: {e}")
        return ["Error processing request."]
