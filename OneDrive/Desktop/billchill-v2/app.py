import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

from config import Config
from extensions import db, migrate
from models import BillCase, AuditFinding, BenchmarkRun
from services.pdf_service import extract_text_from_pdf
from services.audit_service import basic_rule_audit
from services.ai_service import summarize_audit_with_ai, draft_dispute_letter
from services.benchmark_service import create_benchmark_run


PROVIDER_RULES = {
    "United": "United Healthcare",
    "Providence": "Providence HealthCare",
    "Molina": "Molina HealthCare",
    "CMS": "CMS"
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/admin/init-db")
    def admin_init_db():
        db.create_all()
        return "Database initialized."

    @app.route("/admin/seed-synthetic")
    def admin_seed_synthetic():
        from scripts.seed_synthetic_cases import seed_cases

        existing_synthetic_cases = BillCase.query.filter_by(source="synthetic").count()

        if existing_synthetic_cases > 0:
            return f"Synthetic cases already exist: {existing_synthetic_cases}. Not seeding again."

        seed_cases(1000)
        return "Seeded 1000 synthetic cases."

    @app.route("/")
    def index():
        recent_cases = BillCase.query.order_by(BillCase.created_at.desc()).limit(5).all()
        return render_template(
            "index.html",
            providers=list(PROVIDER_RULES.keys()),
            recent_cases=recent_cases
        )

    @app.route("/analyze", methods=["POST"])
    def analyze():
        provider = request.form.get("provider", "Custom Provider")
        patient_name = request.form.get("patient_name", "Demo Patient")
        household_size = int(request.form.get("household_size", 1))
        annual_income = float(request.form.get("annual_income", 0))
        zip_code = request.form.get("zip_code", "")

        bill_file = request.files.get("bill_pdf")

        if not bill_file or bill_file.filename == "":
            flash("Please upload a patient bill PDF.")
            return redirect(url_for("index"))

        safe_filename = secure_filename(bill_file.filename)
        bill_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_filename)
        bill_file.save(bill_path)

        bill_text = extract_text_from_pdf(bill_path)

        findings, discount, total_savings = basic_rule_audit(
            bill_text=bill_text,
            household_size=household_size,
            annual_income=annual_income
        )

        ai_summary = summarize_audit_with_ai(
            bill_text=bill_text,
            findings=findings,
            household_size=household_size,
            annual_income=annual_income,
            zip_code=zip_code
        )

        dispute_letter = draft_dispute_letter(
            patient_name=patient_name,
            provider_name=provider,
            ai_summary=ai_summary
        )

        bill_case = BillCase(
            patient_name=patient_name,
            provider_name=provider,
            household_size=household_size,
            annual_income=annual_income,
            zip_code=zip_code,
            total_billed=None,
            patient_responsibility=None,
            estimated_savings=total_savings,
            eligible_discount_percent=discount,
            status="Analyzed",
            bill_text=bill_text,
            ai_summary=ai_summary,
            dispute_letter=dispute_letter,
            source="uploaded"
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

        db.session.commit()

        return redirect(url_for("case_detail", case_id=bill_case.id))

    @app.route("/cases/<int:case_id>")
    def case_detail(case_id):
        bill_case = BillCase.query.get_or_404(case_id)
        return render_template("case_detail.html", bill_case=bill_case)

    @app.route("/dashboard")
    def dashboard():
        cases = BillCase.query.order_by(BillCase.created_at.desc()).all()

        total_cases = len(cases)
        total_savings = sum(case.estimated_savings or 0 for case in cases)
        uploaded_cases = sum(1 for case in cases if case.source == "uploaded")
        synthetic_cases = sum(1 for case in cases if case.source == "synthetic")

        finding_counts = {}
        for case in cases:
            for finding in case.findings:
                finding_counts[finding.finding_type] = finding_counts.get(finding.finding_type, 0) + 1

        return render_template(
            "dashboard.html",
            cases=cases,
            total_cases=total_cases,
            total_savings=total_savings,
            uploaded_cases=uploaded_cases,
            synthetic_cases=synthetic_cases,
            finding_counts=finding_counts
        )

    @app.route("/benchmark", methods=["GET", "POST"])
    def benchmark():
        if request.method == "POST":
            synthetic_cases = BillCase.query.filter_by(source="synthetic").all()
            create_benchmark_run(synthetic_cases)
            return redirect(url_for("benchmark"))

        runs = BenchmarkRun.query.order_by(BenchmarkRun.created_at.desc()).all()
        synthetic_count = BillCase.query.filter_by(source="synthetic").count()

        return render_template(
            "benchmark.html",
            runs=runs,
            synthetic_count=synthetic_count
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)