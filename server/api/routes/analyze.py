"""
API routes for the readability analysis endpoint (UC2: MeasureReadingLevel).

POST /api/analyze — Compute Flesch-Kincaid grade, map to reading level,
                     identify complex words and long sentences.
"""

import re

import textstat
from fastapi import APIRouter, HTTPException

from schemas.analyze import (
    AnalyzeRequest,
    AnalyzeResult,
    ComplexWordOut,
    LongSentenceOut,
)
from services.rewrite_service import READING_LEVELS

router = APIRouter(prefix="/api", tags=["analyze"])


def _map_grade_to_level(grade: float) -> str:
    """Map a Flesch-Kincaid grade to a reading-level name."""
    if grade <= 3:
        return "Very Simple (Grades 1–3)"
    if grade <= 5:
        return "Simple (Grades 4–5)"
    if grade <= 8:
        return "Plain (Grades 6–8)"
    if grade <= 12:
        return "Standard (Grades 9–12)"
    return "Technical (Grade 13+)"


def _count_syllables(word: str) -> int:
    """Heuristic syllable counter matching the client-side implementation."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if len(w) <= 2:
        return 1

    count = 0
    vowels = "aeiouy"
    prev_vowel = False

    for ch in w:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    # Subtract silent 'e'
    if w.endswith("e") and count > 1:
        count -= 1

    # Handle '-le' ending
    if w.endswith("le") and len(w) > 2 and w[-3] not in vowels:
        count += 1

    return max(count, 1)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _split_words(text: str) -> list[str]:
    """Split text into words."""
    return re.findall(r"[a-zA-Z]+(?:['-][a-zA-Z]+)*", text)


def _get_complex_words(text: str) -> list[ComplexWordOut]:
    """Find words with ≥3 syllables."""
    results = []
    for match in re.finditer(r"[a-zA-Z]+(?:['-][a-zA-Z]+)*", text):
        word = match.group()
        syllables = _count_syllables(word)
        if syllables >= 3:
            results.append(
                ComplexWordOut(
                    word=word,
                    syllables=syllables,
                    start_index=match.start(),
                    end_index=match.end(),
                )
            )
    return results


def _get_long_sentences(text: str) -> list[LongSentenceOut]:
    """Find sentences with word count above the passage average."""
    sentences = _split_sentences(text)
    if not sentences:
        return []

    word_counts = [len(_split_words(s)) for s in sentences]
    avg = sum(word_counts) / len(word_counts)

    results = []
    search_from = 0
    for sentence, wc in zip(sentences, word_counts):
        start = text.index(sentence, search_from)
        if wc > avg:
            results.append(
                LongSentenceOut(
                    sentence=sentence,
                    word_count=wc,
                    start_index=start,
                    end_index=start + len(sentence),
                )
            )
        search_from = start + len(sentence)

    return results


@router.post("/analyze", response_model=AnalyzeResult)
async def analyze_text(body: AnalyzeRequest) -> AnalyzeResult:
    """
    Analyze the readability of the given text.

    Returns 200 with grade, level name, complex words, and long sentences.
    Returns 422 if text is too short for meaningful analysis.
    """
    text = body.text.strip()

    if not text:
        raise HTTPException(status_code=422, detail="Text is empty")

    words = _split_words(text)
    if len(words) < 2:
        raise HTTPException(
            status_code=422,
            detail="Selection too short for meaningful analysis",
        )

    sentences = _split_sentences(text)
    grade = textstat.flesch_kincaid_grade(text)
    level_name = _map_grade_to_level(grade)
    complex_words = _get_complex_words(text)
    long_sentences = _get_long_sentences(text)

    total_words = len(words)
    total_sentences = len(sentences)
    avg_sentence_length = total_words / total_sentences if total_sentences else 0

    return AnalyzeResult(
        grade=round(grade, 2),
        level_name=level_name,
        complex_words=complex_words,
        long_sentences=long_sentences,
        average_sentence_length=round(avg_sentence_length, 1),
        total_words=total_words,
        total_sentences=total_sentences,
    )
