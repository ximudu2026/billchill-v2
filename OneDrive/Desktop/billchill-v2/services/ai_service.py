import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_audit_with_ai(bill_text: str, findings: list, household_size: int, annual_income: float, zip_code: str):
    findings_text = "\n".join([
        f"- {f['finding_type']}: {f['reason']} Estimated savings: ${f['estimated_savings']:.2f}"
        for f in findings
    ])

    prompt = f"""
You are a medical billing audit assistant.

Important constraints:
- Do not claim final legal, insurance, or medical certainty.
- Explain findings in plain English.
- Recommend that the patient verify with the provider or insurer.
- Be concise and practical.

Patient Info:
Household Size: {household_size}
Annual Income: {annual_income}
ZIP Code: {zip_code}

Extracted Bill Text:
{bill_text[:6000]}

Rule-Based Findings:
{findings_text if findings_text else "No rule-based findings."}

Return:
1. Plain-English summary
2. Main possible savings opportunities
3. Recommended next steps
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content


def draft_dispute_letter(patient_name: str, provider_name: str, ai_summary: str):
    prompt = f"""
Draft a professional medical bill dispute / financial assistance request letter.

Patient Name: {patient_name}
Provider Name: {provider_name}

Audit Summary:
{ai_summary}

Requirements:
- Formal and polite
- Concise
- Request itemized review
- Request financial assistance screening
- Avoid making unsupported accusations
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content