"""
Deterministic test double for the StyleRewriter.
Used during acceptance and integration tests.
"""

from adapters.style_rewriter_port import StyleRewriterPort
from services.exceptions import ServiceUnavailableError, UnclearTextError

# Pre-crafted responses whose Flesch-Kincaid grade falls near each target.
# Grades: Very Simple ~0.1, Simple ~4.3, Plain ~6.8, Standard ~11.9, Technical ~15.9
_FAKE_RESPONSES: dict[str, str] = {
    "Very Simple (Grades 1–3)": (
        "Plants need sun to make food. "
        "The sun gives them energy. "
        "They use water too. "
        "They make sugar from it. "
        "This helps them grow big."
    ),
    "Simple (Grades 4–5)": (
        "Plants can make their own food from sunlight, water, and air. "
        "The green parts of a plant have tiny parts that catch sunlight. "
        "The plant takes in water from the ground through its roots. "
        "It also takes in a gas called carbon dioxide from the air through its leaves. "
        "The plant then uses the energy from sunlight to turn the water and gas into sugar for food."
    ),
    "Plain (Grades 6–8)": (
        "Plants make food using sunlight in a process called photosynthesis. "
        "Inside each plant cell, small parts called chloroplasts capture light. "
        "The chloroplasts use this light energy to change water and carbon dioxide into sugar. "
        "This sugar gives the plant the energy it needs to live and grow."
    ),
    "Standard (Grades 9–12)": (
        "Photosynthesis is a process in which plants convert light energy into chemical energy stored as glucose. "
        "Chloroplasts within the plant cells contain chlorophyll, a green pigment that absorbs sunlight. "
        "During this process, water molecules are split and carbon dioxide is reduced, "
        "resulting in the production of oxygen as a byproduct. "
        "The glucose produced serves as the primary energy source for plant cellular respiration."
    ),
    "Technical (Grade 13+)": (
        "Photosynthesis occurs in the chloroplast organelles of plant cells. "
        "Photosystem II complexes absorb photon energy and catalyze water oxidation. "
        "The released electrons traverse a membrane-bound transport chain. "
        "This establishes an electrochemical proton gradient across the thylakoid membrane. "
        "ATP synthase harnesses this gradient to phosphorylate adenosine diphosphate. "
        "The Calvin cycle then assimilates carbon dioxide via RuBisCO-mediated carboxylation."
    ),
}

_DEFAULT_RESPONSE = (
    "Plants use light to make their food through a natural process. "
    "Water and carbon dioxide are changed into sugar inside the plant. "
    "This gives the plant energy to grow and stay healthy."
)

UNCLEAR_SENTINEL = "UNCLEAR_SENTINEL"


class FakeStyleRewriter(StyleRewriterPort):
    """
    Test double that returns deterministic rewritten text.

    Behaviours:
    - Normal: returns a pre-crafted response for the requested level.
    - Unclear text: raises UnclearTextError if input contains UNCLEAR_SENTINEL.
    - Service outage: raises ServiceUnavailableError when simulate_outage is True.
    """

    def __init__(self) -> None:
        self.simulate_outage: bool = False

    async def rewrite(self, text: str, target_level: str) -> str:
        """Return a deterministic rewrite or raise a test error."""
        if self.simulate_outage:
            raise ServiceUnavailableError()

        if UNCLEAR_SENTINEL in text:
            raise UnclearTextError()

        return _FAKE_RESPONSES.get(target_level, _DEFAULT_RESPONSE)
