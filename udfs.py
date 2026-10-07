"""Pixeltable UDFs for museum loans (recorded by module path, e.g. `udfs.is_overdue`)."""
import pixeltable as pxt

LOAN_TERM_DAYS = {'out': 90, 'in-transit': 14, 'returned': 10**6, 'requested': 10**6}


@pxt.udf
def is_overdue(status: str, days_out: int) -> bool:
    return days_out > LOAN_TERM_DAYS.get(status, 90)


@pxt.udf
def urgency(status: str, days_out: int) -> str:
    over = days_out - LOAN_TERM_DAYS.get(status, 90)
    if over <= 0:
        return 'none'
    return 'high' if over > 30 else 'medium'


@pxt.udf
def loan_label(accession: str, borrower: str, venue: str) -> str:
    return f'{accession} → {borrower} ({venue})'
