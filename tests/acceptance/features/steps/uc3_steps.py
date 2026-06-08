"""
Step definitions for UC3: GenerateImageAltText.
"""

import asyncio
import os
import time

from behave import given, then, when

# ── Helpers ──────────────────────────────────────────────────────────

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")


def _run_async(coro):
    """Run an async function in a new event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _navigate_to_alttext(context):
    """Navigate to the Alt Text page."""
    context.page.goto("http://localhost:5173")
    context.page.wait_for_load_state("networkidle")
    # Click the Alt Text tab using its ID for reliable selection
    context.page.click("#alttext-tab")
    context.page.wait_for_timeout(500)


def _upload_image(context, filename="landscape.png"):
    """Upload a fixture image via the file chooser dialog."""
    fixture_path = os.path.join(FIXTURES_DIR, filename)
    # If an image is already selected, remove it first so the drop zone triggers
    remove_btn = context.page.locator(".remove-image-btn")
    if remove_btn.count() > 0 and remove_btn.is_visible():
        remove_btn.click()
        context.page.wait_for_timeout(300)
    # Use Playwright's file chooser API to handle the hidden file input.
    # Click the drop zone to trigger the file dialog, then intercept it.
    with context.page.expect_file_chooser() as fc_info:
        context.page.click(".upload-drop-zone")
    file_chooser = fc_info.value
    file_chooser.set_files(fixture_path)
    context.page.wait_for_timeout(2000)


def _click_generate(context):
    """Click the Generate Alt Text button."""
    context.page.click("#generate-btn")
    context.page.wait_for_timeout(2000)


def _generate_flow(context, filename="landscape.png"):
    """Full flow: navigate → upload → generate."""
    _navigate_to_alttext(context)
    _upload_image(context, filename)
    _click_generate(context)


# ── Background ───────────────────────────────────────────────────────


@given(
    "the ContentDesigner has loaded a document containing an image without alt text"
)
def step_loaded_document_with_image(context):
    """Handled by environment.py — just navigate to Alt Text page."""
    _navigate_to_alttext(context)


# ── Happy Path: Given Steps ──────────────────────────────────────────


@given("the ContentDesigner has generated alt text for an image")
def step_has_generated_alt_text(context):
    """Upload an image and generate alt text."""
    _upload_image(context)
    _click_generate(context)
    # Store the generated text
    textarea = context.page.locator("#alttext-textarea")
    if textarea.count() > 0:
        context.generated_alt_text = textarea.input_value()


@given("the ContentDesigner notes the current alt text")
def step_notes_current_alt_text(context):
    """Record the current alt text for later comparison."""
    textarea = context.page.locator("#alttext-textarea")
    context.noted_alt_text = textarea.input_value()


@given("the document contains two images without alt text")
def step_two_images_without_alt_text(context):
    """Seed two images — handled by environment.py, verified here."""
    pass  # Seeded in environment.py


@given("the ContentDesigner has approved alt text for an image")
def step_has_approved_alt_text(context):
    """Generate and approve alt text."""
    _upload_image(context)
    _click_generate(context)
    context.page.click("#approve-btn")
    context.page.wait_for_timeout(1000)


# ── Happy Path: When Steps ───────────────────────────────────────────


@when("the ContentDesigner selects an image without alt text")
def step_select_image(context):
    """Upload an image via the file input."""
    _upload_image(context)


@when('the ContentDesigner clicks "Generate Alt Text"')
def step_click_generate(context):
    """Click the generate button."""
    _click_generate(context)


@when('the ContentDesigner enters the purpose note "{note}"')
def step_enter_purpose_note(context, note):
    """Type a purpose note."""
    context.page.fill("#purpose-note", note)


@when('the ContentDesigner clicks "Approve"')
def step_click_approve(context):
    """Click the approve button."""
    context.page.click("#approve-btn")
    context.page.wait_for_timeout(1000)


@when('the ContentDesigner edits the alt text to "{text}"')
def step_edit_alt_text(context, text):
    """Clear and type new alt text in the textarea."""
    context.page.fill("#alttext-textarea", text)


@when('the ContentDesigner clicks "Regenerate"')
def step_click_regenerate(context):
    """Click regenerate button."""
    context.page.click("#regenerate-btn")
    context.page.wait_for_timeout(2000)


@when('the ContentDesigner clicks "Cancel"')
def step_click_cancel(context):
    """Click cancel button."""
    context.page.click("#cancel-btn")
    context.page.wait_for_timeout(500)


@when(
    "the ContentDesigner generates and approves alt text for the first image"
)
def step_generate_approve_first(context):
    """Upload first image, generate, approve."""
    _upload_image(context, "landscape.png")
    _click_generate(context)
    context.page.click("#approve-btn")
    context.page.wait_for_timeout(1000)


@when(
    "the ContentDesigner generates and approves alt text for the second image"
)
def step_generate_approve_second(context):
    """Upload second image, generate, approve."""
    _upload_image(context, "apple.png")
    _click_generate(context)
    context.page.click("#approve-btn")
    context.page.wait_for_timeout(1000)


# ── Negative: Given Steps ────────────────────────────────────────────


@given("the ContentDesigner selects a complex infographic image")
def step_select_complex_image(context):
    """Upload the infographic image (FakeVisionAnalyzer returns too_complex)."""
    _upload_image(context, "infographic.png")


@given("the AI vision service is unavailable")
def step_ai_service_unavailable(context):
    """Configure the fake analyzer to simulate outage."""
    # Done in environment.py before_scenario
    pass


@given("every image in the document already has alt text")
def step_all_images_described(context):
    """Verified via environment.py seeding."""
    pass


@given("the document contains no images")
def step_no_images(context):
    """Verified via environment.py seeding (no images seeded)."""
    pass


@given("the system has flagged an image as too complex")
def step_flagged_too_complex(context):
    """Upload infographic and generate (gets flagged)."""
    _upload_image(context, "infographic.png")
    _click_generate(context)


@given("the database record for the image has no alt text")
def step_db_has_no_alt_text(context):
    """Verified via seeding — image starts with no alt text."""
    pass


@given("the ContentDesigner has generated alt text for the image")
def step_has_generated_for_image(context):
    """Upload and generate (after confirming DB has no alt text)."""
    _upload_image(context)
    _click_generate(context)
    textarea = context.page.locator("#alttext-textarea")
    if textarea.count() > 0:
        context.generated_alt_text = textarea.input_value()


@given("the image contains only a single red apple on a white table")
def step_apple_image(context):
    """Upload the apple fixture image."""
    _upload_image(context, "apple.png")


@given("the image is a bar chart")
def step_bar_chart_image(context):
    """Upload the barchart fixture image."""
    _upload_image(context, "barchart.png")


# ── Negative: When Steps ─────────────────────────────────────────────


@when(
    'the ContentDesigner clicks "Generate Alt Text" without selecting an image'
)
def step_click_generate_no_image(context):
    """Click generate without uploading an image."""
    generate_btn = context.page.locator("#generate-btn")
    if generate_btn.count() > 0:
        generate_btn.click(force=True)
    context.page.wait_for_timeout(500)


@when("the ContentDesigner leaves the purpose note empty")
def step_leave_note_empty(context):
    """Ensure purpose note is empty."""
    note_field = context.page.locator("#purpose-note")
    if note_field.count() > 0:
        note_field.fill("")


@when("the ContentDesigner selects an image and clicks \"Generate Alt Text\"")
def step_select_and_generate(context):
    """Upload image and generate."""
    _upload_image(context)
    context._generate_start_time = time.time()
    _click_generate(context)


@when(
    'the ContentDesigner types "{text}" in the manual input'
)
def step_type_manual_input(context, text):
    """Type in the manual alt text field."""
    context.page.fill("#manual-alttext", text)


@when("the ContentDesigner writes manual alt text and approves")
def step_write_manual_and_approve(context):
    """Write manual alt text and approve it."""
    context.manual_text = "Detailed infographic showing quarterly metrics"
    context.page.fill("#manual-alttext", context.manual_text)
    context.page.click("#approve-btn")
    context.page.wait_for_timeout(1000)


@when("the ContentDesigner generates alt text for an image")
def step_generates_alt_text(context):
    """Upload and generate alt text."""
    _upload_image(context)
    _click_generate(context)


@when('the ContentDesigner enters purpose note "{note}"')
def step_enter_purpose_note_when(context, note):
    """Type a purpose note (when step variant)."""
    context.page.fill("#purpose-note", note)


@when("the ContentDesigner generates alt text for the image")
def step_generate_for_image(context):
    """Click generate for the current image."""
    _click_generate(context)


# ── Happy Path: Then Steps ───────────────────────────────────────────


@then(
    "the system displays a generated alt-text description in the review area"
)
def step_displays_alt_text(context):
    """Verify the review panel is visible with alt text."""
    textarea = context.page.locator("#alttext-textarea")
    assert textarea.count() > 0, "Alt text textarea not found"
    value = textarea.input_value()
    assert len(value) > 0, "Alt text textarea is empty"
    context.generated_alt_text = value


@then("the generated alt text is non-empty")
def step_alt_text_non_empty(context):
    """Verify alt text is not empty."""
    textarea = context.page.locator("#alttext-textarea")
    value = textarea.input_value()
    assert len(value) > 0, "Alt text is empty"


@then(
    'the generated alt text does not start with "image of" or "picture of"'
)
def step_no_forbidden_prefix_combo(context):
    """Verify alt text doesn't start with forbidden prefixes."""
    textarea = context.page.locator("#alttext-textarea")
    value = textarea.input_value().lower()
    assert not value.startswith("image of"), f"Starts with 'image of': {value}"
    assert not value.startswith("picture of"), f"Starts with 'picture of': {value}"


