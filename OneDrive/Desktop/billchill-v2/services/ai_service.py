import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_audit_with_ai(
    bill_text: str,
    findings: list,
    household_size: int,
    annual_income: float,
    zip_code: str,
    provider_policy_text: str = ""
):
    findings_text = "\n".join([
        f"- {f['finding_type']}: {f['reason']} Estimated savings: ${f['estimated_savings']:.2f}"
        for f in findings
    ])

    provider_policy_context = (
        provider_policy_text[:6000]
        if provider_policy_text
        else "No provider-specific policy text was available."
    )

    if not os.getenv("OPENAI_API_KEY"):
        return f"""
AI summary unavailable because OPENAI_API_KEY is not configured.

Provider Policy Context:
{provider_policy_context}

Rule-based findings:
{findings_text if findings_text else "No rule-based findings."}
"""

    prompt = f"""
You are a medical billing audit assistant.

Important constraints:
- Do not claim final legal, insurance, or medical certainty.
- Explain findings in plain English.
- Recommend that the patient verify with the provider or insurer.
- Be concise and practical.
- Use the provider policy context only as supporting context, not as absolute proof.
- If the provider policy context appears relevant, mention how it may support the findings.
- If the provider policy context is not clearly relevant, say the finding should be verified with the provider.

Patient Info:
Household Size: {household_size}
Annual Income: {annual_income}
ZIP Code: {zip_code}

Provider Policy Context:
{provider_policy_context}

Extracted Bill Text:
{bill_text[:6000]}

Rule-Based Findings:
{findings_text if findings_text else "No rule-based findings."}

Return:
1. Plain-English audit summary
2. Main possible savings opportunities
3. Provider-policy context that may support the findings
4. Recommended next steps
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content

    except Exception as error:
        return f"""
AI summary failed: {str(error)}

Provider Policy Context:
{provider_policy_context}

Rule-based findings:
{findings_text if findings_text else "No rule-based findings."}
"""


def draft_dispute_letter(
    patient_name: str,
    provider_name: str,
    ai_summary: str,
    provider_policy_text: str = ""
):
    provider_policy_context = (
        provider_policy_text[:4000]
        if provider_policy_text
        else "No provider-specific policy text was available."
    )

    if not os.getenv("OPENAI_API_KEY"):
        return f"""
Dear {provider_name} Billing Department,

I am writing to request an itemized review of my medical bill and to ask whether I may qualify for financial assistance or charity care.

Based on my preliminary review, there may be charges that require clarification. Please provide an itemized explanation of the services, charges, adjustments, and any available assistance programs.

Thank you for your time and consideration.

Sincerely,
{patient_name}
"""

    prompt = f"""
Draft a professional medical bill dispute / financial assistance request letter.

Patient Name: {patient_name}
Provider Name: {provider_name}

Provider Policy Context:
{provider_policy_context}

Audit Summary:
{ai_summary}

Requirements:
- Formal and polite
- Concise
- Request itemized review
- Request financial assistance screening
- Reference provider policy context only if relevant
- Avoid making unsupported accusations
- Do not claim guaranteed eligibility or guaranteed overcharge
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content

    except Exception as error:
        return f"""
Dear {provider_name} Billing Department,

I am writing to request an itemized review of my medical bill and to ask whether I may qualify for financial assistance or charity care.

The automated letter generator was unavailable, but I would still like to request clarification of the charges and any available financial assistance options.

Thank you for your time and consideration.

Sincerely,
{patient_name}

Error details: {str(error)}
"""