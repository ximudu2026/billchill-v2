from datetime import datetime
from extensions import db


class BillCase(db.Model):
    __tablename__ = "bill_cases"

    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(120), nullable=False, default="Demo Patient")
    provider_name = db.Column(db.String(120), nullable=False)
    household_size = db.Column(db.Integer, nullable=False, default=1)
    annual_income = db.Column(db.Float, nullable=False, default=0)
    zip_code = db.Column(db.String(20), nullable=True)

    total_billed = db.Column(db.Float, nullable=True)
    patient_responsibility = db.Column(db.Float, nullable=True)
    estimated_savings = db.Column(db.Float, nullable=False, default=0)
    eligible_discount_percent = db.Column(db.Float, nullable=False, default=0)

    status = db.Column(db.String(50), nullable=False, default="Uploaded")
    bill_text = db.Column(db.Text, nullable=True)
    ai_summary = db.Column(db.Text, nullable=True)
    dispute_letter = db.Column(db.Text, nullable=True)

    source = db.Column(db.String(50), nullable=False, default="uploaded") 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    findings = db.relationship(
        "AuditFinding",
        backref="bill_case",
        cascade="all, delete-orphan",
        lazy=True
    )


class AuditFinding(db.Model):
    __tablename__ = "audit_findings"

    id = db.Column(db.Integer, primary_key=True)
    bill_case_id = db.Column(db.Integer, db.ForeignKey("bill_cases.id"), nullable=False)

    finding_type = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(200), nullable=True)
    amount = db.Column(db.Float, nullable=True)
    estimated_savings = db.Column(db.Float, nullable=False, default=0)
    confidence_score = db.Column(db.Float, nullable=False, default=0.8)
    reason = db.Column(db.Text, nullable=False)


class BenchmarkRun(db.Model):
    __tablename__ = "benchmark_runs"

    id = db.Column(db.Integer, primary_key=True)
    cases_processed = db.Column(db.Integer, nullable=False, default=0)
    total_simulated_savings = db.Column(db.Float, nullable=False, default=0)
    average_savings_per_case = db.Column(db.Float, nullable=False, default=0)
    manual_minutes_estimate = db.Column(db.Float, nullable=False, default=0)
    automated_minutes_estimate = db.Column(db.Float, nullable=False, default=0)
    time_reduction_percent = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)