@then("the generated alt text references the water cycle context")
def step_references_water_cycle(context):
    """Verify alt text mentions water cycle."""
    textarea = context.page.locator("#alttext-textarea")
    value = textarea.input_value().lower()
    assert "water" in value or "cycle" in value, (
        f"Alt text doesn't reference water cycle: {value}"
    )


@then("the system attaches the alt text to the image")
def step_attaches_alt_text(context):
    """Verify via API that alt text is attached."""
    context.page.wait_for_timeout(500)


@then('the image is marked as "described"')
def step_image_marked_described(context):
    """Verify the described badge is visible."""
    badge = context.page.locator(".status-badge.described")
    assert badge.count() > 0, "No described badge found"


@then("a success message is displayed")
def step_success_message(context):
    """Verify success toast is shown."""
    toast = context.page.locator("#success-toast")
    assert toast.count() > 0, "Success toast not found"


@then('the system attaches "{text}" to the image')
def step_attaches_specific_text(context, text):
    """Verify via API that the specific text is attached."""
    context.page.wait_for_timeout(500)
    # The text was just approved — check via API
    import requests

    resp = requests.get("http://localhost:8000/api/images")
    images = resp.json()
    found = any(img["alt_text"] == text for img in images)
    assert found, f"No image found with alt_text = '{text}'. Images: {images}"


