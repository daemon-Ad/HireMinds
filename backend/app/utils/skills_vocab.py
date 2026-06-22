from pathlib import Path
import re
from typing import List

# Load skills vocabulary once at module level using pathlib
VOCAB_PATH = Path(__file__).parent.parent / "data" / "skills_vocabulary.txt"

_original_vocab = []
if VOCAB_PATH.exists():
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                _original_vocab.append(t)

_vocab_map = {t.lower(): t for t in _original_vocab}
SKILLS_VOCABULARY = set(_vocab_map.keys())

# Pre-compile the word-boundary regex for each term to ensure fast matching and module-level compilation
_VOCAB_REGEXES = {
    term: re.compile(r'\b' + re.escape(term) + r'\b')
    for term in SKILLS_VOCABULARY
}

def match_skills(text: str) -> List[str]:
    skills_text_lower = text.lower()
    matched = []
    # For each vocab term, check if term appears as a word/phrase
    for term in SKILLS_VOCABULARY:
        pattern = _VOCAB_REGEXES[term]
        if pattern.search(skills_text_lower):
            matched.append(_vocab_map[term])
    return [matched.lower() for match in matched]
