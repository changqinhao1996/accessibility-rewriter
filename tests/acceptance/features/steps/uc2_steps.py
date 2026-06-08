"""
Step definitions for UC2 — MeasureReadingLevel acceptance tests.

Uses Playwright for UI assertions and requests for backend API tests.
"""

import time

import requests
from behave import given, then, when

BASE_URL = "http://localhost:5173"
API_BASE = "http://localhost:8000/api"

BACKGROUND_TEXT = (
    "Photosynthesis is the biochemical process by which chloroplasts in plant cells "
    "convert light energy into adenosine triphosphate, facilitating the synthesis of "
    "glucose from carbon dioxide and water. The chlorophyll pigments within the "
    "thylakoid membranes absorb photon energy, initiating a cascade of electron "
    "transfer reactions that ultimately reduce NADP+ to NADPH."
)


# ── Background ────────────────────────────────────────────────────────


@given("the ContentDesigner has loaded the analyze page with the following text")
@given("the ContentDesigner has loaded the analyze page with the following text:")
def step_load_analyze_page(context):
    """Navigate to the app and switch to the Analyze tab."""
    page = context.page
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    # Click the Analyze tab
    page.click("text=📊 Analyze")
    page.wait_for_selector("#analyze-editor", timeout=5000)

    # The textarea should already have the background text pre-loaded.
    # If the scenario provides a docstring, set it.
    if context.text:
        page.fill("#analyze-editor", context.text.strip())


# ── Analyze Action ────────────────────────────────────────────────────


@when("the ContentDesigner clicks the Analyze button")
@given("the ContentDesigner clicks the Analyze button")
def step_click_analyze(context):
    page = context.page
    btn = page.locator("#analyze-btn")
    if btn.is_enabled():
        context._analyze_start = time.time()
        btn.click()
        # Wait for either badge or warning to appear
        page.wait_for_selector(
            "#readability-badge, #readability-warning", timeout=5000
        )
        context._analyze_end = time.time()


# ── Text Modification ─────────────────────────────────────────────────


@given('the ContentDesigner replaces the text with "{text}"')
@when('the ContentDesigner changes the text to "{text}"')
def step_replace_text(context, text):
    context.page.fill("#analyze-editor", text)


@given("the ContentDesigner clears all text from the editor")
def step_clear_editor(context):
    context.page.fill("#analyze-editor", "")


@given("the editor contains a 2000-word passage")
def step_load_long_text(context):
    # Generate a simple 2000-word passage
    sentence = "The quick brown fox jumps over the lazy dog. "
    long_text = sentence * 222  # ~2000 words
    context.page.fill("#analyze-editor", long_text.strip())


@when("the ContentDesigner clicks Clear")
@given("the ContentDesigner clicks Clear")
def step_click_clear(context):
    context.page.click("text=Clear")


@given("the ContentDesigner restores the original text")
@when("the ContentDesigner restores the original text")
def step_restore_text(context):
    context.page.fill("#analyze-editor", BACKGROUND_TEXT)


# ── Details Toggle ────────────────────────────────────────────────────


@when('the ContentDesigner clicks "Show Details"')
@given("the ContentDesigner opens the detailed breakdown")
def step_show_details(context):
    context.page.click("#details-toggle")
    context.page.wait_for_selector("#breakdown-panel", timeout=3000)


@when('the ContentDesigner clicks "Hide Details"')
def step_hide_details(context):
    context.page.click("#details-toggle")


# ── Badge Assertions ──────────────────────────────────────────────────


@then("the system displays a readability badge")
@then("the readability badge is visible")
@given("the readability badge is visible")
def step_badge_visible(context):
    assert context.page.locator("#readability-badge").is_visible()


@then("the badge shows a numeric Flesch–Kincaid grade")
def step_badge_has_grade(context):
    text = context.page.locator("#readability-grade").inner_text()
    assert "Grade" in text
    # Extract the number
    num = text.replace("Grade", "").strip()
    assert float(num), f"Expected a number, got: {num}"


@then("the badge shows a reading-level name from the standard taxonomy")
def step_badge_has_level(context):
    text = context.page.locator("#readability-level-name").inner_text()
    valid_levels = [
        "Very Simple (Grades 1–3)",
        "Simple (Grades 4–5)",
        "Plain (Grades 6–8)",
        "Standard (Grades 9–12)",
        "Technical (Grade 13+)",
    ]
    assert text in valid_levels, f"Level '{text}' not in taxonomy"


@then("the readability badge updates to show a different grade")
def step_badge_different_grade(context):
    new_text = context.page.locator("#readability-grade").inner_text()
    assert hasattr(context, "_noted_grade"), "No previous grade noted"
    assert new_text != context._noted_grade, (
        f"Grade should have changed but both are: {new_text}"
    )


@then("the readability badge remains visible")
def step_badge_still_visible(context):
    assert context.page.locator("#readability-badge").is_visible()


@then("no readability badge is displayed")
def step_no_badge(context):
    assert not context.page.locator("#readability-badge").is_visible()


# ── Level Name Assertions ─────────────────────────────────────────────


@then("the displayed reading-level name is one of")
@then("the displayed reading-level name is one of:")
def step_level_is_one_of(context):
    text = context.page.locator("#readability-level-name").inner_text()
    valid = [row[0] for row in context.table.rows]
    assert text in valid, f"Level '{text}' not in expected list"


# ── Breakdown Assertions ──────────────────────────────────────────────


@then("a detailed breakdown panel opens")
def step_breakdown_open(context):
    assert context.page.locator("#breakdown-panel").is_visible()


@then("the panel displays the reading-level name")
def step_breakdown_has_level(context):
    text = context.page.locator("#breakdown-panel").inner_text()
    valid_levels = [
        "Very Simple", "Simple", "Plain", "Standard", "Technical"
    ]
    assert any(level in text for level in valid_levels)


