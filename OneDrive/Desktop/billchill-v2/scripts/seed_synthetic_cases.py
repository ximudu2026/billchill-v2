import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import random
from extensions import db
from models import BillCase, AuditFinding
from services.audit_service import basic_rule_audit


HOSPITALS = [
    "Riverside General Hospital",
    "Northview Medical Center",
    "Atlantic Community Hospital",
    "Providence Demo Health",
    "Metro Regional Clinic"
]

SERVICES = [
    "Emergency room facility fee",
    "Chest X-ray",
    "Blood test panel",
    "Medication administration",
    "CT scan",
    "Outpatient consultation",
    "Lab processing fee"
]

NAMES = [
    "Alex Morgan",
    "Jordan Lee",
    "Taylor Chen",
    "Casey Smith",
    "Riley Johnson",
    "Morgan Patel"
]


def generate_fake_bill_text():
    selected_services = random.sample(SERVICES, random.randint(3, 6))
    lines = []
    total = 0

    for service in selected_services:
        amount = random.randint(150, 3500)
        total += amount
        lines.append(f"{service}: ${amount}.00")

    if random.random() < 0.2:
        duplicate_service = random.choice(selected_services)
        duplicate_amount = random.randint(200, 800)
        total += duplicate_amount
        lines.append(f"{duplicate_service}: ${duplicate_amount}.00 duplicate possible same charge")

    bill_text = "\n".join(lines)
    bill_text += f"\nTotal Patient Responsibility: ${total}.00"

    return bill_text, total


def seed_cases(n=1000):
    created = 0

    for _ in range(n):
        patient_name = random.choice(NAMES)
        provider_name = random.choice(HOSPITALS)
        household_size = random.randint(1, 5)
        annual_income = random.randint(22000, 140000)
        zip_code = str(random.randint(10000, 99999))

        bill_text, total = generate_fake_bill_text()

        findings, discount, estimated_savings = basic_rule_audit(
            bill_text=bill_text,
            household_size=household_size,
            annual_income=annual_income
        )

        bill_case = BillCase(
            patient_name=patient_name,
            provider_name=provider_name,
            household_size=household_size,
            annual_income=annual_income,
            zip_code=zip_code,
            total_billed=total,
            patient_responsibility=total,
            estimated_savings=estimated_savings,
            eligible_discount_percent=discount,
            status="Synthetic Analyzed",
            bill_text=bill_text,
            ai_summary="Synthetic benchmark case generated for demo evaluation.",
            dispute_letter="Synthetic case; no real dispute letter generated.",
            source="synthetic"
        )

        db.session.add(bill_case)
        db.session.commit()

        for finding in findings:
            db_finding = AuditFinding(
                bill_case_id=bill_case.id,
                finding_type=finding["finding_type"],
                service=finding.get("service"),
                amount=finding.get("amount"),
                estimated_savings=finding.get("estimated_savings", 0),
                confidence_score=finding.get("confidence_score", 0.8),
                reason=finding["reason"]
            )
            db.session.add(db_finding)

        created += 1

    db.session.commit()
    print(f"Seeded {created} synthetic cases.")


if __name__ == "__main__":
    from app import app

    with app.app_context():
        seed_cases(1000)