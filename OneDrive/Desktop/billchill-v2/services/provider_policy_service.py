from pathlib import Path
from services.pdf_service import extract_text_from_pdf


POLICY_DIR = Path("provider_policies")

PROVIDER_POLICY_FILES = {
    "United": "united.pdf",
    "Providence": "providence.pdf",
    "Molina": "molina.pdf",
    "CMS": "cms.pdf",
}


def load_provider_policy_text(provider_name: str) -> str:
    """
    Loads the selected provider's policy PDF from provider_policies/
    and extracts its text using the same pdfplumber-based PDF service.

    This makes the OpenAI summary provider-aware by adding policy context.
    """

    filename = PROVIDER_POLICY_FILES.get(provider_name)

    if not filename:
        return ""

    policy_path = POLICY_DIR / filename

    if not policy_path.exists():
        return ""

    try:
        return extract_text_from_pdf(str(policy_path))
    except Exception as error:
        print(f"Failed to load provider policy for {provider_name}: {error}")
        return ""