@then("the panel displays the numeric grade")
def step_breakdown_has_grade(context):
    text = context.page.locator("#breakdown-panel").inner_text()
    assert "Grade" in text


@then("the detailed breakdown panel closes")
def step_breakdown_closed(context):
    assert not context.page.locator("#breakdown-panel").is_visible()


# ── Highlight Assertions ──────────────────────────────────────────────


@then("at least one word with 3 or more syllables is visually highlighted")
def step_has_highlighted_words(context):
    count = context.page.locator(".highlight-word").count()
    assert count > 0, "No complex words highlighted"


@then('"{word}" is among the highlighted words')
def step_word_is_highlighted(context, word):
    elements = context.page.locator(".highlight-word").all()
    texts = [el.inner_text().lower() for el in elements]
    assert word.lower() in texts, f"'{word}' not found among highlighted words: {texts}"


@then("at least one sentence is highlighted as a long sentence")
def step_has_highlighted_sentences(context):
    count = context.page.locator(".highlight-sentence").count()
    assert count > 0, "No long sentences highlighted"


@then("every highlighted word in the word list has 3 or more syllables noted")
def step_word_chips_have_syllables(context):
    chips = context.page.locator(".word-chip").all()
    assert len(chips) > 0, "No word chips found"
    for chip in chips:
        text = chip.inner_text()
        assert "syl" in text, f"Word chip missing syllable info: {text}"


# ── Empty / Warning Assertions ────────────────────────────────────────


@then('the system shows a prompt: "{prompt}"')
def step_shows_prompt(context, prompt):
    el = context.page.locator("#readability-empty")
    assert el.is_visible(), "Empty prompt not visible"
    assert prompt in el.inner_text()


@then('the system shows a warning: "{warning}"')
def step_shows_warning(context, warning):
    el = context.page.locator("#readability-warning")
    assert el.is_visible(), "Warning not visible"
    assert warning in el.inner_text()


@then("the Analyze button is disabled")
def step_analyze_disabled(context):
    assert context.page.locator("#analyze-btn").is_disabled()


# ── Grade Noting ──────────────────────────────────────────────────────


@given("the readability badge shows a grade")
@when("notes the displayed grade")
def step_note_grade(context):
    text = context.page.locator("#readability-grade").inner_text()
    context._noted_grade = text


@then("the displayed grade equals the previously noted grade")
def step_grade_equals_noted(context):
    current = context.page.locator("#readability-grade").inner_text()
    assert current == context._noted_grade, (
        f"Grades differ: {current} vs {context._noted_grade}"
    )


@then("the displayed Flesch–Kincaid grade is a valid number")
def step_grade_is_number(context):
    text = context.page.locator("#readability-grade").inner_text()
    num = text.replace("Grade", "").strip()
    float(num)  # Will raise if not a number


# ── Performance Assertions ────────────────────────────────────────────


@then("the readability badge appears within 200 milliseconds")
def step_badge_within_200ms(context):
    elapsed = (context._analyze_end - context._analyze_start) * 1000
    assert elapsed < 200, f"Badge took {elapsed:.1f}ms (> 200ms)"


# ── Persistence Assertions ────────────────────────────────────────────


@given("the database row counts are noted")
def step_note_db_counts(context):
    """Snapshot DB row counts via the API."""
    resp = requests.get(f"{API_BASE}/documents")
    context._doc_count = len(resp.json())
    # Count versions for all documents
    total_versions = 0
    for doc in resp.json():
        v_resp = requests.get(f"{API_BASE}/documents/{doc['id']}/versions")
        if v_resp.ok:
            total_versions += len(v_resp.json())
    context._version_count = total_versions


@then("the database row counts have not changed")
def step_db_counts_unchanged(context):
    resp = requests.get(f"{API_BASE}/documents")
    new_doc_count = len(resp.json())
    assert new_doc_count == context._doc_count, (
        f"Document count changed: {context._doc_count} → {new_doc_count}"
    )
    total_versions = 0
    for doc in resp.json():
        v_resp = requests.get(f"{API_BASE}/documents/{doc['id']}/versions")
        if v_resp.ok:
            total_versions += len(v_resp.json())
    assert total_versions == context._version_count, (
        f"Version count changed: {context._version_count} → {total_versions}"
    )


# ── Backend API Assertions ────────────────────────────────────────────


@when("the backend receives a POST to /api/analyze with the background text")
def step_api_analyze_background(context):
    context._api_response = requests.post(
        f"{API_BASE}/analyze",
        json={"text": BACKGROUND_TEXT},
    )


@when('the backend receives a POST to /api/analyze with text "{text}"')
def step_api_analyze_text(context, text):
    context._api_response = requests.post(
        f"{API_BASE}/analyze",
        json={"text": text},
    )


@then("the response status is {status:d}")
def step_response_status(context, status):
    assert context._api_response.status_code == status, (
        f"Expected {status}, got {context._api_response.status_code}: "
        f"{context._api_response.text}"
    )


@then("the response contains a valid grade and level_name")
def step_response_has_grade(context):
    data = context._api_response.json()
    assert "grade" in data
    assert "level_name" in data
    assert isinstance(data["grade"], (int, float))
    valid_levels = [
        "Very Simple (Grades 1–3)",
        "Simple (Grades 4–5)",
        "Plain (Grades 6–8)",
        "Standard (Grades 9–12)",
        "Technical (Grade 13+)",
    ]
    assert data["level_name"] in valid_levels


@then('the response detail is "{detail}"')
def step_response_detail(context, detail):
    data = context._api_response.json()
    assert data["detail"] == detail, f"Expected '{detail}', got '{data.get('detail')}'"
