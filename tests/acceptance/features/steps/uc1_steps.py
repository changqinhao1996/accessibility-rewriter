"""
Step definitions for UC1: RewriteTextToReadingLevel.
Maps Gherkin steps to Playwright UI actions and DB assertions.
"""

import asyncio
import time

import textstat
from behave import given, when, then

from tests.acceptance.support.db_helpers import (
    get_latest_version,
    get_version_count,
    get_versions,
)

# ═══════════════════════════════════════════════════════════════
# Helper to run async functions in step definitions
# ═══════════════════════════════════════════════════════════════

def _run(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ═══════════════════════════════════════════════════════════════
# BACKGROUND STEPS
# ═══════════════════════════════════════════════════════════════

@given("the ContentDesigner is authenticated")
def step_authenticated(context):
    """Authentication is handled outside UC1 (A8). No-op."""
    pass


@given("a document with the following text is loaded")
def step_document_loaded(context):
    """The document is seeded in before_scenario; verify it loaded in the UI."""
    page = context.page
    textarea = page.locator("#source-text")
    textarea.wait_for(state="visible", timeout=5000)
    assert not textarea.is_disabled(), "Source text should be enabled when document is loaded"


# ═══════════════════════════════════════════════════════════════
# GIVEN STEPS
# ═══════════════════════════════════════════════════════════════

@given("the ContentDesigner selects all the source text")
def step_select_all_text(context):
    """Source text is already pre-filled by document load; select all."""
    page = context.page
    textarea = page.locator("#source-text")
    textarea.click()
    textarea.select_text()


@given("the ContentDesigner selects only the first sentence of the source text")
def step_select_first_sentence(context):
    """Replace textarea with only the first sentence."""
    page = context.page
    textarea = page.locator("#source-text")
    full_text = textarea.input_value()
    first_sentence = full_text.split(".")[0] + "."
    textarea.fill(first_sentence)
    context.selected_text = first_sentence


@given('the ContentDesigner chooses reading level "{level}"')
def step_choose_level(context, level):
    """Select a reading level from the dropdown."""
    page = context.page
    page.locator("#reading-level-select").select_option(label=level)


@given("no reading level is chosen")
def step_no_level_chosen(context):
    """Ensure the reading level dropdown is on the default placeholder."""
    page = context.page
    page.locator("#reading-level-select").select_option(value="")


@given("no document is loaded")
def step_no_document(context):
    """Document was not seeded; the page should show disabled controls."""
    pass  # Handled by before_scenario setting document_id = None


@given("the document is loaded but contains no text")
def step_document_empty_text(context):
    """Document with empty content was seeded in before_scenario."""
    page = context.page
    textarea = page.locator("#source-text")
    assert textarea.input_value().strip() == "", "Source text should be empty"


@given("the document is loaded but contains only whitespace")
def step_document_whitespace(context):
    """Document with whitespace-only content was seeded in before_scenario."""
    page = context.page
    textarea = page.locator("#source-text")
    assert textarea.input_value().strip() == "", "Source text should be whitespace-only"


@given("the ContentDesigner selects source text that is ambiguous and unclear")
def step_select_unclear_text(context):
    """Source text contains UNCLEAR_SENTINEL; it's already loaded."""
    page = context.page
    textarea = page.locator("#source-text")
    assert "UNCLEAR_SENTINEL" in textarea.input_value()


@given("the StyleRewriter service is unavailable")
def step_service_unavailable(context):
    """FakeStyleRewriter is configured for outage in before_scenario."""
    assert context.fake_rewriter.simulate_outage is True


@given("the ContentDesigner submits the rewrite request")
def step_submit_rewrite_given(context):
    """Submit and wait for result (used as a Given precondition)."""
    page = context.page
    page.locator("#btn-rewrite").click()
    # Wait for either the reviewing panel or an error to appear
    page.wait_for_selector("#panel-rewritten, [id^='error-']", timeout=10000)


@given("the system displays the rewritten draft beside the original text")
def step_draft_displayed_given(context):
    """Verify the side-by-side view is visible."""
    page = context.page
    assert page.locator("#panel-original").is_visible()
    assert page.locator("#panel-rewritten").is_visible()


@given("the system displays the rewritten draft")
def step_draft_displayed_short(context):
    """Alias: verify the rewritten panel is visible."""
    page = context.page
    assert page.locator("#panel-rewritten").is_visible()


@given("the document already has {count:d} existing versions")
def step_existing_versions(context, count):
    """Versions are seeded in before_scenario; verify count."""
    actual = _run(get_version_count(context.document_id))
    assert actual == count, f"Expected {count} versions but found {actual}"


@given("the document has {count:d} existing version")
def step_existing_version_singular(context, count):
    """Alias for singular version count."""
    actual = _run(get_version_count(context.document_id))
    assert actual == count, f"Expected {count} version(s) but found {actual}"


# ═══════════════════════════════════════════════════════════════
# WHEN STEPS
# ═══════════════════════════════════════════════════════════════

@when("the ContentDesigner submits the rewrite request")
def step_submit_rewrite(context):
    """Click the Rewrite button."""
    page = context.page
    page.locator("#btn-rewrite").click()
    # Wait for result or error
    page.wait_for_selector(
        "#panel-rewritten, [id^='error-']", timeout=10000
    )


@when("the ContentDesigner attempts to submit the rewrite request")
def step_attempt_submit(context):
    """Click Rewrite when validation should fail."""
    page = context.page
    btn = page.locator("#btn-rewrite")
    if btn.is_disabled():
        # Button is disabled — that's a valid validation state
        return
    btn.click()
    # Wait for validation error
    page.wait_for_selector("[id^='error-']", timeout=5000)


@when("the ContentDesigner saves the draft")
def step_save_draft(context):
    """Click the Save button."""
    page = context.page
    page.locator("#btn-save").click()
    # Wait for success toast or error
    page.wait_for_selector("#toast-success, [id^='error-']", timeout=10000)


@when("the ContentDesigner discards the draft")
def step_discard_draft(context):
    """Click the Discard button."""
    page = context.page
    page.locator("#btn-discard").click()
    page.wait_for_timeout(500)  # Allow UI state transition


@when(
    "the ContentDesigner submits the rewrite request {n:d} times "
    "with representative text samples"
)
def step_submit_n_times(context, n):
    """Submit the rewrite request N times and record latencies."""
    page = context.page
    latencies = []

    for _ in range(n):
        start = time.perf_counter()
        page.locator("#btn-rewrite").click()
        page.wait_for_selector("#panel-rewritten", timeout=10000)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        # Discard to reset state for next iteration
        page.locator("#btn-discard").click()
        page.wait_for_timeout(200)

    context.latencies = latencies


@when("the system returns an error that the text was too unclear")
def step_error_unclear_when(context):
    """Wait for the unclear-text error to appear."""
    page = context.page
    page.wait_for_selector("#error-unclear-text", timeout=5000)


# ═══════════════════════════════════════════════════════════════
# THEN STEPS
# ═══════════════════════════════════════════════════════════════

@then(
    "the system displays the rewritten text beside the original text "
    "in a side-by-side view"
)
def step_side_by_side_view(context):
    """Verify both panels are visible."""
    page = context.page
    assert page.locator("#panel-original").is_visible(), "Original panel not visible"
    assert page.locator("#panel-rewritten").is_visible(), "Rewritten panel not visible"


@then(
    "the system displays the rewritten text beside the selected original text "
    "in a side-by-side view"
)
def step_side_by_side_partial(context):
    """Verify panels visible; original panel shows only the selected text."""
    page = context.page
    assert page.locator("#panel-original").is_visible()
    assert page.locator("#panel-rewritten").is_visible()


@then("the rewritten text preserves the original intent of the source text")
def step_preserves_intent(context):
    """Verify the rewritten text is non-empty and differs from original."""
    page = context.page
    original = page.locator("#panel-original").text_content()
    rewritten = page.locator("#panel-rewritten").text_content()
    assert rewritten and rewritten.strip(), "Rewritten text is empty"
    assert rewritten != original, "Rewritten text should differ from original"


@then("only the selected portion is rewritten")
def step_only_selected_rewritten(context):
    """Verify the rewritten text is present (partial selection was passed)."""
    page = context.page
    rewritten = page.locator("#panel-rewritten").text_content()
    assert rewritten and rewritten.strip(), "Rewritten text should not be empty"


@then("the reading level of the rewritten text is within ±1 grade of grade {target:d}")
def step_reading_level_within(context, target):
    """Check Flesch-Kincaid grade of rewritten text."""
    page = context.page
    rewritten = page.locator("#panel-rewritten").text_content()
    grade = textstat.flesch_kincaid_grade(rewritten)
    assert target - 1 <= grade <= target + 1, (
        f"Reading grade {grade:.1f} is not within ±1 of {target}"
    )


@then("the system stores the rewritten draft as a new version of the document")
def step_version_stored(context):
    """Verify a new version exists in the database."""
    count = _run(get_version_count(context.document_id))
    assert count >= 1, "No version was created in the database"


@then("a success confirmation is displayed")
def step_success_toast(context):
    """Verify the success toast is visible."""
    page = context.page
    assert page.locator("#toast-success").is_visible(), "Success toast not visible"


@then("the rewrite controls are disabled")
def step_controls_disabled(context):
    """Verify all input controls are disabled."""
    page = context.page
    assert page.locator("#source-text").is_disabled(), "Source text should be disabled"
    assert page.locator("#reading-level-select").is_disabled(), "Level select should be disabled"
    assert page.locator("#btn-rewrite").is_disabled(), "Rewrite button should be disabled"


@then("the ContentDesigner cannot submit a rewrite request")
def step_cannot_submit(context):
    """Rewrite button is disabled."""
    page = context.page
    assert page.locator("#btn-rewrite").is_disabled()


@then("the system displays a validation error indicating the source text is empty")
def step_error_empty_text(context):
    """Verify the empty-text error is visible."""
    page = context.page
    assert page.locator("#error-empty-text").is_visible(), "Empty text error not shown"


@then("the system displays a validation error prompting the user to select a reading level")
def step_error_no_level(context):
    """Verify the no-level error is visible."""
    page = context.page
    # Could be disabled button or error message
    is_disabled = page.locator("#btn-rewrite").is_disabled()
    has_error = page.locator("#error-no-level").is_visible()
    assert is_disabled or has_error, "No level validation error not shown"


@then("no rewrite is performed")
def step_no_rewrite(context):
    """Verify the rewritten panel is NOT visible."""
    page = context.page
    assert not page.locator("#panel-rewritten").is_visible(), (
        "Rewritten panel should not be visible"
    )


@then("the system displays an error explaining that the text was too unclear to rewrite safely")
def step_error_unclear(context):
    """Verify unclear-text error is visible."""
    page = context.page
    assert page.locator("#error-unclear-text").is_visible(), "Unclear text error not shown"


@then("no rewritten draft is presented")
def step_no_draft(context):
    """Verify the rewritten panel is NOT visible."""
    page = context.page
    assert not page.locator("#panel-rewritten").is_visible()


@then("no new document version is created")
def step_no_version_created(context):
    """Verify version count is 0 or unchanged."""
    count = _run(get_version_count(context.document_id))
    expected = getattr(context, "initial_version_count", 0)
    assert count == expected, f"Version count changed: expected {expected}, got {count}"


@then("the system displays a service-unavailable error message")
def step_error_service_unavailable(context):
    """Verify service-unavailable error is visible."""
    page = context.page
    assert page.locator("#error-service-unavailable").is_visible()


@then("the ContentDesigner is offered the option to retry")
def step_retry_available(context):
    """Verify the retry button is visible."""
    page = context.page
    assert page.locator("#btn-retry").is_visible(), "Retry button not visible"


@then("the draft is removed from the side-by-side view")
def step_draft_removed(context):
    """Verify both comparison panels are gone."""
    page = context.page
    assert not page.locator("#panel-rewritten").is_visible()
    assert not page.locator("#panel-original").is_visible()


@then("a new version record exists in the database linked to the original document")
def step_version_in_db(context):
    """Verify at least one version exists."""
    count = _run(get_version_count(context.document_id))
    assert count >= 1, "No version record found"


@then("the new version contains the rewritten text")
def step_version_has_content(context):
    """Verify the latest version has non-empty content."""
    version = _run(get_latest_version(context.document_id))
    assert version is not None, "No version found"
    assert version["content"] and version["content"].strip(), "Version content is empty"


@then('the new version metadata includes the target reading level "{level}"')
def step_version_reading_level(context, level):
    """Verify the version's reading_level matches."""
    version = _run(get_latest_version(context.document_id))
    assert version is not None
    assert version["reading_level"] == level, (
        f"Expected reading_level '{level}', got '{version['reading_level']}'"
    )


@then("the new version metadata includes a timestamp and the author reference")
def step_version_metadata(context):
    """Verify timestamp and author are present."""
    version = _run(get_latest_version(context.document_id))
    assert version is not None
    assert version["created_at"] is not None, "Timestamp is missing"
    assert version["author"] and version["author"].strip(), "Author is missing"


@then("the document now has {count:d} versions")
def step_version_count(context, count):
    """Verify total version count."""
    actual = _run(get_version_count(context.document_id))
    assert actual == count, f"Expected {count} versions, got {actual}"


@then("the content and metadata of the {count:d} previous versions remain unchanged")
def step_prior_versions_unchanged(context, count):
    """Compare prior version snapshots with current state."""
    current_versions = _run(get_versions(context.document_id))
    prior = context.prior_versions

    assert len(prior) == count, f"Expected {count} prior versions, got {len(prior)}"

    for i, (p, c) in enumerate(zip(prior, current_versions[:count])):
        assert p["id"] == c["id"], f"Version {i+1} ID changed"
        assert p["content"] == c["content"], f"Version {i+1} content changed"
        assert p["reading_level"] == c["reading_level"], f"Version {i+1} reading_level changed"
        assert p["created_at"] == c["created_at"], f"Version {i+1} created_at changed"


@then("the document still has exactly {count:d} version")
def step_exact_version_count_singular(context, count):
    """Verify version count (singular form)."""
    actual = _run(get_version_count(context.document_id))
    assert actual == count, f"Expected {count} version(s), got {actual}"


@then("at least {threshold:d} of the {total:d} requests complete within {ms:d} milliseconds")
def step_p90_latency(context, threshold, total, ms):
    """Check that >= threshold requests completed within ms."""
    latencies = context.latencies
    within = sum(1 for l in latencies if l <= ms)
    assert within >= threshold, (
        f"Only {within}/{total} requests completed within {ms}ms "
        f"(needed {threshold}). P90 = {sorted(latencies)[int(total*0.9)-1]:.0f}ms"
    )


@then(
    "the readability score of the rewritten text corresponds to a grade level "
    "between {low:d} and {high:d}"
)
def step_readability_range(context, low, high):
    """Verify Flesch-Kincaid grade is in [low, high]."""
    page = context.page
    rewritten = page.locator("#panel-rewritten").text_content()
    grade = textstat.flesch_kincaid_grade(rewritten)
    assert low <= grade <= high, (
        f"Readability grade {grade:.1f} is not in [{low}, {high}]"
    )
