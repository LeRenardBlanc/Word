import os
import re
from typing import List, Dict

# Try to import heavy ML libraries
try:
    import torch
    from transformers import pipeline
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: torch or transformers not found. AI features will be disabled.")

try:
    from spellchecker import SpellChecker
    spell = SpellChecker()
    SPELL_AVAILABLE = True
except ImportError:
    SPELL_AVAILABLE = False
    spell = None
    print("Warning: pyspellchecker not found. Spell features disabled.")

# Use a small, efficient model suitable for CPU/standard GPU.
MODEL_NAME = "google/flan-t5-small"

# Global variable to hold the pipeline
summarizer = None

def load_model():
    global summarizer
    if not ML_AVAILABLE:
        return

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
    if not ML_AVAILABLE:
        return "AI features are disabled."
        
    load_model()
    if not summarizer:
        return "AI Model not available."
    
    try:
        # Improved prompt
        prompt = f"Summarize the following text in a concise and clear way: {text}"
        
        if len(prompt) > 2000:
             prompt = prompt[:2000]

        result = summarizer(prompt, max_length=200, min_length=50, do_sample=False)
        return result[0]['generated_text']
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Error processing request."

def generate_flashcards(text: str) -> List[str]:
    if not ML_AVAILABLE:
        return ["AI features disabled."]

    load_model()
    if not summarizer:
        return ["AI Model not available."]
    
    try:
        cards = []
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        import random
        # Process up to 5 sentences to ensure coverage
        selected_sentences = sentences[:5] if len(sentences) < 10 else random.sample(sentences, 5)
            
        for sent in selected_sentences:
            prompt = f"Create a question for this answer: {sent}"
            result = summarizer(prompt, max_length=64, do_sample=False)
            question = result[0]['generated_text']
            cards.append(f"Q: {question}\nA: {sent}")
            
        if not cards:
             cards.append("Could not extract enough context for flashcards.")
             
        return cards

    except Exception as e:
        print(f"Error during flashcard generation: {e}")
        return ["Error processing request."]

def autocorrect_text(text: str) -> str:
    if not SPELL_AVAILABLE:
        return text
    
    # Simple correction of the whole text (word by word)
    words = text.split()
    corrected = []
    for word in words:
        # Strip punctuation for checking
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word and clean_word not in spell:
            corr = spell.correction(clean_word)
            if corr:
                # replace the word but keep punctuation if possible
                # This is a naive replacement
                word = word.replace(clean_word, corr)
        corrected.append(word)
    return " ".join(corrected)

def autocomplete_text(text: str) -> List[str]:
    """Returns a list of suggested completions for the last partial word."""
    if not SPELL_AVAILABLE:
        return []
    
    words = text.split()
    if not words:
        return []
    
    last_word = words[-1]
    # Get candidates
    candidates = spell.candidates(last_word)
    if candidates:
        return list(candidates)[:5]
    return []

def smart_completion(text: str) -> str:
    """Uses LLM to predict the next part of the sentence."""
    if not ML_AVAILABLE:
        return ""
    load_model()
    if not summarizer:
        return ""
    
    try:
        prompt = f"Complete this sentence: {text}"
        result = summarizer(prompt, max_length=30, do_sample=True) # Sample for variety
        return result[0]['generated_text']
    except Exception:
        return ""

def detect_abbreviations(text: str) -> Dict[str, str]:
    """
    Uses heuristics and AI to find abbreviations.
    Returns dict {abbrev: potential_meaning}
    """
    # 1. Regex for uppercase words (2-5 chars)
    potential_abbr = set(re.findall(r'\b[A-Z]{2,5}\b', text))
    results = {}
    
    if not ML_AVAILABLE:
        return {abbr: "Unknown (AI disabled)" for abbr in potential_abbr}

    load_model()
    if not summarizer:
        return {abbr: "Unknown" for abbr in potential_abbr}

    for abbr in potential_abbr:
        # Ask AI to define it in context
        prompt = f"What does the abbreviation '{abbr}' stand for in this text? Text: {text[:500]}"
        try:
            res = summarizer(prompt, max_length=20, do_sample=False)
            results[abbr] = res[0]['generated_text']
        except:
            results[abbr] = "Could not determine"
            
    return results