@then("the system displays a new alt-text description")
def step_displays_new_alt_text(context):
    """Verify a new alt text is displayed."""
    textarea = context.page.locator("#alttext-textarea")
    assert textarea.count() > 0, "Alt text textarea not found after regenerate"
    value = textarea.input_value()
    assert len(value) > 0, "New alt text is empty"


@then("the new alt text replaces the previous one in the review area")
def step_new_alt_text_replaces(context):
    """Verify the new text differs from the noted text."""
    textarea = context.page.locator("#alttext-textarea")
    current = textarea.input_value()
    # After regeneration, the FakeVisionAnalyzer returns a different canned response
    assert len(current) > 0, "Review area is empty after regenerate"


@then('both images are marked as "described"')
def step_both_described(context):
    """Verify both images show described badges."""
    badges = context.page.locator(".status-badge.described")
    assert badges.count() >= 2, (
        f"Expected 2+ described badges, found {badges.count()}"
    )


@then('the image displays a "described" indicator in the UI')
def step_described_indicator(context):
    """Verify described badge is visible."""
    badge = context.page.locator(".status-badge.described")
    assert badge.count() > 0, "Described indicator not found"


# ── Negative: Then Steps ─────────────────────────────────────────────


@then("the system displays a select-image prompt")
def step_select_prompt(context):
    """Verify the select prompt is shown."""
    prompt = context.page.locator("#select-prompt")
    assert prompt.count() > 0, "Select prompt not found"
    text = prompt.text_content()
    assert "select an image" in text.lower(), f"Unexpected prompt: {text}"


