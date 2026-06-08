"""
Pydantic schemas for the readability analysis endpoint (UC2).
"""

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    """Input for the readability analysis endpoint."""
    text: str


class ComplexWordOut(BaseModel):
    """A word with ≥3 syllables."""
    word: str
    syllables: int
    start_index: int
    end_index: int


class LongSentenceOut(BaseModel):
    """A sentence longer than the passage average."""
    sentence: str
    word_count: int
    start_index: int
    end_index: int


class AnalyzeResult(BaseModel):
    """Full readability analysis result."""
    grade: float
    level_name: str
    complex_words: list[ComplexWordOut]
    long_sentences: list[LongSentenceOut]
    average_sentence_length: float
    total_words: int
    total_sentences: int
