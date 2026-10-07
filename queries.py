"""Loan queries."""
import pixeltable as pxt

from models import Loans


@pxt.query
def overdue_loans(curator: str):
    """Overdue loans for one curator, most urgent first."""
    return Loans.where((Loans.curator == curator) & (Loans.overdue == True)).select(  # noqa: E712
        Loans.id, Loans.label, Loans.days_out, Loans.urgency_band
    ).order_by(Loans.days_out, asc=False)