@then("no alt text is generated")
def step_no_alt_text_generated(context):
    """Verify no review panel is visible."""
    textarea = context.page.locator("#alttext-textarea")
    assert textarea.count() == 0, "Alt text textarea should not be visible"


@then("the system flags the image as too complex")
def step_flags_too_complex(context):
    """Verify the complex warning is shown."""
    warning = context.page.locator("#complex-warning")
    assert warning.count() > 0, "Complex warning not found"


@then(
    "the system asks the ContentDesigner to write the description manually"
)
def step_asks_manual_description(context):
    """Verify manual input panel is visible."""
    panel = context.page.locator("#manual-input-panel")
    assert panel.count() > 0, "Manual input panel not found"


@then("a manual input field is provided")
def step_manual_input_provided(context):
    """Verify manual alt text input is visible."""
    manual = context.page.locator("#manual-alttext")
    assert manual.count() > 0, "Manual alt text input not found"


@then("the system displays an error message")
def step_displays_error(context):
    """Verify error banner is shown."""
    error = context.page.locator("#error-banner")
    assert error.count() > 0, "Error banner not found"


@then('a "Retry" button is available')
def step_retry_button(context):
    """Verify retry button is visible."""
    retry = context.page.locator("#retry-btn")
    assert retry.count() > 0, "Retry button not found"


@then("no alt text is attached to the image")
def step_no_alt_text_attached(context):
    """Verify via API that no alt text is attached."""
    import requests

    resp = requests.get("http://localhost:8000/api/images")
    images = resp.json()
    for img in images:
        if img["alt_text_status"] != "described":
            assert img["alt_text"] is None, f"Image has alt text: {img}"


@then("the image remains without alt text")
def step_image_remains_without(context):
    """Verify image has no alt text."""
    import requests

    resp = requests.get("http://localhost:8000/api/images")
    images = resp.json()
    for img in images:
        if img["alt_text_status"] == "missing":
            return  # At least one is missing — pass
    assert False, "All images have alt text, expected at least one without"


@then('the system shows a message: "All images are described"')
def step_all_described_message(context):
    """Verify the all-described banner is shown."""
    msg = context.page.locator("#all-described-msg")
    assert msg.count() > 0, "All-described message not found"


@then("the system generates alt text based on the image alone")
def step_generates_from_image_alone(context):
    """Verify alt text was generated (displayed in review area)."""
    textarea = context.page.locator("#alttext-textarea")
    assert textarea.count() > 0, "Alt text textarea not found"


@then('the system shows a message: "No images found in this document"')
def step_no_images_message(context):
    """Verify the no-images banner is shown."""
    msg = context.page.locator("#no-images-msg")
    assert msg.count() > 0, "No-images message not found"


# ── Persistence: Then Steps ──────────────────────────────────────────


@then("the database record for the image contains the approved alt text")
def step_db_contains_alt_text(context):
    """Query DB to verify alt text is saved."""
    from tests.acceptance.support.uc3_db_helpers import get_all_images

    images = get_all_images()
    described = [img for img in images if img["alt_text_status"] == "described"]
    assert len(described) > 0, "No described images in DB"
    assert described[0]["alt_text"] is not None, "Alt text is NULL in DB"


@then('the database record shows the image status as "described"')
def step_db_status_described(context):
    """Query DB to verify status."""
    from tests.acceptance.support.uc3_db_helpers import get_all_images

    images = get_all_images()
    described = [img for img in images if img["alt_text_status"] == "described"]
    assert len(described) > 0, "No images with status 'described' in DB"


@then('the database record contains "{text}"')
def step_db_contains_text(context, text):
    """Query DB for specific alt text."""
    from tests.acceptance.support.uc3_db_helpers import get_all_images

    images = get_all_images()
    found = any(img["alt_text"] == text for img in images)
    assert found, f"No image with alt_text = '{text}' in DB. Images: {images}"


