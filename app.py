"""Museum Loans API built with Pixeltable.

    pxt schema update app.py museum
    pxt service run app.py museum
"""
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

from udfs import is_overdue, loan_label, urgency

# ---- tables ----
TableModel = pxt.model_base()


class Objects(TableModel, name='objects'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    accession: pxt.String
    title: pxt.String
    medium: pxt.String
    year: pxt.Int
    gallery: pxt.String

    accession_upper = pxtf.string.upper(accession)
    title_lower = pxtf.string.lower(title)


class Loans(TableModel, name='loans'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    accession: pxt.String
    borrower: pxt.String
    venue: pxt.String
    status: pxt.String
    days_out: pxt.Int
    notes: pxt.String | None
    curator: pxt.String

    label = loan_label(accession, borrower, venue)
    overdue = is_overdue(status, days_out)
    urgency_band = urgency(status, days_out)


# ---- queries ----
@pxt.query
def overdue_loans(curator: str):
    """Overdue loans for one curator, most urgent first."""
    return Loans.where((Loans.curator == curator) & (Loans.overdue == True)).select(  # noqa: E712
        Loans.id, Loans.label, Loans.days_out, Loans.urgency_band
    ).order_by(Loans.days_out, asc=False)


# ---- routes ----
loans_api = FastAPIRouter(name='loans_api')
loans_api.add_insert_route(Objects, path='/objects',
                           inputs=[Objects.accession, Objects.title, Objects.medium, Objects.year, Objects.gallery],
                           outputs=[Objects.id, Objects.accession_upper, Objects.title_lower])
loans_api.add_insert_route(Loans, path='/loans',
                           inputs=[Loans.accession, Loans.borrower, Loans.venue, Loans.status, Loans.days_out,
                                   Loans.notes, Loans.curator],
                           outputs=[Loans.id, Loans.label, Loans.overdue, Loans.urgency_band])
loans_api.add_update_route(Loans, path='/loans/update', inputs=[Loans.status, Loans.days_out],
                           outputs=[Loans.id, Loans.overdue, Loans.urgency_band])
loans_api.add_compute_route(Loans, path='/urgency', inputs=[Loans.status, Loans.days_out],
                            outputs=[Loans.overdue, Loans.urgency_band])
loans_api.add_query_route(path='/loans/overdue', query=overdue_loans, method='get')
