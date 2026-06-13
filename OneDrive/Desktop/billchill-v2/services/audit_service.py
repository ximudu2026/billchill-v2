import re


def estimate_charity_discount(household_size: int, annual_income: float) -> float:
    """
    Simplified demo charity-care logic.
    This is NOT legal or medical advice.
    It is for synthetic benchmark/demo purposes.
    """

    # Rough synthetic thresholds, not official policy.
    thresholds = {
        1: 45000,
        2: 60000,
        3: 75000,
        4: 90000,
        5: 105000,
    }

    threshold = thresholds.get(household_size, 90000 + (household_size - 4) * 15000)

    if annual_income <= threshold * 0.5:
        return 100.0
    elif annual_income <= threshold * 0.75:
        return 75.0
    elif annual_income <= threshold:
        return 50.0
    elif annual_income <= threshold * 1.25:
        return 25.0
    else:
        return 0.0


def extract_money_values(text: str):
    values = re.findall(r"\$?\s?([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{2})?)", text)
    cleaned = []

    for value in values:
        try:
            cleaned.append(float(value.replace(",", "")))
        except ValueError:
            pass

    return cleaned


def basic_rule_audit(bill_text: str, household_size: int, annual_income: float):
    """
    Returns deterministic findings.
    This gives your app explainable behavior even before calling OpenAI.
    """

    findings = []
    lower_text = bill_text.lower()

    discount = estimate_charity_discount(household_size, annual_income)

    if discount > 0:
        findings.append({
            "finding_type": "charity_care_eligibility",
            "service": "Financial assistance screening",
            "amount": None,
            "estimated_savings": 500.0 * (discount / 100),
            "confidence_score": 0.85,
            "reason": f"Household size and income suggest possible eligibility for a {discount:.0f}% charity-care discount in this demo model."
        })

    if "duplicate" in lower_text or "same charge" in lower_text:
        findings.append({
            "finding_type": "possible_duplicate_charge",
            "service": "Duplicate charge",
            "amount": None,
            "estimated_savings": 250.0,
            "confidence_score": 0.75,
            "reason": "Bill text contains language suggesting a possible duplicate or repeated charge."
        })

    money_values = extract_money_values(bill_text)

    for value in money_values:
        if value >= 2000:
            findings.append({
                "finding_type": "high_charge_review",
                "service": "High-cost line item",
                "amount": value,
                "estimated_savings": value * 0.15,
                "confidence_score": 0.65,
                "reason": f"Line item amount ${value:,.2f} exceeds the demo high-charge review threshold."
            })
            break

    total_estimated_savings = sum(f["estimated_savings"] for f in findings)

    return findings, discount, total_estimated_savings