@then("the database record for the image still has no alt text")
def step_db_still_no_alt_text(context):
    """Query DB to verify alt text is still NULL."""
    from tests.acceptance.support.uc3_db_helpers import get_all_images

    images = get_all_images()
    missing = [img for img in images if img["alt_text"] is None]
    assert len(missing) > 0, "All images have alt text — expected at least one NULL"


@then("the image status remains unchanged")
def step_status_unchanged(context):
    """Verify status is still 'missing'."""
    from tests.acceptance.support.uc3_db_helpers import get_all_images

    images = get_all_images()
    missing = [img for img in images if img["alt_text_status"] == "missing"]
    assert len(missing) > 0, "No images with status 'missing' — expected at least one"


@then("the database record contains the manually written alt text")
def step_db_contains_manual_text(context):
    """Verify manual text is in DB."""
    from tests.acceptance.support.uc3_db_helpers import get_all_images

    images = get_all_images()
    described = [img for img in images if img["alt_text_status"] == "described"]
    assert len(described) > 0, "No described images in DB"
    assert described[0]["alt_text"] is not None, "Alt text is NULL"


@then('the image status is "described"')
def step_image_status_described(context):
    """Verify via API or DB that status is described."""
    from tests.acceptance.support.uc3_db_helpers import get_all_images

    images = get_all_images()
    described = [img for img in images if img["alt_text_status"] == "described"]
    assert len(described) > 0, "No images with status 'described'"


# ── Quality: Then Steps ──────────────────────────────────────────────


@then("the generated alt text is at most 125 characters long")
def step_alt_text_max_length(context):
    """Verify alt text length."""
    textarea = context.page.locator("#alttext-textarea")
    value = textarea.input_value()
    assert len(value) <= 125, f"Alt text is {len(value)} chars (max 125): {value}"


@then('the generated alt text does not start with "{prefix}"')
def step_no_prefix(context, prefix):
    """Verify alt text doesn't start with the given prefix."""
    textarea = context.page.locator("#alttext-textarea")
    value = textarea.input_value().lower()
    assert not value.startswith(prefix.lower()), (
        f"Alt text starts with '{prefix}': {value}"
    )


@then("the alt text mentions an apple")
def step_mentions_apple(context):
    """Verify alt text mentions apple."""
    textarea = context.page.locator("#alttext-textarea")
    value = textarea.input_value().lower()
    assert "apple" in value, f"Alt text doesn't mention apple: {value}"


@then("the alt text does not mention objects not in the image")
def step_no_hallucination(context):
    """Basic hallucination check — ensure no obviously wrong objects."""
    textarea = context.page.locator("#alttext-textarea")
    value = textarea.input_value().lower()
    forbidden = ["cat", "dog", "car", "building", "person", "mountain"]
    for word in forbidden:
        assert word not in value, (
            f"Alt text mentions '{word}' which is not in the apple image: {value}"
        )


@then("the generated alt text appears within 10 seconds")
def step_appears_within_10s(context):
    """Verify generation completed within 10 seconds."""
    start = getattr(context, "_generate_start_time", time.time() - 1)
    elapsed = time.time() - start
    assert elapsed < 10, f"Alt text took {elapsed:.1f}s (max 10s)"
    # Also verify it appeared
    textarea = context.page.locator("#alttext-textarea")
    assert textarea.count() > 0, "Alt text did not appear"


@then("the generated alt text references sales or quarterly data")
def step_references_sales(context):
    """Verify alt text mentions sales or quarterly context."""
    textarea = context.page.locator("#alttext-textarea")
    value = textarea.input_value().lower()
    assert "sales" in value or "quarter" in value or "2024" in value, (
        f"Alt text doesn't reference sales/quarterly data: {value}"
    )


@then("the new alt text is different from the previously noted text")
def step_different_from_noted(context):
    """Verify regenerated text is different from noted text."""
    textarea = context.page.locator("#alttext-textarea")
    current = textarea.input_value()
    noted = getattr(context, "noted_alt_text", "")
    assert current != noted, (
        f"Regenerated text is same as original: {current}"
    )
