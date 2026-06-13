from models import BenchmarkRun
from extensions import db


def create_benchmark_run(cases):
    cases_processed = len(cases)
    total_savings = sum(case.estimated_savings or 0 for case in cases)

    manual_minutes_per_case = 10
    automated_minutes_per_case = 0.75

    manual_total = cases_processed * manual_minutes_per_case
    automated_total = cases_processed * automated_minutes_per_case

    if manual_total > 0:
        time_reduction = ((manual_total - automated_total) / manual_total) * 100
    else:
        time_reduction = 0

    run = BenchmarkRun(
        cases_processed=cases_processed,
        total_simulated_savings=total_savings,
        average_savings_per_case=total_savings / cases_processed if cases_processed else 0,
        manual_minutes_estimate=manual_total,
        automated_minutes_estimate=automated_total,
        time_reduction_percent=time_reduction
    )

    db.session.add(run)
    db.session.commit()

    return run